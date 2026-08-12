# Wayfinder Local-Markdown Tracker

This directory holds wayfinder maps and their child tickets as markdown files. It is used when no external issue tracker is configured.

## Convention

- **Map**: `docs/wayfinder/<slug>-map.md`  
  Frontmatter: `label: wayfinder:map`, `destination`, `status`.
- **Tickets**: `docs/wayfinder/tickets/<nnn>-<slug>.md`  
  Frontmatter: `id`, `type` (`research` | `prototype` | `grilling` | `task`), `status`, `blocked_by`.
- **Blocking**: declared in ticket frontmatter (`blocked_by: ["002"]`). The map also renders the frontier in its body.
- **Resolution**: when a ticket closes, append a one-line decision to the map's **Decisions so far** section and update the ticket's status to `closed` with a resolution comment at the bottom.

## Frontier rule

A ticket is on the frontier when it is `status: open` and every ticket in `blocked_by` is `status: closed`.
