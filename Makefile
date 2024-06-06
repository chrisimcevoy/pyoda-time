.PHONY: docs.sphinx.html



docs.sphinx.html:
	@echo "Cleaning build directory"
	# This deletes everything from the /docs/build directory, using the
	# sphinx Makefile in /docs. It is only really useful for local builds,
	# given that the /docs/build directory is in .gitignore.
	poetry run make -C docs clean

	@echo "Generating source files with sphinx-apidoc"
	# This uses sphinx-apidoc to automatically generate rst files in
	# /docs/source for each public module in the pyoda_time package
	# recursively. Those files will contain directives (e.g. :automodule:)
	# which can later be handled by the autodoc extension.
	poetry run sphinx-apidoc --no-toc --no-headings --force -d 1 -o docs/source pyoda_time

	@echo "Building html docs with sphinx-autodoc"
	# Uses the sphinx Makefile in /docs to build the documentation.
	# The autodoc extension is enabled in /docs/conf.py.
	# That extensions interprets the directives in the files which were
	# generated by sphinx-apidoc in the previous command, allowing
	# us to turn that into html documentation.
	poetry run make -C docs SPHINXOPTS=-W html
