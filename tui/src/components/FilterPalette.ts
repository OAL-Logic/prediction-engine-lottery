import { BoxRenderable, TextRenderable, InputRenderable, type RenderContext, RGBA } from "@opentui/core";

export interface Filter {
  id: string;
  name: string;
  tier: number;
}

export class FilterPalette extends BoxRenderable {
  private searchInput: InputRenderable;
  private resultsBox: BoxRenderable;
  private filters: Filter[] = [
    { id: "structural_odd_count", name: "Odd Number Count", tier: 1 },
    { id: "structural_prime_count", name: "Prime Number Count", tier: 1 },
    { id: "structural_ac_value", name: "Arithmetic Complexity (AC)", tier: 1 },
    { id: "positional_successive_groups", name: "Successive Groups", tier: 2 },
    { id: "positional_first_last_distance", name: "First-Last Distance", tier: 2 },
    { id: "algebraic_number_sum", name: "Number Sum", tier: 3 },
    { id: "algebraic_root_sum", name: "Root Sum", tier: 3 },
    { id: "historical_hot_cold", name: "Hot-Cold Distribution", tier: 4 },
  ];

  constructor(ctx: RenderContext) {
    super(ctx, {
      flexDirection: "column",
      border: true,
      borderColor: RGBA.fromHex("#00FF41"),
      padding: 0,
      width: "40%",
      title: " FILTER PALETTE ",
    });

    this.searchInput = new InputRenderable(ctx, {
      placeholder: "Search filters...",
      marginBottom: 1,
    });

    this.resultsBox = new BoxRenderable(ctx, {
      flexGrow: 1,
      flexDirection: "column",
    });

    this.add(this.searchInput);
    this.add(this.resultsBox);

    this.updateResults("");

    // Input events
    this.searchInput.on("change", () => {
      this.updateResults(this.searchInput.value);
    });
  }

  private updateResults(query: string) {
    const children = this.resultsBox.getChildren();
    children.forEach(child => this.resultsBox.remove(child.id));
    
    const filtered = this.filters.filter(f => 
      f.name.toLowerCase().includes(query.toLowerCase()) ||
      f.id.toLowerCase().includes(query.toLowerCase())
    );

    filtered.forEach(f => {
      const item = new TextRenderable(this.ctx, {
        content: ` [T${f.tier}] ${f.name} `,
        fg: RGBA.fromHex("#00FF41"),
      });
      this.resultsBox.add(item);
    });

    if (filtered.length === 0) {
      this.resultsBox.add(new TextRenderable(this.ctx, { 
        content: " No matches found. ", 
        fg: RGBA.fromHex("#888888"),
      }));
    }
  }
}
