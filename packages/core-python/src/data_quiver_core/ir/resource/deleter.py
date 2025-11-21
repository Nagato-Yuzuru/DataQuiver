from typing import assert_never

from data_quiver_core.ir.base import IRBase
from data_quiver_core.ir.resource import ResourceSelector
from pydantic import Field, model_validator


class DropResource(IRBase):
    target_selector: ResourceSelector
    purge_physical: bool = Field(False, description="True: purge physical storage, like Kafka.False: just drop meta")

    @model_validator(mode="after")
    def no_where_protect_valid(self):
        if self.target_selector.exact_ids:
            return self
        if self.target_selector.filter:
            return self
        if self.target_selector.filter is None:
            raise ValueError("Must specify target resource, You close to *DROP ALL DATAS*")
        assert_never(self)


__all__ = ["DropResource"]
