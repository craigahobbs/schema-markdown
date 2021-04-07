PYTHON_VERSIONS := \
    3.9 \
    3.10-rc \
    3.8 \
    3.7

# Sphinx documentation directory
SPHINX_DOC := doc

# Download Python Build base makefile and pylintrc
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
_WGET := $$(shell if which wget; then wget -q $(1); else curl -Os $(1); fi)
endif
endef
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/master/Makefile.base))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/master/pylintrc))

# Include Python Build
include Makefile.base

# Build statics
clean:
	rm -rf Makefile.base pylintrc
	$(MAKE) -C static clean

superclean:
	$(MAKE) -C static superclean

.PHONY: commit-static
commit-static:
	$(MAKE) -C static commit

commit: commit-static

# Copy the Schema Markdown documentation application into the documentation directory
doc:
	rsync -rv --delete static/src/ build/doc/html/doc/
	mv build/doc/html/doc/doc.html build/doc/html/doc/index.html