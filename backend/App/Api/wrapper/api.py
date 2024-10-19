from flask import request, jsonify
from flask_restful import Resource
from App.Api.wrapper.utils import (
    create_rule, combine_rules, get_all_rules, evaluate_rule
)


class CreateRuleResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            response, status_code = create_rule(data)
            return response, status_code
        except Exception as e:
            print(f"Error creating rule: {str(e)}")
            return jsonify({"error": "Internal Server Error"}), 500


class CombineRulesResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            response, status_code = combine_rules(data)
            return response, status_code
        except Exception as e:
            return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


class EvaluateRuleResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            response, status_code = evaluate_rule(data)
            return response, status_code
        except Exception as e:
            print(f"Error evaluating Rule: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500


class GetAllRulesResource(Resource):
    def get(self):
        try:
            response_data, status_code = get_all_rules()
            return response_data, status_code
        except Exception as e:
            return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
