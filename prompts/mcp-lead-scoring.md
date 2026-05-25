# MCP Readiness Checklist — Scoring Criteria

Reference for the Hermes Agent MCP lead generation cron job.
These signals indicate a company is a good candidate for MCP Integration Audit.

## Scoring System

13 questions across 4 sections. Score = number of signals detected.
**8+ pts** = HIGH priority · **5-7** = WARM · **0-4** = COLD

---

### Section 1: Systems Fragmentation (Q1-Q3)
| # | Signal |
|---|--------|
| Q1 | Uses 5+ SaaS tools that don't talk to each other |
| Q2 | Proprietary/legacy internal APIs — siloed databases |
| Q3 | Uses Zapier/Make (especially if complaining about cost) |

### Section 2: Manual Work & Friction (Q4-Q7)
| # | Signal |
|---|--------|
| Q4 | Someone copies/pastes data between systems (10+ hrs/week) |
| Q5 | Workflows that "should be automated" but aren't |
| Q6 | Data always outdated/conflicting between systems |
| Q7 | "Data person" doing undocumented manual magic |

### Section 3: Scale & Growth (Q8-Q10)
| # | Signal |
|---|--------|
| Q8 | Each new client adds proportional manual work |
| Q9 | Wants automation but no devs available |
| Q10 | Planning 50%+ growth in next 12 months |

### Section 4: Budget & Readiness (Q11-Q13)
| # | Signal |
|---|--------|
| Q11 | Already invests €500+/month in SaaS |
| Q12 | Has €20-40k budget for consulting if ROI is clear |
| Q13 | Has CTO, VP Ops, or internal champion |

### Priority Override: AUDIT NOW

Companies with **public API docs or GitHub repos** marked as AUDIT NOW — the highest priority tier, regardless of score.

### Target Profile

SMEs (10-200 employees) in LATAM or Spain showing any of: "tech stack", "API integration", "automation", "Zapier is expensive", "data silos", "legacy systems".