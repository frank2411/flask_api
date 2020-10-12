import uuid

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import ValidationError, validates, validates_schema, post_load, fields  # noqa
from marshmallow_sqlalchemy.fields import Related

from work_api.models import db
from work_api.models import Team, Employee, Holiday

from sqlalchemy.orm.exc import NoResultFound


class FixedRelated(Related):  # pragma: no cover

    default_error_messages = {
        "invalid": "Could not deserialize related value {value!r}; "
        "expected a dictionary with keys {keys!r}",
        "not_found": "Related Object doesn't exist in DB",
        "invalid_uuid": "Not a valid UUID."
    }

    def _deserialize(self, value, *args, **kwargs):
        """Deserialize a serialized value to a model instance.
        If the parent schema is transient, create a new (transient) instance.
        Otherwise, attempt to find an existing instance in the database.
        :param value: The value to deserialize.
        """
        if not isinstance(value, dict):
            if len(self.related_keys) != 1:
                keys = [prop.key for prop in self.related_keys]
                raise self.make_error("invalid", value=value, keys=keys)
            value = {self.related_keys[0].key: value}
        if self.transient:
            return self.related_model(**value)

        if self.related_model.id.type.__str__() == "UUID":
            try:
                uuid.UUID(value["id"])
            except (ValueError, AttributeError, TypeError) as error:
                raise self.make_error("invalid_uuid") from error

        try:
            result = self._get_existing_instance(
                self.session.query(self.related_model), value
            )
        except NoResultFound:
            # The related-object DNE in the DB, but we still want to deserialize it
            # ...perhaps we want to add it to the DB later
            raise self.make_error("not_found")
        return result

    def _serialize(self, value, attr, obj):
        ret = {prop.key: getattr(value, prop.key, None) for prop in self.related_keys}

        # Little hack to prevent errors in uuid deserialization
        if isinstance(ret["id"], uuid.UUID):
            ret["id"] = str(ret["id"])

        return ret if len(ret) > 1 else list(ret.values())[0]


def base_validate_empty_string(schema, value):
    if not value:
        # check needed for empty string password because our lib doesn't validate it
        raise ValidationError(schema.error_messages["value_is_empty"])


class EmployeeSchema(SQLAlchemyAutoSchema):
    error_messages = {
        "value_is_empty": "Field cannot be empty",
    }

    team = FixedRelated(required=True)

    @validates("email")
    def validate_name(self, value):
        base_validate_empty_string(self, value)

    class Meta:
        model = Employee
        sqla_session = db.session
        load_instance = True


class TeamSchema(SQLAlchemyAutoSchema):
    error_messages = {
        "value_is_empty": "Field cannot be empty",
    }

    @validates("name")
    def validate_name(self, value):
        base_validate_empty_string(self, value)

    @validates("description")
    def validate_decription(self, value):
        base_validate_empty_string(self, value)

    class Meta:
        model = Team
        sqla_session = db.session
        load_instance = True


class HolidaySchema(SQLAlchemyAutoSchema):
    error_messages = {
        "start_date_bigger": "Start date cannot be bigger then End date",
        "days_already_taken": "Those days are already taken for this type of holiday",
        "type_not_permitted": "Holiday type not permitted",
        "subtype_not_permitted": "Holiday subtype not permitted",
    }

    def __init__(self, is_creation=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_creation = is_creation

    valid_types = ["paid", "unpaid"]
    valid_subtypes = [None, "rtt", "normal"]

    employee = FixedRelated(required=True)

    holiday_type = fields.Method("get_type_value", deserialize="validate_holiday_type")
    holiday_subtype = fields.Method("get_subtype_value", deserialize="validate_holiday_subtype")

    def get_type_value(self, obj):
        return obj.holiday_type.value

    def get_subtype_value(self, obj):
        try:
            value = obj.holiday_subtype.value
            return value
        except AttributeError:
            return None

    def validate_holiday_type(self, value):
        if value not in self.valid_types:
            raise ValidationError(self.error_messages["type_not_permitted"])
        return value

    def validate_holiday_subtype(self, value):
        if value not in self.valid_subtypes:
            raise ValidationError(self.error_messages["subtype_not_permitted"])
        return value

    @post_load
    def validate_types_and_subtypes(self, instance, **kwargs):
        instance_type = instance.holiday_type
        instance_subtype = instance.holiday_subtype

        if instance_type == "paid" and instance_subtype is None:
            instance.holiday_subtype = "normal"

        if instance_type == "unpaid" and instance_subtype:
            instance.holiday_subtype = None

        return instance

    @validates_schema
    def perfom_last_validations(self, data, **kwargs):
        start_date = data.get("start_date", None)
        end_date = data.get("end_date", None)
        holiday_type = data.get("holiday_type", None)

        if self.instance:
            start_date = data.get("start_date", self.instance.start_date)
            end_date = data.get("end_date", self.instance.end_date)
            holiday_type = data.get("holiday_type", self.instance.holiday_type.value)

        if (self.instance) and (start_date == self.instance.start_date) and (end_date == self.instance.end_date):
            return

        if start_date > end_date:
            raise ValidationError(self.error_messages["start_date_bigger"], "dates")

        if Holiday.check_if_days_are_taken(
            start_date, end_date, holiday_type, self.instance
        ):
            raise ValidationError(self.error_messages["days_already_taken"], "days")

    class Meta:
        model = Holiday
        sqla_session = db.session
        load_instance = True
