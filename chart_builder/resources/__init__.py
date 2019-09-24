class ResourceTemplate(object):

    def __init__(self, service_name=None, labels=None):
        self.service_name = service_name
        self.labels = labels

        self.hasBuild = False
        self._template = None
        self._values = None

    def gen_deployment(self, deployment):
        pass

    def gen_kube_service(self, kube_service):
        pass

    def gen_configmap(self, configmap):
        pass

    def get_template(self):
        assert self.hasBuild
        return self._template

    def update_values(self, values):
        assert self.hasBuild
        return self._values
