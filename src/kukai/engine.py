from pathlib import Path
from cookiecutter.main import cookiecutter
from jinja2 import Template


class CookieEngine:
    @staticmethod
    def create(path: str | Path, destination: str | Path, context: dict) -> None:
        cookiecutter(
            str(path), output_dir=str(destination), no_input=True, extra_context=context
        )


class FileEngine:
    @staticmethod
    def create(
        path: str | Path,
        destination: str | Path,
        context: dict,
        name_key: None | str = None,
    ) -> None:
        file_path = Path(path)
        if not name_key:
            t = Template(file_path.name)
        else:
            t = Template(name_key)
        new_file = Path(destination) / t.render(context)
        with file_path.open("r") as f:
            templ = Template(f.read())
        rend = templ.render(context)
        with new_file.open("w") as f:
            f.write(rend)
