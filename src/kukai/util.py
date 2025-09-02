from pathlib import Path

from kukai.core import KukaiTemplate, RepoType, KukaiRepo
from kukai.context import ContextParser


class RepoExtraction:
    _type = None
    _context_file = None
    _template = None

    def __init__(self, repo_path: Path | str) -> None:
        target_path = Path(repo_path)
        if target_path.is_dir():
            parse_dir = target_path
        if target_path.is_file():
            parse_dir = target_path.parent
        match self._check_type(target_path):
            case RepoType.COOKIECUTTER:
                self._template = self._get_cc_template(target_path)
            case RepoType.KUKAI:
                self._template = self._get_kukai_template(target_path)
            case _:
                pass

        if not self._template:
            raise ValueError(f"{target_path} does not exists")

        self._parse_dir(parse_dir)

    def _check_type(self, repo_path: Path) -> RepoType:
        if repo_path.is_dir():
            parse_dir = repo_path
        if repo_path.is_file():
            parse_dir = repo_path.parent
        kukai_file = parse_dir / "kukai.toml"
        if kukai_file.exists():
            return RepoType.KUKAI
        cc_file = parse_dir / "cookiecutter.json"
        if cc_file.exists():
            return RepoType.COOKIECUTTER
        return RepoType.UNKNOWN

    def _get_cc_template(self, location: Path) -> KukaiTemplate:
        template = KukaiTemplate({})
        template.location = location
        template.name = location.stem
        template.template_type = RepoType.COOKIECUTTER
        return template

    def _get_kukai_template(self, location: Path) -> KukaiTemplate | None:
        target_path = Path(location)
        if target_path.is_dir():
            parse_dir = target_path
        if target_path.is_file():
            parse_dir = target_path.parent
        repo = KukaiRepo(parse_dir.resolve())
        templates = repo.get_templates()
        for templ in templates:
            if templ.name == target_path.stem:
                return templ
        return None

    def _parse_dir(self, repo_path: Path) -> None:
        kukai_file = repo_path / "kukai.toml"
        cc_file = repo_path / "cookiecutter.json"
        if kukai_file.exists():
            self._template.template_type = RepoType.KUKAI
            self._context_file = kukai_file
            return
        if cc_file.exists():
            self._template.template_type = RepoType.COOKIECUTTER
            self._context_file = cc_file
            return
        raise ValueError(f"{repo_path} is not a valid repo")

    def get_template(self) -> KukaiTemplate:
        return self._template

    def get_type(self) -> RepoType:
        return self._type

    def get_context(self) -> ContextParser:
        return ContextParser(self._context_file)

    def info(self) -> None:
        print(self._type)
        print(self._context_file)
