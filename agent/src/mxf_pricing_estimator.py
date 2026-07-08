import xml.etree.ElementTree as ET
import os

def estimate_mxf_materials_and_price(
    mxf_path: str,
    timber_rate_eur_m3: float = 4866.76,
    plate_markup: float = 1.0,
    fabrication_markup: float = 0.2878,
    setup_cost_per_type: float = 156.41,
    exchange_rate: float = 25.9667,
    substitute_real_prices: bool = False
) -> dict:
    """Parses any post-processed MXF file and calculates the material volumes, raw costs, and final estimated price."""
    if not os.path.exists(mxf_path):
        raise FileNotFoundError(f"MXF file not found at {mxf_path}")
        
    tree = ET.parse(mxf_path)
    root = tree.getroot()
    
    # Slovak priced M20/T150 catalog overrides for unpriced GNA20/T150 placeholder plates
    substitute_map = {
        ("0812", "GNA20"): ("0813", "M20", 688.21, 0.0757682),
        ("0912", "T150"): ("1014", "T150", 1032.314, 0.1729512),
        ("1010", "GNA20"): ("1010", "M20", 688.21, 0.0816714),
        ("1010", "T150"): ("1014", "T150", 1032.314, 0.1729512),
        ("1014", "GNA20"): ("1015", "M20", 688.21, 0.1217064),
        ("1014", "T150"): ("1014", "T150", 1032.314, 0.1729512),
        ("1031", "GNA20"): ("1025", "M20", 688.21, 0.2033778)
    }
    
    # 1. Load PlateTypeList costs (converted to EUR)
    pt_map = {}
    pt_list = root.find("PlateTypeList")
    if pt_list is not None:
        for pt in pt_list:
            cost_czk = float(pt.get("cost") or 0.0)
            weight = float(pt.get("weight") or 0.0)
            name = pt.get("name")
            gauge = pt.get("gauge")
            
            if substitute_real_prices:
                key = (name, gauge)
                if key in substitute_map:
                    new_name, new_gauge, cost_czk, weight = substitute_map[key]
                    name = new_name
                    
            pt_map[pt.get("id")] = {
                "cost_eur": (cost_czk / exchange_rate) * plate_markup,
                "weight_kg": weight,
                "name": name
            }
            
    # 2. Map Timber Sections
    ts_map = {}
    ts_list = root.find("TimberSectionList")
    if ts_list is not None:
        for ts in ts_list:
            ts_map[ts.get("id")] = {
                "height": float(ts.get("height")),
                "thickness": float(ts.get("thickness")),
            }
            
    # 3. Collect Frame definitions
    frame_defs = {}
    frame_list = root.find("FrameList")
    if frame_list is not None:
        for frame in frame_list:
            fid = frame.get("id")
            name = frame.get("name")
            
            # Calculate local timber volume of this frame
            vol = 0.0
            for part in frame.find("PartList"):
                for m in part.find("MemberList"):
                    thick = float(m.get("overallThickness") or 0.045)
                    timber_id = m.get("timberID")
                    ts_info = ts_map.get(timber_id)
                    height = ts_info["height"] if ts_info else 0.09
                    length = float(m.get("stockLength") or 0.0)
                    vol += thick * height * length
                    
            # Calculate local plate count & cost of this frame
            plt_cost_eur = 0.0
            plt_weight_kg = 0.0
            plt_qty = 0
            for part in frame.find("PartList"):
                fixing = part.find("MemberFixingList")
                if fixing is not None:
                    for pl in fixing.findall("Plate"):
                        pid = pl.get("plateTypeID")
                        pt_info = pt_map.get(pid)
                        if pt_info:
                            plt_cost_eur += pt_info["cost_eur"]
                            plt_weight_kg += pt_info["weight_kg"]
                            plt_qty += 1
                            
            frame_defs[fid] = {
                "name": name,
                "timber_volume_m3": vol,
                "plates_cost_eur": plt_cost_eur,
                "plates_weight_kg": plt_weight_kg,
                "plates_qty": plt_qty
            }
            
    # 4. Count frame instances in BuildingFrameList
    bf_list = root.find(".//BuildingFrameList")
    frame_instances = {}
    if bf_list is not None:
        for bf in bf_list:
            fid = bf.get("frameID")
            frame_instances[fid] = frame_instances.get(fid, 0) + 1
            
    # 5. Calculate totals
    total_timber_volume = 0.0
    total_plates_cost = 0.0
    total_plates_weight = 0.0
    total_plates_qty = 0
    unique_types_count = len(frame_instances)
    
    line_items = []
    
    for fid, qty in frame_instances.items():
        fdef = frame_defs.get(fid)
        if not fdef:
            continue
        
        timber_vol = fdef["timber_volume_m3"] * qty
        plates_cost = fdef["plates_cost_eur"] * qty
        plates_weight = fdef["plates_weight_kg"] * qty
        plates_qty = fdef["plates_qty"] * qty
        
        total_timber_volume += timber_vol
        total_plates_cost += plates_cost
        total_plates_weight += plates_weight
        total_plates_qty += plates_qty
        
        # Line item price = (Timber_Cost + Plates_Cost) * (1 + fabrication_markup) + (setup_cost_per_type / qty)*qty
        # Since setup cost is per type, the contribution to this line item is setup_cost_per_type
        raw_materials = (timber_vol * timber_rate_eur_m3) + plates_cost
        line_price = raw_materials * (1.0 + fabrication_markup) + setup_cost_per_type
        
        line_items.append({
            "name": fdef["name"],
            "qty": qty,
            "timber_volume_m3": timber_vol,
            "timber_cost_eur": timber_vol * timber_rate_eur_m3,
            "plates_cost_eur": plates_cost,
            "price_eur": line_price
        })
        
    total_price = sum(item["price_eur"] for item in line_items)
    
    return {
        "timber_volume_m3": total_timber_volume,
        "plates_qty": total_plates_qty,
        "plates_weight_kg": total_plates_weight,
        "plates_cost_eur": total_plates_cost,
        "line_items": line_items,
        "total_price_eur": total_price
    }
