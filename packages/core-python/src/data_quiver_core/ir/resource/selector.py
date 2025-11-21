from collections.abc import Sequence, Set
from typing import Any, Literal

from data_quiver_core.ir.base import IRBase
from data_quiver_core.ir.resource import ResourceID
from pydantic import Field

type MetaFilterOperator = Literal["EQ", "NEQ", "GT", "LT", "GE", "LE", "IN", "CONTAINS", "LIKE"]


class MetadataExprNode(IRBase):
    pass


class MetaFilter(MetadataExprNode):
    attr: str
    op: MetaFilterOperator
    value: Any


class MetaFilterLogic(MetadataExprNode):
    op: Literal["AND", "OR", "NOT"]
    nodes: Sequence[MetadataExprNode] = Field(..., min_length=1)


class MetaOrder(IRBase):
    attrs: str = Field(..., description="Attribute to order by")
    direction: Literal["ASC", "DESC"] = Field(..., description="Order by ascending or descending")
    nulls_first: bool = Field(False, description="If nulls first or last")


class ResourceSelector(IRBase):
    exact_ids: Set[ResourceID] | None = Field(None, description="If give exact_ids, ignore other expr")
    filter: MetadataExprNode | None = Field(None, description="Filter by metadata")

    select_attrs: Sequence[str] = Field(default_factory=list, description="Select specific attributes within")
    order_by: Sequence[MetaOrder] = Field(default_factory=list, description="Order by, default by resource id")

    limit: int | None = Field(100, description="Limit the number of resources", ge=1)
    offset: int = Field(default=0, ge=0)


__all__ = ["ResourceSelector", "MetaFilter", "MetaFilterLogic", "MetaOrder"]
