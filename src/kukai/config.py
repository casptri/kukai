from pathlib import Path
import toml

from kukai.helper import merge_nested


class KukaiConfig:
    _global_config_file = Path("/etc/kukai/config/kukai.toml")
    _local_config_file = Path.home() / ".config" / "kukai" / "kukai.toml"

    def __init__(self):
        self.data = self._import_data()

    def _import_data(self) -> dict:
        global_data = {}
        local_data = {}
        if self._global_config_file.exists():
            with self._global_config_file.open("r") as fd:
                global_data = toml.load(fd)
        if self._local_config_file.exists():
            with self._local_config_file.open("r") as fd:
                local_data = toml.load(fd)
        data = merge_nested(global_data, local_data)
        return data

    def _get_config_file(self) -> Path:
        if not self._local_config_file.exists():
            self._local_config_file.parent.mkdir(parents=True, exist_ok=True)
            self._local_config_file.touch()
        repo_conf = self._local_config_file
        return repo_conf

    def add_repo(self, config_file: Path) -> bool:
        config_path = Path(config_file)
        if self._check_exists(config_path):
            return False
        repo_config = self._get_config_file()
        with repo_config.open("r") as fd:
            data = toml.load(fd)
        new_entry = {"kukai": {"location": [str(config_path.resolve())]}}
        new_data = merge_nested(data, new_entry)
        with repo_config.open("w") as fd:
            toml.dump(new_data, fd)
        data = self._import_data()
        return True

    def _get_repo_config(self, config_file: Path) -> list:
        repo_list = []
        with config_file.open("r") as fd:
            data = toml.load(fd)
        repo_list += [{"location": str(config_file.resolve()), "data": data}]
        for repo in data.get("kukai", {}).get("location", []):
            repo_path = Path(repo)
            if repo_path.is_file():
                repo_list += self._get_repo_config(Path(repo))
            else:
                repo_list += self._get_repo_config(Path(repo) / "kukai.toml")
        return repo_list

    def _check_exists(self, config_file: Path) -> bool:
        repos = self.get_repos()
        for repo in repos:
            if repo.get("location") == str(config_file.resolve()):
                return True
        return False

    def get_repos(self) -> list:
        data = []
        if self._local_config_file.exists():
            data += self._get_repo_config(self._local_config_file)
        if self._global_config_file.exists():
            data += self._get_repo_config(self._global_config_file)
        return data
