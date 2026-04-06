"""Immediate-mode UI helpers: buttons, bars, text.

Immediate-mode style: each frame, the screen logic calls `button(...)` and
gets back True if it was clicked this frame. No retained widget tree to keep
in sync with the game state.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from . import theme as T


class InputState:
    """Per-frame input snapshot passed to the immediate-mode helpers."""

    def __init__(self) -> None:
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.click: bool = False        # left click released this frame
        self.right_click: bool = False
        self.keys_pressed: List[int] = []  # KEYDOWN events this frame

    def reset_frame(self) -> None:
        self.click = False
        self.right_click = False
        self.keys_pressed = []

    def feed(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.click = True
                self.mouse_pos = event.pos
            elif event.button == 3:
                self.right_click = True
                self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_pos = event.pos
        elif event.type == pygame.KEYDOWN:
            self.keys_pressed.append(event.key)


def button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    inp: InputState,
    enabled: bool = True,
    hotkey: Optional[int] = None,
    font_size: int = 16,
) -> bool:
    """Draw a button. Returns True if clicked (or hotkey pressed) this frame."""
    hovered = enabled and rect.collidepoint(inp.mouse_pos)

    if not enabled:
        bg = T.BTN_DISABLE
        text_color = T.TEXT_DIM
    elif hovered:
        bg = T.BTN_HOVER
        text_color = T.TEXT
    else:
        bg = T.BTN
        text_color = T.TEXT

    pygame.draw.rect(surface, bg, rect, border_radius=4)
    border = T.BORDER_HI if hovered else T.BORDER
    pygame.draw.rect(surface, border, rect, width=1, border_radius=4)

    f = T.font(font_size)
    text = f.render(label, True, text_color)
    tx = rect.x + (rect.w - text.get_width()) // 2
    ty = rect.y + (rect.h - text.get_height()) // 2
    surface.blit(text, (tx, ty))

    clicked = False
    if enabled:
        if hovered and inp.click:
            clicked = True
        if hotkey is not None and hotkey in inp.keys_pressed:
            clicked = True
    return clicked


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: Tuple[int, int],
    size: int = 16,
    color=T.TEXT,
    bold: bool = False,
) -> pygame.Rect:
    f = T.font(size, bold=bold)
    surf = f.render(text, True, color)
    surface.blit(surf, pos)
    return surf.get_rect(topleft=pos)


def wrap_text(text: str, font: pygame.font.Font, max_w: int) -> List[str]:
    out: List[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        cur = ""
        for w in words:
            candidate = w if not cur else cur + " " + w
            if font.size(candidate)[0] <= max_w:
                cur = candidate
            else:
                if cur:
                    out.append(cur)
                cur = w
        out.append(cur)
    return out


def draw_wrapped(
    surface: pygame.Surface,
    text: str,
    rect: pygame.Rect,
    size: int = 14,
    color=T.TEXT_DIM,
) -> int:
    """Returns the y just below the last drawn line."""
    f = T.font(size)
    lines = wrap_text(text, f, rect.w)
    y = rect.y
    for line in lines:
        if y + f.get_height() > rect.bottom:
            break
        surface.blit(f.render(line, True, color), (rect.x, y))
        y += f.get_height() + 2
    return y


def draw_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    value: int,
    max_value: int,
    bg_color,
    fg_color,
    label: Optional[str] = None,
) -> None:
    pygame.draw.rect(surface, bg_color, rect, border_radius=2)
    pct = max(0.0, min(1.0, value / max_value if max_value > 0 else 0))
    inner = pygame.Rect(rect.x, rect.y, int(rect.w * pct), rect.h)
    if inner.w > 0:
        pygame.draw.rect(surface, fg_color, inner, border_radius=2)
    pygame.draw.rect(surface, T.BORDER, rect, width=1, border_radius=2)
    if label:
        f = T.font(12)
        text = f.render(label, True, T.TEXT)
        tx = rect.x + (rect.w - text.get_width()) // 2
        ty = rect.y + (rect.h - text.get_height()) // 2
        surface.blit(text, (tx, ty))


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, hi: bool = False) -> None:
    pygame.draw.rect(surface, T.BG_PANEL, rect, border_radius=6)
    border = T.BORDER_HI if hi else T.BORDER
    pygame.draw.rect(surface, border, rect, width=1, border_radius=6)
