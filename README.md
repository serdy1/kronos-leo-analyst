# Kronos LEO Analyst - Combo Skill

**Kronos Foundation Model** (financial K-line forecasting) + **AI Hedge Fund** (multi-agent trading system) = Unified analysis API.

## Architecture

```
kronos-leo-analyst/
├── src/
│   ├── main.py              # FastAPI server (entry point)
│   ├── engine.py            # Integration engine (Kronos + Hedge Fund)
│   ├── kronos/              # Kronos foundation model (from shiyu-coder/Kronos)
│   │   ├── kronos_model.py      # Kronos, KronosTokenizer, KronosPredictor
│   │   └── module.py            # Transformer modules, BSQuantizer, etc.
│   └── hedge_fund/          # AI Hedge Fund agents (from virattt/ai-hedge-fund)
│       ├── agents/              # 18 investment persona agents
│       ├── backtesting/         # Backtesting engine
│       ├── graph/               # LangGraph workflow state
│       ├── tools/api.py         # Financial data API client
│       ├── utils/               # Display, LLM, progress, etc.
│       ├── llm/                 # LLM model configurations
│       └── main.py              # Hedge fund workflow entry
├── requirements.txt
├── Dockerfile
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check & status |
| GET | `/agents` | List available hedge fund agents |
| GET | `/models` | List available LLM models |
| POST | `/analyze` | Full combo analysis (Kronos forecast + agent signals) |
| POST | `/hedge-fund` | Run full hedge fund workflow |
| POST | `/kronos-forecast` | Kronos-only forecast |

### Example: `/analyze`

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA", "days_back": 365, "forecast_horizon": 30}'
```

### Example: `/hedge-fund`

```bash
curl -X POST http://localhost:8000/hedge-fund \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"], "selected_analysts": ["warren_buffett", "michael_burry"]}'
```

## Source Repos

- [shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos) - Foundation model for financial K-line data
- [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) - Multi-agent AI hedge fund

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Server port (default: 8000) |
| `HF_TOKEN` | Hugging Face token for Kronos model download |
| `KRONOS_MODEL` | Kronos model name (default: `NeoQuasar/Kronos-small`) |
| `KRONOS_TOKENIZER` | Kronos tokenizer name (default: `NeoQuasar/Kronos-Tokenizer-base`) |
| `OPENAI_API_KEY` | OpenAI API key for hedge fund agents |
| `FINANCIAL_DATASETS_API_KEY` | API key for financial data |
| `LLM_MODEL` | LLM model for agents (default: `gpt-4o-mini`) |
| `LLM_PROVIDER` | LLM provider (default: `OpenAI`) |

## Deployment

```bash
docker build -t kronos-leo .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key kronos-leo
```

## License

MIT
