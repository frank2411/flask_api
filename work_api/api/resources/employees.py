from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from work_api.models import Employee
from work_api.api.schemas import EmployeeSchema


class EmployeeDetailResource(Resource):

    def get(self, employee_id):
        schema = EmployeeSchema()
        employee = Employee.get_employee(employee_id)
        return {'employee': schema.dump(employee)}

    def patch(self, employee_id):
        employee = Employee.get_employee(employee_id)
        schema = EmployeeSchema(partial=True, instance=employee)

        try:
            employee = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        employee.save()
        return {'message': 'employee updated', 'employee': schema.dump(employee)}

    def delete(self, employee_id):
        employee = Employee.get_employee(employee_id)
        employee.delete()
        return {'message': 'employee deleted'}


class EmployeeListResource(Resource):
    """Creation and get_all"""

    def get(self):
        schema = EmployeeSchema(many=True)
        employees = Employee.get_employees()
        return {"employees": schema.dump(employees)}

    def post(self):
        try:
            schema = EmployeeSchema()
            employee = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        employee.save()
        return {'message': 'employee created', 'employee': schema.dump(employee)}, 201
