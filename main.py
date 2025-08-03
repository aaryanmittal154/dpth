import argparse
import asyncio
import os
from dotenv import load_dotenv

from app.agent.deptheon import Deptheon
from app.logger import logger

# Load environment variables from .env file
load_dotenv()


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Deptheon agent with a prompt")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    args = parser.parse_args()

    # Create and initialize Deptheon agent
    agent = await Deptheon.create()
    try:
        # Use command line prompt if provided, otherwise ask for input
        prompt = args.prompt if args.prompt else input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        # Ensure agent resources are cleaned up before exiting
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
