# KDP 2.0: Data Engineering Strategy

**To:** Dave Freeman, Colin Davis  
**From:** Matt Pappas, CDO  
**Date:** February 2026

---

## The Problem

KDS cannot deliver data science or data products at the velocity Kiewit needs. The root cause is structural:

| Issue | Impact |
|-------|--------|
| **Two overlapping central DE teams** (KDS and KTG) | Duplicate pipelines, inconsistent tooling, coordination overhead |
| **28+ Snowflake databases** | Data sprawl—teams create copies because they can't trust or access the central source |
| **Source data access controlled by separate org** | KTG has source access; KDS has business context. Neither owns the end-to-end outcome. |
| **No single owner of data product quality** | When pipelines break, finger-pointing between KTG (infrastructure), InEight (source), and KDS (consumption) |

This is not a technology problem. It is an organizational design problem.

---

## The Industry Benchmark

Gartner predicts **80% of data and analytics governance initiatives will fail by 2027** due to "center-out, command-and-control" approaches that operate reactively rather than strategically. The fix: link data capabilities directly to business outcomes and distribute ownership to domain teams.

*Source: [Gartner, Feb 2024](https://www.gartner.com/en/newsroom/press-releases/2024-02-28-gartner-predicts-80-percent-of-data-and-analytics-governance-initiatives-will-fail-by-2027)*

Standard organizational models for data teams:
1. Embedded in operating divisions
2. Integrated as part of IT
3. Integrated operational function
4. Stand-alone service function

**Kiewit's current state—two overlapping central teams (KDS and KTG)—is not one of these models.** It is a historical artifact, not a design choice.

---

## The Solution: Hub-and-Spoke with DE CSMs

We propose a **Hub-and-Spoke model** where:

- **Hub (Ed Smith, KDS DE):** Owns the data platform layer (Dagster+, Databricks, Iceberg/Snowflake integration, ADLS)
- **Spokes (DE CSMs):** Embedded with each data science domain (Estimating, Scheduling, Procurement, etc.)

---

### DE CSM Owns (High-Value Work)

| Responsibility | DE CSM Role |
|----------------|-------------|
| Data Structures | Design and maintain Bronze/Silver/Gold schemas, Iceberg tables, data models |
| Pipeline Development | Build Dagster DAGs, data movement in/out, orchestration logic |
| Monitoring & Observability | Pipeline health, data quality alerts, lineage tracking in Dagster+ |
| Domain Coordination | Translate DS requirements into data products, prioritize with Data Domain Strategy |
| Architecture Artifacts | Document data flows, maintain source-to-target mappings |

---

### DE CSM Delegates via Ticket (Low-Value Work)

| Request | Submit Ticket To | SLA Expectation |
|---------|------------------|-----------------|
| Infrastructure Provisioning | KTG Platform Team | Azure resources provisioned per spec |
| User Access Administration | KTG IAM | Routine access granted via self-service or ticket |
| Security Patching | KTG Security | Platform patched; DE CSM notified of downtime |
| Network Configuration | KTG Networking | Firewall rules, VNet peering per DE CSM spec |
| Cost Reporting | KTG FinOps | Monthly cost reports provided to DE CSM |

---

### DE CSM Coordinates (Shared Accountability)

| Responsibility | Coordination Partner | How |
|----------------|---------------------|-----|
| Data Architecture Standards | Data Architecture (KDS) | DE CSM implements standards set by architecture team |
| Domain Prioritization | Data Domain Strategy (Colin Davis) | DE CSM executes priorities; Strategy sets roadmap |
| Security Reviews | KTG Security | KTG reviews; DE CSM implements controls in pipelines |
| Source System Access | InEight / SAP owners | DE CSM requests API access; source owners grant |
| Data Governance | KTG + KDS Governance | Shared policies; DE CSM enforces in data layer |

---

## Platform Outcomes (KIP/KDP 2.0)

1. **Modern orchestration through Dagster+** — replacing fragmented .bat/Task Scheduler scripts
2. **New data from InEight, Palantir, and engineering models** — landed in KDP 2.0, governed centrally
3. **Access to data tools** (Databricks, Snowflake, HVR, Kubernetes) with self-service provisioning
4. **All data extensible in Snowflake through Iceberg tables** — one platform, compute anywhere

---

## Addressing Stakeholder Concerns

| Stakeholder | Concern | How This Addresses It |
|-------------|---------|----------------------|
| **CIO / KTG** | "KDS is building shadow IT" | DE CSMs consume KTG infrastructure—they don't replace it. Dagster+ orchestrates KDS workloads only. |
| **CIO / KTG** | "Multi-cloud increases risk" | GCP is limited to closed-source model AI (approved Nov 2024). Core data stays in Azure. |
| **InEight President** | "KDS is replicating our data" | InEight is the system of record. KDP 2.0 lands InEight data to enable analytics—not to compete. |
| **InEight President** | "Who owns the truth?" | InEight owns source data. KDS owns derived analytics. Lineage is tracked in Dagster+. |
| **InEight President** | "We could build this cheaper in InEight." | KDS builds capabilities that span multiple source systems (InEight + SAP + engineering models + Palantir). InEight Intelligence is the right home for InEight-only analytics; KDS handles cross-system integration that no single product team should own. |

---

## What I Need From You

**Dave Freeman:**
- Approval to staff DE CSMs (initial ask: 2-3 for Estimating and Scheduling domains)
- Air cover with KTG and InEight leadership when concerns arise
- Executive sponsorship for KDP 2.0 as the strategic platform

**Colin Davis:**
- Domain prioritization: Which DS initiatives get DE CSMs first?
- Data domain strategy alignment with DE CSM roadmap
- Architecture standards for DE CSMs to implement

---

## Organizational Clarity

| Role | Owner | Responsibility |
|------|-------|----------------|
| DE Platform & DE CSMs | Ed Smith | Dagster+, Databricks, K8s, data structures, pipelines |
| Data Domain Strategy | Colin Davis | Domain prioritization, business alignment, roadmap |
| Executive Oversight | Dave Freeman | Cross-org roadblocks, staffing approval, KTG/InEight alignment |

---

## Next Steps

1. **Staffing:** Identify 2-3 DE CSM candidates for Estimating and Scheduling
2. **Domain Kickoff:** Colin aligns with DS leads on first domains to receive DE CSM support
3. **KTG Alignment:** Matt meets with CIO to socialize model and address concerns
4. **InEight Alignment:** Matt meets with InEight President to clarify KDS vs. InEight Intelligence boundaries
