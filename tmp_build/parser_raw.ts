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
            const coords = coordsStr.split(",").map((c) => parseFloat(c));
            px = coords[0] || 0;
            py = coords[1] || 0;
          }
        }

        const solidPlacement = resolvePlacement3D(entities, positionId);
        const solidBasis = solidPlacement
          ? getOrthonormalBasis(solidPlacement.axis, solidPlacement.refDir)
          : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
        const solidOrigin: Vec3 = solidPlacement
          ? solidPlacement.location
          : [0, 0, 0];

        const productPlacementId = findProductLocalPlacementId(
          entities,
          solidId
        );
        const productPlacement = productPlacementId
          ? resolvePlacement3D(entities, productPlacementId)
          : null;
        const productBasis = productPlacement
          ? getOrthonormalBasis(productPlacement.axis, productPlacement.refDir)
          : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
        const productOrigin: Vec3 = productPlacement
          ? productPlacement.location
          : [0, 0, 0];

        const xMin = px - xDim / 2;
        const xMax = px + xDim / 2;
        const yMin = py - yDim / 2;
        const yMax = py + yDim / 2;

        // Profile corners in the solid's local coordinate system.
        // Bottom face sits at z=0; top face is extruded by depth along local Z.
        const localVerts: Vec3[] = [
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
        const verts: Vec3[] = localVerts.map((v) => {
          const inSolidFrame = transformPoint(v, solidOrigin, solidBasis);
          return transformPoint(inSolidFrame, productOrigin, productBasis);
        });

        const addLine = (pt1: Vec3, pt2: Vec3) => {
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
      } else if (sweptArea.type === "IFCARBITRARYCLOSEDPROFILEDEF") {
        // Arbitrary closed profile: resolve the polyline path defined by an
        // IFCCOMPOSITECURVE (or a direct IFCPOLYLINE) and sweep the 2D loop
        // along the local extrusion axis by the solid depth.
        if (sweptArea.args.length < 3) continue;
        const profilePts = resolveCompositeCurvePoints(
          entities,
          sweptArea.args[2]
        );
        if (profilePts.length < 2) continue;

        const solidPlacement = resolvePlacement3D(entities, positionId);
        const solidBasis = solidPlacement
          ? getOrthonormalBasis(solidPlacement.axis, solidPlacement.refDir)
          : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
        const solidOrigin: Vec3 = solidPlacement
          ? solidPlacement.location
          : [0, 0, 0];

        const productPlacementId = findProductLocalPlacementId(
          entities,
          solidId
        );
        const productPlacement = productPlacementId
          ? resolvePlacement3D(entities, productPlacementId)
          : null;
        const productBasis = productPlacement
          ? getOrthonormalBasis(productPlacement.axis, productPlacement.refDir)
          : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
        const productOrigin: Vec3 = productPlacement
          ? productPlacement.location
          : [0, 0, 0];

        // Bottom face sits at local Z=0; top face is swept by depth.
        const projectLoop = (zOffset: number): Vec3[] =>
          profilePts.map((p) => {
            const local: Vec3 = [p[0], p[1], zOffset];
            const inSolid = transformPoint(local, solidOrigin, solidBasis);
            return transformPoint(inSolid, productOrigin, productBasis);
          });

        const bottom = projectLoop(0);
        const top = projectLoop(depth);
        const n = bottom.length;

        for (let i = 0; i < n; i++) {
          dxfEntities += formatDxfLine(bottom[i], bottom[(i + 1) % n]);
        }
        for (let i = 0; i < n; i++) {
          dxfEntities += formatDxfLine(top[i], top[(i + 1) % n]);
        }
        for (let i = 0; i < n; i++) {
          dxfEntities += formatDxfLine(bottom[i], top[i]);
        }
      }
    } catch (err) {
      console.error("Error parsing solid geometry:", err);
    }
  }

  // B-Rep geometry: IFCFACETEDBREP -> IFCCLOSEDSHELL -> IFCFACE ->
  // IFCFACEOUTERBOUND/IFCFACEBOUND -> IFCPOLYLOOP -> IFCCARTESIANPOINT.
  // Each polyloop edge becomes a DXF LINE so Pamir B-Rep meshes render as
  // a wireframe without a client-side solid kernel.
  const brepSolids = Object.entries(entities).filter(
    ([, ent]) => ent.type === "IFCFACETEDBREP"
  );

  for (const [brepId, brep] of brepSolids) {
    try {
      if (brep.args.length < 1) continue;
      const closedShellId = brep.args[0].replace("#", "").trim();
      const closedShell = entities[closedShellId];
      if (
        !closedShell ||
        (closedShell.type !== "IFCCLOSEDSHELL" &&
          closedShell.type !== "IFCOPENSHELL")
      )
        continue;

      const faceRefs = closedShell.args[0]
        .replace(/[()]/g, "")
        .split(",")
        .map((s) => s.trim().replace("#", ""))
        .filter(Boolean);

      const productPlacementId = findProductLocalPlacementId(
        entities,
        brepId
      );
      const productPlacement = productPlacementId
        ? resolvePlacement3D(entities, productPlacementId)
        : null;
      const productBasis = productPlacement
        ? getOrthonormalBasis(productPlacement.axis, productPlacement.refDir)
        : getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
      const productOrigin: Vec3 = productPlacement
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
          if (
            !bound ||
            (bound.type !== "IFCFACEOUTERBOUND" &&
              bound.type !== "IFCFACEBOUND")
          )
            continue;
          const pts = resolvePolyLoop(entities, bound.args[0]);
          if (pts.length < 2) continue;
          const verts = pts.map((v) =>
            transformPoint(v, productOrigin, productBasis)
          );
          for (let i = 0; i < verts.length; i++) {
            const a = verts[i];
            const b = verts[(i + 1) % verts.length];
            dxfEntities += formatDxfLine(a, b);
          }
        }
      }
    } catch (err) {
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

type IfcEntity = { type: string; args: string[] };
type Vec3 = [number, number, number];
interface Placement3D {
  location: Vec3;
  axis: Vec3;
  refDir: Vec3;
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

function parseCartesianOrDirection(
  entities: Record<string, IfcEntity>,
  ref: string,
  fallback: Vec3
): Vec3 {
  const id = ref.replace("#", "").trim();
  const entity = entities[id];
  if (
    !entity ||
    (entity.type !== "IFCCARTESIANPOINT" && entity.type !== "IFCDIRECTION")
  ) {
    return fallback;
  }
  const coordsStr = entity.args[0].replace(/[()]/g, "");
  const coords = coordsStr.split(",").map((c) => parseFloat(c));
  return [coords[0] || 0, coords[1] || 0, coords[2] || 0];
}

function findProductLocalPlacementId(
  entities: Record<string, IfcEntity>,
  solidId: string
): string | null {
  let shapeRepId: string | null = null;
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
  if (shapeRepId === null) return null;

  let productDefShapeId: string | null = null;
  for (const [id, entity] of Object.entries(entities)) {
    if (
      entity.type === "IFCPRODUCTDEFINITIONSHAPE" &&
      entity.args.length >= 1
    ) {
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
  if (productDefShapeId === null) return null;

  for (const entity of Object.values(entities)) {
    if (
      PRODUCT_ENTITY_TYPES.has(entity.type) &&
      entity.args.length >= 7
    ) {
      const repRef = entity.args[6].replace("#", "");
      if (repRef === productDefShapeId) {
        return entity.args[5].replace("#", "");
      }
    }
  }
  return null;
}

// Parse a bare IFCAXIS2PLACEMENT3D entity into a LOCAL Placement3D frame
// (location + axis + refDir), without walking any parent placement chain.
function parseAxis2Placement3D(
  entities: Record<string, IfcEntity>,
  placementId: string
): Placement3D | null {
  const entity = entities[placementId];
  if (!entity || entity.type !== "IFCAXIS2PLACEMENT3D") return null;

  const location = parseCartesianOrDirection(entities, entity.args[0], [
    0,
    0,
    0,
  ]);
  const axis: Vec3 =
    entity.args.length > 1 && entity.args[1] && entity.args[1] !== "$"
      ? parseCartesianOrDirection(entities, entity.args[1], [0, 0, 1])
      : [0, 0, 1];
  const refDir: Vec3 =
    entity.args.length > 2 && entity.args[2] && entity.args[2] !== "$"
      ? parseCartesianOrDirection(entities, entity.args[2], [1, 0, 0])
      : [1, 0, 0];

  return { location, axis, refDir };
}

// Recursively resolves an IFCLOCALPLACEMENT (or bare IFCAXIS2PLACEMENT3D) into
// an ABSOLUTE Placement3D frame by walking the PlacementRelTo parent chain and
// accumulating nested coordinate transforms via matrix multiplication:
//   M_global = M_parent * M_local
// The `visited` set guards against malformed cyclic placement graphs: a repeat
// reference short-circuits to null instead of recursing forever.
function resolvePlacement3D(
  entities: Record<string, IfcEntity>,
  placementId: string,
  visited: Set<string> = new Set()
): Placement3D | null {
  const id = placementId.replace("#", "").trim();
  if (!id || visited.has(id)) return null;
  visited.add(id);

  const entity = entities[id];
  if (!entity) return null;

  // A bare IFCAXIS2PLACEMENT3D has no parent chain — return its local frame.
  if (entity.type === "IFCAXIS2PLACEMENT3D") {
    return parseAxis2Placement3D(entities, id);
  }

  if (entity.type !== "IFCLOCALPLACEMENT") return null;
  if (entity.args.length < 2) return null;

  // IFCLOCALPLACEMENT args: (PlacementRelTo, RelativePlacement).
  // PlacementRelTo (args[0]) is optional and "$" when this is the storey root.
  const parentRef =
    entity.args[0] && entity.args[0] !== "$"
      ? entity.args[0].replace("#", "").trim()
      : null;
  const relativeRef = entity.args[1].replace("#", "").trim();

  const localFrame = parseAxis2Placement3D(entities, relativeRef);
  if (!localFrame) return null;
  if (!parentRef) return localFrame;

  const parentFrame = resolvePlacement3D(entities, "#" + parentRef, visited);
  if (!parentFrame) return localFrame;

  return combinePlacements(parentFrame, localFrame);
}

// Combines a parent Placement3D frame with a child Placement3D frame to produce
// the child's absolute frame (M_parent * M_local), expressed back as a
// Placement3D: axis = combined Z column, refDir = combined X column, and
// location = parent origin plus the rotated child translation.
function combinePlacements(
  parent: Placement3D,
  child: Placement3D
): Placement3D {
  const [px, py, pz] = getOrthonormalBasis(parent.axis, parent.refDir);
  const [cx, , cz] = getOrthonormalBasis(child.axis, child.refDir);

  const rotateIntoParent = (v: Vec3): Vec3 => [
    px[0] * v[0] + py[0] * v[1] + pz[0] * v[2],
    px[1] * v[0] + py[1] * v[1] + pz[1] * v[2],
    px[2] * v[0] + py[2] * v[1] + pz[2] * v[2],
  ];

  const combinedAxis = rotateIntoParent(cz);
  const combinedRefDir = rotateIntoParent(cx);
  const localOffset = rotateIntoParent(child.location);
  const combinedLocation: Vec3 = [
    parent.location[0] + localOffset[0],
    parent.location[1] + localOffset[1],
    parent.location[2] + localOffset[2],
  ];

  return { location: combinedLocation, axis: combinedAxis, refDir: combinedRefDir };
}

function vecDot(a: Vec3, b: Vec3): number {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function vecCross(a: Vec3, b: Vec3): Vec3 {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0],
  ];
}

function vecNormalize(v: Vec3): Vec3 {
  const len = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
  if (len < 1e-12) return [0, 0, 1];
  return [v[0] / len, v[1] / len, v[2] / len];
}

function getOrthonormalBasis(axis: Vec3, refDir: Vec3): [Vec3, Vec3, Vec3] {
  const z = vecNormalize(axis);
  const dot = vecDot(refDir, z);
  const proj: Vec3 = [
    refDir[0] - dot * z[0],
    refDir[1] - dot * z[1],
    refDir[2] - dot * z[2],
  ];
  const x = vecNormalize(proj);
  const y = vecCross(z, x);
  return [x, y, z];
}

function transformPoint(
  pt: Vec3,
  origin: Vec3,
  basis: [Vec3, Vec3, Vec3]
): Vec3 {
  const [bx, by, bz] = basis;
  return [
    origin[0] + bx[0] * pt[0] + by[0] * pt[1] + bz[0] * pt[2],
    origin[1] + bx[1] * pt[0] + by[1] * pt[1] + bz[1] * pt[2],
    origin[2] + bx[2] * pt[0] + by[2] * pt[1] + bz[2] * pt[2],
  ];
}

function formatDxfLine(pt1: Vec3, pt2: Vec3): string {
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

function resolvePolyLoop(
  entities: Record<string, IfcEntity>,
  loopRef: string
): Vec3[] {
  const loop = entities[loopRef.replace("#", "").trim()];
  if (!loop || loop.type !== "IFCPOLYLOOP" || loop.args.length < 1) return [];
  const pointRefs = loop.args[0]
    .replace(/[()]/g, "")
    .split(",")
    .map((s) => s.trim().replace("#", ""))
    .filter(Boolean);
  const pts: Vec3[] = [];
  for (const ref of pointRefs) {
    pts.push(parseCartesianOrDirection(entities, "#" + ref, [0, 0, 0]));
  }
  return pts;
}

// Resolves an IFCARBITRARYCLOSEDPROFILEDEF outer curve into an ordered list of
// 2D polygon vertices (with z=0). Supports IFCCOMPOSITECURVE (traversing each
// IFCCOMPOSITECURVESEGMENT's parent IFCPOLYLINE) and direct IFCPOLYLINE paths.
// Shared segment endpoints are deduplicated and the implicit closing vertex is
// dropped so the returned loop is a minimal closed polygon.
function resolveCompositeCurvePoints(
  entities: Record<string, IfcEntity>,
  curveRef: string
): Vec3[] {
  const curveId = curveRef.replace("#", "").trim();
  const curve = entities[curveId];
  if (!curve) return [];

  const pts: Vec3[] = [];
  const samePoint = (a: Vec3, b: Vec3): boolean =>
    Math.abs(a[0] - b[0]) < 1e-6 &&
    Math.abs(a[1] - b[1]) < 1e-6 &&
    Math.abs(a[2] - b[2]) < 1e-6;

  const collectPolyline = (polylineRef: string): Vec3[] => {
    const pl = entities[polylineRef.replace("#", "").trim()];
    if (!pl || pl.type !== "IFCPOLYLINE" || pl.args.length < 1) return [];
    const refs = pl.args[0]
      .replace(/[()]/g, "")
      .split(",")
      .map((s) => s.trim().replace("#", ""))
      .filter(Boolean);
    const out: Vec3[] = [];
    for (const r of refs) {
      out.push(parseCartesianOrDirection(entities, "#" + r, [0, 0, 0]));
    }
    return out;
  };

  if (curve.type === "IFCPOLYLINE") {
    pts.push(...collectPolyline("#" + curveId));
  } else if (curve.type === "IFCCOMPOSITECURVE") {
    const segRefs = curve.args[0]
      .replace(/[()]/g, "")
      .split(",")
      .map((s) => s.trim().replace("#", ""))
      .filter(Boolean);
    for (const segRef of segRefs) {
      const seg = entities[segRef];
      if (!seg) continue;
      let parentRef: string;
      if (seg.type === "IFCCOMPOSITECURVESEGMENT" && seg.args.length >= 3) {
        parentRef = seg.args[2];
      } else {
        parentRef = "#" + segRef;
      }
      const segPts = collectPolyline(parentRef);
      for (const p of segPts) {
        if (pts.length === 0 || !samePoint(p, pts[pts.length - 1])) {
          pts.push(p);
        }
      }
    }
  }

  // Drop a trailing duplicate of the first point so the loop is implicit.
  if (pts.length >= 2 && samePoint(pts[0], pts[pts.length - 1])) {
    pts.pop();
  }
  return pts;
}


export { parseIfcToDxf, findProductLocalPlacementId, resolvePlacement3D, getOrthonormalBasis, resolvePolyLoop, resolveCompositeCurvePoints };