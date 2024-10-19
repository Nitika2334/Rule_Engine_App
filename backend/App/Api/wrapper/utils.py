import re
from App.Api.wrapper.schema import create_rule_schema,create_node,save_node,find_rule_by_name,save_rule,get_all_rules_schema

PRECEDENCE = {
    '(': -1,
    ')': -1,
    'or': 1,
    'and': 1,
    '<': 2,
    '>': 2,
    '=': 2,
    '<=': 2,
    '>=': 2
}

ElemType = {
    'LOGICAL': 1,
    'COMPARISON': 2,
    'STRING': 3,
    'INTEGER': 4,
    'VARIABLE': 5
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
    
def combine_rule(rules):
    combined_ast = None
    for rule in rules:
        postfix_expr = shunting_yard(rule)
        root = create_ast(postfix_expr)
        if not combined_ast:
            combined_ast = root
        else:
            combined_node = save_node(ElemType['LOGICAL'], 'and', combined_ast, root)
            combined_ast = combined_node

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

        # Validate each rule
        for rule in rules:
            if not validate_rule(rule):
                return {"error": f"Invalid rule format: {rule}"}, 400

        # Combine rules into AST
        combined_ast = combine_rule(rules)
        if combined_ast:
            combined_rule_str = " AND ".join(rules)
            new_rule = save_rule(rule_name, combined_rule_str, combined_ast._id)
            return {"message": "Rules combined successfully", "rule": new_rule}, 201
        else:
            return {"error": "Failed to combine rules into AST"}, 500
    except Exception as e:
        return {"error": str(e)}, 500


def get_all_rules():
    try:
        rules = get_all_rules_schema()
        return rules, 200
    except Exception as e:
        return {"error": str(e)}, 500
    

def evaluate_ast(root, conditions):
    if root.elem_type == ElemType['LOGICAL']:
        # Perform logical operations
        left_value = evaluate_ast(root.left, conditions)
        right_value = evaluate_ast(root.right, conditions)
        if root.value == 'and':
            return left_value and right_value
        elif root.value == 'or':
            return left_value or right_value
    
    elif root.elem_type == ElemType['COMPARISON']:
        # Perform comparison operations
        variable_name = root.left.value
        condition_value = conditions.get(variable_name)
        comparison_value = root.right.value

        if condition_value is None:
            raise ValueError(f"Condition for {variable_name} not provided.")
        
        # Perform the comparison based on the operator
        if root.value == '=':
            return condition_value == comparison_value
        elif root.value == '>':
            return condition_value > comparison_value
        elif root.value == '<':
            return condition_value < comparison_value
        elif root.value == '>=':
            return condition_value >= comparison_value
        elif root.value == '<=':
            return condition_value <= comparison_value
    
    elif root.elem_type in [ElemType['STRING'], ElemType['INTEGER'], ElemType['VARIABLE']]:
        # Return variable value
        return conditions.get(root.value)
    
    return False

def evaluate_rule(data):
    try:
        rule_name = data.get('rule_name')
        conditions = data.get('conditions')

        # Validate input
        if not rule_name or not conditions:
            return {"error": "Both rule_name and conditions are required"}, 400
        
        # Retrieve the rule by name
        rule = find_rule_by_name(rule_name)
        if not rule:
            return {"error": f"Rule with name {rule_name} not found"}, 404
        
        # Get the AST from the rule
        root_node = rule.root
        
        # Evaluate the AST based on the conditions
        evaluation_result = evaluate_ast(root_node, conditions)
        
        return {'message': 'Rule evaluated successfully', 'evaluation_result': evaluation_result}, 200

    except Exception as e:
        return {"error": str(e)}, 500
