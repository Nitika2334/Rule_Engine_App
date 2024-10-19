from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from App import db
from datetime import datetime

Base = declarative_base()

class NodeModel(Base):
    __tablename__ = 'nodes'

    id = db.Column(Integer, primary_key=True)
    elem_type = db.Column(Integer)
    value = db.Column(String)
    left_id = db.Column(Integer, ForeignKey('nodes.id'))
    right_id = db.Column(Integer, ForeignKey('nodes.id'))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    left = relationship("Node", foreign_keys=[left_id], remote_side=[id], backref="parent_left")
    right = relationship("Node", foreign_keys=[right_id], remote_side=[id], backref="parent_right")