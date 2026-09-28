# AI-based supervision of business processes: continuous controls monitoring, AI audit, spend and invoice audit, and contract/SLA compliance (landscape as of Sept 2026)

Research date: 2026-09-28. Method: web search (about 30 queries). Many vendor sites (sirion.ai, datasnipper.com, vixxo.com, siliconangle, yahoo finance) were blocked for direct fetch in this environment, so several facts rely on search-result snippets of press releases rather than full-page reads. Items marked "[background, unverified this session]" come from prior knowledge and were not confirmed by a source retrieved here. The report writer should treat them as lower confidence.

---

## Q1. Who are the main players in AI continuous controls monitoring (CCM) and AI audit?

### Takeaway
The field splits into four groups. (a) AI-native audit tools for audit firms (Fieldguide, DataSnipper, MindBridge, Inscope, Trullion). (b) Spend and transaction monitoring for corporate finance (AppZen, Oversight, Safebooks, Celery). (c) GRC/SOX platforms that bolt on agents (Optro, formerly AuditBoard; Workiva; Pathlock). (d) Adjacent cyber-GRC CCM vendors (Panaseer, RegScale, Hyperproof, Sprinto, Quod Orbis). Capital and M&A are concentrating on agentic audit: Fieldguide raised $75M at a $700M valuation (Feb 2026), AppZen raised $180M (Sep 2025), Hg bought AuditBoard for more than $3B (2024), and Optro bought Midship (May 2026).

### Cited Findings

**Company-by-company: AI audit and CCM**

| Company | What it does | Target customer | Funding / size | Founded / HQ | Evidence type |
|---|---|---|---|---|---|
| **Fieldguide** | Agentic AI platform for audit and advisory work (engagement automation for CPA firms) | Audit and advisory firms (CPA firms) | Series C of $75M at a $700M valuation, led by Goldman Sachs Alternatives Growth Equity, with Geodesic, Bessemer, 8VC and Thomson Reuters participating. Total raised $125M (Feb 2, 2026) — [SiliconANGLE](https://siliconangle.com/2026/02/02/fieldguide-raises-75m-700m-valuation-scale-agentic-ai-audit-advisory-firms/); [Fortune](https://fortune.com/2026/02/02/goldman-sachs-fieldguide-accounting-cpa-ai-software-platform-venture-capital/); [Intl Accounting Bulletin](https://www.internationalaccountingbulletin.com/news/agentic-ai-audit-platform-fieldguide/) | [background, unverified this session: ~2020, San Francisco] | Documents and workpapers (unstructured) plus client data |
| **DataSnipper** | Excel-native AI for audit and finance. Extracts and matches evidence from documents (invoices, bank statements) to spreadsheet figures. Launched DocuMine and acquired UpLink | Audit firms (Big 4 through mid-tier) and corporate finance/internal audit | $100M Series B led by Index Ventures at a $1B valuation (Feb 2024; older than 2025) — [Fortune](https://fortune.com/2024/02/01/data-snipper-1-billion-valuation-unicorn-funding-round-ai-audit-accounting/); UpLink acquisition and DocuMine launch — [DataSnipper](https://www.datasnipper.com/resources/datasnipper-acquisition-uplink-launch-documine); says it delivered "$1.4B in productivity savings in 2025" — [DataSnipper](https://www.datasnipper.com/resources/datasnipper-delivers-1-4b-in-productivity-savings-in-2025-as-audit-and-finance-enter-the-ai-era) (page title only, not read) | [background, unverified: 2017, Amsterdam] | Strongly unstructured: PDFs and scanned documents matched to structured figures |
| **MindBridge** | AI anomaly and risk detection across 100% of general-ledger transactions. Sept 2026 added "Agentic Risk Assessment" linking evidence, analytics, assertions, materiality and methodology for audit planning. Brands itself as "autonomous financial oversight" | Audit and advisory firms, enterprises, government, financial institutions. More than 20,000 accountants and finance professionals use it | $82.2M raised in total (per search snippet of PitchBook/Yahoo) — [Yahoo/PR](https://finance.yahoo.com/technology/ai/articles/mindbridge-advances-financial-oversight-agentic-120200310.html); Sept 22, 2026 release — [BNN Bloomberg](https://www.bnnbloomberg.ca/press-releases/2026/09/22/mindbridge-advances-financial-oversight-for-the-agentic-era-with-new-platform-capabilities/) | 2015, Ottawa, Canada — [MindBridge company page](https://www.mindbridge.ai/company/) / [NRC Canada](https://nrc.canada.ca/en/stories/risking-financial-risk-mindbridge-uses-artificial-intelligence-drive-growth) | Mainly structured ledger/ERP transactions. The 2026 release adds evidence linking |
| **Inscope** | AI drafting, review and validation of financial statements with audit trails | Enterprises and their accounting firms | $14.5M Series A led by Norwest (Feb 20, 2026). Total $18.8M after a $4.3M seed in 2023. ARR up more than 30x and customers up 5x in 12 months — [GlobeNewswire](https://www.globenewswire.com/news-release/2026/02/20/3242123/0/en/Inscope-Raises-14-5M-Series-A-to-Replace-Manual-Financial-Statement-Preparation-for-Accounting-Firms-and-Enterprises.html); [Finextra](https://www.finextra.com/pressarticle/108928/inscope-raises-145m-for--ai-powered-financial-reporting) | 2023, founded by CPAs Mary Antony and Kelsey Gootnick (HQ not confirmed) — same source | Financial statements plus trial balances (semi-structured) |
| **Trullion** | AI accounting and audit platform covering lease accounting (ASC 842/IFRS 16/GASB 87), revenue recognition (ASC 606) and audit modules. In Dec 2025 added "Data Match" with AI-generated test logic that turns written audit procedures into automated tests. Every figure traces back to its source document | Corporate finance teams, controllers, external audit firms. Mid-market friendly | Funding not found for 2025. Thomson Reuters audit-ecosystem partnership (Dec 2025) — [Trullion product announcements](https://trullion.com/product-announcements/); [Crunchafi/TR](https://www.crunchafi.com/newsroom/thomson-reuters-partnership) | [background, unverified: ~2020, Tel Aviv / New York] | Unstructured: contracts and leases to accounting entries |
| **Midship** (acquired) | AI-native SOX automation. Ingests unstructured data, runs attribute tests autonomously (access reviews, bank reconciliations) and generates workpapers for external auditors | Enterprises with SOX programs | Founded 2024, Y Combinator. Acquired by Optro on May 6, 2026 — [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2026/05/08/optro-acquires-sox-automation-platform-midship/183013/); [PR Newswire](https://www.prnewswire.com/news-releases/optro-leads-the-global-audit-transformation-with-the-acquisition-of-ai-native-midship-302763559.html) | 2024 | Unstructured evidence ingestion |
| **Optro (formerly AuditBoard)** | Connected GRC platform: SOX, internal audit, risk, compliance, AI governance. AI scoping memos, automated vendor assessments. Says Midship integration automates "up to 87% of SOX program management" | Enterprise. More than 2,000 customers, about 50% of the Fortune 500, over $200M ARR (2024) | Acquired by Hg for more than $3B (2024) — [Hg](https://hgcapital.com/insights/auditboard-agrees-to-be-acquired-by-hg); rebranded to Optro in March 2026 — [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2026/03/09/auditboard-is-now-optro/179518/); acquired FairNow (AI governance) in fall 2025 — [Corporate Compliance Insights](https://www.corporatecomplianceinsights.com/auditboard-rebrands-to-optro/); AI features — [CPA Practice Advisor 2025](https://www.cpapracticeadvisor.com/2025/03/10/auditboard-adds-advanced-ai-capabilities-to-internal-audit-platform/157101/) | San Diego (started as SOXHUB, renamed AuditBoard in 2017) — [GRC Report](https://www.grcreport.com/post/auditboard-rebrands-as-optro-as-ai-reshapes-the-future-of-grc) | Mixed |
| **Workiva** | Financial reporting and GRC platform. In July 2026 launched three AI agents plus "Workiva Knowledge". The Tie-Out Agent checks figures across reports, flags discrepancies and explains variances | Enterprise (public company) | Public (NYSE: WK) — [Workiva IR](https://investor.workiva.com/news-releases/news-release-details/workiva-launches-specialized-ai-agents-and-intelligence-layer) | [background: Ames, Iowa] | Reports and documents plus structured data |
| **Safebooks AI** | "Agentic Revenue Integrity" layer for quote-to-revenue: continuous reconciliation, data controls and compliance checks. Has monitored more than $40B in transactions | Enterprise finance teams | $15M seed (Nov/Dec 2025) led by 10D, Propel Ventures and Mensch Capital — [PR Newswire](https://www.prnewswire.com/news-releases/safebooks-ai-raises-15-million-to-automate-revenue-data-integrity-for-enterprise-finance-teams-302633241.html); [Fintech Global](https://fintech.global/2025/12/12/safebooks-ai-raises-15m-for-finance-data-integrity-tech/) | Founded 2023 (same source). [background, unverified: Israeli founders] | Mostly structured (CRM, billing, ERP) plus contracts |
| **Celery** | AI audit agents for payroll, then revenue and expense monitoring. Detects fraud, compliance issues and inefficiencies "without integrations". Has processed more than $550M of payroll data and claims up to 91% less manual oversight | Labor-heavy industries. Dozens of US healthcare providers (mid-market) | $6.25M seed led by Team8 (May 2025). $9M raised in total — [Calcalist](https://www.calcalistech.com/ctechnews/article/rkhk00ogzel); [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2025/05/13/celery-secures-fresh-funding-to-anticipate-and-prevent-costly-financial-errors-before-they-happen/160278/) | 2023, Israel (Israeli startup) | Payroll and financial data; "no integration" suggests file- and document-based ingestion |
| **Pathlock** | Application GRC for ERP (SAP and others): segregation of duties, access governance, CCM across 100% of transactions with financial-impact analysis. Nexus is its AI-native platform. Partners with KPMG | Large ERP enterprises | PE-backed (details not found) — [Pathlock CCM](https://pathlock.com/products/continuous-controls-monitoring/); [ERP Today](https://erp.today/pathlock-kpmg-erp-access-governance-ai/) | n/a | Structured ERP only |
| **SafePaaS** | Controls automation, preventative controls, continuous monitoring across ERP; AI governance | Enterprise | n/a — [SafePaaS](https://www.safepaas.com/) | n/a | Structured ERP |
| **Nace AI** | "MetaModel 1" agents for credit, bills, invoices, expenses and procurement risk and compliance checks | Enterprise | $5M, led by General Catalyst (launched March 2025) — [Medium roundup](https://medium.com/@joycebirkins/6-ai-powered-audit-workflow-form-analysis-tools-for-finance-and-procurement-2025-1-10m-seed-5dc90f4d909c) (secondary source) | 2024, Palo Alto | Documents plus data |

**Cyber-GRC CCM (adjacent, briefly):** Gartner has a Continuous Controls Monitoring review category — [Gartner Peer Insights](https://www.gartner.com/reviews/market/continuous-controls-monitoring-ccm). Vendors named include Panaseer, Quod Orbis, Hyperproof, Sprinto (more than 3,000 organizations) and RegScale. These focus on SOC 2, ISO and IT security controls, not business-process supervision — [RiskRecon blog](https://blog.riskrecon.com/5-key-takeaways-inside-gartners-2025-market-guide); [Quod Orbis on Gartner](https://www.gartner.com/reviews/market/it-risk-management-solutions/vendor/quod-orbis/product/quod-orbis-continuous-controls-monitoring). Israeli GRC startup Vendict raised a $10M Series A — [Calcalist 2025 list](https://www.calcalistech.com/ctechnews/article/bkoi5iyujl).

**Regulatory tailwind:** One source says PCAOB amended AS 2201/AS 2101 take effect for fiscal years beginning on or after Dec 15, 2026, and that continuous controls monitoring is replacing point-in-time evidence — [Optro blog](https://optro.ai/blog/autonomous-control-testing) / [search snippet]. This is a vendor source and the PCAOB effective date should be verified. Grant Thornton on AI in SOX — [Grant Thornton](https://www.grantthornton.com/insights/articles/advisory/2026/the-power-of-ai-in-efficient-sox-compliance).

### Inferences
- Audit-firm-facing tools (Fieldguide, DataSnipper, MindBridge, Inscope, Trullion) are the best-funded AI-native cluster. Their buyer is the auditor, not the audited service business.
- Of the CCM tools, only DataSnipper, Trullion and Midship have strong "evidence document vs. figure" matching. Most CCM (Pathlock, SafePaaS, MindBridge's core) works on structured ERP and GL data.
- Consolidation pattern: incumbents (Optro/Hg, Thomson Reuters partnerships, Workiva) absorb AI-native point tools.

### Gaps
- Public pricing is not available for any of the audit or CCM vendors above; all appear to be quote-based.
- Could not confirm HQ or founding year for Fieldguide, DataSnipper or Trullion from a retrieved source, or any recent Trullion funding.
- Did not find a 2025–2026 Gartner Market Guide specifically for *financial* CCM (as opposed to cyber CCM).

---

## Q2. Who does contract-to-obligation extraction and post-signature compliance, and does anyone verify actual service delivery?

### Takeaway
Enterprise CLM leaders (Sirion, Icertis, Evisort/Workday, Ironclad) all extract obligations with AI. Sirion markets itself most explicitly on post-signature obligation, SLA and invoice compliance, including comparing "actual service delivery vs. promised SLA". That comparison depends on performance data fed in from ERP, ITSM or supplier reports. None was found that independently verifies physical service delivery from field evidence such as photos or site visits. The CLM market is consolidating through PE buyouts and strategic acquisitions (Haveli–Sirion 2026, Workday–Evisort 2024).

### Cited Findings

| Company | What it does | Target | Funding / status | Service-delivery verification? |
|---|---|---|---|---|
| **Sirion** | AI-native CLM with agentic AI (AskSirion orchestrating agents), obligation management, SLA tracking, post-signature workflows | Large enterprises, buy-side (procurement and IT outsourcing) | Majority investment by Haveli Investments completed (announced Feb 23, 2026; described as acquired Jan 2026) — [Business Wire](https://www.businesswire.com/news/home/20260223223160/en/Sirion-Announces-Completion-of-Majority-Investment-from-Haveli-to-Help-Accelerate-the-Future-of-AI-Native-Contract-Lifecycle-Management); ranked top in Spend Matters Fall 2025 SolutionMap for CLM and a Leader in IDC 2025 buy-side CLM — [AI Magazine](https://aimagazine.com/news/sirion-the-forefront-clm) | Partial. Sirion content describes linking obligations to live performance data from ERP, S2P and CRM, predictive breach alerts 7–14 days ahead, and "actual service delivery vs promised SLA" analysis — [Sirion SLA tracking](https://www.sirion.ai/library/contract-insights/post-signature-sla-tracking-contract-compliance-software/); [Sirion actual vs promised](https://www.sirion.ai/library/contract-insights/actual-vs-promised-sla-comparison/) (vendor marketing; relies on supplied performance data) |
| **Icertis** | Contract intelligence platform. "Icertis Vera" AI (2025) aims to "ensure contract obligations are met". Acquired Dioptra (AI contract review) in Nov 2025. Multi-year Microsoft partnership for agentic contracts | Large enterprise and public sector (BMW, McDonald's and the US Defense Logistics Agency are new logos) | Raised $50M in March 2025 to pay down debt. ARR "approaching $350M" (Aug 2025). Valuation figures conflict: $5B (2022 round, cited as 2025) vs. $2.8B (March 2025, secondary estimate) — [Sacra](https://sacra.com/c/icertis/); [Icertis record year](https://www.icertis.com/company/news/icertis-reports-record-year-of-new-business-growth/). Glassdoor reviews mention layoffs in 2025 (anecdotal) — [Glassdoor](https://www.glassdoor.com/Reviews/Icertis-layoff-Reviews-EI_IE683463.0,7_KH8,14.htm) | Obligation tracking; no evidence of independent delivery verification |
| **Evisort (Workday)** | AI contract intelligence and CLM, now part of Workday (procurement and finance suite) | Enterprise (Workday customers) | Acquisition closed Oct 8, 2024, for about $311M in cash — [Workday newsroom](https://newsroom.workday.com/2024-09-17-Workday-Signs-Definitive-Agreement-to-Acquire-Evisort); [Workday ARS FY2025](https://www.sec.gov/Archives/edgar/data/1327811/000110465925038024/tm2431104d2_ars.pdf); added to the Workday platform in March 2025 — [Enterprise Times](https://www.enterprisetimes.co.uk/2025/03/28/workday-adds-evisort-clm-and-ci-to-platform/) | Extraction and tracking only |
| **Ironclad** | AI CLM, strongest on sell-side and legal workflow | Mid-market to enterprise | Last priced round was a $150M Series E (Jan 2022) at a $3.2B valuation. No new 2025 round found — [Sacra](https://sacra.com/c/ironclad/); [Latka](https://getlatka.com/companies/ironclad) | No |
| **SpotDraft** | AI CLM: redlining, repository, clause extraction | Fast-growing and SMB/mid-market companies (India/US) | $54M Series B (Feb 2025) led by Vertex Growth and Trident Growth — [SpotDraft](https://www.spotdraft.com/blog/spotdraft-secures-54-million-to-lead-ai-contract-lifecycle-management) | No |
| **Concord, Juro, ContractSafe** | Lightweight CLM with AI extraction and renewal reminders | SMB through mid-market — [Concord](https://www.concord.app/comparisons/concord-spotdraft-comparison); [ContractSafe list](https://www.contractsafe.com/blog/best-clm-software) | n/a | Dates and renewals only |
| **CloudEagle.ai** | SaaS vendor management and SLA tracking | Mid-market IT/SaaS buyers — [CloudEagle](https://www.cloudeagle.ai/blogs/service-level-agreements-best-practices) | n/a | SaaS usage and licences, not field services |

- Generic "SLA monitoring agents" exist from agent builders such as ZBrain and Akira AI, but they are ITSM-focused — [ZBrain](https://zbrain.ai/agents/Information-Technology/all/Service-Level-Agreement-Monitoring/sla-compliance-monitoring-agent/).

### Inferences
- "Verify actual delivery" today means reconciling vendor-reported or system-logged KPIs (ITSM tickets, uptime, ERP receipts) against contract SLAs. It does not mean verifying physical work done with evidence like photos, GPS or checklists.
- Enterprise CLM leaders focus on large outsourcing and procurement contracts. Small service providers and their customers are served by lightweight CLMs that only track dates.

### Gaps
- Could not read Sirion's pages directly (egress blocked), so the depth of its "actual vs promised" capability is known only from page titles and snippets.
- No public pricing for Sirion, Icertis or Evisort. SMB CLMs publish tiered pricing, but it was not captured this session.

---

## Q3. Who does AI invoice-vs-contract / three-way matching for services (facility services, freight, telecom, legal)?

### Takeaway
Services invoice audit is organized by vertical. Freight audit is the hottest and best-funded area (Loop $95M Series C in 2026, $210M total; Freehand $75M; Trax Prizma). Legal bill review is consolidating into information giants (Wolters Kluwer bought Brightflag for €425M in 2025). Telecom and IT expense management is PE-owned incumbents (Tangoe, Calero) adding GenAI. Recovery audit belongs to PRGX. Facility-services invoice audit is served by FM service providers (Vixxo, whose AI checks work orders against GPS time on site and contracted rates) and by small proof-of-service apps. No well-funded AI-native player was found there.

### Cited Findings

**Freight / logistics**
- **Loop**: began in freight audit and payment and expanded into a logistics data platform. $95M Series C (Apr 17, 2026) led by Valor Equity Partners, with 8VC, Founders Fund, Index, J.P. Morgan Growth and others. $210M raised in total — [Business Wire](https://www.businesswire.com/news/home/20260417578056/en/Loop-Raises-$95M-Series-C-to-Scale-Its-AI-Platform-Across-the-Supply-Chain); new Logistics Data Platform (May 2026) — [Business Wire](https://www.businesswire.com/news/home/20260504771246/en/Loop-Launches-the-Logistics-Data-Platform-Powered-by-New-AI-Capabilities). Target: enterprise shippers. Evidence: unstructured freight documents (BOLs, invoices, rate confirmations).
- **Freehand**: "AI Teams" that run freight audit, payment and procurement end to end, from ingestion and matching through carrier dispute and ERP posting. Customers include Meta, Unilever and J&J. $75M co-led by Battery Ventures and NewRoad (reported as Series C). Claims to recover 1.5–2.5% of freight spend — [Freehand PR](https://www.freehand.ai/press-release/freehand-raises-75m-to-scale-ai-teams-managing-supply-chain-spend-for-fortune-500-companies); [Freehand blog](https://www.freehand.ai/articles/best-ai-freight-audit-and-payment-software).
- **Trax Technologies**: launched the Prizma AI freight audit platform (AI Extractor for documents, AI Audit Optimizer) in Aug 2025. Enterprise global shippers — [Trax](https://www.traxtech.com/blog/ai-powered-freight-audit-year-in-review).
- **Cass Information Systems**: public payment and audit provider covering freight, telecom and utility expense — [logisticsmgmt](https://www.logisticsmgmt.com/article/freight_payment_2026_where_ai_expertise_and_global_integration_converge) (mentioned in search results).

**Legal bill review**
- **Brightflag**: AI legal bill review and e-billing. Claims 10% spend reduction and 80% less admin work. Acquired by Wolters Kluwer for €425M (about $482M), closed June 2025. Wolters Kluwer already runs TyMetrix 360° and LegalVIEW BillAnalyzer (over $4B in invoices a year) — [Bloomberg Law](https://news.bloomberglaw.com/legal-ops-and-tech/wolters-kluwer-to-acquire-legal-spend-software-maker-brightflag); [Brightflag](https://brightflag.com/legal-bill-review/); [William Blair](https://www.williamblair.com/News/Brightflag-and-Wolters-Kluwer-Transaction). Other competitors: Thomson Reuters Legal Tracker and Mitratech Managed Bill Review — [Slashdot comparison](https://slashdot.org/software/comparison/Brightflag-vs-Mitratech-Managed-Bill-Review-vs-Thomson-Reuters-Legal-Tracker/). Target: corporate legal departments (enterprise). Evidence: unstructured LEDES and narrative time entries checked against outside-counsel billing guidelines.

**Telecom / IT expense**
- **Tangoe**: telecom and IT expense management with invoice audit and optimization. Tangoe AI Assistant (GenAI natural-language queries) and a Tangoe Tax Audit service. Reported first-half 2026 momentum with larger enterprises. PE-owned (Clearlake/Vector per older source) — [AOL/PR](https://www.aol.com/articles/tangoe-reports-first-half-2026-130100000.html); [Tangoe invoice audit](https://www.tangoe.com/telecom-expense-management/invoice-audit-optimization/); [True Blue Partners](https://truebluepartners.com/clearlake-vector-tangoe-inc-spotlight/).
- **Calero** (merged with MDSL in 2019; acquired Network Control in 2022 for mid-market TEM). PE-backed, Rochester, NY — [Amalgam Insights](https://amalgaminsights.com/2022/08/04/calero-mdsl-acquires-network-control-to-support-mid-market-tem-demand/); [PitchBook](https://pitchbook.com/profiles/company/60648-13). Lightyear is a newer challenger — [Lightyear](https://lightyear.ai/tips/tangoe-vs-calero).

**Recovery audit / general supplier contract compliance**
- **PRGX**: recovery audit applying AI across source-to-pay to "enforce contract value". Analyzes $2.3T of annual client spend and has more than 50 years of history. Launched an AI AP platform (Supplier Connect). Large retail and enterprise customers; contingency-fee model typical of recovery audit [background, unverified] — [PRGX](https://www.prgx.com/); [PRGX guide](https://www.prgx.com/guides/supplier-contract-compliance-audits-guide/); [SSON](https://sharedserviceslink.com/news/prgx-unveils-ai-powered-ap-platform).
- **GEP**: AI-agent real-time invoice auditing inside its procurement suite (enterprise) — [GEP](https://www.gep.com/blog/technology/ai-agent-driven-real-time-invoice-auditing).

**Facility services**
- **Vixxo** (FM service provider): its AI invoice auditing cross-checks each work-order line against GPS-verified technician time on site, market parts pricing, pre-negotiated trade labor rates and contract compliance rules — [Vixxo](https://www.vixxo.com/facilities-management-news/can-ai-detect-overcharges-in-facilities-management-invoices) (snippet only; page blocked).
- Proof-of-service apps for cleaning and field teams: Provvio, WizyVision, FreshOps, Serfy and Tiliter. They offer GPS check-ins, timestamped photos, checklists and, in Tiliter's case, AI "cleanliness scoring" from inspection photos. They document work but do not audit it against invoices or contracts — [Provvio](https://provvio.com/cleaning); [WizyVision](https://wizyvision.com/proof-of-service); [FreshOps](https://www.getfreshops.com/news/photo-verifications-build-trust-for-cleaning-business/); [Tiliter](https://www.tiliter.com/blog/how-to-prove-cleaning-was-completed-with-photo-evidence); [Serfy](https://serfy.io/blog/the-2026-guide-to-digital-proof-of-work-for-contractors).
- PayKeeper: AI verification for construction fund control (draw verification) — [PayKeeper](https://paykeeper.com/ai-verifications-for-fund-control/).

**Expense and AP audit (horizontal)**
- **AppZen**: AI expense audit (computer vision on receipts, checks against policy, weather and FX data; 42 languages and 97 countries), Autonomous AP, and Mastermind AI Studio agents. More than 500 brands, including Amazon and Salesforce. $180M Series D led by Riverwood (Sep 22, 2025). $283M raised in total. Priced on transaction volume and agents (per Sacra) — [Fintech Global](https://fintech.global/2025/09/22/appzen-secures-180m-to-scale-autonomous-finance-ai/); [Foley](https://www.foley.com/news/2025/09/foley-represents-riverwood-capital-as-lead-investor-in-180m-funding-for-appzen/); [Sacra](https://sacra.com/c/appzen/). [background, unverified: founded 2012, San Jose]
- **Oversight**: AI spend monitoring and financial audit that monitors 100% of enterprise spend (T&E, card, AP) for fraud, waste and abuse. Launched a next-gen "Finance Risk Intelligence" platform in Dec 2025. Founded 2003. Backed by TCV (PE) — [PR Newswire](https://www.prnewswire.com/news-releases/oversights-next-generation-ai-platform-ushers-in-the-era-of-finance-risk-intelligence-302642909.html); [Crunchbase](https://www.crunchbase.com/organization/oversight-systems). [background, unverified: Atlanta]

### Inferences
- Freight is the only services vertical with multiple AI-native, venture-scale players (Loop, Freehand) because freight invoices are high-volume, rate-card-based and document-heavy.
- Facility services (cleaning, maintenance, security, landscaping) have the evidence-capture layer (photo and GPS apps) and some FM integrators (Vixxo) doing invoice audit. No independent AI product was found that combines the contract, work evidence (photos, logs) and invoice into one verdict.

### Gaps
- No funding or size data found for Vixxo, the proof-of-service apps or Lightyear.
- Legal bill review AI-native startups (other than Brightflag) were not researched in depth.
- Healthcare payment integrity (Cotiviti and others) and utility bill audit are adjacent and not covered.

---

## Q4. Which serve SMBs or small service companies versus only large enterprises?

### Takeaway
Nearly every AI audit, CCM, contract-compliance and services-audit vendor found targets enterprises or audit firms. SMB coverage comes mostly from spend platforms (Ramp and Brex policy agents), lightweight CLMs (SpotDraft, Concord, Juro, ContractSafe) and proof-of-service field apps. None of these combines contract obligations with evidence of delivered work.

### Cited Findings
- **Ramp**'s Policy Agent applies written expense policies to every card transaction and reimbursement. It uses RAG to cite the exact policy text and considers receipts, memos, attendees and trip data. Early customers reported 99% accuracy. Ramp also launched agents for controllers in July 2025 — [Ramp Help Center](https://support.ramp.com/hc/en-us/articles/44072387128979-Policy-Agent-Overview); [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2025/07/10/ramp-introduces-ai-agents-suited-for-controllers/164684/).
- **Brex** AI agents write memos, fetch receipts and answer policy questions — [Brex](https://www.brex.com/platform/intelligent-finance).
- SpotDraft targets SMB and fast-growing companies; Concord spans SMB to enterprise — [SpotSaaS compare](https://www.spotsaas.com/compare/contractsafe-vs-spotdraft-vs-juro); [Concord SMB guide](https://www.concord.app/blog/contract-management-software-small-business).
- Celery serves mid-sized US healthcare providers (labor-heavy) — [Calcalist](https://www.calcalistech.com/ctechnews/article/rkhk00ogzel).
- Enterprise-only examples: Optro (about 50% of the Fortune 500), Freehand (Fortune 500), AppZen (more than 500 large brands), Icertis and Sirion (Fortune-ranked), Pathlock (multi-ERP) — sources cited above.
- Audit-firm tools (Fieldguide, DataSnipper, Inscope, Trullion, MindBridge) serve CPA firms of all sizes. Their end beneficiaries include SMB audit clients, but the SMB is not the buyer.

### Inferences
- Opportunity: small and mid-sized service companies (cleaning, security, maintenance and logistics subcontractors) and their mid-sized customers lack an affordable tool that turns a contract into obligations and checks invoices and field evidence against it.
- SMB buyers are reached through spend-card platforms (Ramp/Brex) that bundle AI audit for free or at low cost [pricing not verified this session], which makes it hard to charge standalone for expense auditing.

### Gaps
- Public price lists were not captured for Ramp, Brex, SpotDraft, Concord or the proof-of-service apps.

---

## Q5. Recent funding, acquisitions and consolidation (2024–2026)

### Takeaway
Late-stage capital flows to agentic audit and freight audit, while strategic buyers and PE firms roll up GRC, CLM and legal-spend assets.

### Cited Findings
**Funding (chronological)**
- DataSnipper: $100M Series B, $1B valuation (Feb 2024) — [Fortune](https://fortune.com/2024/02/01/data-snipper-1-billion-valuation-unicorn-funding-round-ai-audit-accounting/)
- SpotDraft: $54M Series B (Feb 2025) — [SpotDraft](https://www.spotdraft.com/blog/spotdraft-secures-54-million-to-lead-ai-contract-lifecycle-management)
- Icertis: $50M (Mar 2025, for debt paydown) — [Sacra](https://sacra.com/c/icertis/)
- Nace AI: $5M (Mar 2025) — [Medium](https://medium.com/@joycebirkins/6-ai-powered-audit-workflow-form-analysis-tools-for-finance-and-procurement-2025-1-10m-seed-5dc90f4d909c)
- Celery: $6.25M seed (May 2025) — [Calcalist](https://www.calcalistech.com/ctechnews/article/rkhk00ogzel)
- AppZen: $180M Series D (Sep 2025) — [Fintech Global](https://fintech.global/2025/09/22/appzen-secures-180m-to-scale-autonomous-finance-ai/)
- Safebooks AI: $15M seed (Nov/Dec 2025) — [PR Newswire](https://www.prnewswire.com/news-releases/safebooks-ai-raises-15-million-to-automate-revenue-data-integrity-for-enterprise-finance-teams-302633241.html)
- Fieldguide: $75M Series C at $700M (Feb 2026) — [Fortune](https://fortune.com/2026/02/02/goldman-sachs-fieldguide-accounting-cpa-ai-software-platform-venture-capital/)
- Inscope: $14.5M Series A (Feb 2026) — [GlobeNewswire](https://www.globenewswire.com/news-release/2026/02/20/3242123/0/en/Inscope-Raises-14-5M-Series-A-to-Replace-Manual-Financial-Statement-Preparation-for-Accounting-Firms-and-Enterprises.html)
- Loop: $95M Series C (Apr 2026) — [Business Wire](https://www.businesswire.com/news/home/20260417578056/en/Loop-Raises-$95M-Series-C-to-Scale-Its-AI-Platform-Across-the-Supply-Chain)
- Freehand: $75M (2026, date not confirmed) — [Freehand](https://www.freehand.ai/press-release/freehand-raises-75m-to-scale-ai-teams-managing-supply-chain-spend-for-fortune-500-companies)

**M&A and consolidation**
- Hg acquires AuditBoard for more than $3B (2024), then rebrand to Optro (Mar 2026), FairNow acquisition (fall 2025) and Midship acquisition (May 2026) — [Hg](https://hgcapital.com/insights/auditboard-agrees-to-be-acquired-by-hg); [Corporate Compliance Insights](https://www.corporatecomplianceinsights.com/optro-acquires-ai-auditing-platform-midship/)
- Workday acquires Evisort for about $311M (closed Oct 2024) — [SEC ARS](https://www.sec.gov/Archives/edgar/data/1327811/000110465925038024/tm2431104d2_ars.pdf)
- Wolters Kluwer acquires Brightflag for €425M (closed June 2025) — [Bloomberg Law](https://news.bloomberglaw.com/legal-ops-and-tech/wolters-kluwer-to-acquire-legal-spend-software-maker-brightflag)
- Icertis acquires Dioptra (Nov 2025) — [Sacra](https://sacra.com/c/icertis/)
- Haveli takes a majority stake in Sirion (Jan/Feb 2026) — [Business Wire](https://www.businesswire.com/news/home/20260223223160/en/Sirion-Announces-Completion-of-Majority-Investment-from-Haveli-to-Help-Accelerate-the-Future-of-AI-Native-Contract-Lifecycle-Management)
- DataSnipper acquires UpLink — [DataSnipper](https://www.datasnipper.com/resources/datasnipper-acquisition-uplink-launch-documine)
- Thomson Reuters audit-ecosystem partnerships including Trullion (Dec 2025) and investment in Fieldguide — [Crunchafi](https://www.crunchafi.com/newsroom/thomson-reuters-partnership); [Fortune](https://fortune.com/2026/02/02/goldman-sachs-fieldguide-accounting-cpa-ai-software-platform-venture-capital/)

### Inferences
- Information and content incumbents (Thomson Reuters, Wolters Kluwer, Workday) are buying AI-native audit and spend tools, and PE (Hg, Haveli, TCV) owns key platforms. Likely exits for new AI supervision startups are acquisition by these groups.

### Gaps
- Exact date of Freehand's round and total raised were not confirmed. No 2025–2026 funding news found for Oversight, MindBridge (beyond the $82.2M total) or Ironclad.

---

## Q6. Where are the clear gaps (segments, languages, evidence types)?

### Takeaway
The clearest white space is AI supervision of *outsourced physical services*: turning the service contract into obligations, then checking field evidence (photos, GPS, logs, checklists, free text) and invoices against it. This matters most for SMB and mid-market buyers and sellers, and in non-English markets. Existing players either audit structured ERP data, audit finance documents for auditors, or track contract dates and SLA KPIs fed from IT systems.

### Cited Findings
- CCM and GRC tools cover ERP and financial controls (Pathlock, SafePaaS, MindBridge) or cyber controls (Panaseer, Sprinto and others), not operational service delivery — [Pathlock](https://pathlock.com/products/continuous-controls-monitoring/); [Gartner CCM](https://www.gartner.com/reviews/market/continuous-controls-monitoring-ccm).
- CLM "actual vs promised SLA" depends on performance data integrated from ERP, S2P or CRM systems — [Sirion](https://www.sirion.ai/library/contract-insights/actual-vs-promised-sla-comparison/) (snippet).
- Proof-of-service apps capture photos and GPS but are workflow tools for the service provider, not contract/invoice auditors — [Provvio](https://provvio.com/proof-of-service-software); [Tiliter](https://www.tiliter.com/blog/how-to-prove-cleaning-was-completed-with-photo-evidence).
- Language: AppZen advertises 42 languages for expense receipts — [Sacra](https://sacra.com/c/appzen/). No vendor in this scan advertised Hebrew or other small-language contract-obligation extraction. Israeli players found (Celery, Safebooks, Trullion, Vendict) target the US market — [Calcalist](https://www.calcalistech.com/ctechnews/article/rkhk00ogzel).

### Inferences
- **Segment gap**: SMB and mid-market service buyers (property managers, municipalities, schools, clinics) and small service vendors (cleaning, security, maintenance, catering, subcontracted logistics).
- **Evidence gap**: few vendors reason jointly over multimodal evidence (photos, shift logs, WhatsApp/text reports, sensor data) against contract clauses. Freight (documents) and legal (time narratives) are the text-only exceptions.
- **Language and regional gap**: non-English (e.g. Hebrew, Arabic) contract-to-obligation extraction and local public-procurement compliance appear unserved by the leaders. This inference comes from the absence of results and was not exhaustively verified.
- **Public sector**: Icertis wins large US federal agencies. Municipal and local-government service-contract supervision looks underserved (inference).

### Gaps
- No systematic search of European, Asian or Middle-East local vendors (e.g. German, French or Israeli-market-focused tools). A targeted local-language search would be needed to confirm the language gap.
- No analyst report quantifying the size of the "service delivery verification" market was found.
