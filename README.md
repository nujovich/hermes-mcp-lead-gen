<div align="center">
  <img src="https://raw.githubusercontent.com/NousResearch/hermes-agent/HEAD/assets/banner.png" alt="Hermes Agent" width="600"/>
  <br/><br/>
  <h1>🔌 MCP Lead Generation & Pre-Audit System</h1>
  <p><strong>Powered by <a href="https://hermes-agent.nousresearch.com">Hermes Agent</a></strong></p>
  <p><em>Autonomous daily research pipeline that finds SMEs with legacy APIs,<br/>scores them on MCP readiness, and pre-audits their public API surface.</em></p>
  <br/>
  <p>
    <a href="https://dev.to/nujovich/building-an-autonomous-mcp-lead-generation-system-with-hermes-agent">
      <img src="https://img.shields.io/badge/DEV.to-Hermes%20Challenge-673773?style=for-the-badge&logo=dev.to" alt="Dev.to Post"/>
    </a>
    <a href="https://hermes-agent.nousresearch.com">
      <img src="https://img.shields.io/badge/Hermes%20Agent-Docs-FFD700?style=for-the-badge" alt="Hermes Agent Docs"/>
    </a>
    <a href="https://nadiaujovich.dev">
      <img src="https://img.shields.io/badge/By-Nadia%20Ujovich-0D7377?style=for-the-badge" alt="Nadia Ujovich"/>
    </a>
  </p>
</div>

---

## 🎯 What This Does

Every day at 10:00 AM, **Hermes Agent** autonomously:

1. 🔍 **Researches** LinkedIn, Reddit, GitHub, Product Hunt, and tech blogs for SMEs showing signs of systems fragmentation
2. 📊 **Scores** each prospect against a 13-point **MCP Readiness Checklist**
3. 🛠️ **Pre-audits** high-scorers by analyzing their public API documentation and GitHub repos
4. 📧 **Emails** you a structured report with company name, contact info, MCP score, and concrete MCP tool proposals

> **The result:** A daily pipeline of warm, pre-vetted leads — each one with a specific MCP integration plan ready to present.

---

## 🏆 MCP Readiness Checklist (13 Questions)

### 1. Systems Fragmentation (3 pts)
| # | Signal |
|---|--------|
| Q1 | Uses 5+ SaaS tools that don't talk to each other |
| Q2 | Has proprietary/legacy internal APIs or siloed databases |
| Q3 | Uses Zapier/Make for integrations (bonus: complaining about cost) |

### 2. Manual Work & Friction (4 pts)
| # | Signal |
|---|--------|
| Q4 | Someone copies/pastes data between systems (10+ hrs/week wasted) |
| Q5 | Workflows that "should be automated" but aren't |
| Q6 | Data is always outdated/conflicting between systems |
| Q7 | "Data person" doing undocumented manual magic |

### 3. Scale & Growth (3 pts)
| # | Signal |
|---|--------|
| Q8 | Each new client/project adds manual work hours |
| Q9 | Wants automation but no devs available (integrations take 3-4 weeks) |
| Q10 | Planning 50%+ growth in next 12 months |

### 4. Budget & Readiness (3 pts)
| # | Signal |
|---|--------|
| Q11 | Already invests €500+/month in SaaS |
| Q12 | Has €20-40k budget for consulting if ROI is clear |
| Q13 | Has CTO, VP Ops, or internal champion |

**Scoring:** 8-13 → **HIGH** · 5-7 → **WARM** · 0-4 → **COLD**

### Priority Override: AUDIT NOW

If a company has **public API documentation or GitHub repos**, mark them as **AUDIT NOW** regardless of score — the system pre-audits immediately.

---

## 🔧 Architecture

<p align="center">
  <img src="https://raw.githubusercontent.com/nujovich/hermes-mcp-lead-gen/main/assets/architecture.png" alt="Architecture Diagram" width="700"/>
</p>

---


## 📋 Real Results: Pre-Audited Companies

### Cobre (cobre.com) — Score: 9/13 | AUDIT NOW

**Industry:** Fintech / B2B Payments (Colombia, Mexico)
**API Surface:** ~50 REST endpoints in 18 categories

**5 MCP tools identified:**
- `cobre_crear_contraparte` — Register beneficiaries by country/rail
- `cobre_ejecutar_pago_local` — SPEI/ACH/Bre-B payments
- `cobre_crear_cotizacion_fx` — FX quote requests
- `cobre_ejecutar_pago_internacional` — Cross-border payments
- `cobre_consultar_estado_pago` — Payment status tracking

**→ Already uses MCP via Apidog, but no Python/Node.js SDKs exist.**

### Truora (truora.com) — Score: 7/13 | AUDIT NOW

**Industry:** Identity Verification / KYC (LATAM)
**API Surface:** ~120 endpoints across 5 API families

**5 MCP tools identified:**
- `truora_check_background` — Background checks per country
- `truora_get_check_result` — Verification results with scores
- `truora_create_identity_process` — Digital identity validation
- `truora_send_whatsapp_message` — WhatsApp via templates
- `truora_list_checks` — Verification history

**→ Only has iOS SDKs. No Python/Node.js/Go tooling exists.**

---

## 🚀 Getting Started

### Prerequisites
- [Hermes Agent](https://hermes-agent.nousresearch.com/docs) installed
- `himalaya` CLI for email
- LinkedIn/GitHub access for research

### Quick Start
```bash
# 1. Copy the scoring reference
cp prompts/mcp-lead-scoring.md ~/.hermes/skills/

# 2. Create the cron job
hermes cron create \
  --schedule "0 10 * * *" \
  --prompt "$(cat prompts/cron-prompt.txt)" \
  --name "MCP Lead Generation"

# 3. First report arrives tomorrow at 10 AM
```

---

## 📁 Repository Structure

```
📂 hermes-mcp-lead-gen/
├── 📄 README.md
├── 📂 prompts/
│   ├── 📄 cron-prompt.txt        ← Full Hermes Agent cron job prompt
│   └── 📄 mcp-lead-scoring.md    ← 13-point scoring reference
└── 📂 examples/
    └── 📄 report-sample.txt      ← Example daily output
```

---

## 📝 License

MIT — Built with [Hermes Agent](https://hermes-agent.nousresearch.com) by [Nadia Ujovich](https://nadiaujovich.dev)

<div align="center">
  <br/>
  <sub>Part of the <a href="https://dev.to/devteam/join-the-hermes-agent-challenge-1000-in-prizes-13cd">Hermes Agent Challenge</a> · May 2026</sub>
</div>
