The Kiewit Data Platform build could be built much better.  The plan for the platform is now and has always been:
#initial outcomes from the Kiewit Intelligence Program which contains the Kiewit Data Platform
1-Modern orchestration through Dagster+
2-New data from InEight, Palantir, Engineering model datasets
3-Access to data and data tools (DataBricks, Snowflake, HVR, Kubernetes...)
4-All data is extensible in Snowflake through open-source tables (iceberg)

My plan forward would be to assign a data engineering customer success manager (DE CSM) to each project / data science lead.  The DE CSM would ensure these items are successful at a minimum:

1-Storage: KDP 2.0 (bronze/silver/gold in Azure/Databricks/Snowflake) is hydrated, has strong monitoring/observability in Dagster+, has architecture artifacts.

2-Out/In: The DE CSM would provide data pipelines in and out of KDP2.  Enabling teams to build in a Mesh (small agile work groups that are focused on the same domain) but maintaining a homogenous storage platform (KDP 2).

3-Financial Operations Cost: Review workloads and continually cost cut the worst offenders.

4-Last but most important DE CSM's will incorporate alterations to the golden data at the direction of data scientists which reduces duplication and reinforces a SSOT.  We won't have data scientists prioritizing the mathemetical analysis and pushing the data management to the side of their desks and we won't have data engineers building something for themselves.

The DE CSM's, for domains we want to own, would report to Ed Smith.  Ed Smith would have administrative authority over DataBricks (he has this), Azure Kubernetes (he has this), Snowflake (he has the Polaris credentials), and Azure Data Lake Storage (doesn't have this).  



Ed would report to me and I will ensure that both DE and DS are able to see value from the platform and I will coordinate with KTG (Malatek, Huttmann, Kayla, etc.)

# Research & HBR-Relevant Insights

## Why DE and DS in One Organization?

HBR and industry research (2024-2025) shows a clear trend: **data teams are moving away from centralized support models toward embedded, cross-functional structures**. More than 80% of chief data officers are actively hiring for new data roles, and success depends on "balancing centralized efficiency with embedded, stakeholder-facing roles."

The coordination overhead between DE and DS is the #1 reason organizations fail to deliver data products at velocity. When DE and DS are separate:
- Handoffs create delays and miscommunication
- DE builds pipelines without understanding DS consumption patterns
- DS builds workarounds when DE is a bottleneck
- Neither team owns the end-to-end outcome

**The DE CSM model addresses this**: a single person owns the relationship between a domain and the platform, ensuring both pipeline quality and DS usability.

---

## Key Business Outcomes for Data Consumers

### 1. Lineage, Observability, and Code Access

**Dagster+ capabilities:**
- Integrated lineage and observability across the entire development lifecycle
- Built-in monitoring, data quality checks, and cost tracking
- Full visibility into data assets with ability to trace lineage and catch issues before they reach downstream
- Asset-based orchestration (similar to Airflow 3's `@asset` paradigm)—pipelines focus on data products, not just tasks

**Airflow 3 (April 2025 GA) capabilities:**
- Experimental lineage support tracking data flow between tasks and from hooks
- OpenLineage integration for automatic metadata collection (inputs, outputs, execution time, state)
- Asset Event Details page showing "Asset Runs" similar to DAG runs
- Answers critical questions: "When was this data last updated?" "What upstream sources feed this?" "What broke and why?"

**What the consumer should expect:**
- Click on any table/asset and see: upstream sources, downstream consumers, last refresh time, data quality status
- Access to the code that produced the asset (Git-linked)
- Alerting on freshness, volume, and schema changes
- Self-service exploration without requiring DE involvement for basic questions

### 2. Reusable Objects vs. Database Sprawl

The current state—28+ Snowflake databases—is a symptom of unmanaged data duplication. Each team created their own copy because:
- They couldn't trust the central source
- Access was too slow or bureaucratic
- They needed a slightly different transformation

**The fix is not more governance—it's better products:**
- Bronze/Silver/Gold medallion architecture in KDP 2.0
- Iceberg tables in Unity Catalog enable compute-anywhere access (Databricks, Snowflake, Trino, Spark)
- Domain teams publish certified data products with SLAs, documentation, and versioning
- Central platform team (Ed's team) provides the infrastructure; domain teams own the data

**Databricks Unity Catalog (2025) now supports:**
- Full Iceberg REST Catalog API—external engines can read/write to Unity-managed Iceberg tables
- Iceberg Catalog Federation—query Iceberg tables in AWS Glue, Hive, or Snowflake without data copying
- Compatibility Mode on Azure Data Lake—generates read-only versions accessible by external clients

### 3. Decoupled Architecture for Real-Time and Batch

**Confluent Kafka pattern:**
- Event Broker enables complete decoupling of services—sources and sinks are isolated
- Independent scaling and higher resiliency
- Different teams work independently; services change with minimal impact on dependents
- Replaces point-to-point, batch, and streaming pipelines with unified infrastructure

**Application to Kiewit:**
- Scheduling data (pub/sub model you mentioned) is a natural fit for Kafka
- Projects waiting hours → waiting 4 minutes is the kind of outcome streaming enables
- CDC from source systems (SAP, InEight) to Iceberg tables via Kafka = real-time bronze layer
- AI/ML applications get real-time access to fresh business data

---

## Data Mesh Principles Applied to KDP 2.0

The DE CSM model is essentially a **Hub-and-Spoke / Data Mesh hybrid**:

| Principle | KDP 2.0 Implementation |
|-----------|------------------------|
| **Domain-Oriented Ownership** | DE CSM assigned to each domain (Estimating, Scheduling, etc.) |
| **Data as a Product** | Domains publish certified data products with SLAs, documentation |
| **Self-Serve Data Platform** | Ed's team owns Databricks, AKS, Snowflake (Polaris), ADLS—domains consume |
| **Federated Computational Governance** | Central policies (security, compliance) executed locally via Dagster+ |

**Critical success factor:** The DE CSM is not a gatekeeper. They are an enabler who ensures domain teams can publish quality data products without requiring deep infrastructure expertise.

---

## Multi-Cloud Compute Strategy

| Workload | Platform | Rationale |
|----------|----------|-----------|
| **Data Lake / Medallion Architecture** | Azure Data Lake Storage + Databricks Unity | Primary storage, governance, lineage |
| **Data Warehouse / BI** | Snowflake (via Polaris/Iceberg) | SQL analytics, certified reporting |
| **Orchestration** | Dagster+ (hybrid: Dagster-hosted backend, user code on AKS) | Observability, lineage, cost tracking |
| **Closed-Source Model AI** | GCP (Atlas, Scheduling apps) | Best-of-breed model APIs, velocity |
| **Training / Fine-Tuning / Inference** | On-Prem NVIDIA B200 Cluster (16 nodes) | 3x training perf, 15x inference perf vs H100 |
| **Real-Time Streaming** | Confluent Kafka (if adopted) | CDC, pub/sub for scheduling data |

**The B200 cluster (16 nodes = 128 GPUs, 23 TB GPU memory) is exceptional:**
- 144 PFLOPS FP4 Tensor Core performance per node
- Real-time LLM inference at scale (50ms token-to-token latency)
- Handles training, fine-tuning, and inference in one platform
- Keeps sensitive data on-prem while enabling GPU-intensive workloads

---

## Next Steps to Define

3. **FinOps accountability**: Who reviews workloads and cuts costs? DE CSM should have this in their scorecard.

4. **ADLS access for Ed**: You noted he doesn't have this. Critical for him to own the platform.

5. **Kafka evaluation**: Is Confluent the right fit for pub/sub scheduling data, or is a simpler solution (e.g., Azure Event Hubs) sufficient?

6. **Domain prioritization**: Which domains get DE CSMs first? Estimating and Scheduling are obvious. What's next?

