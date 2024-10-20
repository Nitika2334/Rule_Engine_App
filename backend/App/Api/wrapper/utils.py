import re
from App.Api.wrapper.schema import (
    create_rule_schema,
    create_node,
    save_node,
    find_rule_by_name,
    save_rule,
    get_all_rules_from_db,
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
            return {"error": "rule_name can't be null or length can't be zero"}, 400

        if not rule or not isinstance(rule, str):
            return {"error": "rule can't be null"}, 400

        # Validate the rule format
        if not validate_rule(rule):
            return {"error": "Invalid rule format. Ensure it contains logical and comparison operators."}, 400

        # Convert the rule into postfix
        postfix_expr = shunting_yard(rule)

        # Create AST
        root = create_ast(postfix_expr)
        if not root:
            return {"error": "Failed to create AST"}, 500

        # Save rule to DB
        new_rule, error = create_rule_schema(rule_name, rule, root, postfix_expr)
        if error:
            return {"error": error}, 400

        return {"message": "Rule created successfully", "rule": new_rule.id}, 201

    except Exception as e:
        return {"error": str(e)}, 500


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
            return {"error": "rule_name can't be null or length can't be zero"}, 400
        if not rules or not isinstance(rules, list) or len(rules) == 0:
            return {"error": "rules must be a non-empty array"}, 400

        # Check if a rule with the same name exists
        existing_rule = find_rule_by_name(rule_name)
        if existing_rule:
            return {"error": "A rule with this name already exists"}, 400

        # Validate each rule and collect postfix expressions
        postfix_expressions = []
        for rule in rules:
            if not validate_rule(rule):
                return {"error": f"Invalid rule format: {rule}"}, 400
            
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
            new_rule = save_rule(rule_name, combined_rule_str, combined_ast.id, combined_postfix_expr)  # Pass the postfix expression
            return {"message": "Rules combined successfully", "rule": new_rule.id}, 201
        else:
            return {"error": "Failed to combine rules into AST"}, 500
    except Exception as e:
        return {"error": str(e)}, 500


def get_all_rules():
    try:
        rules = get_all_rules_from_db()
        # Convert each rule to a dictionary
        rules_list = [rule.to_dict() for rule in rules]
        return rules_list, 200
    except Exception as e:
        return {"error": str(e)}, 500


def evaluate_rule(data):
    try:
        rule_name = data.get('rule_name')
        conditions = data.get('conditions')

        evaluation_result = evaluate_ast(rule_name, conditions)

        return {'message': 'Rule evaluated successfully', 'evaluation_result': evaluation_result}, 200

    except Exception as e:
        return {"error": str(e)}, 500


def evaluate_ast(rule_name, conditions):
    # Fetch the rule from the database using rule_name
    rule = find_rule_by_name(rule_name)
    if not rule:
        return {"error": f"Rule '{rule_name}' not found"}, 404

    # Retrieve the root node from the AST
    root_node = NodeModel.query.filter_by(id=rule.root).first()
    if not root_node:
        return {"error": "AST root node not found"}, 500

    # Evaluate the AST starting from the root node
    result = evaluate_node(root_node, conditions)
    return result


def evaluate_node(node, conditions):
    """
    Recursively evaluates the AST node.

    Args:
        node: The current node being evaluated.
        conditions: A dictionary of variable values used in the comparison.

    Returns:
        The result of the evaluation: True/False for logical/comparison nodes or a variable's value for leaf nodes.
    """
    if node.elem_type == ElemType['LOGICAL']:
        # Logical operator (AND/OR)
        left_result = evaluate_node(NodeModel.query.filter_by(id=node.left).first(), conditions)
        right_result = evaluate_node(NodeModel.query.filter_by(id=node.right).first(), conditions)

        if node.value == 'and':
            return left_result and right_result
        elif node.value == 'or':
            return left_result or right_result
    elif node.elem_type == ElemType['COMPARISON']:
        # Comparison operator (<, >, =, <=, >=)
        left_value = evaluate_node(NodeModel.query.filter_by(id=node.left).first(), conditions)
        right_value = evaluate_node(NodeModel.query.filter_by(id=node.right).first(), conditions)

        if node.value == '<':
            return left_value < right_value
        elif node.value == '>':
            return left_value > right_value
        elif node.value == '=':
            return left_value == right_value
        elif node.value == '<=':
            return left_value <= right_value
        elif node.value == '>=':
            return left_value >= right_value
    elif node.elem_type in [ElemType['STRING'], ElemType['INTEGER'], ElemType['VARIABLE']]:
        # If the node is a variable, lookup its value in conditions
        if node.elem_type == ElemType['VARIABLE']:
            return conditions.get(node.value)
        else:
            # Otherwise, return the value as-is (for constants like '5' or "'string'")
            return node.value

    # If something goes wrong or an unknown element type is encountered, return None
    return None