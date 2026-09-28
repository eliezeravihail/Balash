# AI-Based Proof-of-Service and Service Delivery Verification for Field Service Industries (as of Sept 2026)

Scope note: research done 2026-09-28 with web search. Several primary vendor sites (wastevision.ai, blog.haulerhero.com, wastedive.com, issa.com) were blocked by the research network proxy, so some facts rely on search-result snippets of those pages, not full-page reads. Snippet-derived facts are marked "(snippet)". Vendor claims are self-reported marketing unless stated otherwise.

## Q1. Waste collection: who does AI route/pickup verification and contamination detection, and who verifies hauler performance for the buyer?

### Takeaway
Waste is the most mature vertical for AI proof-of-service: at least five vendors (WasteVision AI, AMCS Vision AI, Routeware incl. ex-Rubicon fleet tech, Hauler Hero "Hero Vision", Rubicon Smart City) run computer vision on truck cameras to verify service, overflow and contamination, and two broker-style players (RoadRunner/Compology, RTS/Pello) put AI cameras/sensors in the container itself, which gives the waste generator (buyer) an independent record. Pure buyer-side "audit my haulers" software for municipalities and brokers is thin; most buyer verification comes bundled inside a managed brokerage service.

### Cited Findings

**WasteVision AI (Scottsdale, Arizona, US) - hauler/municipality side, truck cameras**
- Positioning: "turns the cameras already on your trucks into an operational data platform — verifying service, flagging contamination, capturing every overflow." (snippet) — [WasteVision AI](https://wastevision.ai/)
- Contamination detection at the hopper in real time, tied to the generator address, "without the driver lifting a finger"; requires a connected video-telematics hopper camera; models identify bags, styrofoam, construction debris, yard waste; claims >99.5% accuracy (snippet) — [WasteVision contamination page](https://wastevision.ai/contamination-detection.html); [Waste360](https://www.waste360.com/fleet-technology/artificial-intelligence-ai-is-a-game-changer-for-waste-contamination-detection-60333)
- Claims overflows occur in up to 12% of commercial bins and are billable when documented (snippet) — [Waste360 / WasteVision sponsored piece](https://www.waste360.com/fleet-technology/with-on-truck-ai-haulers-are-no-longer-blind); [Waste Dive sponsored](https://www.wastedive.com/spons/with-on-truck-ai-haulers-are-no-longer-blind/692940/)
- May 2026: integration with Lytx so Lytx video-safety customers get WasteVision Service Verification, Overflow Detection and Contamination Detection layered on existing cameras — [PR Newswire via Morningstar, 11 May 2026](https://www.morningstar.com/news/pr-newswire/20260511la56298/wastevision-ai-and-lytx-integrate-to-bring-operational-ai-to-waste-haulers-already-running-lytx-safety-technology)
- HQ Scottsdale AZ; funding undisclosed / conflicting across databases (one says no funding raised, another says one undisclosed round) — [Crunchbase](https://www.crunchbase.com/organization/wastevision-ai); [Tracxn](https://tracxn.com/d/companies/wastevisionai/__gHnG6UP_uGi0yRzrriVrW2Pm8kPd-3Ult9zpMk4_qj8); [PitchBook](https://pitchbook.com/profiles/company/181812-16)
- Target: private haulers and municipalities (contamination enforcement, MRF cost reduction) — [WasteVision contamination page](https://wastevision.ai/contamination-detection.html)

**Hauler Hero (New York, US) - SMB/mid hauler operating system with AI**
- Feb 2026: $16M Series A led by Frontier Growth (with Disruptive Founders Fund, Somersault Ventures, waste-industry and ServiceTitan execs); >$27M raised to date; platform automates invoicing, routing, dispatch, customer engagement — [TechCrunch, 10 Feb 2026](https://techcrunch.com/2026/02/10/hauler-hero-collects-16m-for-its-ai-waste-management-software/); [Waste Today](https://www.wastetodaymagazine.com/news/hauler-hero-raises-16m-series-a-funding-for-ai-powered-operating-system/)
- AI agents in development/testing at time of raise: Hero Vision (truck camera identifying service issues), Hero Chat (AI comms), Hero Routing — [Waste Today](https://www.wastetodaymagazine.com/news/hauler-hero-raises-16m-series-a-funding-for-ai-powered-operating-system/)
- Hero Vision = camera-based computer vision to verify service issues, review exceptions, surface revenue (billable exceptions); "triple verification": Hero Vision + GPS context + RFID workflows + driver tablet records; company blog argues edge devices are the future of waste AI (snippet) — [Hauler Hero Vision](https://www.haulerhero.com/vision); [Hauler Hero blog](https://blog.haulerhero.com/proof-of-service-in-waste-hauling-how-triple-verification-reduces-disputes-and-captures-billable-exceptions)

**AMCS (Ireland-HQ'd enterprise waste ERP) - AMCS Vision AI**
- Vehicle-mounted cameras + ML detecting contamination, overfilled containers and material composition issues — [AMCS Vision AI](https://www.amcsgroup.com/solutions/amcs-vision-ai/)

**Routeware (US) + former Rubicon fleet technology**
- Routeware acquired the recently spun-off Rubicon fleet-technology business (Rubicon Smart City / Rubicon Pro), moving toward end-to-end fleet software for the circular economy (Waste Dive article, ~2024 — older than 2026; full text blocked) — [Waste Dive](https://www.wastedive.com/news/routeware-acquires-recently-spun-off-rubicon-fleet-tech-business/725404/)
- RUBICONSmartCity (on AWS): onboard AI camera documents potholes, recycling/organics contamination, overflowing containers, illegal dumping; sold as monthly SaaS; used by >100 municipal heavy-duty fleets incl. Houston, Atlanta, Miami (snippet) — [Routeware blog](https://routeware.com/blog/how-ai-is-helping-cities-drive-improvements-in-infrastructure-and-citizen-satisfaction/)
- Example municipal buy: High Point, NC council committee approved a Routeware contract to add cameras to every sanitation truck — [Citizen Portal](https://citizenportal.ai/articles/8007947/North-Carolina/Guilford-County/High-Point/Council-committee-approves-RouteWare-contract-to-add-cameras-to-every-sanitation-truck)
- Routeware markets "verified, billable work" for waste disposal — [Routeware blog](https://routeware.com/blog/waste-disposal-software/)

**RoadRunner Recycling (Pittsburgh, US) + Compology - buyer/generator-side via managed service**
- Compology (San Francisco) built in-dumpster cameras + AI for container monitoring and "indisputable service verification"; acquired by RoadRunner in Oct 2022 (older info) — [Waste Dive](https://www.wastedive.com/news/roadrunner-recycling-compology-acquisition-ai-technology/633392/); [Compology Medium](https://medium.com/@compology/from-the-stone-age-to-the-future-indisputable-service-verification-for-waste-has-arrived-440afa707a83)
- A 2026 comparison notes a "Compology evaluation in 2026 is usually really an evaluation of RoadRunner" — sensing is delivered inside a managed waste service, not as a standalone tool — [Dyrt.co](https://dyrt.co/posts/compology-alternative)

**RTS - Recycle Track Systems (New York, US) - waste broker with Pello sensors**
- Acquired RecycleSmart (Canada's largest waste broker) and its Pello sensor — [Waste Dive](https://www.wastedive.com/news/rts-acquisition-recyclesmart-canada-pello/646232/); [Recycling Today](https://www.recyclingtoday.com/news/recycle-track-systems-acquires-recycle-smart-solutions/)
- Pello = ultrasonic fill-level sensor + multispectrum camera; detects fill level, location, contamination; "imaging AI and fullness data identifies pickups with over 95% accuracy"; data surfaces on the RTS customer portal — this is effectively buyer-side verification that the hauler actually emptied the bin — [RTS Pello](https://www.rts.com/product/pello/); [RTS Pello case study](https://www.rts.com/blog/pello-case-study/)
- RoadRunner filed a trade-secret suit against RTS over Pello technology (snippet; date not verified) — [search result referencing Pello litigation](https://www.wastedive.com/news/rts-acquisition-recyclesmart-canada-pello/646232/)

**MRF-side AI (material composition, not proof of pickup)**
- Greyparrot (London, UK): AI cameras above sorting belts identify material, product and brand; July 2026 $27M Series B (total ~$60M), led by Omar Mir; >1 trillion objects detected; customers WM, Veolia, Biffa, FCC, Circular Services — [Tech.eu, 28 Jul 2026](https://tech.eu/2026/07/28/greyparrot-secures-27m-series-b-to-scale-ai-waste-intelligence-for-the-circular-economy/); [Waste Dive](https://www.wastedive.com/news/greyparrot-27m-funding-round-scales-ai-recycling-analytics/826339/)
- AMP (Denver, US): $91M Series D, Dec 2024, led by Congruent Ventures (Sequoia and others participating), to roll out AMP ONE automated MSW sortation — [AMP](https://ampsortation.com/articles/amp-raises-91m-seriesd); [The Robot Report](https://www.therobotreport.com/amp-robotics-raises-91m-accelerate-deployment-recycling-systems/)

**Non-AI / light-AI buyer-side and SMB hauler tools**
- FTS GPS markets "waste collection verification" via GPS fleet tracking — [FTS GPS](https://www.ftsgps.com/industries/waste-management/)
- TrashLab, CurbWaste: SMB hauler software with GPS timestamps + photo proof of service to settle missed-pickup disputes (no confirmed CV) — [TrashLab](https://trashlab.com/waste-hauler-software-requirements-checklist); [CurbWaste FAQ](https://www.curbwaste.com/waste-hauler-technology-software-faq)
- Broker software guidance: brokers need work-order audit trails for "missed service investigations" with timestamps/attachments — [WP Reset article on waste broker software](https://wpreset.com/best-waste-broker-software-for-waste-management-operations/)

### Inferences
- Truck-camera CV for service verification is converging into a "layer on existing telematics" model (WasteVision on Lytx; AMCS/Routeware inside their own stacks). A new entrant would compete on integration breadth, not cameras.
- Buyer-side verification (the waste generator or municipality checking the hauler) exists mostly as a feature of vertically-integrated brokers (RTS/Pello, RoadRunner/Compology). A neutral, broker-independent multi-hauler verification tool for property managers or municipalities does not show up in results.
- Municipal contract monitoring of private franchise haulers (e.g., verifying missed pickups, contamination enforcement) is partly served by the same hauler-side tools the city buys for its own fleet (Routeware/Rubicon Smart City), not by an independent auditor product.

### Gaps
- Pricing for WasteVision, AMCS Vision AI, Hero Vision not public.
- Could not verify date/outcome of RoadRunner v. RTS Pello litigation.
- No reliable source found for dedicated municipal "franchise hauler compliance auditing" SaaS (independent of the hauler's own system). Did not research non-US waste CV vendors outside Greyparrot (e.g., EU/Israel/Asia truck-camera players).
- Waste Dive article with Routeware-Rubicon deal specifics could not be read (blocked).

## Q2. Construction and demolition (C&D) waste: software for disposal certificates, weigh tickets, diversion and permit/occupancy compliance

### Takeaway
In the US (especially California), Green Halo Systems is the de facto municipal C&D compliance portal: contractors upload weight tickets, the city approves a final diversion report before final inspection / Certificate of Occupancy. No AI is advertised. In the UK, mandatory Digital Waste Tracking (live from 2026) is creating a regulatory data layer, with BRE SmartWaste as the established project-level tracking tool.

### Cited Findings
- Green Halo: free web service for applicants to establish, monitor and document a C&D waste management plan; contractors upload weight tickets throughout the project and "Submit For Final"; approval of the Compliance Report is required before final building inspection and Certificate of Occupancy; supports 65% diversion requirement under CALGreen and SB 1383 — [City of Pinole instructions (Jan 2025)](https://www.pinole.gov/wp-content/uploads/2025/01/Green-Halo-Instructions-Jan-2025.pdf); [City of Lakewood CA instructions 2025](https://www.lakewoodca.gov/files/assets/public/v/3/residents/trash-amp-recycling-trees/brochures-and-articles/1-2025-green-halo-step-by-step-instructions.pdf)
- Municipal adopters include Brea, Carlsbad, Pinole, Lakewood (CA), Sonoma County (Permit Sonoma), Lafayette, Aspen (CO) — [City of Brea](https://www.cityofbrea.gov/1683/Construction-and-Demolition-Debris-CD); [Permit Sonoma](https://permitsonoma.org/greenhalo); [Carlsbad](https://www.carlsbadca.gov/departments/environmental-sustainability/reduce-reuse-recycle/construction-demolition); [Lafayette](https://www.lovelafayette.org/city-hall/quick-links/hot-topics/green-halo-waste-management-plans); [Aspen FAQ](https://aspen.gov/m/faq?cat=99#question-691)
- Pricing model: free to applicants (the municipality is the customer) — [Permit Sonoma](https://permitsonoma.org/sonomacountylaunchesgreenhaloconstructionwastemanagementplanandrecyclingtool)
- UK: Digital Waste Tracking mandatory for permitted waste receiving sites from Oct 2026 (England & Wales), Jan 2027 (Scotland, NI); carriers, brokers, dealers from Oct 2027; replaces paper waste transfer notes; receivers must submit records within two working days; public beta launched 28 Apr 2026 — [Reconomy](https://www.reconomy.com/digital-waste-tracking/); [Environment Agency blog, 30 Apr 2026](https://environmentagency.blog.gov.uk/2026/04/30/digital-waste-tracking-goes-live-a-major-step-forward-in-stopping-waste-crime/); [Digital Waste Tracking (England) Regulations 2026](https://www.legislation.gov.uk/ukdsi/2026/9780348282726)
- BRE SmartWaste: dataset of 4,791 UK construction projects (£34bn, 2016-2025) used for 41 waste/energy/water benchmarks — [BRE UK Construction Benchmarks 2026](https://bregroup.com/insights/uk-construction-benchmarks-2026)
- Commercial software vendors (e.g., The Access Group) are marketing waste software updates for UK mandatory digital waste tracking compliance — [The Access Group](https://www.theaccessgroup.com/en-gb/waste-management/mandatory-digital-waste-tracking/)

### Inferences
- The C&D workflow (weigh tickets, disposal certificates, facility receipts -> diversion % -> permit sign-off) is document-heavy and still manual upload + human review; this is a natural target for LLM/OCR extraction of weigh tickets and cross-checking against facility records, but no vendor was found advertising AI for it.
- The UK mandatory tracking regime will produce a national record of waste movements that could be used to verify contractor disposal claims; tools that reconcile contractor paperwork against that record are a likely emerging niche.

### Gaps
- No source found for AI-based weigh-ticket verification or fraud detection in C&D. Did not find verified info on other US C&D tools (e.g., Recology/hauler-provided reports, LEED tracking tools) or on Green Halo's own funding/size.
- No data on Israel or other non-English C&D permit compliance software.

## Q3. Commercial cleaning / janitorial: AI proof-of-service and inspection

### Takeaway
Most janitorial platforms (Swept, CleanTelligent, Janitorial Manager, OrangeQC, Connecteam-type tools) provide photo/QR/GPS proof and human-scored inspections, not AI. Genuine AI photo scoring comes from horizontal vision vendors (Tiliter's Cleensight) and new AI-app builders (QuantumByte, which explicitly accepts WhatsApp submissions). "Proof" (proofco.ai) presents itself as an AI-heavy platform, but its public footprint looks like programmatic SEO and its claims should be treated as unverified.

### Cited Findings
- Tiliter / Cleensight (Sydney, Australia; founded 2017): Vision AI turning photos into cleanliness scores, detecting debris, residue, spills, surface marks, flagging rework; "no hardware or setup"; adds assignments, mobile capture, workflow rules and audit-ready reporting; used for trains, public facilities and shared spaces — [Tiliter Cleensight](https://www.tiliter.com/cleensight); [Tiliter Cleanliness Evaluator](https://www.tiliter.com/vision-ai-agents/cleanliness-evaluator); [Tiliter blog](https://www.tiliter.com/blog/how-to-prove-cleaning-was-completed-with-photo-evidence)
- QuantumByte (quantumbyte.ai): build-your-own AI apps where crews submit photos, video or voice notes via mobile or WhatsApp; AI scores against the customer's standards and flags failures; dashboards with timestamped audit trails; pricing Free / $6 prototype / $29 per month Pro / Enterprise custom — [QuantumByte cleaning inspection](https://quantumbyte.ai/articles/cleaning-inspection-software); [QuantumByte best cleaning inspection apps](https://quantumbyte.ai/articles/best-cleaning-inspection-app)
- Proof AI (proofco.ai): claims AI dispatch, "Spatial Vision AI" with LiDAR/thermal, blockchain-hashed photos and signatures, FinTech split payouts, contractor license/insurance verification; site has near-identical city pages in many languages (e.g., Korean, Vietnamese, Hindi, Russian, Arabic variants for US cities) — [Proof cleaning](https://www.proofco.ai/cleaning/); [example localized city page](https://www.proofco.ai/ko/cleaning/massachusetts/cambridge)
- Swept (Canada): supervisor inspections with timestamped photos and instant quality scoring, plus ops and client comms — [Software Advice](https://www.softwareadvice.com/field-service/swept-profile/); [Swept inspection](https://sweptworks.com/janitorial-inspection-software)
- CleanTelligent: QA-focused, scored inspections by area, photo-attached deficiencies, client-facing quality reports — [Guideflow](https://www.guideflow.com/blog/janitorial-software)
- Janitorial Manager: Scan4Clean QR codes let cleaners open checklists on site and attach photos as proof of visit; Scan2Inspect for inspections — [Janitorial Manager vs Swept](https://www.janitorialmanager.com/blog/janitorial-manager-vs-swept/)
- OrangeQC: inspection software with photos, timestamps, GPS pings (also used for groundskeeping) — [OrangeQC](https://www.orangeqc.com/roles/groundskeeper-inspection-software/)
- Industry trend: ISSA reports growing demand for digital proof of service and real-time verification in cleaning (page itself blocked; headline only) — [ISSA](https://www.issa.com/industry-news/demand-for-digital-proof-of-service-grows-as-cleaning-operations-turn-to-real-time-verification/)
- Generic inspection platforms (SafetyCulture, GoAudits, eAuditor) list janitorial inspection templates — [SafetyCulture](https://safetyculture.com/apps/janitorial-inspection-software); [eAuditor, Jul 2026](https://eauditor.app/2026/07/12/janitorial-inspection-software/)

### Inferences
- The market splits into (a) vertical janitorial ops suites with manual QA and (b) horizontal vision-AI scorers. Nobody visible combines contract/scope-of-work -> auto-generated rules -> AI photo scoring -> client-facing multi-vendor report.
- Proofco.ai's many templated, machine-translated city pages and hyperbolic claims ("mathematically", "blockchain") suggest an early or SEO-driven site; the report writer should not treat it as a proven competitor without further diligence.

### Gaps
- No funding/size found for Swept, CleanTelligent, Janitorial Manager, Proof, QuantumByte, or Tiliter (Owler profile exists but not read). Connecteam and ProTeams were not specifically verified for AI proof-of-service features.

## Q4. Facility management vendor oversight platforms: AI delivery verification vs. invoice reconciliation vs. dispatch

### Takeaway
The big FM platforms (ServiceChannel, Corrigo/JLL, Facilio, Fexa) are adding AI mainly for work-order triage, invoice capture and invoice-to-rate validation. Facilio is the one that explicitly advertises AI that checks before/after photos against job notes. None was found doing independent computer-vision verification that physical work met a contract specification across multiple vendors.

### Cited Findings
- ServiceChannel (Fortive): "ServiceChannel AI" trained on 300M+ work orders detects wrong trades, unrealistic NTEs, multi-visit risk before dispatch; validates invoices against approved labor rates, hours, materials; AI computer vision captures PDF invoice content into invoice fields (beta Fall 2026); compliance holds keep work orders unbillable until compliance fields/attachments entered — [ServiceChannel AI](https://servicechannel.com/tools/ai-what-it-means-for-your-business/); [Summer 2026 release](https://servicechannel.com/blog/summer-2026-product-release/); [Spring 2026 release](https://servicechannel.com/blog/spring-2026-product-release/)
- Facilio: repositioned as AI-native; "Atom" autonomous agent suite launched Feb 2026; invoice validation AI with 3-way matching (invoice / work order / contract rates) pre-approval; autonomous COI (insurance) agent; work-order completion validator comparing before-and-after photos against job notes (sources are Facilio's own and a third-party roundup) — [Superkind AI FM tools review](https://superkind.ai/blog/ai-facility-management-tools); [Facilio AI in FM](https://facilio.com/blog/ai-in-facilities-management/); [Facilio agentic AI for ServiceChannel users](https://facilio.com/blog/agentic-ai-for-servicechannel-users/)
- Corrigo (JLL): cloud CMMS with contractor routing, NTE/SLA enforcement and invoice reconciliation across service-provider networks (per competitor Facilio's reviews; treat as biased source) — [Facilio Corrigo review](https://facilio.com/blog/corrigo-review/); [Superkind](https://superkind.ai/blog/ai-facility-management-tools)
- Fexa: FexaAI multi-agent AI for CMMS, strongest in multi-site retail; invoices flow in directly to finance/facilities — [Superkind](https://superkind.ai/blog/ai-facility-management-tools); [Fexa State of AI in FM](https://fexa.io/guide/state-of-ai-in-facilities-management/)
- Prefix Maintenance (founded 2022, US): Apr 2026 raised $7.5M; agentic-AI coordination layer between multisite restaurant/retail operators and independent local contractors; aims at 10,000+ locations — [SiliconANGLE, 14 Apr 2026](https://siliconangle.com/2026/04/14/prefix-raises-7-5m-scale-ai-driven-facility-management-platform/)
- WizyVision: AI field-photo app with geotagged photos, OCR meter reading, asset serial-number scanning, no-code capture screens — [WizyVision proof of service](https://wizyvision.com/proof-of-service)

### Inferences
- FM platforms verify the paper trail (rates, NTE, compliance attachments, invoice fields) far more than the physical outcome. Photo-based AI completion checks (Facilio) are early and single-platform.
- The buyer who uses many vendors across several platforms (or vendors not on any platform) lacks a neutral verification layer; this is a visible whitespace.

### Gaps
- Specialized trade verification for elevators, HVAC and fire-safety inspections (e.g., third-party inspection report compliance portals used by fire authorities) was not researched within the tool budget; no sourced vendors to report.
- Pricing of ServiceChannel/Corrigo/Fexa not captured (Facilio publishes a Corrigo pricing blog, not read).

## Q5. Landscaping, pest control, security patrol verification tools

### Takeaway
Landscaping proof-of-service is GPS/geofence + before/after photos with no confirmed AI. Pest control verification is strongest where the provider owns IoT devices (Rentokil PestConnect), giving the client a portal for auditors. Security patrol verification is mature (QR/NFC/GPS checkpoint proof), with AI only starting to appear (Deggy anti-spoofing, QR-Patrol AI image summaries, TrackTik AI incident reporting).

### Cited Findings
**Landscaping**
- Cappsure: GPS/geofence arrival/completion/departure, mandatory before-and-after photos, instant reports for clients, municipalities, property managers — [Cappsure landscaping](https://home.cappsure.com/landscaping/)
- Nektyd: GPS logs, timestamps, job records and photos per property visit as structured service records — [Nektyd](https://nektyd.com/landscaping-software)
- provvio: generic proof-of-service software (GPS check-ins, timestamped photos, checklists, auto client reports) — [provvio](https://provvio.com/proof-of-service-software)
- OrangeQC groundskeeper inspections; Fieldproxy, FieldServicely offer photo/GPS proof as FSM features — [OrangeQC](https://www.orangeqc.com/roles/groundskeeper-inspection-software/); [Fieldproxy](https://www.fieldproxy.ai/resources/blog/top-field-service-management-software-for-landscaping-companies-d1-13)

**Pest control**
- Rentokil PestConnect: infrared-sensor connected rodent devices plus smart cameras with AI to identify rodents, insects, birds; alerts to server and local tech; data in PestNetOnline; myRentokil portal lets customers download digital proof-of-service reports for audits — [Rentokil PestConnect](https://www.rentokil.com/services/digital-pest-control/pestconnect); [Rentokil smart monitoring UK](https://www.rentokil.co.uk/pest-control/smart-remote-pest-monitoring/); [myRentokil](https://www.rentokil-boecker.com/myrentokil)

**Security patrol**
- TrackTik (Trackforce): guard-tour verification via NFC/QR/barcode/GPS geofence, geofenced clock-out alerts, AI-powered incident reporting, command center — [Trackforce TrackTik guard tour](https://www.trackforce.com/products/tracktik/security-guard-tour-system/); [Trackforce 2026 comparison](https://www.trackforce.com/resources/blog-articles/security-officer-tracking-software-guide-tracktik-vs-qr-patrol-vs-guardspro-2026-comparison/)
- Silvertrac (also Trackforce): QR/barcode/NFC checkpoints with auto GPS/time logging; ~4.7 Capterra — [Trackforce Silvertrac](https://www.trackforce.com/products/silvertrac/); [SafeTrac comparison](https://safetrac.io/best-security-guard-management-software/)
- Deggy: AI verifies each checkpoint scan for authenticity, detects counterfeit QR codes ("ghost patrols") — [Deggy](https://deggy.com/); [Deggy App Store](https://apps.apple.com/us/app/deggy-ai-guard-tour/id6443438611)
- QR-Patrol (used in 90+ countries): QR/NFC/BLE/geofence proof of presence; client schedule performance report; AI-assisted image summaries — [QR-Patrol features](https://www.qrpatrol.com/features); [QR-Patrol updates](https://www.qrpatrol.com/blog-categories/application-updates)
- A third-party 2026 review says only QR-Patrol and Deggy have confirmed native AI; it lists TrackTik as having none, contradicting Trackforce's own "AI-powered incident reporting" claim — [Digitalguardtour/review snippet](https://digitalguardtour.com/top-5-tracktik-alternatives-2026/); contradicted by [Trackforce](https://www.trackforce.com/resources/blog-articles/security-officer-tracking-software-guide-tracktik-vs-qr-patrol-vs-guardspro-2026-comparison/)

### Inferences
- Security is the only vertical with a norm of client-facing proof-of-presence reports; its weak spot is spoofing (photographed QR codes), which is where AI is entering.
- Pest control verification is locked inside large providers' proprietary IoT portals; SMB pest companies and buyers with multiple pest vendors have no equivalent.

### Gaps
- Did not verify pest-control FSM software (PestPac/WorkWave, FieldRoutes, GorillaDesk) AI features, or Pelsis/other independent IoT trap vendors. No AI landscaping-specific verification vendor found.

## Q6. WhatsApp-native or no-app-install tools

### Takeaway
Only QuantumByte was found explicitly accepting field-worker evidence via WhatsApp for AI scoring. Tiliter Cleensight is "no hardware" but still uses its own capture flow. Truck-camera waste AI is "no driver action" by design. No established vertical vendor was found that is WhatsApp-native.

### Cited Findings
- QuantumByte: submissions "through WhatsApp or other channels the team already uses"; AI scores them; timestamped audit trail — [QuantumByte](https://quantumbyte.ai/articles/cleaning-inspection-software)
- WasteVision: contamination detection "without the driver lifting a finger" from existing truck cameras (snippet) — [WasteVision](https://wastevision.ai/contamination-detection.html)
- Tiliter Cleensight: "no hardware or setup required" — [Tiliter](https://www.tiliter.com/cleensight)
- Evidence-integrity concern: plain images/WhatsApp media carry no inherent proof of authenticity; courts increasingly skeptical in 2026 given AI fakes — [PrintChat blog](https://printchat.app/en/blog/whatsapp-screenshots-rejected-court-evidence-2026); [ProofSnap](https://getproofsnap.com/whatsapp-voice-notes-evidence.html)

### Inferences
- WhatsApp-first capture is a clear gap for SMB, non-English and subcontractor-heavy markets (Israel, LatAm, India, where WhatsApp is the default work channel), but it must be paired with anti-tampering (metadata, geolocation, liveness) to be trusted as proof.

### Gaps
- Did not find verifiable WhatsApp-native vendors in Israel, LatAm or India for field-service proof; this likely needs local-language searches.

## Q7. Visible gaps in the market

### Takeaway
Gaps cluster around (1) neutral multi-vendor buyer view, (2) contract-to-rules automation, (3) SMB providers without camera fleets or enterprise suites, (4) WhatsApp/non-English workflows, and (5) AI on documentary evidence (weigh tickets, disposal certificates, invoices) outside the FM giants.

### Cited Findings
- Buyer-side verification in waste mostly comes bundled with brokerage (RTS Pello portal, RoadRunner/Compology managed service) — [RTS Pello](https://www.rts.com/product/pello/); [Dyrt.co](https://dyrt.co/posts/compology-alternative)
- FM AI focuses on invoices/rates/NTE and dispatch anomalies, not physical outcomes — [ServiceChannel AI](https://servicechannel.com/tools/ai-what-it-means-for-your-business/); [Superkind](https://superkind.ai/blog/ai-facility-management-tools)
- C&D compliance is manual weigh-ticket upload and municipal review — [Pinole Green Halo instructions](https://www.pinole.gov/wp-content/uploads/2025/01/Green-Halo-Instructions-Jan-2025.pdf)
- Janitorial and landscaping tools are photo/GPS/QR evidence with human scoring — [Guideflow](https://www.guideflow.com/blog/janitorial-software); [Cappsure](https://home.cappsure.com/landscaping/)
- Security AI is limited to a few vendors (Deggy, QR-Patrol) per a 2026 review — [Digitalguardtour](https://digitalguardtour.com/top-5-tracktik-alternatives-2026/)

### Inferences
- Multi-vendor buyer view: a property/facility manager or municipality overseeing cleaning + waste + landscaping + pest + security vendors has no single AI verification layer; each vertical tool is provider-side or single-vendor.
- Contract-to-rules: no vendor found that ingests a service contract/SLA (frequency, scope, quality standards) and automatically turns it into verification rules and exception reports; QuantumByte's "configured to your standards" is the closest but is manual configuration.
- SMB providers: AI truck-camera verification requires connected cameras (Lytx etc.); SMB cleaners/landscapers rely on generic FSM apps; low-cost photo-AI (QuantumByte $29/mo) is the exception.
- Non-English markets: nearly all identified vendors are US/UK/Australia/Canada-centric; only Greyparrot (UK/EU) and Rentokil (global) have multinational reach, and neither targets proof-of-service for SMB buyers.
- Evidence integrity (anti-spoofing, deepfake-resistant capture) is an emerging requirement (Deggy's fake-QR detection; court skepticism of photos).

### Gaps
- No quantitative market sizing found for the "proof-of-service verification" category specifically.
- No G2/Capterra category data retrieved on how many vendors claim AI verification.
- Elevator/HVAC/fire-safety inspection compliance vendors not covered.
