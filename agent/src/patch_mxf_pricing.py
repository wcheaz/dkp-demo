import xml.etree.ElementTree as ET
import os

def patch_mxf_bytes(mxf_bytes: bytes) -> bytes:
    try:
        root = ET.fromstring(mxf_bytes)
    except Exception as e:
        raise ValueError(f"Failed to parse MXF XML: {e}")
        
    pt_list = root.find("PlateTypeList")
    if pt_list is None:
        # If no PlateTypeList, just return unmodified bytes
        return mxf_bytes
        
    # Mapping table from GNA20 / placeholder plates to priced M20/T150 catalog plates
    # Format: (gna_name, gna_gauge) -> (m20_name, m20_gauge, cost, weight, length, width)
    mapping = {
        ("0812", "GNA20"): ("0813", "M20", 688.21, 0.0757682, 0.127, 0.076),
        ("0912", "T150"): ("1014", "T150", 1032.314, 0.1729512, 0.144, 0.102),
        ("1010", "GNA20"): ("1010", "M20", 688.21, 0.0816714, 0.102, 0.102),
        ("1010", "T150"): ("1014", "T150", 1032.314, 0.1729512, 0.144, 0.102),
        ("1014", "GNA20"): ("1015", "M20", 688.21, 0.1217064, 0.152, 0.102),
        ("1014", "T150"): ("1014", "T150", 1032.314, 0.1729512, 0.144, 0.102),
        ("1031", "GNA20"): ("1025", "M20", 688.21, 0.2033778, 0.254, 0.102)
    }
    
    id_map = {}
    pt_elements = list(pt_list)
    pt_list.clear()
    
    for idx, pt in enumerate(pt_elements):
        name = pt.get("name")
        gauge = pt.get("gauge")
        old_id = pt.get("id")
        
        key = (name, gauge)
        if key in mapping:
            new_name, new_gauge, cost, weight, length, width = mapping[key]
            new_id = f"PT{idx}"
            id_map[old_id] = new_id
            
            ET.SubElement(pt_list, "PlateType", {
                "id": new_id,
                "gauge": new_gauge,
                "name": new_name,
                "length": f"{length:g}",
                "width": f"{width:g}",
                "quantityPerBox": "0",
                "weight": f"{weight:g}",
                "cost": f"{cost:g}",
                "currency": "€",
                "quantity": pt.get("quantity") or "100"
            })
        else:
            new_id = f"PT{idx}"
            id_map[old_id] = new_id
            pt.set("id", new_id)
            pt_list.append(pt)

    # Update all Plate elements in FrameList to use the new plateTypeIDs
    frame_list = root.find("FrameList")
    if frame_list is not None:
        for frame in frame_list:
            for plate in frame.iter("Plate"):
                old_pid = plate.get("plateTypeID")
                if old_pid in id_map:
                    plate.set("plateTypeID", id_map[old_pid])

    # Update PlateTypeQuantityList in JobList/Job
    job_qty_list = root.find(".//PlateTypeQuantityList")
    if job_qty_list is not None:
        qty_elements = list(job_qty_list)
        job_qty_list.clear()
        for q in qty_elements:
            old_pid = q.get("plateTypeID")
            if old_pid in id_map:
                q.set("plateTypeID", id_map[old_pid])
                job_qty_list.append(q)

    return ET.tostring(root, encoding="utf-8")
