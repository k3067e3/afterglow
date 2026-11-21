"""A new activity started from a copy of one the project already has.

Adding an activity offers two starting points: an empty one, or a copy of an existing
activity. The copy is everything the original says - its devices, inputs, startup and
shutdown, buttons, favourites, power plan and properties - minus what belongs to exactly
one activity:

* its ``id``: activities are referenced by id, so the copy gets a new one when it is
  saved, exactly as an empty new activity does;
* its activity key (``activity_button``, the 650/700's Watch TV / Movie / Music key):
  one key starts one activity, so the copy does not take the original's. The identity
  page then offers the first free key, as it does for any new activity.

Its name becomes "<original> (copy)", numbered when that is taken, so the two are told
apart on the remote even if the user changes nothing else.

Pure standard library on purpose: it is testable without a display.
"""
from __future__ import annotations

import copy

# Fields that identify one activity and must not be shared by two.
_UNIQUE_FIELDS = ("id", "activity_button")

COPY_SUFFIX = " (copy)"


def copy_label(label: str, taken: list[str] | set[str] | None = None) -> str:
    """'Watch TV (copy)', or 'Watch TV (copy 2)', ... when that is taken."""
    base = (label or "").strip() or "Activity"
    names = {(t or "").strip().casefold() for t in taken or ()}
    candidate = f"{base}{COPY_SUFFIX}"
    number = 2
    while candidate.casefold() in names:
        candidate = f"{base} (copy {number})"
        number += 1
    return candidate


def activity_template(source: dict, activities: list[dict] | None = None) -> dict:
    """A new, unsaved activity that starts as a copy of ``source``.

    ``source`` itself is never changed: the result is a deep copy, so editing the copy
    in the wizard - or cancelling it - leaves the original as it was.
    """
    template = copy.deepcopy(source or {})
    for field in _UNIQUE_FIELDS:
        template.pop(field, None)
    template["label"] = copy_label(
        (source or {}).get("label", ""),
        [a.get("label", "") for a in activities or []])
    return template


def template_choices(activities: list[dict] | None) -> list[tuple[str, int]]:
    """(text shown, index into ``activities``) for each activity that can be copied."""
    return [((act.get("label") or "").strip() or f"Activity {i + 1}", i)
            for i, act in enumerate(activities or [])]
