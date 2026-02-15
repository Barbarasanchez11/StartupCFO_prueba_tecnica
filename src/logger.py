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
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[34m',       # Blue
        'SUCCESS': '\033[32m',    # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        # Get the color for this log level
        log_color = self.COLORS.get(record.levelname, '')
        levelname = record.levelname
            
        # Create colored prefix
        colored_level = f"{log_color}{self.BOLD}[{levelname}]{self.RESET}"
        
        # Format the message
        log_message = super().format(record)
        # Replace the default levelname with colored one
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
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    if RICH_AVAILABLE and use_rich:
        # Use Rich for beautiful terminal output
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
        # Fallback to colored formatter
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Add custom SUCCESS level
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
    
    # If logger doesn't have handlers, set it up
    # Check if root logger has handlers (means setup_logger was called)
    root_logger = logging.getLogger("StartupCFO")
    if not root_logger.handlers:
        setup_logger("StartupCFO")
    
    # Return logger with the requested name (will inherit from root)
    return logging.getLogger(name)

