# AI Revenue Audit RAG Prototype - Agent Instructions

## Project Overview
This is a Python Streamlit application for AI-assisted casino eCash reconciliation using Retrieval-Augmented Generation (RAG) with OpenAI. The app compares SDS Slot System data against CMP data, detects variances, and provides AI audit recommendations grounded in SOP guidance.

## Tech Stack
- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **AI**: OpenAI API (GPT models)
- **Environment**: python-dotenv

## Development Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
streamlit run app.py
```

## Architecture Decisions
- **Deterministic Calculations**: All financial reconciliations use pure Python/Pandas logic. AI never performs calculations.
- **SDS as Source of Truth**: All adjustments must validate against SDS values.
- **Human-in-the-Loop**: AI provides recommendations, but humans must approve all adjustments.
- **RAG Workflow**: AI recommendations are grounded in [knowledge_base/ecash_audit_sop.txt](knowledge_base/ecash_audit_sop.txt).

## Key Conventions
- CSV files must have columns: `slot_location`, `gamingdt`, `ecash_in`, `ecash_out`
- Reconciliation uses outer merge on `slot_location` + `gamingdt`
- Variance columns: `ecash_in_variance`, `ecash_out_variance`
- All financial values are floats; handle precision carefully

## Common Pitfalls
- **OpenAI API**: Use `client.chat.completions.create()` with `messages=[{"role": "user", "content": prompt}]`, not `client.responses.create()`
- **Model Names**: Use valid models like "gpt-4" or "gpt-3.5-turbo", not "gpt-4.1-mini"
- **Environment Variables**: Always check for `OPENAI_API_KEY`; missing key causes silent failures
- **File Paths**: Use relative paths from app.py location for data/SOP files
- **Streamlit Reruns**: Code executes on every interaction; optimize for performance

## Key Files
- [app.py](app.py): Main Streamlit application
- [requirements.txt](requirements.txt): Dependencies
- [README.md](README.md): Business and technical documentation
- [knowledge_base/ecash_audit_sop.txt](knowledge_base/ecash_audit_sop.txt): SOP rules for RAG
- [data/](data/): Sample CSV files for testing

## Testing
- Use sample CSVs in [data/](data/) for development
- Test reconciliation logic with known variance scenarios
- Verify AI recommendations reference SOP rules correctly
- Check adjustment validation against SDS values

## Code Style
- Follow Python PEP 8 conventions
- Use descriptive variable names for financial data
- Add docstrings to functions, especially reconciliation logic
- Handle exceptions gracefully in API calls</content>
<parameter name="filePath">c:\Users\gowri\OneDrive\Documents\ai-revenue-audit-rag-prototype\AGENTS.md