import re
from App.Api.wrapper.schema import (
    create_rule_schema,
    create_node,
    save_node,
    find_rule_by_name,
    save_rule,
    get_all_rules_from_db,
    find_node_by_id,
)
from App.Models.NodeModel import NodeModel

PRECEDENCE = {
    '(': -1,
    ')': -1,
    'or': 1,
    'and': 1,
    '<': 2,
    '>': 2,
    '=': 2,
    '<=': 2,
    '>=': 2,
}

ElemType = {
    'LOGICAL': 1,
    'COMPARISON': 2,
    'STRING': 3,
    'INTEGER': 4,
    'VARIABLE': 5,
}

def validate_rule(rule):
    rule_pattern = r"\w+\s*(<|>|=|<=|>=)\s*('[^']*'|\w+)\s*(AND|OR)\s*\w+\s*(<|>|=|<=|>=)\s*('[^']*'|\w+)"
    return bool(re.search(rule_pattern, rule, re.IGNORECASE))

def shunting_yard(rule):
    tokens = re.findall(r"\w+|[><]=?|AND|OR|\(|\)|=", rule)
    stack = []
    postfix_expr = []

    for token in tokens:
        token = token.lower()
        if token not in PRECEDENCE:
            postfix_expr.append(token)
        else:
            if not stack:
                stack.append(token)
            else:
                prevoper = PRECEDENCE[stack[-1]]
                curroper = PRECEDENCE[token]
                if curroper > prevoper:
                    stack.append(token)
                else:
                    if token == '(':
                        stack.append(token)
                    elif token == ')':
                        while stack[-1] != '(':
                            postfix_expr.append(stack.pop())
                        stack.pop()  # remove the '('
                    else:
                        while stack and curroper <= PRECEDENCE[stack[-1]]:
                            postfix_expr.append(stack.pop())
                        stack.append(token)

    while stack:
        popped = stack.pop()
        if PRECEDENCE.get(popped, 0) == -1:
            return []
        postfix_expr.append(popped)

    return postfix_expr

def create_ast(postfix_expr):
    node_stack = []
    for token in postfix_expr:
        if token not in PRECEDENCE:
            node = create_node(ElemType['STRING'], token)
            node_stack.append(node)
        else:
            operand1 = node_stack.pop()
            operand2 = node_stack.pop()
            node = create_node(
                ElemType['LOGICAL'] if token in ['and', 'or'] else ElemType['COMPARISON'],
                token,
                operand2,
                operand1
            )
            node_stack.append(node)

    return node_stack[0] if node_stack else None

def create_rule(data):
    try:
        rule_name = data.get('rule_name')
        rule = data.get('rule')

        # Validate input
        if not rule_name or len(rule_name) <= 0:
            return {"status": "error", "message": "rule_name can't be null or length can't be zero"}, 400

        if not rule or not isinstance(rule, str):
            return {"status": "error", "message": "rule can't be null"}, 400

        # Validate the rule format
        if not validate_rule(rule):
            return {"status": "error", "message": "Invalid rule format. Ensure it contains logical and comparison operators."}, 400

        # Convert the rule into postfix
        postfix_expr = shunting_yard(rule)

        # Create AST
        root = create_ast(postfix_expr)
        if not root:
            return {"status": "error", "message": "Failed to create AST"}, 500

        # Save rule to DB
        new_rule, error = create_rule_schema(rule_name, rule, root, postfix_expr)
        if error:
            return {"status": "error", "message": error}, 400

        return {
            "status": "success",
            "message": "Rule created successfully",
            "rule": {
                "ruleName":new_rule.rule_name,
                "rule":new_rule.rule,
                "root":new_rule.root,
                "postfixExpr": new_rule.postfix_expr
            }
        }, 201

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def combine(rules):
    combined_ast = None
    for rule in rules:
        # Convert the rule into postfix notation
        postfix_expr = shunting_yard(rule)
        root = create_ast(postfix_expr)

        # If this is the first rule, set it as the combined AST
        if not combined_ast:
            combined_ast = root
        else:
            # Create a new node representing the logical combination (AND)
            combined_node = save_node(
                ElemType['LOGICAL'], 
                'and', 
                left=combined_ast.id,  # Use the ID of the combined_ast
                right=root.id          # Use the ID of the new root
            )
            combined_ast = combined_node  # Update combined_ast to the new combined node

    return combined_ast

def combine_rules(data):
    try:
        rule_name = data.get('rule_name')
        rules = data.get('rules')

        # Validate input
        if not rule_name or len(rule_name) == 0:
            return {"status": "error", "message": "rule_name can't be null or length can't be zero"}, 400
        if not rules or not isinstance(rules, list) or len(rules) == 0:
            return {"status": "error", "message": "rules must be a non-empty array"}, 400

        # Check if a rule with the same name exists
        existing_rule = find_rule_by_name(rule_name)
        if existing_rule:
            return {"status": "error", "message": "A rule with this name already exists"}, 400

        # Validate each rule and collect postfix expressions
        postfix_expressions = []
        for rule in rules:
            if not validate_rule(rule):
                return {"status": "error", "message": f"Invalid rule format: {rule}"}, 400
            
            # Get the postfix expression for the current rule
            postfix_expr = shunting_yard(rule)
            # Join the postfix expression into a string for saving
            postfix_expressions.append(" ".join(postfix_expr))

        # Combine rules into AST
        combined_ast = combine(rules)
        if combined_ast:
            combined_rule_str = " AND ".join(rules)
            # Create the combined postfix expression as a string
            combined_postfix_expr = " AND ".join(postfix_expressions)
            new_rule = save_rule(rule_name, combined_rule_str, combined_ast.id, combined_postfix_expr)
            return {
                "status": "success",
                "message": "Rules combined successfully",
                "rule": {
                    "ruleName":new_rule.rule_name,
                    "rule":new_rule.rule,
                    "root":new_rule.root,
                    "postfixExpr": new_rule.postfix_expr
                }
            }, 201
        else:
            return {"status": "error", "message": "Failed to combine rules into AST"}, 500
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


def to_dict(self):
    return {
        'id': str(self.id),
        'rule_name': self.rule_name,
        'rule': self.rule,
        'root': self.root,
        'postfixExpr': self.postfix_expr
    }
    

def get_all_rules():
    try:
        rules = get_all_rules_from_db()
        # Convert each rule to a dictionary
        rules_list = [rule.to_dict() for rule in rules]
        return rules_list,200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def evaluate_rule(data):
    try:
        rule_name = data.get('rule_name')
        conditions = data.get('conditions')

        if not rule_name or not conditions:
            return {"status": "error", "message": "Missing rule_name or conditions in request"}, 400

        # Fetch the rule from the database
        rule = find_rule_by_name(rule_name)
        if not rule:
            return {"status": "error", "message": f"Rule '{rule_name}' not found"}, 404

        # Reconstruct the AST
        root_node = reconstruct_ast(rule.root)
        if not root_node:
            return {"status": "error", "message": "Failed to reconstruct AST"}, 500

        # Evaluate the AST
        evaluation_result = evaluate_ast(root_node, conditions)
        print(f'Evaluation Result: {evaluation_result}')

        return {
            "status": "success",
            "message": "Rule evaluated successfully",
            "data": {
                "evaluation_result": evaluation_result
            }
        }, 200

    except Exception as e:
        print(f"Error evaluating Rule: {e}")
        return {"status": "error", "message": "Internal Server Error"}, 500

def evaluate_ast(node, conditions):
    try:
        if not node:
            return False

        if node['elem_type'] == ElemType['COMPARISON']:
            left_value = conditions.get(node['left']['value'], node['left']['value'])
            right_value = conditions.get(node['right']['value'], node['right']['value'])

            # Convert both values to float if possible, otherwise keep as string
            try:
                left_value = float(left_value)
                right_value = float(right_value)
            except ValueError:
                # If conversion fails, keep the values as strings
                pass

            print(f"Left Value: {left_value}")
            print(f"Right Value: {right_value}")

            if left_value is None or right_value is None:
                raise ValueError('Missing condition value for comparison')

            if node['value'] == '>':
                return left_value > right_value
            elif node['value'] == '<':
                return left_value < right_value
            elif node['value'] == '=':  # Changed from '===' to '='
                return left_value == right_value
            elif node['value'] == '<=':
                return left_value <= right_value
            elif node['value'] == '>=':
                return left_value >= right_value
            else:
                return False

        if node['elem_type'] == ElemType['LOGICAL']:
            left_eval = evaluate_ast(node['left'], conditions)
            right_eval = evaluate_ast(node['right'], conditions)

            if node['value'].lower() == 'and':
                return left_eval and right_eval
            elif node['value'].lower() == 'or':
                return left_eval or right_eval

        return True
    except Exception as error:
        print(f"Error evaluating AST: {error}")
        raise ValueError('Failed to evaluate AST')

# You'll need to implement this function to reconstruct the AST from your database
from App.Api.wrapper.schema import find_node_by_id

def reconstruct_ast(node_id):
    try:
        node = find_node_by_id(node_id)
        if not node:
            return None

        # Create a dictionary representation of the node
        reconstructed_node = {
            'id': node.id,
            'elem_type': node.elem_type,
            'value': node.value,
            'left': None,
            'right': None
        }

        # Recursively reconstruct left and right children if they exist
        if node.left:
            reconstructed_node['left'] = reconstruct_ast(node.left)
        if node.right:
            reconstructed_node['right'] = reconstruct_ast(node.right)

        return reconstructed_node
    except Exception as e:
        print(f"Error reconstructing AST: {e}")
        return None
