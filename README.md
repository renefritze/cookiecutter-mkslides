# cookiecutter-mkslides

Template for [mkslides](https://github.com/MartenBE/mkslides) presentations with Python cookiecutter.

[Demo output](https://rene.fritze.me/cookiecutter-mkslides/)

[![Build Status](https://github.com/renefritze/cookiecutter-mkslides/actions/workflows/build.yml/badge.svg?main)](https://github.com/renefritze/cookiecutter-mkslides/actions/workflows/build.yml)
[![GitHub license](https://img.shields.io/github/license/renefritze/cookiecutter-mkslides.svg)](https://github.com/renefritze/cookiecutter-mkslides/blob/main/LICENSE)

## Install

1. Install [Python](https://www.python.org/downloads/)
2. Install [cookiecutter](https://pypi.python.org/pypi/cookiecutter) via `pip`

```
python3 -m pip install cookiecutter
```

## Usage

1. Create a template using [cookiecutter](https://pypi.python.org/pypi/cookiecutter)
2. Change the directory to the folder with the same name as the `directory_name` input
3. Install dependencies with [npm](https://www.npmjs.com/)
4. Render HTML slides in the `static_html` folder
5. Render PDF slides in the `slides` folder

```
cookiecutter gh:renefritze/cookiecutter-mkslides
cd <directory_name>
make install
make html
make pdf
```

See [Implementation](#implementation) for more details.

## Developer Notes

### Create Github Repository

1. Ensure [git](https://git-scm.com/) is installed
2. Change directory to the generated folder `cd <directory_name>`
3. Initialize the repository
4. Add the generated files to commit
5. Create an empty [Github repository](https://help.github.com/articles/create-a-repo/) with the same name as `directory_name`
6. Pull any changes if the Github repository is not empty
7. Push the commit from `4.` to your created Github repository

```
git init
git add .
git commit -a -m "Initial commit"
git remote add origin https://github.com/<github_user>/<directory_name>.git
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Implementation

This code creates folders and files for [cookiecutter](https://pypi.python.org/pypi/cookiecutter) templates.

* The main file is [cookiecutter.json](https://github.com/renefritze/cookiecutter-mkslides/blob/main/cookiecutter.json) which defines the inputs for the command line interface
* The inputs then replace any values surrounded with `{{}}` inside the folder [{{cookiecutter.directory_name}}](https://github.com/renefritze/cookiecutter-mkslides/tree/main/%7B%7Bcookiecutter.directory_name%7D%7D)

```
        cookiecutter              <-- template tool
             |
      cookiecutter.json           <-- template inputs
             |
{{cookiecutter.directory_name}}    <-- generated template
```

The following files will be created inside a folder with the same name as the `directory_name` input:

File | Description
--- | ---
**slides/<file_name>.md** | [Markdown](https://daringfireball.net/projects/markdown/) file containing the slide contents
**template.html** | A [reveal-md](https://www.npmjs.com/package/reveal-md) custom template file for generating slides
**.gitignore** | A Node [.gitignore](https://git-scm.com/docs/gitignore) automatically generated from github
**.npmignore** | A file to specify ignoring `static_html/*`
**LICENSE** | MIT [license file](https://help.github.com/articles/licensing-a-repository/) automatically created from github
**.github** | [Github Actions](https://github.com/features/actions) workflows for deploying the page to Github Pages
**package.json** | The [npm package.json](https://docs.npmjs.com/files/package.json) specifications with [reveal-md](https://www.npmjs.com/package/reveal-md) and [decktape](https://www.npmjs.com/package/decktape) dependencies
**README.md** | a readme [Markdown](https://daringfireball.net/projects/markdown/) file with header section
