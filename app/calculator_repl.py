########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from colorama import Fore, Style, init # Using Colorama for color coded output
init(autoreset=True)

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory, Modulus, IntDivide, Percent, AbsDiff

# Register new operations with the factory
OperationFactory.register_operation('modulus', Modulus)
OperationFactory.register_operation('int_divide', IntDivide)
OperationFactory.register_operation('percent', Percent)
OperationFactory.register_operation('abs_diff', AbsDiff)


def calculator_repl(max_iterations: int = None):
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.

    Args:
        max_iterations (int, optional): For testing purposes, limits the number of loop iterations.
    """
    try:
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(f"{Fore.CYAN}Calculator started. Type 'help' for commands.{Style.RESET_ALL}")

        iterations = 0
        while True:
            if max_iterations is not None and iterations >= max_iterations:
                break
            iterations += 1

            try:
                command = input("\nEnter command: ").lower().strip()

                if command == 'help':
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root")
                    print("  modulus, int_divide, percent, abs_diff")
                    print("  history - Show calculation history")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  exit - Exit the calculator")
                    continue

                if command == 'exit':
                    try:
                        calc.save_history()
                        print(f"{Fore.YELLOW}History saved successfully.{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Warning: Could not save history: {e}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(f"{Fore.YELLOW}No calculations in history{Style.RESET_ALL}")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print(f"{Fore.YELLOW}History cleared{Style.RESET_ALL}")
                    continue

                if command == 'undo':
                    if calc.undo():
                        print(f"{Fore.YELLOW}Operation undone{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Nothing to undo{Style.RESET_ALL}")
                    continue

                if command == 'redo':
                    if calc.redo():
                        print(f"{Fore.YELLOW}Operation redone{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Nothing to redo{Style.RESET_ALL}")
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print(f"{Fore.YELLOW}History saved successfully{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Error saving history: {e}{Style.RESET_ALL}")
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print(f"{Fore.YELLOW}History loaded successfully{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Error loading history: {e}{Style.RESET_ALL}")
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root',
                               'modulus', 'int_divide', 'percent', 'abs_diff']:
                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")
                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                            continue
                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                            continue

                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)
                        result = calc.perform_operation(a, b)

                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(f"\nResult: {Fore.GREEN}{result}{Style.RESET_ALL}")
                    except (ValidationError, OperationError) as e:
                        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
                    continue

                print(f"{Fore.RED}Unknown command: '{command}'. Type 'help' for available commands.{Style.RESET_ALL}")

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                continue
            except EOFError:
                print(f"\n{Fore.CYAN}Input terminated. Exiting...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                continue

    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
