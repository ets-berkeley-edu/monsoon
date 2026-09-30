# Redis vs. AWS Secrets Manager for CollectionSpace credential storage

**Context:** Monsoon (the Flask/Vue reimplementation of cspace-webapps-common) passes user
credentials through to CollectionSpace rather than handling authentication/authorization
itself. CollectionSpace's REST API is stateless — every call is authenticated independently
via HTTP Basic Auth, with no server-side session of its own. That means the app has to hold a
logged-in user's CollectionSpace username/password somewhere for the duration of their browser
session, so they aren't asked to re-enter it on every click.

This note lays out why that "somewhere" should be Redis, not AWS Secrets Manager.

## Why an in-process cache is not an option

cspace-webapps-common's current `CSpaceAuthN` backend verifies a login once via Basic Auth and
then caches the password in a process-wide Python dict (`CSpaceAuthN.authNDictionary`) so it
doesn't have to re-verify on every request. Its own documentation already flags this as unsafe
under multiple WSGI workers (a cache miss on another worker silently breaks CSpace calls until
re-login) and as something that would leak credentials across tenants/users if ever run in a
shared process.

Monsoon's architecture — one shared deployment serving every tenant, not a process per tenant
— makes this worse, not better. Whatever holds these credentials has to be a store that's
shared and durable across workers/processes by construction. An in-memory dict is a
non-starter; the credential store has to be external.

## The reference implementation

A sample CollectionSpace Media/Blob uploader app was reviewed as prior art. Its approach:

- Verify login via `GET /accounts/0/accountperms` (a real, documented sentinel account ID that
  always resolves to "whichever account is currently authenticated" — a clean way to validate
  credentials and pull permission grants in one call).
- Store the username/password (plus instance URL and SSL-verify flag) in AWS Secrets Manager,
  under a random per-login secret name.
- Put only a *reference* to that secret in the Flask session cookie — never the credential
  itself.
- Fetch the credential fresh from Secrets Manager on every request that needs it, deliberately
  never caching it in memory, so that deleting the secret (logout) takes effect immediately on
  the very next request.

That fetch-fresh-every-request design is good and worth keeping — it's what makes logout
actually mean something. But it's also the detail that decides the Secrets-Manager-vs-Redis
question: whatever store holds this value sits on the hot path of every authenticated request,
not just at login.

## Secrets Manager: pros and cons

**Pros**
- Encryption at rest (KMS-backed) and IAM-scoped access control are automatic, no
  configuration to get wrong.
- Every read/write is CloudTrail-logged with caller identity — a real audit trail if "who
  touched this credential, and when" ever needs to be independently verifiable.
- Fully managed — nothing new to run, patch, or monitor.

**Cons**
- **No built-in TTL.** The reference app's own documentation admits this: a browser that
  closes without hitting "log out" leaves its secret orphaned indefinitely, since Flask's
  cookie-based sessions have no server-side expiry hook to trigger cleanup. Their stated
  mitigation is a separate scheduled job to prune old secrets by hand — extra infrastructure
  that has to be built and maintained just to compensate for this gap.
- Cost and latency both scale with *call volume*: roughly $0.05 per 10,000 API calls plus a
  network round-trip, on top of the flat per-secret fee. "Fetch on every request" is exactly
  the access pattern that costs the most and adds the most latency here — an interactive page
  making several sequential CollectionSpace calls (permission checks, a lookup, then a create)
  means several sequential Secrets Manager round-trips stacked in front of them.
- Requires real AWS credentials to develop against locally, even for a single engineer running
  the app on their laptop.

## Redis: pros and cons

**Pros**
- **Native per-key TTL** (`SETEX`/`EXPIRE`) solves the cleanup gap above outright — "this
  credential vanishes N minutes after last use" is a one-line feature, not a cron job.
- Sub-millisecond to low-single-digit-millisecond round trips, especially co-located in the
  same VPC — a much better fit for a fetch-on-every-request pattern.
- Flat infrastructure cost regardless of traffic volume, rather than cost that scales with the
  number of calls.
- Already part of the stack: Ripley (the sibling project these conventions are modeled on)
  already runs Redis for caching and its `rq` job queue. Reusing it here is less new
  operational surface than standing up a new AWS service and a new IAM policy, and it composes
  naturally if Monsoon ever wants a general-purpose cache or job queue too, instead of running
  two separate stores for "secrets" and "everything else."
- Easy local dev story: a local Redis (or a fake in-memory Redis for tests) needs no cloud
  credentials to develop or test against.

**Cons**
- No encryption at rest by default — see below, this turns out not to matter much in practice.
- A thinner built-in audit trail than IAM + CloudTrail; "who read this key, and when" isn't
  free the way it is with Secrets Manager.

## Closing the encryption gap

ElastiCache for Redis supports encryption at rest as a cluster-level setting
(`AtRestEncryptionEnabled`), configured in infrastructure (CloudFormation/Terraform/console),
not in application code, and it is effectively free to turn on:

- **Cost:** no extra charge for the feature itself. Using a customer-managed KMS key instead of
  the AWS-managed default adds about $1/month plus a negligible number of KMS calls (key
  wrapping happens occasionally, not per Redis operation); the AWS-managed default key costs
  nothing.
- **Latency:** negligible. Redis's working set lives in memory; at-rest encryption only covers
  the storage layer (disk persistence and backup snapshots), not the in-memory read/write path,
  so a `GET`/`SETEX` runs at the same speed either way.

(The setting that *does* have a real, if usually small, per-request cost is encryption **in
transit** — a TLS handshake per connection plus ongoing CPU overhead to encrypt/decrypt each
request. That's a separate, genuine trade-off, unlike at-rest.)

Since at-rest encryption is immutable once a cluster is created, and nothing is running yet,
there's no reason not to enable it from the start with the default AWS-managed key — it
removes Redis's main disadvantage against Secrets Manager at no real cost.

## What to actually store

Store the same structured shape the reference app uses — `username`, `password`,
`instance_url`, `verify_ssl` — rather than a pre-encoded HTTP Basic Auth header string
(`base64("username:password")`). Two reasons:

- Base64 is an encoding, not encryption. A pre-encoded value is exactly as sensitive as the raw
  username/password, just format-shifted — and it risks being mistaken for "already secured"
  by someone auditing what's in Redis later, when it isn't.
- Structured fields keep the username usable on its own (for display and logging), let the
  HTTP client library build the Basic Auth header correctly (handling character-encoding edge
  cases per RFC 7617), and keep log/secret redaction simple: "never log the `password` field"
  is easy to verify by inspection, whereas "never log this opaque string that happens to
  decode to the password" is exactly the kind of thing an incomplete redaction rule misses.

## Recommendation

Use Redis, with a per-key TTL matching the app's session lifetime, as the credential store for
the CollectionSpace pass-through auth flow. Enable ElastiCache at-rest encryption (default
AWS-managed KMS key) at cluster creation, since it costs nothing and closes Redis's one real
disadvantage against Secrets Manager. Store `username`/`password`/`instance_url`/`verify_ssl`
as plain structured fields in the Redis value, and let the HTTP client library handle Basic
Auth header construction at request time.
