"""Tests for the calibrated Pamir pricing formula in ``generate_quote``.

These tests lock the calibrated coefficients (C24 timber @ 6200 CZK/m3, ABR90
angle brackets @ 370 CZK, gusset/assembly/hanger costs) documented in
``openspec/changes/pamir-ifc-pricing-bridge``. They guard against accidental
regression of the deterministic quote formula.
"""

import asyncio
import os
import sys
from pathlib import Path

# Provide dummy API credentials so the module-level DeepSeek model can be
# constructed in test environments that do not carry a real .env.
os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-tests")
os.environ.setdefault("DEEPSEEK_API_KEY", "dummy-key-for-tests")

_AGENT_DIR = str(Path(__file__).resolve().parent.parent / "agent")
if _AGENT_DIR not in sys.path:
    sys.path.insert(0, _AGENT_DIR)

import pytest  # noqa: E402

from src.agent import generate_quote  # noqa: E402


def _quote(dimensions: str, roof_type: str) -> str:
    """Run the async ``generate_quote`` tool synchronously."""
    return asyncio.run(
        generate_quote(None, dimensions, roof_type, 35, "Family house")
    )


def _eur_from_output(output: str) -> int:
    """Extract the integer EUR value from the formatted quote string."""
    prefix = "Estimated price: \u20ac"
    suffix = " (excl. VAT)"
    assert output.startswith(prefix), output
    assert output.endswith(suffix), output
    return int(output[len(prefix) : -len(suffix)])


def _calibrated_component_sum(floor_area: float) -> float:
    """Factor-independent CZK sum of the calibrated component costs.

    Replicates the published formula so the tests can verify both the exact
    intermediate structural values and the roof-type factor relationship at
    the pre-EUR-rounding (CZK) level.
    """
    total_joints = round(floor_area * 1.32)
    timber_volume = floor_area * 0.254
    total_trusses = round(floor_area * 0.147)
    support_nodes = total_trusses * 2
    bracket_count = round(support_nodes * 1.6)
    return (
        total_joints * 50
        + timber_volume * 6200
        + (total_trusses / 20) * 18000
        + total_trusses * 120
        + bracket_count * 370
    )


class TestCalibratedQuote:
    def test_gable_10x15_golden_value(self):
        # floor_area=150 -> joints=198, volume=38.1, trusses=22, brackets=70
        # subtotal=294460 CZK, total_eur=round(294460/25)=11778
        assert _quote("10x15m", "Gable") == "Estimated price: \u20ac11778 (excl. VAT)"

    def test_structural_values_for_150m2(self):
        # Spec scenario: joints ~198, volume ~38.1, trusses ~22, bracketCount ~70
        floor_area = 150.0
        assert round(floor_area * 1.32) == 198
        assert floor_area * 0.254 == 38.1
        assert round(floor_area * 0.147) == 22
        assert round((22 * 2) * 1.6) == 70

    def test_deterministic_across_repeated_calls(self):
        first = _quote("10x15m", "Hip")
        second = _quote("10x15m", "Hip")
        assert first == second

    def test_hip_exactly_1p3_times_gable_before_rounding(self):
        component_sum = _calibrated_component_sum(150.0)
        gable_czk = component_sum * 1.0
        hip_czk = component_sum * 1.3
        # Exact 1.3x relationship holds at the CZK level (before EUR rounding)
        assert hip_czk == pytest.approx(gable_czk * 1.3, rel=1e-9)
        assert round(gable_czk / 25) == _eur_from_output(_quote("10x15m", "Gable"))
        assert round(hip_czk / 25) == _eur_from_output(_quote("10x15m", "Hip"))

    @pytest.mark.parametrize(
        "roof_type,factor",
        [
            ("Gable", 1.0),
            ("Hip", 1.3),
            ("Mono-pitch", 0.9),
            ("Flat", 0.8),
        ],
    )
    def test_roof_type_factor_applied(self, roof_type, factor):
        component_sum = _calibrated_component_sum(150.0)
        expected_eur = round(component_sum * factor / 25)
        assert _eur_from_output(_quote("10x15m", roof_type)) == expected_eur

    def test_calibrated_coefficients_differ_from_legacy(self):
        # Legacy (pre-calibration) Gable 10x15m returned 7923. Calibrated
        # formula must return a strictly higher price (6200 vs 4500 timber,
        # added metalwork, etc.).
        assert _eur_from_output(_quote("10x15m", "Gable")) > 7923

    def test_unparseable_dimensions_returns_error_string(self):
        result = _quote("big house", "Gable")
        assert isinstance(result, str)
        assert result.startswith("Error:")
        assert "10x15m" in result

    def test_metalwork_bracket_formula(self):
        # bracket_count is derived from support nodes (trusses*2 * 1.6)
        breakdown = _calibrated_component_sum(150.0)
        # Recompute metalwork contribution explicitly to assert it is included.
        total_joints = round(150 * 1.32)
        total_trusses = round(150 * 0.147)
        bracket_count = round((total_trusses * 2) * 1.6)
        legacy_sum_without_metalwork = (
            total_joints * 50
            + (150 * 0.254) * 6200
            + (total_trusses / 20) * 18000
            + total_trusses * 120
        )
        assert breakdown == legacy_sum_without_metalwork + bracket_count * 370
        assert bracket_count * 370 == 25900
