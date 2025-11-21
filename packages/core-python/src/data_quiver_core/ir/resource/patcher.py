from collections.abc import Sequence
from typing import Literal

from data_quiver_core.ir.base import IRBase
from data_quiver_core.ir.resource import ResourceID
from pydantic import Field, Json


class PatchMetaOp(IRBase):
    op_type: str


class SetAttribute(PatchMetaOp):
    op_type: Literal["SET_ATTR"] = Field("SET_ATTR", init=False)
    key: str
    value: Json


class DeleteAttribute(PatchMetaOp):
    op_type: Literal["DELETE_ATTR"] = Field("DELETE_ATTR", init=False)
    key: str


class PatchResource(IRBase):
    target: ResourceID
    ops: Sequence[PatchMetaOp] = Field(..., min_length=1)

    expected_version: str | None = Field(None, description="Optimistic lock to CAS.")


__all__ = ["PatchResource", "SetAttribute", "DeleteAttribute"]
