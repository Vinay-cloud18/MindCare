# Three-Minute Project Introduction

## Why

MindCare is a mental-health journaling application designed to make personal reflection easier to maintain and easier to review. A user can write a dated journal entry, receive a lightweight sentiment signal, and later look for patterns rather than treating each entry as an isolated note. The project is aimed at an individual user who wants a simple journaling workflow with basic emotional feedback and access to crisis resources. It is important to frame it as a reflection aid, not a clinical diagnosis or emergency service.

## What

The application is built around four Streamlit tabs. In New Entry, the user selects a date, writes about their thoughts or feelings, and saves the entry. The application first checks for a small set of crisis phrases. If none are found, it runs a Hugging Face Transformers sentiment pipeline and stores the original text, model label, broad sentiment category, and confidence in SQLite. The History tab lets the user search text, filter by sentiment, and export the entries to PDF. Analytics uses pandas and Plotly to show a sentiment trend, emotion distribution, entry counts, a current streak, and average confidence. Settings provides logout, static Indian mental-health resources, and a self-care suggestion.

## How

The architecture is a small modular monolith. `main.py` initializes the SQLite schema, checks Streamlit session state, loads the model, and composes the tabs. `database.py` owns the SQLite table creation and entry queries. The components own the user-facing workflows, while `utils.py` contains authentication helpers, model loading, sidebar content, and PDF generation. I chose Streamlit and SQLite because they make an early Python data application quick to run and easy to understand. Running sentiment analysis synchronously gives immediate feedback and avoids introducing a queue before it is needed.

The main trade-off is that this simplicity puts a lot on the interactive path. Model inference can delay saving, all history is loaded into memory, and SQLite is not a strong fit for multiple replicas or high write concurrency. The most important technical challenge is also a safety boundary: keyword-based crisis detection is deterministic and easy to explain, but it is not comprehensive or clinically validated. I would describe it honestly as a limited heuristic.

## What Now

The current repository looks like an early MVP or portfolio project, not a production mental-health service. My first production changes would be to hash passwords, restore secure session/XSRF settings, add tests for data isolation and crisis handling, define privacy and deletion rules, and make analysis status explicit. The next architectural step would be to save the entry first and process sentiment through a durable worker if latency or traffic justified it. I would measure save latency, model latency, query time as history grows, model quality on a reviewed dataset, and false crisis detections before choosing more complexity. That gives a clear path from a useful local prototype to a safer, observable system.

## Thirty-Second Version

MindCare is a Streamlit mental-health journaling MVP. Users register, write dated entries, receive a local Transformers sentiment classification, and store the text and derived result in SQLite. They can search and filter history, view Plotly-based mood patterns, export a PDF, and access crisis resources. Streamlit and SQLite were sensible for fast iteration, but the current design is not production-ready: passwords are plaintext, crisis detection is only a small keyword heuristic, settings are not persisted, and model inference is synchronous. My first improvements would be secure authentication, tests, privacy controls, and explicit asynchronous analysis only when measurement shows it is needed.

## Key Points to Remember

- Problem: make personal journaling and pattern review easier.
- Flow: authenticate, write, classify, persist, review, export.
- Architecture: Streamlit modular monolith with SQLite and local Transformers inference.
- Good MVP choice: simple Python stack with an end-to-end vertical slice.
- Main safety boundary: keyword crisis detection is not clinical detection.
- Biggest security issue: plaintext passwords and disabled XSRF in dev setup.
- Biggest scale issue: synchronous model work plus full in-memory history reads.
- Next step: secure, test, observe, and measure before adding distributed components.