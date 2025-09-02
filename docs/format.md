# Cookiecutter Example
```
[kukai.repo]
engine = "cc"
group = "cc"
tags = ["cc","tests"]

[[kukai.repo.mapping]]
name = "cc-0"
tags = ["test"]

[[kukai.repo.mapping]]
name = "cc-1"
tags = ["something"]
```

# Jinja File Example
```
[kukai.repo]
engine = "file"
group = "file_template"
tags = ["file"]

[kukai.repo.key]
project_name = "Kukai File Test"
project_slug = "{{ project_name.lower()|replace(' ', '_')|replace('-', '_') }}"
author = "Max Muster"

[[kukai.repo.mapping]]
name="jinja_template.toml"
name_key="{{project_slug}}.toml"

[[kukai.repo.mapping]]
name="test.txt"
name_key="{{project_slug}}.txt"
```
