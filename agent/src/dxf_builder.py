import math
import re
from datetime import datetime, timezone
from io import BytesIO, StringIO
from typing import TYPE_CHECKING, Any, Optional

import ezdxf

if TYPE_CHECKING:
    from agent.src.agent import DesignParameters

_DIMENSION_RE = re.compile(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?")
_OVERHANG_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(mm|m)?\s*$", re.IGNORECASE)

_VALID_ROOF_TYPES = {"gable", "hip", "mono-pitch", "flat"}

WALL_HEIGHT = 2700.0

_ISO_COS30 = math.cos(math.pi / 6)
_ISO_SIN30 = 0.5


def _to_iso(x: float, y: float, z: float) -> tuple[float, float]:
    return ((x - y) * _ISO_COS30, (x + y) * _ISO_SIN30 + z)

LAYER_FLOOR_PLAN = "Floor_Plan"
LAYER_WALL_CENTERLINES = "Wall_Centerlines"
LAYER_ROOF_OUTLINE = "Roof_Outline"
LAYER_TRUSSES = "Trusses"
LAYER_DIMENSIONS = "Dimensions"
LAYER_LABELS = "Labels"
LAYER_LUMBER_SPECS = "Lumber_Specs"
LAYER_TITLE_BLOCK = "Title_Block"


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
    corners = [(0, 0), (w, 0), (w, d), (0, d)]
    for z in (0, WALL_HEIGHT):
        for i in range(4):
            sx, sy = corners[i]
            ex, ey = corners[(i + 1) % 4]
            msp.add_line(
                _to_iso(sx, sy, z), _to_iso(ex, ey, z),
                dxfattribs={"layer": LAYER_FLOOR_PLAN},
            )
    for cx, cy in corners:
        msp.add_line(
            _to_iso(cx, cy, 0), _to_iso(cx, cy, WALL_HEIGHT),
            dxfattribs={"layer": LAYER_FLOOR_PLAN},
        )


def _draw_wall_centerlines(msp, w: float, d: float) -> None:
    corners_3d = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0)]
    projected = [_to_iso(x, y, z) for x, y, z in corners_3d]
    msp.add_lwpolyline(
        projected,
        close=True,
        dxfattribs={"layer": LAYER_WALL_CENTERLINES},
    )


def _draw_gable(msp, w: float, d: float, pitch_deg: float = 30.0) -> None:
    ridge_h = (min(w, d) / 2) * math.tan(pitch_deg * math.pi / 180)
    z_eave = WALL_HEIGHT
    z_ridge = WALL_HEIGHT + ridge_h
    if d >= w:
        mid_x = w / 2
        ridge_start = (mid_x, 0, z_ridge)
        ridge_end = (mid_x, d, z_ridge)
        msp.add_line(
            (0, 0, z_eave), (mid_x, d / 2, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
        msp.add_line(
            (w, 0, z_eave), (mid_x, d / 2, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
        msp.add_line(
            (0, d, z_eave), (mid_x, d / 2, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
        msp.add_line(
            (w, d, z_eave), (mid_x, d / 2, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
    else:
        mid_y = d / 2
        ridge_start = (0, mid_y, z_ridge)
        ridge_end = (w, mid_y, z_ridge)
        msp.add_line(
            (0, 0, z_eave), (w / 2, mid_y, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
        msp.add_line(
            (0, d, z_eave), (w / 2, mid_y, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
        msp.add_line(
            (w, 0, z_eave), (w / 2, mid_y, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
        msp.add_line(
            (w, d, z_eave), (w / 2, mid_y, z_ridge),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )
    msp.add_line(
        ridge_start, ridge_end, dxfattribs={"layer": LAYER_ROOF_OUTLINE}
    )


def _draw_hip(msp, w: float, d: float, pitch_deg: float = 30.0) -> None:
    ridge_h = (min(w, d) / 2) * math.tan(pitch_deg * math.pi / 180)
    z_eave = WALL_HEIGHT
    z_ridge = WALL_HEIGHT + ridge_h
    if d >= w:
        ridge_len = d - w
        ry_start = (w / 2, (d - ridge_len) / 2, z_ridge)
        ry_end = (w / 2, (d + ridge_len) / 2, z_ridge)
        msp.add_line(ry_start, ry_end, dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_start, (0, 0, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_start, (w, 0, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_end, (0, d, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(ry_end, (w, d, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
    else:
        ridge_len = w - d
        rx_start = ((w - ridge_len) / 2, d / 2, z_ridge)
        rx_end = ((w + ridge_len) / 2, d / 2, z_ridge)
        msp.add_line(rx_start, rx_end, dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_start, (0, 0, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_start, (0, d, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_end, (w, 0, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
        msp.add_line(rx_end, (w, d, z_eave), dxfattribs={"layer": LAYER_ROOF_OUTLINE})


def _draw_mono_pitch(msp, w: float, d: float, pitch_deg: float = 10.0) -> None:
    ridge_h = w * math.tan(pitch_deg * math.pi / 180)
    z_low = WALL_HEIGHT
    z_high = WALL_HEIGHT + ridge_h
    msp.add_line((0, 0, z_low), (w, 0, z_high), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
    msp.add_line((w, 0, z_high), (w, d, z_high), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
    msp.add_line((w, d, z_high), (0, d, z_low), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
    msp.add_line((0, d, z_low), (0, 0, z_low), dxfattribs={"layer": LAYER_ROOF_OUTLINE})
    msp.add_line((0, 0, z_low), (w, 0, z_high), dxfattribs={"layer": LAYER_ROOF_OUTLINE})


def _draw_flat(msp, w: float, d: float, pitch_deg: float = 0.0) -> None:
    corners = [(0, 0), (w, 0), (w, d), (0, d)]
    for i in range(4):
        sx, sy = corners[i]
        ex, ey = corners[(i + 1) % 4]
        msp.add_line(
            (sx, sy, WALL_HEIGHT), (ex, ey, WALL_HEIGHT),
            dxfattribs={"layer": LAYER_ROOF_OUTLINE},
        )


def _compute_truss_count(width_m: float, depth_m: float) -> int:
    return max(2, round(width_m * depth_m * 0.147))


def _draw_trusses(msp, w: float, d: float, roof_key: str, roof_pitch) -> None:
    count = _compute_truss_count(w / 1000, d / 1000)

    if roof_pitch is None or roof_pitch == 0:
        if roof_key in ("gable", "hip"):
            pitch_deg = 30.0
        elif roof_key == "mono-pitch":
            pitch_deg = 10.0
        else:
            pitch_deg = 0.0
    else:
        pitch_deg = float(roof_pitch)

    shorter = min(w, d)
    inset = shorter * 0.05

    if count == 1:
        positions = [d / 2]
    else:
        span = d - 2 * inset
        step = span / (count - 1)
        positions = [inset + i * step for i in range(count)]

    if roof_key in ("gable", "hip"):
        ridge_h = (w / 2) * math.tan(pitch_deg * math.pi / 180)
    elif roof_key == "mono-pitch":
        ridge_h = w * math.tan(pitch_deg * math.pi / 180)
    else:
        ridge_h = 0.0

    z_eave = WALL_HEIGHT
    z_ridge = WALL_HEIGHT + ridge_h

    for y_pos in positions:
        if roof_key in ("gable", "hip"):
            msp.add_line(
                (0, y_pos, z_eave), (w / 2, y_pos, z_ridge),
                dxfattribs={"layer": LAYER_TRUSSES},
            )
            msp.add_line(
                (w, y_pos, z_eave), (w / 2, y_pos, z_ridge),
                dxfattribs={"layer": LAYER_TRUSSES},
            )
            msp.add_line(
                (0, y_pos, z_eave), (w, y_pos, z_eave),
                dxfattribs={"layer": LAYER_TRUSSES},
            )
        elif roof_key == "mono-pitch":
            msp.add_line(
                (0, y_pos, z_eave), (w, y_pos, z_ridge),
                dxfattribs={"layer": LAYER_TRUSSES},
            )
            msp.add_line(
                (0, y_pos, z_eave), (w, y_pos, z_eave),
                dxfattribs={"layer": LAYER_TRUSSES},
            )
            msp.add_line(
                (w, y_pos, z_eave), (w, y_pos, z_ridge),
                dxfattribs={"layer": LAYER_TRUSSES},
            )
        else:
            msp.add_line(
                (0, y_pos, z_eave), (w, y_pos, z_eave),
                dxfattribs={"layer": LAYER_TRUSSES},
            )


def _parse_overhang(raw: Optional[str]) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    m = _OVERHANG_RE.match(str(raw).strip())
    if not m:
        return None
    value = float(m.group(1))
    unit = (m.group(2) or "").lower()
    if unit == "m":
        return value * 1000
    return value


def _draw_dimensions(
    msp, w, d, w_m, d_m, roof_key, ridge_height_mm, overhang_mm
) -> None:
    text_h = 250

    w_dim_offset = d * 0.1
    dim = msp.add_linear_dim(
        base=(0, -w_dim_offset),
        p1=(0, 0),
        p2=(w, 0),
        angle=0,
        dxfattribs={"layer": LAYER_DIMENSIONS},
    )
    dim.render()

    d_dim_offset = w * 0.1
    dim = msp.add_linear_dim(
        base=(-d_dim_offset, 0),
        p1=(0, 0),
        p2=(0, d),
        angle=90,
        dxfattribs={"layer": LAYER_DIMENSIONS},
    )
    dim.render()

    if roof_key in ("gable", "hip") and ridge_height_mm and ridge_height_mm > 0:
        shorter = min(w, d)
        first_truss_y = shorter * 0.05
        rh_offset = w * 0.1
        dim = msp.add_linear_dim(
            base=(w + rh_offset, 0),
            p1=(w, first_truss_y),
            p2=(w, first_truss_y + ridge_height_mm),
            angle=90,
            dxfattribs={"layer": LAYER_DIMENSIONS},
        )
        dim.render()

    if overhang_mm is not None and overhang_mm > 0:
        dim = msp.add_linear_dim(
            base=(w, d + 1500),
            p1=(w, d),
            p2=(w + overhang_mm, d),
            angle=0,
            dxfattribs={"layer": LAYER_DIMENSIONS},
        )
        dim.render()

    label_x = -d_dim_offset
    label_y = -w_dim_offset - 1500

    msp.add_text(
        f"Width: {w_m:g}m",
        dxfattribs={"layer": LAYER_LABELS, "height": text_h},
    ).dxf.insert = (label_x, label_y)

    msp.add_text(
        f"Depth: {d_m:g}m",
        dxfattribs={"layer": LAYER_LABELS, "height": text_h},
    ).dxf.insert = (label_x, label_y - 500)

    if roof_key in ("gable", "hip") and ridge_height_mm and ridge_height_mm > 0:
        ridge_m = round(ridge_height_mm / 1000, 2)
        msp.add_text(
            f"Ridge Height: {ridge_m:g}m",
            dxfattribs={"layer": LAYER_LABELS, "height": text_h},
        ).dxf.insert = (label_x, label_y - 1000)


def _draw_lumber_specs(msp, w: float, d: float) -> None:
    specs = [
        "Lumber Grade: C24",
        "Member Thickness: 45 mm",
        "Member Width: 120 mm",
    ]
    text_h = 250
    start_x = -w * 0.1
    start_y = -d * 0.1 - 3000
    for i, spec in enumerate(specs):
        msp.add_mtext(
            spec,
            dxfattribs={"layer": LAYER_LUMBER_SPECS, "char_height": text_h},
        ).dxf.insert = (start_x, start_y - i * 500)


def _draw_title_block(msp, w: float, d: float, params) -> None:
    tb_w = 40000.0
    tb_h = 15000.0
    tb_x = w - tb_w
    tb_y = -tb_h

    msp.add_line((tb_x, tb_y), (tb_x + tb_w, tb_y),
                 dxfattribs={"layer": LAYER_TITLE_BLOCK})
    msp.add_line((tb_x + tb_w, tb_y), (tb_x + tb_w, tb_y + tb_h),
                 dxfattribs={"layer": LAYER_TITLE_BLOCK})
    msp.add_line((tb_x + tb_w, tb_y + tb_h), (tb_x, tb_y + tb_h),
                 dxfattribs={"layer": LAYER_TITLE_BLOCK})
    msp.add_line((tb_x, tb_y + tb_h), (tb_x, tb_y),
                 dxfattribs={"layer": LAYER_TITLE_BLOCK})

    building_type = getattr(params, "buildingType", None) or "Building"
    location = getattr(params, "location", None) or "Location not specified"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    w_m = w / 1000
    d_m = d / 1000
    roof_type = getattr(params, "roofType", None) or "Unknown"

    text_h = 800
    col_x = tb_x + 1500
    start_y = tb_y + tb_h - 2000
    line_spacing = 2500

    entries = [
        f"Type: {building_type}",
        f"Location: {location}",
        f"Date: {date_str}",
        f"Plan: {w_m:g}x{d_m:g}m",
        f"Roof: {roof_type}",
    ]

    for i, text in enumerate(entries):
        msp.add_mtext(
            text,
            dxfattribs={"layer": LAYER_TITLE_BLOCK, "char_height": text_h},
        ).dxf.insert = (col_x, start_y - i * line_spacing)


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

    doc = ezdxf.new("R2004")
    doc.layers.add(LAYER_FLOOR_PLAN)
    doc.layers.get(LAYER_FLOOR_PLAN).rgb = (128, 128, 128)
    doc.layers.get(LAYER_FLOOR_PLAN).color = 9
    doc.layers.add(LAYER_WALL_CENTERLINES)
    doc.layers.get(LAYER_WALL_CENTERLINES).rgb = (34, 139, 34)
    doc.layers.get(LAYER_WALL_CENTERLINES).color = 3
    doc.layers.add(LAYER_ROOF_OUTLINE)
    doc.layers.get(LAYER_ROOF_OUTLINE).rgb = (70, 130, 180)
    doc.layers.get(LAYER_ROOF_OUTLINE).color = 4

    msp = doc.modelspace()
    _draw_floor_plan(msp, w, d)
    _draw_wall_centerlines(msp, w, d)

    pitch_val = float(params.roofPitch) if hasattr(params, "roofPitch") and params.roofPitch is not None else None
    if pitch_val is None or pitch_val == 0:
        if roof_key in ("gable", "hip"):
            pitch_val = 30.0
        elif roof_key == "mono-pitch":
            pitch_val = 10.0
        else:
            pitch_val = 0.0

    _ROOF_DRAWERS[roof_key](msp, w, d, pitch_val)

    doc.layers.add(LAYER_TRUSSES)
    doc.layers.get(LAYER_TRUSSES).rgb = (139, 90, 43)
    doc.layers.get(LAYER_TRUSSES).color = 34
    _draw_trusses(msp, w, d, roof_key, params.roofPitch if hasattr(params, "roofPitch") else None)

    w_m = w / 1000
    d_m = d / 1000
    if roof_key in ("gable", "hip"):
        ridge_height_mm = (w / 2) * math.tan(pitch_val * math.pi / 180)
    elif roof_key == "mono-pitch":
        ridge_height_mm = w * math.tan(pitch_val * math.pi / 180)
    else:
        ridge_height_mm = 0.0

    overhang_mm = _parse_overhang(
        getattr(params, "overhang", None)
    )

    doc.layers.add(LAYER_DIMENSIONS)
    doc.layers.get(LAYER_DIMENSIONS).rgb = (0, 0, 255)
    doc.layers.get(LAYER_DIMENSIONS).color = 5
    _draw_dimensions(msp, w, d, w_m, d_m, roof_key, ridge_height_mm, overhang_mm)

    doc.layers.add(LAYER_LABELS)
    doc.layers.get(LAYER_LABELS).rgb = (218, 165, 32)
    doc.layers.get(LAYER_LABELS).color = 2

    doc.layers.add(LAYER_LUMBER_SPECS)
    doc.layers.get(LAYER_LUMBER_SPECS).rgb = (128, 0, 128)
    doc.layers.get(LAYER_LUMBER_SPECS).color = 6
    _draw_lumber_specs(msp, w, d)

    # Title block disabled — generated DXFs are for customer preview, not final plots.
    # doc.layers.add(LAYER_TITLE_BLOCK)
    # _draw_title_block(msp, w, d, params)

    sbuf = StringIO()
    doc.write(sbuf)
    return sbuf.getvalue().encode("utf-8")
