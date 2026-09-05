.DEFAULT_GOAL := help
PYTHON ?= python3
TOOLS := $(patsubst %/Makefile,%,$(wildcard conversion/*/Makefile util/*/*/Makefile))
.PHONY: help generate check check-lib check-mcp check-docs check-tests test test-functional test-all install-hooks
help:
	@echo "make check | test | test-functional | test-all | generate | install-hooks"
	@echo "Run a tool: bin/$(notdir $(CURDIR)) TOOL --help"
generate:
	$(PYTHON) scripts/generate.py
check:
	$(PYTHON) scripts/check.py
check-lib check-mcp check-docs check-tests: check
test:
	$(PYTHON) -m unittest discover -s tests -p test_common.py -v
test-functional:
	$(PYTHON) -m unittest discover -s tests -p test_functional.py -v
test-all:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
install-hooks:
	git config core.hooksPath .githooks

define TOOL_ALIAS
$(notdir $(1))-%:
	$$(MAKE) -C $(1) $$*
endef
$(foreach t,$(TOOLS),$(eval $(call TOOL_ALIAS,$(t))))
