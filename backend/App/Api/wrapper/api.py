from flask import request
from flask_restful import Resource
from App.Api.wrapper.utils import create_rule, combine_rules, evaluate_rule, get_all_rules


class CreateRuleResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            response_data, status_code = create_rule(data)
            return response_data, status_code
        except Exception as e:
            return {
                'message': 'Create rule failed',
                'status': False,
                'type': 'custom_error',
                'error_status': {'error_code': '10001'}
            }, 400

class CombineRulesResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            response_data, status_code = combine_rules(data)
            return response_data, status_code
        except Exception as e:
            return {
                'message': 'Combine rules failed',
                'status': False,
                'type': 'custom_error',
                'error_status': {'error_code': '10002'}
            }, 400

class EvaluateRuleResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            response_data, status_code = evaluate_rule(data)
            return response_data, status_code
        except Exception as e:
            return {
                'message': 'Evaluate rule failed',
                'status': False,
                'type': 'custom_error',
                'error_status': {'error_code': '10003'}
            }, 400

class GetAllRulesResource(Resource):
    def get(self):
        try:
            data = request.get_json()
            response_data, status_code = get_all_rules(data)
            return response_data, status_code
        except Exception as e:
            return {
                'message': 'Fetching rules failed',
                'status': False,
                'type': 'custom_error',
                'error_status': {'error_code': '10004'}
            }, 400
