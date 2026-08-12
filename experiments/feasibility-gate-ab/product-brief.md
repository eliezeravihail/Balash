# Product request (from the user)

I want a personal bridge between WhatsApp and ChatGPT. Build it as a single service on a Google Cloud
VM, serving just me plus one other "key" number — both read from a private allow-list, both with full
access.

How it should work:
- First-time setup: I log into WhatsApp and into ChatGPT through a small local settings page reached over
  an SSH tunnel. After that the service runs headless and stays up on its own.
- Each of the two numbers has its own *active conversation*, but the ChatGPT account, the conversation
  list, and search are shared between them.
- A normal text message goes to the sender's active conversation, and the reply comes back to that sender.
- `/conversations` and `/searchconversation <name>` return numbered lists; sending a number after a list
  picks a conversation for that sender only; `/newconversation` creates and selects a fresh one.
- Both numbers may select the *same* conversation; requests to one conversation run in order of arrival,
  and each reply still returns to the right sender.
- State persists on the same machine. After a login expires the service asks me to log in again, tries to
  restore each number's active conversation, and only starts a fresh one when restore isn't possible.

Stack notes:
- Node.js LTS, TypeScript strict.
- For WhatsApp the current candidate library is Baileys.
- For ChatGPT I intend to drive the ChatGPT web app (there is no official API in scope).

Out of scope for now: media, multi-tenant, cross-machine failover, the official OpenAI API, the WhatsApp
Business API.
