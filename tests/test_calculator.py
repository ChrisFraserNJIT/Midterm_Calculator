import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# ----------------------------------------------------------------------
# Fixture to initialize Calculator with a temporary directory
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Calculator core tests
# ----------------------------------------------------------------------
def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
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
    try:
        calculator.load_history()
        assert len(calculator.history) == 1
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# ----------------------------------------------------------------------
# REPL tests with max_iterations to prevent freezing
# ----------------------------------------------------------------------
@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl(max_iterations=1)
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("\x1b[33mHistory saved successfully.\x1b[0m")
        mock_print.assert_any_call("\x1b[36mGoodbye!\x1b[0m")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl(max_iterations=2)
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl(max_iterations=4)
    mock_print.assert_any_call("\nResult: \x1b[32m5\x1b[0m")

@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_history(mock_print, mock_input):
    with patch('app.calculator.Calculator.show_history', return_value=['2 + 3 = 5']):
        calculator_repl(max_iterations=2)
        mock_print.assert_any_call("\nCalculation History:")
        mock_print.assert_any_call("1. 2 + 3 = 5")

@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_calculator_repl_clear(mock_print, mock_input):
    with patch('app.calculator.Calculator.clear_history') as mock_clear:
        calculator_repl(max_iterations=2)
        mock_clear.assert_called_once()
        mock_print.assert_any_call("\x1b[33mHistory cleared\x1b[0m")

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo(mock_print, mock_input):
    with patch('app.calculator.Calculator.undo', return_value=False):
        calculator_repl(max_iterations=2)
        mock_print.assert_any_call("\x1b[33mNothing to undo\x1b[0m")

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo(mock_print, mock_input):
    with patch('app.calculator.Calculator.redo', return_value=False):
        calculator_repl(max_iterations=2)
        mock_print.assert_any_call("\x1b[33mNothing to redo\x1b[0m")

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save:
        calculator_repl(max_iterations=2)
        mock_save.assert_called()
        mock_print.assert_any_call("\x1b[33mHistory saved successfully\x1b[0m")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history') as mock_load:
        calculator_repl(max_iterations=2)
        mock_load.assert_called()
        mock_print.assert_any_call("\x1b[33mHistory loaded successfully\x1b[0m")

@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel(mock_print, mock_input):
    calculator_repl(max_iterations=3)
    mock_print.assert_any_call("\x1b[33mOperation cancelled\x1b[0m")

@patch('builtins.input', side_effect=['nonsense', 'exit'])
@patch('builtins.print')
def test_calculator_repl_invalid_command(mock_print, mock_input):
    calculator_repl(max_iterations=2)
    mock_print.assert_any_call("\x1b[31mUnknown command: 'nonsense'. Type 'help' for available commands.\x1b[0m")

@patch('builtins.input', side_effect=KeyboardInterrupt)
@patch('builtins.print')
def test_calculator_repl_keyboard_interrupt(mock_print, mock_input):
    calculator_repl(max_iterations=1)
    mock_print.assert_any_call("\n\x1b[33mOperation cancelled\x1b[0m")

@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_calculator_repl_eof(mock_print, mock_input):
    calculator_repl(max_iterations=1)
    mock_print.assert_any_call("\n\x1b[36mInput terminated. Exiting...\x1b[0m")
