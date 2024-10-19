from datetime import datetime
from App import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RuleModel(Base):
    __tablename__ = 'rules'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = db.Column(db.String)
    rule = db.Column(db.String)
    root_id = db.Column(UUID(as_uuid=True), ForeignKey('nodes.id'))
    postfix_expr = db.Column(db.String)  # Stored as JSON string
    root = relationship('NodeModel', back_populates='rules')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Rule(id={self.id}, rule_name='{self.rule_name}')>"