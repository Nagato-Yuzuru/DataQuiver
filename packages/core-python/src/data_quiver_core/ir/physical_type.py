from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from datetime import date, datetime, time
from typing import Annotated, ClassVar, Literal, assert_never
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScalarTypeLabel = Literal["STRING", "INT", "FLOAT", "BOOL", "JSON", "DATE", "BYTES"]


class DataContainer(BaseModel, ABC):
    model_config = ConfigDict(frozen=True)
    _data_container_type: str

    @classmethod
    def is_scalar(cls) -> bool:
        return False


class ScalarType(DataContainer):
    label: ScalarTypeLabel
    _data_container_type: Literal["SCALAR_TYPE"] = Field("SCALAR_TYPE", init=False)

    @classmethod
    def is_scalar(cls) -> bool:
        return True


class TemporalType(DataContainer):
    _data_container_type: Literal["TEMPORAL_TYPE"] = Field("TEMPORAL_TYPE", init=False)

    variant: Literal["TIMESTAMPTZ", "TIMETZ"]

    # IANA Timezone String (e.g., "UTC", "Asia/Shanghai") or offset
    timezone: ZoneInfo = Field(ZoneInfo("UTC"), description="Must be a valid IANA timezone or 'UTC'")
    precision: Literal["s", "ms", "us", "ns"] = "ms"

    # @field_validator("timezone", mode="before")
    # @classmethod
    # def check_timezone(cls, v):
    #     try:
    #         ZoneInfo(v)
    #     except ValueError as e:
    #         raise ValueError(f"'{v}' is not a valid IANA timezone") from e
    #     return v


EnumerableLabel = Literal["STRING", "INT", "DATE"]

type ALLOWED_ENUM_TYPE = int | str | date | time | datetime


class EnumType[T: ALLOWED_ENUM_TYPE](DataContainer):
    __allowed_scalar_labels: ClassVar[set[str]] = {"STRING", "INT", "DATE", "TIMESTAMPTZ", "TIMETZ"}

    _data_container_type: Literal["ENUM_TYPE"] = Field("ENUM_TYPE", init=False)
    value_type: ScalarType | TemporalType
    values: Sequence[T] = Field(..., min_length=1)

    @model_validator(mode="after")
    def allowed_enum(self):  # noqa: PLR0912
        # match exhaustive
        first_value = self.values[0]
        match self.value_type:
            case ScalarType(label=label):
                if label not in self.__allowed_scalar_labels:
                    raise ValueError(f"Enum type {label} is not allowed")

                match label:
                    case "STRING":
                        if not isinstance(first_value, str):
                            raise ValueError("Enum type STRING must have string values")
                    case "INT":
                        if not isinstance(first_value, int):
                            raise ValueError("Enum type INT must have int values")
                    case "DATE":
                        if not isinstance(first_value, date):
                            raise ValueError("Enum type DATE must have date values")
                    case _:
                        assert_never(label)
            case TemporalType(variant=variant):
                # All temporal types allow
                match variant:
                    case "TIMESTAMPTZ":
                        if not isinstance(first_value, datetime):
                            raise ValueError("Enum type TIMESTAMPTZ must have datetime values")
                    case "TIMETZ":
                        if not isinstance(first_value, time):
                            raise ValueError("Enum type TIMETZ must have time values")
                    case _:
                        assert_never(variant)
            case _:
                assert_never(self.value_type)
        return self

    @classmethod
    def is_scalar(cls) -> bool:
        return True


class OptionType(DataContainer):
    value_type: PhysicalType
    _data_container_type: Literal["OPTION_TYPE"] = Field("OPTION_TYPE", init=False)

    @classmethod
    def is_scalar(cls) -> bool:
        return cls.value_type.is_scalar()


class UnionType(DataContainer):
    _data_container_type: Literal["UNION_TYPE"] = Field("UNION_TYPE", init=False)
    union_types: Sequence[PhysicalType]

    @classmethod
    def is_scalar(cls) -> bool:
        return all(u.is_scalar() for u in cls.union_types)


class RepeatedType(DataContainer):
    _data_container_type: Literal["LIST_TYPE"] = Field("LIST_TYPE", init=False)
    value_type: PhysicalType


class MapType(DataContainer):
    """
    Only support string keys
    """

    _data_container_type: Literal["MAP_TYPE"] = Field("MAP_TYPE", init=False)
    value_type: PhysicalType


PhysicalType = Annotated[
    ScalarType | OptionType | UnionType | RepeatedType | TemporalType | EnumType | MapType,
    Field(discriminator="_data_container_type"),
]

OptionType.model_rebuild()
UnionType.model_rebuild()
RepeatedType.model_rebuild()
MapType.model_rebuild()
