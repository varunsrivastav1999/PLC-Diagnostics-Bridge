class PLCConnectionError(Exception):
    """Raised when a PLC connection attempt fails."""
    pass

class PLCReadError(Exception):
    """Raised when a PLC read operation fails."""
    pass

class PLCWriteError(Exception):
    """Raised when a PLC write operation fails."""
    pass

class PLCTimeoutError(Exception):
    """Raised when a PLC operation exceeds the configured timeout."""
    pass
