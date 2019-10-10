import os
import logging
import tempfile
from git import Repo
from urllib.parse import urlparse

import chart_builder.utils.helper as helper
from chart_builder.utils.exceptions import StorageError

LOG = logging.getLogger(__name__)


class LocalDir(object):
    def __init__(self, path):
        self.source_path = path

    def read(self, path):
        file_path = os.path.join(self.source_path, path)
        return helper.read_file(file_path)

    def write(self, path, content):
        file_path = os.path.join(self.source_path, path)
        helper.write_file(file_path, content)

    def touch(self, path):
        file_path = os.path.join(self.source_path, path)
        if os.path.isfile(file_path):
            return

        default_content = ""
        if path == ".helmignore":
            default_content = helper.get_default_helm_ignore()
        helper.write_file(file_path, default_content)

    def mkdir(self, sub_path):
        dir_path = os.path.join(self.source_path, sub_path)
        if os.path.exists(dir_path):
            return
        os.mkdir(dir_path)

    def push(self):
        LOG.warning("Do push chart to nowhere")


class _TmpDir(LocalDir):
    def __init__(self):
        self._tmp_dir = tempfile.mkdtemp(prefix='chartbuilder-')
        LOG.info("Create tempdir: {}".format(self._tmp_dir))
        super(_TmpDir, self).__init__(self._tmp_dir)

    def __del__(self):
        os.rmdir(self._tmp_dir)


class GitRepo(_TmpDir):

    def __init__(self, repo_url, branch, path):
        super(GitRepo, self).__init__()
        self.repo_url = repo_url
        self.branch = branch
        self.git_repo = None

        self.source_path = os.path.join(self._tmp_dir, path)

    def clone(self):
        repo = Repo.clone_from(
            url=self.repo_url,
            to_path=self._tmp_dir,
            branch=self.branch
        )
        self.git_repo = repo
        LOG.info("Git clone repo {} to {}".format(
            self.repo_url, self._tmp_dir))

    def git_commit(self):
        self.git_repo.git.add(u=True)
        self.git_repo.index.commit('Update Helm Chart by ChartBuilder.')

    def git_push(self):
        remote = self.git_repo.remote()
        remote.pull()
        remote.push()

    def push(self):
        self.git_commit()
        self.git_push()


class ChartRepo(_TmpDir):
    def __init__(self, repo_url, chart, **kwargs):
        super(ChartRepo, self).__init__()
        repo_scheme = urlparse(repo_url).scheme

        self.repo_schema = repo_scheme
        self.repo_url = repo_url
        self.chart = chart

        self._get_from_repo()

    def _get_from_repo(self):
        raise StorageError("repo", "Get from repo is not support yet")

    def _get_from_s3(self, repo_url, file_url):
        raise StorageError("repo", "S3 is not support yet")

    def _get_from_http(self, repo_url, file_url):
        raise StorageError("repo", "HTTP is not support yet")


class Storage(object):

    def __init__(self, storage_type, source: dict = None):
        self.sub_path = source.get("sub_path") or ''

        if storage_type == "local":
            try:
                self.work_dir = LocalDir(source['path'])
            except KeyError:
                raise StorageError(storage_type, "Source args: path")

        elif storage_type == "git":
            try:
                self.work_dir = GitRepo(
                    repo_url=source['git_url'],
                    branch=source.get('branch') or 'master',
                    path=source.get('path') or '',
                )
            except KeyError:
                raise StorageError(storage_type, "Source args: git_url, branch, path")

        elif storage_type == "repo":
            try:
                self.work_dir = ChartRepo(
                    repo_url=source['repo_url'],
                    chart=source['chart'],
                    version=source.get('version'),
                    headers=source.get('headers'),
                )
            except KeyError:
                raise StorageError(storage_type, "Source args: repo_url, chart, version, headers")

        else:
            raise StorageError(storage_type, "Do not found {} type".format(storage_type))

        self.source_path = os.path.join(self.work_dir.source_path, self.sub_path)

    def read(self, file_name):
        return self.work_dir.read(file_name)

    def write(self, file_name, content):
        self.work_dir.write(file_name, content)

    def init_workdir(self):
        self.work_dir.mkdir("charts")
        self.work_dir.mkdir("templates")

        self.work_dir.touch(".helmignore")
        self.work_dir.touch("Chart.yaml")
        self.work_dir.touch("values.yaml")
        self.work_dir.touch("README.md")
        self.work_dir.touch("templates/NOTES.txt")
