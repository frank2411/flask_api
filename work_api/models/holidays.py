import enum
# from datetime import datetime, timedelta

from .db import db

from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, Integer, Enum, ForeignKey
from sqlalchemy import or_
from sqlalchemy.types import Date

from flask_restful import abort


class HolidayTypeEnum(enum.Enum):
    paid = "paid"
    unpaid = "unpaid"


class HolidaySubtypeTypeEnum(enum.Enum):
    rtt = "rtt"
    normal = "normal"


class Holiday(db.Model):
    __tablename__ = 'holidays'

    id = Column(Integer, primary_key=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)

    holiday_type = Column(Enum(HolidayTypeEnum), nullable=False, default="paid")
    holiday_subtype = Column(Enum(HolidaySubtypeTypeEnum))

    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    @staticmethod
    def get_holiday(holiday_id):
        holiday = Holiday.query.filter_by(id=holiday_id).one_or_none()

        if not holiday:
            abort(404, message='Holiday not found')

        return holiday

    @staticmethod
    def get_holidays():
        employee = Holiday.query
        # Here apply filters
        return employee.all()

    @staticmethod
    def check_if_days_are_taken(start_date, end_date, holiday_type, instance):
        taken_days = Holiday.query.filter(Holiday.start_date <= start_date)
        taken_days = taken_days.filter(Holiday.end_date >= end_date)
        taken_days = taken_days.filter(Holiday.holiday_type == holiday_type)

        if instance:
            taken_days = taken_days.filter(Holiday.id != instance.id)

        taken_days = taken_days.all()
        return len(taken_days) > 0

    def save(self):
        start_date = str(self.start_date)
        end_date = str(self.end_date)

        ovl_holidays = Holiday.query.filter(or_(
            Holiday.start_date.between(start_date, end_date),
            Holiday.end_date.between(start_date, end_date)
        ))
        ovl_holidays = ovl_holidays.filter(Holiday.holiday_type == self.holiday_type)
        ovl_holidays = ovl_holidays.filter(Holiday.employee_id == self.employee_id)
        if self.id:
            ovl_holidays = ovl_holidays.filter(Holiday.id != self.id)
        ovl_holidays = ovl_holidays.all()

        #  Data is all good. I can save.
        if not ovl_holidays:
            self.session.add(self)
            self.session.commit()

        # Merge old overlapped holidays in the new one
        for old_holiday in ovl_holidays:
            if str(old_holiday.start_date) < start_date:
                self.start_date = str(old_holiday.start_date)

            if str(old_holiday.end_date) > end_date:
                self.end_date = str(old_holiday.end_date)

            old_holiday.delete()  # Delete overlapped records

        # Here check for contigous dates
        # @TODO
        self.session.add(self)
        self.session.commit()
