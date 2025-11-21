from data_quiver_core.api.register import ResourceTypeRegister


class ResourceTypeRegistry(ResourceTypeRegister):
    """
    sdk启动的时候注册类型到 core, api部分持有 register 实例对入参校验
    """

    ...
