PYTHON ?= python3
.PHONY: help convert convert-quiet dry-run check test
help:
	@$(PYTHON) "$(ROOT)/lib/core.py" "$(TOOL)" --help
convert:
	@$(PYTHON) "$(ROOT)/lib/core.py" "$(TOOL)" $(ARGS)
convert-quiet:
	@$(PYTHON) "$(ROOT)/lib/core.py" "$(TOOL)" --quiet $(ARGS)
dry-run:
	@$(PYTHON) "$(ROOT)/lib/core.py" "$(TOOL)" --dry-run $(ARGS)
check:
	@$(MAKE) -C "$(ROOT)" check
test:
	@$(MAKE) -C "$(ROOT)" test-all
