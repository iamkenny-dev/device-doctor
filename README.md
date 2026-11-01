🩺 Device Doctor

An AI agent that troubleshoots rugged mobile computers and printers for frontline workers.

A store associate describes a problem in plain language. Device Doctor looks up the device's health data, searches a troubleshooting knowledge base, and returns short, numbered steps anyone on the shop floor can follow.

Week 1 of a 12-week series building frontline AI agents: device support, knowledge, sales assistance, merchandising and multi-agent orchestration.

The problem

Frontline workers in retail, warehouses and logistics depend on handheld computers and label printers. When a device fails mid-shift, they usually wait for IT, lose productivity, or apply the wrong fix. Most issues (worn batteries, missed syncs, printer ribbon errors) have known fixes buried in manuals nobody reads.

What the agent does
You: Device TC52-001 dies before lunch every day, what should I do?

🔧 get_device_status({'device_id': 'TC52-001'})
🔧 search_knowledge_base({'keyword': 'battery'})

Device Doctor: Your device's battery health is at 58% (below the 70% threshold)
and needs replacing...

The agent decides on its own which tools to call and in what order. Nobody scripted "check the device, then search for battery". The model reasons its way there from the data.

How it works
needs data
has enough info
Worker question
LLM
Tool call
get_device_status
search_knowledge_base
Step-by-step answer

This is the agent loop:

Send the question, plus descriptions of the available tools, to the LLM.
If the LLM requests a tool, run it and send the result back.
Repeat until the LLM returns a final answer.
Tool Purpose
get_device_status Returns battery health, OS version, days since last sync and error codes for a device ID
search_knowledge_base Finds troubleshooting articles by keyword
What I learned: reducing hallucination

The first version gave confident answers that included steps not in the knowledge base (specific button menus and LED colours from the model's general training). It also reported only the first problem it found and ignored a device that hadn't synced in 9 days.

I fixed both with explicit rules in the system prompt:

Review every field in the device data and report all problems.
Only give steps that come from the knowledge base. Otherwise, escalate to IT.

Before: 1 issue found, several invented steps. After: <!-- paste your improved result here -->

In frontline settings, an agent that confidently gives wrong instructions is worse than no agent. Grounding answers in approved content is the difference between a demo and a deployable product.

Run it yourself

Requires Python 3.11+ and a free Google AI Studio API key.

bash
git clone https://github.com/iamkenny-dev/device-doctor.git
cd device-doctor
python -m venv venv
venv\Scripts\activate # Mac/Linux: source venv/bin/activate
pip install openai python-dotenv

Create a .env file (see .env.example):

GEMINI_API_KEY=your-key-here

Run:

bash
python agent.py

The code uses the OpenAI-compatible API format, so it also runs on Groq, OpenRouter or other providers by changing the base_url, key and model name.

Roadmap
Agent loop with tool calling
Prompt rules to reduce hallucination
create_service_ticket tool to escalate unresolved issues
Replace mock data with a real knowledge base (RAG) — Week 2
Web UI and voice input
Notes

All device data and knowledge base articles are mock data created for learning. This is a personal learning project and not an official product of any company.

Built by Kehinde Adelakun, Sales Engineer · https://www.linkedin.com/in/adelakunkehinde/
