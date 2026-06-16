"use client";

import dynamic from "next/dynamic";
import { useCallback, useState, useRef, DragEvent, ChangeEvent } from "react";

const CadViewer3D = dynamic(
  () => import("@/components/cad-viewer-3d").then((m) => m.CadViewer3D),
  { ssr: false }
);

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

function parseIfcToDxf(ifcText: string): string {
  const cleanText = ifcText.replace(/\/\*[\s\S]*?\*\//g, "");
  const statements = cleanText.split(";");
  const entities: Record<string, { type: string; args: string[] }> = {};
  
  // Regex to match #123 = ENTITYNAME(...)
  const statementRegex = /^#(\d+)\s*=\s*([A-Z0-9_]+)\s*\(([\s\S]*)\)\s*$/i;
  
  for (const statement of statements) {
    const match = statement.trim().match(statementRegex);
    if (match) {
      const id = match[1];
      const type = match[2].toUpperCase();
      const argsStr = match[3];
      
      const args: string[] = [];
      let current = "";
      let parenDepth = 0;
      let inString = false;
      
      for (let i = 0; i < argsStr.length; i++) {
        const char = argsStr[i];
        if (char === "'" && (i === 0 || argsStr[i - 1] !== "\\")) {
          inString = !inString;
          current += char;
        } else if (inString) {
          current += char;
        } else if (char === "(") {
          parenDepth++;
          current += char;
        } else if (char === ")") {
          parenDepth--;
          current += char;
        } else if (char === "," && parenDepth === 0) {
          args.push(current.trim());
          current = "";
        } else {
          current += char;
        }
      }
      if (current.trim()) {
        args.push(current.trim());
      }
      
      entities[id] = { type, args };
    }
  }
  
  // Helper to trace shape representation -> product definition shape -> product -> local placement
  function findProductLocalPlacementId(solidId: string): string | null {
    let shapeRepId: string | null = null;
    for (const [id, ent] of Object.entries(entities)) {
      if (ent.type === "IFCSHAPEREPRESENTATION") {
        const itemsStr = ent.args[3]; // 4th argument: (item1, item2, ...)
        if (itemsStr && itemsStr.includes(`#${solidId}`)) {
          shapeRepId = id;
          break;
        }
      }
    }
    if (!shapeRepId) return null;

    let prodDefShapeId: string | null = null;
    for (const [id, ent] of Object.entries(entities)) {
      if (ent.type === "IFCPRODUCTDEFINITIONSHAPE") {
        const repsStr = ent.args[2]; // 3rd argument: (rep1, rep2, ...)
        if (repsStr && repsStr.includes(`#${shapeRepId}`)) {
          prodDefShapeId = id;
          break;
        }
      }
    }
    if (!prodDefShapeId) return null;

    for (const ent of Object.values(entities)) {
      if (
        ent.type === "IFCMEMBER" ||
        ent.type === "IFCWALLSTANDARDCASE" ||
        ent.type === "IFCWALL" ||
        ent.type === "IFCBEAM" ||
        ent.type === "IFCCOLUMN"
      ) {
        const shapeArg = ent.args[6]; // 7th argument
        if (shapeArg && shapeArg.replace("#", "") === prodDefShapeId) {
          const placementArg = ent.args[5]; // 6th argument
          if (placementArg) {
            return placementArg.replace("#", "");
          }
        }
      }
    }
    return null;
  }

  // Helper to parse IFCCARTESIANPOINT
  function parseCartesianPoint(pointId: string): [number, number, number] {
    const ent = entities[pointId];
    if (ent && ent.type === "IFCCARTESIANPOINT") {
      const coordsStr = ent.args[0].replace(/[()]/g, "");
      const coords = coordsStr.split(",").map(c => parseFloat(c));
      return [coords[0] || 0, coords[1] || 0, coords[2] || 0];
    }
    return [0, 0, 0];
  }

  // Helper to parse IFCDIRECTION
  function parseDirection(dirId: string, defVal: [number, number, number]): [number, number, number] {
    const ent = entities[dirId];
    if (ent && ent.type === "IFCDIRECTION") {
      const dirStr = ent.args[0].replace(/[()]/g, "");
      const dir = dirStr.split(",").map(d => parseFloat(d));
      return [dir[0] ?? defVal[0], dir[1] ?? defVal[1], dir[2] ?? defVal[2]];
    }
    return defVal;
  }

  // Helper to resolve IFCAXIS2PLACEMENT3D coordinates and directions
  function resolvePlacement3D(placementId: string) {
    const placement = entities[placementId];
    let location: [number, number, number] = [0, 0, 0];
    let axis: [number, number, number] = [0, 0, 1];
    let refDir: [number, number, number] = [1, 0, 0];

    if (placement && placement.type === "IFCAXIS2PLACEMENT3D") {
      const locId = placement.args[0].replace("#", "");
      location = parseCartesianPoint(locId);

      if (placement.args[1] && placement.args[1] !== "$") {
        const axisId = placement.args[1].replace("#", "");
        axis = parseDirection(axisId, [0, 0, 1]);
      }
      if (placement.args[2] && placement.args[2] !== "$") {
        const refDirId = placement.args[2].replace("#", "");
        refDir = parseDirection(refDirId, [1, 0, 0]);
      }
    }

    // Orthonormalize basis
    // 1. Z-axis
    const zLen = Math.sqrt(axis[0]*axis[0] + axis[1]*axis[1] + axis[2]*axis[2]) || 1.0;
    const zAxis = [axis[0]/zLen, axis[1]/zLen, axis[2]/zLen];

    // 2. Project refDir onto plane perpendicular to zAxis: xProj = refDir - (refDir . zAxis) * zAxis
    const dot = refDir[0]*zAxis[0] + refDir[1]*zAxis[1] + refDir[2]*zAxis[2];
    let xProj = [
      refDir[0] - dot * zAxis[0],
      refDir[1] - dot * zAxis[1],
      refDir[2] - dot * zAxis[2]
    ];

    let xLen = Math.sqrt(xProj[0]*xProj[0] + xProj[1]*xProj[1] + xProj[2]*xProj[2]);
    if (xLen < 1e-6) {
      // Collinear fallback
      if (Math.abs(zAxis[0]) > 0.9) {
        xProj = [0, 1, 0];
      } else {
        xProj = [1, 0, 0];
      }
      const dot2 = xProj[0]*zAxis[0] + xProj[1]*zAxis[1] + xProj[2]*zAxis[2];
      xProj = [
        xProj[0] - dot2 * zAxis[0],
        xProj[1] - dot2 * zAxis[1],
        xProj[2] - dot2 * zAxis[2]
      ];
      xLen = Math.sqrt(xProj[0]*xProj[0] + xProj[1]*xProj[1] + xProj[2]*xProj[2]) || 1.0;
    }
    const xAxis = [xProj[0]/xLen, xProj[1]/xLen, xProj[2]/xLen];

    // 3. Y-axis = Z-axis x X-axis
    const yAxis = [
      zAxis[1]*xAxis[2] - zAxis[2]*xAxis[1],
      zAxis[2]*xAxis[0] - zAxis[0]*xAxis[2],
      zAxis[0]*xAxis[1] - zAxis[1]*xAxis[0]
    ];

    return { location, xAxis, yAxis, zAxis };
  }
  
  const extrudedSolids = Object.entries(entities).filter(
    ([, ent]) => ent.type === "IFCEXTRUDEDAREASOLID"
  );
  
  let dxfEntities = "";
  
  for (const [solidId, solid] of extrudedSolids) {
    try {
      const sweptAreaId = solid.args[0].replace("#", "");
      const positionId = solid.args[1].replace("#", "");
      const depth = parseFloat(solid.args[3]);
      
      const sweptArea = entities[sweptAreaId];
      if (!sweptArea) continue;
      
      if (sweptArea.type === "IFCRECTANGLEPROFILEDEF") {
        const profilePosId = sweptArea.args[2].replace("#", "");
        const xDim = parseFloat(sweptArea.args[3]);
        const yDim = parseFloat(sweptArea.args[4]);
        
        let px = 0;
        let py = 0;
        const profilePos = entities[profilePosId];
        if (profilePos && profilePos.type === "IFCAXIS2PLACEMENT2D") {
          const locId = profilePos.args[0].replace("#", "");
          const loc = entities[locId];
          if (loc && loc.type === "IFCCARTESIANPOINT") {
            const coordsStr = loc.args[0].replace(/[()]/g, "");
            const coords = coordsStr.split(",").map(c => parseFloat(c));
            px = coords[0] || 0;
            py = coords[1] || 0;
          }
        }
        
        // 1. Resolve Solid placement coordinate transformation
        const T_solid = resolvePlacement3D(positionId);

        // 2. Compute local 3D vertices relative to the product coordinate system
        const xMin = px - xDim / 2;
        const xMax = px + xDim / 2;
        const yMin = py - yDim / 2;
        const yMax = py + yDim / 2;

        const p_local = [
          [xMin, yMin],
          [xMax, yMin],
          [xMax, yMax],
          [xMin, yMax]
        ];

        // Transform 2D profile coordinates to local 3D coordinates using T_solid
        const v_local: number[][] = [];
        for (let i = 0; i < 4; i++) {
          const pt = p_local[i];
          v_local.push([
            T_solid.location[0] + pt[0] * T_solid.xAxis[0] + pt[1] * T_solid.yAxis[0],
            T_solid.location[1] + pt[0] * T_solid.xAxis[1] + pt[1] * T_solid.yAxis[1],
            T_solid.location[2] + pt[0] * T_solid.xAxis[2] + pt[1] * T_solid.yAxis[2]
          ]);
        }
        // Top profile vertices are swept along Z-axis of solid placement by depth
        for (let i = 0; i < 4; i++) {
          const bottom = v_local[i];
          v_local.push([
            bottom[0] + depth * T_solid.zAxis[0],
            bottom[1] + depth * T_solid.zAxis[1],
            bottom[2] + depth * T_solid.zAxis[2]
          ]);
        }

        // 3. Resolve Product local placement (from storey to global)
        const placementId = findProductLocalPlacementId(solidId);
        let v_global = v_local;

        if (placementId) {
          const placement = entities[placementId];
          if (placement && placement.type === "IFCLOCALPLACEMENT") {
            const relPlacementId = placement.args[1].replace("#", "");
            const T_product = resolvePlacement3D(relPlacementId);

            // Transform local 3D vertices to global coordinates
            v_global = v_local.map(vl => [
              T_product.location[0] + vl[0] * T_product.xAxis[0] + vl[1] * T_product.yAxis[0] + vl[2] * T_product.zAxis[0],
              T_product.location[1] + vl[0] * T_product.xAxis[1] + vl[1] * T_product.yAxis[1] + vl[2] * T_product.zAxis[1],
              T_product.location[2] + vl[0] * T_product.xAxis[2] + vl[1] * T_product.yAxis[2] + vl[2] * T_product.zAxis[2]
            ]);
          }
        }

        const v1 = v_global[0];
        const v2 = v_global[1];
        const v3 = v_global[2];
        const v4 = v_global[3];
        const v5 = v_global[4];
        const v6 = v_global[5];
        const v7 = v_global[6];
        const v8 = v_global[7];

        const COS_30 = 0.86602540378;
        const SIN_30 = 0.5;
        const projectPoint = (pt: number[]): [number, number] => {
          const x = pt[0];
          const y = pt[1];
          const z = pt[2];
          const xIso = (x - y) * COS_30;
          const yIso = (x + y) * SIN_30 + z;
          return [xIso, yIso];
        };

        const p1 = projectPoint(v1);
        const p2 = projectPoint(v2);
        const p3 = projectPoint(v3);
        const p4 = projectPoint(v4);
        const p5 = projectPoint(v5);
        const p6 = projectPoint(v6);
        const p7 = projectPoint(v7);
        const p8 = projectPoint(v8);
        
        const addLine = (pt1: [number, number], pt2: [number, number]) => {
          return `  0
LINE
  8
0
 10
${pt1[0]}
 20
${pt1[1]}
 30
0.0
 11
${pt2[0]}
 21
${pt2[1]}
 31
0.0
`;
        };
        
        dxfEntities += addLine(p1, p2);
        dxfEntities += addLine(p2, p3);
        dxfEntities += addLine(p3, p4);
        dxfEntities += addLine(p4, p1);
        
        dxfEntities += addLine(p5, p6);
        dxfEntities += addLine(p6, p7);
        dxfEntities += addLine(p7, p8);
        dxfEntities += addLine(p8, p5);
        
        dxfEntities += addLine(p1, p5);
        dxfEntities += addLine(p2, p6);
        dxfEntities += addLine(p3, p7);
        dxfEntities += addLine(p4, p8);
      }
    } catch (err) {
      console.error("Error parsing solid geometry:", err);
    }
  }
  
  if (!dxfEntities) {
    dxfEntities = `  0
LINE
  8
0
 10
0.0
 20
0.0
 30
0.0
 11
1000.0
 21
1000.0
 31
1000.0
`;
  }
  
  return `  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1015
  0
ENDSEC
  0
SECTION
  2
ENTITIES
${dxfEntities}  0
ENDSEC
  0
EOF`;
}

export default function CadViewer3DPage() {
  const [dxfContent, setDxfContent] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback((file: File) => {
    const lowerName = file.name.toLowerCase();
    const isDxf = lowerName.endsWith(".dxf");
    const isIfc = lowerName.endsWith(".ifc") || lowerName.endsWith(".icf");

    if (!isDxf && !isIfc) {
      setError("Please select a .dxf, .ifc, or .icf file");
      return;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError("File exceeds 10 MB limit");
      return;
    }
    setError(null);
    setLoading(true);
    setFileName(file.name);

    const reader = new FileReader();
    if (isDxf) {
      reader.onload = () => {
        const arrayBuffer = reader.result as ArrayBuffer;
        const bytes = new Uint8Array(arrayBuffer);
        let binary = "";
        const chunkSize = 8192;
        for (let i = 0; i < bytes.length; i += chunkSize) {
          const chunk = bytes.subarray(i, Math.min(i + chunkSize, bytes.length));
          binary += String.fromCharCode.apply(null, Array.from(chunk));
        }
        const base64 = btoa(binary);
        setDxfContent(base64);
        setLoading(false);
      };
      reader.onerror = () => {
        setError("Failed to read file");
        setLoading(false);
      };
      reader.readAsArrayBuffer(file);
    } else {
      reader.onload = () => {
        try {
          const text = reader.result as string;
          const dxfText = parseIfcToDxf(text);
          const base64 = btoa(dxfText);
          setDxfContent(base64);
          setLoading(false);
        } catch {
          setError("Failed to parse IFC file to DXF");
          setLoading(false);
        }
      };
      reader.onerror = () => {
        setError("Failed to read file");
        setLoading(false);
      };
      reader.readAsText(file);
    }
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) processFile(file);
      if (fileInputRef.current) fileInputRef.current.value = "";
    },
    [processFile]
  );

  const handleReset = useCallback(() => {
    setDxfContent(null);
    setFileName("");
    setError(null);
  }, []);

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-[#d4d4d4] flex flex-col">
      <header className="flex items-center justify-between px-6 py-4 border-b border-[#333]">
        <h1 className="text-lg font-semibold tracking-wide text-[#e0e0e0]">
          3D CAD Test Viewer
        </h1>
        {fileName && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-[#858585]">{fileName}</span>
            <button
              onClick={handleReset}
              className="px-3 py-1 text-sm rounded bg-[#333] hover:bg-[#444] text-[#d4d4d4] transition-colors cursor-pointer"
            >
              Clear
            </button>
          </div>
        )}
      </header>

      <main className="flex-1 flex flex-col">
        {dxfContent ? (
          <div className="flex-1 relative border-t-2 border-[#007fd4]">
            <CadViewer3D
              dxfContent={dxfContent}
              className="w-full h-full absolute inset-0"
            />
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-8">
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`
                w-full max-w-xl h-72 rounded-xl border-2 border-dashed
                flex flex-col items-center justify-center gap-4 cursor-pointer
                transition-all duration-200
                ${
                  isDragOver
                    ? "border-[#007fd4] bg-[#007fd4]/10"
                    : "border-[#555] bg-[#252526] hover:border-[#007fd4] hover:bg-[#2a2a2a]"
                }
              `}
            >
              {loading ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-2 border-[#007fd4] border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm text-[#858585]">
                    Loading file...
                  </span>
                </div>
              ) : (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-12 h-12 text-[#555]"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
                    />
                  </svg>
                  <div className="text-center">
                    <p className="text-[#d4d4d4] text-sm font-medium">
                      Drag & drop a DXF, IFC, or ICF file here
                    </p>
                    <p className="text-[#858585] text-xs mt-1">
                      or click to browse (max 10 MB)
                    </p>
                  </div>
                </>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".dxf,.ifc,.icf"
              className="hidden"
              onChange={handleFileInput}
            />
          </div>
        )}

        {error && (
          <div className="px-6 py-3 bg-red-900/30 border-t border-red-800 text-red-300 text-sm">
            {error}
          </div>
        )}
      </main>
    </div>
  );
}
