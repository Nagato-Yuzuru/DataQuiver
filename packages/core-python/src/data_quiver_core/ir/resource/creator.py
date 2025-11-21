from typing import Literal

from data_quiver_core.ir.base import IRBase
from data_quiver_core.ir.resource import ResourceDescriptorIR
from pydantic import Field


class RegisterResource(IRBase):
    descriptor: ResourceDescriptorIR
    if_exists: Literal["FAIL", "REPLACE", "IGNORE"] = "FAIL"
    auto_provision: bool = Field(
        False, description="True: try to provision to physical storage, like Kafka. False: just Register meta"
    )

__all__ = ["RegisterResource"]