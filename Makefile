PYTHON_VERSIONS := \
    3.9 \
    3.10-rc \
    3.8 \
    3.7

# Sphinx documentation directory
SPHINX_DOC := doc

# Download Python Build base makefile
ifeq '$(wildcard Makefile.base)' ''
    $(info Downloading Makefile.base)
    $(shell curl -s -o Makefile.base 'https://raw.githubusercontent.com/craigahobbs/python-build/master/Makefile.base')
endif

# Download Python Build's pylintrc
ifeq '$(wildcard pylintrc)' ''
    $(info Downloading pylintrc)
    $(shell curl -s -o pylintrc 'https://raw.githubusercontent.com/craigahobbs/python-build/master/pylintrc')
endif

# Include Python Build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc

$(BUILD)/doc/type_model.smd: $(DOC_PYTHON_3_9_VENV_BUILD)
	mkdir -p $(dir $@)
	$(DOC_PYTHON_3_9_VENV_CMD)/python3 -c 'import schema_markdown.type_model as tm; print(tm.TYPE_MODEL_SCHEMA_MARKDOWN)' > $@

doc-python-3-9: $(BUILD)/doc/type_model.smd
