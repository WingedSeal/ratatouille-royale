const fs = require("fs");
const path = require("path");

// Bitwise mask to remove all flip flags
const TILE_ID_MASK = 0x1fffffff;

function clearFlipFlags(mapData) {
  const cleaned = { ...mapData };

  // Process all layers
  cleaned.layers = mapData.layers.map((layer) => {
    if (layer.data && Array.isArray(layer.data)) {
      return {
        ...layer,
        data: layer.data.map((gid) => gid & TILE_ID_MASK),
      };
    }
    return layer;
  });

  return cleaned;
}

// Main execution
const inputFile = "rrmap.tmj";
const outputFile = "rrmap_fixed.tmj";

try {
  // Read the original file
  console.log(`Reading ${inputFile}...`);
  const fileContent = fs.readFileSync(inputFile, "utf8");
  const mapData = JSON.parse(fileContent);

  // Clear all flip flags
  console.log("Clearing flip flags...");
  const cleanedMap = clearFlipFlags(mapData);

  // Write to new file
  console.log(`Writing to ${outputFile}...`);
  fs.writeFileSync(outputFile, JSON.stringify(cleanedMap, null, 2));

  console.log("✓ Done! Fixed map saved as " + outputFile);
  console.log(
    "Review the file, then rename it back to rrmap.tmj if it looks correct.",
  );
} catch (error) {
  console.error("Error:", error.message);
  process.exit(1);
}
