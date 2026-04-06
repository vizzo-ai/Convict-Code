"""The top-level game state: day clock, action points, suspicion, crew, map."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .crew import CrewMember, default_crew_pool
from .escape import EscapePlan
from .resources import Resources
from .zones import Zone, ZoneId, build_prison


MAX_DAYS = 30
STARTING_AP = 4
MAX_SUSPICION = 100
SEARCH_THRESHOLD = 75
LOCKDOWN_THRESHOLD = 90


class GameOverReason(str, Enum):
    CAUGHT_SUSPICION = "caught_suspicion"
    BETRAYED = "betrayed"
    OUT_OF_TIME = "out_of_time"
    ESCAPED = "escaped"


@dataclass
class GameState:
    day: int = 1
    ap: int = STARTING_AP
    suspicion: int = 0
    current_zone: ZoneId = ZoneId.CELL_BLOCK
    resources: Resources = field(default_factory=Resources)
    escape_plan: EscapePlan = field(default_factory=EscapePlan)
    zones: Dict[ZoneId, Zone] = field(default_factory=build_prison)
    crew_pool: List[CrewMember] = field(default_factory=default_crew_pool)
    lockdown: bool = False
    game_over: Optional[GameOverReason] = None
    log: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------ log
    def note(self, message: str) -> None:
        self.log.append(f"Day {self.day}: {message}")

    # -------------------------------------------------------------- lookups
    def zone(self, zone_id: ZoneId) -> Zone:
        return self.zones[zone_id]

    def crew_member(self, crew_id: str) -> CrewMember:
        for m in self.crew_pool:
            if m.id == crew_id:
                return m
        raise KeyError(f"No crew member with id {crew_id}")

    def recruited_crew(self) -> List[CrewMember]:
        return [m for m in self.crew_pool if m.recruited]

    # ---------------------------------------------------------- suspicion
    def add_suspicion(self, amount: int, reason: str = "") -> None:
        self.suspicion = max(0, min(MAX_SUSPICION, self.suspicion + amount))
        if reason and amount != 0:
            sign = "+" if amount > 0 else ""
            self.note(f"Suspicion {sign}{amount} ({reason}). Now {self.suspicion}.")
        if self.suspicion >= MAX_SUSPICION and self.game_over is None:
            self.game_over = GameOverReason.CAUGHT_SUSPICION
            self.note("The guards have figured it out. You're done.")

    # ----------------------------------------------------------- movement
    def move_to(self, zone_id: ZoneId) -> bool:
        here = self.zone(self.current_zone)
        if zone_id not in here.connections:
            return False
        target = self.zone(zone_id)
        if target.hidden:
            # Hidden zones (the tunnel) don't fire the normal suspicion bump.
            pass
        elif target.suspicion_on_enter:
            self.add_suspicion(target.suspicion_on_enter, f"seen in {target.name}")
        if self.lockdown and zone_id != ZoneId.CELL_BLOCK:
            return False
        self.current_zone = zone_id
        return True

    def reveal_zone(self, zone_id: ZoneId) -> None:
        self.zones[zone_id].hidden = False

    # --------------------------------------------------------- day cycle
    def spend_ap(self, cost: int) -> bool:
        if cost > self.ap:
            return False
        self.ap -= cost
        return True

    def end_day(self) -> None:
        """Night resolution: threats escalate, lockdowns check, day advances."""
        # Lockdown kicks in if suspicion is very high.
        self.lockdown = self.suspicion >= LOCKDOWN_THRESHOLD
        if self.suspicion >= SEARCH_THRESHOLD:
            self.note("Random cell searches tonight. Hidden items may be lost.")
        if self.lockdown:
            self.note("Lockdown. Movement restricted to your cell.")

        # Any at-risk crew member rolls for betrayal under pressure.
        for member in self.recruited_crew():
            if member.is_at_risk():
                self.note(
                    f"{member.name}'s loyalty is dangerously low. They may inform."
                )
                # Guards pressuring low-loyalty recruits leak plans.
                if member.loyalty <= 15:
                    self.game_over = GameOverReason.BETRAYED
                    self.note(f"{member.name} talked. The plan is blown.")
                    return

        # Advance day.
        self.day += 1
        self.ap = STARTING_AP
        if self.day > MAX_DAYS and self.game_over is None:
            self.game_over = GameOverReason.OUT_OF_TIME
            self.note("You never made your move in time.")

    # --------------------------------------------------------- snapshot
    def status(self) -> Dict:
        return {
            "day": self.day,
            "ap": self.ap,
            "suspicion": self.suspicion,
            "lockdown": self.lockdown,
            "zone": self.current_zone.value,
            "resources": self.resources.as_dict(),
            "escape": {c.value: v for c, v in self.escape_plan.readiness.items()},
            "crew": [
                {"id": m.id, "name": m.name, "role": m.role.value, "loyalty": m.loyalty}
                for m in self.recruited_crew()
            ],
            "game_over": self.game_over.value if self.game_over else None,
        }
