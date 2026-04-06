"""Colours, sizes, and font helpers for the UI.

Palette is intentionally desaturated and gloomy to match the GDD's tone.
"""

from __future__ import annotations

import pygame

# ----- window
WINDOW_W = 1024
WINDOW_H = 680
FPS = 60
TITLE = "Convict Code"

# ----- palette (R, G, B)
BG          = (18,  18,  22)
BG_PANEL    = (30,  30,  36)
BG_PANEL_2  = (40,  40,  48)
BORDER      = (70,  70,  80)
BORDER_HI   = (140, 130, 90)

TEXT        = (220, 220, 210)
TEXT_DIM    = (150, 150, 140)
TEXT_WARN   = (220, 170, 80)
TEXT_BAD    = (210, 80,  80)
TEXT_GOOD   = (130, 200, 130)

BTN         = (55,  55,  65)
BTN_HOVER   = (80,  80,  95)
BTN_DOWN    = (100, 100, 120)
BTN_DISABLE = (35,  35,  40)

SUSPICION_BAR_BG = (50, 30, 30)
SUSPICION_BAR_FG = (200, 70, 70)

LOYALTY_BAR_BG = (35, 45, 35)
LOYALTY_BAR_FG = (110, 180, 110)

PROGRESS_BAR_BG = (35, 35, 50)
PROGRESS_BAR_FG = (110, 140, 200)

# ----- pixel-art palette used by art.py
PA_SKIN_LIGHT = (210, 175, 140)
PA_SKIN_MID   = (170, 130, 100)
PA_SKIN_DARK  = (110, 80,  60)
PA_HAIR_DARK  = (40,  30,  25)
PA_HAIR_GREY  = (170, 170, 170)
PA_JUMPSUIT   = (180, 100, 50)
PA_JUMPSUIT_D = (130, 70,  35)
PA_BARS       = (90,  90,  100)
PA_FLOOR      = (70,  60,  50)
PA_WALL       = (60,  55,  60)
PA_DIRT       = (90,  70,  50)
PA_GRASS      = (70,  100, 60)
PA_METAL      = (130, 130, 140)
PA_BRICK      = (120, 70,  60)
PA_WOOD       = (110, 75,  45)
PA_LIGHT      = (240, 220, 150)
PA_BLOOD      = (140, 40,  40)


_FONT_CACHE: dict = {}


def font(size: int, bold: bool = False) -> pygame.font.Font:
    """Cached font lookup. Uses default pygame font for portability."""
    key = (size, bold)
    if key not in _FONT_CACHE:
        f = pygame.font.SysFont("dejavusansmono,monospace", size, bold=bold)
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]
