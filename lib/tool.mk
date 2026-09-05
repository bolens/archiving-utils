.PHONY: help convert convert-quiet dry-run check test
help:
	@$(ROOT)/bin/$(notdir $(ROOT)) $(TOOL) --help
convert:
	@$(ROOT)/bin/$(notdir $(ROOT)) $(TOOL) $(ARGS)
convert-quiet:
	@$(ROOT)/bin/$(notdir $(ROOT)) $(TOOL) --quiet $(ARGS)
dry-run:
	@$(ROOT)/bin/$(notdir $(ROOT)) $(TOOL) --dry-run $(ARGS)
check:
	@$(MAKE) -C $(ROOT) check
test:
	@$(MAKE) -C $(ROOT) test-all
