"""Tracked resources: contraband, tools, information, favours."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Resources:
    contraband: int = 0
    tools: int = 0
    information: int = 0
    favours: int = 0

    def add(self, **kwargs: int) -> None:
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise KeyError(f"Unknown resource: {key}")
            setattr(self, key, getattr(self, key) + val)

    def spend(self, **kwargs: int) -> bool:
        """Try to spend resources. Returns False and changes nothing if insufficient."""
        for key, val in kwargs.items():
            if getattr(self, key) < val:
                return False
        for key, val in kwargs.items():
            setattr(self, key, getattr(self, key) - val)
        return True

    def as_dict(self) -> dict:
        return {
            "contraband": self.contraband,
            "tools": self.tools,
            "information": self.information,
            "favours": self.favours,
        }
