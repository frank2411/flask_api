from .db import db

from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from flask_restful import abort


class Employee(db.Model):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)

    holidays = relationship(
        'Holiday',
        backref='employee',
        lazy='joined',
        cascade='all,delete-orphan',
        passive_deletes=True
    )

    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    @staticmethod
    def get_employee(employee_id):
        employee = Employee.query.filter_by(id=employee_id).one_or_none()

        if not employee:
            abort(404, message='Employee not found')

        return employee

    @staticmethod
    def get_employees():
        employee = Employee.query
        # Here apply filters
        return employee.all()
