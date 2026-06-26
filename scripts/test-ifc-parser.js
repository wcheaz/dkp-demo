const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const pageContent = fs.readFileSync(path.join(__dirname, '../src/app/cad-viewer-3d/page.tsx'), 'utf8');

const startMarker = 'const MAX_FILE_SIZE_BYTES';
const endMarker = 'export default function CadViewer3DPage';
const startIdx = pageContent.indexOf(startMarker);
const endIdx = pageContent.indexOf(endMarker);

if (startIdx === -1 || endIdx === -1) {
  console.error("Could not locate parser code block");
  process.exit(1);
}

const functionCode = pageContent.slice(startIdx, endIdx);

// Create tmp_build directory
const tmpBuildDir = path.join(__dirname, '../tmp_build');
if (!fs.existsSync(tmpBuildDir)) {
  fs.mkdirSync(tmpBuildDir, { recursive: true });
}

// Identify functions present in the code and export them
const exportsList = ['parseIfcToDxf'];
if (functionCode.includes('findProductLocalPlacementId')) exportsList.push('findProductLocalPlacementId');
if (functionCode.includes('resolvePlacement3D')) exportsList.push('resolvePlacement3D');
if (functionCode.includes('getOrthonormalBasis')) exportsList.push('getOrthonormalBasis');
if (functionCode.includes('resolvePolyLoop')) exportsList.push('resolvePolyLoop');
if (functionCode.includes('resolveCompositeCurvePoints')) exportsList.push('resolveCompositeCurvePoints');

const exportStatement = `\nexport { ${exportsList.join(', ')} };`;

// Write to parser_raw.ts
fs.writeFileSync(path.join(tmpBuildDir, 'parser_raw.ts'), functionCode + exportStatement, 'utf8');

// Compile using tsc
try {
  execSync('npx tsc --target es2020 --module commonjs --skipLibCheck true tmp_build/parser_raw.ts', {
    cwd: path.join(__dirname, '..'),
    stdio: 'pipe'
  });
} catch (err) {
  console.error("Compilation error:");
  console.error(err.stdout ? err.stdout.toString() : '');
  console.error(err.stderr ? err.stderr.toString() : err.message);
  process.exit(1);
}

// Require the compiled JS module
const parserModulePath = path.join(tmpBuildDir, 'parser_raw.js');
const parser = require(parserModulePath);

const ifcPath = path.join(__dirname, '../generated/gable.ifc');
if (!fs.existsSync(ifcPath)) {
  console.error(`IFC file not found at ${ifcPath}`);
  process.exit(1);
}

const ifcText = fs.readFileSync(ifcPath, 'utf8');

// Helper to check vector equality
function vecEquals(v1, v2, tol = 1e-4) {
  if (v1.length !== v2.length) return false;
  for (let i = 0; i < v1.length; i++) {
    if (Math.abs(v1[i] - v2[i]) > tol) return false;
  }
  return true;
}

// Phase 1: Verify parsing helpers if implemented
if (parser.resolvePlacement3D) {
  console.log("Testing resolvePlacement3D...");
  // Test resolvePlacement3D with mock entities
  const mockEntities = {
    '1': { type: 'IFCAXIS2PLACEMENT3D', args: ['#2', '#3', '#4'] },
    '2': { type: 'IFCCARTESIANPOINT', args: ['(10.0, 20.0, 30.0)'] },
    '3': { type: 'IFCDIRECTION', args: ['(0.0, 0.0, 1.0)'] },
    '4': { type: 'IFCDIRECTION', args: ['(1.0, 0.0, 0.0)'] }
  };
  const res = parser.resolvePlacement3D(mockEntities, '1');
  if (!res || !vecEquals(res.location, [10, 20, 30]) || !vecEquals(res.axis, [0, 0, 1]) || !vecEquals(res.refDir, [1, 0, 0])) {
    console.error("FAIL: resolvePlacement3D did not parse expected location/axis/refDir", res);
    process.exit(1);
  }
  console.log("SUCCESS: resolvePlacement3D basic tests passed.");

  // Recursive placement: an IFCLOCALPLACEMENT with a PlacementRelTo parent must
  // accumulate the parent translation into the absolute frame. With identity
  // rotations, the combined location is simply parent + child offsets.
  const nestedEntities = {
    '1': { type: 'IFCLOCALPLACEMENT', args: ['$', '#2'] },
    '2': { type: 'IFCAXIS2PLACEMENT3D', args: ['#5', '#6', '#7'] },
    '5': { type: 'IFCCARTESIANPOINT', args: ['(100.0,200.0,0.0)'] },
    '6': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '7': { type: 'IFCDIRECTION', args: ['(1.0,0.0,0.0)'] },
    // Member placement nested inside assembly #1 via PlacementRelTo.
    '10': { type: 'IFCLOCALPLACEMENT', args: ['#1', '#11'] },
    '11': { type: 'IFCAXIS2PLACEMENT3D', args: ['#15', '#16', '#17'] },
    '15': { type: 'IFCCARTESIANPOINT', args: ['(10.0,20.0,30.0)'] },
    '16': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '17': { type: 'IFCDIRECTION', args: ['(1.0,0.0,0.0)'] }
  };
  const nestedRes = parser.resolvePlacement3D(nestedEntities, '10');
  if (
    !nestedRes ||
    !vecEquals(nestedRes.location, [110, 220, 30]) ||
    !vecEquals(nestedRes.axis, [0, 0, 1]) ||
    !vecEquals(nestedRes.refDir, [1, 0, 0])
  ) {
    console.error("FAIL: recursive placement did not combine translations", nestedRes);
    process.exit(1);
  }
  console.log("SUCCESS: recursive placement combined nested translations.");

  // Deep chain: storey -> assembly -> member. Translations must accumulate
  // across every level down to the storey root.
  const deepEntities = {
    '100': { type: 'IFCLOCALPLACEMENT', args: ['$', '#101'] },
    '101': { type: 'IFCAXIS2PLACEMENT3D', args: ['#105', '#106', '#107'] },
    '105': { type: 'IFCCARTESIANPOINT', args: ['(0.0,0.0,0.0)'] },
    '106': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '107': { type: 'IFCDIRECTION', args: ['(1.0,0.0,0.0)'] },
    '110': { type: 'IFCLOCALPLACEMENT', args: ['#100', '#111'] },
    '111': { type: 'IFCAXIS2PLACEMENT3D', args: ['#115', '#116', '#117'] },
    '115': { type: 'IFCCARTESIANPOINT', args: ['(1000.0,0.0,0.0)'] },
    '116': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '117': { type: 'IFCDIRECTION', args: ['(1.0,0.0,0.0)'] },
    '120': { type: 'IFCLOCALPLACEMENT', args: ['#110', '#121'] },
    '121': { type: 'IFCAXIS2PLACEMENT3D', args: ['#125', '#126', '#127'] },
    '125': { type: 'IFCCARTESIANPOINT', args: ['(0.0,500.0,300.0)'] },
    '126': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '127': { type: 'IFCDIRECTION', args: ['(1.0,0.0,0.0)'] }
  };
  const deepRes = parser.resolvePlacement3D(deepEntities, '120');
  if (!deepRes || !vecEquals(deepRes.location, [1000, 500, 300])) {
    console.error("FAIL: deep placement chain did not accumulate translations", deepRes);
    process.exit(1);
  }
  console.log("SUCCESS: deep placement chain accumulated translations.");

  // Rotated parent: a parent rotated 90 deg about Z must rotate the child's
  // local offset and basis into the parent frame (child X -> parent Y).
  const rotatedEntities = {
    '200': { type: 'IFCLOCALPLACEMENT', args: ['$', '#201'] },
    '201': { type: 'IFCAXIS2PLACEMENT3D', args: ['#205', '#206', '#207'] },
    '205': { type: 'IFCCARTESIANPOINT', args: ['(0.0,0.0,0.0)'] },
    '206': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '207': { type: 'IFCDIRECTION', args: ['(0.0,1.0,0.0)'] },
    '210': { type: 'IFCLOCALPLACEMENT', args: ['#200', '#211'] },
    '211': { type: 'IFCAXIS2PLACEMENT3D', args: ['#215', '#216', '#217'] },
    '215': { type: 'IFCCARTESIANPOINT', args: ['(10.0,0.0,0.0)'] },
    '216': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '217': { type: 'IFCDIRECTION', args: ['(1.0,0.0,0.0)'] }
  };
  const rotRes = parser.resolvePlacement3D(rotatedEntities, '210');
  if (
    !rotRes ||
    !vecEquals(rotRes.location, [0, 10, 0]) ||
    !vecEquals(rotRes.axis, [0, 0, 1]) ||
    !vecEquals(rotRes.refDir, [0, 1, 0])
  ) {
    console.error("FAIL: rotated parent placement did not transform child frame", rotRes);
    process.exit(1);
  }
  console.log("SUCCESS: rotated parent placement transformed child frame.");

  // Cycle guard: a self-referential PlacementRelTo must terminate (return null
  // or a frame) rather than blow the stack with infinite recursion.
  const cyclicEntities = {
    '300': { type: 'IFCLOCALPLACEMENT', args: ['#300', '#301'] },
    '301': { type: 'IFCAXIS2PLACEMENT3D', args: ['#305', '#306', '#307'] },
    '305': { type: 'IFCCARTESIANPOINT', args: ['(1.0,2.0,3.0)'] },
    '306': { type: 'IFCDIRECTION', args: ['(0.0,0.0,1.0)'] },
    '307': { type: 'IFCDIRECTION', args: ['(1.0,0.0,0.0)'] }
  };
  let cyclicOk = true;
  try {
    const cyclicRes = parser.resolvePlacement3D(cyclicEntities, '300');
    if (cyclicRes === null) cyclicOk = true;
    else if (!vecEquals(cyclicRes.location, [1, 2, 3])) cyclicOk = false;
  } catch (e) {
    cyclicOk = false;
    console.error("FAIL: cyclic placement threw instead of terminating", e);
  }
  if (!cyclicOk) {
    console.error("FAIL: cyclic placement did not terminate safely");
    process.exit(1);
  }
  console.log("SUCCESS: cyclic placement terminated safely.");
}

// Phase 2: Verify math helpers if implemented
if (parser.getOrthonormalBasis) {
  console.log("Testing getOrthonormalBasis...");
  // Test basic identity basis
  const basis1 = parser.getOrthonormalBasis([0, 0, 1], [1, 0, 0]);
  if (!basis1 || !vecEquals(basis1[0], [1, 0, 0]) || !vecEquals(basis1[1], [0, 1, 0]) || !vecEquals(basis1[2], [0, 0, 1])) {
    console.error("FAIL: getOrthonormalBasis identity case failed", basis1);
    process.exit(1);
  }
  
  // Test sloped rafter basis case
  // E.g. Axis (Z-axis of rafter) is sloped, say (0.866025, 0, 0.5)
  // RefDir (X-axis approximation) is (0.5, 0, -0.866025)
  const axis = [0.866025, 0, 0.5];
  const refDir = [0.5, 0, -0.866025];
  const basis2 = parser.getOrthonormalBasis(axis, refDir);
  
  // Assert orthogonality: dot products should be 0
  const dot = (a, b) => a.reduce((sum, val, idx) => sum + val * b[idx], 0);
  const x = basis2[0];
  const y = basis2[1];
  const z = basis2[2];
  if (Math.abs(dot(x, y)) > 1e-4 || Math.abs(dot(x, z)) > 1e-4 || Math.abs(dot(y, z)) > 1e-4) {
    console.error("FAIL: getOrthonormalBasis did not produce orthogonal vectors", basis2);
    process.exit(1);
  }
  console.log("SUCCESS: getOrthonormalBasis math tests passed.");
}

// Phase 3: Run full integration parse
try {
  const dxfText = parser.parseIfcToDxf(ifcText);
  console.log("SUCCESS: Parsed IFC to DXF successfully.");
  console.log(`DXF line count: ${dxfText.split('\n').length}`);
  
  if (!dxfText.includes('SECTION') || !dxfText.includes('ENTITIES')) {
    console.error("FAIL: DXF output is missing standard sections");
    process.exit(1);
  }

  // Verify the output contains true 3D coordinates (non-zero Z components).
  // DXF stores entity vertices as alternating group-code/value lines; group
  // codes 30 and 31 are the start/end Z of a LINE entity.
  const dxfLines = dxfText.split('\n');
  let hasNonZeroZ = false;
  for (let i = 0; i < dxfLines.length - 1; i++) {
    const code = dxfLines[i].trim();
    if (code === '30' || code === '31') {
      const zVal = parseFloat(dxfLines[i + 1]);
      if (Number.isFinite(zVal) && Math.abs(zVal) > 1e-6) {
        hasNonZeroZ = true;
        break;
      }
    }
  }
  if (!hasNonZeroZ) {
    console.error("FAIL: Output DXF does not contain any non-zero Z coordinates");
    process.exit(1);
  }
  console.log("SUCCESS: Output DXF contains true 3D coordinates.");
} catch (e) {
  console.error("FAIL: Exception thrown during parsing", e);
  process.exit(1);
}

// Phase 4: Verify B-Rep (IFCFACETEDBREP / IFCCLOSEDSHELL) parsing
if (parser.resolvePolyLoop) {
  console.log("Testing resolvePolyLoop...");
  const brepEntities = {
    '5': { type: 'IFCPOLYLOOP', args: ['(#6,#7,#8)'] },
    '6': { type: 'IFCCARTESIANPOINT', args: ['(0.0,0.0,0.0)'] },
    '7': { type: 'IFCCARTESIANPOINT', args: ['(2.0,0.0,0.0)'] },
    '8': { type: 'IFCCARTESIANPOINT', args: ['(2.0,3.0,0.0)'] }
  };
  const loopPts = parser.resolvePolyLoop(brepEntities, '#5');
  if (
    loopPts.length !== 3 ||
    !vecEquals(loopPts[0], [0, 0, 0]) ||
    !vecEquals(loopPts[1], [2, 0, 0]) ||
    !vecEquals(loopPts[2], [2, 3, 0])
  ) {
    console.error("FAIL: resolvePolyLoop did not extract expected vertices", loopPts);
    process.exit(1);
  }
  // Non-polyloop / malformed refs must return empty arrays, not throw.
  if (parser.resolvePolyLoop(brepEntities, '#999').length !== 0) {
    console.error("FAIL: resolvePolyLoop did not handle missing loop ref");
    process.exit(1);
  }
  console.log("SUCCESS: resolvePolyLoop extracted polyloop vertices.");
}

console.log("Testing IFCFACETEDBREP parsing...");
const brepIfc = [
  '#1 = IFCFACETEDBREP(#2);',
  '#2 = IFCCLOSEDSHELL((#3));',
  '#3 = IFCFACE((#4));',
  '#4 = IFCFACEOUTERBOUND(#5,.T.);',
  '#5 = IFCPOLYLOOP((#6,#7,#8));',
  '#6 = IFCCARTESIANPOINT((0.0,0.0,0.0));',
  '#7 = IFCCARTESIANPOINT((5.0,0.0,0.0));',
  '#8 = IFCCARTESIANPOINT((5.0,5.0,0.0));'
].join('\n');
try {
  const brepDxf = parser.parseIfcToDxf(brepIfc);
  const brepLineCount = (brepDxf.match(/^LINE$/gm) || []).length;
  // A triangle polyloop yields 3 closed-loop edges.
  if (brepLineCount < 3) {
    console.error(`FAIL: B-Rep parse produced ${brepLineCount} LINE entities, expected at least 3`);
    process.exit(1);
  }
  // Collect X coordinates (group code 10) and verify the triangle vertices survived.
  const brepXCoords = new Set();
  const brepDxfLines = brepDxf.split('\n');
  for (let i = 0; i < brepDxfLines.length - 1; i++) {
    if (brepDxfLines[i].trim() === '10') {
      brepXCoords.add(parseFloat(brepDxfLines[i + 1]));
    }
  }
  if (!brepXCoords.has(0) || !brepXCoords.has(5)) {
    console.error("FAIL: B-Rep DXF output missing expected X coordinates (0 and 5)", Array.from(brepXCoords));
    process.exit(1);
  }
  console.log(`SUCCESS: B-Rep parse produced ${brepLineCount} LINE entities with expected vertices.`);
} catch (e) {
  console.error("FAIL: Exception thrown during B-Rep parsing", e);
  process.exit(1);
}

// Phase 5: Verify arbitrary closed profile (IFCARBITRARYCLOSEDPROFILEDEF +
// IFCCOMPOSITECURVE) parsing.
if (parser.resolveCompositeCurvePoints) {
  console.log("Testing resolveCompositeCurvePoints...");
  const profEntities = {
    '20': { type: 'IFCCOMPOSITECURVE', args: ['(#21,#22,#23,#24)', '.F.'] },
    '21': { type: 'IFCCOMPOSITECURVESEGMENT', args: ['.CONTINUOUS.', '.T.', '#30'] },
    '22': { type: 'IFCCOMPOSITECURVESEGMENT', args: ['.CONTINUOUS.', '.T.', '#31'] },
    '23': { type: 'IFCCOMPOSITECURVESEGMENT', args: ['.CONTINUOUS.', '.T.', '#32'] },
    '24': { type: 'IFCCOMPOSITECURVESEGMENT', args: ['.CONTINUOUS.', '.T.', '#33'] },
    '30': { type: 'IFCPOLYLINE', args: ['(#40,#41)'] },
    '31': { type: 'IFCPOLYLINE', args: ['(#41,#42)'] },
    '32': { type: 'IFCPOLYLINE', args: ['(#42,#43)'] },
    '33': { type: 'IFCPOLYLINE', args: ['(#43,#40)'] },
    '40': { type: 'IFCCARTESIANPOINT', args: ['(0.0,0.0)'] },
    '41': { type: 'IFCCARTESIANPOINT', args: ['(5000.0,0.0)'] },
    '42': { type: 'IFCCARTESIANPOINT', args: ['(5000.0,200.0)'] },
    '43': { type: 'IFCCARTESIANPOINT', args: ['(0.0,200.0)'] }
  };
  const cpts = parser.resolveCompositeCurvePoints(profEntities, '#20');
  if (cpts.length !== 4) {
    console.error(`FAIL: resolveCompositeCurvePoints returned ${cpts.length} points, expected 4`, cpts);
    process.exit(1);
  }
  if (
    !vecEquals(cpts[0], [0, 0, 0]) ||
    !vecEquals(cpts[1], [5000, 0, 0]) ||
    !vecEquals(cpts[2], [5000, 200, 0]) ||
    !vecEquals(cpts[3], [0, 200, 0])
  ) {
    console.error("FAIL: resolveCompositeCurvePoints did not produce expected closed loop", cpts);
    process.exit(1);
  }
  // Missing / malformed refs must return empty arrays, not throw.
  if (parser.resolveCompositeCurvePoints(profEntities, '#999').length !== 0) {
    console.error("FAIL: resolveCompositeCurvePoints did not handle missing curve ref");
    process.exit(1);
  }
  console.log("SUCCESS: resolveCompositeCurvePoints built closed polygon loop.");
}

console.log("Testing IFCARBITRARYCLOSEDPROFILEDEF parsing...");
const profIfc = [
  '#10 = IFCEXTRUDEDAREASOLID(#11,#12,#13,1000.0);',
  '#11 = IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#20);',
  '#12 = IFCAXIS2PLACEMENT3D(#14,$,$);',
  "#13 = IFCDIRECTION((0.0,0.0,1.0));",
  "#14 = IFCCARTESIANPOINT((0.0,0.0,0.0));",
  "#20 = IFCCOMPOSITECURVE((#21,#22,#23,#24),.F.);",
  "#21 = IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#30);",
  "#22 = IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#31);",
  "#23 = IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#32);",
  "#24 = IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#33);",
  "#30 = IFCPOLYLINE((#40,#41));",
  "#31 = IFCPOLYLINE((#41,#42));",
  "#32 = IFCPOLYLINE((#42,#43));",
  "#33 = IFCPOLYLINE((#43,#40));",
  "#40 = IFCCARTESIANPOINT((0.0,0.0));",
  "#41 = IFCCARTESIANPOINT((5000.0,0.0));",
  "#42 = IFCCARTESIANPOINT((5000.0,200.0));",
  "#43 = IFCCARTESIANPOINT((0.0,200.0));"
].join("\n");
try {
  const profDxf = parser.parseIfcToDxf(profIfc);
  const profLineCount = (profDxf.match(/^LINE$/gm) || []).length;
  // A 4-vertex swept loop yields 4 bottom + 4 top + 4 vertical edges = 12.
  if (profLineCount < 12) {
    console.error(`FAIL: Arbitrary profile parse produced ${profLineCount} LINE entities, expected at least 12`);
    process.exit(1);
  }
  // Collect X (group code 10) and Z (group code 30) coordinates and verify the
  // swept profile vertices survived the extrusion.
  const profXCoords = new Set();
  const profZCoords = new Set();
  const profDxfLines = profDxf.split('\n');
  for (let i = 0; i < profDxfLines.length - 1; i++) {
    const code = profDxfLines[i].trim();
    if (code === '10') {
      profXCoords.add(parseFloat(profDxfLines[i + 1]));
    } else if (code === '30') {
      profZCoords.add(parseFloat(profDxfLines[i + 1]));
    }
  }
  if (!profXCoords.has(0) || !profXCoords.has(5000)) {
    console.error("FAIL: Arbitrary profile DXF output missing expected X coordinates (0 and 5000)", Array.from(profXCoords));
    process.exit(1);
  }
  if (!profZCoords.has(0) || !profZCoords.has(1000)) {
    console.error("FAIL: Arbitrary profile DXF output missing expected Z coordinates (0 and 1000)", Array.from(profZCoords));
    process.exit(1);
  }
  console.log(`SUCCESS: Arbitrary profile parse produced ${profLineCount} LINE entities with swept vertices.`);
} catch (e) {
  console.error("FAIL: Exception thrown during arbitrary profile parsing", e);
  process.exit(1);
}
