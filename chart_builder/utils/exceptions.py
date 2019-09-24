class BadBuildAction(Exception):
    pass


class StorageError(BadBuildAction):
    def __init__(self, storage_type, msg):
        super(StorageError, self).__init__(
            "Init {} Storage error: {}".format(storage_type, msg))
