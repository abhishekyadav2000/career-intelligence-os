"""Backward-compatible loader — delegates to data_loader."""

from src.data_loader import load_all, load_raw

__all__ = ["load_all", "load_raw"]
