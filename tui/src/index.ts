import { createCliRenderer, BoxRenderable, TextRenderable, RGBA } from "@opentui/core";
import { FilterPalette } from "./components/FilterPalette.js";
import { WheelMatrix } from "./components/WheelMatrix.js";
import { SpatialRetina } from "./components/SpatialRetina.js";

async function main() {
  const renderer = await createCliRenderer({
    exitOnCtrlC: true,
  });

  const root = renderer.root;
  root.flexDirection = "column";
  renderer.setBackgroundColor(RGBA.fromHex("#000000"));

  const header = new BoxRenderable(renderer, {
    backgroundColor: RGBA.fromHex("#00FF41"),
    height: 3,
    padding: 1,
    justifyContent: "center",
  });

  const headerText = new TextRenderable(renderer, {
    content: "[ SYNAPSE ARCHITECT ] v10.0 | OPEN-TUI COCKPIT",
    fg: RGBA.fromHex("#000000"),
  });
  header.add(headerText);

  const body = new BoxRenderable(renderer, {
    flexGrow: 1,
    flexDirection: "row",
    border: true,
    borderColor: RGBA.fromHex("#00FF41"),
    padding: 0,
  });

  const palette = new FilterPalette(renderer);
  const matrix = new WheelMatrix(renderer, 15);
  
  const retinaBox = new BoxRenderable(renderer, {
    flexGrow: 1,
    border: true,
    borderColor: RGBA.fromHex("#00FF41"),
    title: " SPATIAL RETINA (3D) ",
  });
  const retina = new SpatialRetina(renderer);
  retinaBox.add(retina);

  body.add(palette);
  body.add(matrix);
  body.add(retinaBox);

  const footer = new TextRenderable(renderer, {
    content: " System Ready | TUI Mode: OpenTUI (Zig Core) | Press Ctrl+C to Exit ",
    fg: RGBA.fromHex("#00FF41"),
    opacity: 0.5,
  });

  root.add(header);
  root.add(body);
  root.add(footer);

  console.log("🚀 OpenTUI Cockpit Initialized with 3D Spatial Retina.");
  renderer.start();
}

main().catch(console.error);

