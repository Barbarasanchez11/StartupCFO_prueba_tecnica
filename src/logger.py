import logging
import sys
from typing import Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    import colorama
    from colorama import Fore, Style, init
    init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""

    COLORS = {
        'DEBUG': '\033[36m',     
        'INFO': '\033[34m',       
        'SUCCESS': '\033[32m',   
        'WARNING': '\033[33m',    
        'ERROR': '\033[31m',     
        'CRITICAL': '\033[35m',   
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
       
        log_color = self.COLORS.get(record.levelname, '')
        levelname = record.levelname
            
        colored_level = f"{log_color}{self.BOLD}[{levelname}]{self.RESET}"
  
        log_message = super().format(record)

        log_message = log_message.replace(f"[{levelname}]", colored_level, 1)
        
        return log_message


def setup_logger(name: str = "StartupCFO", level: int = logging.INFO, use_rich: bool = True) -> logging.Logger:
    """
    Set up a logger with colored terminal output.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        use_rich: Whether to use rich library if available (default: True)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.handlers.clear()

    if RICH_AVAILABLE and use_rich:

        console = Console(stderr=True)
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True,
            show_level=True,
        )
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
    else:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    

    logging.addLevelName(25, "SUCCESS")
    
    def success(self, message, *args, **kwargs):
        """Log a success message."""
        if self.isEnabledFor(25):
            self._log(25, message, args, **kwargs)
    
    logging.Logger.success = success
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Optional logger name (default: "StartupCFO")
    
    Returns:
        Logger instance
    """
    if name is None:
        name = "StartupCFO"
    
    logger = logging.getLogger(name)

    root_logger = logging.getLogger("StartupCFO")
    if not root_logger.handlers:
        setup_logger("StartupCFO")

    return logging.getLogger(name)

