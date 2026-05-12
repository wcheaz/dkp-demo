import copy

ALL_PARAM_KEYS = [
    "buildingType", "floorPlanDimensions", "roofType", "roofPitch",
    "atticUsage", "eavesShape", "wallConstruction", "location", "overhang",
]


def _reset_design(state, *, design_ids=None, remove_designs=False,
                  clear_parameters=None, clear_all_parameters=False,
                  clear_session_parameters=None):
    current_designs = state.get("designs", [])
    valid_ids = [d["id"] for d in current_designs]

    if clear_parameters:
        invalid = [k for k in clear_parameters if k not in ALL_PARAM_KEYS]
        if invalid:
            return (f"Error: invalid parameter keys: {', '.join(invalid)}. "
                    f"Valid keys: {', '.join(ALL_PARAM_KEYS)}."), state

    if clear_session_parameters:
        invalid = [k for k in clear_session_parameters if k not in ALL_PARAM_KEYS]
        if invalid:
            return (f"Error: invalid session parameter keys: {', '.join(invalid)}. "
                    f"Valid keys: {', '.join(ALL_PARAM_KEYS)}."), state

    target_ids = design_ids
    if target_ids and len(target_ids) > 0:
        not_found = [i for i in target_ids if i not in valid_ids]
        if not_found:
            return (f"Error: design IDs not found: {', '.join(str(i) for i in not_found)}. "
                    f"Valid IDs: [{', '.join(str(i) for i in valid_ids)}]."), state
    else:
        target_ids = valid_ids

    new_state = copy.deepcopy(state)
    updated_designs = new_state.get("designs", [])
    summary = ""

    if remove_designs:
        updated_designs = [d for d in current_designs if d["id"] not in target_ids]
        s = "s" if len(target_ids) != 1 else ""
        summary = f"Removed {len(target_ids)} design entry{s} entirely."
    else:
        if clear_all_parameters or clear_parameters:
            for d in updated_designs:
                if d["id"] not in target_ids:
                    continue
                existing = d.get("parameters", {}) or {}
                keys_to_clear = list(ALL_PARAM_KEYS) if clear_all_parameters else clear_parameters
                for key in keys_to_clear:
                    existing[key] = "---"
                d["parameters"] = existing

        cleared_keys = "all parameters" if clear_all_parameters else (
            ", ".join(clear_parameters) if clear_parameters else "")
        s = "s" if len(target_ids) != 1 else ""
        ids_str = ", ".join(str(i) for i in target_ids)
        ids_label = f"ID{s}: {ids_str}"
        summary = f"Reset {len(target_ids)} design entry{s} ({ids_label}). Cleared parameters: {cleared_keys}."

        preserved_parts = []
        for tid in target_ids:
            entry = next((d for d in current_designs if d["id"] == tid), None)
            if not entry or not entry.get("parameters"):
                continue
            preserved = [f"{k}={v}" for k, v in entry["parameters"].items()
                         if v is not None and v != "" and v != "---"
                         and not (clear_all_parameters or (clear_parameters and k in clear_parameters))]
            if preserved:
                preserved_parts.append(", ".join(preserved))
        if preserved_parts:
            summary += f" Preserved parameters: {'; '.join(preserved_parts)}."

    new_state["designs"] = updated_designs
    session_summary = ""

    if clear_session_parameters:
        current_params = new_state.get("parameters") or {}
        new_params = dict(current_params)
        for key in clear_session_parameters:
            new_params.pop(key, None)
        new_state["parameters"] = new_params

        remaining = [f"{k}={v}" for k, v in new_params.items() if v is not None and v != ""]
        session_summary = f" Cleared session parameters: {', '.join(clear_session_parameters)}."
        if remaining:
            session_summary += f" Remaining session parameters: {', '.join(remaining)}."
        else:
            session_summary += " No session parameters remaining."

    return (summary + session_summary).strip(), new_state


def _make_entry(entry_id, params=None, price=None, status="complete", image_url="/design.svg", prompt="test"):
    entry = {"id": entry_id, "imageUrl": image_url, "promptText": prompt, "status": status}
    if params:
        entry["parameters"] = params
    if price:
        entry["price"] = price
    return entry


def _make_state(entries, parameters=None):
    state = {"designs": [copy.deepcopy(e) for e in entries]}
    if parameters:
        state["parameters"] = copy.deepcopy(parameters)
    return state


class TestPartialReset:
    def test_clear_specific_fields(self):
        entries = [_make_entry(1, params={"buildingType": "House", "roofType": "Gable", "location": "Bratislava"})]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1], clear_parameters=["roofType"])
        assert new_state["designs"][0]["parameters"]["roofType"] == "---"
        assert new_state["designs"][0]["parameters"]["buildingType"] == "House"
        assert new_state["designs"][0]["parameters"]["location"] == "Bratislava"

    def test_preserved_fields_untouched(self):
        entries = [_make_entry(1, params={"buildingType": "House", "roofPitch": 30, "location": "Bratislava"})]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1], clear_parameters=["roofPitch"])
        assert new_state["designs"][0]["parameters"]["buildingType"] == "House"
        assert new_state["designs"][0]["parameters"]["location"] == "Bratislava"
        assert new_state["designs"][0]["parameters"]["roofPitch"] == "---"

    def test_prompt_text_preserved(self):
        entries = [_make_entry(1, params={"buildingType": "House"}, prompt="My design")]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1], clear_parameters=["buildingType"])
        assert new_state["designs"][0]["promptText"] == "My design"


class TestNoOpReset:
    def test_no_clear_parameters_no_change(self):
        entries = [_make_entry(1, params={"buildingType": "House", "roofType": "Gable"})]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1])
        assert new_state["designs"][0]["parameters"]["buildingType"] == "House"
        assert new_state["designs"][0]["parameters"]["roofType"] == "Gable"
        assert len(new_state["designs"]) == 1


class TestFullScrap:
    def test_remove_single_entry(self):
        entries = [_make_entry(1), _make_entry(2)]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1], remove_designs=True)
        assert len(new_state["designs"]) == 1
        assert new_state["designs"][0]["id"] == 2
        assert "Removed" in result

    def test_remove_all_entries(self):
        entries = [_make_entry(1), _make_entry(2)]
        state = _make_state(entries)
        result, new_state = _reset_design(state, remove_designs=True)
        assert len(new_state["designs"]) == 0

    def test_full_scrap_ignores_clear_parameters(self):
        entries = [_make_entry(1, params={"buildingType": "House"})]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1], remove_designs=True,
                                          clear_parameters=["buildingType"])
        assert len(new_state["designs"]) == 0
        assert "Removed" in result


class TestClearAllParameters:
    def test_clear_all_sets_every_field(self):
        params = {k: f"value_{k}" for k in ALL_PARAM_KEYS}
        entries = [_make_entry(1, params=params)]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1], clear_all_parameters=True)
        for key in ALL_PARAM_KEYS:
            assert new_state["designs"][0]["parameters"][key] == "---", f"{key} not cleared"

    def test_clear_all_takes_precedence_over_clear_parameters(self):
        params = {"buildingType": "House", "roofType": "Gable"}
        entries = [_make_entry(1, params=params)]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1],
                                          clear_parameters=["roofType"],
                                          clear_all_parameters=True)
        assert new_state["designs"][0]["parameters"]["buildingType"] == "---"
        assert new_state["designs"][0]["parameters"]["roofType"] == "---"


class TestSessionParameterClearing:
    def test_clear_session_params(self):
        state = _make_state([_make_entry(1)], parameters={"buildingType": "House", "location": "Bratislava"})
        result, new_state = _reset_design(state, clear_session_parameters=["buildingType"])
        assert "buildingType" not in new_state["parameters"]
        assert new_state["parameters"]["location"] == "Bratislava"

    def test_session_clear_independent_of_entries(self):
        state = _make_state([_make_entry(1, params={"roofType": "Gable"})],
                            parameters={"roofType": "Hip", "location": "Kosice"})
        result, new_state = _reset_design(state, clear_session_parameters=["roofType"])
        assert new_state["designs"][0]["parameters"]["roofType"] == "Gable"
        assert "roofType" not in new_state["parameters"]
        assert new_state["parameters"]["location"] == "Kosice"


class TestCompoundResetAndSessionClear:
    def test_entry_reset_plus_session_clear(self):
        entries = [_make_entry(1, params={"buildingType": "House", "roofPitch": 30})]
        state = _make_state(entries, parameters={"buildingType": "House", "roofPitch": 30})
        result, new_state = _reset_design(state, design_ids=[1],
                                          clear_parameters=["roofPitch"],
                                          clear_session_parameters=["roofPitch"])
        assert new_state["designs"][0]["parameters"]["roofPitch"] == "---"
        assert new_state["designs"][0]["parameters"]["buildingType"] == "House"
        assert "roofPitch" not in new_state["parameters"]
        assert new_state["parameters"]["buildingType"] == "House"


class TestResetAllDesigns:
    def test_omitted_design_ids_targets_all(self):
        entries = [_make_entry(1, params={"buildingType": "A"}), _make_entry(2, params={"buildingType": "B"})]
        state = _make_state(entries)
        result, new_state = _reset_design(state, clear_parameters=["buildingType"])
        assert new_state["designs"][0]["parameters"]["buildingType"] == "---"
        assert new_state["designs"][1]["parameters"]["buildingType"] == "---"

    def test_empty_design_ids_targets_all(self):
        entries = [_make_entry(1, params={"location": "X"})]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[], clear_parameters=["location"])
        assert new_state["designs"][0]["parameters"]["location"] == "---"


class TestInvalidDesignId:
    def test_invalid_id_returns_error(self):
        entries = [_make_entry(1), _make_entry(2)]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[99])
        assert result.startswith("Error: design IDs not found")
        assert new_state["designs"] == state["designs"]

    def test_error_lists_valid_ids(self):
        entries = [_make_entry(1), _make_entry(3)]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[5])
        assert "1, 3" in result
        assert len(new_state["designs"]) == 2


class TestInvalidParameterKey:
    def test_invalid_clear_parameters_key(self):
        entries = [_make_entry(1)]
        state = _make_state(entries)
        result, new_state = _reset_design(state, design_ids=[1], clear_parameters=["invalidKey"])
        assert result.startswith("Error: invalid parameter keys")
        assert new_state["designs"] == state["designs"]

    def test_invalid_session_parameter_key(self):
        state = _make_state([_make_entry(1)], parameters={"buildingType": "House"})
        result, new_state = _reset_design(state, clear_session_parameters=["notAParam"])
        assert result.startswith("Error: invalid session parameter keys")
        assert new_state["parameters"]["buildingType"] == "House"

    def test_no_state_mutation_on_error(self):
        params = {"buildingType": "House", "roofType": "Gable"}
        entries = [_make_entry(1, params=params)]
        state = _make_state(entries, parameters={"location": "Bratislava"})
        original_state = copy.deepcopy(state)
        _reset_design(state, design_ids=[1], clear_parameters=["badKey"])
        assert state == original_state


class TestReturnSummaryFormat:
    def test_partial_reset_summary(self):
        entries = [_make_entry(1, params={"buildingType": "House", "roofType": "Gable"})]
        state = _make_state(entries)
        result, _ = _reset_design(state, design_ids=[1], clear_parameters=["roofType"])
        assert "Reset 1 design entry" in result
        assert "roofType" in result

    def test_full_scrap_summary(self):
        entries = [_make_entry(1)]
        state = _make_state(entries)
        result, _ = _reset_design(state, design_ids=[1], remove_designs=True)
        assert "Removed 1 design entry entirely." in result

    def test_session_clear_summary(self):
        state = _make_state([_make_entry(1)], parameters={"buildingType": "House"})
        result, _ = _reset_design(state, clear_session_parameters=["buildingType"])
        assert "Cleared session parameters: buildingType" in result
        assert "No session parameters remaining" in result
