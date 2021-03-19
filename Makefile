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
    $$(shell if which wget > /dev/null; then wget -q '$(strip $(1))'; else curl -Os '$(strip $(1))'; fi)
endif
endef
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/master/Makefile.base))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/master/pylintrc))

# Include Python Build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc

$(BUILD)/doc/type_model.smd: $(DOC_PYTHON_3_9_VENV_BUILD)
	mkdir -p $(dir $@)
	$(DOC_PYTHON_3_9_VENV_CMD)/python3 -c 'import schema_markdown.type_model as tm; print(tm.TYPE_MODEL_SMD)' > $@

doc-python-3-9: $(BUILD)/doc/type_model.smd
