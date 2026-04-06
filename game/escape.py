"""The five-component escape plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class EscapeComponent(str, Enum):
    EXIT_ROUTE = "exit_route"       # the tunnel, usually
    TIMING = "timing"               # the right night
    COVER = "cover"                 # delay the alarm
    OUTSIDE = "outside"             # transport and contact
    LOOSE_ENDS = "loose_ends"       # internal threats silenced


READINESS_MAX = 100
READY_THRESHOLD = 80


@dataclass
class EscapePlan:
    readiness: Dict[EscapeComponent, int] = field(
        default_factory=lambda: {c: 0 for c in EscapeComponent}
    )

    def advance(self, component: EscapeComponent, amount: int) -> None:
        current = self.readiness[component]
        self.readiness[component] = max(0, min(READINESS_MAX, current + amount))

    def is_component_ready(self, component: EscapeComponent) -> bool:
        return self.readiness[component] >= READY_THRESHOLD

    def ready_components(self) -> int:
        return sum(1 for c in EscapeComponent if self.is_component_ready(c))

    def fully_ready(self) -> bool:
        return self.ready_components() == len(EscapeComponent)

    def ending_quality(self) -> str:
        """Quality label based on how many components are ready at escape time."""
        ready = self.ready_components()
        if ready == 5:
            return "clean"
        if ready == 4:
            return "rough"
        if ready == 3:
            return "solo"
        if ready <= 2:
            return "pyrrhic"
        return "pyrrhic"
