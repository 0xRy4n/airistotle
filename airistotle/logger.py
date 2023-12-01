"""
:mod:`logger.py` -- **** Common Libray : Logging functions
===============================================================
.. module:: Taken from the **** Log Module (8-11-2023)
    :synopsis: Customized logging and error handling.
.. moduleauthor:: Ryan Gordon <

This module contains a customized log formatter, a custom logger class, and various
functions and classes for use in error handling. The most prominent thing featured here
is the GlobalLogger class, which is a custom logger useful for standardizing logging
through different modules of a larger project.
"""

# Standard library imports
import logging
import traceback

# Third Party Imports
import colorama
import functools

from colorama import Fore
from typing import Optional as Opt


class LogFormatter(logging.Formatter):
    """
    Custom formatter that adds color to log messages based on the log level.
    Adds an additional style for level 5 messages (AUDIT in the GlobalLogger class).

    :param record: Log record to format.
    """

    def __init__(self):
        """Initializes the formatter, initializes colorama."""
        super().__init__(fmt="%(message)s", datefmt=None, style="%")
        colorama.init(autoreset=True)  # Auto reverts line colors to default

    def format(self, record: logging.LogRecord) -> str:
        """Overrides the format method of the logging.Formatter class. Adds color and per-level formatting."""
        format_orig = self._style._fmt

        if record.levelno == 5:
            self._style._fmt = f"{Fore.MAGENTA}[#] %(asctime)s - %(name)s - %(levelname)s : %(message)s"
        elif record.levelno == 10:
            self._style._fmt = f"{Fore.LIGHTMAGENTA_EX}[%%] %(asctime)s - %(name)s - %(levelname)s : %(message)s"
        elif record.levelno == 20:
            self._style._fmt = f"{Fore.LIGHTWHITE_EX}[*] %(asctime)s - %(name)s - %(levelname)s : %(message)s"
        elif record.levelno == 30:
            self._style._fmt = f"{Fore.LIGHTYELLOW_EX}[!] %(asctime)s - %(name)s - %(levelname)s : %(message)s"
        elif record.levelno == 40:
            self._style._fmt = f"{Fore.LIGHTRED_EX}[X] %(asctime)s - %(name)s - %(levelname)s : %(message)s"
        elif record.levelno == 50:
            # We'll use a cross here because if you see a critical error only the gods can help you
            self._style._fmt = (
                f"{Fore.RED}[†] %(asctime)s - %(name)s - %(levelname)s : %(message)s"
            )

        result = logging.Formatter.format(self, record)
        self._style._fmt = format_orig

        return result


class GlobalLogger(logging.Logger):
    """
    Defines a a custom global logger that can be used throughout an application.
    The first time this class is instantiated, it will create a base logger, which
    will serve as the parent for all other loggers created with this class. Unset
    paramaters for new loggers will inherit the parameters of the base logger.
    Adds a custom AUDIT level to the logger, which is treated as being one level
    below DEBUG.

    :param name: Name of the logger. Defaults to the name of the base logger.
    :param level: Logging level. Defaults to the level of the base logger.
    :param log_file: Path to the log file. If provided, will create a file handler.
    :param formatter: Custom formatter to use for the logger. Defaults to LogFormatter
        class contained in this module.
    """

    logging.addLevelName(5, "AUDIT")

    _base_logger = None

    _defaults = {
        "name": "GlobalLogger",
        "level": logging.DEBUG,
        "log_file": None,
        "formatter": LogFormatter(),
    }

    def __init__(
        self,
        name: Opt[str] = None,
        level: Opt[int] = None,
        log_file: Opt[str] = None,
        formatter: Opt[logging.Formatter] = None,
    ):
        self.__set_parameters(
            name=name, level=level, log_file=log_file, formatter=formatter
        )
        super().__init__(self.name, self.level)

        # Setup file handling if a log file is specified.
        if self.log_file:  # type: ignore
            self.fhandler = logging.FileHandler(self.log_file)  # type: ignore
            self.fhandler.setFormatter(self.formatter)  # type: ignore
            self.addHandler(self.fhandler)

        self.shandler = logging.StreamHandler()
        self.shandler.setFormatter(self.formatter)  # type: ignore
        self.addHandler(self.shandler)

    def __new__(cls, *args, **kwargs) -> "GlobalLogger":
        new_logger = super().__new__(cls)
        if cls._base_logger:
            new_logger.parent = cls._base_logger
        else:
            cls._base_logger = new_logger
        return new_logger

    def __set_parameters(self, **kwargs):
        for key, value in kwargs.items():
            if value:
                setattr(self, key, value)
            elif hasattr(self.__class__._base_logger, key):
                setattr(self, key, getattr(self.__class__._base_logger, key))
            else:
                setattr(self, key, self._defaults[key])

    def audit(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(5):
            self._log(5, msg, args, **kwargs)


class HandleErrorsMeta(type):
    """
    Defines a class-level metaclass which wraps all methods in a class with error handling.
    Ignores the __init__ method.
    """

    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if attr_name == "__init__":
                continue
            if callable(attr_value):
                attrs[attr_name] = cls.wrap_method_with_handle_errors(attr_value)
        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def wrap_method_with_handle_errors(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            log = GlobalLogger(__name__)
            try:
                return method(*args, **kwargs)
            except Exception as e:
                log.warning(f"Error in method: {method.__name__}")
                log.error(e)
                log.debug(traceback.format_exc())

        return wrapper
