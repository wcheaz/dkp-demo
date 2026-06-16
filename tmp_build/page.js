"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = CadViewer3DPage;
const dynamic_1 = require("next/dynamic");
const react_1 = require("react");
const CadViewer3D = (0, dynamic_1.default)(() => Promise.resolve().then(() => require("@/components/cad-viewer-3d")).then((m) => m.CadViewer3D), { ssr: false });
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;
function parseIfcToDxf(ifcText) {
    const cleanText = ifcText.replace(/\/\*[\s\S]*?\*\//g, "");
    const statements = cleanText.split(";");
    const entities = {};
    // Regex to match #123 = ENTITYNAME(...)
    const statementRegex = /^#(\d+)\s*=\s*([A-Z0-9_]+)\s*\(([\s\S]*)\)\s*$/i;
    for (const statement of statements) {
        const match = statement.trim().match(statementRegex);
        if (match) {
            const id = match[1];
            const type = match[2].toUpperCase();
            const argsStr = match[3];
            const args = [];
            let current = "";
            let parenDepth = 0;
            let inString = false;
            for (let i = 0; i < argsStr.length; i++) {
                const char = argsStr[i];
                if (char === "'" && (i === 0 || argsStr[i - 1] !== "\\")) {
                    inString = !inString;
                    current += char;
                }
                else if (inString) {
                    current += char;
                }
                else if (char === "(") {
                    parenDepth++;
                    current += char;
                }
                else if (char === ")") {
                    parenDepth--;
                    current += char;
                }
                else if (char === "," && parenDepth === 0) {
                    args.push(current.trim());
                    current = "";
                }
                else {
                    current += char;
                }
            }
            if (current.trim()) {
                args.push(current.trim());
            }
            entities[id] = { type, args };
        }
    }
    const extrudedSolids = Object.entries(entities).filter(([, ent]) => ent.type === "IFCEXTRUDEDAREASOLID");
    let dxfEntities = "";
    for (const [, solid] of extrudedSolids) {
        try {
            const sweptAreaId = solid.args[0].replace("#", "");
            const positionId = solid.args[1].replace("#", "");
            const depth = parseFloat(solid.args[3]);
            const sweptArea = entities[sweptAreaId];
            if (!sweptArea)
                continue;
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
                let sx = 0;
                let sy = 0;
                let sz = 0;
                const solidPos = entities[positionId];
                if (solidPos && solidPos.type === "IFCAXIS2PLACEMENT3D") {
                    const locId = solidPos.args[0].replace("#", "");
                    const loc = entities[locId];
                    if (loc && loc.type === "IFCCARTESIANPOINT") {
                        const coordsStr = loc.args[0].replace(/[()]/g, "");
                        const coords = coordsStr.split(",").map(c => parseFloat(c));
                        sx = coords[0] || 0;
                        sy = coords[1] || 0;
                        sz = coords[2] || 0;
                    }
                }
                const xMin = px - xDim / 2;
                const xMax = px + xDim / 2;
                const yMin = py - yDim / 2;
                const yMax = py + yDim / 2;
                const v1 = [xMin + sx, yMin + sy, sz];
                const v2 = [xMax + sx, yMin + sy, sz];
                const v3 = [xMax + sx, yMax + sy, sz];
                const v4 = [xMin + sx, yMax + sy, sz];
                const v5 = [v1[0], v1[1], v1[2] + depth];
                const v6 = [v2[0], v2[1], v2[2] + depth];
                const v7 = [v3[0], v3[1], v3[2] + depth];
                const v8 = [v4[0], v4[1], v4[2] + depth];
                const COS_30 = 0.86602540378;
                const SIN_30 = 0.5;
                const projectPoint = (pt) => {
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
                const addLine = (pt1, pt2) => {
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
        }
        catch (err) {
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
function CadViewer3DPage() {
    const [dxfContent, setDxfContent] = (0, react_1.useState)(null);
    const [fileName, setFileName] = (0, react_1.useState)("");
    const [loading, setLoading] = (0, react_1.useState)(false);
    const [error, setError] = (0, react_1.useState)(null);
    const [isDragOver, setIsDragOver] = (0, react_1.useState)(false);
    const fileInputRef = (0, react_1.useRef)(null);
    const processFile = (0, react_1.useCallback)((file) => {
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
                const arrayBuffer = reader.result;
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
        }
        else {
            reader.onload = () => {
                try {
                    const text = reader.result;
                    const dxfText = parseIfcToDxf(text);
                    const base64 = btoa(dxfText);
                    setDxfContent(base64);
                    setLoading(false);
                }
                catch {
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
    const handleDrop = (0, react_1.useCallback)((e) => {
        e.preventDefault();
        setIsDragOver(false);
        const file = e.dataTransfer.files?.[0];
        if (file)
            processFile(file);
    }, [processFile]);
    const handleDragOver = (0, react_1.useCallback)((e) => {
        e.preventDefault();
        setIsDragOver(true);
    }, []);
    const handleDragLeave = (0, react_1.useCallback)((e) => {
        e.preventDefault();
        setIsDragOver(false);
    }, []);
    const handleFileInput = (0, react_1.useCallback)((e) => {
        const file = e.target.files?.[0];
        if (file)
            processFile(file);
        if (fileInputRef.current)
            fileInputRef.current.value = "";
    }, [processFile]);
    const handleReset = (0, react_1.useCallback)(() => {
        setDxfContent(null);
        setFileName("");
        setError(null);
    }, []);
    return (<div className="min-h-screen bg-[#1e1e1e] text-[#d4d4d4] flex flex-col">
      <header className="flex items-center justify-between px-6 py-4 border-b border-[#333]">
        <h1 className="text-lg font-semibold tracking-wide text-[#e0e0e0]">
          3D CAD Test Viewer
        </h1>
        {fileName && (<div className="flex items-center gap-3">
            <span className="text-sm text-[#858585]">{fileName}</span>
            <button onClick={handleReset} className="px-3 py-1 text-sm rounded bg-[#333] hover:bg-[#444] text-[#d4d4d4] transition-colors cursor-pointer">
              Clear
            </button>
          </div>)}
      </header>

      <main className="flex-1 flex flex-col">
        {dxfContent ? (<div className="flex-1 relative border-t-2 border-[#007fd4]">
            <CadViewer3D dxfContent={dxfContent} className="w-full h-full absolute inset-0"/>
          </div>) : (<div className="flex-1 flex items-center justify-center p-8">
            <div onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onClick={() => fileInputRef.current?.click()} className={`
                w-full max-w-xl h-72 rounded-xl border-2 border-dashed
                flex flex-col items-center justify-center gap-4 cursor-pointer
                transition-all duration-200
                ${isDragOver
                ? "border-[#007fd4] bg-[#007fd4]/10"
                : "border-[#555] bg-[#252526] hover:border-[#007fd4] hover:bg-[#2a2a2a]"}
              `}>
              {loading ? (<div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-2 border-[#007fd4] border-t-transparent rounded-full animate-spin"/>
                  <span className="text-sm text-[#858585]">
                    Loading file...
                  </span>
                </div>) : (<>
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-12 h-12 text-[#555]">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"/>
                  </svg>
                  <div className="text-center">
                    <p className="text-[#d4d4d4] text-sm font-medium">
                      Drag & drop a DXF, IFC, or ICF file here
                    </p>
                    <p className="text-[#858585] text-xs mt-1">
                      or click to browse (max 10 MB)
                    </p>
                  </div>
                </>)}
            </div>
            <input ref={fileInputRef} type="file" accept=".dxf,.ifc,.icf" className="hidden" onChange={handleFileInput}/>
          </div>)}

        {error && (<div className="px-6 py-3 bg-red-900/30 border-t border-red-800 text-red-300 text-sm">
            {error}
          </div>)}
      </main>
    </div>);
}
