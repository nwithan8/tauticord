from typing import List

from sqlalchemy.orm import DeclarativeMeta

from modules.database.base.imports import *
from modules.utils import convert_string_to_bool

Base = declarative_base()


def get_table_schema_name(table: DeclarativeMeta) -> str:
    return getattr(table, "__name__", None)


def get_table_columns(table: Table) -> List[Column]:
    return table.columns._all_columns


def get_table_column_names(table: Table) -> List[str]:
    columns = get_table_columns(table=table)
    return [column.name for column in columns]


def table_schema_to_name_type_pairs(table: Table):
    columns = get_table_columns(table=table)
    pairs = {}
    ignore_columns = getattr(table, "_ignore", [])
    for column in columns:
        if column not in ignore_columns:
            pairs[column.name] = sql_type_to_human_type_string(column.type)
    return pairs


def sql_type_to_human_type_string(sql_type) -> str:
    if not hasattr(sql_type, "python_type"):
        return ""

    python_type = sql_type.python_type
    if python_type == str:
        return "String"
    elif python_type in [int, float]:
        return "Number"
    elif python_type == bool:
        return "True/False"
    return ""


def human_type_to_python_type(human_type: str):
    try:
        return float(human_type)  # is it a float?
    except:
        try:
            return int(human_type)  # is it an int?
        except:
            bool_value = convert_string_to_bool(bool_string=human_type)
            if bool_value is not None:  # is it a bool?
                return bool_value
            else:
                return human_type  # it's a string
