from abc import ABC
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class IRBase(BaseModel, ABC):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SemanticType(StrEnum):
    def __new__(cls, value: str, desc: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.desc = desc
        return obj

    UNKNOWN = "UNKNOWN", "Unknown semantic type"
    METRIC = "METRIC", "Metric"
    DIMENSION = "DIMENSION", "Dimension (group & filter)"
    TIME = "TIME", "All aware time, do not must native time"
    GEO_POINT = "GEO_POINT", "Geo Point"
    GEO_POLYGON = "GEO_POLYGON", "Geo Polygon"
    IDENTITY = "IDENTITY", "Identity tuple"


