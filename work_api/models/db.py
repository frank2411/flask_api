import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.Model.metadata.create_all(db.get_engine())


@click.command("drop-db")
@with_appcontext
def drop_db_command():
    db.Model.metadata.drop_all(db.get_engine())


@click.command("populate-db")
@with_appcontext
def populate_db_command():
    from work_api.models import Team, Holiday, Employee

    team = Team(
        name="Test Team 1",
        description="Test Team 1 description"
    )
    team.save()

    employee = Employee(
        email="test@email.com",
        team_id=team.id
    )
    employee.save()

    unpaid_holiday = Holiday(
        start_date="2020-10-10",
        end_date="2020-10-12",
        employee_id=employee.id,
        holiday_type="unpaid"
    )
    unpaid_holiday.save()

    paid_holiday_normal = Holiday(
        start_date="2020-10-10",
        end_date="2020-10-15",
        employee_id=employee.id,
        holiday_type="paid",
        holiday_subtype="normal"
    )
    paid_holiday_normal.save()

    paid_holiday_normal_2 = Holiday(
        start_date="2020-10-15",
        end_date="2020-10-17",
        employee_id=employee.id,
        holiday_type="paid",
        holiday_subtype="normal"
    )
    paid_holiday_normal_2.save()

    click.echo("done")


@click.command("test-db")
@with_appcontext
def test_db():
    from work_api.models import Holiday
    from sqlalchemy import or_

    # Overlapping works.
    n = Holiday(
        start_date="2020-10-11",
        end_date="2020-10-17",
        employee_id=1,
        holiday_type="paid"
    )

    s_date = "2020-10-10"
    e_date = "2020-10-17"

    ol_holidays = Holiday.query.filter(or_(
        Holiday.start_date.between(s_date, e_date),
        Holiday.end_date.between(s_date, e_date)
    ))
    ol_holidays = ol_holidays.filter(Holiday.holiday_type == "paid")
    ol_holidays = ol_holidays.filter(Holiday.employee_id == n.employee_id)
    ol_holidays = ol_holidays.all()

    for ho in ol_holidays:
        if str(ho.start_date) < n.start_date:
            n.start_date = str(ho.start_date)

        if str(ho.end_date) > n.end_date:
            n.end_date = str(ho.end_date)

        ho.delete()

    n.save()


class Model:
    __abstract__ = True

    session = None
    query = None

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        identity = inspect(self).identity

        if identity is None:
            pk = f"(transient {id(self)})"
        else:
            pk = ", ".join(str(value) for value in identity)

        return f"<{type(self).__name__} {pk}>"


class DynamicBindSession(Session):

    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def get_bind(self, mapper=None, clause=None):
        """Return the engine or connection for a given model"""

        if self.bind:
            return self.bind

        # Get default engine
        return self.db.get_engine()


class DBConfig:

    def __init__(self, app=None):
        self.engine = None
        self.app = app
        self.session = self.get_session()
        self.model_class = Model
        self.Model = self.make_declarative_base(self.model_class)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.teardown_appcontext(self.cleanup)
        app.cli.add_command(init_db_command)
        app.cli.add_command(drop_db_command)
        app.cli.add_command(populate_db_command)
        app.cli.add_command(test_db)

    def cleanup(self, resp_or_exc):
        if self.session:
            self.session.remove()
        return resp_or_exc

    def init_db(self):
        self.Model.metadata.create_all(self.get_engine())

    def drop_db(self):
        self.Model.metadata.drop_all(self.get_engine())

    # We must set the engine in the session class. Since we have to wait for the
    # application context to be loaded in order to have the right configs
    def get_engine(self, is_query=True):
        if self.engine:
            return self.engine

        self.engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
        return self.engine

    def get_session(self, bind=None):
        self.session = scoped_session(sessionmaker(class_=DynamicBindSession, db=self, bind=None))
        return self.session

    def make_declarative_base(self, model, metadata=None):
        model = declarative_base(cls=model, name="Model")
        model.session = self.session
        model.query = self.session.query_property()
        return model


db = DBConfig()
