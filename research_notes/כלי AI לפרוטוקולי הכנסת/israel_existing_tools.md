# Existing Israeli AI/RAG/search tools over Knesset protocols (as of 2026-10-14)

Method note: research done 2026-10-14. "VERIFIED" means I opened the page (via WebFetch or GitHub API). "SNIPPET-ONLY" means the information comes only from a search-engine result or summary because the sandbox proxy blocked the domain. Blocked domains: knesset-ai.com, zmanknesset.co.il, goinfo.co.il, oknesset.org, huggingface.co, geektime.co.il, israelhayom.co.il, glama.ai, main.knesset.gov.il, onrender.com. GitHub was reachable.

## Is there any existing RAG/chatbot over Knesset protocols (Hebrew or English)?

### Takeaway
Yes. Since early 2026 there have been several small, individually built open-source projects. **knesset.watch** is the most complete: a hosted Next.js dashboard with Gemini-based RAG "Ask" over committee and plenary transcripts. **knesset-lm** (an agent with a protocol summarizer and SQLite FTS) and **knessy** (LangGraph with OpenSearch hybrid RAG and an MCP server) are also notable. All of them are hobby or solo projects with 0–2 stars. None is institutional, well-known or evaluated, and none was covered in the Israeli tech press that I could find. Third-party protocol sites also exist (knesset-ai.com, zmanknesset.co.il, goinfo.co.il full-text search), but I could not open them to confirm whether they have AI features.

### Cited Findings
**knesset.watch** (github.com/knesset-watch/knesset.watch). VERIFIED (repo README).
- A Hebrew dashboard for MKs, bills, votes, committees, plenary speeches and ministers. The README describes "AI-powered Hebrew search across protocol transcripts" using RAG over committee and plenary turns. — [GitHub](https://github.com/knesset-watch/knesset.watch)
- Stack: Gemini for query rewriting, streamed answers and Google Search grounding; Jina AI 256-dim embeddings; Turso (libSQL) for protocol search and vectors; Upstash Redis cache (2h TTL); Next.js 16, Tailwind, RTL; SQLite (better-sqlite3); Vercel and Render. — [GitHub](https://github.com/knesset-watch/knesset.watch)
- Status: about 450 commits, created 2026-03-30, last updated 2026-09-30. Production at knesset.watch is password-gated. An open deployment runs at afarkeset-laknesset.onrender.com ("אפרכסת לכנסת"), with budget caps on /ask. I could not open the deployment because the proxy blocked it. — [GitHub](https://github.com/knesset-watch/knesset.watch); dates from the GitHub API search.

**knesset-lm** (omriysh/knesset-lm). VERIFIED (repo README).
- The web app is called "מעורב ירושלמי". It is an AI research agent that answers Hebrew questions about MKs and committees from protocols, votes and bills, and cites the transcript or API result it used. — [GitHub](https://github.com/omriysh/knesset-lm)
- Components: a protocol summarizer (src/summarization, using the Gemini batch API for bulk summarization); agent tools `query_protocols`, `get_meeting_attendance`, `find_mk`, `query_bills`, `query_votes`; a state-machine agent designer UI. — [GitHub](https://github.com/omriysh/knesset-lm)
- Stack: Python, llama.cpp local models or the Gemini API, SQLite FTS5. No vector DB is mentioned, so retrieval is lexical. Data comes from Knesset OData v4 and the oknesset.org API, with raw transcriptions stored per Knesset and committee. Runs locally only (localhost:5000). MIT license, 187 commits, 0 stars, created 2026-02-27, updated 2026-10-05. — [GitHub](https://github.com/omriysh/knesset-lm)

**knessy / "Knesset Helper"** (amnir/knessy). VERIFIED.
- An "agentic research assistant for Israeli Knesset data — LangGraph + RAG + MCP". The pipeline is Planner → Researcher → Judge (up to 3 loops) → Synthesizer, producing a cited answer. — [GitHub](https://github.com/amnir/knessy)
- Committee protocols are indexed in OpenSearch with hybrid kNN and BM25 search. A prebuilt OpenSearch snapshot is hosted on Hugging Face. It uses the OpenAI API and runs as a CLI or a local Gradio-style web UI (port 7860, Chat and Search tabs, RTL). It also has an MCP server with `search_bills`, `get_bill_details`, `get_bill_votes` and `search_protocols`. MIT license, 22 commits, 1 star, created 2026-04-02, last updated 2026-04-19, which suggests it is dormant. — [GitHub](https://github.com/amnir/knessy)

**glassy-knesset** (aaronprais). VERIFIED.
- A planned local agent: LangGraph, Ollama (DictaLM 3.0, Qwen2.5-Coder), OData-to-pandas analysis, and RAG over the API schema rather than over protocols. It is a scaffold only: every module raises NotImplementedError. Created 2026-08-15. — [GitHub](https://github.com/aaronprais/glassy-knesset)

**Third-party protocol sites.** SNIPPET-ONLY.
- **knesset-ai.com** (title "פרוטוקולי הכנסת"). It describes itself as a single portal for "protocols of plenary sessions and committees, laws passed in third reading", votes, MK profiles and political analysis. I could not confirm the owner or which AI features it has, because the domain was blocked. — [knesset-ai.com via search](https://knesset-ai.com/)
- **zmanknesset.co.il/committees/protocols**: lists committee protocols by date and topic and shows "no protocol published yet". I found no indication of AI features. — [zmanknesset](https://zmanknesset.co.il/committees/protocols)
- **goinfo.co.il/knesset/protocols/search.html**: a private site that, according to the search summary, offers advanced-syntax full-text search over 25th-Knesset committee and plenary protocols. It is lexical search, not AI. — [goinfo](https://goinfo.co.il/knesset/protocols/search.html)

### Inferences
- A full, polished, public, maintained RAG chat over all Knesset protocols does not appear to exist yet. knesset.watch comes closest but is access-limited. Every project found is under 12 months old and is a solo effort.
- The projects differ on three axes that matter for comparison: retrieval method (lexical FTS in knesset-lm vs hybrid vector in knessy and knesset.watch), coverage (committee only vs plenary too), and hosting (local vs public).

### Gaps
- Could not open knesset-ai.com, zmanknesset or goinfo (proxy-blocked). Their owners, AI features and coverage are unverified.
- Could not test knesset.watch's /ask feature live.
- No relevant Product Hunt or LinkedIn findings; I did not search them directly within the call budget.

## Hasadna / Open Knesset: AI features, pipelines, Datasette?

### Takeaway
Hasadna runs the main open-data pipelines: knesset-data-pipelines (active, last updated 2026-07) and the open-knesset backend/API. The only AI use I found is the new **knesset-mk-tracking** project (2026-08), which uses Gemini embeddings and summaries over MKs' X posts versus their votes. It does not cover protocols. I found no Hasadna chat or RAG over protocols.

### Cited Findings
- hasadna/knesset-data-pipelines: "Main repository for Open Knesset project – contains the knesset data scrapers and processing pipelines". 20 stars, 28 forks, last updated 2026-07-07. hasadna/knesset-data (API docs) was last updated 2026-06-19. hasadna/open-knesset-backend was last updated 2025-11-03. — [GitHub API search, org:hasadna](https://github.com/hasadna/knesset-data-pipelines)
- hasadna/knesset-mk-tracking compares MKs' social-media statements with their plenum votes. It uses Gemini embeddings, k-means clustering and LLM-written cluster summaries over X posts, with a FastAPI, React and PostgreSQL stack. It is early-stage and mid-migration from BigQuery. Created 2026-08-07. — [GitHub](https://github.com/hasadna/knesset-mk-tracking)
- Open Knesset (oknesset.org) provides committee protocols as source files, text files and per-speaker split files (search snippet; site blocked). — [oknesset.org](https://oknesset.org/)

### Inferences
- Hasadna's per-speaker protocol text files and pipelines are the de facto ingestion source that knesset-lm and others build on.

### Gaps
- Could not open oknesset.org to confirm whether the Datasette/Metabase instance still exists, or whether there are any AI features in the 2026 site.

## Academic: HaifaCLGroup KnessetCorpus, ivrit.ai, Dicta, Open University

### Takeaway
The academic work is corpora and models, not chat or search demos. The Knesset Corpus (Haifa / Open University) is the key annotated text dataset. Its old Kibana search interface no longer works, and a Sketch Engine (concordance) migration is in progress. Knesset-DictaBERT is a fine-tuned encoder.

### Cited Findings
- KnessetCorpus on Hugging Face: annotated plenary and committee protocols from 1992 to 2024, with POS, morphology, dependency and NER annotations. The dataset viewer is disabled; access is through `datasets` with streaming. — [HF dataset (search snippet)](https://huggingface.co/datasets/HaifaCLGroup/KnessetCorpus)
- The Open University project page says the original Kibana-based interface no longer works, the HF release needs programming skills, and the committee subset is being migrated to Sketch Engine. — [OpenU DHSS hub](https://www.openu.ac.il/en/dhsshub/projects/pages/the_knesset_corpus_projec.aspx)
- Knesset-DictaBERT (Goldin & Wintner, arXiv 2407.20581, July 2024) is fine-tuned from dicta-il/dictabert. The corpus has over 32M sentences and over 384M tokens. — [arXiv](https://arxiv.org/abs/2407.20581v1)
- ParlaMint-IL (CLARIN.SI): all plenary and committee protocols from 1994 to 2024, more than 12M speeches and over 400M words, the largest corpus in ParlaMint. The canonical citation is Goldin, Wintner & Rabinovich, *Language Resources and Evaluation* (2025). A NoSketch Engine search is available. — [CLARIN.SI](https://www.clarin.si/repository/xmlui/handle/11356/2032?show=full)
- Follow-up: a factuality and check-worthiness annotation scheme for parliamentary proceedings (arXiv 2509.26406). Knesset-DictaBERT was the best model tested. — [arXiv](https://arxiv.org/pdf/2509.26406)
- IsraParlTweet (arXiv 2405.20269): Knesset plenary records parsed from DOC/DOCX from the 13th Knesset (1992) on, because earlier files are OCR scans with too many errors. — [arXiv](https://arxiv.org/pdf/2405.20269)

### Inferences
- ParlaMint-IL's NoSketch Engine is the only public "search the whole corpus" interface from academia, and it is concordance search, not semantic search.

### Gaps
- ivrit.ai: could not open huggingface.co/datasets/ivrit-ai/knesset-plenums (blocked). Its contents (audio plus transcripts of plenums, intended for ASR) and license are unverified. ivrit.ai's GitHub shows ASR and alignment work (for example ivrit-ai/eval-forced-alignment, updated 2026-10) but no protocol chat.
- The KnessetCorpus license was not confirmed in this session.

## Knesset's own initiatives (AI search, summarization, transcription)

### Takeaway
In January 2026 the Knesset launched an internal AI system for MKs, built by its IT division on AWS. Its centerpiece is the "דבר-עם" speech generator, based on the Knesset speech archive since 2003. I found no evidence of a public AI search or summarization tool over protocols on knesset.gov.il. One search summary claims a Knesset tender describes an AI transcription and search system for plenary protocols that will be extended to committees, but I could not verify this.

### Cited Findings
- Geektime: "הכנסת השיקה כלי חדש שיכתוב לח"כים נאומים בעזרת AI". Other reports: Israel Hayom ("פרלמנט חכם: הכנסת משיקה מערכת AI – עם מחולל נאומים לח"כ"), Mako and pc.co.il. According to the search summary: launched around 13.01.2026, developed by the Knesset Information & Technology Division on AWS, the generator "דבר-עם" draws on the Knesset speech archive from 2003 plus web data, it is available to MKs, parliamentary advisers and staff, and it was developed under cyber-unit oversight. SNIPPET-ONLY, since the article pages were blocked. — [Geektime](https://www.geektime.co.il/israeli-knesset-launches-ai-tool/); [Israel Hayom](https://www.israelhayom.co.il/news/politics/article/19663597); [Mako](https://www.mako.co.il/nexter-news/Article-5faf7b5e157bb91027.htm); [pc.co.il](https://www.pc.co.il/news/%D7%91%D7%99%D7%A0%D7%94-%D7%9E%D7%9C%D7%90%D7%9B%D7%95%D7%AA%D7%99%D7%AA/444277/)
- Knesset outsourcing IT tender 02/2025: the E-Parliament system manages creation of plenary and committee protocols and feeds "דברי הכנסת". The tender names the "סנהדרין" and "המליאה" projects and mentions video-synced protocols. One search summary also claimed the tender describes a transcription-and-search system running on plenary protocols with planned extension to committees. UNVERIFIED, because the PDF was blocked. — [comp2.pdf](https://main.knesset.gov.il/About/KnessetWork/Documents/comp2.pdf); [comp3.pdf](https://main.knesset.gov.il/About/KnessetWork/Documents/comp3.pdf)
- The Knesset Research and Information Center (ממ"מ) has published reports on AI implementation and on generative AI regulation. These are policy papers, not tools. — [MMM AI implementation PDF](https://fs.knesset.gov.il/globaldocs/MMM/85c6ceb0-f648-ef11-815f-005056aac6c3/2_85c6ceb0-f648-ef11-815f-005056aac6c3_11_20852.pdf)

### Inferences
- The Knesset's own AI system is internal and focused on speeches. If it does include protocol RAG, that is not public. The external public still has no official AI search.

### Gaps
- Need to open the tender PDFs and the launch articles directly to confirm whether the internal system includes protocol search or summarization, and whether ASR is used for protocols.

## MCP servers

### Takeaway
Of the Knesset MCP servers I found, only knessy's MCP exposes protocol text search (`search_protocols`). zohar/knesset-mcp and matanmill304/knesset-mcp cover OData metadata only. matanmill304's returns protocol file links but does not extract their text. il-eli-mcp covers legislation, not protocols.

### Cited Findings
- zohar/knesset-mcp (Node.js, `https://knesset.gov.il/Odata/ParliamentInfo.svc`) exposes 9 tools for bills, committees, factions and MKs. It has no protocol or session-document tools. 3 stars, created 2025-04-13, last updated 2026-09-30. — [GitHub](https://github.com/zohar/knesset-mcp)
- matanmill304/knesset-mcp (Python, OData v4, streamable HTTP /mcp) offers `find_person`, `search_bills`, `get_vote`, `get_session` and a generic `query`. `get_session` lists agenda items, documents and protocol links (.pdf/.doc), but the README says document contents are not yet extracted. Created 2026-09-23. — [GitHub](https://github.com/matanmill304/knesset-mcp)
- matematicsolutions/il-eli-mcp provides Israeli legislation via Knesset OData plus 10,558 court judgments. It returns law PDF links and does not cover protocols. Apache-2.0, updated 2026-10-06. — [GitHub](https://github.com/matematicsolutions/il-eli-mcp)
- The knessy MCP exposes `search_protocols` over its OpenSearch index. — [GitHub](https://github.com/amnir/knessy)

### Gaps
- No separate "zohar-knesset-mcp" was found beyond zohar/knesset-mcp. I did not check the listings on mcp.so or lobehub because those sites are blocked or were not checked.

## Other civic-tech, hackathon and Kaggle work

### Takeaway
There are many non-AI or analysis-only projects. I found no AI protocol tool from "שקוף" or "המשמר החברתי".

### Cited Findings
- Alexeyisme/howKnessetVotes: a roll-call database with a web UI and REST API (FastAPI, Next.js, PostgreSQL), created 2026-10-09. Not AI. — [GitHub API search](https://github.com/Alexeyisme/howKnessetVotes)
- JacobWeinbren/Jev-Knesset, "Jev AI Model Analysis on Knesset" (2026-09). Its scope is unclear. — [GitHub](https://github.com/JacobWeinbren/Jev-Knesset)
- Protocol scrapers and downloaders: amit-shkolnik/knesset_odata ("Download Knesset protocols", updated 2025-09); amit-shkolnik/Knesset-dataset; GuyBarel/open-knesset-scraping (2023); ido90/KnessetClassifier (a topic classifier for committee protocols, 2019); university NLP coursework building corpora from protocols (AhmadEgbaria1, eissawahesh). — [GitHub search "knesset protocols"](https://github.com/amit-shkolnik/knesset_odata)
- The searches for "המשמר החברתי" and "שקוף" combined with AI or protocols returned nothing relevant. — [search, 2026-10-14](https://www.google.com/search?q=%D7%94%D7%9E%D7%A9%D7%9E%D7%A8+%D7%94%D7%97%D7%91%D7%A8%D7%AA%D7%99+%D7%91%D7%99%D7%A0%D7%94+%D7%9E%D7%9C%D7%90%D7%9B%D7%95%D7%AA%D7%99%D7%AA+%D7%A4%D7%A8%D7%95%D7%98%D7%95%D7%A7%D7%95%D7%9C%D7%99%D7%9D)

### Gaps
- I did not check Kaggle notebooks.

## Datasets enabling the work

### Takeaway
The core sources are: official OData (metadata plus file links to protocol DOC/PDF on fs.knesset.gov.il); Hasadna pipelines (parsed text and per-speaker splits); the Knesset Corpus / ParlaMint-IL (1992/4–2024, annotated); ZeAlenu/knesset-data (an HF mirror of OData); and ivrit-ai plenums (audio, unverified).

### Cited Findings
- ZeAlenu/knesset-data (HF) mirrors the Knesset OData API: 44 tables, about 1.5M records, CC-BY-SA-4.0. It includes `KNS_DocumentCommitteeSession` with about 196,085 records of committee documents. `FilePath` values in document tables point to fs.knesset.gov.il files, for example .docx files. SNIPPET-ONLY. — [HF README](https://huggingface.co/datasets/ZeAlenu/knesset-data/blob/main/README.md)
- OData therefore exposes document metadata and file URLs, not inline protocol text. Text must be downloaded and parsed from DOC, DOCX or PDF. This is consistent with matanmill304's note that contents are "not yet extracted". — [GitHub](https://github.com/matanmill304/knesset-mcp)
- Knesset Corpus and ParlaMint-IL: see the academic section above. — [CLARIN.SI](https://www.clarin.si/repository/xmlui/handle/11356/2032?show=full)
- The knessy prebuilt OpenSearch snapshot (with embeddings) is on HF. It is a reusable vector index of committee protocols. — [GitHub](https://github.com/amnir/knessy)

### Gaps
- Not verified this session: KnessetCorpus license, ivrit-ai/knesset-plenums contents and license, and the exact OData entity for plenum protocol files.
