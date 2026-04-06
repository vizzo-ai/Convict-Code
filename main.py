"""Convict Code - text-mode driver for manually exercising the core systems.

This is intentionally bare-bones. It is not the final Pygame UI; it is a
debug shell so the Week 1 systems can be poked at directly.

Run with:
    python main.py
"""

from __future__ import annotations

from game import AVAILABLE_ACTIONS, GameState, ZoneId
from game.actions import action_by_key


def render(state: GameState) -> None:
    zone = state.zone(state.current_zone)
    print()
    print("=" * 60)
    print(f"Day {state.day}/30   AP {state.ap}   Suspicion {state.suspicion}/100"
          + ("   [LOCKDOWN]" if state.lockdown else ""))
    print(f"Location: {zone.name}")
    print(f"  {zone.description}")
    res = state.resources
    print(
        f"Resources: contraband={res.contraband} tools={res.tools} "
        f"info={res.information} favours={res.favours}"
    )
    crew = state.recruited_crew()
    if crew:
        print("Crew:")
        for m in crew:
            print(f"  - {m.name} ({m.role.value}) loyalty={m.loyalty}")
    print("Escape plan:")
    for component, value in state.escape_plan.readiness.items():
        bar = "#" * (value // 10) + "." * (10 - value // 10)
        print(f"  {component.value:11s} [{bar}] {value}/100")


def show_menu(state: GameState) -> None:
    print()
    print("Commands:")
    here = state.zone(state.current_zone)
    visible = [c for c in here.connections if not state.zones[c].hidden
               or state.zones[c].id == ZoneId.TUNNEL and not state.zones[c].hidden]
    print("  go <zone>      where <zone> is one of:",
          ", ".join(c.value for c in here.connections if not state.zones[c].hidden))
    for action in AVAILABLE_ACTIONS:
        suffix = " <crew_id>" if action.needs_crew else ""
        print(f"  {action.key}{suffix}  ({action.ap_cost} AP) - {action.name}")
    print("  end            end the day")
    print("  status         reprint state")
    print("  crew           list crew pool")
    print("  quit           exit")


def list_crew(state: GameState) -> None:
    print()
    for m in state.crew_pool:
        flag = "*" if m.recruited else " "
        print(f"  {flag} {m.id:11s} {m.name:18s} {m.role.value:9s} "
              f"loyalty={m.loyalty}")
        print(f"      {m.bio}")


def main() -> None:
    state = GameState()
    print("CONVICT CODE - prototype shell")
    print("Type 'help' to see commands.\n")
    render(state)

    while state.game_over is None:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not raw:
            continue
        parts = raw.split()
        cmd, args = parts[0], parts[1:]

        if cmd in ("help", "?"):
            show_menu(state)
        elif cmd == "status":
            render(state)
        elif cmd == "crew":
            list_crew(state)
        elif cmd == "quit":
            return
        elif cmd == "go":
            if not args:
                print("Where to?")
                continue
            try:
                target = ZoneId(args[0])
            except ValueError:
                print("Unknown zone.")
                continue
            if state.move_to(target):
                render(state)
            else:
                print("You can't go there from here.")
        elif cmd == "end":
            state.end_day()
            render(state)
        else:
            action = action_by_key(cmd)
            if not action:
                print("Unknown command. Type 'help'.")
                continue
            try:
                if action.needs_crew:
                    if not args:
                        print("Which crew member? (use 'crew' to list)")
                        continue
                    result = action.func(state, args[0])
                else:
                    result = action.func(state)
            except KeyError as exc:
                print(f"Error: {exc}")
                continue
            print(result.message)
            render(state)

    print()
    print(f"GAME OVER: {state.game_over.value}")
    if state.log:
        print("\nLog:")
        for line in state.log[-10:]:
            print("  " + line)


if __name__ == "__main__":
    main()
