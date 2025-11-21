from __future__ import annotations

from collections.abc import Mapping, Set
from typing import Any, Literal, NewType

from data_quiver_core.ir.base import IRBase, SemanticType
from pydantic import Field, Json, model_validator

Namespace = NewType("Namespace", str)
ResourceTypeName = NewType("ResourceTypeName", str)


class AttributeDef(IRBase):
    name: str
    type: Literal["STRING", "INT", "FLOAT", "BOOL", "JSON", "TIME", "DATETIME", "DATE"]

    description: str | None = None
    required: bool = Field(
        ...,
        description="True: is identity_attrs, must have and must is a scalar. "
        "False: optional, just description to read or filter ",
    )
    default: Any | None = Field(None, description="Default value, only used when required is False")
    repeated: bool = Field(False, description="True: container. False: single value")
    allowed_values: list[Any] | None = Field(None, description="Allowed values, only used when type is ENUM")

    is_map: bool = Field(False, description="True: map, False: scalar. The key is and only is string")

    @model_validator(mode="after")
    def attr_valid(self):
        if self.required:
            if self.repeated or self.is_map:
                raise ValueError("Identity attrs must be a scalar")
            if self.type == "JSON":
                raise ValueError("Identity attrs must be a scalar, not support JSON")
        if self.repeated and self.is_map:
            raise ValueError("Repeated map is not supported")

        return self


class ResourceTypeDefinition(IRBase):
    namespace: Namespace
    type_name: ResourceTypeName = Field(..., description="Type name, e.g. 'GRID', 'TABLE' 'Module', 'Weather' ")
    description: str | None = Field(None)

    identity_attrs: Mapping[str, AttributeDef] = Field(default_factory=dict)
    description_attrs: Mapping[str, AttributeDef] = Field(default_factory=dict)

    all_shape_fields: Mapping[str, DataShapeField] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_attrs_def(self):
        self._check_map_consistency(self.identity_attrs, "Identity attribute", "name")
        for key, attr in self.identity_attrs.items():
            if not attr.required:
                raise ValueError(f"Identity attribute '{key}' must be required")

        self._check_map_consistency(self.description_attrs, "Description attribute", "name")
        for key, attr in self.description_attrs.items():
            if attr.required:
                raise ValueError(f"Description attribute '{key}' must NOT be required")

        self._check_map_consistency(self.all_shape_fields, "Shape field", "name")

        return self

    @staticmethod
    def _check_map_consistency(mapping: Mapping[str, Any], type_name: str, item_field_name):
        """Helper to validate that dictionary keys match object names."""
        for key, item in mapping.items():
            if key != getattr(item, item_field_name):
                raise ValueError(f"{type_name} mismatch: key '{key}' != name '{item.name}'")


class ResourceID(IRBase):
    """
    Data IDs are not unique across the entire system.
    Use struct id.
    """

    namespace: Namespace
    type: ResourceTypeName = Field(..., description="Type, e.g. 'GRID', 'TABLE' 'Module', 'Weather' ")
    id: str = Field(..., description="In namespace and type unique ID")
    identity_attrs: Mapping[str, Json] = Field(default_factory=dict)
    version: str | None = Field(None, description="Version, default to latest")

    def __str__(self):
        v = self.version if self.version is not None else "latest"

        identity_attrs = "::".join([f"{k}@{v}" for k, v in sorted(self.identity_attrs.items())])
        return f"{self.namespace}::{self.type}::{self.id}::{identity_attrs}::@{v}"


class DataShapeField(IRBase):
    """
    A field within a data resource, like timestamp,
    """

    name: str = Field(..., description="Name of the field, e.g. 'timestamp', 'value', 'horizon' ")
    semantic_type: SemanticType
    physical_type: str = Field(
        ..., description="Physical type, e.g. 'datetime', 'int64'. Do not parse in core, just trans to plugin"
    )
    description: str | None = Field(None)


class ResourceShape(IRBase):
    """
    Shape of a data resource, same types of resource should have the same shapes
    """

    fields: Mapping[str, DataShapeField] = Field(default_factory=dict)

    primary_dimensions: Set[str] = Field(
        default_factory=Set,
        description="Allow slicing dimension on data, e.g. {'timestamp'}. Must be subset of fields",
    )

    @model_validator(mode="after")
    def check_primary_dimensions(self):
        if not (set(self.primary_dimensions) <= self.fields.keys()):
            raise ValueError("Primary dimensions must be subset of fields")
        return self


class ResourceDescriptorIR(IRBase):
    """
    Catalog return
    include:

    1. what data type (shape)
    2. who data (id / meta / attr)
    """

    id: ResourceID
    shape: ResourceShape
    attrs: Mapping[str, Any] = Field(default_factory=dict)
    storage_config: dict[str, Any] = Field(
        default_factory=dict, description="Storage config for data, core don't parse"
    )


__all__ = [
    "ResourceID",
    "DataShapeField",
    "ResourceDescriptorIR",
    "ResourceShape",
    "AttributeDef",
    "ResourceTypeDefinition",
    "Namespace",
    "ResourceTypeName",
]
