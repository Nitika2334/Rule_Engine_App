from App import db

class NodeModel(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    elem_type = db.Column(db.Integer, nullable=False)  # Can store types like LOGICAL, COMPARISON, etc.
    value = db.Column(db.String(255), nullable=False)
    left = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=True)
    right = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()