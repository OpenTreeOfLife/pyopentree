# Unit tests
# Add your unit test file here - make sure it contains
# if __name__ == '__main__':
#    unittest.main()
# so that the tests get run
#

PYTHON="python"
LEGACY_PYTHON = $(shell $(PYTHON) -c 'import sys; print(sys.hexversion < 0x03000000)')
ifeq ($(LEGACY_PYTHON),True)
	UNIT_TESTS = _api_level_1_py26_and_below.py
else
	UNIT_TESTS = _api_level_1.py
endif

# default case (and test). Loop through all
# tests listed above and run them
test: ${UNIT_TESTS}
	@for file in $(UNIT_TESTS); do \
	echo "----"; \
	echo "Running: $${file} using Python interpreter found at '${PYTHON}'"; \
	$(PYTHON) $${file}; \
	done ;
