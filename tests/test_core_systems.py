"""Tests for the core Convict Code systems."""

import pytest

from game import (
    AVAILABLE_ACTIONS,
    EscapeComponent,
    GameState,
    GameOverReason,
    ZoneId,
)
from game.actions import (
    action_by_key,
    arrange_cover,
    arrange_outside,
    craft_tool,
    dig_tunnel,
    gather_intelligence,
    lie_low,
    recruit,
    source_contraband,
    spend_time_with,
    tie_loose_end,
    trigger_escape,
    work_prison_job,
)
from game.escape import READY_THRESHOLD
from game.state import LOCKDOWN_THRESHOLD, MAX_DAYS, STARTING_AP


# ---------------------------------------------------------------- state

def test_initial_state_defaults():
    s = GameState()
    assert s.day == 1
    assert s.ap == STARTING_AP
    assert s.suspicion == 0
    assert s.current_zone == ZoneId.CELL_BLOCK
    assert s.game_over is None


def test_action_points_spend_and_refuse():
    s = GameState()
    assert s.spend_ap(2) is True
    assert s.ap == 2
    assert s.spend_ap(5) is False
    assert s.ap == 2  # unchanged


def test_end_day_advances_clock_and_resets_ap():
    s = GameState()
    s.ap = 1
    s.end_day()
    assert s.day == 2
    assert s.ap == STARTING_AP


def test_out_of_time_game_over():
    s = GameState()
    s.day = MAX_DAYS
    s.end_day()
    assert s.game_over == GameOverReason.OUT_OF_TIME


# ---------------------------------------------------------------- suspicion

def test_suspicion_clamps_and_triggers_game_over():
    s = GameState()
    s.add_suspicion(120, "test")
    assert s.suspicion == 100
    assert s.game_over == GameOverReason.CAUGHT_SUSPICION


def test_suspicion_does_not_go_negative():
    s = GameState()
    s.add_suspicion(-50)
    assert s.suspicion == 0


def test_lockdown_blocks_movement():
    s = GameState()
    s.suspicion = LOCKDOWN_THRESHOLD
    s.end_day()
    assert s.lockdown is True
    # From cell block, all moves leaving the cell block are blocked.
    assert s.move_to(ZoneId.YARD) is False
    assert s.current_zone == ZoneId.CELL_BLOCK


# ---------------------------------------------------------------- zones

def test_movement_only_along_connections():
    s = GameState()
    assert s.current_zone == ZoneId.CELL_BLOCK
    assert s.move_to(ZoneId.WORKSHOP) is False  # not connected
    assert s.move_to(ZoneId.YARD) is True
    assert s.current_zone == ZoneId.YARD
    assert s.move_to(ZoneId.WORKSHOP) is True


def test_warden_corridor_raises_suspicion():
    s = GameState()
    s.move_to(ZoneId.YARD)
    s.move_to(ZoneId.WORKSHOP)
    before = s.suspicion
    s.move_to(ZoneId.WARDEN_CORRIDOR)
    assert s.suspicion > before


def test_tunnel_starts_hidden_and_revealed_by_digging():
    s = GameState()
    assert s.zones[ZoneId.TUNNEL].hidden is True
    s.resources.add(tools=1)
    dig_tunnel(s)
    assert s.zones[ZoneId.TUNNEL].hidden is False


# ---------------------------------------------------------------- resources

def test_resources_spend_atomic():
    s = GameState()
    s.resources.add(contraband=1, tools=1)
    # Should fail and roll back if any one is short.
    assert s.resources.spend(contraband=1, tools=2) is False
    assert s.resources.contraband == 1
    assert s.resources.tools == 1
    assert s.resources.spend(contraband=1, tools=1) is True
    assert s.resources.contraband == 0


# ---------------------------------------------------------------- crew

def test_recruit_requires_loyalty():
    s = GameState()
    member = s.crew_member("reese")
    member.loyalty = 49
    res = recruit(s, "reese")
    assert not res.ok
    assert not member.recruited
    member.loyalty = 60
    s.ap = STARTING_AP
    res = recruit(s, "reese")
    assert res.ok
    assert member.recruited


def test_spend_time_increases_loyalty():
    s = GameState()
    m = s.crew_member("boone")
    before = m.loyalty
    spend_time_with(s, "boone")
    assert m.loyalty == before + 8


def test_low_loyalty_recruit_betrays():
    s = GameState()
    m = s.crew_member("reese")
    m.recruited = True
    m.loyalty = 10
    s.end_day()
    assert s.game_over == GameOverReason.BETRAYED


# ---------------------------------------------------------------- actions

def test_lie_low_drops_suspicion():
    s = GameState()
    s.suspicion = 20
    lie_low(s)
    assert s.suspicion == 15


def test_source_contraband_requires_correct_zone():
    s = GameState()  # starts in cell block
    res = source_contraband(s)
    assert not res.ok
    s.move_to(ZoneId.YARD)
    s.ap = STARTING_AP
    res = source_contraband(s)
    assert res.ok
    assert s.resources.contraband == 2


def test_craft_tool_consumes_contraband_in_workshop():
    s = GameState()
    s.move_to(ZoneId.YARD)
    s.move_to(ZoneId.WORKSHOP)
    s.resources.add(contraband=1)
    s.ap = STARTING_AP
    res = craft_tool(s)
    assert res.ok
    assert s.resources.tools == 1
    assert s.resources.contraband == 0


def test_dig_tunnel_progresses_exit_route():
    s = GameState()
    s.resources.add(tools=2)
    dig_tunnel(s)
    assert s.escape_plan.readiness[EscapeComponent.EXIT_ROUTE] == 15


def test_gather_intelligence_progresses_timing():
    s = GameState()
    gather_intelligence(s)
    assert s.escape_plan.readiness[EscapeComponent.TIMING] == 8


def test_arrange_cover_requires_favours():
    s = GameState()
    res = arrange_cover(s)
    assert not res.ok
    s.resources.add(favours=1)
    s.ap = STARTING_AP
    res = arrange_cover(s)
    assert res.ok
    assert s.escape_plan.readiness[EscapeComponent.COVER] == 20


def test_arrange_outside_needs_infirmary_and_info():
    s = GameState()
    s.resources.add(information=1)
    res = arrange_outside(s)
    assert not res.ok  # wrong zone
    s.move_to(ZoneId.INFIRMARY)
    s.ap = STARTING_AP
    res = arrange_outside(s)
    assert res.ok
    assert s.escape_plan.readiness[EscapeComponent.OUTSIDE] == 20


def test_tie_loose_end_boosts_loyalty_when_targeted():
    s = GameState()
    m = s.crew_member("doc")
    before = m.loyalty
    tie_loose_end(s, "doc")
    assert m.loyalty == before + 10
    assert s.escape_plan.readiness[EscapeComponent.LOOSE_ENDS] == 15


def test_work_prison_job_grants_favour():
    s = GameState()
    work_prison_job(s)
    assert s.resources.favours == 1


def test_action_registry_lookup():
    assert action_by_key("dig") is not None
    assert action_by_key("nope") is None
    assert {a.key for a in AVAILABLE_ACTIONS} >= {"lie_low", "dig", "escape"}


# ---------------------------------------------------------------- escape

def test_ending_quality_scales_with_readiness():
    s = GameState()
    for c in EscapeComponent:
        s.escape_plan.advance(c, READY_THRESHOLD)
    assert s.escape_plan.fully_ready()
    assert s.escape_plan.ending_quality() == "clean"


def test_ending_pyrrhic_when_unprepared():
    s = GameState()
    assert s.escape_plan.ending_quality() == "pyrrhic"


def test_trigger_escape_ends_game():
    s = GameState()
    res = trigger_escape(s)
    assert res.ok
    assert s.game_over == GameOverReason.ESCAPED


# ---------------------------------------------------------------- happy path

def test_full_minimal_winning_run():
    """Smoke test: a scripted sequence reaches a clean escape."""
    s = GameState()
    # Build up loyalty and recruit one crew member.
    for _ in range(2):
        spend_time_with(s, "marguerite")
    s.end_day()
    recruit(s, "marguerite")
    s.end_day()

    # Force readiness via direct advancement (granular per-action paths are
    # already covered above; this test just exercises the end-to-end flow).
    for c in EscapeComponent:
        s.escape_plan.advance(c, 100)
    res = trigger_escape(s)
    assert res.ok
    assert s.escape_plan.ending_quality() == "clean"
    assert s.game_over == GameOverReason.ESCAPED
