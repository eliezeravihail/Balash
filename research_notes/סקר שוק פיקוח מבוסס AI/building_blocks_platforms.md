# Horizontal platforms and building blocks for a generic "AI supervision framework of composable blocks" (as of Sept 2026)

Reference concept being compared against ("the concept"): (1) canonical data model of entity / commitment-obligation / event / evidence over a company's data lake; (2) LLMs that compile contracts, procedures and regulations into structured, machine-checkable rules; (3) LLMs that judge unstructured evidence (documents, photos, messages); (4) a deterministic rule/check engine; (5) findings with provenance plus a human review queue; (6) reusable blocks (invoice parser, GPS stop/visit detection, entity resolution).

Method note: research done via web search on 2026-09-28. Direct page fetches to several vendor sites (norm.ai, reducto.ai, bdemerson.com) were blocked by the network egress proxy, so many facts below come from search-result summaries of the cited pages rather than a full read. Pricing figures from third-party review/comparison sites (and from vendors' comparison pages about competitors) should be treated as indicative and re-verified before quoting. Items dated before 2026 are marked.

---

## 1. Ontology-based operational platforms (Palantir Foundry/AIP and analogues): how close, and are they accessible to SMB service companies?

### Takeaway
Palantir Foundry/AIP is architecturally the closest existing product to the concept (ontology of objects + links + actions/functions + AIP agents over enterprise data), but it is priced and sold for large enterprises (first contracts typically $0.5M–$2M/yr) and is not realistically accessible to SMB service companies beyond a free, capped developer tier. The most important new analogue is Microsoft Fabric IQ "Ontology" (preview), which ships entity types, relationships, rules and actions that agents can use inside Fabric; there are also smaller "sovereign/open" Foundry alternatives (Scrydon, digetiers dAP, Timbr) and knowledge-graph vendors (Stardog, Neo4j, etc.). None of them ship the obligation/evidence/finding semantics out of the box — they are generic modeling substrates.

### Cited Findings
- Palantir does not publish AIP pricing; commercial Foundry/AIP engagements reportedly range from ~$250K/yr for a narrow single-use-case deployment to several million for an enterprise program, with most first contracts at mid-market and large enterprises between $500K and $2M annually; AIP ships inside the Foundry subscription with usage-based compute on top and model inference billed via the serving provider; platform subscriptions "typically starting in the mid six figures per year" (third-party analysis, not Palantir-confirmed) — [bdemerson.com "What Palantir Costs"](https://www.bdemerson.com/article/palantir-cost)
- Palantir offers a free AIP Developer Tier: "Developer Tier is a free tier of Foundry / AIP and you won't be charged," with limited capacity hard-capped so users can't accidentally incur charges — [Palantir Developer Community: Developer Tier Billing and Usage](https://community.palantir.com/t/developer-tier-billing-and-usage/1074); [Build with AIP](https://build.palantir.com/)
- Third-party commentary cautions the free/low-cost tiers "do not resemble the contracts an enterprise signs" — [bdemerson.com](https://www.bdemerson.com/article/palantir-cost)
- Palantir positions the Ontology as organizing enterprise data "into a connected operational framework"; Palantir blog on connecting agents to decisions via the Ontology — [Palantir blog: Connecting Agents to Decisions](https://blog.palantir.com/connecting-agents-to-decisions-277dee8ddb40)
- Palantir's scale: raised 2026 revenue guidance to ~$8.15B, with US commercial revenue expected >$3.42B (+134%) (as summarized by search results from financial press) — [TheStreet](https://www.thestreet.com/investing/palantirs-latest-ai-move-reveals-a-much-bigger-ambition); [Palantir Q4 2025 investor presentation](https://investors.palantir.com/files/Palantir%20-%20Q4%202025%20Investor%20Presentation.pdf). Stock reportedly down ~35% in 2026 amid valuation scrutiny — [Dealroom news](https://app.dealroom.co/news/feed/palantir-stock-down-35-in-2026-as-ontology-driven-ai-platform-faces-valuation-scrutiny)
- Palantir has "AI FDEs" — AIP-native agents that connect data sources, transform data, create ontologies and functions, and build applications (reduces the forward-deployed-engineer cost that historically kept it enterprise-only) — per search summary of [Yahoo Finance: Palantir ontology edge](https://finance.yahoo.com/technology/ai/articles/palantirs-ontology-edge-redefining-ai-143300981.html)
- Microsoft Fabric IQ "Ontology (preview)" defines "core business entities, relationships, properties, rules, and actions"; rules "transform live business context in the ontology into operationalized outcomes" via alerts and automated actions; agents (Fabric data agents, Operations Agent, Foundry, M365 Copilot) can consume the ontology as a knowledge source and evaluate conditions/take actions — [Microsoft Learn: What is Ontology (preview)](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview); [Fabric IQ overview](https://learn.microsoft.com/en-us/fabric/iq/overview); [Agent integration options](https://learn.microsoft.com/en-us/fabric/iq/ontology/concepts-agent-integration); [Fabric blog: What's next for Fabric IQ Ontology](https://blog.fabric.microsoft.com/sr-latn-rs/blog/whats-next-for-fabric-iq-ontology-the-operational-context-that-powers-your-ai-agents-preview?ft=All)
- Smaller Foundry-style alternatives cited in vendor/analyst listicles: Timbr (semantic layer/ontology modeled in SQL), Elementum (AI workflow orchestration independent of a proprietary ontology), digetiers dAP (ontology-driven operational intelligence, less lock-in), Scrydon (sovereign Foundry alternative: semantic model on open table formats, grounds AI agents, runs in customer perimeter), plus knowledge-graph platforms Neo4j, TigerGraph, Stardog, Ontotext GraphDB — [Stardog: 8 Best Palantir Alternatives](https://www.stardog.com/blog/best-palantir-competitors-alternatives/); [Timbr on Medium](https://medium.com/timbr-ai/palantir-timbr-the-enterprise-race-to-make-data-ai-ready-4b26a1efe89c); [digetiers](https://www.digetiers.com/en/insights/library/palantir-foundry-alternatives); [Scrydon](https://scrydon.com/platform/compare/palantir-foundry-alternative/); [Elementum](https://www.elementum.ai/blog/palantir-alternative). (Note: these are self-promotional sources.)
- Open-source Foundry-like options are discussed by Dashjoin — [Dashjoin: Demystifying Palantir](https://dashjoin.medium.com/demystifying-palantir-features-and-open-source-alternatives-ed3ed39432f9)

### Inferences
- Closeness to the concept: Palantir = high on (1) canonical model, (4) actions/functions, (5) human-in-loop apps; medium on (2)/(3) (AIP can do it but you build it); low on (6) domain blocks (no stock "GPS stop detection" or "weigh-ticket parser" as products). Fabric IQ = similar shape, earlier maturity, but far cheaper entry for companies already on Microsoft/Power BI — plausibly the most realistic "ontology substrate" for an SMB-oriented vendor to build on or to compete with.
- For SMB service companies (dozens to low hundreds of employees), Palantir is out of reach on price and implementation effort; the realistic route is a vertical product that embeds an opinionated ontology (entity/obligation/event/evidence) rather than a generic modeling tool the customer must configure.
- The "commitment/obligation" and "evidence" object types are not first-class in any of these platforms; they would be user-defined object types. That semantic layer (and the rule-compilation workflow on top) is the differentiation space.

### Gaps
- No Palantir-published price list; the $250K–$2M figures are a single third-party estimate. Could not fetch the page directly (egress blocked).
- Fabric IQ Ontology pricing (it rides on Fabric capacity SKUs) and GA date not confirmed.
- Funding/size of Scrydon, digetiers, Timbr, Elementum not researched.

---

## 2. LLM-driven regulatory / policy-as-code compliance engines (Norm Ai, Greenlite/Bretton, Hebbia-type, others)

### Takeaway
The best-funded "text rules -> machine-checkable checks" companies are vertical to financial services and legal: Norm Ai (regulations/policies compiled into a proprietary decision-tree language executed by LLM agents; $1.2B valuation, June 2026) and Bretton AI (formerly Greenlite; AML/KYC agents for banks, $75M Series B Feb 2026). Kognitos is the clearest horizontal analogue of "natural-language rules executed deterministically" (neurosymbolic "English as code"). Close functional analogues in back-office finance/logistics — Ramp Policy Agent, AppZen, Loop, Icertis Vera Obligations — prove the "policy + evidence -> finding" loop works commercially, but each is locked to one domain (expenses, AP, freight, contracts). None targets SMB field-service/operations supervision across arbitrary data.

### Cited Findings
**Norm Ai**
- Raised $48M in March 2025 (led by Coatue; Craft, Vanguard, Blackstone, Bain Capital, New York Life, Citi, TIAA, Marc Benioff), total then $87M — [SiliconANGLE, Mar 2025](https://siliconangle.com/2025/03/11/ai-agent-powered-compliance-automation-startup-norm-ai-raises-48m/); [PR Newswire](https://www.prnewswire.com/news-releases/norm-ai-secures-48-million-to-transform-regulations-into-compliance-ai-agents-302398351.html)
- Norm built "a proprietary programming language representing corporate policies and government regulations in decision trees that can be understood by LLMs," enabling "Regulatory AI Agents" that automate compliance checks on AI-generated content, legal agreements, communications, marketing materials — [SiliconANGLE](https://siliconangle.com/2025/03/11/ai-agent-powered-compliance-automation-startup-norm-ai-raises-48m/)
- Nov 2025: additional $50M from Blackstone and launch of "Norm Law", an AI-native law firm; total funding >$140M — [LawNext](https://www.lawnext.com/2025/11/norm-ai-raises-50-million-from-blackstone-launches-ai-native-law-firm.html); [FinTech Global](https://fintech.global/2025/11/21/blackstone-backs-norm-ai-with-fresh-50m-investment/)
- June 2026: $120M Series C at $1.2B valuation led by Khosla Ventures (per search summary of Norm's own announcement; page could not be fetched) — [Norm Ai announcement](https://www.norm.ai/resources/norm-ai-raises-20-million-at-a-1-2-billion-valuation); [Angel Investors Network](https://angelinvestorsnetwork.com/venture-capital/norm-ai-legal-tech-series-c-unicorn)
- Buyers: large financial institutions / asset managers (investor base described as representing >$15T AUM) — [PR Newswire](https://www.prnewswire.com/news-releases/norm-ai-secures-48-million-to-transform-regulations-into-compliance-ai-agents-302398351.html)

**Greenlite AI -> Bretton AI**
- May 2025: $15M Series A (Greylock, Thomson Reuters Ventures, Canvas), total $20M; AI agents for KYC/AML/sanctions used by OCC-regulated banks, SEC broker-dealers; customers include Ramp, Mercury, Betterment, Gusto; "Trust Infrastructure" embeds US federal banking regulations into agents — [BusinessWire, May 2025](https://www.businesswire.com/news/home/20250521200064/en/Greenlite-AI-Raises-$15M-Series-A-to-Help-Banks-and-Fintechs-Fight-Financial-Crime-with-Trusted-AI-Workforce); [FinTech Global](https://fintech.global/2025/05/22/regtech-innovator-greenlite-ai-secures-15m-to-scale-trusted-ai-compliance-agents/)
- Feb 2026: rebranded to Bretton AI with a $75M Series B led by Sapphire Ventures (plus Canvas, Greylock, Thomson Reuters Ventures, YC, TIAA Ventures); founded 2023; covers transaction analysis, KYC/KYB, AML & sanctions investigations, ongoing monitoring — [BusinessWire, Feb 2026](https://www.businesswire.com/news/home/20260209387593/en/Bretton-AI-Raises-$75M-Series-B-Rebrands-from-Greenlite-AI-to-Build-the-AI-Standard-for-Financial-Crime); [FinTech Futures](https://www.fintechfutures.com/venture-capital-funding/greenlite-ai-rebrands-as-bretton-ai-secures-75m-series-b)

**Hebbia (document-analysis "matrix" for finance/legal)**
- Series B $130M led by a16z at ~$700M valuation, July 2024 (older info); total ~$161M — [Sacra](https://sacra.com/c/hebbia/); [Forge](https://forgeglobal.com/hebbia_ipo/)
- Reported ~$24.6M revenue as of Sept 2025 (Latka estimate — low-reliability source) — [GetLatka](https://getlatka.com/companies/hebbia.com)
- Inference on fit: Hebbia is a question-over-documents grid, not a rule engine; relevant as a UX pattern (row = document, column = question/check with cited answer).

**Kognitos (horizontal, "English as code")**
- Neurosymbolic platform: plain-English business rules "are the executable code"; a "Symbolic Executor" runs them deterministically with a complete audit trail; used for AP, finance, healthcare, ops, supply chain, logistics — [Kognitos site](https://www.kognitos.com/); [Yahoo Finance, June 2025 launch](https://finance.yahoo.com/news/kognitos-launches-neurosymbolic-ai-platform-130000313.html)
- $25M Series B (June 2025); total ~$51.8M (Tracxn); earlier $20M Series A led by Khosla — [Tracxn](https://tracxn.com/d/companies/kognitos/__87YyupNd4wK8W-c2nD9swjpVwN4FBUuFwQnhE98Bp2M); [Kognitos news](https://www.kognitos.com/news/kognitos-raises-20m-in-series-a-funding-round-led-by-khosla-ventures/)

**Domain analogues of "policy + evidence -> finding + review queue"**
- Ramp Policy Agent: applies the customer's written expense policy to every transaction; interprets semantically, uses RAG to cite exact policy text, evaluates receipts/memos/attendees/trip context; outputs recommendation categories (e.g., "Approval recommended", "Requires review"); Ramp claims 3 of 4 in-policy expenses approved without human review, 7x more out-of-policy spend caught; GA to Ramp Plus customers — [Ramp support: Policy Agent overview](https://support.ramp.com/policy-agent-overview); [Ramp blog: GA launch](https://ramp.com/blog/ramp-policy-agent-ga-launch); [ZenML LLMOps database case study](https://www.zenml.io/llmops-database/building-trustworthy-llm-agents-for-automated-expense-management)
- AppZen: "AI auditor" for expenses/AP; audits 100% of expense reports in real time; Policy Enforcement Agent; Receipt Itemization Agent (CV + NLP); cross-checks receipts against online sources; Workday integration completed March 2026; raised a $180M growth round led by Riverwood (date not confirmed in results) — [AppZen](https://www.appzen.com/ai-for-expense-audit); [CPA Practice Advisor, Mar 2026](https://www.cpapracticeadvisor.com/2026/03/17/appzen-completes-workday-integration-for-ai-powered-expense-audit/179868/)
- Loop (logistics): $95M Series C April 2026 (Valor, 8VC, Founders Fund, Index, J.P. Morgan Growth); converts invoices, contracts, PDFs, spreadsheets into structured data (DUX 2.0 engine, >200 data points per shipment); reconciles carrier invoices against contracts, finds overcharges; "Exception Agent" handles disputes autonomously; launched a "Logistics Data Platform" May 2026 — [BusinessWire, Apr 2026](https://www.businesswire.com/news/home/20260417578056/en/Loop-Raises-$95M-Series-C-to-Scale-Its-AI-Platform-Across-the-Supply-Chain); [SiliconANGLE](https://siliconangle.com/2026/04/17/supply-chain-ai-startup-loop-secures-95m-investment/); [FreightWaves](https://www.freightwaves.com/news/loop-logistics-data-platform)
- Icertis Vera Obligations: generative AI discovers, extracts and classifies contract obligations into action-oriented tasks; agentic monitoring triggers alerts/escalations when obligations are at risk; cross-references invoices against contract terms — [Icertis Vera Obligations](https://www.icertis.com/products/operate/vera-obligations/); [Icertis contract performance](https://www.icertis.com/products/platform/contract-performance/)
- MindBridge: ingests GL data, applies ML to test 100% of financial transactions for anomalies (statistical, not rule-compilation) — per [DSG.AI continuous auditing tools list](https://www.dsg.ai/blog/continuous-auditing-tools)
- Big-4 direction: EY launched an enterprise agentic AI platform across global Assurance in April 2026 (risk identification, evidence collection, controls testing) — per search summary of [DSG.AI](https://www.dsg.ai/blog/continuous-auditing-tools) (secondary source)

### Inferences
- Norm Ai's "regulation -> intermediate decision-tree language -> LLM agent" is the closest published analogue of the concept's rule-compilation layer, but it targets Fortune-500 financial compliance with enterprise pricing (not public).
- Kognitos is the closest horizontal match for "NL rule -> deterministic execution + audit trail," but it is a process-automation tool (do the work), not a supervision tool (check that others did the work and produce findings over event/evidence data).
- The commercial proof points (Ramp, AppZen, Loop, Icertis) show buyers pay for "policy/contract compiled into checks + evidence judged by LLM + exceptions to humans" — but each owns only one evidence type and one obligation type. A cross-domain framework for operations (field services, logistics subcontractors, facility contracts) is not served by any of them.

### Gaps
- No public pricing for Norm Ai, Bretton, Kognitos, Icertis, AppZen.
- Did not find a well-known startup selling "compile any SOP/contract/regulation into checks over your operational data" to SMBs; absence of evidence is not proof, but multiple searches returned only AI-agent-observability tools (monitoring the agents themselves), not business-operations supervision.
- AppZen $180M round date/valuation not confirmed.

---

## 3. Intelligent document processing (IDP) / extraction building blocks: capabilities and pricing for invoices, weigh tickets, certificates

### Takeaway
Document extraction is a commoditized, price-competitive layer in 2026: LLM-native APIs (Reducto, Extend, LlamaParse, Unstructured) charge roughly $0.001–$0.06 per page depending on mode; hyperscaler prebuilt models (Azure invoice ~$10/1K pages, Google custom extractor ~$30/1K pages) are cheaper still at scale; workflow IDP (Rossum, Nanonets) is priced per workflow/volume and aimed at AP teams. Invoices are a solved prebuilt use case; weigh tickets and certificates need schema-based "custom extraction" which all LLM-native vendors support without templates. Buy/wrap, don't build.

### Cited Findings
- Reducto: $108M total funding after a $75M Series B led by a16z (Benchmark, First Round, YC, BoxGroup) — [Reducto blog: Series B](https://reducto.ai/blog/reducto-series-b-funding)
- Reducto pricing (since Sept 2026, per product): Parse $0.01/page (r-1, preview), Extract $0.02/page, Deep Extract $0.04/page (parsing included), per-field surcharge above 100 fields/page; 15,000 free credits; batch queue 20% off with 12-hour SLA — [Reducto pricing](https://reducto.ai/pricing); [Reducto: Best document processing APIs 2026](https://llms.reducto.ai/best-document-processing-apis-2026) (page could not be fetched directly; figures from search summary)
- Extend: $17M seed+Series A June 2025 led by Innovation Endeavors (YC, Homebrew, angels) (older info); LLM-based classification, extraction and validation; targets healthcare, finance, logistics — [BusinessWire, Jun 2025](https://www.businesswire.com/news/home/20250617790342/en/Extend-Raises-$17-Million-to-Build-the-Document-Processing-Cloud); [SiliconANGLE](https://siliconangle.com/2025/06/17/extend-gets-17m-funding-boost-speed-accuracy-document-processing-llms/)
- Extend pricing: 10,000 free credits; $0.0125/credit PAYG, no platform fee; Scale tier $500/mo with 50,000 credits then $0.01/credit; Light Parse 0.5 credits/page (~$0.006), Performance Parse 2 credits/page (~$0.025) — [Extend vs Reducto](https://www.extend.ai/resources/extend-vs-reducto-document-ai-comparison)
- LlamaParse (LlamaIndex): $1.25 per 1,000 credits; Fast 1 credit/page (~$0.00125), Cost-effective 3, Agentic 10 (~$0.0125), Agentic Plus 45 (~$0.056); layout +3 credits/page; enriched forms +10 credits/page — [LlamaIndex pricing](https://www.llamaindex.ai/pricing); [LlamaParse FAQ](https://developers.llamaindex.ai/llamaparse/general/faq/)
- LlamaIndex funding: $19M Series A (Norwest, Greylock) March 2025, ~$27.5M total disclosed (older info) — [PR Newswire](https://www.prnewswire.com/news-releases/llamaindex-secures-19-million-series-a-to-power-enterprise-grade-knowledge-agents-302390936.html)
- Unstructured: 15K free pages/month, then $0.03/page PAYG (capped $3K/mo) per third-party comparisons — [markaicode: Unstructured vs LlamaParse](https://markaicode.com/vs/unstructured-vs-llamaparse/); [anyformat](https://anyformat.ai/blog/llamaparse-vs-unstructured-vs-reducto). Funding ~$65M through Series B (2024) per [TechCrunch 2023](https://techcrunch.com/2023/07/19/unstructured-which-offers-tools-to-prep-enterprise-data-for-llms-raises-25m/) and [Dealroom](https://app.dealroom.co/companies/unstructured_io); a reported 2025 $40M Series C at $200M valuation comes from a low-reliability aggregator ([salestools.io](https://salestools.io/en/report/unstructured-raises-40m-series-c)) — unverified.
- Google Document AI Custom Extractor: ~$30 per 1,000 pages (1–1M pages/month), ~$20/1K above — per search summary of [Google Cloud Document AI](https://cloud.google.com/document-ai) and third-party pricing pages ([aiproductivity.ai](https://aiproductivity.ai/pricing/google-document-ai/))
- Azure Document Intelligence prebuilt models (incl. Invoice): ~$10 per 1,000 pages; Read OCR drops to ~$0.60/1K above 1M pages; commitment tiers 5–25% discount — [Azure pricing page](https://azure.microsoft.com/en-us/pricing/details/document-intelligence/); [docuocr.com](https://docuocr.com/blog/azure-document-intelligence-pricing)
- Rossum: proprietary "transactional LLM" Aurora trained on millions of transactional documents; designed for traceable/auditable extractions; aimed at enterprise AP; pricing reportedly from ~$1,500/month (~$30K/yr), custom by volume (third-party) — [Rossum Aurora](https://rossum.ai/aurora-advanced-ai/); [grooper.com comparison](https://grooper.com/blog_posts/rossum-vs-nanonets-vs-docsumo/); [Capterra](https://www.capterra.com/p/193772/Rossum/)
- Nanonets: $200 free credits, PAYG per "block" ~$0.02 (simple) to ~$0.30 (complex AI); a typical invoice workflow runs 4–6 blocks (<$2/invoice); up to 40% volume discounts — [Nanonets pricing](https://nanonets.com/pricing); [toolradar](https://toolradar.com/tools/nanonets/pricing). Funding: $29M Series B led by Accel India (March 2024, older), $42M total — [Nanonets blog](https://nanonets.com/blog/nanonets-raises-29-million-in-series-b/); [TechCrunch](https://techcrunch.com/2024/03/12/nanonets-funding-accel-india/)
- Palantir also offers "AIP Document Intelligence" (community thread about availability on free dev tier) — [Palantir community](https://community.palantir.com/t/aip-document-intelligence-for-free-developer-tier/6223)

### Inferences
- For a supervision framework, document extraction is a commodity input: wrap one LLM-native API behind an internal interface (to swap vendors) and add domain schemas (invoice, weigh ticket, delivery note, certificate of analysis/insurance). Per-page cost ($0.01–$0.04) is negligible relative to the value of a finding.
- The value is not in parsing but in (a) domain schemas + validation rules per document type, (b) linking extracted fields to entities/obligations/events (e.g., weigh ticket -> truck -> GPS stop at the scale -> contract rate), and (c) provenance (page/bbox citations) carried into findings. Reducto/Extend/LlamaParse return citations/bounding boxes, which supports this.
- Hebrew-language documents (relevant for an Israeli market) are not addressed in any pricing/capability source found; must be tested.

### Gaps
- No vendor offers a prebuilt "weigh ticket" or "certificate" model found in this research; those require custom schemas (not verified per vendor).
- Accuracy on Hebrew/RTL, handwriting and phone photos of tickets not benchmarked in sources found.
- Several pricing figures come from competitor comparison pages (Extend about Reducto, Reducto about others) — potential bias.

---

## 4. Geospatial / telematics building blocks: open-source stop detection and multi-provider telematics APIs

### Takeaway
Stop/stay-point detection is a well-solved, open-source problem (MovingPandas BSD-3, scikit-mobility, trackintel MIT) — build a thin wrapper, don't buy. Cross-provider telematics normalization exists as a product: Terminal ("Plaid for telematics", 325+ providers, $26M raised) sells a unified API mainly to insurers and fleet software companies. Individual fleet providers (Samsara, Geotab, Motive) all have developer APIs available to their customers; the missing piece is the business semantics on top ("visit to customer site X fulfilled service obligation Y").

### Cited Findings
- MovingPandas: BSD-3-Clause, ~1.4k GitHub stars, built on GeoPandas; includes `TrajectoryStopDetector`, trajectory splitting, generalization, Kalman-filter cleaning/smoothing, aggregation; used in 28+ peer-reviewed publications — [GitHub movingpandas](https://github.com/movingpandas/movingpandas)
- scikit-mobility: `detection.stops` finds stay points where an object stayed at least N minutes within a radius (spatial_radius_km × stop_radius_factor); also privacy-risk assessment and synthetic mobility generation — [GitHub scikit-mobility](https://github.com/scikit-mobility/scikit-mobility); [arXiv paper](https://arxiv.org/pdf/1907.07062)
- trackintel (ETH Zurich mie-lab): MIT license; hierarchical model positionfix -> staypoint -> tripleg -> trip -> tour, plus "locations" (places visited repeatedly); `generate_staypoints()` uses an extended sliding-window algorithm with distance/time thresholds; latest version reported 1.1.12 — [GitHub trackintel](https://github.com/mie-lab/trackintel); [LICENSE](https://github.com/mie-lab/trackintel/blob/master/LICENSE); [arXiv](https://arxiv.org/pdf/2206.03593)
- Terminal (Toronto, YC S23): $20M Series A led by Battery Ventures (Intact Private Capital, Penske new strategic investors), $26M total since 2023 founding; single API to 325+ telematics service providers; data "normalized against common models"; delivers GPS, safety events, fault codes, dashcam media; ~half of revenue from commercial auto insurers, rest mostly software companies serving carriers — [PR Newswire](https://www.prnewswire.com/news-releases/terminal-raises-20-million-to-scale-market-leading-telematics-integration-technology-for-fortune-500-companies-across-insurance-fleet-management-and-logistics-302837250.html); [FreightWaves](https://www.freightwaves.com/news/terminal-fleet-telematics-data-funding); [Terminal](https://www.withterminal.com/)
- Samsara API: 150 req/s per token, 200 req/s per org, endpoint-level tiers; 429 on excess — [Samsara developer docs: rate limits](https://developers.samsara.com/docs/rate-limits)
- Geotab MyGeotab SDK: rate limits per method/entity/user/database (e.g., Device Get 650/min); open API/SDK — [Geotab developer docs](https://developers.geotab.com/myGeotab/guides/rateLimits/index.html)
- Indicative hardware subscription pricing (third-party): Samsara ~$27–$60/vehicle/mo (3-yr contracts typical), Geotab ~$10–$35 via resellers, Motive ~$25–$35 — [oxmaint comparison](https://oxmaint.com/industries/fleet-management/samsara-geotab-motive-telematics-comparison-fleet-2026)

### Inferences
- For SMB service companies with 1–3 telematics vendors, direct integration with each vendor's API plus open-source stop detection is cheaper than Terminal; Terminal becomes worth it when serving many customers each on different providers (the SaaS-vendor scenario — which is the position of a supervision-framework vendor).
- Terminal covers North American trucking providers; coverage of Israeli/local GPS providers (e.g., Pointer, Ituran, local fleet trackers) was not found — likely a gap requiring in-house connectors.
- "Visit verification" (stop matched to a customer site/geofence, duration vs. contracted service time) is where the domain logic lives; libraries give stops, not obligations.

### Gaps
- Terminal pricing not public in sources found.
- No commercial "visit detection as a service" API was evaluated (e.g., Radar, HERE) — not researched.
- Coverage of non-US telematics providers by Terminal not verified.

---

## 5. Entity resolution tools (Senzing, Splink, Zingg) and LLM-based matching

### Takeaway
Entity resolution is mature and affordable: Splink (MIT, UK MoJ) and Zingg (AGPL, Spark-native) are strong open-source options; Senzing is a commercial SDK with a free 100K-record tier and per-record pricing. LLMs are now used as a second-stage matcher/adjudicator for hard pairs; research shows rule/probabilistic and LLM approaches fail in complementary ways, supporting a hybrid (probabilistic blocking + LLM on borderline pairs + human review). Buy/wrap.

### Cited Findings
- Splink: MIT license, ~2.4k GitHub stars, Fellegi–Sunter probabilistic linkage with EM training, blocking, term-frequency adjustments; DuckDB and Spark backends; a demo of Splink 5 deduplicated 1B input rows (10B comparisons) in 8.5 minutes on a 192-vCPU EC2 instance for <$1 on spot (per search summary) — [GitHub splink](https://github.com/moj-analytical-services/splink); [Splink docs](https://moj-analytical-services.github.io/splink/index.html); [IJPDS: Splink recent developments](https://ijpds.org/index.php/ijpds/article/view/3598)
- Zingg: AGPL v3.0 open-source MDM/entity resolution; runs natively on Databricks, Snowflake, Fabric, Glue, GCP; Enterprise edition with extra features — [GitHub zingg](https://github.com/zinggAI/zingg); [zingg.ai](https://www.zingg.ai/)
- Senzing: free evaluation up to 100K records; subscription priced on Data Source Records (DSRs), e.g., 10M DSRs ≈ $58,560/yr; unlimited-record licensing available to many customers — [Senzing pricing](https://senzing.com/pricing/); [Senzing desktop trial](https://senzing.com/desktop/)
- Open-source tools do not by themselves provide hosted APIs, access control, monitoring, review queues or governance; Splink requires engineering ownership; Zingg requires labeling/tuning discipline (vendor-authored comparison, Tilores) — [Tilores: Top 10 ER tools 2026](https://tilores.io/content/top-10-entity-resolution-tools-for-enterprises-in-2026-ranked-by-use-case/)
- Enterprise ER vendors listed for 2026: Tilores, Senzing, AWS Entity Resolution, Informatica, Reltio, Data Ladder, Quantexa, Tamr, Zingg, Splink — [Tilores](https://tilores.io/content/top-10-entity-resolution-tools-for-enterprises-in-2026-ranked-by-use-case/)
- LLM matching research: OpenSanctions Pairs benchmark (2026) finds rule-based matching over-matches (false positives), while LLMs fail mainly on cross-script transliteration and minor identifier/date inconsistencies — complementary failure modes — [arXiv 2603.11051](https://arxiv.org/html/2603.11051v1). Earlier work compares match/compare/select strategies for LLM entity matching — [arXiv 2405.16884](https://arxiv.org/pdf/2405.16884)

### Inferences
- For a supervision framework, ER is needed to link "the same" customer site, vehicle, subcontractor or supplier across ERP, invoices, telematics and messages. Splink (DuckDB, MIT) fits an SMB-scale data lake well; LLM adjudication of borderline pairs, with reviewer confirmation feeding back, fits the concept's human-review loop.
- Cross-script transliteration weakness of LLMs is directly relevant to Hebrew/English name matching — needs explicit normalization/transliteration features.

### Gaps
- No evaluation found of ER tools on Hebrew data.
- AWS Entity Resolution pricing not collected.

---

## 6. LLM evaluation / LLM-as-judge and audit-trail tooling for defensible findings

### Takeaway
LLM-eval/observability is a crowded, well-funded tooling category (Braintrust, Langfuse, Patronus, Arize, Confident AI/DeepEval, etc.) that provides tracing, scorers, datasets, and annotation queues — useful for measuring the evidence-judge's accuracy and keeping a trace of every LLM call. But these tools audit the AI system, not the business finding; none provides a "finding" object with rule citation, evidence links and reviewer disposition. Research literature (2026) stresses that LLM judges are unstable across model changes and need calibration and human escalation — supporting the concept's design of deterministic checks + LLM for evidence only + human queue.

### Cited Findings
- Braintrust: $80M Series B led by ICONIQ (a16z, Greylock, Elad Gil) announced 17 Feb 2026 (per third-party summary); CI/CD-integrated scorers with deployment blocking — [Voiceflow: What is Braintrust](https://www.voiceflow.com/blog/what-is-braintrust); [Confident AI comparison](https://www.confident-ai.com/knowledge-base/compare/top-braintrust-alternatives-and-competitors-compared)
- Langfuse: most widely deployed open-source LLM observability, ClickHouse-backed, self-hostable (data residency) — [Braintrust: Langfuse alternatives 2026](https://www.braintrust.dev/articles/langfuse-alternatives-2026) (competitor-authored)
- Patronus AI: reported $50M Series B led by Greenfield Partners (Lightspeed, Notable, Datadog, Samsung) — [respan.ai comparison](https://www.respan.ai/market-map/compare/braintrust-vs-patronus-ai) (low-reliability source; unverified)
- Laminar: open-source observability for AI agents with trace replay and anomaly detection — per search summary (source: [aiagentstore weekly news](https://aiagentstore.ai/ai-agent-news/this-week))
- Research: "When the Judge Changes, So Does the Measurement" (2026) audits LLM-as-judge reliability across judge swaps — [arXiv 2607.08535](https://arxiv.org/pdf/2607.08535); "The Stability Trap" on instability of LLM-based instruction-adherence auditing — [arXiv 2601.11783](https://arxiv.org/pdf/2601.11783); DA-RAC calibration for trustworthy AI auditing, using neighbourhood difficulty as a signal for human review — [arXiv 2608.14950](https://arxiv.org/pdf/2608.14950)
- Compliance-grade LLM serving for fraud/AML uses LLM-as-judge as pre-production quality gates and shadow-mode monitoring, without replacing human investigators — [arXiv 2605.11232](https://arxiv.org/pdf/2605.11232)
- Rossum markets "auditable outputs, so every extraction decision can be traced, reviewed, and validated" — [Rossum Aurora](https://rossum.ai/blog/rossum-aurora/); Ramp's Policy Agent cites exact policy text used in each decision — [Ramp support](https://support.ramp.com/policy-agent-overview)

### Inferences
- Wrap an eval/trace tool (Langfuse self-hosted is the cheapest, open-source path) for LLM-call lineage and judge accuracy tracking; build the business-level finding/provenance model yourself (rule version, rule source clause, evidence ids with page/bbox or timestamp, model + prompt version, confidence, reviewer decision, feedback into rule/prompt).
- Judge instability research argues for pinning model versions per rule version and re-running a golden set on each model change — a feature a supervision product should expose to customers as part of defensibility.

### Gaps
- Funding figures for Braintrust and Patronus come from secondary/competitor sites; not confirmed from primary press releases.
- No product found that provides a ready-made "finding with provenance + reviewer queue" object for business audits outside vertical products (AppZen, Ramp, Loop).

---

## 7. Vertical-agnostic "AI auditor" / "AI ops monitoring" startups (NL rules over customer data)

### Takeaway
I found no clearly established horizontal startup that lets arbitrary companies define supervision rules in natural language over their operational data and produces evidence-backed findings. The market splits into (a) agent-observability/security tools that monitor AI agents (AIR, Zenity, Dataiku Agent Management) — a different problem; (b) finance/audit tools (MindBridge, AppZen, Ramp, Big-4 platforms); (c) domain platforms (Loop for freight, Icertis for contracts, Bretton/Norm for financial compliance); and (d) horizontal NL automation (Kognitos) or ontology substrates (Palantir, Fabric IQ). This is a genuine white space for SMB service/operations supervision, though large platforms (Microsoft Fabric IQ rules + Operations Agent; Palantir AIP) are moving toward it from above.

### Cited Findings
- AIR: $50M seed (Sept 2026), Unit 8200 founders; discovers AI agents in a company and vets their skills/add-ons — agent security, not business supervision — [TechCrunch, Sep 2026](https://techcrunch.com/2026/09/01/air-raises-50m-to-help-companies-vet-the-skills-and-add-ons-ai-agents-use/); [PYMNTS](https://www.pymnts.com/news/investment-tracker/2026/ai-agent-security-startup-air-raises-50-million-to-guard-enterprise-supply-chains/)
- Dataiku Agent Management (announced 24 Sept 2026): inventories AI agents, tracks KPIs and technical performance, risk-tiers agents — per search summary of [aiagentstore weekly news](https://aiagentstore.ai/ai-agent-news/this-week)
- Microsoft Fabric IQ Ontology rules + Operations Agent: agents evaluate conditions defined on ontology entities and take actions — [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/iq/ontology/concepts-agent-integration)
- AI agents in audit "build work papers continuously… supporting evidence linked automatically, anomalies flagged before they become audit findings" (industry commentary) — [Trullion: 5 audit trends 2026](https://trullion.com/blog/recent-trends-in-auditing/); [DSG.AI](https://www.dsg.ai/blog/continuous-auditing-tools)
- Revenue-leakage claims (e.g., "4.2% hidden leakage found in first quarter") appear only on low-quality marketing pages — [energent.ai](https://www.energent.ai/energent/compare/en/revenue-leakage-definition-with-ai) (treat as unreliable)
- See also section 2 for Kognitos, Ramp Policy Agent, AppZen, Loop, Icertis, Norm, Bretton.

### Inferences
- Closeness ranking to the full concept (subjective, based on findings above):
  1. Palantir Foundry/AIP — highest architectural overlap; enterprise-only price.
  2. Microsoft Fabric IQ Ontology + agents — similar substrate, lower entry cost, preview maturity, no domain content.
  3. Norm Ai — closest on "regulation -> structured checks"; financial/legal vertical, enterprise.
  4. Loop / AppZen / Ramp Policy Agent / Icertis — full loop (extract -> check vs contract/policy -> exception queue) in one domain each.
  5. Kognitos — NL rules executed deterministically; automation, not supervision.
  6. Bretton AI — agents for AML investigations; vertical.
  7. Hebbia — document Q&A grid; UX pattern only.
- Buyers across these: large enterprises and regulated financial institutions; SMB service companies are essentially unserved except via finance tools (Ramp) that cover only spend.

### Gaps
- Searches for "AI agents monitor business operations with natural-language rules" returned mostly AI-agent observability; possible smaller/stealth startups (e.g., YC batches) were not identified. A targeted YC directory scan was not completed.
- No Israeli players identified in this scope.

---

## 8. Commodity (buy/wrap) vs. no good product (build)

### Takeaway
Buy/wrap: document parsing/extraction, OCR, telematics connectors (vendor APIs or Terminal), stop detection libraries, entity resolution, LLM tracing/eval, data lake/warehouse. Build: the opinionated canonical model (entity/obligation/event/evidence/finding), the contract/SOP/regulation -> versioned executable rule compiler with human approval, the evidence-to-obligation linking logic (e.g., stop at site ↔ service visit ↔ invoice line ↔ contract rate), the finding object with end-to-end provenance and reviewer workflow, and the domain rule/schema libraries per vertical.

### Cited Findings
- Extraction is priced at ~$0.001–$0.06/page across LLM-native vendors and ~$10–$30/1K pages at hyperscalers — [LlamaIndex pricing](https://www.llamaindex.ai/pricing); [Extend](https://www.extend.ai/resources/extend-vs-reducto-document-ai-comparison); [Reducto pricing](https://reducto.ai/pricing); [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/document-intelligence/)
- Stop detection is available in BSD/MIT open-source libraries — [MovingPandas](https://github.com/movingpandas/movingpandas); [trackintel](https://github.com/mie-lab/trackintel)
- Telematics normalization across 325+ providers is productized — [Terminal](https://www.withterminal.com/)
- ER is available open-source (Splink MIT, Zingg AGPL) or commercially with a free tier (Senzing) — [Splink](https://github.com/moj-analytical-services/splink); [Zingg](https://github.com/zinggAI/zingg); [Senzing pricing](https://senzing.com/pricing/)
- Rule compilation into an intermediate machine-checkable language exists only inside vertical products (Norm Ai's proprietary decision-tree language; Kognitos "English as code") — [SiliconANGLE](https://siliconangle.com/2025/03/11/ai-agent-powered-compliance-automation-startup-norm-ai-raises-48m/); [Kognitos](https://www.kognitos.com/)
- Ontology substrates exist but are generic and either enterprise-priced (Palantir) or in preview (Fabric IQ) — [bdemerson](https://www.bdemerson.com/article/palantir-cost); [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview)

### Inferences
- A defensible product wedge is the "obligation compiler + evidence judge + finding ledger" layer, sold with vertical rule packs, running on commodity blocks. The main competitive threat is from above (Palantir AIP/Fabric IQ adding templates) and from sideways (domain players like Loop/AppZen expanding scope), not from an existing horizontal SMB competitor.
- Commodity-block choice should prioritize swapability (vendor-neutral interfaces) since pricing in IDP is changing fast (e.g., Reducto changed its billing model in Sept 2026).

### Gaps
- No total-cost model was built for an SMB deployment (e.g., per-customer monthly cost of extraction + LLM judging + telematics access).
- Local-market (Israel/Hebrew) availability of each block was not verified.
