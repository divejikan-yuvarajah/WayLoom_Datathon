"""Task 2A demand forecasting support, from canonical history through features."""

from .history import HistoryValidationError, build_task2a_history
from .multihorizon import build_direct_multihorizon_table

__all__ = ["HistoryValidationError", "build_task2a_history", "build_direct_multihorizon_table"]
