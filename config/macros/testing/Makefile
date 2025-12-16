# Klipper Macro Testing Framework
# ================================
# Run `make` to see available targets

VENV := .venv
PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
PYTEST_OPTS := -v

.PHONY: help venv install test test-fast test-all test-mcu clean
.PHONY: test-glyphs test-perimeter test-fill test-retract test-outer-loop test-combined
.PHONY: test-retraction-calibration test-temperature-tower test-file test-match markers

.DEFAULT_GOAL := help

help: ## Show this help
	@echo "Klipper Macro Testing Framework"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Setup Targets
# ============================================================================

venv: ## Create virtual environment only
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)

install: venv ## Create venv and install dependencies (run first)
	@echo "Installing dependencies..."
	. $(VENV)/bin/activate && pip install -r requirements.txt
	@echo "Setup complete! Run 'make test' to verify."

clean: ## Remove venv and test results
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf test_results/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete."

# ============================================================================
# Test Targets - All Tests
# ============================================================================

test: ## Run all fast tests (excludes slow MCU tests)
	@echo "Running fast tests (excluding MCU tests)..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "not mcu"

test-fast: test ## Alias for 'test'

test-all: ## Run ALL tests including slow MCU tests
	@echo "Running ALL tests (including slow MCU tests)..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS)

test-mcu: ## Run only MCU-level integration tests (slow)
	@echo "Running MCU-level integration tests (slow)..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "mcu"

# ============================================================================
# Test Targets - By Component
# ============================================================================

test-glyphs: ## Test digit/period drawing macros
	@echo "Running glyph macro tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "glyphs"

test-perimeter: ## Test perimeter drawing macros
	@echo "Running perimeter macro tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "perimeter"

test-fill: ## Test fill pattern macros
	@echo "Running fill pattern tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "fill"

test-retract: ## Test retract/unretract macros
	@echo "Running retract/unretract tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "retract_unretract"

test-outer-loop: ## Test pressure advance loop macros
	@echo "Running outer loop (PA loop) tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "outer_loop"

test-combined: ## Test component integration
	@echo "Running combined component tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -m "combined"

# ============================================================================
# Test Targets - By Feature
# ============================================================================

test-retraction-calibration: ## All retraction calibration tests
	@echo "Running all retraction calibration tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/retraction_calibration/ $(PYTEST_OPTS)

test-temperature-tower: ## All temperature tower tests
	@echo "Running all temperature tower tests..."
	. $(VENV)/bin/activate && $(PYTEST) tests/temperature_tower/ $(PYTEST_OPTS)

# ============================================================================
# Development Helpers
# ============================================================================

test-file: ## Run specific test file (FILE=path/to/test.py)
	@echo "Running tests from $(FILE)..."
	. $(VENV)/bin/activate && $(PYTEST) $(FILE) $(PYTEST_OPTS)

test-match: ## Run tests matching pattern (PATTERN="name")
	@echo "Running tests matching '$(PATTERN)'..."
	. $(VENV)/bin/activate && $(PYTEST) tests/ $(PYTEST_OPTS) -k "$(PATTERN)"

markers: ## Show available pytest markers
	@echo "Available pytest markers:"
	. $(VENV)/bin/activate && $(PYTEST) --markers | grep -A1 "^@pytest.mark"
