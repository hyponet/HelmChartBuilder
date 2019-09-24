class BadBuildAction(Exception):
    pass


class StorageError(BadBuildAction):
    def __init__(self, storage_type, msg):
        super(StorageError, self).__init__(
            "Init {} Storage error: {}".format(storage_type, msg))


class TemplateGenError(BadBuildAction):
    def __init__(self, resource_type, msg):
        super(TemplateGenError, self).__init__(
            "Gen {} yaml template error: {}".format(resource_type, msg))


class DateSchemaValidationError(BadBuildAction):
    def __init__(self, resource_name, msg):
        super(DateSchemaValidationError, self).__init__(
            "Resource {}  date schema validation error: {}".format(resource_name, msg))
