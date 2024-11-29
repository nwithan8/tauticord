from functools import wraps
from typing import List

from sqlalchemy import create_engine, MetaData, null
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database


def no_none(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """
        Throw exception if any values are None
        """
        func(self, *args, **kwargs)
        for k, v in self.__dict__.items():
            if v is None:
                raise Exception(f"None value for {k}")

    return wrapper


def none_as_null(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """
        Replace None as null()
        """
        func(self, *args, **kwargs)
        for k, v in self.__dict__.items():
            if v is None:
                setattr(self, k, null())

    return wrapper


def map_attributes(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """
        Map kwargs to class attributes
        """
        func(self, *args, **kwargs)
        for k, v in kwargs.items():
            if getattr(self, k):
                setattr(self, k, v)

    return wrapper


def false_if_error(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """
        Return False if error encountered in function, instead of raising exception
        """
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            return False

    return wrapper


class SQLAlchemyDatabase:
    def __init__(self,
                 sqlite_file: str):
        self.sqlite_file = sqlite_file

        self.engine = None
        self.session = None

        self.url = f'sqlite:///{sqlite_file}'

        self._setup()

    def _commit(self):
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to commit session: {e}")

    def _rollback(self):
        try:
            self.session.rollback()
        except Exception as e:
            raise Exception(f"Failed to rollback session: {e}")

    def _close(self):
        self.session.close()

    def _setup(self):
        if not self.url:
            return

        self.engine = create_engine(self.url)

        if not self.engine:
            return

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        MetaData().create_all(self.engine)

        _session = sessionmaker()
        _session.configure(bind=self.engine)
        self.session = _session()

    def _build_query(self, table_schema, *filters):
        query = self.session.query(table_schema)
        if filters:
            query = query.filter(*filters)
        return query

    def _get_first_entry(self, table_schema, *filters) -> None | object:
        query = self._build_query(table_schema, *filters)

        return query.first()

    def _get_all_entries(self, table_schema, *filters) -> List[object]:
        query = self._build_query(table_schema, *filters)

        return query.all()

    def _get_attribute_from_first_entry(self, table_schema, field_name, *filters) -> None | object:
        entry = self._get_first_entry(table_schema=table_schema, *filters)

        return getattr(entry, field_name, None)

    def _get_attribute_from_all_entries(self, table_schema, field_name, *filters) -> List[object]:
        entries = self._get_all_entries(table_schema=table_schema, *filters)

        return [getattr(entry, field_name, None) for entry in entries]

    def _set_attribute_of_first_entry(self, table_schema, field_name, field_value, *filters) -> bool:
        entry = self._get_first_entry(table_schema=table_schema, *filters)

        if not entry:
            entry = self._create_entry(table_schema, **{field_name: field_value})

        return self._update_entry_single_field(entry, field_name, field_value)

    def _set_attribute_of_all_entries(self, table_schema, field_name, field_value, *filters) -> bool:
        entries = self._get_all_entries(table_schema=table_schema, *filters)

        if not entries:
            entries = [self._create_entry(table_schema, **{field_name: field_value})]

        return all([self._update_entry_single_field(entry, field_name, field_value) for entry in entries])

    @false_if_error
    def _create_entry(self, table_schema, **kwargs) -> object:
        entry = table_schema(**kwargs)
        self.session.add(entry)
        self._commit()
        return entry

    @false_if_error
    def _create_entry_if_does_not_exist(self, table_schema, fields_to_check: List[str], **kwargs) -> object:
        filters = {k: v for k, v in kwargs.items() if k in fields_to_check}
        entries = self._get_all_entries(table_schema=table_schema, *filters)
        if not entries:
            return self._create_entry(table_schema=table_schema, **kwargs)
        return entries[0]

    def _create_entry_fail_if_exists(self, table_schema, fields_to_check: List[str], **kwargs) -> object:
        filters = {k: v for k, v in kwargs.items() if k in fields_to_check}
        entries = self._get_all_entries(table_schema=table_schema, *filters)
        # TODO: Different exception types (duplicate record vs connection error), parse downstream
        if entries:
            raise Exception(f"Entry already exists for {kwargs}")
        return self._create_entry(table_schema=table_schema, **kwargs)

    @false_if_error
    def _update_entry_single_field(self, entry, field_name, field_value) -> bool:
        setattr(entry, field_name, field_value)
        self._commit()
        return True

    @false_if_error
    def _update_entry_multiple_fields(self, entry, **kwargs) -> bool:
        for field, value in kwargs.items():
            setattr(entry, field, value)
        self._commit()
        return True


class CustomTable:
    def __init__(self):
        self._ignore = []
