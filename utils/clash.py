"""Clash detection between selected course offerings."""
from __future__ import annotations
from typing import Iterable
from .slots import slots_to_cells, parse_slot_string


def cells_of_course(course: dict) -> set[tuple[str, int]]:
    """All cells (day, band) occupied by a selected course dict."""
    cells: set[tuple[str, int]] = set()
    if course.get("theory_slot"):
        cells |= slots_to_cells(course["theory_slot"])
    if course.get("lab_slot"):
        cells |= slots_to_cells(course["lab_slot"])
    return cells


def occupied_cells(selected: Iterable[dict]) -> set[tuple[str, int]]:
    """Union of every cell occupied by any selected course."""
    out: set[tuple[str, int]] = set()
    for c in selected:
        out |= cells_of_course(c)
    return out


def clashes_with(slot_str: str, selected: Iterable[dict],
                 ignore_course_code: str | None = None) -> list[str]:
    """Return the list of course_codes that clash with `slot_str`.

    A clash occurs when any cell in `slot_str` is already occupied by another
    selected course (different course_code).
    """
    if not slot_str:
        return []
    incoming = slots_to_cells(slot_str)
    if not incoming:
        return []
    conflicts: list[str] = []
    for c in selected:
        if ignore_course_code and c.get("course_code") == ignore_course_code:
            continue
        if incoming & cells_of_course(c):
            conflicts.append(c.get("course_code", "?"))
    return conflicts


def has_internal_clash(theory_slot: str, lab_slot: str) -> bool:
    """Return True if a course's own theory and lab slots overlap."""
    if not theory_slot or not lab_slot:
        return False
    return bool(slots_to_cells(theory_slot) & slots_to_cells(lab_slot))


def combo_clash(offerings: list[dict]) -> bool:
    """Return True if any two offerings in the combo occupy the same cell."""
    seen: set[tuple[str, int]] = set()
    for off in offerings:
        cells = set()
        if off.get("theory_slot"):
            cells |= slots_to_cells(off["theory_slot"])
        if off.get("lab_slot"):
            cells |= slots_to_cells(off["lab_slot"])
        if cells & seen:
            return True
        seen |= cells
    return False


def pretty_slot(slot_str: str) -> str:
    """Normalise display of a slot string."""
    return "+".join(parse_slot_string(slot_str))
