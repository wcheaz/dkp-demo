const fs = require("fs");
const path = require("path");

const targetFiles = [
  "node_modules/three-dxf-loader/dist/three-dxf-loader.js",
  "node_modules/three-dxf-loader/dist/three-dxf-viewer.js"
];

targetFiles.forEach(file => {
  const filePath = path.resolve(__dirname, "..", file);
  if (!fs.existsSync(filePath)) {
    console.log(`File not found, skipping: ${file}`);
    return;
  }

  let content = fs.readFileSync(filePath, "utf8");
  
  // 1. Patch customDepthMaterial getter with a setter
  const depthRegex = /get customDepthMaterial\(\)\{return (\w+)\(this\.material\)\.getDepthMaterial\(\)\}/;
  if (depthRegex.test(content)) {
    content = content.replace(depthRegex, "get customDepthMaterial(){return $1(this.material).getDepthMaterial()}set customDepthMaterial(v){this._customDepthMaterial=v}");
    console.log(`Successfully patched customDepthMaterial in ${file}`);
  } else {
    console.log(`Could not find customDepthMaterial target in ${file} (or it was already patched)`);
  }

  // 2. Patch customDistanceMaterial getter with a setter
  const distanceRegex = /get customDistanceMaterial\(\)\{return (\w+)\(this\.material\)\.getDistanceMaterial\(\)\}/;
  if (distanceRegex.test(content)) {
    content = content.replace(distanceRegex, "get customDistanceMaterial(){return $1(this.material).getDistanceMaterial()}set customDistanceMaterial(v){this._customDistanceMaterial=v}");
    console.log(`Successfully patched customDistanceMaterial in ${file}`);
  } else {
    console.log(`Could not find customDistanceMaterial target in ${file} (or it was already patched)`);
  }

  // 3. Patch Vector3(s.x, s.y, 0) to use Z coordinate s.z
  const vector3Regex = /s=t\.vertices\[c\],(\w+)\.push\(new (\w+)\.Vector3\(s\.x,s\.y,0\)\)/g;
  if (vector3Regex.test(content)) {
    content = content.replace(vector3Regex, "s=t.vertices[c],$1.push(new $2.Vector3(s.x,s.y,s.z||0))");
    console.log(`Successfully patched Vector3 Z coordinate in ${file}`);
  }

  // 4. Patch bulge interpolation Vector3(l.x, l.y, 0) and Vector3(o.x, o.y, 0) to use l.z
  const bulgeStartRegex = /new (\w+)\.Vector3\(l\.x,l\.y,0\)/g;
  if (bulgeStartRegex.test(content)) {
    content = content.replace(bulgeStartRegex, "new $1.Vector3(l.x,l.y,l.z||0)");
    console.log(`Successfully patched bulge start Vector3 Z coordinate in ${file}`);
  }
  const bulgeInterpRegex = /new (\w+)\.Vector3\(o\.x,o\.y,0\)/g;
  if (bulgeInterpRegex.test(content)) {
    content = content.replace(bulgeInterpRegex, "new $1.Vector3(o.x,o.y,l.z||0)");
    console.log(`Successfully patched bulge interp Vector3 Z coordinate in ${file}`);
  }

  // 5. Patch polyface mesh Vector3(r.x, r.y, 0) to use r.z
  const meshRegex = /a\.push\(new (\w+)\.Vector3\(r\.x,r\.y,0\)\)/g;
  if (meshRegex.test(content)) {
    content = content.replace(meshRegex, "a.push(new $1.Vector3(r.x,r.y,r.z||0))");
    console.log(`Successfully patched polyface mesh Vector3 Z coordinate in ${file}`);
  }

  fs.writeFileSync(filePath, content, "utf8");
});
