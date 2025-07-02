# 📊 Tax Alert Chatbot (MCP-Powered)

An interactive **Streamlit-based chatbot** that connects to a custom **MCP (Multi-Component Protocol)** server. It allows users to **query**, **insert**, **update**, and **delete** tax alerts stored in a local SQLite database. The app uses **LangGraph’s REACT agent framework** with **Google Gemini models** and supports both **SSE** and **STDIO** transport modes.

---

## 📁 Project Structure

.
├── client/ # Frontend Streamlit Chat UI
│ └── main.py # Main Streamlit app
├── server/ # Backend FastMCP SQLite server
│ └── server.py # MCP tool & prompt definitions
├── dummy_tax_alerts.db # SQLite database (if present)
├── .env # Environment variables
└── README.md # Documentation

---
## 🚀 Features

- 🤖 Conversational interface with Google Gemini 1.5 models
- 🧠 REACT-style reasoning agent via LangGraph
- 🛠️ Tool execution via MCP server
- 📄 Query, insert, update, and delete operations on tax alert data
- 🔄 Real-time responses using SSE or STDIO

---

## 🛠️ Tech Stack

| Layer        | Tools / Frameworks                                 |
|--------------|-----------------------------------------------------|
| Frontend     | Streamlit, LangGraph, LangChain                     |
| Backend      | FastMCP, SQLite                                     |
| LLM Provider | Google Gemini 1.5 Flash / Pro (via LangChain)       |
| Transport    | SSE (Server-Sent Events) or STDIO                   |
| Runtime      | Python 3.10+, venv, python-dotenv                   |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/tax-alert-chatbot.git
cd tax-alert-chatbot
2. Create and Activate Virtual Environment

python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
(Optional: Split into client/requirements.txt and server/requirements.txt if needed.)

4. Configure Environment Variables
Create a .env file in the root folder:

GOOGLE_API_KEY=your_google_api_key
ALERTS_DB=dummy_tax_alerts.db
🗃️ SQLite Schema
CREATE TABLE tax_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    date TEXT,
    jurisdiction TEXT,
    topics TEXT,
    summary TEXT,
    full_text TEXT,
    source_url TEXT,
    tags TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
🔧 MCP Server Tools
Tool Name	Description
query(sql)	Run SELECT queries on tax_alerts table
insert(...)	Insert a new alert
update(...)	Update existing alerts based on a condition
delete(...)	Delete rows using WHERE conditions
schema_info()	Return schema info of the table

▶️ Running the Server
cd server
python server.py --transport sse
# or
python server.py --transport stdio
Make sure your .env contains a valid path to dummy_tax_alerts.db.

💬 Running the Client (Chat UI)
cd client
streamlit run main.py
Then open http://localhost:8501 in your browser.

⚙️ Configuration (via Sidebar)
Gemini Model: Choose between gemini-1.5-flash or gemini-1.5-pro

Server Mode: Only single server supported

Server Type: SSE or STDIO

Server URL: Required only for SSE mode

Clear Chat / Show Tool Executions: Debug & reset tools

🧪 Sample Interaction
User Input:
"Show me tax alerts from 2024 in California"

Agent Response (Tool Call):

SELECT * FROM tax_alerts WHERE jurisdiction='California' AND date LIKE '2024%'
Returned Result:
Displayed in the chat UI or "No results found" if empty

🧼 Debugging & Notes
MCP server must be running before starting the client.

Full traceback is shown in the client if errors occur.

Ensure correct database path in .env.


