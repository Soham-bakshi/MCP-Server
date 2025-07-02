import os
import sys
import streamlit as st
import datetime
import asyncio
import traceback
import nest_asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient as SSEClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, ToolMessage

# --- Load environment and apply nest_asyncio ---
load_dotenv()
nest_asyncio.apply()
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# --- Initialize async loop ---
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

def run_async(coro):
    return st.session_state.loop.run_until_complete(coro)

# --- Connect to MCP Server ---
async def connect_and_load_tools(client, server_name):
    try:
        async with client.session(server_name) as session:
            tools = await load_mcp_tools(session)
            return session, tools
    except Exception as e:
        traceback.print_exc()
        raise e

def run_agent(agent, user_input):
    return agent.ainvoke({"messages": user_input})

# --- Main Chat Tab ---
def tab_chat():
    for key in ["chat_history", "tool_executions"]:
        if key not in st.session_state:
            st.session_state[key] = []

    chat_container = st.container()
    input_container = st.container()

    with chat_container:
        st.header("💼 Tax Alert Chatbot")

        # Connection Status
        if st.session_state.client is not None:
            st.success("📶 Connected to MCP server(s)")
        else:
            st.warning("⚠️ Not connected to any MCP server")

        # Chat History
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            elif message["role"] == "assistant":
                if message.get("tool"):
                    st.code(message["tool"])
                st.chat_message("assistant").write(message["content"])

    with input_container:
        if user_input := st.chat_input("Type your message here..."):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)

            if st.session_state.agent is None:
                st.error("Please connect to an MCP server first.")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = run_async(run_agent(st.session_state.agent, user_input))
                            tool_output = None
                            output = ""

                            if isinstance(response, dict) and "messages" in response:
                                for msg in response["messages"]:
                                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                        for tool_call in msg.tool_calls:
                                            tool_output = next(
                                                (m.content for m in response["messages"]
                                                 if isinstance(m, ToolMessage) and
                                                 m.tool_call_id == tool_call['id']),
                                                None
                                            )
                                            if tool_output:
                                                st.session_state.tool_executions.append({
                                                    "tool_name": tool_call['name'],
                                                    "input": tool_call['args'],
                                                    "output": tool_output,
                                                    "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                })

                                for msg in response["messages"]:
                                    if isinstance(msg, HumanMessage):
                                        continue
                                    elif hasattr(msg, 'name') and msg.name:
                                        st.code(msg.content)
                                    elif hasattr(msg, "content") and msg.content:
                                        output = str(msg.content)
                                        st.write(output)

                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "tool": tool_output,
                                "content": output
                            })

                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error during response: {e}")
                            st.code(traceback.format_exc(), language="python")

# --- UI Setup ---
st.set_page_config(page_title="Tax Alert Chatbot", page_icon="💼")

# Sidebar Config
st.sidebar.title("Configuration")
selected_model = st.sidebar.selectbox("Gemini Model", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0)
server_mode = st.sidebar.radio("Server Mode", ["Single Server", "Multi Server"], index=0)
server_type = st.sidebar.radio("Server Type", ["SSE (Server-Sent Events)", "STDIO (Standard IO)"], index=0)

# MCP Server URL (only when SSE is selected)
if server_type == "SSE (Server-Sent Events)":
    mcp_server_url = st.sidebar.text_input("MCP Server URL", "http://localhost:8001/sse", key="sse_url")
else:
    mcp_server_url = None

connect_btn = st.sidebar.button("🔌 Connect to MCP Server")

# Session State Defaults
for key in ["connected", "client", "agent", "session", "tools", "chat_history", "tool_executions"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "history" in key or "executions" in key else None

# Connect to MCP Server
if connect_btn:
    try:
        if server_type == "SSE (Server-Sent Events)":
            client = SSEClient({
                "tax_alert": {
                    "url": mcp_server_url,
                    "transport": "sse"
                }
            })
            session_key = "tax_alert"
        else:  # STDIO mode
            client = SSEClient({
                "mcp-server-time": {
                    "command": "uvx",
                    "args": ["mcp-server-time"],
                    "transport": "stdio"
                }
            })
            session_key = "mcp-server-time"

        session, tools = run_async(connect_and_load_tools(client, session_key))
        agent = create_react_agent(ChatGoogleGenerativeAI(
            model=selected_model,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        ), tools)

        st.session_state.connected = True
        st.session_state.client = client
        st.session_state.agent = agent
        st.session_state.session = session
        st.session_state.tools = tools

    except Exception as e:
        st.error(f"❌ Failed to connect: {e}")
        st.code(traceback.format_exc(), language="python")

# Optional Sidebar Tools
if st.session_state.tools:
    st.sidebar.subheader("Available Tools")
    for tool in st.session_state.tools:
        st.sidebar.markdown(f"- `{tool.name}`")

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat_history.clear()
    st.session_state.tool_executions.clear()
    st.rerun()

if st.sidebar.checkbox("Show Tool Executions"):
    st.sidebar.write(st.session_state.tool_executions)

# --- Run Chat ---
tab_chat()

