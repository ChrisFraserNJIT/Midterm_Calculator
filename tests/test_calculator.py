import datetime
from pathlib import Path
from decimal import Decimal
from tempfile import TemporaryDirectory
import pandas as pd
import pytest
from unittest.mock import patch, PropertyMock

from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# ---------------------------
# Fixture for Calculator
# ---------------------------
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            yield Calculator(config=config)

# ---------------------------
# Basic Calculator Tests
# ---------------------------
def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

def test_add_and_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

def test_set_and_perform_operation(calculator):
    op = OperationFactory.create_operation('add')
    calculator.set_operation(op)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_errors(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)
    calc2 = Calculator()
    with pytest.raises(OperationError):
        calc2.perform_operation(2, 3)

def test_undo_redo_history(calculator):
    op = OperationFactory.create_operation('add')
    calculator.set_operation(op)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []
    calculator.redo()
    assert len(calculator.history) == 1

# ---------------------------
# History Management
# ---------------------------
@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    calculator.load_history()
    assert len(calculator.history) == 1
    h = calculator.history[0]
    assert h.operation == "Addition"
    assert h.operand1 == Decimal("2")
    assert h.operand2 == Decimal("3")
    assert h.result == Decimal("5")

def test_clear_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# ---------------------------
# REPL runner
# ---------------------------
def run_repl_with_inputs(inputs):
    """
    Run calculator_repl() safely with mocked input.
    inputs: list of strings OR generator/lambda that raises exceptions
    Returns the mocked print object for assertions.
    """
    # Convert list of strings to a generator
    if isinstance(inputs, list):
        input_gen = (i for i in inputs)
    else:
        input_gen = inputs  # assume generator/lambda raising exception

    def mock_input(_prompt=""):
        try:
            return next(input_gen)
        except StopIteration:
            raise EOFError  # safely end inputs

    with patch("builtins.input", side_effect=mock_input), \
         patch("builtins.print") as mock_print:
        calculator_repl()  # Will exit on 'exit' or EOFError
    return mock_print


# ---------------------------
# REPL Tests
# ---------------------------
from unittest.mock import patch

def test_repl_exit():
    with patch("app.calculator.Calculator.save_history") as mock_save:
        mock_print = run_repl_with_inputs(["exit"])
        mock_save.assert_called_once()
        mock_print.assert_any_call("\x1b[36mGoodbye!\x1b[0m")

def test_repl_help():
    mock_print = run_repl_with_inputs(["help", "exit"])
    mock_print.assert_any_call("\nAvailable commands:")

def test_repl_addition():
    mock_print = run_repl_with_inputs(["add", "2", "3", "exit"])
    mock_print.assert_any_call("\nResult: \x1b[32m5\x1b[0m")

def test_repl_history():
    with patch("app.calculator.Calculator.show_history", return_value=["2 + 3 = 5"]):
        mock_print = run_repl_with_inputs(["history", "exit"])
        mock_print.assert_any_call("\nCalculation History:")
        mock_print.assert_any_call("1. 2 + 3 = 5")

def test_repl_clear():
    with patch("app.calculator.Calculator.clear_history") as mock_clear:
        mock_print = run_repl_with_inputs(["clear", "exit"])
        mock_clear.assert_called_once()
        mock_print.assert_any_call("\x1b[33mHistory cleared\x1b[0m")

def test_repl_undo_redo_nothing():
    for cmd in ["undo", "redo"]:
        with patch(f"app.calculator.Calculator.{cmd}", return_value=False) as mock_method:
            mock_print = run_repl_with_inputs([cmd, "exit"])
            mock_method.assert_called_once()
            mock_print.assert_any_call(f"\x1b[33mNothing to {cmd}\x1b[0m")

def test_repl_save_load_exceptions():
    with patch("app.calculator.Calculator.save_history", side_effect=Exception("Save failed")), \
         patch("app.calculator.Calculator.load_history", side_effect=Exception("Load failed")):
        mock_print = run_repl_with_inputs(["save", "load", "exit"])
        mock_print.assert_any_call("\x1b[31mError saving history: Save failed\x1b[0m")
        mock_print.assert_any_call("\x1b[31mError loading history: Load failed\x1b[0m")

def test_repl_cancel_input():
    mock_print = run_repl_with_inputs(["add", "cancel", "exit"])
    mock_print.assert_any_call("\x1b[33mOperation cancelled\x1b[0m")

def test_repl_invalid_command():
    mock_print = run_repl_with_inputs(["nonsense", "exit"])
    mock_print.assert_any_call("\x1b[31mUnknown command: 'nonsense'. Type 'help' for available commands.\x1b[0m")

def test_repl_keyboard_interrupt():
    # Simulate Ctrl+C in REPL
    def raise_keyboard():
        raise KeyboardInterrupt
        yield  # generator
    mock_print = run_repl_with_inputs(raise_keyboard())
    mock_print.assert_any_call("\n\x1b[33mOperation cancelled\x1b[0m")

def test_repl_eof():
    # Simulate EOF in REPL
    def raise_eof():
        raise EOFError
        yield
    mock_print = run_repl_with_inputs(raise_eof())
    mock_print.assert_any_call("\n\x1b[36mInput terminated. Exiting...\x1b[0m")

def test_repl_unexpected_exception():
    with patch("app.calculator.Calculator.perform_operation", side_effect=Exception("Unexpected")):
        mock_print = run_repl_with_inputs(["add", "2", "3", "exit"])
        mock_print.assert_any_call("\x1b[31mUnexpected error: Unexpected\x1b[0m")
