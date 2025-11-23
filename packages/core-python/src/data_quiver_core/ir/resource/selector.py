from __future__ import annotations

from collections.abc import Sequence, Set
from typing import Annotated, Any, Literal

from data_quiver_core.ir.base import IRBase, UnionIRBase
from data_quiver_core.ir.resource import ResourceID
from pydantic import Field, model_validator

type MetaFilterOperator = Literal["EQ", "NEQ", "GT", "LT", "GE", "LE", "IN", "CONTAINS", "LIKE"]


class MetadataExprNode(UnionIRBase):
    pass


class MetaFilter(MetadataExprNode):
    _union_eigen_type: Literal["resource.selector.meta_filter"] = Field("resource.selector.meta_filter", init=False)

    attr: str
    op: MetaFilterOperator
    value: Any


class MetaFilterLogic(MetadataExprNode):
    _union_eigen_type: Literal["resource.selector.meta_filter_logic"] = Field(
        "resource.selector.meta_filter_logic", init=False
    )
    op: Literal["AND", "OR", "NOT"]
    # NOTE: Use N-Array pattern not binary tree cause to optimization, low cost to merge same expr
    nodes: Sequence[UnionMetaFilterNode] = Field(..., min_length=1)

    @model_validator(mode="after")
    def nodes_count_valid(self):
        if self.op == "NOT" and len(self.nodes) != 1:
            raise ValueError("NOT must have exactly one child")
        return self


# TODO: runtime check attr and Filter physical type
type UnionMetaFilterNode = Annotated[MetaFilter | MetaFilterLogic, Field(discriminator="_union_eigen_type")]


class MetaOrder(IRBase):
    attrs: str = Field(..., description="Attribute to order by")
    direction: Literal["ASC", "DESC"] = Field(..., description="Order by ascending or descending")
    nulls_first: bool = Field(False, description="If nulls first or last")
    # TODO: add order func to custom


class ResourceSelector(IRBase):
    exact_ids: Set[ResourceID] | None = Field(None, description="If give exact_ids, ignore other expr")
    filter: UnionMetaFilterNode | None = Field(None, description="Filter by metadata")

    select_attrs: Sequence[str] = Field(default_factory=list, description="Select specific attributes within")
    order_by: Sequence[MetaOrder] = Field(default_factory=list, description="Order by, default by resource id")

    limit: int | None = Field(100, description="Limit the number of resources", ge=1)
    offset: int = Field(default=0, ge=0)


# ref instance
MetaFilterLogic.model_rebuild()

__all__ = ["ResourceSelector", "MetaFilter", "MetaFilterLogic", "MetaOrder"]
