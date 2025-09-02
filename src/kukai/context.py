from pathlib import Path
import json
import toml
from jinja2 import Template


class JinjaUtils:
    @staticmethod
    def render_entry(value: str, context: dict) -> str:
        templ = Template(value)
        rendered_value = templ.render(context)
        return rendered_value


class ContextParser:
    """Representation of Context

    A helper class to generate context from user input
    """

    _default_context = {}
    _context = {}

    def __init__(self, file_path: Path | str) -> None:
        context_file = Path(file_path)
        self._stem = context_file.stem
        match context_file.suffix:
            case ".json":
                with context_file.open("r") as f:
                    self.data = json.load(f)
            case ".toml":
                with context_file.open("r") as f:
                    self.data = toml.load(f)

    def _iter_context(self):
        for key in self.as_dict():
            ctx_value = self.as_dict().get(key)
            yield key, ctx_value

    def __iter__(self):
        return self._iter_context()

    def add_context(self, new_context: dict) -> None:
        self._context = self._context | new_context

    def clear_context(self) -> None:
        self._context = {}

    def parse_cc_context(self, context: dict) -> dict:
        running_context = {}
        for key, value in self.data.items():
            if key in context:
                entry = context[key]
            else:
                if type(value) is bool:
                    entry = value
                else:
                    entry = JinjaUtils.render_entry(
                        value, {self._stem: running_context}
                    )
            running_context[key] = entry
        return running_context

    def parse_kukai_context(self, context: dict) -> dict:
        base_context = self.data.get("kukai", {}).get("repo", {}).get("key", {})
        running_context = {}
        for key, value in base_context.items():
            if key in context:
                entry = context[key]
            else:
                if type(value) is bool:
                    entry = value
                else:
                    entry = JinjaUtils.render_entry(value, running_context)
            running_context[key] = entry
        return running_context

    def as_dict(self) -> dict:
        match self._stem:
            case "cookiecutter":
                return self.parse_cc_context(self._context)
            case _:
                return self.parse_kukai_context(self._context)
