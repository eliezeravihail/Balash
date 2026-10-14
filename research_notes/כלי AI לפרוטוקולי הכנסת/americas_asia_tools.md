# AI/RAG/LLM tools over legislative proceedings outside Europe and Israel (Americas, Asia, Oceania, Africa), as of Oct 2026

Method note: about 17 tool calls. WebFetch failed with DNS errors (ENOTFOUND) for fedscoop.com, journalismai.info, mobiletime.com.br and openparliament.ca. Most findings below therefore come from search-result snippets and summaries, not full-page reads. Claims marked **[verified-primary]** come from an official or project's own page as shown in search. **[secondary]** means news or an aggregator. **[unverified]** means a single or weak source.

## US: Congress, CRS, civic-tech and commercial tools

### Takeaway
The most important US data point is a negative one. CRS spent two years testing six LLMs on bill summarization, and fewer than 3% of 3,000 summaries met its accuracy and objectivity standards. CRS has now switched to narrow, decomposed AI tasks such as triage. The strongest civic-tech model is CalMatters' Digital Democracy. It uses AI transcription, face-recognition speaker attribution with human confirmation, and OpenAI LLM "Tip Sheets" that go only to reporters as leads, never as published facts. Commercial vendors (FiscalNote, Plural) advertise "grounded" summaries but publish no evaluation.

### Cited Findings
- **CRS / Library of Congress LLM bill-summary experiment.** At a House Administration Committee hearing (June 25, 2026), CRS Director Karen Donfried said CRS tested 6 LLMs on hundreds of bills and produced 3,000 AI summaries. Fewer than 3% met CRS's accuracy and objectivity standards, over a two-year project [secondary]. Sources: [FedScoop](https://fedscoop.com/crs-tried-to-use-ai-but-less-than-3-of-results-met-their-standards/); [Bloomberg Government](https://news.bgov.com/bloomberg-government-news/ai-bill-summary-test-deemed-flop-by-congressional-research-head); [House Admin Committee takeaways](https://cha.house.gov/2026/6/top-takeaways-from-full-committee-hearing-on-the-congressional-research-service-and-ai) [verified-primary, official committee page as listed in search].
- CRS's new approach breaks the workflow into steps instead of generating whole summaries. An early candidate is AI that flags which bills are heading to the floor, so analysts can prioritize them — [FedScoop](https://fedscoop.com/crs-tried-to-use-ai-but-less-than-3-of-results-met-their-standards/).
- CRS is reported to be seeking a $1.6M increase for FY2027 and planning a 12-month evaluation of five tools (Claude, ChatGPT, Google AI, Perplexity, MS Copilot) [unverified, single secondary source] — [legis1.com](https://legis1.com/news/ai-bill-summaries-accuracy-fail-congressional).
- Earlier, CRS's interim director said the agency was working on "five models" for bill summaries. He also said Politico's AI-generated summaries, which CRS reviewed, "did not pass the test" — [FedScoop](https://fedscoop.com/congressional-research-service-eyes-ai-bill-summaries/).
- No source was found showing AI-generated summaries published on Congress.gov itself. See Gaps.
- **CalMatters Digital Democracy (California Legislature).** This is a philanthropically funded project hosted by CalMatters and built with Cal Poly San Luis Obispo (Prof. Foaad Khosmood) and the web firm Fueled/10up — [Fueled case study](https://fueled.com/work/calmatters-digital-democracy/); [SVCAF seminar](https://svcaf.org/posts/ai4legislation-seminar-5-recording-slides-and-summary/).
  - Pipeline: hearing video goes through AI transcription. Quotes are attributed to speakers using facial recognition, and human editors confirm the attribution. OpenAI LLMs then run over bill text and transcripts to produce "Tip Sheets" — [JournalismAI Innovation Challenge 2024 profile](https://www.journalismai.info/programmes/innovation/innovation-challenge-2024/calmatters) (snippet only).
  - Tip Sheets are AI-generated story leads sent to registered reporters in near real time as hearings happen and votes are taken. Each describes the anomaly (for example an unusual voting pattern or a possible conflict of interest), how the AI found it, and why it was flagged — [National Press Foundation](https://nationalpress.org/?p=50130); [Dick Tofel interview with Neil Chase](https://dicktofel.substack.com/p/bringing-digital-democracy-to-california).
  - Neutrality and hallucination handling: the tool draws a line between data and "the conclusions or the ideas that the AI is identifying". Reporters treat tips as leads and verify them with editors before publishing — [Tofel/Chase interview](https://dicktofel.substack.com/p/bringing-digital-democracy-to-california). Tip Sheets are shared with other news outlets in a careful rollout — same source. Cal Poly also built an "AI Robot Reporter" — [SVCAF](https://svcaf.org/posts/ai4legislation-seminar-5-recording-slides-and-summary/).
  - CalMatters links Digital Democracy to a 2026 "trust challenge" win — [CalMatters Inside the Newsroom, Apr 2026](https://calmatters.org/inside-the-newsroom/2026/04/trust-challenge-win/) (details not read).
- **Plural (formerly Plural Policy; built on Open States data), commercial.** Features: AI bill summaries, AI summaries of the differences between bill versions, ML topic tagging, cross-jurisdiction similar-bill search (it finds model and omnibus bills), a "Momentum Indicator" that predicts which bills will advance, and the "Plural Policy Analyzer". Plural claims fewer inaccuracies than ChatGPT, but this is vendor marketing — [Plural AI-powered bill tracking](https://pluralpolicy.com/ai-powered-bill-tracking/); [Plural AI insights](https://pluralpolicy.com/ai-powered-insights/). Plural was reportedly acquired by SAI360 on Dec 1, 2025 [secondary] — [LegalTechnologyHub](https://www.legaltechnologyhub.com/vendors/plural-by-sai360/).
- **FiscalNote (PolicyNote / Copilot for Policy), commercial.** Copilot for Policy (2024) is "powered by FiscalNote's authoritative, proprietary databases" — [FiscalNote newsroom](https://fiscalnote.com/newsroom/copilot-for-policy). The PolicyNote AI assistant (Jan 2025) is said to pull "only from verified sources" — [BusinessWire Jan 2025](https://www.businesswire.com/news/home/20250115254693/en). FiscalNote added legislative forecasting alerts and bill discovery (June 2025) — [BusinessWire](https://www.businesswire.com/news/home/20250612678578/en/FiscalNote-Accelerates-AI-Innovation-with-New-Enhancements-to-PolicyNote-for-Legislative-Forecasting-Alerts-and-Bill-Discovery). AI legislative drafting followed (July 2025) — [FiscalNote](https://fiscalnote.com/newsroom/fiscalnote-expands-policynote-with-ai-powered-legislative-drafting-giving-policy-professionals-a-new-strategic-edge). FiscalNote also sells congressional hearing transcripts — [FiscalNote](https://fiscalnote.com/products/congressional-hearing-transcripts). No public hallucination or citation evaluation was found.
- **Academic datasets.** C-QUERI (arXiv 2509.21548) is a dataset of question/answer exchanges from 16,130 congressional hearings, covering the 108th–117th Congresses and built from transcripts available as of April 2022. It is a dataset paper, not a RAG benchmark, but it is a usable QA corpus — [arXiv](https://arxiv.org/pdf/2509.21548). ScalableRAG (arXiv 2607.25135) uses US Senate hearing transcripts from GovInfo as its RAG corpus. Its evaluation details were not verified — [arXiv](https://arxiv.org/pdf/2607.25135).
- Anecdotal user practice: a health-policy blogger reports ChatGPT saved hours finding seven statements by RFK Jr. in hearing records. This is anecdotal, not an evaluation — [Discoveries in Health Policy, May 2026](https://www.discoveriesinhealthpolicy.com/2026/05/chat-gpt-saves-hours-finding-7-rfk-jr.html).

### Inferences
- The CRS result is the strongest public evidence that free-form, "neutral" LLM summaries of legislation fail strict objectivity and accuracy standards. For a Knesset RAG this argues for extractive or quote-anchored answers, decomposed tasks (classify, triage, locate) and human review, rather than authoritative generated summaries.
- Digital Democracy's design has three lessons worth borrowing for the Knesset project:
  - Treat speaker attribution as a first-class, human-verified layer.
  - Frame LLM output as "leads", with an explanation of why each item was flagged.
  - Keep data and AI inference visibly separate.
- Vendor phrases like "grounded" and "verified sources" come with no published metrics. This suggests the sector has no shared evaluation standard, which is an opportunity to publish one for Hebrew.

### Gaps
- Whether Congress.gov has shipped any public generative-AI feature (search or summaries) by Oct 2026. Not found.
- GovTrack, LegiScan, BillTrack50 and Quiver: no AI-feature evidence was gathered within the call budget.
- Details of the Digital Democracy stack (vector DB, retrieval, evaluation metrics) beyond "OpenAI LLMs". The primary page could not be fetched.
- GitHub hearing-transcript RAG projects were not surveyed.

## Canada

### Takeaway
No reliable evidence was found within this research's budget that OpenParliament.ca or the House of Commons offers official generative-AI Q&A over Hansard. Community MCP servers (for example FedMCP) wrap Canadian parliamentary data for LLMs.

### Cited Findings
- OpenParliament.ca is a volunteer project by Michael Mulley. It reformats Hansard by topic and date and exposes an API that third-party tools use — [Slaw](https://www.slaw.ca/?p=19457); [myparliament.ca credits](https://myparliament.ca/credits).
- "FedMCP" (northernvariables) is an MCP server exposing Canadian federal parliamentary data to LLM agents [unverified, directory listing only] — [Glama](https://glama.ai/mcp/servers/northernvariables/FedMCP/tree/17d533ce29be7ff8dc602d8e3ba72b9e5fdb352d).
- An Omdena chapter challenge "CanPolicy Insight" applied LLMs to Canadian policy documents (volunteer project) — [Omdena](https://www.omdena.com/chapter-challenges/canpolicy-insight-clear-insights-into-canadian-policies-leveraging-llm).
- MPs have debated AI use in the Commons, and AI use is reportedly permitted under current House rules [secondary] — [LetsDataScience](https://letsdatascience.com/news/canadian-mps-debate-ai-use-in-commons-9699c4cd).

### Inferences
- The MCP-server pattern (exposing parliamentary APIs as LLM tools) is a cheap, growing alternative or complement to a bespoke RAG UI. A Knesset MCP server over the Knesset OData API would follow the same pattern.

### Gaps
- Whether openparliament.ca now shows AI-generated bill or debate summaries. The site could not be fetched (DNS failure), and the researcher's prior recollection that it carries such summaries is unverified, so this is not claimed.

## Brazil and Latin America

### Takeaway
Brazil's Chamber of Deputies "Ulysses" is the most mature official parliamentary AI ecosystem in the region. It started in 2018 with classical ML that links legislative data, and it now includes generative AI: a staff chat over rules and procedures plus access to commercial LLMs. Its governance policy and more than 12,000 users are cited. Bússola Tech and the Chilean Chamber run the regional knowledge network.

### Cited Findings
- Ulysses launched in 2018 as a "digital robot" that combines several AI algorithms to automatically link legislative data across the portal and internal systems. It is named after Ulysses Guimarães — [Câmara notícias](https://www.camara.leg.br/noticias/548730-camara-lanca-ulysses-robo-digital-que-articula-dados-legislativos/) [verified-primary].
- New phase: a chat that lets staff query the Chamber's rules, services and procedures, with access to Claude, Gemini and ChatGPT. Chamber president Hugo Motta launched AI and data-governance policies [secondary, date of article not confirmed] — [Mobile Time](https://www.mobiletime.com.br/?p=843793). The 2025 management report mentions a "new stage of the Ulysses ecosystem" applying AI to administrative and legislative routines — [Câmara gestão 2025](https://www2.camara.leg.br/a-camara/estruturaadm/gestao-na-camara-dos-deputados/principais-acoes-da-gestao-2025/view).
- Gartner CIO Brazil session (Sept 2026): Patricia Almeida, Data & AI Lead, describes Ulysses as an ecosystem integrating traditional and generative AI, with more than 12,000 users and "responsible governance" — [Gartner](https://www.gartner.com/en/conferences/la/cio-brazil/sessions/detail/5941969-Gartner-Talks-Patricia-Almeida-Data-and-AI-Lead-at-the-Brazilian-Chamber-of-Deputies--How-the-Ulysses-AI-Ecosystem-Brings-Efficiency-and-Responsible-Governance).
- Brazil's Chamber of Deputies contributed use cases to the IPU's collection of more than 40 parliamentary AI use cases — [IPU news, July 2024](https://www.ipu.org/news/news-in-brief/2024-07/artificial-intelligence-draft-ipu-resolution-and-use-cases-ai-in-parliaments-published).
- Chile: the Chamber of Deputies and Bússola Tech co-hosted a June 2024 conference in Valparaíso on AI in parliaments. Topics included legislative drafting, records management, bias, gender stereotypes and privacy — [Programme](https://www.camara.cl/conferenciaia/img/docs/PROGRAMME_EN.pdf); [ParlAmericas press release](https://parlamericas.org/uploads/documents/PressRelease-BussolaTech-Chile-en.pdf).
- Bússola Tech, the OAS, the CPA and Rio Grande do Norte's assembly published the book "Artificial Intelligence in Legislative Services: Principles for Effective Implementation". Its authors include staff from Brazil's Senate and Chamber and from Argentina's Chamber. It stresses human oversight and staff training — [Civictech directory](https://directory.civictech.guide/listing/artificial-intelligence-in-legislative-services-principles-for-effective-implementation).
- A ParlAmericas staff meeting (Aug 2024) had a panel on AI with Chilean and Mexican Chamber of Deputies officials — [Agenda](https://www.parlamericas.org/uploads/documents/Agenda-ParlStaffMeeting-2024-08-13-en.pdf).
- Academic: a Brazilian paper on AI as an instrument supporting rationality in the legislative process — [Revista Mackenzie de Direito](https://editorarevistas.mackenzie.br/rmd/article/view/16334); a Portuguese NLP book chapter on legal NER — [Brasileiras em PLN](https://brasileiraspln.ufscar.br/livro-pln-4ed-vol3/aplicacoes-e-dominios/cap-direito-ren/cap-direito-ren.pdf).

### Inferences
- Ulysses shows a staged path: classification and linking first (2018), generative features later, under an explicit AI governance policy. Internal, staff-facing tools came before public-facing ones. A Knesset project could copy this order: start internal, publish a governance policy, then expose features publicly.

### Gaps
- Ulysses' technical stack, its RAG design over rules and procedures, and its evaluation methods were not found in accessible sources.
- No concrete generative-AI tools were confirmed for Argentina, Mexico or Chile's Senate.

## Asia: Taiwan, India, Japan, Korea

### Takeaway
India has the clearest official programme: Sansad Bhashini (Lok Sabha with MeitY, March 2025). It covers speech-to-text verbatim transcription (deployed from the July 2025 session), translation of legacy debates into regional languages, and a planned rules chatbot. Japan's activity is mostly executive-side AI drafting of answers that uses Diet minutes. Korea's National Assembly Library has research experiments in generative-AI summarization and indexing. Taiwan's activity found was policy-level, not a deployed RAG tool.

### Cited Findings
- **India.** On 18 March 2025 the Lok Sabha Secretariat and MeitY signed an MoU for a "Sansad AI" solution under Bhashini. Parliamentary data will be used to fine-tune the tools — [NeGD press release PDF](https://negd.gov.in/wp-content/uploads/2025/03/Press-Release-Lok-Sabha-Secretariat-and-MeitY-Sign-MoU.pdf) [verified-primary]. Planned scope: AI translation of legacy debates, agenda and committee proceedings into regional languages, speech-to-text, speech-to-speech, and a chatbot on procedural rules — [Inc42](https://inc42.com/?p=505553); [OpenGovAsia](https://archive.opengovasia.com/2025/03/19/ai-revolutionising-indias-parliamentary-operations/). A 14 July 2025 Lok Sabha press release says an AI verbatim-transcription tool on the Sansad Bhashini STT model would run alongside human reporting from the coming session — [Lok Sabha press release](https://pprloksabha.sansad.in/PressReleaseFiles/file1475.pdf) [verified-primary]. Lok Sabha also plans AI tools and a chatbot for MPs to access parliamentary records [secondary] — [Deccan Herald](https://www.deccanherald.com/amp/story/india%2Flok-sabha-plans-ai-tools-chatbot-for-mps-to-access-parliament-records-3451937). An IIT Madras blog analyses AI in Indian parliamentary debate during the 2025 Budget session — [IITM WSAI](https://wsai.iitm.ac.in/blogs/ai-indian-parliament-budget-session-2025/).
- **Japan.** Defense Minister Koizumi said (24 April 2026, House of Representatives Security Committee) that an in-ministry AI team drafts answer outlines — [hashout.jp](https://hashout.jp/ai/318/). The Digital Minister disclosed using AI for Diet answers, and concerns about bureaucrats' over-reliance and misinformation were reported — [Hokkaido Shimbun](https://www.hokkaido-np.co.jp/article/1332166/). METI reportedly ran a pilot feeding five years of Diet minutes to AI to draft answer texts [secondary via Nikkei, date unconfirmed]. Commentators note consistency with past answers is a key risk — [Agora](https://agora-web.jp/?p=65393). In March 2023 a CDP member asked PM Kishida questions generated by ChatGPT — [ITmedia](https://www.itmedia.co.jp/news/article/2303/29/1230329170/). A May 2026 Upper House written question asks about archiving generative-AI prompts as public records — [Sangiin](https://www.sangiin.go.jp/japanese/joho1/kousei/syuisyo/221/meisai/m221049.htm).
- **Korea.** National Assembly Library research reports (2024 research, published 2025) document experiments using generative AI for summarization, automatic classification, subject indexing and keyword extraction — [NANET record](https://dl.nanet.go.kr/detail/REFD0002470113); [NANET record](https://dl.nanet.go.kr/detail/REFD0002470100). The NANET site describes legislative-support services "from parliamentary and legal info to AI analysis" [snippet]. No public generative-AI search over the 회의록 (minutes) was confirmed.
- **Taiwan.** WFD launched Mandarin AI guidelines for parliaments with the Taiwan Foundation for Democracy. Legislator Ko Ju-chun called them a parliamentary "AI basic law". Legislator Su Chiao-hui warned of manipulation and accountability gaps — [WFD](https://www.wfd.org/news/supporting-taiwans-digital-democracy-wfd-launches-ai-guidelines-parliaments-mandarin). In 2024 a legislator's team used ElevenLabs voice cloning so a colleague could interpellate, a first in the Legislative Yuan — [ElevenLabs blog](https://elevenlabs.io/zh/blog/taiwan-parliament) (vendor source).

### Inferences
- India's sequence (speech-to-text, then translation, then chatbot) mirrors the Knesset's need for good Hebrew ASR and transcript structure before RAG. Fine-tuning on in-house parliamentary data is the explicit strategy.
- Japan's "AI drafts answers from past minutes" use case shows that consistency with prior statements is a key retrieval task, and that it carries political risk.

### Gaps
- No g0v project offering LLM Q&A over Legislative Yuan records was found. g0v's long-running ly.govapi.tw / Legislative Yuan data APIs were not verified in this session.
- PRS Legislative Research (India): no AI features were found or searched.
- Korea: no confirmed public National Assembly chatbot.

## Australia, New Zealand, South Africa

### Takeaway
No evidence was found of generative-AI features on OpenAustralia or South Africa's PMG. Both remain search, alert and human-minutes platforms. PMG's human workflow (audio published immediately, edited minutes within 24–36 hours, editorial QC) is a neutrality benchmark that AI summaries would have to meet.

### Cited Findings
- OpenAustralia is run by the OpenAustralia Foundation on mySociety's TheyWorkForYou code. Its strengths are search, RSS and email alerts — [OpenAustralia about](https://www.openaustralia.org.au/about/); [API](https://openaustralia.org.au/api).
- PMG monitors attend all committee meetings, record and minute them, and publish audio right away. Written reports follow after editorial and quality control, aiming for objective, accurate reports within 24–36 hours — [PMG](https://pmg.org.za/page/what-is-pmg); [OpeningParliament case study](https://openingparliament.org/blog-sub/post/72453070135/case-study-8-parliamentary-monitoring-groups).

### Inferences
- These PMOs are natural RAG corpora (clean, structured minutes), but they have not publicly adopted LLMs. This may reflect caution about neutrality or limited resources. That reading is speculative.

### Gaps
- Australian Parliament (APH/ParlInfo) and New Zealand Parliament generative-AI pilots were not found in this session.
- mySociety's 2024–2026 AI experiments (UK-based, out of scope) may have spilled over to OpenAustralia. Not verified.

## Global frameworks (IPU, Bússola Tech, NDI/WFD)

### Takeaway
The IPU's Guidelines for AI in Parliaments (Dec 2024) and its use-case library are the reference framework. They are licensed CC BY-NC-SA, recommend small pilots, human oversight and transparency, and come with 40+ use cases from parliaments.

### Cited Findings
- The IPU CIP and its Parliamentary Data Science Hub launched the Guidelines and use cases in December 2024. Use cases cover bill drafting and amendments, verbatim reports and subtitles, analysis of public submissions, and cybersecurity — [IPU use cases](https://www.ipu.org/resources/publications/reference/2024-12/use-cases-ai-in-parliaments); [IPU press release](https://www.ipu.org/news/press-releases/2024-12/new-ipu-tools-harness-potential-ai-in-parliament); [About the guidelines](https://www.ipu.org/ai-guidelines/about-guidelines).
- Recommendations: start with small pilots, pick clear-benefit and manageable-risk use cases, keep humans in oversight, and prioritise transparency and accountability. The material is licensed CC BY-NC-SA 4.0 — [IPU](https://www.ipu.org/ai-guidelines/about-guidelines).
- More than 40 use cases were contributed by July 2024, including from Brazil's Chamber — [IPU](https://www.ipu.org/news/news-in-brief/2024-07/artificial-intelligence-draft-ipu-resolution-and-use-cases-ai-in-parliaments-published).
- The IPU also covers inter-parliamentary cooperation on AI — [IPU](https://www.ipu.org/ai-guidelines/inter-parliamentary-cooperation-ai). WFD has commentary on parliaments harnessing AI democratically — [WFD](https://wfd.org/commentary/how-parliaments-can-harness-benefits-ai-democratically).

### Inferences
- A Knesset RAG project can align its governance documents with the IPU guidelines, which are reusable under CC BY-NC-SA. The project could also submit itself as an IPU use case.

### Gaps
- No NDI-specific report on AI in legislatures was located in this session.
- No IPU AI "hub" tracker statistics for 2026 were retrieved.
