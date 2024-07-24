# Friend Simulation

Friend Simulation is a Discord bot project that creates an engaging group chat experience using AI-powered personalities. It simulates conversations between multiple AI entities, each with its own unique characteristics.



## Features

- Six distinct AI personalities engaging in group conversations
- GPT-4o-mini powered responses for natural language interaction
- Topic-based conversation initiation
- Conversation continuation functionality
- Automatic emoji reactions to humorous messages
- Randomized response order for more natural conversation flow

## Prerequisites

- Python 3.8+
- `discord.py` library
- OpenAI Python library
- Discord bot tokens
- OpenAI API key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/nazk-1/friend-simulation.git
    cd friend-simulation
    ```

2. Install required dependencies:
    ```bash
    pip install discord.py openai
    ```

3. Create a `configs.py` file in the project root with the following structure:
    ```python
    BOT_TOKENS = ['token1', 'token2', 'token3', 'token4', 'token5', 'token6']
    CHANNEL_ID = your_channel_id
    OPENAI_API_KEY = 'your_openai_api_key'
    BOT_NAMES = ['Name1', 'Name2', 'Name3', 'Name4', 'Name5', 'Name6']
    PERSONALITY_PROMPTS = [
        "Personality description for Bot 1",
        "Personality description for Bot 2",
        "Personality description for Bot 3",
        "Personality description for Bot 4",
        "Personality description for Bot 5",
        "Personality description for Bot 6"
    ]
    ```

## Usage

Run the bot:
```bash
python bot.py
```
## Available Discord commands:

- `/context [topic]`: Initiate a new conversation on the specified topic
- `/continue`: Resume the most recent conversation

## Contributing

Contributions to the Friend Simulation project are welcome. Please feel free to submit issues or pull requests on the [GitHub repository](https://github.com/nazk-1/friend-simulation).

## License

This project is licensed under the MIT License. See the [LICENSE file](https://github.com/nazk-1/friend-simulation/blob/main/LICENSE) in the repository for full license text.

## Disclaimer

This bot is intended for educational and entertainment purposes. Ensure compliance with Discord's Terms of Service and OpenAI's use-case policies when deploying and using this bot.

