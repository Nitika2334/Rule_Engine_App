from App import db

class RuleModel(db.Model):
    __tablename__ = 'rules'

    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(255), unique=True)
    rule = db.Column(db.Text, nullable=False)
    root = db.Column(db.Integer, nullable=False)
    postfix_expr = db.Column(db.JSON, nullable=False)

    @classmethod
    def find_one(cls, filters):
        return cls.query.filter_by(**filters).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': str(self.id),
            'rule_name': self.rule_name,
            'rule': self.rule,
            'root': self.root,
            'postfixExpr': self.postfix_expr
        }