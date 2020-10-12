from .db import db

from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from flask_restful import abort


class Team(db.Model):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)

    employees = relationship(
        'Employee',
        backref='team',
        lazy='joined',
        cascade='all,delete-orphan',
        passive_deletes=True,
    )

    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    @staticmethod
    def get_team(team_id):
        team = Team.query.filter_by(id=team_id).one_or_none()

        if not team:
            abort(404, message='Team not found')

        return team

    @staticmethod
    def get_teams():
        teams = Team.query
        return teams.all()
