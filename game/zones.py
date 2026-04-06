"""Prison zones and navigation graph.

The prison is modelled as a small graph of named zones. The player occupies
one zone at a time. Some zones are hidden until discovered (e.g. the tunnel).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class ZoneId(str, Enum):
    YARD = "yard"
    CELL_BLOCK = "cell_block"
    WORKSHOP = "workshop"
    KITCHEN = "kitchen"
    INFIRMARY = "infirmary"
    WARDEN_CORRIDOR = "warden_corridor"
    TUNNEL = "tunnel"


@dataclass
class Zone:
    id: ZoneId
    name: str
    description: str
    connections: List[ZoneId] = field(default_factory=list)
    hidden: bool = False
    # Base suspicion added just for being seen here. Most zones are 0.
    suspicion_on_enter: int = 0


def build_prison() -> Dict[ZoneId, Zone]:
    """Build the default prison graph."""
    zones: Dict[ZoneId, Zone] = {
        ZoneId.YARD: Zone(
            id=ZoneId.YARD,
            name="The Yard",
            description="Open ground. Factions stake territory. Everyone is watching everyone.",
            connections=[ZoneId.CELL_BLOCK, ZoneId.WORKSHOP, ZoneId.KITCHEN],
        ),
        ZoneId.CELL_BLOCK: Zone(
            id=ZoneId.CELL_BLOCK,
            name="Cell Block",
            description="Rows of steel doors. Your cell is here. Quiet enough to talk.",
            connections=[ZoneId.YARD, ZoneId.INFIRMARY, ZoneId.TUNNEL],
        ),
        ZoneId.WORKSHOP: Zone(
            id=ZoneId.WORKSHOP,
            name="Workshop",
            description="Metal shavings and borrowed tools. Things go missing here.",
            connections=[ZoneId.YARD, ZoneId.WARDEN_CORRIDOR],
        ),
        ZoneId.KITCHEN: Zone(
            id=ZoneId.KITCHEN,
            name="Kitchen",
            description="Steam, shouting, knives chained to the counters.",
            connections=[ZoneId.YARD, ZoneId.INFIRMARY],
        ),
        ZoneId.INFIRMARY: Zone(
            id=ZoneId.INFIRMARY,
            name="Infirmary",
            description="Bleach and whispered confessions. The doctor listens.",
            connections=[ZoneId.CELL_BLOCK, ZoneId.KITCHEN],
        ),
        ZoneId.WARDEN_CORRIDOR: Zone(
            id=ZoneId.WARDEN_CORRIDOR,
            name="Warden's Corridor",
            description="Polished linoleum. You are not supposed to be here.",
            connections=[ZoneId.WORKSHOP],
            suspicion_on_enter=2,
        ),
        ZoneId.TUNNEL: Zone(
            id=ZoneId.TUNNEL,
            name="The Tunnel",
            description="Cold earth. Your secret. Your way out.",
            connections=[ZoneId.CELL_BLOCK],
            hidden=True,
        ),
    }
    return zones
