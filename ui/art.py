"""Procedural low-res pixel art.

Everything is drawn into small pygame Surfaces (typically 80x50 or 24x32)
and then scaled up with nearest-neighbour. No external assets are required.
"""

from __future__ import annotations

import random
from typing import Callable, Dict

import pygame

from . import theme as T
from game.zones import ZoneId


# ------------------------------------------------------------ helpers

def _new(w: int, h: int, bg=(0, 0, 0)) -> pygame.Surface:
    s = pygame.Surface((w, h))
    s.fill(bg)
    return s


def _rect(s: pygame.Surface, x: int, y: int, w: int, h: int, color) -> None:
    pygame.draw.rect(s, color, (x, y, w, h))


def _px(s: pygame.Surface, x: int, y: int, color) -> None:
    s.set_at((x, y), color)


def scale(surface: pygame.Surface, factor: int) -> pygame.Surface:
    w, h = surface.get_size()
    return pygame.transform.scale(surface, (w * factor, h * factor))


# --------------------------------------------------------- zone scenes
# Base resolution 80x50. Scaled 6x at draw time → 480x300.

def _scene_cell_block() -> pygame.Surface:
    s = _new(80, 50, T.PA_WALL)
    # back wall texture
    for y in range(0, 50, 4):
        for x in range(0, 80, 6):
            _px(s, x, y, (45, 45, 50))
    # floor
    _rect(s, 0, 40, 80, 10, T.PA_FLOOR)
    # bunk
    _rect(s, 8, 30, 24, 4, T.PA_METAL)
    _rect(s, 8, 34, 4, 6, T.PA_METAL)
    _rect(s, 28, 34, 4, 6, T.PA_METAL)
    _rect(s, 8, 28, 24, 2, (140, 130, 110))
    # toilet
    _rect(s, 60, 32, 8, 8, (200, 200, 210))
    # bars in front
    for x in range(0, 80, 6):
        _rect(s, x, 0, 2, 50, T.PA_BARS)
    _rect(s, 0, 22, 80, 2, T.PA_BARS)
    return s


def _scene_yard() -> pygame.Surface:
    s = _new(80, 50, (60, 70, 100))
    # ground
    _rect(s, 0, 30, 80, 20, T.PA_GRASS)
    _rect(s, 0, 36, 80, 14, (60, 85, 50))
    # fence
    for x in range(2, 80, 4):
        _rect(s, x, 18, 1, 14, T.PA_METAL)
    _rect(s, 0, 18, 80, 1, T.PA_METAL)
    _rect(s, 0, 24, 80, 1, T.PA_METAL)
    _rect(s, 0, 30, 80, 1, T.PA_METAL)
    # razor wire
    for x in range(0, 80, 3):
        _px(s, x, 16, (200, 200, 210))
        _px(s, x + 1, 17, (200, 200, 210))
    # watchtower silhouette
    _rect(s, 60, 6, 12, 14, (40, 30, 25))
    _rect(s, 56, 6, 20, 4, (35, 25, 20))
    _px(s, 64, 9, T.PA_LIGHT)
    _px(s, 65, 9, T.PA_LIGHT)
    return s


def _scene_workshop() -> pygame.Surface:
    s = _new(80, 50, (55, 50, 45))
    # floor
    _rect(s, 0, 38, 80, 12, T.PA_FLOOR)
    # workbench
    _rect(s, 8, 28, 64, 4, T.PA_WOOD)
    _rect(s, 8, 32, 4, 10, T.PA_WOOD)
    _rect(s, 68, 32, 4, 10, T.PA_WOOD)
    # tools on pegboard
    _rect(s, 6, 6, 68, 18, (80, 65, 50))
    # hammer
    _rect(s, 12, 10, 6, 2, T.PA_WOOD)
    _rect(s, 17, 8, 3, 6, T.PA_METAL)
    # wrench
    _rect(s, 26, 10, 2, 10, T.PA_METAL)
    _px(s, 25, 10, T.PA_METAL)
    _px(s, 28, 10, T.PA_METAL)
    # saw
    _rect(s, 38, 12, 16, 2, T.PA_METAL)
    for x in range(38, 54):
        _px(s, x, 14, T.PA_METAL)
    # pipe
    _rect(s, 60, 10, 10, 2, T.PA_METAL)
    return s


def _scene_kitchen() -> pygame.Surface:
    s = _new(80, 50, (55, 55, 60))
    # tile wall
    for y in range(0, 30, 4):
        for x in range(0, 80, 8):
            _rect(s, x, y, 7, 3, (180, 180, 175))
    # counter
    _rect(s, 0, 30, 80, 4, (160, 160, 165))
    _rect(s, 0, 34, 80, 16, (90, 90, 95))
    # pot
    _rect(s, 10, 24, 14, 6, (60, 60, 65))
    _px(s, 9, 25, (60, 60, 65))
    _px(s, 24, 25, (60, 60, 65))
    # steam
    for x in (12, 16, 20):
        _px(s, x, 20, (200, 200, 200))
        _px(s, x, 22, (180, 180, 180))
    # knife rack
    _rect(s, 50, 18, 22, 2, T.PA_WOOD)
    _rect(s, 52, 20, 2, 8, T.PA_METAL)
    _rect(s, 58, 20, 2, 8, T.PA_METAL)
    _rect(s, 64, 20, 2, 8, T.PA_METAL)
    return s


def _scene_infirmary() -> pygame.Surface:
    s = _new(80, 50, (200, 200, 200))
    # walls
    _rect(s, 0, 36, 80, 14, (180, 180, 185))
    # bed
    _rect(s, 14, 28, 36, 4, T.PA_METAL)
    _rect(s, 14, 32, 36, 8, (220, 220, 230))
    _rect(s, 14, 30, 4, 12, T.PA_METAL)
    _rect(s, 46, 30, 4, 12, T.PA_METAL)
    # pillow
    _rect(s, 16, 30, 10, 4, (240, 240, 240))
    # red cross
    _rect(s, 60, 8, 12, 12, (240, 240, 240))
    _rect(s, 64, 10, 4, 8, T.PA_BLOOD)
    _rect(s, 62, 12, 8, 4, T.PA_BLOOD)
    return s


def _scene_warden_corridor() -> pygame.Surface:
    s = _new(80, 50, (90, 80, 70))
    # tiled floor in perspective
    for y in range(28, 50, 2):
        shade = 70 + (y - 28)
        _rect(s, 0, y, 80, 2, (shade, shade - 5, shade - 10))
    for x in range(0, 80, 8):
        for y in range(28, 50, 2):
            _px(s, x, y, (40, 35, 30))
    # door at end
    _rect(s, 32, 14, 16, 24, (80, 55, 35))
    _rect(s, 32, 14, 16, 2, (40, 25, 15))
    _px(s, 45, 26, T.PA_LIGHT)
    # frame
    _rect(s, 30, 12, 20, 2, (50, 35, 25))
    return s


def _scene_tunnel() -> pygame.Surface:
    s = _new(80, 50, (25, 18, 12))
    # dirt walls
    for y in range(50):
        for x in range(80):
            if (x * 7 + y * 13) % 17 == 0:
                _px(s, x, y, T.PA_DIRT)
            elif (x * 3 + y * 5) % 23 == 0:
                _px(s, x, y, (50, 35, 25))
    # tunnel mouth (dark oval)
    pygame.draw.ellipse(s, (10, 6, 4), (20, 12, 40, 30))
    # tool on ground
    _rect(s, 6, 42, 10, 2, T.PA_METAL)
    _rect(s, 14, 41, 4, 4, T.PA_WOOD)
    return s


_SCENE_BUILDERS: Dict[ZoneId, Callable[[], pygame.Surface]] = {
    ZoneId.CELL_BLOCK: _scene_cell_block,
    ZoneId.YARD: _scene_yard,
    ZoneId.WORKSHOP: _scene_workshop,
    ZoneId.KITCHEN: _scene_kitchen,
    ZoneId.INFIRMARY: _scene_infirmary,
    ZoneId.WARDEN_CORRIDOR: _scene_warden_corridor,
    ZoneId.TUNNEL: _scene_tunnel,
}


_scene_cache: Dict[ZoneId, pygame.Surface] = {}


def zone_scene(zone_id: ZoneId, scale_factor: int = 6) -> pygame.Surface:
    """Get the scaled pixel-art scene for a zone, cached."""
    key = (zone_id, scale_factor)
    cached = _scene_cache.get(key)  # type: ignore[arg-type]
    if cached is not None:
        return cached
    base = _SCENE_BUILDERS[zone_id]()
    scaled = scale(base, scale_factor)
    _scene_cache[key] = scaled  # type: ignore[index]
    return scaled


# --------------------------------------------------------- portraits
# 24x32 base portraits, deterministic per crew_id seed.

_portrait_cache: Dict[str, pygame.Surface] = {}


def crew_portrait(crew_id: str, scale_factor: int = 4) -> pygame.Surface:
    key = f"{crew_id}@{scale_factor}"
    cached = _portrait_cache.get(key)
    if cached is not None:
        return cached

    rng = random.Random(crew_id)
    skins = [T.PA_SKIN_LIGHT, T.PA_SKIN_MID, T.PA_SKIN_DARK]
    hairs = [T.PA_HAIR_DARK, T.PA_HAIR_GREY, (90, 60, 30), (180, 130, 60)]
    skin = rng.choice(skins)
    hair = rng.choice(hairs)
    bald = rng.random() < 0.25
    beard = rng.random() < 0.4
    scar = rng.random() < 0.3

    s = _new(24, 32, T.BG_PANEL_2)
    # jumpsuit collar
    _rect(s, 2, 26, 20, 6, T.PA_JUMPSUIT)
    _rect(s, 2, 30, 20, 2, T.PA_JUMPSUIT_D)
    # neck
    _rect(s, 9, 22, 6, 4, skin)
    # head
    _rect(s, 6, 8, 12, 16, skin)
    # jaw shadow
    _rect(s, 6, 22, 12, 2, T.PA_SKIN_DARK)
    # hair
    if not bald:
        _rect(s, 5, 6, 14, 4, hair)
        _rect(s, 4, 8, 2, 6, hair)
        _rect(s, 18, 8, 2, 6, hair)
        if rng.random() < 0.5:
            _rect(s, 5, 5, 14, 2, hair)
    # ears
    _px(s, 5, 14, skin)
    _px(s, 18, 14, skin)
    # eyes
    _rect(s, 8, 14, 2, 2, (20, 20, 25))
    _rect(s, 14, 14, 2, 2, (20, 20, 25))
    # eyebrows
    _px(s, 8, 12, hair)
    _px(s, 9, 12, hair)
    _px(s, 14, 12, hair)
    _px(s, 15, 12, hair)
    # nose
    _px(s, 11, 17, T.PA_SKIN_DARK)
    _px(s, 12, 17, T.PA_SKIN_DARK)
    _px(s, 12, 18, T.PA_SKIN_DARK)
    # mouth
    _rect(s, 10, 20, 4, 1, (90, 50, 50))
    if beard:
        _rect(s, 8, 21, 8, 2, hair)
        _rect(s, 9, 23, 6, 1, hair)
    if scar:
        _rect(s, 16, 13, 1, 5, T.PA_BLOOD)

    scaled = scale(s, scale_factor)
    _portrait_cache[key] = scaled
    return scaled


def clear_caches() -> None:
    _scene_cache.clear()
    _portrait_cache.clear()
