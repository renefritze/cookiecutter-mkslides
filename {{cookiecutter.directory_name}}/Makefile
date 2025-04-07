SHELL = /bin/bash
.PHONY: .FORCE html pdf watch clean install install-browsers

.DEFAULT_GOAL := html

.FORCE:

static_html/index.html: install .FORCE slides/{{cookiecutter.file_name}}.md slides/qr_self.png
	uv run mkslides build slides/{{cookiecutter.file_name}}.md -d static_html

slides/{{cookiecutter.file_name}}.pdf: install static_html/index.html install
	uv run mkslides pdf slides/{{cookiecutter.file_name}}.md -d slides/{{cookiecutter.file_name}}.pdf

uv.lock:
	uv lock

install: uv.lock .FORCE
	uv sync --frozen

install-browsers: .FORCE
	uv run -m playwright install chromium

html: static_html/index.html

pdf: static_html/index.html install-browsers
	@mkdir -p slides
	uv run html_to_pdf.py static_html/index.html slides/{{cookiecutter.file_name}}.pdf

watch: .FORCE
	uv run mkslides serve slides/{{cookiecutter.file_name}}.md

slides/qr_%.png: .FORCE
	uv run render_qr.py
	mv -f qr_*png slides/

clean: .FORCE
	rm -f qr_*png
	rm -rf static_html/*
