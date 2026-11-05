import json, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
MODEL = "gemini-3.8-flash"

# --- Mock data ---
DEVICES = {
    "TC52-001": {"model": "TC52", "battery_health_pct": 58, "os": "Android 11", "days_since_sync": 9},
    "TC501-002": {"model": "TC501", "battery_health_pct": 68, "os": "Android 11", "days_since_sync": 10},
    "TC701-003": {"model": "TC701", "battery_health_pct": 55, "os": "Android 11", "days_since_sync": 8},
    "TC78-004": {"model": "TC78", "battery_health_pct": 59, "os": "Android 11", "days_since_sync": 6},
    "ZT411-007": {"model": "ZT411 printer", "printhead_km": 48, "last_error": "RIBBON OUT"},
}
KNOWLEDGE_BASE = {
    "battery": "Battery health below 70% causes short runtime. Replace battery; enable battery swap mode.",
    "sync": "Devices not synced for 7+ days may miss OS/security updates. Check MDM enrollment and Wi-Fi.",
    "ribbon": "RIBBON OUT: reload ribbon, confirm ribbon side (ink in/out) matches printer settings.",
    "scanner": "Frequent scan failures: 1. Clean the scanner exit window with a soft lint-free cloth. "
               "2. Check the barcode is not damaged or poorly printed. 3. Hold the device 10-30 cm from the barcode. "
               "4. If failures continue, escalate to IT for a scanner configuration check.",
    "calibration": "Labels misaligned or PAPER OUT shown with labels loaded: 1. Open the printer and confirm the labels "
                   "sit under the media guides. 2. Close the printer and run media calibration (hold the FEED button "
                   "until the light flashes). 3. Print a test label.",
    "wifi": "Frequent Wi-Fi disconnects: 1. Check whether disconnects happen in one store area (possible coverage gap). "
            "2. Restart Wi-Fi on the device. 3. If disconnects continue across the store, escalate to IT to check "
            "access points and roaming settings.",
}

# --- Tools (OpenAI format) ---
TOOLS = [
    {"type": "function", "function": {
        "name": "get_device_status",
        "description": "Get health and status data for a device by its ID.",
        "parameters": {"type": "object",
                       "properties": {"device_id": {"type": "string"}},
                       "required": ["device_id"]}}},
    {"type": "function", "function": {
        "name": "search_knowledge_base",
        "description": "Search troubleshooting articles by keyword, e.g. 'battery', 'sync', 'ribbon'.",
        "parameters": {"type": "object",
                       "properties": {"keyword": {"type": "string"}},
                       "required": ["keyword"]}}},
]

def run_tool(name, args):
    if name == "get_device_status":
        return DEVICES.get(args["device_id"], {"error": "Device not found"})
    if name == "search_knowledge_base":
        hits = {k: v for k, v in KNOWLEDGE_BASE.items() if args["keyword"].lower() in k}
        return hits or {"result": "No article found"}
    return {"error": "Unknown tool"}

SYSTEM = (
    "You are Device Doctor, a support agent for frontline workers using rugged "
    "mobile computers and printers.\n"
    "Rules:\n"
    "1. Always check device data before diagnosing.\n"
    "2. Review EVERY field in the device data and report all problems, not just the first.\n"
    "3. Search the knowledge base for each problem you find.\n"
    "4. Only give steps that come from the knowledge base. If the knowledge base "
    "doesn't cover something, say 'Contact your IT support team' instead of guessing.\n"
    "5. Give short, numbered steps a store associate can follow."
)

def ask(question):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    while True:  # the agent loop
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            print(f"  🔧 {call.function.name}({args})")
            output = run_tool(call.function.name, args)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(output)})

if __name__ == "__main__":
    while True:
        q = input("\nYou: ")
        if q.lower() in ("quit", "exit"):
            break
        print("\nDevice Doctor:", ask(q))