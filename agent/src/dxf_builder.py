import re
from io import BytesIO, StringIO
from typing import TYPE_CHECKING, Any

import ezdxf

if TYPE_CHECKING:
    from agent.src.agent import DesignParameters

_DIMENSION_RE = re.compile(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?")

_VALID_ROOF_TYPES = {"gable", "hip", "mono-pitch", "flat"}

LAYER_FLOOR_PLAN = "Floor_Plan"
LAYER_ROOF_OUTLINE = "Roof_Outline"


def _parse_dimensions(raw: str) -> tuple[float, float]:
    if raw is None:
        raise ValueError("floorPlanDimensions is required")
    m = _DIMENSION_RE.match(raw.strip())
    if not m:
        raise ValueError(f"Cannot parse floorPlanDimensions: {raw!r}")
    width_mm = float(m.group(1)) * 1000
    depth_mm = float(m.group(2)) * 1000
    return width_mm, depth_mm


def _draw_floor_plan(msp, w: float, d: float) -> None:
    msp.add_lwpolyline(
        [(0, 0), (w, 0), (w, d), (0, d)],
        close=True,
        dxfattribs={"layer": LAYER_FLOOR_PLAN},
    )


def _draw_gable(msp, w: float, d: float) -> None:
    if d >= w:
        mid_x = w / 2
        ridge_start = (mid_x, 0)
        ridge_end = (mid_x, d)
        msp.add_line(
            (0, 0), (mid_x, d / 2), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
        msp.add_line(
            (w, 0), (mid_x, d / 2), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
        msp.add_line(
            (0, d), (mid_x, d / 2), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
        msp.add_line(
            (w, d), (mid_x, d / 2), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
    else:
        mid_y = d / 2
        ridge_start = (0, mid_y)
        ridge_end = (w, mid_y)
        msp.add_line(
            (0, 0), (w / 2, mid_y), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
        msp.add_line(
            (0, d), (w / 2, mid_y), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
        msp.add_line(
            (w, 0), (w / 2, mid_y), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
        msp.add_line(
            (w, d), (w / 2, mid_y), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
        )
    msp.add_line(
        ridge_start, ridge_end, dxfattribs={"layer": LAYER_ROOF_OUTLINE}
    )


def _draw_hip(msp, w: float, d: float) -> None:
    if d >= w:
        ridge_len = d - w
        ry_start = (w / 2, (d - ridge_len) / 2)
        ry_end = (w / 2, (d + ridge_len) / 2)
        msp.add_line(ry_start, ry_end, dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_start, (0, 0), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_start, (w, 0), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_end, (0, d), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_end, (w, d), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
    else:
        ridge_len = w - d
        rx_start = ((w - ridge_len) / 2, d / 2)
        rx_end = ((w + ridge_len) / 2, d / 2)
        msp.add_line(rx_start, rx_end, dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_start, (0, 0), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_start, (0, d), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_end, (w, 0), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_end, (w, d), dxfattribs={"layer": LAYER_ROOF_OUTLINE})


def _draw_mono_pitch(msp, w: float, d: float) -> None:
    msp.add_lwpolyline(
        [(0, 0), (w, 0), (w, d), (0, d)],
        close=True,
        dxfattribs={"layer": LAYER_ROOF_OUTLINE},
    )
    msp.add_line(
        (0, d), (w, d), dxfattribs={"layer": LAYER_ROOF_OUTLINE}
    )


def _draw_flat(msp, w: float, d: float) -> None:
    msp.add_lwpolyline(
        [(0, 0), (w, 0), (w, d), (0, d)],
        close=True,
        dxfattribs={"layer": LAYER_ROOF_OUTLINE},
    )


_ROOF_DRAWERS = {
    "gable": _draw_gable,
    "hip": _draw_hip,
    "mono-pitch": _draw_mono_pitch,
    "flat": _draw_flat,
}


def build_dxf(params: Any) -> bytes:
    if params.roofType is None:
        raise ValueError("roofType is required")
    roof_key = params.roofType.strip().lower()
    if roof_key not in _VALID_ROOF_TYPES:
        raise ValueError(f"Unsupported roofType: {params.roofType!r}")

    w, d = _parse_dimensions(params.floorPlanDimensions)

    doc = ezdxf.new("R2000")
    doc.layers.add(LAYER_FLOOR_PLAN)
    doc.layers.add(LAYER_ROOF_OUTLINE)

    msp = doc.modelspace()
    _draw_floor_plan(msp, w, d)
    _ROOF_DRAWERS[roof_key](msp, w, d)

    sbuf = StringIO()
    doc.write(sbuf)
    return sbuf.getvalue().encode("utf-8")
