# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE


# Download python-build
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
_WGET := $$(shell [ -f ../python-build/$(notdir $(1)) ] && cp ../python-build/$(notdir $(1)) . || $(call WGET_CMD, $(1)))
endif
endef
WGET_CMD = if which wget; then wget -q -c $(1); else curl -f -Os $(1); fi
$(eval $(call WGET, https://craigahobbs.github.io/python-build/Makefile.base))
$(eval $(call WGET, https://craigahobbs.github.io/python-build/pylintrc))


# Sphinx documentation directory
SPHINX_DOC := doc


# Include python-build
include Makefile.base


clean:
	rm -rf Makefile.base pylintrc
