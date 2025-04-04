SHELL = /bin/bash
PHONY: .FORCE

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

html: static_html/index.html

pdf:
	# This target is a placeholder for generating PDF slides.
	@echo "PDF generation is not implemented yet."

watch: .FORCE
	uv run mkslides serve slides/{{cookiecutter.file_name}}.md

slides/qr_%.png: .FORCE
	uv run render_qr.py
	mv -f qr_*png slides/

clean: .FORCE
	rm -f qr_*png
	rm -rf static_html/*
