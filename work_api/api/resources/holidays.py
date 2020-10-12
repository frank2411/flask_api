from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from work_api.models import Holiday
from work_api.api.schemas import HolidaySchema


class HolidayDetailResource(Resource):

    def get(self, holiday_id):
        schema = HolidaySchema()
        holiday = Holiday.get_holiday(holiday_id)
        return {'holiday': schema.dump(holiday)}

    def patch(self, holiday_id):
        holiday = Holiday.get_holiday(holiday_id)
        schema = HolidaySchema(partial=True, instance=holiday)

        try:
            holiday = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        holiday.save()
        return {'message': 'holiday updated', 'holiday': schema.dump(holiday)}

    def delete(self, holiday_id):
        holiday = Holiday.get_holiday(holiday_id)
        holiday.delete()
        return {'message': 'holiday deleted'}


class HolidayListResource(Resource):
    """Creation and get_all"""

    def get(self):
        schema = HolidaySchema(many=True)
        holidays = Holiday.get_holidays()
        return {"holidays": schema.dump(holidays)}

    def post(self):
        try:
            schema = HolidaySchema(is_creation=True)
            holiday = schema.load(request.json)
        except ValidationError as err:
            return err.messages, 422

        holiday.save()
        return {'message': 'holiday created', 'holiday': schema.dump(holiday)}, 201
