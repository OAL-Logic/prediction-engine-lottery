# 17 — Rebuild Guidance (Behavioral)

This is a **reference architecture** based on observed behavior and safe signals—avoid copying proprietary implementation.

## Scope of rebuild
- MVP feature set (link to Feature IDs):
- Out of scope:

## Proposed architecture (high-level)
### Subsystems
| Subsystem | Responsibilities | Inputs/Outputs | Notes |
|---|---|---|---|
| UI Shell | Navigation, windowing, commands | Screens, command events |  |
| Domain Services | Business rules | DTOs / domain entities |  |
| Persistence | Local storage | Files/DB |  |
| Network Client | Remote calls (as required) | Endpoint catalog |  |
| Settings | Config + policy | Settings catalog |  |
| Logging | Diagnostics | Log taxonomy |  |

### Data model (observed)
| Entity | Key fields | Relationships | Source evidence |
|---|---|---|---|
|  |  |  |  |

## Compatibility targets
- Import/export formats (observed):
- Migration approach:

## Parity risks / redesign opportunities
| Area | Risk | Proposed approach |
|---|---|---|
|  |  |  |

