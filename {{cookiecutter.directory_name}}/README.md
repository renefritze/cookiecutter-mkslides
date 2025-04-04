# {{cookiecutter.directory_name}}

{{cookiecutter.author}}
{{cookiecutter.email}}

* [Slides](https://{{cookiecutter.github_user}}.github.io/{{cookiecutter.directory_name}})
* [PDF](https://github.com/{{cookiecutter.github_short}}/blob/master/slides/{{cookiecutter.file_name}}.pdf)

{{cookiecutter.repository_description}}.

[![Build Status](https://github.com/{{cookiecutter.github_short}}/actions/workflows/build.yml/badge.svg?main)](https://github.com/{{cookiecutter.github_short}}/actions/workflows/build.yml)
[![GitHub license](https://img.shields.io/github/license/{{cookiecutter.github_short}}.svg)](https://github.com/{{cookiecutter.github_short}}/blob/main/LICENSE)


## Install

1. Install [npm](https://www.npmjs.com/)
2. Make sure you have `uv` [installed](https://docs.astral.sh/uv/getting-started/installation/)
3. [Clone](https://git-scm.com/docs/git-clone) this repository
4. Install dependencies with `npm`

```
git clone {{cookiecutter.github_url}}
cd {{cookiecutter.directory_name}}
make install
```

See [Edits](#edits) and [Implementation](#implementation) for more details.

## Usage

1. Generate `{{cookiecutter.reveal_static}}/index.html` (see `script.html` in [package.json](https://github.com/{{cookiecutter.github_short}}/blob/master/package.json))
2. Generate `slides/{{cookiecutter.file_name}}.pdf` (see `script.pdf` in [package.json](https://github.com/{{cookiecutter.github_short}}/blob/master/package.json))

```
make html
make pdf
```

## Developer Notes

### Edits

The following can be edited before generating:

* `slides/{{cookiecutter.file_name}}.md`: [Markdown](https://daringfireball.net/projects/markdown/) file with slide contents
* `slides/template.html`: Custom [reveal-md](https://github.com/webpro/reveal-md) template to generate slides with
* `{{cookiecutter.reveal_static}}/edit/style.css`: [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) file to adjust styling of slides
* `{{cookiecutter.reveal_static}}/edit/logo.png`: logo image to use

### Implementation


The slides [{{cookiecutter.directory_name}}]({{cookiecutter.github_url}}) uses the following [npm](https://www.npmjs.com/) packages for its implementation:

npm | Purpose
--- | ---
[reveal-md](https://www.npmjs.com/package/reveal-md) | Converting `slides/{{cookiecutter.file_name}}.md` to `{{cookiecutter.reveal_static}}/index.html`
[decktape](https://www.npmjs.com/package/decktape) | Converting `slides/{{cookiecutter.file_name}}.md` to `slides/{{cookiecutter.file_name}}.pdf`
[windows-build-tools](https://www.npmjs.com/package/windows-build-tools) | Compiling dependencies for decktape on Windows Operating System (OS)

```
       reveal-md            <-- Convert markdown  slides to html

       decktape             <-- Convert markdown slides to pdf
          |
  windows-build-tools       <-- Compile decktape on Windows OS
```

### Deployment

Pushes to the main branch trigger a Github Action that builds the html slides and deploys the `static_html/` directory via the `gh-pages` branch to Github Pages.
For this to work goto Repository Settings -> Actions -> General -> Workflow permissions and set that to "read and write".

### Notes

- [Mermaid](https://mermaid-js.github.io/mermaid/) Support thanks to [plugin by @amra](https://github.com/amra/reveal-md-scripts)
