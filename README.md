# Auto-Agent: Dynamic AI Agent Creator

Auto-Agent is a powerful meta-agent system designed to build, test, and deploy specialized AI "Worker Agents" from natural language instructions.

## 🚀 How it Works

The system operates in two distinct layers:

### 1. The Builder Agent (Meta-Layer)
The **Builder Agent** is the architect. When you give it a request (e.g., "Monitor AI job postings and email me summaries"), it:
- **Plans**: Uses Gemini to analyze existing tools and identify what's missing.
- **Builds**: Generates Python code for new tools if needed.
- **Tests**: Runs new tools in a sandbox to ensure they work.
- **Registers**: Adds verified tools to the system registry.
- **Deploys**: Generates a standalone Worker Agent script, saves it to the database, and launches it.

### 2. Worker Agents (Execution Layer)
**Worker Agents** are autonomous task runners built by the Builder. They:
- Run on a schedule (e.g., every 24 hours) or as one-shot tasks.
- Use a unified tool registry to perform web searches, scrapers, emails, and custom tasks.
- Log every run, result, and error to MongoDB for full observability.

## 🧠 LLM Usage & Routing

Auto-Agent uses a sophisticated **LLM Router** to balance performance, cost (mostly free models), and accuracy:

| Task Type | Primary Model | Why? |
|-----------|---------------|------|
| **Planning & Tools** | `gemini-2.0-flash` | Superior at following JSON schemas and structured planning. |
| **Code Writing** | `deepseek-reasoner` | Best-in-class reasoning for bug-free tool generation. |
| **Agent Execution** | `Llama-3.3-70B` | Robust, multi-tool support via the Hugging Face Router. |

**Hugging Face Router**: We use the Hugging Face OpenAI-compatible endpoint (`https://router.huggingface.co/v1`) to access state-of-the-art open models with a single API key (`HF_TOKEN`).

## 🛠️ Built-in Tools
- **Web Search**: DuckDuckGo integration.
- **Web Scraper**: Clean text extraction from URLs.
- **Email**: Full SMTP/IMAP support (Send/Read).
- **FileSystem**: Secure read/write access.
- **HTTP**: Generic API interaction.

## 📂 Project Structure
- `main.py`: Entry point for the system.
- `builder/`: Logic for the Builder Agent and its MCP servers.
- `generated_agents/`: Where your custom agents live.
- `tools_dir/`: The shared tool registry and implementation files.
- `llm/`: The unified LLM routing layer.
- `db/`: MongoDB connection and collection management.

## ⚙️ Setup
1. Clone the repo and create a `venv`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure your `.env` with `HF_TOKEN`, `MONGO_URI`, and email credentials.
4. Run: `python main.py`
