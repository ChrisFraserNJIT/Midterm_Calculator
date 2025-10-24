# Advanced Calculator Application

## Project Description

This is an advanced command-line calculator application built with Python that implements multiple design patterns and provides robust error handling, history management, and comprehensive logging capabilities. The calculator supports various arithmetic operations and features a REPL (Read-Eval-Print Loop) interface for interactive use.

### Key Features

- **Multiple Arithmetic Operations**: Addition, subtraction, multiplication, division, power, root, modulus, integer division, percentage calculation, and absolute difference
- **Design Patterns**: 
  - Factory Pattern for operation management
  - Memento Pattern for undo/redo functionality
  - Observer Pattern for logging and auto-save capabilities
- **History Management**: Complete calculation history with undo/redo support
- **Data Persistence**: Save and load calculation history using pandas and CSV format
- **Configuration Management**: Environment-based configuration using .env files
- **Comprehensive Logging**: Detailed logging of all operations and errors
- **Robust Error Handling**: Custom exceptions and input validation
- **CI/CD Pipeline**: Automated testing with GitHub Actions
- **High Test Coverage**: 90%+ test coverage using pytest

## Installation Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Setup Steps

1. **Clone the Repository and Make a New Local Directory**
   ```bash
   mkdir Midterm_calculator
   cd Midterm_calculator
   git clone git@github.com:ChrisFraserNJIT/Assignment5.git
   ```

2. **Create and Activate Virtual Environment**
   
   **macOS/Linux: For this project it will be macOS**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables** (see Configuration Setup below)

## Configuration Setup

### Creating the .env File

Create a `.env` file in the project root directory with the following configuration parameters:

```env
# Base Directories
CALCULATOR_LOG_DIR=logs
CALCULATOR_HISTORY_DIR=history

# History Settings
CALCULATOR_MAX_HISTORY_SIZE=100
CALCULATOR_AUTO_SAVE=true

# Calculation Settings
CALCULATOR_PRECISION=2
CALCULATOR_MAX_INPUT_VALUE=1000000
CALCULATOR_DEFAULT_ENCODING=utf-8

# File Paths (optional - will use defaults if not specified)
CALCULATOR_LOG_FILE=logs/calculator.log
CALCULATOR_HISTORY_FILE=history/calculator_history.csv
```

### Configuration Parameters Explained

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `CALCULATOR_LOG_DIR` | Directory where log files are stored | `logs` |
| `CALCULATOR_HISTORY_DIR` | Directory where history files are stored | `history` |
| `CALCULATOR_MAX_HISTORY_SIZE` | Maximum number of calculations to keep in history | `100` |
| `CALCULATOR_AUTO_SAVE` | Enable/disable automatic saving of history | `true` |
| `CALCULATOR_PRECISION` | Number of decimal places for results | `2` |
| `CALCULATOR_MAX_INPUT_VALUE` | Maximum allowed input value | `1000000` |
| `CALCULATOR_DEFAULT_ENCODING` | Character encoding for file operations | `utf-8` |

### Important Notes

- The application will create the `logs/` and `history/` directories automatically if they don't exist
- If `.env` file is not present, the application will use default values
- Ensure proper file permissions for writing logs and history files

## Usage Guide

### Starting the Calculator

Run the application from the project root directory:

```bash
python main.py
```

or

```bash
python -m app.calculator
```

### Available Commands

The calculator provides an interactive REPL interface with the following commands:

#### Arithmetic Operations

All arithmetic operations require two numeric operands.

| Command | Description | Example | Result |
|---------|-------------|---------|--------|
| `add` | Add two numbers | `add 5 3` | `8.00` |
| `subtract` | Subtract second number from first | `subtract 10 4` | `6.00` |
| `multiply` | Multiply two numbers | `multiply 6 7` | `42.00` |
| `divide` | Divide first number by second | `divide 20 4` | `5.00` |
| `power` | Raise first number to power of second | `power 2 3` | `8.00` |
| `root` | Calculate nth root of first number | `root 27 3` | `3.00` |
| `modulus` | Find remainder of division | `modulus 17 5` | `2.00` |
| `int_divide` | Integer division (quotient only) | `int_divide 17 5` | `3.00` |
| `percent` | Calculate percentage (a/b)*100 | `percent 25 200` | `12.50` |
| `abs_diff` | Absolute difference between numbers | `abs_diff 10 15` | `5.00` |

#### History Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `history` | Display all calculation history | `history` |
| `clear` | Clear all calculation history | `clear` |
| `undo` | Undo the last calculation | `undo` |
| `redo` | Redo the last undone calculation | `redo` |

#### File Operations Commands

| Command | Description | Example |
|---------|-------------|---------|
| `save` | Manually save history to CSV file | `save` |
| `load` | Load history from CSV file | `load` |

#### Utility Commands

| Command | Description |
|---------|-------------|
| `help` | Display available commands and usage |
| `exit` | Exit the calculator application |

### Usage Examples

```
Welcome to the Advanced Calculator!
Type 'help' for available commands or 'exit' to quit.

> add 10 5
Result: 15.00

> power 2 8
Result: 256.00

> history
1. add(10, 5) = 15.00
2. power(2, 8) = 256.00

> undo
Undone: power(2, 8) = 256.00

> percent 50 200
Result: 25.00

> save
History saved successfully to history/calculator_history.csv

> exit
Goodbye!
```

### Error Handling

The calculator includes robust error handling for common issues:

- **Division by Zero**: `divide 10 0` → Error message displayed
- **Invalid Input**: Non-numeric inputs are rejected with helpful messages
- **Out of Range**: Values exceeding `CALCULATOR_MAX_INPUT_VALUE` are rejected
- **Invalid Operations**: Unknown commands display available options
- **File Errors**: Issues with saving/loading files are reported clearly

## Testing Instructions

### Running Tests

Execute the full test suite:

```bash
pytest
```

### Running Tests with Coverage

Check test coverage:

```bash
pytest --cov=app
```

### Running Tests with Coverage Report

Generate a detailed HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the detailed report.

### Enforcing Coverage Threshold

Ensure tests meet the 90% coverage requirement:

```bash
pytest --cov=app --cov-fail-under=90
```

### Running Specific Test Files

Run tests for specific modules:

```bash
pytest tests/test_calculator.py
pytest tests/test_operations.py
pytest tests/test_calculation.py
```

### Running Tests with Verbose Output

```bash
pytest -v
```

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py
├── test_calculator.py       # Calculator class tests
├── test_calculation.py      # Calculation class tests
├── test_operations.py       # Operation classes tests
├── test_history.py          # History management tests
├── test_memento.py          # Memento pattern tests
└── test_observers.py        # Observer pattern tests
```

## CI/CD Information

### GitHub Actions Workflow

This project uses GitHub Actions for Continuous Integration to automatically run tests and enforce code quality standards on every push and pull request to the main branch.

### Workflow Features

- **Automatic Testing**: Runs full test suite on every commit
- **Coverage Enforcement**: Fails if test coverage drops below 90%
- **Multi-Python Version Support**: Tests against specified Python versions
- **Dependency Management**: Automatically installs requirements
- **Status Badges**: Build status visible in repository

### Workflow Configuration

The workflow is defined in `.github/workflows/python-app.yml` and includes:

1. **Checkout Code**: Retrieves the latest code from the repository
2. **Setup Python**: Configures the Python environment
3. **Install Dependencies**: Installs packages from `requirements.txt`
4. **Run Tests**: Executes pytest with coverage measurement
5. **Enforce Coverage**: Fails build if coverage < 90%

### Viewing CI/CD Results

- Check the **Actions** tab in the GitHub repository
- Green checkmark (✓) indicates passing tests
- Red X (✗) indicates failing tests or insufficient coverage
- Click on any workflow run to see detailed logs

### Local Pre-Commit Testing

Before pushing code, run tests locally to ensure CI will pass:

```bash
pytest --cov=app --cov-fail-under=90
```

## Project Structure

```
Midterm_Calculator/
├── app/
│   ├── __init__.py
│   ├── calculator.py           # Main Calculator class with REPL
│   ├── calculation.py          # Calculation data class
│   ├── calculator_config.py    # Configuration management
│   ├── calculator_memento.py   # Memento pattern implementation
│   ├── exceptions.py           # Custom exception classes
│   ├── history.py              # History management
│   ├── input_validators.py     # Input validation utilities
│   ├── operations.py           # Operation classes (Factory pattern)
│   └── logger.py               # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_calculation.py
│   ├── test_operations.py
│   └── ...
├── .github/
│   └── workflows/
│       └── python-app.yml      # GitHub Actions workflow
├── .env                        # Environment configuration (not in repo)
├── .gitignore                  # Git ignore patterns
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── main.py                     # Application entry point
```

## Design Patterns Implemented

### Factory Pattern
- **Location**: `app/operations.py`
- **Purpose**: Creates operation instances dynamically based on operation type
- **Benefit**: Easy to add new operations without modifying existing code

### Memento Pattern
- **Location**: `app/calculator_memento.py`
- **Purpose**: Implements undo/redo functionality
- **Benefit**: Maintains calculation history and allows state restoration

### Observer Pattern
- **Location**: `app/calculator.py` and observer classes
- **Purpose**: Notifies observers (LoggingObserver, AutoSaveObserver) of new calculations
- **Benefit**: Decouples calculation logic from logging and persistence

## Dependencies

Key dependencies include:

- `python-dotenv`: Environment variable management
- `pandas`: Data manipulation and CSV operations
- `pytest`: Testing framework
- `pytest-cov`: Coverage measurement
- Additional dependencies listed in `requirements.txt`

## License

This project is created for academic purposes as part of IS218 coursework.

## Author

Chris Fraser - NJIT

