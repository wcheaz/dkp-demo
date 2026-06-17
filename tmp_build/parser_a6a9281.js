"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseIfcToDxf = parseIfcToDxf;
exports.findProductLocalPlacementId = findProductLocalPlacementId;
exports.resolvePlacement3D = resolvePlacement3D;
exports.getOrthonormalBasis = getOrthonormalBasis;
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;
const PRODUCT_ENTITY_TYPES = new Set([
    "IFCMEMBER",
    "IFCWALLSTANDARDCASE",
    "IFCWALL",
    "IFCBEAM",
    "IFCCOLUMN",
    "IFCSLAB",
    "IFCROOF",
    "IFCFOOTING",
    "IFCCURTAINWALL",
]);
function argContainsEntityRef(arg, id) {
    const ref = `#${id}`;
    let idx = arg.indexOf(ref);
    while (idx !== -1) {
        const afterIdx = idx + ref.length;
        const nextChar = arg[afterIdx];
        if (!nextChar || !/[0-9]/.test(nextChar))
            return true;
        idx = arg.indexOf(ref, afterIdx);
    }
    return false;
}
function findEntityReferencingArg(entities, type, id) {
    for (const [entId, ent] of Object.entries(entities)) {
        if (ent.type === type && ent.args.some((a) => argContainsEntityRef(a, id))) {
            return entId;
        }
    }
    return null;
}
function parseDirectionVec3(entities, refRaw, fallback) {
    const cleaned = refRaw.replace("#", "").trim();
    if (!cleaned || cleaned === "$")
        return fallback;
    const ent = entities[cleaned];
    if (!ent || ent.type !== "IFCDIRECTION")
        return fallback;
    const coordsStr = ent.args[0].replace(/[()]/g, "");
    const coords = coordsStr.split(",").map((c) => parseFloat(c));
    return [coords[0] || 0, coords[1] || 0, coords[2] || 0];
}
function resolvePlacement3D(entities, axisPlacementId) {
    const placement = entities[axisPlacementId];
    if (!placement || placement.type !== "IFCAXIS2PLACEMENT3D")
        return null;
    let location = [0, 0, 0];
    const locRef = (placement.args[0] || "").replace("#", "").trim();
    if (locRef && locRef !== "$") {
        const loc = entities[locRef];
        if (loc && loc.type === "IFCCARTESIANPOINT") {
            const coordsStr = loc.args[0].replace(/[()]/g, "");
            const coords = coordsStr.split(",").map((c) => parseFloat(c));
            location = [coords[0] || 0, coords[1] || 0, coords[2] || 0];
        }
    }
    const axis = parseDirectionVec3(entities, placement.args[1] || "", [0, 0, 1]);
    const refDir = parseDirectionVec3(entities, placement.args[2] || "", [1, 0, 0]);
    return { location, axis, refDir };
}
function vecNormalize(v) {
    const len = Math.hypot(v[0], v[1], v[2]);
    if (len === 0)
        return [0, 0, 0];
    return [v[0] / len, v[1] / len, v[2] / len];
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
function vecSub(a, b) {
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}
function vecScale(a, s) {
    return [a[0] * s, a[1] * s, a[2] * s];
}
function getOrthonormalBasis(axis, refDir) {
    const z = vecNormalize(axis);
    const x = vecNormalize(vecSub(refDir, vecScale(z, vecDot(refDir, z))));
    const y = vecCross(z, x);
    return [x, y, z];
}
function transformPointByPlacement(point, placement) {
    const [x, y, z] = getOrthonormalBasis(placement.axis, placement.refDir);
    return [
        placement.location[0] + x[0] * point[0] + y[0] * point[1] + z[0] * point[2],
        placement.location[1] + x[1] * point[0] + y[1] * point[1] + z[1] * point[2],
        placement.location[2] + x[2] * point[0] + y[2] * point[1] + z[2] * point[2],
    ];
}
function findProductLocalPlacementId(entities, solidId) {
    const shapeRepId = findEntityReferencingArg(entities, "IFCSHAPEREPRESENTATION", solidId);
    if (shapeRepId === null)
        return null;
    const prodDefShapeId = findEntityReferencingArg(entities, "IFCPRODUCTDEFINITIONSHAPE", shapeRepId);
    if (prodDefShapeId === null)
        return null;
    for (const ent of Object.values(entities)) {
        if (PRODUCT_ENTITY_TYPES.has(ent.type) &&
            ent.args.some((a) => argContainsEntityRef(a, prodDefShapeId))) {
            const placementRef = (ent.args[5] || "").replace("#", "").trim();
            if (placementRef && placementRef !== "$")
                return placementRef;
            return null;
        }
    }
    return null;
}
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
                        const coords = coordsStr.split(",").map(c => parseFloat(c));
                        px = coords[0] || 0;
                        py = coords[1] || 0;
                    }
                }
                const solidPlacement = resolvePlacement3D(entities, positionId);
                let productPlacement = null;
                const productLocalPlacementId = findProductLocalPlacementId(entities, solidId);
                if (productLocalPlacementId) {
                    const productLocalPlacement = entities[productLocalPlacementId];
                    if (productLocalPlacement &&
                        productLocalPlacement.type === "IFCLOCALPLACEMENT") {
                        const productAxisPlacementId = (productLocalPlacement.args[1] || "")
                            .replace("#", "")
                            .trim();
                        if (productAxisPlacementId && productAxisPlacementId !== "$") {
                            productPlacement = resolvePlacement3D(entities, productAxisPlacementId);
                        }
                    }
                }
                const toGlobal = (localPoint) => {
                    let p = localPoint;
                    if (solidPlacement)
                        p = transformPointByPlacement(p, solidPlacement);
                    if (productPlacement)
                        p = transformPointByPlacement(p, productPlacement);
                    return p;
                };
                const xMin = px - xDim / 2;
                const xMax = px + xDim / 2;
                const yMin = py - yDim / 2;
                const yMax = py + yDim / 2;
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
                const globalVerts = localVerts.map(toGlobal);
                const v1 = globalVerts[0];
                const v2 = globalVerts[1];
                const v3 = globalVerts[2];
                const v4 = globalVerts[3];
                const v5 = globalVerts[4];
                const v6 = globalVerts[5];
                const v7 = globalVerts[6];
                const v8 = globalVerts[7];
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
