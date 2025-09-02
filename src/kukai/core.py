import sys
from pathlib import Path
from enum import Enum
import toml
import Levenshtein as leven

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

from kukai.config import KukaiConfig
from kukai.engine import CookieEngine, FileEngine
from kukai.context import ContextParser


class RepoType(Enum):
    UNKNOWN = 0
    COOKIECUTTER = 1
    KUKAI = 2

    @classmethod
    def from_string(cls, engine: str) -> Self:
        match engine:
            case "cc":
                return cls.COOKIECUTTER
            case "file":
                return cls.KUKAI
            case _:
                return cls.UNKNOWN


class KukaiTemplate:
    """Representation of a Template

    This class provides all necessary info and methods to generate a template.

    Attributes:
        name (str): Human readable representation of template
        tags (list[str]): Tags to identify template
        group (str): Group the template is embedded in
        default_context (dict): Context provided by template
        context (dict): Active context of template
        location (str): Location where template data is stored
    """

    _used_values = set()

    name = ""
    template_type: RepoType = RepoType.UNKNOWN
    tags: list[str]
    group: str
    _location: str = ""
    data: dict
    default_context: dict
    context: dict
    mapping: dict

    @classmethod
    def exists(cls, value: dict | str | Path) -> bool:
        match value:
            case dict():
                location = value["location"]
            case _:
                location = str(value)
        if location in cls._used_values:
            return True
        else:
            return False

    def __init__(self, data: dict) -> None:
        self.context = {}
        self.default_context = {}
        self.data = data
        self.tags = data.get("tags", [])
        self.group = data.get("group", "")
        loc = data.get("location")
        if loc:
            self.location = loc
        if self._location:
            self.name = Path(self.location).stem

    def __del__(self):
        self._used_values.discard(str(self._location))

    @property
    def location(self) -> str:
        return self._location

    @location.setter
    def location(self, value: str | Path) -> None:
        if str(value) in self._used_values:
            raise ValueError(f"{value} already exists")
        self._used_values.add(str(value))
        self._location = Path(value)

    def __str__(self) -> str:
        return f"{self.name}: group: {self.group} tags: {self.tags} location: {self.location}"
        return self.name + ": " + str(self.data)

    def add_tags(self, tags: list[str]) -> None:
        self.tags = list(set(self.tags) | set(tags))

    def add_mapping(self, data: dict) -> None:
        self.add_tags(data.get("tags", []))
        self.mapping = data

    def create(self, dest_path: str | Path, context: dict) -> None:
        """Create the template

        Args:
            dest_path: Destination path where the template will be generated
            context: Context to generate template with
        """
        match self.template_type:
            case RepoType.KUKAI:
                name_key = self.mapping.get("name_key")
                FileEngine.create(Path(self.location), dest_path, context, name_key)
            case RepoType.COOKIECUTTER:
                CookieEngine.create(self.location, dest_path, context)
            case _:
                raise ValueError("No enigne found for this kind of repo")

    def get_context(self) -> ContextParser:
        match self.template_type:
            case RepoType.KUKAI:
                context_file = self.location.parent / "kukai.toml"
            case RepoType.COOKIECUTTER:
                context_file = self.location / "cookiecutter.json"
            case _:
                raise ValueError("Unknown template type")
        return ContextParser(context_file)


class KukaiRepo:
    """Representation of a Repository"""

    _templates = []

    def __init__(self, location: Path | str) -> None:
        self._templates = []
        if Path(location).is_file():
            kukai_file = Path(location)
        else:
            kukai_file = Path(location) / "kukai.toml"
        if not kukai_file.exists():
            raise FileNotFoundError(f"{kukai_file} does not exist")
        self._location = kukai_file
        with kukai_file.open("r") as fd:
            self.data = toml.load(fd)
        kukai_data = self.data.get("kukai", {})

        for template in kukai_data.get("template", []):
            if not KukaiTemplate.exists(template):
                self._templates.append(KukaiTemplate(template))

        repo_location = kukai_data.get("location", [])
        for location in repo_location:
            repo = KukaiRepo(location)
            templates = repo.get_templates()
            self._templates += templates

        repo_data = kukai_data.get("repo")
        if repo_data:
            self._templates += self._parse_repo(repo_data)

    def _parse_location(self, engine: str) -> list:
        folder = self._location.parent
        files = []
        match engine:
            case "cc":
                files = [file for file in folder.iterdir() if file.is_dir()]
            case "file":
                files = [file for file in folder.iterdir() if file.is_file()]
        return files

    def _get_mapping(self, name: str, data: dict) -> dict:
        mapping_data = data.get("mapping", [])
        for mapping in mapping_data:
            if mapping.get("name") == name:
                return mapping
        return {}

    def _create_template(self, location: Path, data: dict) -> KukaiTemplate:
        template = KukaiTemplate(data)
        template_type = data.get("engine", "")
        template.template_type = RepoType.from_string(template_type)
        template.location = location
        template.name = location.stem
        template.group = data.get("group", "")
        template.default_context = data.get("key", {})
        template.add_tags(data.get("tags", []))
        mapping_data = self._get_mapping(location.name, data)
        template.add_mapping(mapping_data)
        return template

    def _parse_repo(self, data: dict) -> list[KukaiTemplate]:
        templates = []
        candidate_list = self._parse_location(data.get("engine"))
        for candidate in candidate_list:
            if not KukaiTemplate.exists(candidate):
                templates.append(self._create_template(candidate, data))
        return templates

    def get_templates(self) -> list[KukaiTemplate]:
        return self._templates


class TemplateCollection:
    _template: list[KukaiTemplate] = []

    def add_template(self, data: dict) -> None:
        loc = data["location"]
        if not KukaiTemplate.exists(loc):
            t = KukaiTemplate(data)
            template_type = data.get("engine", "")
            t.template_type = RepoType.from_string(template_type)
            self._template.append(t)

    def add_repo(self, location: Path | str) -> None:
        # repo_location = data.get("location")
        repo_location = location
        repo = KukaiRepo(repo_location)
        templates = repo.get_templates()
        self._template += templates
        name = "hans"
        if name in templates:
            pass

    def get_name(self, name: str) -> KukaiTemplate | None:
        for t in self._template:
            if t.name == name:
                return t

    def get_tags(self, tag: str) -> list[KukaiTemplate]:
        templates = []
        for t in self._template:
            if tag in t.tags:
                templates.append(t)
        return templates

    def _get_lowest_score(self, tag: str, data: list[str]) -> tuple[str | None, float]:
        selected = None
        score = 0.0
        for t in data:
            jaro = leven.jaro(t, tag)
            if jaro > score:
                score = jaro
                selected = t
        return selected, score

    def get_near_tag(self, tag: str) -> str:
        tag_list = []
        for t in self._template:
            tag_list += t.tags
        selected, score = self._get_lowest_score(tag, list(set(tag_list)))
        return selected

    def get(self) -> list[KukaiTemplate]:
        return self._template

    def get_grouped(self, tag: str | None = None) -> dict:
        data = {}
        if not tag:
            templates = self._template
        else:
            templates = self.get_tags(tag)
        for t in templates:
            if t.group not in data:
                data[t.group] = []
            data[t.group].append(t.name)
        return data


class KukaiCore:
    _config: KukaiConfig

    def __init__(self) -> None:
        self._config = KukaiConfig()

    @property
    def data(self):
        return self._config.data

    def add_repo(self, config_file: str | Path) -> bool:
        return self._config.add_repo(Path(config_file))

    def get_data(self) -> dict:
        return self.data

    def get_repos(self) -> dict:
        return self._config.get_repos()

    def _add_base_repo(self, repo_data: dict, collection: TemplateCollection) -> None:
        kukai_data = repo_data.get("kukai", {})
        templates = kukai_data.get("template", [])
        for t in templates:
            collection.add_template(t)

        repos = kukai_data.get("location", [])
        for r in repos:
            collection.add_repo(r)

    def get_collection(self) -> TemplateCollection:
        collection = TemplateCollection()
        self._add_base_repo(self.data, collection)
        return collection

    def get_template_list(self) -> list:
        templates = self.data.get("template")
        return templates
