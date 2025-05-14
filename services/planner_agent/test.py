import asyncio
from planner_agent import initialize_agent, send_to_agent, shutdown_agent

async def main():
    await initialize_agent()
    user_query = "what is Giskard?"
    response = await send_to_agent(user_query)
    print("Planner Agent Response:")
    print(response)
    await shutdown_agent()

if __name__ == "__main__":
    asyncio.run(main())
