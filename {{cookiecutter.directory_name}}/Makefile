HOST_PYTHON=python
SHELL = /bin/bash

static_html/index.html: slides/{{cookiecutter.file_name}}.md slides/qr_self.png
	npm run html

slides/{{cookiecutter.file_name}}.pdf: static_html/index.html
	npm run pdf

install:
	npm install

html: static_html/index.html

pdf: slides/{{cookiecutter.file_name}}.pdf

watch:
	npm run watch

slides/qr_%.png:
	uv run render_qr.py
	mv -f qr_*png slides/

clean:
	rm -f qr_*png
	rm -rf static_html/*
