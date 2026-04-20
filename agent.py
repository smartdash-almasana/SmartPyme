from google.adk.agents import Agent

root_agent = Agent(
    name="smartpyme_root",
    model="gemini-3.1-flash-lite-preview",
    instruction="Eres el agente raíz de SmartPyme. Responde en español."
)
