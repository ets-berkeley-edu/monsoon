"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""
from flask import current_app as app, Response
import requests
import simplejson as json


class ResponseExceptionWrapper:
    """Wraps a failed outgoing request's exception (and response, if any).

    Borrows the Requests convention of truthy successes / falsy failures, so callers of
    request() can write `if response:` regardless of which they got back.
    """

    def __init__(self, exception, original_response=None):
        self.exception = exception
        self.raw_response = original_response

    def __bool__(self):
        return False

    def __repr__(self):
        return f'<ResponseExceptionWrapper exception={self.exception}, raw_response={self.raw_response}>'


def request(url, headers=None, method='get', auth=None, data=None, timeout=None, **kwargs):
    """Exception and error catching wrapper for outgoing HTTP requests.

    Returns the HTTP response from the external server, if the request was successful.
    Otherwise, a ResponseExceptionWrapper containing the exception and the original HTTP
    response, if one was returned.
    """
    if method not in ('get', 'post', 'put', 'delete'):
        raise ValueError(f'Unrecognized HTTP method "{method}"')
    headers = headers or {}
    app.logger.debug({'message': 'HTTP request', 'url': url, 'method': method, 'headers': headers})
    response = None
    try:
        http_method = getattr(requests, method)
        response = http_method(url, headers=headers, auth=auth, data=data, timeout=timeout or 60, **kwargs)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        wrapped = ResponseExceptionWrapper(e, response)
        app.logger.error(wrapped)
        if hasattr(response, 'content'):
            app.logger.error(response.content)
        return wrapped
    else:
        return response


def tolerant_jsonify(obj, status=200, **kwargs):
    content = json.dumps(obj, ignore_nan=True, separators=(',', ':'), **kwargs)
    return Response(content, mimetype='application/json', status=status)
