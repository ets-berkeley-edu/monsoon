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
from monsoon import db, std_commit
from monsoon.models.base import Base

# Pure many-to-many association, with no attributes of its own -- which tenants can reach which
# tools is the manifest itself, not an entity.
tenant_tools = db.Table(
    'tenant_tools',
    db.Column('tenant_id', db.Integer, db.ForeignKey('tenants.id'), primary_key=True),
    db.Column('tool_id', db.Integer, db.ForeignKey('tools.id'), primary_key=True),
)


class Tool(Base):
    __tablename__ = 'tools'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    key = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, key, name):
        self.key = key
        self.name = name

    @classmethod
    def create(cls, key, name):
        tool = cls(key=key, name=name)
        db.session.add(tool)
        std_commit()
        return tool

    @classmethod
    def grant_to_tenant(cls, tool, tenant):
        db.session.execute(tenant_tools.insert().values(tenant_id=tenant.id, tool_id=tool.id))
        std_commit()

    @classmethod
    def available_for_tenant(cls, tenant_id):
        return cls.query.join(tenant_tools).filter(tenant_tools.c.tenant_id == tenant_id).order_by(cls.key).all()

    def to_api_json(self):
        return {
            'key': self.key,
            'name': self.name,
        }
