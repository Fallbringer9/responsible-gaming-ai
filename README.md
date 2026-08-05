# Responsible Gaming AI

AI-powered Responsible Gaming analysis platform built with Python, AWS and Large Language Models.

## Overview

After 12 years working in the casino industry, I decided to transition into AI and backend development.

This project combines my industry experience with modern AI engineering to build a Responsible Gaming platform capable of detecting player risk indicators through deterministic business rules, enriching the analysis with Retrieval-Augmented Generation (RAG), and producing structured risk assessments and recommendations with a Large Language Model while keeping a human operator in the decision loop.

The project is designed as a portfolio application showcasing modern AI engineering practices, clean architecture, and cloud-native development.

---

## High-Level Architecture

```text
                        Player Activity
                               │
                               ▼
                 PlayerActivitySnapshot
                               │
                               ▼
               Deterministic Signal Detection
                               │
                               ▼
                    RiskAnalysisResult
                               │
                               ▼
                   Knowledge Base (RAG)
                               │
                               ▼
                     LLM Risk Assessment
                               │
                               ▼
               Structured Recommendations
                               │
                               ▼
                       Human Review
```

---

## Tech Stack

- Python 3.13
- uv
- Ruff
- Pytest
- Amazon Bedrock *(planned)*
- LangGraph *(planned)*
- AWS *(planned)*

---

## Current Status

- ✅ Project foundation
- ✅ Domain model
- ✅ Deterministic signal detection engine
- ✅ Unit tests
- 🚧 RAG pipeline
- 🚧 LLM risk assessment
- 🚧 AWS infrastructure

---

## Project Goals

- Build a clean Domain-Driven Design architecture.
- Detect Responsible Gaming signals using deterministic business rules.
- Enrich the analysis with domain knowledge through RAG.
- Generate structured risk assessments using an LLM.
- Produce explainable recommendations for Responsible Gaming operators.
- Keep the human expert responsible for the final decision.

---

## License

MIT
