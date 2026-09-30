# Converting Business Processes to AI: Process Mining + Agents, Agentic Process Automation, AI-Native BPO, "Services as Software" (landscape as of Sept 2026)

Method note: research done 2026-09-28 via web search. Many primary pages (techcrunch.com, foundationcapital.com, crescendo.ai, kyp.ai, caritas.ventures, substack) were blocked by the network egress proxy, so a lot of the findings below come from search-result snippets of those pages, not full-page reads. Treat numbers as "reported" and check them before relying on them in anything final. Vendor-authored comparisons (e.g., KYP.ai comparing itself to Skan/Mimica) are marked.

Legend for each company: **Exec** = does the work (execution); **Sup** = checks, monitors or governs the work (supervision); **Model** = license / per-outcome / managed service / forward-deployed engineers (FDE) / roll-up (owns the service firm).

## Q1. Incumbents moving to agents (Celonis, UiPath, Automation Anywhere, SAP Signavio, ServiceNow, Microsoft Power Automate, Pega, Appian): what do their agentic offerings actually do in 2025-2026?

### Takeaway
Every incumbent now sells an "agent" layer, but they come at it from two directions. The process-intelligence vendors (Celonis, SAP Signavio) mostly sell *context and analysis*: they feed process data to agents that run on other platforms (Copilot Studio, Bedrock, Agentforce), so they lean toward supervision and optimisation. The RPA and workflow vendors (UiPath, Automation Anywhere, Pega, Appian, ServiceNow, Power Automate) sell *orchestration and execution*: they build agents, run them alongside bots and humans, and add governance consoles (ServiceNow AI Control Tower, for example). All of them sell enterprise software licences or consumption. None prices by outcome.

### Cited Findings
**Celonis** (Munich/NY; process mining leader; enterprise; licence) — **Sup/context**
- AgentC is "a suite of AI agent tools, integrations, and partnerships" that lets customers build agents in *third-party* agent platforms. Those agents are powered by Celonis Process Intelligence — [Celonis press](https://www.celonis.com/news/press/celonis-agentc-making-ai-agents-work-for-the-enterprise-with-process-intelligence)
- It has an extended process-intelligence API that shares context, metrics and recommended actions with Microsoft Copilot Studio, Amazon Bedrock and Salesforce Agentforce. It also offers what Celonis calls the industry's first MCP server for process intelligence (Nov 2025) — [SiliconANGLE, 2025-11-04](https://siliconangle.com/2025/11/04/celonis-feeds-ai-agents-process-intelligence-data-enhance-operational-context/)
- Microsoft Agent 365 + Celonis integration went into private preview on 1 May 2026. An expanded AWS collaboration was announced in May 2026 — [Celonis blog](https://www.celonis.com/blog/scaling-the-agentic-enterprise-with-microsoft-agent-365-and-celonis); [AWS press 2026/5](https://press.aboutamazon.com/aws/2026/5/celonis-collaborates-with-aws-to-optimize-business-operations-with-industrialized-enterprise-ai)
- Launched "Solution Suites" and strengthened AgentC under a "No AI without PI (process intelligence)" strategy — [diginomica](https://diginomica.com/celonis-launches-solution-suites-and-enhances-agentc-advancing-its-no-ai-without-pi-strategy-faster)
- Celonis 2026 Process Optimization Report (vendor survey): 85% of organisations want to be an "agentic enterprise" within 3 years, and 76% say their operations can't support it — [Celonis](https://www.celonis.com/insights/reports/process-optimization); [Celonis press](https://www.celonis.com/news/press/the-enterprise-ai-reality-check-high-ambitions-meet-operational-barriers)

**UiPath** (NYSE: PATH; NY; enterprise; subscription licence) — **Exec + orchestration**
- Q4 FY2026 (reported ~Mar 2026): ARR $1.853B (+11% YoY), revenue $481M (+14%), first full year of GAAP profitability — [Yahoo Finance transcript](https://finance.yahoo.com/quote/PATH/earnings/PATH-Q4-2026-earnings_call-412609.html)
- "AI product ARR" (Agentic + IDP + Maestro) was nearly $200M in that quarter, about 11% of total ARR — [same](https://finance.yahoo.com/quote/PATH/earnings/PATH-Q4-2026-earnings_call-412609.html)
- Early adoption (FY26 Q1 remarks, older, ~May 2025): Agent Builder had "thousands" of agents and 250k+ agent runs. Maestro (agentic orchestration of agents + robots + humans) had powered 11,000+ process instances in preview — [UiPath Q1 FY26 prepared remarks](https://d1io3yog0oux5.cloudfront.net/_33a6dc8473fa74d1a5a6ea958a71d67e/uipath/db/1195/14865/webcast_transcript/UiPath+-+1Q+2026+-+Earnings+Transcript.pdf)
- Q1 FY2027 results are also out — [UiPath IR](https://ir.uipath.com/news/detail/452/uipath-reports-first-quarter-fiscal-2027-financial-results). I did not extract the figures.

**Automation Anywhere** (San Jose; private; enterprise) — **Exec**
- Brands itself "Agentic Process Automation (APA)". The 2026 platform adds a "Context Intelligence Graph" that supplies enterprise context to agents, automations and human decisions, plus an "Autonomous Service Desk" (multi-agent IT support with pre-built agents) — [AA press](https://www.automationanywhere.com/company/press-room/automation-anywhere-unveils-2026-platform-enhancements-run-ai-driven-processes)
- Sells two things: an APA system for IT/developers and packaged agentic solutions for finance, customer service, IT and HR business leaders — [same](https://www.automationanywhere.com/company/press-room/automation-anywhere-unveils-2026-platform-enhancements-run-ai-driven-processes); [Imagine 2026 blog](https://www.automationanywhere.com/company/blog/imagine-2026-dallas-ai-product-announcements)

**SAP Signavio** (SAP; enterprise) — **Sup/analysis, not execution**
- Joule inside SAP Signavio became generally available in Feb 2026 — [SAP News 2026-02](https://news.sap.com/2026/02/process-conversation-joule-sap-signavio-solutions-generally-available/)
- Five Joule Agents are in beta: Workspace Administration, Process Content Recommender, Dashboard Analyzer (turns mining data into insights), SIGNAL query interpretation, and business-case translation. They support *process analysis and transformation*, not running the processes — [Process Excellence Network](https://www.processexcellencenetwork.com/process-mining/news/sap-signavio-announces-beta-launch-of-5-new-joule-agents-to-boost-process-transformation); [SAPinsider](https://sapinsider.org/blogs/new-sap-signavio-joule-agents-target-faster-process-transformation/)
- Execution agents sit in SAP's wider Joule Agents / Joule Studio (new enterprise-scale version announced May 2026). Sapphire 2026 was themed "autonomous enterprise + agent guardrails" — [SAP News 2026-05](https://news.sap.com/2026/05/new-joule-studio-enterprise-scale-agentic-development/); [SAPinsider Sapphire 2026](https://sapinsider.org/blogs/sap-sapphire-2026-autonomous-enterprise-ai-agents/)

**ServiceNow** (enterprise; subscription) — **Exec + Sup (governance)**
- AI Agent Studio (natural-language agent building), pre-built agents for ITSM/CSM/HRSD/SecOps, an AI Agent Orchestrator for cross-department workflows, and **AI Control Tower** for governance and monitoring of all agent activity. Source is a partner/integrator blog, not ServiceNow — [Kellton](https://www.kellton.com/kellton-tech-blog/servicenow-ai-agents-and-agentic-workflow-automation-complete-guide)

**Microsoft Power Automate / Copilot Studio** — **Exec**
- 2026 release wave 1 includes AI agent authoring, self-healing desktop flows (RPA that adapts when UIs change), Copilot Studio-powered actions in cloud flows, desktop flows callable from Copilot Studio agents, **GA of object-centric process mining**, and consolidated governance reporting — [Microsoft Learn](https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-automate/); [Power Platform June 2026 update](https://www.microsoft.com/en-us/power-platform/blog/2026/06/11/whats-new-in-power-platform-june-2026-feature-update/)

**Pega** — **Exec/orchestration**
- "Pega Agentic Process Fabric" registers AI agents, workflows and data across Pega apps and third-party systems to automate end-to-end customer journeys — [Pega press](https://www.pega.com/about/news/press-releases/pega-agentic-process-fabric-reliably-orchestrates-end-end-ai-automation); [TechTarget](https://www.techtarget.com/searchcustomerexperience/news/366625157/Pegasystems-expands-agentic-AI-for-business-automation)

**Appian** — **Exec**
- Agent Studio is GA: agents that "reason, handle unexpected conditions, and act on enterprise data" inside Appian process models (2025 announcement) — [Appian press 2025](https://appian.com/about/explore/press-releases/2025/appian-launches-new-ai-capabilities-to-automate-complex-work)

### Inferences
- The incumbent stack is layering up: mining/intelligence (Celonis, Signavio, MS process mining) → orchestration (UiPath Maestro, Pega Fabric, ServiceNow Orchestrator) → execution agents → governance console (ServiceNow AI Control Tower, MS consolidated governance). Governance is sold as an add-on to each vendor's *own* agents, not as a neutral cross-vendor check of whether the business outcome was correct.
- UiPath's AI ARR at about 11% of total shows that agentic revenue at incumbents is real but still a minority. Most revenue is still classic RPA.
- Celonis is positioning itself as a neutral "context provider" to every agent platform. That makes it the closest incumbent to a supervision play (conformance, KPIs), but it does not sell outcome checking.

### Gaps
- Could not verify Celonis 2025-26 revenue or valuation (last widely reported valuation was $13B in 2022; older and unverified here).
- No detail found on pricing of agent SKUs (per agent run, consumption credits) for UiPath, AA, ServiceNow or Pega.
- The ServiceNow details come from an integrator blog, not ServiceNow's own release or earnings.

## Q2. Task/process mining and discovery startups (Skan.ai, Mimica, Soroco, KYP.ai, others): do they now generate AI automations automatically?

### Takeaway
Yes. In 2026 the desktop-observation task-mining startups repositioned themselves from "discovery" to "discovery → agent generation". KYP.ai says it generates ready-to-run agent code for the customer's existing agent platform. Skan.ai generates "Agent Operating Procedures" from observed work and deploys governed agents. Mimica claims production agents in about 24 hours. Most of these claims come from vendor self-descriptions.

### Cited Findings
- Skan, Soroco and Mimica "watch the desktop instead of the log", unlike log-based process mining such as Celonis — [Bardeen 2026 list](https://www.bardeen.ai/best/process-intelligence-software)
- **KYP.ai** (Germany; enterprise): "generates structured business context and ready-to-execute agent code for AI agents, deployable on the customer's existing agentic platform". It claims this compresses "months of analysis + RPA team design" into "days of automated code generation + review". Source is KYP's own comparison — [KYP.ai comparison (vendor)](https://kyp.ai/which-next-gen-process-intelligence-solution-is-right-for-you/); [KYP task mining tools compared (vendor)](https://kyp.ai/task-mining-tools-compared/)
- **Skan.ai** (US/India; enterprise, heavy in insurance and financial services): "deploys governed AI agents built from Agent Operating Procedures derived from observed human work rather than hand-written SOPs", including exceptions and edge cases. Source is KYP's comparison page — [KYP comparison](https://kyp.ai/which-next-gen-process-intelligence-solution-is-right-for-you/); see also [ERP Research Skan review](https://www.erpresearch.com/erp-add-ons/process-mining/skan-ai)
- **Mimica** (London; enterprise): positioned as process intelligence + task mining, and "can build and deploy production-ready agents in as little as 24 hours" — [Mimica site](https://www.mimica.ai/); [KYP comparison](https://kyp.ai/which-next-gen-process-intelligence-solution-is-right-for-you/)
- **Soroco** (Scout; Boston/Bangalore): still listed as a key task-mining player. The search results gave no detail on agent generation — [Bardeen](https://www.bardeen.ai/best/process-intelligence-software)
- Gartner maintains a "Task Mining Tools" review market (2026) — [Gartner Peer Insights](https://www.gartner.com/reviews/market/task-mining-tools)
- Mid-market insurance angle: process-intelligence vendor comparisons now target the mid-market, not just the Global 2000 — [Insightful](https://source.insightful.io/blog/blog-process-intelligence-insurance-mid-market)

### Inferences
- The discovery layer is turning into a way to *generate* agents. Discovery itself (recording work and turning it into SOPs) is becoming commoditised and bundled.
- Recording "how humans actually do the work, including exceptions" is also exactly the baseline a *supervision* product needs, i.e. a reference for what correct execution looks like. These vendors are well placed to pivot into ongoing conformance monitoring of agents, but I found no evidence that they sell it as a separate product.

### Gaps
- No verified 2025-26 funding for Skan.ai, Mimica, Soroco or KYP.ai (fetches blocked). From older memory, unverified: Skan raised a ~$25M Series B (2022) and Mimica a ~$26M Series B (2024). Do not cite these without checking.
- No independent (non-vendor) evidence on how well auto-generated agents perform in production.

## Q3. AI-native BPO and "services as software" startups: who does the work, who targets SMB vs enterprise?

### Takeaway
The best-funded AI-native services companies sell to **enterprises or to service firms themselves**. Basis sells to top accounting firms, Pace to large insurers, Crescendo to enterprise contact centres, Tennr to healthcare providers, and Ema to enterprise HR/IT/finance. Almost all are **execution** plays and increasingly priced **by outcome**: Crescendo charges per resolution with a guarantee, and Digits bills only when a client's books are 95% zero-touch. SMB-direct AI services mostly reach SMBs through accounting firms and roll-ups rather than selling to them directly.

### Cited Findings
Market size / structure
- A database of AI-native service firms maps **211 companies across 70 industries and 23 countries, with >$5B raised in total**. It defines an AI-native service company as one "built from the ground up to deliver a business outcome through software, agents, data and expert oversight" — [VC Cafe](https://www.vccafe.com/ai-native-services-the-new-startup-playbook/)
- Indian BPO providers and AI-native operators have repriced around outcomes (resolution, retention, revenue recovery) instead of headcount — [Mascallnet (low-authority blog)](https://mascallnet.ai/bpo-for-startups-in-2026-can-small-businesses-really-afford-to-outsource-customer-support/)
- Outcome-based pricing is described as the fastest-growing pricing model for agentic AI in 2025-26 — [Growth Unhinged 2026 monetisation report](https://www.growthunhinged.com/p/the-state-of-b2b-monetization-in-2026) (search snippet)

Company profiles
- **Basis** (NYC; AI agents for accounting firms; enterprise-ish, top CPA firms): $100M Series B led by Accel with GV, Khosla and Lloyd Blankfein, at a **$1.15B valuation** (Feb 2026). Used by about 30% of the top 25 accounting firms. Agents run tax, audit and client advisory workflows end to end. **Exec; software sold to firms** — [CPA Practice Advisor 2026-02-24](https://www.cpapracticeadvisor.com/2026/02/24/basis-raises-100-million-to-deploy-ai-agents-for-accounting-firms/178759/); [PYMNTS](https://www.pymnts.com/news/investment-tracker/2026/basis-raises-100-million-to-build-up-ai-in-accounting)
- **Pace** (NY; "AI operations partner" for insurers; enterprise): $46M Series B co-led by Thrive Capital and Sequoia, with Emergence and Pruven (~June 2026), following a $10M Series A led by Sequoia. It has completed 250k+ insurance workflows autonomously. Clients include Prudential, Palomar, Convex and WTW. **Exec; AI-native BPO / managed service** — [Beinsure](https://beinsure.com/news/pace-raises-46-mn-for-ai-insurance-operations/); [FinTech Global 2026-06-01](https://fintech.global/2026/06/01/pace-lands-46m-funding-round-to-automate-insurance-workflows/); [Yahoo/Fortune on Series A](https://finance.yahoo.com/news/exclusive-pace-raises-10-million-112542033.html)
- **Crescendo** (San Francisco; AI-native contact centre; enterprise/mid-market): $50M Series C led by General Catalyst at $500M post-money (Oct 2024, older). Expected to exceed $100M ARR by the end of 2025, and per a search snippet confirmed crossing $100M ARR in May 2026. It combines AI agents with its own human staff. Third-party estimate: about **$1.25 per resolution + ~$2,900/month**. Its "Total Outcome Guarantee" (Oct 2025) promises go-live in 30 days or free implementation, with payment only for positive outcomes across AI and human agents. **Exec; managed service, outcome-priced** — [Sacra](https://sacra.com/c/crescendo/); [Yahoo/GlobeNewswire ARR](https://finance.yahoo.com/news/crescendo-exceed-100m-arr-global-160000769.html); [GlobeNewswire guarantee](https://www.globenewswire.com/news-release/2025/10/23/3172240/0/en/Crescendo-Launches-the-Total-Outcome-Guarantee-We-ll-Outperform-Any-AI-for-CX-or-You-Don-t-Pay.html); [Macha pricing (third party)](https://www.getmacha.com/blog/crescendo-ai-complete-guide)
- **Tennr** (NYC; founded 2021; healthcare referrals, intake, prior auth; providers from mid-size to large): raised $101M (date not confirmed in snippet, likely 2025). Processes 10M documents/month for hundreds of healthcare organisations. Added a voice agent for outbound referral calls. Former Cleveland Clinic/Google executive William Morris joined as CMO in Feb 2026. **Exec** — [Fierce Healthcare $101M](https://www.fiercehealthcare.com/health-tech/tennr-clinches-101m-build-out-ai-automates-patient-referral-workflows); [Fierce Healthcare voice](https://www.fiercehealthcare.com/health-tech/tennr-takes-aim-phone-call-bottlenecks-it-automates-patient-referral-process)
- **Ema** (teams of AI agents across HR, IT and finance; enterprise): raised **$77M (Sept 2026)** and pitches itself as replacing work done by enterprise software *and* IT services — [TechCrunch 2026-09-23](https://techcrunch.com/2026/09/23/ema-raises-77m-as-ai-starts-eating-into-enterprise-software-and-services/) (headline only; page blocked)
- **Digits** (accounting platform): in April 2026 it moved to outcome-based pricing for accounting firms, billing only for clients whose books reach ≥95% zero-touch transaction processing — [Carly AI accounting category map](https://www.usecarly.com/blog/ai-accounting-software/); [Rework](https://resources.rework.com/tools/ai-tools/best-ai-tools-for-accounting-2026)
- Other accounting AI rounds 2025-26: **Quanta** $15M, **Bluebook** €2.4M — [Carly](https://www.usecarly.com/blog/ai-accounting-software/)
- YC is heavily backing "AI-native service companies" in 2026 — [Kanopy Labs](https://kanopylabs.com/blog/ai-native-service-companies-yc-bets-2026) (secondary blog)
- AccountingTech Startup 100 (2026) lists 100 AI accounting startups — [Debit AI](https://debitai.co/ats100/)

### Inferences
- **SMB vs enterprise.** The venture money is going to enterprise-sold AI services, or to AI tools sold to *service providers* (CPA firms) that serve SMBs. Direct-to-SMB AI-native services exist (Pilot and Puzzle in bookkeeping, many YC companies), but the SMB channel is increasingly captured by (a) accounting firms using Basis or Digits and (b) roll-ups (Q5) that buy the local firms SMBs already trust.
- Nearly every AI-native BPO is an *execution* company that keeps humans in-house as the quality layer. Crescendo's "Superhuman agents" and Pace's human operators are examples. Supervision is bundled into the service, not sold separately.
- Outcome pricing (per resolution, per zero-touch client) forces the vendor to measure outcome quality itself. That creates a natural need for independent verification from the buyer's side.

### Gaps
- Pilot (bookkeeping): found no 2026 information on agents or funding.
- No reliable global (non-US) list of AI-native BPOs, e.g. in Europe, Israel or India, beyond the "211 companies / 23 countries" database headline.
- Could not verify Crescendo's May 2026 $100M ARR confirmation beyond the search snippet.

## Q4. Consultancies and "AI implementation" boutiques building custom agent workflows: how do small shops succeed, what do they charge?

### Takeaway
The implementation layer is splitting in two. At the top, model labs and big finance are building AI-services firms: Anthropic's JV with Blackstone, H&F and Goldman (May 2026, $1.5B), and a parallel OpenAI venture. At the bottom there is a long tail of automation agencies charging roughly $3k-$50k per build plus $500-$15k/month retainers. The retainer covers *monitoring and maintenance*, which is effectively ongoing supervision done by hand.

### Cited Findings
- **Anthropic enterprise AI services firm** (announced 2026-05-04): founding partners Blackstone, Hellman & Friedman and Goldman Sachs. Valued at $1.5B, with $300M committed each by Anthropic, Blackstone and H&F. Backers include Apollo, General Atlantic, GIC, Leonard Green and Sequoia. It is a standalone firm with Anthropic engineers embedded, set up to fix the "scarcity of experts capable of implementing the technology inside real-world operations" — [Anthropic](https://www.anthropic.com/news/enterprise-ai-services-company); [CNBC](https://www.cnbc.com/2026/05/04/anthropic-goldman-blackstone-ai-venture.html); [Blackstone](https://www.blackstone.com/news/press/anthropic-partners-with-blackstone-hellman-friedman-and-goldman-sachs-to-launch-enterprise-ai-services-firm/); [Fortune: "takes shot at consulting industry"](https://fortune.com/2026/05/04/anthropic-claude-consulting-industry-joint-venture-blackstone-goldman-sachs/)
- OpenAI launched a parallel enterprise-AI-services joint venture the same week — [TechCrunch 2026-05-04](https://techcrunch.com/2026/05/04/anthropic-and-openai-are-both-launching-joint-ventures-for-enterprise-ai-services/) (headline/snippet)
- Agency pricing (2026, secondary/marketing blogs, so indicative only):
  - $5k-$50k per project, $2k-$15k/month retainer, or $100-$300/hour — [Lets-Viz](https://lets-viz.com/blogs/ai-automation-agency-pricing-2026-what-buyers-pay)
  - One-time builds $3k-$15k; retainers $2.5k-$8k/month covering error monitoring, fixes when upstream APIs change, and the next automation — [search snippet, multiple agency blogs](https://www.layer3labs.io/roi/ai-automation-agency-cost)
  - Retainers: SMB $500-$2k/month, mid-market $3k-$8k/month — [Taskip](https://taskip.net/ai-automation-agency-pricing/)
  - Boutique agencies $3.5k-$50k per project, best suited to production systems for the B2B mid-market — [Digital Agency Network](https://digitalagencynetwork.com/ai-agency-pricing/)
  - Offshore "embedded automation specialist" at about $15/hour ($2,400/month full time), compared with $13.5k-$15k/month fully loaded for a US automation engineer — [Axis AI (vendor)](https://axis-ai.agency/blog/ai-automation-cost-2026)
- Some agencies explicitly sell "service as software", i.e. selling the work, not the tool — [Automaton Agency](https://automatonagency.com/insights/service-as-software)

### Inferences
- Small shops and solo operators succeed by (1) picking a vertical and repeatable workflow templates, (2) selling a build plus a monitoring/maintenance retainer, and (3) moving toward outcome pricing. The retainer is essentially paid **supervision**: watching for breakage, drift and upstream changes. That is evidence of demand for productised oversight of agent workflows.
- The Anthropic and OpenAI JVs and PE-backed firms will squeeze the mid and upper market. Boutiques' defensible ground is SMB and lower mid-market plus niche verticals and languages, where large firms won't deploy FDEs.

### Gaps
- Agency pricing sources are low-authority marketing blogs. I found no survey-grade data.
- No data on Accenture, Deloitte or Indian IT (Infosys, TCS) agent practice revenue. That was out of scope for the call budget.

## Q5. VC theses ("services as software") and AI roll-ups of service businesses: who funds roll-ups in accounting, property management, home services, waste or facilities?

### Takeaway
"Services as software" (Foundation Capital's $4.6T framing) is now the default B2B thesis. It has two executions: sell AI that does the work, or **buy the service firm and automate it**. General Catalyst (about $1.5B dedicated), Thrive Holdings ($2B raised in Aug 2026 at a $12B valuation, OpenAI-linked) and Bessemer lead the roll-up side. Verticals so far are accounting, IT MSPs, property management, legal, contact centres and corporate travel (Long Lake's $6.3B Amex GBT take-private). Home services, waste and facilities are still dominated by classic PE (Apollo, Blackstone, Bain). The AI-native roll-ups are only starting to move into physical services (Thrive's new "physical assets" vertical).

### Cited Findings
Theses
- Foundation Capital: a **$4.6T** opportunity over five years as AI eats in-house salaries and outsourced services, compared with a ~$200B SaaS market. The logic is that roughly $6 is spent on services for every $1 on software — [Foundation Capital](https://foundationcapital.com/the-4-6t-service-as-software-opportunity-lessons-from-year-one/); [FC "System of Agents"](https://foundationcapital.com/system-of-agents/) (snippets)
- Sequoia, Foundation Capital, a16z, YC and Bessemer have all framed services-as-software as the dominant opportunity of the cycle — [FC 2026 outlook snippet](https://foundationcapital.com/ideas/where-ai-is-headed-in-2026)
- J.P. Morgan Private Bank's note on the private-market opportunity in AI-led disruption of services — [JPM](https://privatebank.jpmorgan.com/nam/en/insights/markets-and-investing/a-new-wave-of-ai-led-disruption)
- General Catalyst's own thesis page is "The Future of Services" — [GC](https://www.generalcatalyst.com/stories/the-future-of-services)

Roll-up players
- **General Catalyst** (~$40B AUM): **$1.5B** for buying accounting firms, call centres, property managers and IT service providers. It is run by MD Marc Bhargava ("Creation Strategies": incubations, transformations, venture buyouts). GC mapped 70 services categories down to the 10 with the most immediate AI impact — [Sourcery](https://www.sourcery.vc/p/breaking-inside-general-catalysts); [Capital & Clarity](https://capitalandclarity.substack.com/p/the-general-catalyst-behind-15-billion)
  - **Long Lake** (started in HOA/property management): raised about $670M and acquired 18 businesses. AI agents handle resident inquiries and draft board materials. Reported $100M EBITDA in under 2 years — [Sourcery](https://www.sourcery.vc/p/breaking-inside-general-catalysts). On 2026-05-04 it agreed to take **Amex Global Business Travel private for $6.3B** ($9.50/share, a 60% premium), backed by GC and Alpha Wave. Closing expected 2H 2026 — [BusinessWire](https://www.businesswire.com/news/home/20260504231235/en/Long-Lake-Agrees-to-Acquire-American-Express-Global-Business-Travel-the-Worlds-Largest-Corporate-Travel-Platform-for-$6.3-Billion-With-Support-From-General-Catalyst-and-Alpha-Wave); [PitchBook](https://pitchbook.com/news/articles/general-catalysts-6-3b-amex-deal-puts-its-ai-roll-up-strategy-on-display); [Skift](https://skift.com/2026/05/04/amex-gbt-acquired-general-catalyst-long-lake-6-3-billion/)
  - **Eudia** (legal): $105M, targets the billable-hour model — [Sourcery](https://www.sourcery.vc/p/breaking-inside-general-catalysts)
  - **Titan MSP** (IT services): acquired RFA and deploys agents for ticket triage and failure prediction — [Sourcery](https://www.sourcery.vc/p/breaking-inside-general-catalysts)
  - **Accrual** (accounting): $75M, GC's entry into CPA firms — [Capital Founders](https://www.capitalfounders.io/playbooks/ai-enabled-roll-ups/chapters/capital-and-players/)
  - **Crescendo** (contact centre) is also GC-backed (see Q3)
- **Thrive Holdings** (Thrive Capital; OpenAI-backed): raised **$2B at a $12B valuation** (Aug 2026) from SoftBank, D1 and Altimeter. It takes controlling stakes in services firms and rewires them with AI. Over 1,000 employees and 10,000+ clients. It is expanding into a new **"physical assets"** vertical — [TechCrunch 2026-08-12](https://techcrunch.com/2026/08/12/openai-backed-thrive-holdings-raises-2b-to-bring-ai-to-the-enterprise/); [PYMNTS](https://www.pymnts.com/news/artificial-intelligence/2026/thrive-holdings-raises-2-billion-to-buy-and-rewire-services-firms-with-ai/)
  - **Current** (formerly Crete Professionals Alliance, rebranded June 2026; accounting): $300M+ annual revenue across 30+ firms, or 50+ firms and 2,000+ professionals per the later report. Named Accounting Today's fastest-growing firm of 2025. Its "Tax AI", built with Thrive Holdings and OpenAI, processed 7,000 returns in one season and cut time by about a third. It plans $500M+ of acquisitions — [BusinessWire 2026-06-02](https://www.businesswire.com/news/home/20260602293257/en/Crete-Professionals-Alliance-Rebrands-as-Current-to-Equip-Independent-Accounting-Firms-to-Compete-at-Enterprise-Scale); [International Accounting Bulletin](https://www.internationalaccountingbulletin.com/news/cpa-over-500m-investment-us-accounting-firms/)
  - **Shield Technology Partners** (IT MSP): raised a second $100M from Thrive Holdings (Feb 2026). About 20 companies on the platform — [Morningstar/BusinessWire](https://www.morningstar.com/news/business-wire/20260202196878/shield-raises-100-million-from-thrive-holdings-to-accelerate-the-growth-of-its-it-services-platform); [Bloomberg](https://www.bloomberg.com/news/articles/2026-02-02/thrive-holdings-makes-a-100-million-bet-on-ai-for-it-help)
- Total capital deployed specifically to AI roll-ups across major players is reported at over **$3B** (GC, Thrive, Bessemer and others) — [Capital Founders](https://www.capitalfounders.io/playbooks/ai-enabled-roll-ups/chapters/capital-and-players/)
- Market maps: [Caritas Ventures AI roll-up & AI-native PE map 2026](https://caritas.ventures/ai-rollup-market-map/) (blocked; exists); [Newcomer "VC roll-up craze"](https://www.newcomer.co/p/inside-the-vc-roll-up-craze-that); [Alloy Partners on AI-first accounting firms](https://www.alloypartners.com/articles/the-ai-first-accounting-firm-from-smarter-bookkeeping-to-strategic-insight); [Jupid, who is buying accounting firms 2026](https://jupid.com/blog/who-is-buying-accounting-firms-2026)

Home services / waste / facilities
- Home-services roll-ups in 2026 are still classic PE: Apex Service Partners (Apollo, $10B), Wrench Group (Leonard Green), Sila (Goldman Sachs Alternatives, $1.7B), Service Logic (Bain + Mubadala), Redwood Services (Altas, $1.1B), Champions Group (Blackstone, $2.5B at 18.5x EBITDA). A trade source says explicitly that AI ventures are *not* directly rolling up HVAC — [HVAC Know It All](https://hvacknowitall.com/blog/ai-private-equity-and-the-independent-hvac-contractor-in-2026); [Homestead](https://homesteadsp.com/hvac-mergers-and-acquisitions/)

### Inferences
- The roll-up model makes the acquirer *both* executor and supervisor. It owns the licensed professionals who sign off: CPA sign-off at Current, lawyers at Eudia. That is how roll-ups get around the liability and trust barrier that pure-software AI services face.
- The target verticals are ones with fragmented ownership, recurring revenue and document-heavy back offices. Physical trades (HVAC, waste, facilities) are next but still PE-led, and AI there mostly means back office (dispatch, quoting, billing).

### Gaps
- Found **no named AI-native roll-up in waste management or facility services**. There are also no verified details on Bessemer's specific roll-up portfolio companies, or on 8VC/Elad Gil-type roll-ups (e.g. Elad Gil's reported roll-up holdcos). The search budget ran out.
- Details of the OpenAI JV (name, size) are unverified because TechCrunch was blocked.

## Q6. Where is supervision/oversight of processes (as opposed to execution) underserved?

### Takeaway
Supervision exists in two narrow forms. (1) **Technical agent observability and governance** (Arthur, Credo AI, Galileo, Confident AI, Kore.ai, ServiceNow AI Control Tower), which checks model traces, policies and PII, not business outcomes. (2) **In-house human QA inside each AI-native BPO**, bundled and not independent. The underserved space is **independent, business-level, cross-vendor verification** that AI- or outsourced-run processes produced correct outcomes: conformance to SOPs, financial or claims correctness, SLA and outcome-billing audits. It matters most for mid-market and SMB buyers without an internal automation CoE, and wherever outcome-based pricing makes the vendor grade its own homework.

### Cited Findings
- "Human-on-the-loop" (humans monitor outcomes, audit traces and intervene past risk thresholds, rather than approving every step) is emerging as the compliance oversight pattern — [FutureAGI glossary](https://futureagi.com/glossary/human-on-the-loop/)
- Agent governance vendors: Arthur (Agent Discovery & Governance), Credo AI (agent registry, dependency graph, trace-level evaluation), Kore.ai (runtime policy/guardrails/RBAC). Observability/QA: Confident AI, Galileo (evals, runtime blocking of unsafe outputs). All of these work at the model/agent level — [Arthur](https://www.arthur.ai/column/best-ai-governance-platforms-2026); [Kore.ai](https://www.kore.ai/blog/best-ai-agent-management-platforms); [Galileo](https://galileo.ai/blog/human-in-the-loop-agent-oversight); [Confident AI](https://www.confident-ai.com/knowledge-base/compare/best-ai-agent-observability-tools-2026)
- A 2026 market review counts **90+ vendors** in agent observability, evaluation and governance — [Deepak Gupta](https://guptadeepak.com/ai-agent-observability-evaluation-governance-the-2026-market-reality-check/)
- "Regulated enterprises are leading adoption of manager features like approvals and review controls, with the tooling layer for managing human-in-the-loop interactions at enterprise scale still underdeveloped" — [search snippet from the 2026 governance/observability sources above](https://www.kore.ai/blog/best-ai-agent-management-platforms)
- Incumbent governance is vendor-bound: ServiceNow AI Control Tower governs agent activity on ServiceNow ([Kellton](https://www.kellton.com/kellton-tech-blog/servicenow-ai-agents-and-agentic-workflow-automation-complete-guide)); Microsoft adds "consolidated governance reporting" for Power Platform ([MS Learn](https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-automate/)); SAP's Sapphire 2026 theme was "AI agent guardrails" ([SAPinsider](https://sapinsider.org/blogs/sap-sapphire-2026-autonomous-enterprise-ai-agents/))
- Celonis's own survey: 76% of enterprises say their operations can't support agentic AI — [Celonis](https://www.celonis.com/news/press/the-enterprise-ai-reality-check-high-ambitions-meet-operational-barriers)
- Contact-centre "AI automated QA" is an established sub-category, e.g. Crescendo's own list of 8 tools. It is QA for conversations in one function only — [Crescendo blog](https://www.crescendo.ai/blog/ai-automated-quality-assurance)
- Outcome-priced vendors (Crescendo per resolution, Digits' 95% zero-touch trigger) define and measure the outcome they bill on themselves — [GlobeNewswire](https://www.globenewswire.com/news-release/2025/10/23/3172240/0/en/Crescendo-Launches-the-Total-Outcome-Guarantee-We-ll-Outperform-Any-AI-for-CX-or-You-Don-t-Pay.html); [Carly](https://www.usecarly.com/blog/ai-accounting-software/)
- Automation agency retainers are largely paid for monitoring, error handling and upstream-change fixes, i.e. manual supervision — [Layer3Labs snippet](https://www.layer3labs.io/roi/ai-automation-agency-cost)

### Inferences (analyst judgement, not sourced facts)
Underserved supervision niches:
1. **Buyer-side verification of outcome-priced AI services.** Someone is needed to audit that a "resolution", a "zero-touch close" or a "completed claim" was actually correct, since the vendor both does the work and measures it.
2. **Cross-vendor process conformance.** Enterprises run agents from UiPath, Microsoft, ServiceNow and startups at the same time. Governance consoles are per vendor, and Celonis supplies context but does not grade agent outcomes. A neutral "process auditor" layer that compares actual agent behaviour with SOPs or observed human baselines (the task-mining data from Q2) looks thin.
3. **SMB and mid-market.** Governance tools (Arthur, Credo, ServiceNow) are enterprise-priced. SMBs get supervision only as bundled human QA from their provider or as an agency retainer. There is no productised, affordable "second pair of eyes" on AI-run bookkeeping, collections or customer service.
4. **Regulated sign-off functions** (accounting, insurance claims, healthcare prior auth, legal). Roll-ups solve this by owning the licensed humans. Standalone AI services and in-house deployments lack an independent, auditable sign-off layer.
5. **Non-English / non-US markets.** Nearly all named players are US-centric. Local-language supervision of AI processes (e.g. Hebrew or other local-regulation contexts) is likely even less served. This is an inference; I found no data.

### Gaps
- Found no startup explicitly positioned as an "independent auditor of AI-run business processes" at the business-outcome level, as opposed to model observability. This could be a real gap or a search limitation.
- No market-size data for process-supervision or AI-QA spending.
- No evidence on how outcome-pricing contracts define disputes or verification in practice.
