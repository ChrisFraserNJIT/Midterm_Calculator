import pytest
import datetime
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation

class TestCalculatorMemento:
    def test_to_dict_and_from_dict(self):
        """Test that a memento can be serialized to a dict and restored correctly."""
        # Create some dummy calculations with proper datetime timestamps
        ts1 = datetime.datetime(2025, 10, 23, 17, 22, 51, 794783)
        ts2 = datetime.datetime(2025, 10, 23, 17, 23, 1, 123456)

        calc1 = Calculation(operation="Addition", operand1=2, operand2=3, timestamp=ts1)
        calc1.result = 5

        calc2 = Calculation(operation="Subtraction", operand1=5, operand2=2, timestamp=ts2)
        calc2.result = 3

        history = [calc1, calc2]
        memento = CalculatorMemento(history=history)

        # Convert to dict
        data = memento.to_dict()
        assert 'history' in data
        assert 'timestamp' in data
        assert len(data['history']) == 2
        assert data['history'][0]['operation'] == "Addition"

        # Restore from dict
        restored_memento = CalculatorMemento.from_dict(data)
        assert isinstance(restored_memento, CalculatorMemento)
        assert len(restored_memento.history) == 2
        assert restored_memento.history[0].operation == "Addition"
        assert restored_memento.history[1].result == 3
        # Check timestamp is a datetime object
        assert isinstance(restored_memento.timestamp, datetime.datetime)

    def test_empty_history(self):
        """Test memento with empty history."""
        memento = CalculatorMemento(history=[])
        data = memento.to_dict()
        assert data['history'] == []

        restored = CalculatorMemento.from_dict(data)
        assert restored.history == []
        assert isinstance(restored.timestamp, datetime.datetime)
