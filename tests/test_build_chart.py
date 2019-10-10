from unittest import TestCase, mock
from chart_builder import Builder


class FakeRepo(object):
    def __init__(self, path):
        self.source_path = path

    def read(self, path):
        return ""

    def write(self, path, content):
        pass

    def touch(self, path):
        pass

    def mkdir(self, sub_path):
        pass

    def push(self):
        pass


class TestBuildChart(TestCase):
    def setUp(self):
        self.storage_patch = mock.patch("chart_builder.storage.LocalDir", new=FakeRepo)
        self.storage = {"type": "local", "source": {"path": "/test"}}

        self.storage_patch.start()

    def tearDown(self):
        self.storage_patch.stop()

    def test_builder(self):
        builder = Builder(
            "testChart",
            version="1.0",
            app_version="1.0",
            description="",
            storage=self.storage,
        )
        builder.build_chart()
