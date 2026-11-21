"""A new activity can start as a copy of an existing one (see `activity_copy`)."""
from afterglow.activity_copy import activity_template, copy_label, template_choices


def _activity(**fields):
    return {"id": "1001", "label": "Watch TV", "type": "VirtualTelevisionN",
            "display": "1", "control": "2", "roles": {"Sub": "3"},
            "image_buttons": [{"label": "ORF1"}], "hard_macros": {"Red": [["command", "2", "Red"]]},
            "enter": [["input", "1", "HDMI1"]], "leave": [], "properties": {"x": 1},
            "power_on_devices": ["1", "2", "3"], "activity_button": "TV", **fields}


def test_the_copy_keeps_everything_but_what_belongs_to_one_activity():
    original = _activity()
    copied = activity_template(original, [original])
    assert "id" not in copied and "activity_button" not in copied
    assert copied["label"] == "Watch TV (copy)"
    for key in ("type", "display", "control", "roles", "image_buttons", "hard_macros",
                "enter", "leave", "properties", "power_on_devices"):
        assert copied[key] == original[key]


def test_the_original_is_never_changed():
    original = _activity()
    copied = activity_template(original, [original])
    copied["roles"]["Sub"] = "9"
    copied["enter"].append(["wait", 500])
    assert original == _activity()


def test_a_taken_copy_name_is_numbered():
    taken = ["Watch TV", "Watch TV (copy)", "watch tv (copy 2)"]
    assert copy_label("Watch TV", taken) == "Watch TV (copy 3)"
    assert copy_label("", []) == "Activity (copy)"


def test_choices_list_every_activity_by_name():
    acts = [_activity(), _activity(label="  ")]
    assert template_choices(acts) == [("Watch TV", 0), ("Activity 2", 1)]
    assert template_choices(None) == []


def test_the_start_dialog_and_wizard_take_a_template(qapp_or_skip):
    from afterglow.gui.activity_wizard import ActivityStartDialog, ActivityWizard
    original = _activity()
    dialog = ActivityStartDialog([original])
    assert dialog.template_index() is None
    dialog.copy_radio.setChecked(True)
    assert dialog.template_index() == 0
    devices = [{"id": d, "label": d, "type": "Television", "commands": []}
               for d in ("1", "2", "3")]
    wizard = ActivityWizard(devices, existing=activity_template(original, [original]),
                            taken_ids=["1001"], activities=[original], title="Add Activity")
    spec = wizard._collect()
    assert spec["id"] not in ("", "1001")
    assert spec["label"] == "Watch TV (copy)"
    assert spec["enter"] == original["enter"]
