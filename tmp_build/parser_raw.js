"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseIfcToDxf = parseIfcToDxf;
exports.findProductLocalPlacementId = findProductLocalPlacementId;
exports.resolvePlacement3D = resolvePlacement3D;
exports.getOrthonormalBasis = getOrthonormalBasis;
exports.resolvePolyLoop = resolvePolyLoop;
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
    for (const [solidId, solid] of extrudedSolids) {
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
                        const coords = coordsStr.split(",").map((c) => parseFloat(c));
                        px = coords[0] || 0;
                        py = coords[1] || 0;
                    }
                }
                const solidPlacement = resolvePlacement3D(entities, positionId);
                const solidBasis = solidPlacement
                    ? getOrthonormalBasis(solidPlacement.axis, solidPlacement.refDir)
                    : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
                const solidOrigin = solidPlacement
                    ? solidPlacement.location
                    : [0, 0, 0];
                const productPlacementId = findProductLocalPlacementId(entities, solidId);
                const productPlacement = productPlacementId
                    ? resolvePlacement3D(entities, productPlacementId)
                    : null;
                const productBasis = productPlacement
                    ? getOrthonormalBasis(productPlacement.axis, productPlacement.refDir)
                    : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
                const productOrigin = productPlacement
                    ? productPlacement.location
                    : [0, 0, 0];
                const xMin = px - xDim / 2;
                const xMax = px + xDim / 2;
                const yMin = py - yDim / 2;
                const yMax = py + yDim / 2;
                // Profile corners in the solid's local coordinate system.
                // Bottom face sits at z=0; top face is extruded by depth along local Z.
                const localVerts = [
                    [xMin, yMin, 0],
                    [xMax, yMin, 0],
                    [xMax, yMax, 0],
                    [xMin, yMax, 0],
                    [xMin, yMin, depth],
                    [xMax, yMin, depth],
                    [xMax, yMax, depth],
                    [xMin, yMax, depth],
                ];
                // Map local -> solid placement frame -> product placement frame (global).
                const verts = localVerts.map((v) => {
                    const inSolidFrame = transformPoint(v, solidOrigin, solidBasis);
                    return transformPoint(inSolidFrame, productOrigin, productBasis);
                });
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
${pt1[2]}
 11
${pt2[0]}
 21
${pt2[1]}
 31
${pt2[2]}
`;
                };
                const [p1, p2, p3, p4, p5, p6, p7, p8] = verts;
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
    // B-Rep geometry: IFCFACETEDBREP -> IFCCLOSEDSHELL -> IFCFACE ->
    // IFCFACEOUTERBOUND/IFCFACEBOUND -> IFCPOLYLOOP -> IFCCARTESIANPOINT.
    // Each polyloop edge becomes a DXF LINE so Pamir B-Rep meshes render as
    // a wireframe without a client-side solid kernel.
    const brepSolids = Object.entries(entities).filter(([, ent]) => ent.type === "IFCFACETEDBREP");
    for (const [brepId, brep] of brepSolids) {
        try {
            if (brep.args.length < 1)
                continue;
            const closedShellId = brep.args[0].replace("#", "").trim();
            const closedShell = entities[closedShellId];
            if (!closedShell ||
                (closedShell.type !== "IFCCLOSEDSHELL" &&
                    closedShell.type !== "IFCOPENSHELL"))
                continue;
            const faceRefs = closedShell.args[0]
                .replace(/[()]/g, "")
                .split(",")
                .map((s) => s.trim().replace("#", ""))
                .filter(Boolean);
            const productPlacementId = findProductLocalPlacementId(entities, brepId);
            const productPlacement = productPlacementId
                ? resolvePlacement3D(entities, productPlacementId)
                : null;
            const productBasis = productPlacement
                ? getOrthonormalBasis(productPlacement.axis, productPlacement.refDir)
                : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
            const productOrigin = productPlacement
                ? productPlacement.location
                : [0, 0, 0];
            for (const faceRef of faceRefs) {
                const face = entities[faceRef];
                if (!face || face.type !== "IFCFACE" || face.args.length < 1)
                    continue;
                const boundRefs = face.args[0]
                    .replace(/[()]/g, "")
                    .split(",")
                    .map((s) => s.trim().replace("#", ""))
                    .filter(Boolean);
                for (const boundRef of boundRefs) {
                    const bound = entities[boundRef];
                    if (!bound ||
                        (bound.type !== "IFCFACEOUTERBOUND" &&
                            bound.type !== "IFCFACEBOUND"))
                        continue;
                    const pts = resolvePolyLoop(entities, bound.args[0]);
                    if (pts.length < 2)
                        continue;
                    const verts = pts.map((v) => transformPoint(v, productOrigin, productBasis));
                    for (let i = 0; i < verts.length; i++) {
                        const a = verts[i];
                        const b = verts[(i + 1) % verts.length];
                        dxfEntities += formatDxfLine(a, b);
                    }
                }
            }
        }
        catch (err) {
            console.error("Error parsing B-Rep geometry:", err);
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
const PRODUCT_ENTITY_TYPES = new Set([
    "IFCMEMBER",
    "IFCWALLSTANDARDCASE",
    "IFCWALL",
    "IFCBEAM",
    "IFCCOLUMN",
    "IFCSLAB",
    "IFCPLATE",
    "IFCFOOTING",
    "IFCROOF",
    "IFCCURTAINWALL",
]);
function parseCartesianOrDirection(entities, ref, fallback) {
    const id = ref.replace("#", "").trim();
    const entity = entities[id];
    if (!entity ||
        (entity.type !== "IFCCARTESIANPOINT" && entity.type !== "IFCDIRECTION")) {
        return fallback;
    }
    const coordsStr = entity.args[0].replace(/[()]/g, "");
    const coords = coordsStr.split(",").map((c) => parseFloat(c));
    return [coords[0] || 0, coords[1] || 0, coords[2] || 0];
}
function findProductLocalPlacementId(entities, solidId) {
    let shapeRepId = null;
    for (const [id, entity] of Object.entries(entities)) {
        if (entity.type === "IFCSHAPEREPRESENTATION" && entity.args.length >= 4) {
            const items = entity.args[3]
                .replace(/[()]/g, "")
                .split(",")
                .map((s) => s.trim().replace("#", ""));
            if (items.includes(solidId)) {
                shapeRepId = id;
                break;
            }
        }
    }
    if (shapeRepId === null)
        return null;
    let productDefShapeId = null;
    for (const [id, entity] of Object.entries(entities)) {
        if (entity.type === "IFCPRODUCTDEFINITIONSHAPE" &&
            entity.args.length >= 1) {
            const reps = entity.args[entity.args.length - 1]
                .replace(/[()]/g, "")
                .split(",")
                .map((s) => s.trim().replace("#", ""));
            if (reps.includes(shapeRepId)) {
                productDefShapeId = id;
                break;
            }
        }
    }
    if (productDefShapeId === null)
        return null;
    for (const entity of Object.values(entities)) {
        if (PRODUCT_ENTITY_TYPES.has(entity.type) &&
            entity.args.length >= 7) {
            const repRef = entity.args[6].replace("#", "");
            if (repRef === productDefShapeId) {
                return entity.args[5].replace("#", "");
            }
        }
    }
    return null;
}
function resolvePlacement3D(entities, placementId) {
    let entity = entities[placementId];
    if (!entity)
        return null;
    if (entity.type === "IFCLOCALPLACEMENT") {
        if (entity.args.length < 2)
            return null;
        entity = entities[entity.args[1].replace("#", "")];
        if (!entity)
            return null;
    }
    if (entity.type !== "IFCAXIS2PLACEMENT3D")
        return null;
    const location = parseCartesianOrDirection(entities, entity.args[0], [
        0,
        0,
        0,
    ]);
    const axis = entity.args.length > 1 && entity.args[1] && entity.args[1] !== "$"
        ? parseCartesianOrDirection(entities, entity.args[1], [0, 0, 1])
        : [0, 0, 1];
    const refDir = entity.args.length > 2 && entity.args[2] && entity.args[2] !== "$"
        ? parseCartesianOrDirection(entities, entity.args[2], [1, 0, 0])
        : [1, 0, 0];
    return { location, axis, refDir };
}
function vecDot(a, b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}
function vecCross(a, b) {
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ];
}
function vecNormalize(v) {
    const len = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    if (len < 1e-12)
        return [0, 0, 1];
    return [v[0] / len, v[1] / len, v[2] / len];
}
function getOrthonormalBasis(axis, refDir) {
    const z = vecNormalize(axis);
    const dot = vecDot(refDir, z);
    const proj = [
        refDir[0] - dot * z[0],
        refDir[1] - dot * z[1],
        refDir[2] - dot * z[2],
    ];
    const x = vecNormalize(proj);
    const y = vecCross(z, x);
    return [x, y, z];
}
function transformPoint(pt, origin, basis) {
    const [bx, by, bz] = basis;
    return [
        origin[0] + bx[0] * pt[0] + by[0] * pt[1] + bz[0] * pt[2],
        origin[1] + bx[1] * pt[0] + by[1] * pt[1] + bz[1] * pt[2],
        origin[2] + bx[2] * pt[0] + by[2] * pt[1] + bz[2] * pt[2],
    ];
}
function formatDxfLine(pt1, pt2) {
    return `  0
LINE
  8
0
 10
${pt1[0]}
 20
${pt1[1]}
 30
${pt1[2]}
 11
${pt2[0]}
 21
${pt2[1]}
 31
${pt2[2]}
`;
}
function resolvePolyLoop(entities, loopRef) {
    const loop = entities[loopRef.replace("#", "").trim()];
    if (!loop || loop.type !== "IFCPOLYLOOP" || loop.args.length < 1)
        return [];
    const pointRefs = loop.args[0]
        .replace(/[()]/g, "")
        .split(",")
        .map((s) => s.trim().replace("#", ""))
        .filter(Boolean);
    const pts = [];
    for (const ref of pointRefs) {
        pts.push(parseCartesianOrDirection(entities, "#" + ref, [0, 0, 0]));
    }
    return pts;
}
