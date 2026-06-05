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

  fs.writeFileSync(filePath, content, "utf8");
});
