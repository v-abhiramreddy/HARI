# HARI — Inbox Guardian 🛡️

> **AI-powered email threat detection for your Gmail inbox.**

HARI (Heuristic AI Risk Inspector) is a multi-layered email security platform that combines fast rule-based heuristics with Google Gemini AI deep-analysis to detect phishing, scams, and spam in real-time — directly in your browser via a Streamlit dashboard.

---

## ✨ Features

### 🔍 Real-Time Inbox Analysis
- Fetches your last **10 Gmail messages** via OAuth (expandable with **Load More**)
- Progressive loading — inbox appears row-by-row as analysis runs
- Live progress bar showing fetch, scoring, and LLM analysis stages

### ⚡ Heuristic Scoring Engine (`agents/scoring_agent.py`)
Fast, zero-latency local scoring across 4 signal categories:

| Category | Signals Detected |
|---|---|
| **Sender** | Display name/local-part spoofing, domain mismatch, lookalike/typosquatted domains, failed authentication |
| **Links** | Brand impersonation via URL mismatch, URL shorteners, live threat feed lookups (OpenPhish) |
| **Language** | Urgency & threat phrases, credential/payment requests, too-good-to-be-true offers |
| **Attachments** | Suspicious attachment language patterns |

Scoring returns a **0–100 risk score** and classifies each email as: `safe`, `spam`, `scam`, or `phishing`.

### 🤖 Gemini AI Deep Analysis (`agents/llm_analysis_agent.py`)
- **Threshold-based:** Only emails scoring **≥ 60** trigger a Gemini call (saves quota)
- Returns a natural-language explanation of detected threats
- Hardened against **prompt injection** — email body is sandboxed in `<EMAIL_BODY>` XML tags
- **45-second timeout** to handle slow API responses gracefully
- Result caching (`llm_cache.json`) prevents redundant API calls for already-seen emails

### 🔐 Universal Sender Trust & ARC Support
- **Protocol-driven trust** — any sender passing SPF + DKIM + DMARC gets a score reduction, regardless of whether they are a known brand
- **Mailing list forwarding support** — DKIM + ARC pass is recognized as valid forwarding even when SPF soft-fails (e.g., Google Groups, university mailing lists)
- **Institutional TLD heuristics** — `.edu`, `.gov`, `.ac.in`, `.gov.in`, `.nic.in`, etc. receive extra trust credit
- **ARC extraction from multiple headers** — reads `ARC-Authentication-Results` (multi-hop, outermost), with fallback to `ARC-Seal`

### 🧠 Supervised ML Classifier (`ml/`)
- Purely additive third signal alongside the heuristic engine and Gemini LLM.
- **RandomForest Model:** Trained on real SpamAssassin ham/spam archives and the Nazario phishing corpus.
- **Features:** TF-IDF text vectorization combined with 9 structural features (link counts, keyword frequencies, lookalike domains).
- **Zero-Leakage Evaluation:** The dataset is strictly deduplicated before train/test splitting to guarantee honest evaluation metrics.

### 📊 Streamlit Dashboard (`dashboard/app.py`)
- **8 navigation tabs:** Dashboard, Email Analysis, Threat Intel, Link Scanner, Scam Detector, User Reports, Analytics, Settings
- Filtering by risk category and minimum risk score
- Per-email expandable detail view with heuristic signals and Gemini explanation
- **Demo mode** (`?demo=1`) — uses `results-demo.json` sample data, no login required
- **Load More** button to fetch additional emails in batches of 10

### 🔗 Gmail MCP Server (`mcp-server/gmail_mcp_server.py`)
- OAuth 2.0 authentication flow with token refresh
- Extracts full email headers including SPF, DKIM, DMARC, **and ARC** (multi-hop aware)
- Checks `Authentication-Results`, `ARC-Authentication-Results`, and `ARC-Seal` headers
- Uses the outermost/final hop for accurate authentication assessment
- Rate-limited Gmail API access with retry logic

### 🛡️ Security Hardening
- All secrets loaded from **environment variables only** — no hardcoded keys anywhere
- Structured `logging` throughout — no `print()` statements or raw tracebacks exposed to users
- OAuth token exchange happens server-side; tokens never exposed to the UI or logs
- Atomic cache writes to prevent partial/corrupt JSON files
- HTTPS-only production URLs enforced

### 🧪 Testing
- **17 unit tests** across `scoring_agent.py` and `email_utils.py`
- **11 regression tests** with fictional domains to verify universal trust logic
- False-positive coverage: institutional (.ac.in, .gov.in, .edu), small orgs, mailing lists
- True-positive coverage: phishing, lottery scams, BEC, fake HR recruitment emails

---

## 🗂️ Project Structure

```
HARI/
├── agents/
│   ├── scoring_agent.py        # Fast heuristic scoring engine (0-100 score)
│   ├── llm_analysis_agent.py   # Gemini AI deep analysis (threshold >= 60)
│   ├── connector_agent.py      # Gmail API connector
│   ├── email_utils.py          # Email parsing utilities (ARC, SPF, DKIM, DMARC)
│   └── audit_log.py            # Structured audit logging
├── mcp-server/
│   ├── gmail_mcp_server.py     # Gmail MCP tool server (multi-hop ARC aware)
│   └── gmail_auth.py           # OAuth 2.0 flow and token management
├── ml/
│   ├── collect_data.py         # Downloads/parses Nazario & SpamAssassin datasets
│   ├── feature_engineering.py  # Builds TF-IDF & structural features (zero-leakage)
│   ├── train_model.py          # Trains the RandomForest classifier
│   └── evaluate.py             # Generates the evaluation report & hard-case tests
├── dashboard/
│   └── app.py                  # Streamlit web dashboard
├── utils/
│   └── cache_utils.py          # Atomic JSON read/write and cache key generation
├── tests/
│   └── run_local_tests.py      # Zero-dependency unit + regression test runner
├── results-demo.json           # Sample data for demo mode
├── requirements.txt
└── Dockerfile
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- A Google Cloud project with Gmail API enabled
- `GEMINI_API_KEY` environment variable set

### Installation

```bash
git clone https://github.com/v-abhiramreddy/HARI.git
cd HARI
pip install -r requirements.txt
```

### Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 client secret |
| `SUPABASE_URL` | (Optional) Supabase project URL for user reports |
| `SUPABASE_KEY` | (Optional) Supabase anon key |

### Run Locally

```bash
# Start the Streamlit dashboard
streamlit run dashboard/app.py

# Run all unit tests
python tests/run_local_tests.py

# Run the heuristic scoring regression tests
python -m agents.scoring_agent
```

### Demo Mode

Visit `http://localhost:8501?demo=1` to explore the dashboard with sample data — no Google login required.

---

## 🐳 Docker / Cloud Run Deployment

```bash
# Build and tag the image
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/capstone-repo/hari-dashboard

# Deploy to Cloud Run
gcloud run deploy hari-dashboard \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/capstone-repo/hari-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=...,GOOGLE_CLIENT_ID=...,GOOGLE_CLIENT_SECRET=...
```

---

## ⚙️ Configuration Reference

| Setting | Default | Description |
|---|---|---|
| LLM Threshold | `60` | Minimum heuristic score to trigger Gemini deep analysis |
| Initial email batch | `10` | Emails fetched on first load |
| Load More increment | `+10` | Additional emails fetched per "Load More" click |
| Gemini timeout | `45s` | Max wait time for Gemini API responses |
| OpenPhish TTL | `6h` | Threat feed cache expiry |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
