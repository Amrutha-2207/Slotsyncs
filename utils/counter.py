"""Persistent visitor counter for SlotSync.

Primary : hits a free public counter API (abacus.jasoncameron.dev).
Fallback: local JSON file so local dev still works.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import requests
import streamlit as st

_LOCAL_FILE = Path(__file__).resolve().parent.parent / "data" / "visitor_count.json"

# Namespace/key used on abacus.jasoncameron.dev. Change these for a fresh counter.
_NAMESPACE = "slotsync-vitap"
_KEY = "visits"

_BASE = f"https://abacus.jasoncameron.dev"


def _remote_get() -> int | None:
    try:
        r = requests.get(f"{_BASE}/get/{_NAMESPACE}/{_KEY}", timeout=3)
        if r.ok:
            return int(r.json().get("value", 0))
    except Exception:
        return None
    return None


def _remote_hit() -> int | None:
    try:
        r = requests.get(f"{_BASE}/hit/{_NAMESPACE}/{_KEY}", timeout=3)
        if r.ok:
            return int(r.json().get("value", 0))
        # If the counter doesn't exist yet, create it.
        if r.status_code == 404:
            requests.get(f"{_BASE}/create?namespace={_NAMESPACE}&key={_KEY}", timeout=3)
            r2 = requests.get(f"{_BASE}/hit/{_NAMESPACE}/{_KEY}", timeout=3)
            if r2.ok:
                return int(r2.json().get("value", 0))
    except Exception:
        return None
    return None


def _local_read() -> int:
    try:
        if _LOCAL_FILE.exists():
            return int(json.loads(_LOCAL_FILE.read_text()).get("count", 0))
    except Exception:
        pass
    return 0


def _local_write(n: int) -> None:
    try:
        _LOCAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        _LOCAL_FILE.write_text(json.dumps({"count": int(n)}))
    except Exception:
        pass


def register_visit() -> int:
    """Increment the counter for a new session and return the current value."""
    if st.session_state.get("_visit_counted"):
        return int(st.session_state.get("_visit_count", 0))

    remote = _remote_hit()
    if remote is not None:
        count = remote
    else:
        count = _local_read() + 1
        _local_write(count)

    st.session_state["_visit_counted"] = True
    st.session_state["_visit_count"] = count
    return count


def peek_visits() -> int:
    """Return the counter without incrementing it."""
    if "_visit_count" in st.session_state:
        return int(st.session_state["_visit_count"])
    remote = _remote_get()
    if remote is not None:
        return remote
    return _local_read()
