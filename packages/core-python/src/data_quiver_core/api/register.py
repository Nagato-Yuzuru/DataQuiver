from __future__ import annotations

from typing import Protocol

from data_quiver_core.ir.resource.resource_define import Namespace, ResourceID, ResourceTypeDefinition, ResourceTypeName


class RegistryBaseError(Exception): ...


class RegistryNotFoundError(RegistryBaseError):
    def __init__(self, ns: Namespace, type_name: ResourceTypeName):
        super().__init__(f"Registry not found for {ns}.{type_name}")
        self.ns = ns
        self.type_name = type_name


class RegistryDefMismatchError(RegistryBaseError):
    def __init__(self, resource_id: ResourceID):
        super().__init__(f"Resource ID is invalid: {resource_id}")
        self.resource_id = resource_id


class RegistryResourceAlreadyExistsError(RegistryBaseError):
    def __init__(self, exist_defn: ResourceTypeDefinition, defn: ResourceTypeDefinition):
        super().__init__(f"Resource already exists {exist_defn} vs {defn}")
        self.exist_defn = exist_defn
        self.defn = defn


class ResourceTypeRegister(Protocol):
    def register_resource(self, *defns: ResourceTypeDefinition):
        """
        :raises RegistryResourceAlreadyExistsError: if already registered
        """
        ...

    def get_definition(self, ns: Namespace, type_name: ResourceTypeName) -> ResourceTypeDefinition:
        """
        :raises RegistryNotFoundError: if not found in registered
        """
        ...

    def assert_resource_id_validate(self, resource_id: ResourceID):
        """
        :raises RegistryDefMismatchError: if invalid
        :raises RegistryNotFoundError: if not found in registered
        """
        ...
