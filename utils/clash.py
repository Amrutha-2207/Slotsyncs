"""Clash detection using physical minute-intervals."""
from __future__ import annotations
from typing import Iterable
from .slots import (
    intervals_of_slot, any_overlap, intervals_overlap, parse_slot_string,
)


def intervals_of_course(course: dict) -> list[tuple[str, int, int]]:
    """Every physical interval a selected course occupies."""
    out: list[tuple[str, int, int]] = []
    if course.get("theory_slot"):
        out.extend(intervals_of_slot(course["theory_slot"]))
    if course.get("lab_slot"):
        out.extend(intervals_of_slot(course["lab_slot"]))
    return out


def clashes_with(slot_str: str, selected: Iterable[dict],
                 ignore_course_code: str | None = None) -> list[str]:
    """Return the list of `course_code`s in `selected` that clash with `slot_str`."""
    if not slot_str:
        return []
    incoming = intervals_of_slot(slot_str)
    if not incoming:
        return []
    conflicts: list[str] = []
    for c in selected:
        if ignore_course_code and c.get("course_code") == ignore_course_code:
            continue
        if any_overlap(incoming, intervals_of_course(c)):
            conflicts.append(c.get("course_code", "?"))
    return conflicts


def has_internal_clash(theory_slot: str, lab_slot: str) -> bool:
    """True if a course's own theory and lab slots overlap physically."""
    if not theory_slot or not lab_slot:
        return False
    return any_overlap(intervals_of_slot(theory_slot), intervals_of_slot(lab_slot))


def combo_clash(offerings: list[dict]) -> bool:
    """True if any two offerings in a generated combo overlap in time."""
    all_int: list[tuple[str, int, int]] = []
    for off in offerings:
        for iv in intervals_of_course(off):
            for existing in all_int:
                if intervals_overlap(iv, existing):
                    return True
            all_int.append(iv)
    return False


def pretty_slot(slot_str: str) -> str:
    return "+".join(parse_slot_string(slot_str))
