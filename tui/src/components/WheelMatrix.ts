import { BoxRenderable, TextRenderable, type RenderContext, RGBA } from "@opentui/core";

export class WheelMatrix extends BoxRenderable {
  constructor(ctx: RenderContext, size: number = 10) {
    super(ctx, {
      flexDirection: "column",
      border: true,
      borderColor: RGBA.fromHex("#00FF41"),
      padding: 1,
      flexGrow: 1,
      title: " WHEEL MATRIX ",
    });

    const grid = new BoxRenderable(ctx, {
      flexDirection: "column",
    });

    const blocks = [" . ", " ░ ", " ▒ ", " ▓ ", " █ "];

    for (let i = 0; i < size; i++) {
      let rowContent = `${(i + 1).toString().padStart(2, "0")} `;
      for (let j = 0; j < size; j++) {
        const density = Math.floor(Math.random() * blocks.length);
        rowContent += blocks[density];
      }
      
      grid.add(new TextRenderable(ctx, {
        content: rowContent,
        fg: RGBA.fromHex("#00FF41"),
      }));
    }

    const legend = new TextRenderable(ctx, {
      content: "\n Legend: █ Full | ▓ High | ▒ Med | ░ Low | . Gap ",
      fg: RGBA.fromHex("#00FF41"),
      opacity: 0.5,
    });

    this.add(grid);
    this.add(legend);
  }
}
