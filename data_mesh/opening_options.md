# KDP 2.0 Opening: Two Options

Below are two approaches to reframing the opening section. Both address the political dynamics (CIO retention of DE, InEight data ownership) while conveying a clear solution.

---

## Option A: Collaborative Enablement

*Tone: Positions KDS as a service layer that extends KTG and InEight investments. Minimizes territorial threat.*

---

### The Opportunity

Kiewit has made significant investments in enterprise data infrastructure:

- **KTG** owns the enterprise data platform (Azure, Snowflake, SAP replication), information security, and data privacy 
- **InEight** owns the project lifecycle data model and is investing in InEight Intelligence
- **KDS** owns data strategy (architecture and data domain planning), technical development for data science, data engineering, and application development—capabilities that depend on both KTG infrastructure and InEight source data

The opportunity is not to replace these investments—it is to **connect them** so the technical teams and the business can access trusted data at velocity. This means:

- **Projects** get schedule, cost, and quantity data without waiting weeks for custom extracts.  What if a JOR didn't take 40 minutes to populate?  What if we actually replicated design modeling data to our estimating domain?  What happens when we want to incorporate robotic data capture?  
- **Business users** get self-service access to certified reports and dashboards
- **Operations** get real-time visibility into project performance
- **Shared services** (finance, procurement, HR) get analytics without standing up shadow systems
- **Data science** gets the foundation and more importantly the common orchestration to build/deploy predictive models and AI

### The Gap

Today, data science projects stall waiting for data and data tool access, pipeline development, and environment provisioning. This creates:

- Workarounds (local copies, shadow pipelines, one-off extracts)
- Duplicate datasets (28+ Snowflake databases)
- Coordination overhead between KTG, InEight, and KDS

The gap is not technology—it's **a missing service layer** between platform owners and data consumers.

### The Solution: Data Engineering Customer Success Managers

We propose assigning a **DE CSM** to each major data science initiative. The DE CSM does not own the platform or the source data. Instead, they ensure:

**DE CSM Owns (High-Value Work):**

| Responsibility | DE CSM Role |
|----------------|-------------|
| Data Structures | Design and maintain Bronze/Silver/Gold schemas, Iceberg tables, data models |
| Pipeline Development | Build Dagster DAGs, data movement in/out, orchestration logic |
| Monitoring & Observability | Pipeline health, data quality alerts, lineage tracking in Dagster+ |
| Domain Coordination | Translate DS requirements into data products, prioritize with Data Domain Strategy |
| Architecture Artifacts | Document data flows, maintain source-to-target mappings |

**DE CSM Delegates via Ticket (Low-Value Work):**

| Request | Submit Ticket To | SLA Expectation |
|---------|------------------|-----------------|
| Infrastructure Provisioning | KTG Platform Team | Azure resources provisioned per spec |
| User Access Administration | KTG IAM | Routine access granted via self-service or ticket |
| Security Patching | KTG Security | Platform patched; DE CSM notified of downtime |
| Network Configuration | KTG Networking | Firewall rules, VNet peering per DE CSM spec |
| Cost Reporting | KTG FinOps | Monthly cost reports provided to DE CSM |

**DE CSM Coordinates (Shared Accountability):**

| Responsibility | Coordination Partner | How |
|----------------|---------------------|-----|
| Data Architecture Standards | Data Architecture (KDS) | DE CSM implements standards set by architecture team |
| Domain Prioritization | Data Domain Strategy (Colin Davis) | DE CSM executes priorities; Strategy sets roadmap |
| Security Reviews | KTG Security | KTG reviews; DE CSM implements controls in pipelines |
| Source System Access | InEight / SAP owners | DE CSM requests API access; source owners grant |
| Data Governance | KTG + KDS Governance | Shared policies; DE CSM enforces in data layer |

The DE CSM reports to Ed Smith (KDS Data Engineering), who has administrative alignment with KTG on Databricks, AKS, and Snowflake.

### Initial Outcomes (KIP/KDP 2.0)

1. Modern orchestration through Dagster+ (coordinating KDS workloads, not replacing enterprise scheduling)
2. New data from InEight, Palantir, and engineering models (InEight remains the system of record)
3. Access to data tools (Databricks, Snowflake, HVR, Kubernetes) via KTG-governed infrastructure
4. All data extensible in Snowflake through open-source Iceberg tables (enabling cross-platform compute)

---

## Option B: Problem-First Assertion

*Tone: Establishes the problem clearly and makes the case for organizational change. More direct, higher risk.*

---

### The Problem

KDS cannot deliver data science at the velocity Kiewit needs. The root cause is structural:

| Issue | Impact |
|-------|--------|
| **Two overlapping central DE teams** (KDS and KTG) | Duplicate pipelines, inconsistent tooling, coordination overhead |
| **28+ Snowflake databases** | Data sprawl—teams create copies because they can't trust or access the central source |
| **Source data access controlled by separate org** | KTG has source access; KDS has business context. Neither owns the end-to-end outcome. |
| **No single owner of data product quality** | When pipelines break, finger-pointing between KTG (infrastructure), InEight (source), and KDS (consumption) |

This is not a technology problem. It is an organizational design problem.

### The Industry Benchmark

HBR and industry research (2024-2025) shows organizations moving away from centralized support models toward **embedded, cross-functional data teams**. The coordination overhead between DE and DS is the #1 reason data products fail to ship.

Standard organizational models for data teams:
1. Embedded in operating divisions
2. Integrated as part of IT
3. Integrated operational function
4. Stand-alone service function

**Kiewit's current state—two overlapping central teams (KDS and KTG)—is not one of these models.** It is a historical artifact, not a design choice.

### The Solution: Hub-and-Spoke with DE CSMs

We propose a **Hub-and-Spoke model** where:

- **Hub (Ed Smith, KDS DE):** Owns the data platform layer (Dagster+, Databricks, Iceberg/Snowflake integration, ADLS)
- **Spokes (DE CSMs):** Embedded with each data science domain (Estimating, Scheduling, Procurement, etc.)

The DE CSM ensures:
1. **Storage:** KDP 2.0 (bronze/silver/gold) is hydrated, monitored, documented
2. **Data In/Out:** Pipelines connect domains to KDP 2.0 without creating local copies
3. **FinOps:** Continuous cost review and optimization

### Platform Outcomes (KIP/KDP 2.0)

1. Modern orchestration through Dagster+ (replacing fragmented .bat/Task Scheduler scripts)
2. New data from InEight, Palantir, and engineering models (landed in KDP 2.0, governed centrally)
3. Access to data tools (Databricks, Snowflake, HVR, Kubernetes) with self-service provisioning
4. All data extensible in Snowflake through Iceberg tables (one platform, compute anywhere)

### Addressing Stakeholder Concerns

| Stakeholder | Concern | How This Addresses It |
|-------------|---------|----------------------|
| **CIO / KTG** | "KDS is building shadow IT" | DE CSMs consume KTG infrastructure—they don't replace it. Dagster+ orchestrates KDS workloads only. |
| **CIO / KTG** | "Multi-cloud increases risk" | GCP is limited to closed-source model AI (approved Nov 2024). Core data stays in Azure. |
| **InEight President** | "KDS is replicating our data" | InEight is the system of record. KDP 2.0 lands InEight data to enable analytics—not to compete. |
| **InEight President** | "Who owns the truth?" | InEight owns source data. KDS owns derived analytics. Lineage is tracked in Dagster+. |
| **InEight President** | "We could build this cheaper in InEight." | KDS builds capabilities that span multiple source systems (InEight + SAP + engineering models + Palantir). InEight Intelligence is the right home for InEight-only analytics; KDS handles cross-system integration that no single product team should own. |

---

## Comparison

| Dimension | Option A | Option B |
|-----------|----------|----------|
| **Tone** | Collaborative, service-oriented | Direct, problem-first |
| **Risk** | Lower—less likely to trigger territorial defense | Higher—may provoke pushback from CIO/InEight |
| **Clarity** | Good—but buries the problem | Excellent—problem is explicit |
| **Call to Action** | Implicit (enable faster data science) | Explicit (organizational change required) |
| **Best For** | Audiences who need to feel included | Audiences who need to understand urgency |

---

## Recommendation

**For this audience (Freeman, Davis, from the CDO):**

Option A is the right foundation, but you can be more direct since:
- They already know the problem—they live it daily
- They don't need to be convinced KDS should lead this
- They need clarity on the solution, their roles, and what you're asking them to do

**Suggested adjustments to Option A for this audience:**

1. **Skip the external diplomacy** — You don't need to reassure Freeman/Davis that "KTG owns infrastructure." They know. Get to the solution faster.

2. **Be explicit about organizational expectations:**
   - Ed Smith owns the DE platform and DE CSMs report to him
   - Colin Davis owns data domain strategy and prioritization
   - Freeman has executive oversight and clears cross-org roadblocks

3. **Add a "What I Need From You" section:**
   - Freeman: Approval to staff DE CSMs, air cover with KTG/InEight
   - Davis: Domain prioritization (which DS initiatives get DE CSMs first?)

4. **Keep the stakeholder concern table from Option B** — Freeman and Davis will need to anticipate CIO and InEight pushback. Give them the talking points.

**Bottom line:** Option A's structure works, but tighten the opening (they don't need the setup) and add explicit asks at the end.
