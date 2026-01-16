.PHONY: all build build-tui build-python install clean test run dev

# Go build settings
GO_MODULE = github.com/flight505/agentui
GO_BINARY = agentui-tui
GO_BUILD_DIR = ./bin
GO_CMD_DIR = ./cmd/agentui

# Python settings
PYTHON = python
PIP = pip

all: build

# Build everything
build: build-tui build-python

# Build Go TUI binary
build-tui:
	@echo "Building Go TUI..."
	@mkdir -p $(GO_BUILD_DIR)
	cd $(GO_CMD_DIR) && go build -o ../../$(GO_BUILD_DIR)/$(GO_BINARY) .
	@echo "Built: $(GO_BUILD_DIR)/$(GO_BINARY)"

# Install Go dependencies
deps-go:
	@echo "Installing Go dependencies..."
	go mod download
	go mod tidy

# Build for all platforms
build-all-platforms:
	@echo "Building for all platforms..."
	@mkdir -p $(GO_BUILD_DIR)
	GOOS=darwin GOARCH=amd64 go build -o $(GO_BUILD_DIR)/$(GO_BINARY)-darwin-amd64 $(GO_CMD_DIR)
	GOOS=darwin GOARCH=arm64 go build -o $(GO_BUILD_DIR)/$(GO_BINARY)-darwin-arm64 $(GO_CMD_DIR)
	GOOS=linux GOARCH=amd64 go build -o $(GO_BUILD_DIR)/$(GO_BINARY)-linux-amd64 $(GO_CMD_DIR)
	GOOS=windows GOARCH=amd64 go build -o $(GO_BUILD_DIR)/$(GO_BINARY)-windows-amd64.exe $(GO_CMD_DIR)
	@echo "Built binaries in $(GO_BUILD_DIR)/"

# Build Python package
build-python:
	@echo "Building Python package..."
	$(PYTHON) -m build

# Install Python package in development mode
install-dev:
	@echo "Installing Python package in dev mode..."
	$(PIP) install -e ".[dev]"

# Install everything
install: build-tui install-dev
	@echo "Copying TUI binary to package..."
	@mkdir -p src/agentui/bin
	cp $(GO_BUILD_DIR)/$(GO_BINARY) src/agentui/bin/

# Run tests
test:
	@echo "Running Python tests..."
	$(PYTHON) -m pytest tests/ -v

test-go:
	@echo "Running Go tests..."
	go test ./...

# Run the TUI directly (for testing)
run-tui:
	@echo "Running TUI..."
	$(GO_BUILD_DIR)/$(GO_BINARY) --theme catppuccin-mocha

# Run a demo
demo: build-tui
	@echo "Running demo..."
	$(PYTHON) examples/simple_agent.py

# Development mode - watch and rebuild
dev:
	@echo "Starting development mode..."
	@echo "Run 'make build-tui' after Go changes"
	@echo "Python changes are auto-reloaded with -e install"

# Clean build artifacts
clean:
	@echo "Cleaning..."
	rm -rf $(GO_BUILD_DIR)
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	rm -rf .pytest_cache
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Format code
fmt:
	@echo "Formatting Go code..."
	go fmt ./...
	@echo "Formatting Python code..."
	$(PYTHON) -m ruff format src/ tests/ examples/

# Lint code
lint:
	@echo "Linting Go code..."
	go vet ./...
	@echo "Linting Python code..."
	$(PYTHON) -m ruff check src/ tests/ examples/

# Show help
help:
	@echo "AgentUI Build System"
	@echo ""
	@echo "Commands:"
	@echo "  make build          - Build both Go TUI and Python package"
	@echo "  make build-tui      - Build Go TUI binary"
	@echo "  make build-python   - Build Python package"
	@echo "  make install        - Install everything"
	@echo "  make install-dev    - Install Python package in dev mode"
	@echo "  make test           - Run Python tests"
	@echo "  make test-go        - Run Go tests"
	@echo "  make run-tui        - Run TUI directly"
	@echo "  make demo           - Run demo application"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make fmt            - Format all code"
	@echo "  make lint           - Lint all code"
	@echo ""
	@echo "For development:"
	@echo "  1. make install-dev  - Install Python in dev mode"
	@echo "  2. make build-tui    - Build TUI after Go changes"
	@echo "  3. make demo         - Test your changes"
