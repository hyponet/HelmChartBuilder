from unittest import TestCase, mock

from chart_builder.storage import Storage

MKDTEMP = mock.Mock(return_value="/tmp/chartbuilder-xxx")
RMDTEMP = mock.MagicMock()


class TestStorage(TestCase):

    def setUp(self):
        MKDTEMP.reset_mock()
        RMDTEMP.reset_mock()

    def test_local_dir(self):
        storage_type = "local"
        source = {
            "path": "/home/hypo/workdir",
            "sub_path": "v1"
        }

        storage = Storage(
            storage_type=storage_type,
            source=source,
        )
        self.assertEqual(
            storage.source_path,
            "/home/hypo/workdir/v1"
        )

    @mock.patch("git.Repo.clone_from")
    @mock.patch("tempfile.mkdtemp", new=MKDTEMP)
    @mock.patch("os.rmdir", new=RMDTEMP)
    def test_git_repo(self, *args):
        storage_type = "git"
        source = {
            "git_url": "https://git.hypo.vim/helm/chart",
            "branch": "master",
            "path": "charts/nginx",
            "sub_path": "v1"
        }

        MKDTEMP.assert_not_called()
        storage = Storage(
            storage_type=storage_type,
            source=source,
        )
        MKDTEMP.assert_called_once()

        self.assertEqual(
            storage.source_path,
            "/tmp/chartbuilder-xxx/charts/nginx/v1"
        )

        RMDTEMP.assert_not_called()
        del storage
        RMDTEMP.assert_called_once()

    def test_chart_repo(self):
        pass
