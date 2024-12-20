from App import db
from App.Models.RuleModel import RuleModel
from App.Models.NodeModel import NodeModel

def create_rule_schema(rule_name, rule_text, root, postfix_expr):
    existing_rule = db.session.query(RuleModel).filter_by(rule_name=rule_name).first()
    if existing_rule:
        return None, "Rule with the same name already exists."

    new_rule = RuleModel(rule_name=rule_name, rule=rule_text, root=root.id, postfix_expr=postfix_expr)
    db.session.add(new_rule)
    db.session.commit()
    return new_rule, None

def create_node(elem_type, value, left=None, right=None):
    node = NodeModel(elem_type=elem_type, value=value, left=left.id if left else None, right=right.id if right else None)
    db.session.add(node)
    db.session.commit()
    return node

def save_node(elem_type, value, left=None, right=None):
    node = NodeModel(elem_type=elem_type, value=value, left=left, right=right)
    node.save()
    return node

def save_rule(rule_name, rule, root, postfix_expr):
    new_rule = RuleModel(rule_name=rule_name, rule=rule, root=root, postfix_expr=postfix_expr)
    db.session.add(new_rule)
    db.session.commit()  # Commit the session
    return new_rule

def find_rule_by_name(rule_name):
    return RuleModel.query.filter_by(rule_name=rule_name).first()

def get_all_rules_from_db():
    return RuleModel.query.all()

def find_node_by_id(node_id):
    return NodeModel.query.get(node_id)