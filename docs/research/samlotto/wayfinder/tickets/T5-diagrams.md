<!-- parent: MAP · label: wayfinder:task -->
# T5 — Diagrams (ER, sequence, state)

Type: task (AFK) · Assignee: fable-session  · Status: CLOSED
Blocked-by: — (was T3, closed)  ·  Blocks: —

## Resolution (CLOSED)

Created `Documentation/12-Diagrams.md` (Mermaid): (a) **ER diagram** of the domain
(Game · Draw · Ticket · FilterCatalog · Wheel · AnalysisResult · Prediction ·
Validation) grounded in the verified schema incl. the T3-recovered tables;
(b) **two sequence diagrams** — the play pipeline (generate→filter→wheel→optimize→
check) and pool-based predict/verify; (c) **state diagram** of the ticket lifecycle
(Generated→Filtered→Wheeled→Optimized→Tagged→Played→Checked→Won/Lost).
Cross-linked from docs 00, 06, 07. Blocks nothing further.

## Question

Produce the diagrams the spec is missing, as Mermaid embedded in the docs:
(a) **ER diagram** of the data model from doc 09 (Game · Draw · analysis caches ·
Filters · Tickets · Validation) — needs the complete table set from T3;
(b) **sequence diagrams** for the core flows in doc 06 (generate→filter→wheel→
optimize→check; predict→verify); (c) **state diagram** for the ticket lifecycle
(generated → filtered → wheeled → optimized → tagged → checked). Cross-link from
docs 06/07/09.
