from typing import Callable, List
from asyncio import iscoroutinefunction

class CheckError(Exception):
    """An exception raised when a check fails."""
    pass

class Check:
    """Checks made for commands."""

    def __init__(self, func: Callable):
        self.func = func
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Command:
    """Commands for the ClientCommands bot."""
    def __init__(self, func: Callable, *, name: str = None, description: str = None,
                 example: str = None):
        if not iscoroutinefunction(func):
            raise TypeError("The function must be async.")
        self.callback = func
        self.checks: List[Check] = []
        self.name = name or func.__name__
        if hasattr(func, 'checks'):
            if isinstance(func.checks, list):
                self.checks.extend(func.checks)

        
        
    async def __call__(self, message, *args, **kwargs):
        if await self.can_run(message):
            return await self.callback(message, *args, **kwargs)
        raise CheckError(f"Checks failed for {self.name}.")

    async def can_run(self, message):
        for check in self.checks:
            if not check(message):
                return False
        return True 