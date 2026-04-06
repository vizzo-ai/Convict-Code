"""Actions the player can spend AP on during a day.

Each action is a small function that mutates GameState and returns an
ActionResult describing what happened. Keeping actions here (rather than
scattered through the UI) means they can be tested in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .crew import CrewMember
from .escape import EscapeComponent
from .state import GameState
from .zones import ZoneId


@dataclass
class ActionResult:
    ok: bool
    message: str


# ---------------------------------------------------------------- helpers

def _require_ap(state: GameState, cost: int) -> Optional[ActionResult]:
    if state.game_over is not None:
        return ActionResult(False, "The game is over.")
    if not state.spend_ap(cost):
        return ActionResult(False, f"Not enough action points (need {cost}).")
    return None


# ---------------------------------------------------------------- actions

def lie_low(state: GameState) -> ActionResult:
    """Spend the day keeping your head down. Drops suspicion."""
    err = _require_ap(state, 2)
    if err:
        return err
    state.add_suspicion(-5, "lying low")
    return ActionResult(True, "You keep your head down. The heat eases a little.")


def work_prison_job(state: GameState) -> ActionResult:
    """Legitimate work. Small resources, small suspicion drop."""
    err = _require_ap(state, 2)
    if err:
        return err
    state.resources.add(favours=1)
    state.add_suspicion(-2, "prison job")
    return ActionResult(True, "You put in an honest day's work. Earned a favour.")


def source_contraband(state: GameState) -> ActionResult:
    """High risk, high reward."""
    err = _require_ap(state, 2)
    if err:
        return err
    if state.current_zone not in (ZoneId.WORKSHOP, ZoneId.KITCHEN, ZoneId.YARD):
        state.ap += 2  # refund
        return ActionResult(False, "Nowhere to get contraband from here.")
    state.resources.add(contraband=2)
    state.add_suspicion(8, "sourcing contraband")
    return ActionResult(True, "You scored two pieces of contraband. Eyes on you now.")


def craft_tool(state: GameState) -> ActionResult:
    """Turn contraband into a tool in the workshop."""
    err = _require_ap(state, 1)
    if err:
        return err
    if state.current_zone != ZoneId.WORKSHOP:
        state.ap += 1
        return ActionResult(False, "You can only shape tools in the workshop.")
    if not state.resources.spend(contraband=1):
        state.ap += 1
        return ActionResult(False, "No contraband to work with.")
    state.resources.add(tools=1)
    state.add_suspicion(3, "crafting tools")
    return ActionResult(True, "You sharpen and hide a crude tool.")


def dig_tunnel(state: GameState) -> ActionResult:
    """Advance the exit route. Requires tools and access to cell block/tunnel."""
    err = _require_ap(state, 2)
    if err:
        return err
    if state.current_zone not in (ZoneId.CELL_BLOCK, ZoneId.TUNNEL):
        state.ap += 2
        return ActionResult(False, "You can only dig from your cell.")
    if not state.resources.spend(tools=1):
        state.ap += 2
        return ActionResult(False, "No tools to dig with.")
    state.escape_plan.advance(EscapeComponent.EXIT_ROUTE, 15)
    state.add_suspicion(4, "tunnel work")
    # Reveal the tunnel once you've started.
    state.reveal_zone(ZoneId.TUNNEL)
    return ActionResult(True, "You claw out another fifteen inches of earth.")


def gather_intelligence(state: GameState) -> ActionResult:
    """Learn guard schedules: progresses Timing component."""
    err = _require_ap(state, 1)
    if err:
        return err
    state.resources.add(information=1)
    state.escape_plan.advance(EscapeComponent.TIMING, 8)
    return ActionResult(True, "You note a rotation: a guard who drinks on Thursdays.")


def arrange_cover(state: GameState) -> ActionResult:
    """Spend favours to set up a distraction on the night."""
    err = _require_ap(state, 1)
    if err:
        return err
    if not state.resources.spend(favours=1):
        state.ap += 1
        return ActionResult(False, "No favours to call in.")
    state.escape_plan.advance(EscapeComponent.COVER, 20)
    return ActionResult(True, "A debt comes due. Someone will make noise that night.")


def arrange_outside(state: GameState) -> ActionResult:
    """Use the infirmary phone etc. to set up a contact outside."""
    err = _require_ap(state, 2)
    if err:
        return err
    if state.current_zone != ZoneId.INFIRMARY:
        state.ap += 2
        return ActionResult(False, "You need the infirmary to reach the outside.")
    if not state.resources.spend(information=1):
        state.ap += 2
        return ActionResult(False, "You don't know enough to make the call.")
    state.escape_plan.advance(EscapeComponent.OUTSIDE, 20)
    return ActionResult(True, "A car will be waiting three miles down the highway.")


def tie_loose_end(state: GameState, crew_id: Optional[str] = None) -> ActionResult:
    """Handle an internal threat (e.g. shore up a low-loyalty crew member)."""
    err = _require_ap(state, 1)
    if err:
        return err
    state.escape_plan.advance(EscapeComponent.LOOSE_ENDS, 15)
    if crew_id:
        member = state.crew_member(crew_id)
        member.adjust_loyalty(+10)
        return ActionResult(
            True, f"You smooth things over with {member.name}. +10 loyalty."
        )
    return ActionResult(True, "You quiet a rumour before it grows.")


def recruit(state: GameState, crew_id: str) -> ActionResult:
    """Recruit a crew member. Requires minimum loyalty."""
    err = _require_ap(state, 2)
    if err:
        return err
    member = state.crew_member(crew_id)
    if member.recruited:
        state.ap += 2
        return ActionResult(False, f"{member.name} is already with you.")
    if member.loyalty < 50:
        return ActionResult(
            False, f"{member.name} doesn't trust you enough yet ({member.loyalty}/50)."
        )
    member.recruited = True
    return ActionResult(True, f"{member.name} is in.")


def spend_time_with(state: GameState, crew_id: str) -> ActionResult:
    """Build loyalty with a crew member through conversation."""
    err = _require_ap(state, 1)
    if err:
        return err
    member = state.crew_member(crew_id)
    member.adjust_loyalty(+8)
    return ActionResult(
        True, f"You and {member.name} talk for a while. Loyalty now {member.loyalty}."
    )


def trigger_escape(state: GameState) -> ActionResult:
    """Commit to the escape tonight."""
    if state.game_over is not None:
        return ActionResult(False, "The game is over.")
    from .state import GameOverReason  # local import to avoid cycle at load

    quality = state.escape_plan.ending_quality()
    state.game_over = GameOverReason.ESCAPED
    state.note(f"Escape triggered. Quality: {quality}.")
    return ActionResult(True, f"You run for it. Ending: {quality}.")


# ---------------------------------------------------------- registry

@dataclass
class Action:
    key: str
    name: str
    ap_cost: int
    func: Callable[..., ActionResult]
    needs_crew: bool = False


AVAILABLE_ACTIONS: List[Action] = [
    Action("lie_low", "Lie low", 2, lie_low),
    Action("work", "Work prison job", 2, work_prison_job),
    Action("contraband", "Source contraband", 2, source_contraband),
    Action("craft", "Craft tool", 1, craft_tool),
    Action("dig", "Advance tunnel", 2, dig_tunnel),
    Action("intel", "Gather intelligence", 1, gather_intelligence),
    Action("cover", "Arrange a distraction", 1, arrange_cover),
    Action("outside", "Arrange outside contact", 2, arrange_outside),
    Action("loose", "Tie a loose end", 1, tie_loose_end),
    Action("recruit", "Recruit crew member", 2, recruit, needs_crew=True),
    Action("talk", "Spend time with crew", 1, spend_time_with, needs_crew=True),
    Action("escape", "Trigger the escape", 0, trigger_escape),
]


def action_by_key(key: str) -> Optional[Action]:
    for a in AVAILABLE_ACTIONS:
        if a.key == key:
            return a
    return None
