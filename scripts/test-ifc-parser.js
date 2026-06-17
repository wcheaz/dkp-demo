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
