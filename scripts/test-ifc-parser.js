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
