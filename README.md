📊 Tax Alert Chatbot (MCP-Powered)
An interactive Streamlit-based chatbot that connects to a custom MCP (Multi-Component Protocol) server. It allows users to query, insert, update, and delete tax alerts stored in a local SQLite database. The app uses LangGraph’s REACT agent framework with Google Gemini models and supports both SSE and STDIO transport modes.

🗂️ Project Structure
bash
Copy
Edit
.
├── client/                    # Frontend Streamlit Chat UI
│   └── main.py                # Main Streamlit app
├── server/                    # Backend FastMCP SQLite server
│   └── server.py              # MCP tool & prompt definitions
├── dummy_tax_alerts.db        # SQLite database (if present)
├── .env                       # Environment variables
└── README.md                  # Documentation
🚀 Features
🤖 Conversational interface with Google Gemini 1.5 models

🧠 REACT-style reasoning agent via LangGraph

🛠️ Tool execution via MCP server

🧾 Query, insert, update, and delete operations on tax alert data

🔄 Real-time responses using SSE or STDIO

🛠️ Tech Stack
Layer	Tools/Frameworks
Frontend	Streamlit, LangGraph, LangChain
Backend	FastMCP, SQLite
LLM Provider	Google Gemini 1.5 Flash / Pro via LangChain
Transport	SSE (Server-Sent Events) or STDIO
Runtime	Python 3.10+, venv, dotenv

⚙️ Setup Instructions
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-repo/tax-alert-chatbot.git
cd tax-alert-chatbot
2. Create and Activate Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
3. Install Dependencies
Client:

bash
Copy
Edit
pip install -r client/requirements.txt
Server:

bash
Copy
Edit
pip install -r server/requirements.txt
You may combine both in one file if needed.

4. Set Up .env File
Create a .env file in the root directory:

ini
Copy
Edit
GOOGLE_API_KEY=your_google_api_key
ALERTS_DB=dummy_tax_alerts.db
🗃️ SQLite Schema
The server uses a single table tax_alerts:

sql
Copy
Edit
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
🧠 MCP Server Tools
Tool Name	Description
query(sql)	Run SELECT queries on tax_alerts
insert(...)	Insert a new alert
update(set_clause, condition)	Update rows
delete(condition)	Delete rows
schema_info()	Return schema description

▶️ Run the Server
bash
Copy
Edit
cd server
python server.py --transport sse
# or
python server.py --transport stdio
Make sure your .env file includes ALERTS_DB pointing to your SQLite DB file.

💬 Run the Client UI
bash
Copy
Edit
cd client
streamlit run main.py
Then open the browser window (usually http://localhost:8501) to start chatting.

🔧 Configuration Options
Option	Description
Gemini Model	Choose between gemini-1.5-flash or gemini-1.5-pro
Server Mode	Single server supported
Server Type	Choose SSE or STDIO
MCP Server URL	(Only for SSE) URL to the running MCP server

🧪 Example Interactions
User Input:

Show me all tax alerts from 2024 in California.

Agent Tool Execution:

sql
Copy
Edit
SELECT * FROM tax_alerts WHERE jurisdiction='California' AND date LIKE '2024%'
Output:

(Returns matching alerts from the DB)

🧼 Clear & Debug Options
"🧹 Clear Chat": Resets session chat history

"Show Tool Executions": Displays executed tools + timestamps

Full traceback shown on errors

📌 Notes
The MCP server must be running before launching the client.

If using STDIO, no URL is needed.

Make sure the dummy_tax_alerts.db exists or is created before insertion.
