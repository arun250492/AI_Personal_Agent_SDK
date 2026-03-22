#!/usr/bin/env python3
"""
Example usage of the AI Personal Agent SDK
"""

import os
import sys

# Add the parent directory to the Python path so we can import the local package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_personal_agent_sdk import PersonalAgent, Config, AgentConfig


def main():
    """Main example function"""

    # Load configuration from environment variables
    # You can also create a .env file with these values
    config = Config()

    # If config is not set, you can set it programmatically
    if not config.openai_api_key:
        print("Please set your OpenAI API key in the OPENAI_API_KEY environment variable")
        print("You can get one from: https://platform.openai.com/api-keys")
        return

    # Create agent configuration
    agent_config = AgentConfig(
        openai_api_key=config.openai_api_key,
        zapier_api_key=config.zapier_api_key,
        google_credentials_path=config.google_credentials_path,
        data_storage_path="./agent_data",
        ui_port=8080
    )

    # Create and start the personal agent
    agent = PersonalAgent(agent_config)

    try:
        print("Starting AI Personal Agent...")
        print(f"Web UI will be available at: http://localhost:{agent_config.ui_port}")
        print("Press Ctrl+C to stop")

        agent.start()

        # Keep the main thread alive
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping AI Personal Agent...")
        agent.stop()
        print("Agent stopped successfully")

    except Exception as e:
        print(f"Error running agent: {e}")
        agent.stop()


if __name__ == "__main__":
    main()