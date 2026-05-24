---
title: Prediction Engine — Obsidian DataviewJS Templates
tags: [prediction-engine, obsidian, dataviewjs, template]
---

# Prediction Engine — Obsidian DataviewJS Dashboard

Paste these blocks into any Obsidian note. They query the pattern logs
exported by the Diagnostic Terminal commands and build live dashboards.

All commands that generate pattern logs:
```bash
lottery signal  br/lotofacil  --export-md "vault/logs/signal-2026-05.md"
lottery cluster br/lotofacil  --export-md "vault/logs/cluster-2026-05.md"
lottery stress-test br/lotofacil --export-md "vault/logs/stress-2026-05.md"
lottery detect-patterns br/lotofacil --esoteric all --export-md "vault/logs/detect-2026-05.md"
lottery leaderboard br/lotofacil  --export-md "vault/logs/leaderboard-2026-05.md"
```

---

## 1. Signal-to-Noise History Table

Queries all `signal` pattern logs and shows stability score over time.

````dataviewjs
const pages = dv.pages('"logs"')
  .where(p => p.type === "pattern-log" && p.file.name.startsWith("signal"))
  .sort(p => p.date, "desc");

dv.table(
  ["Date", "Game", "Strategy", "Window", "Stability", "Mean Conf", "Mean Entropy"],
  pages.map(p => [
    p.date,
    p.game,
    p.strategy,
    p.window,
    (parseFloat(p.stability_score) * 100).toFixed(0) + "%",
    parseFloat(p.mean_confidence).toFixed(4),
    parseFloat(p.mean_entropy).toFixed(4),
  ])
);
````

---

## 2. Leaderboard Trend — Composite Score Over Time

Track whether strategies improve or degrade their diagnostic score month-to-month.

````dataviewjs
const pages = dv.pages('"logs"')
  .where(p => p.type === "pattern-log" && p.file.name.startsWith("leaderboard"))
  .sort(p => p.date, "asc");

dv.table(
  ["Date", "Game", "Top Strategy", "Composite"],
  pages.map(p => [
    p.date,
    p.game,
    p.top_strategy,
    parseFloat(p.top_composite).toFixed(3),
  ])
);
````

---

## 3. High-Probability Nodes Tracker

Queries all `detect-patterns` logs and surfaces any esoteric nodes found.

````dataviewjs
const pages = dv.pages('"logs"')
  .where(p => p.type === "pattern-log" && p.file.name.startsWith("detect"))
  .sort(p => p.date, "desc");

const rows = [];
for (const p of pages) {
  const nodes = parseInt(p.high_probability_nodes) || 0;
  rows.push([
    p.date,
    p.game,
    p.strategy,
    p.esoteric,
    nodes > 0
      ? `**${nodes} node${nodes > 1 ? "s" : ""} found** ★`
      : "—",
    p.baseline_stability
      ? (parseFloat(p.baseline_stability) * 100).toFixed(0) + "%"
      : "—",
  ]);
}

dv.table(
  ["Date", "Game", "Strategy", "Overlay", "Nodes", "Baseline Stable%"],
  rows
);
````

---

## 4. Adversarial Stress-Test Summary

Queries all `stress-test` logs and surfaces strategies that cannot distinguish
real data from random injections.

````dataviewjs
const pages = dv.pages('"logs"')
  .where(p => p.type === "pattern-log" && p.file.name.startsWith("stress"))
  .sort(p => p.date, "desc");

dv.table(
  ["Date", "Game", "Inject Ratio", "Trials"],
  pages.map(p => [
    p.date,
    p.game,
    (parseFloat(p.inject_ratio) * 100).toFixed(0) + "%",
    p.trials,
  ])
);
````

---

## 5. Cluster Analysis — Latest Draw Cluster

Tracks which cluster the latest draw falls into over time.
Useful to check if esoteric windows align with cluster membership.

````dataviewjs
const pages = dv.pages('"logs"')
  .where(p => p.type === "pattern-log" && p.file.name.startsWith("cluster"))
  .sort(p => p.date, "desc");

dv.table(
  ["Date", "Game", "Method", "Clusters", "Latest Draw Cluster"],
  pages.map(p => [
    p.date,
    p.game,
    p.method,
    p.clusters,
    "C" + p.latest_draw_cluster,
  ])
);
````

---

## 6. Cross-Reference: Nodes × Cluster × Date

The key diagnostic: do High-Probability Nodes and specific cluster assignments
appear on the same dates? If so, you have converging evidence.

````dataviewjs
// Build date → {cluster, nodes_found} map
const detectLogs = dv.pages('"logs"')
  .where(p => p.type === "pattern-log" && p.file.name.startsWith("detect"));
const clusterLogs = dv.pages('"logs"')
  .where(p => p.type === "pattern-log" && p.file.name.startsWith("cluster"));

const dateMap = {};
for (const p of detectLogs) {
  const d = String(p.date);
  if (!dateMap[d]) dateMap[d] = {};
  dateMap[d].nodes = parseInt(p.high_probability_nodes) || 0;
  dateMap[d].esoteric = p.esoteric;
}
for (const p of clusterLogs) {
  const d = String(p.date);
  if (!dateMap[d]) dateMap[d] = {};
  dateMap[d].cluster = "C" + p.latest_draw_cluster;
}

const rows = Object.entries(dateMap)
  .sort(([a], [b]) => b.localeCompare(a))
  .map(([date, v]) => [
    date,
    v.cluster || "—",
    v.nodes > 0 ? `★ ${v.nodes} node(s) [${v.esoteric}]` : "—",
    v.nodes > 0 && v.cluster ? "⚡ CONVERGING" : "—",
  ]);

dv.table(["Date", "Cluster", "Esoteric Nodes", "Convergence"], rows);
````

---

## Usage Notes

- Store all exported `.md` files in a single Obsidian folder (e.g. `logs/`)
- Update the `dv.pages('"logs"')` path if your folder is named differently
- Run the CLI commands after each draw and re-export to keep the dashboard live
- The "Convergence" column in block 6 flags dates where both esoteric nodes
  AND a specific cluster assignment appear — cross-reference with your draw
  calendar to build evidence for or against the esoteric hypothesis
