import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from openai import OpenAI
import random
from configs import BOT_TOKENS, CHANNEL_ID, OPENAI_API_KEY, BOT_NAMES, PERSONALITY_PROMPTS

# Replace these with your actual bot tokens
bot_tokens = BOT_TOKENS

# Replace this with your desired channel ID
CHANNEL_ID = CHANNEL_ID  # Your channel ID here

# Set up OpenAI API key
openai_client = OpenAI(api_key=OPENAI_API_KEY)


# Set up intents
# Set up intents
intents = discord.Intents.default()
intents.messages = True  # Necessary for receiving messages
intents.guild_messages = True  # Necessary for receiving guild (server) messages
intents.reactions = True  # Necessary for receiving reactions

# Create separate bot instances for each bot
bots = [commands.Bot(command_prefix='!', intents=intents) for _ in range(6)]

# Set the bot names
bot_names = BOT_NAMES

# Define the personality prompts for each bot
personality_prompts = PERSONALITY_PROMPTS

# store conversation history
last_conversation_history = {}

async def generate_response(conversation_history, bot_index):
    prompt = f"""Conversation history:\n{conversation_history}\n\n{personality_prompts[bot_index]}
    In a concise response of no more than two sentences, generate a response as {bot_names[bot_index]} while keeping in mind your unique personality traits. Develop your own thoughts based on the previous response, and ensure that your contribution makes logical sense within the context of the ongoing conversation. Remember, you're emulating a college-aged individual, so use language and expressions that resonate with that age group, adding a touch of humor and wit to the dialogue.
    Notice if your name, {bot_names[bot_index]}, is mentioned in the conversation history. If it is, understand that you are being directly addressed or talked about, and respond appropriately. If you are referring to yourself in the response, use "I" instead of your name.
    """
    try:
        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': f'You are {bot_names[bot_index]}. Do not include your name in the response. If you are referring to yourself, use "I" instead. Keep your response concise and complete, using no more than two sentences.'},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=60,
            n=1,
            stop=None,
            temperature=0.7
        )
        generated_response = response.choices[0].message.content.strip().replace('"', '')
        
        # Check if the generated response ends with a proper punctuation mark
        if not generated_response.endswith(('.', '!', '?')):
            # If not, add a period at the end to ensure a complete sentence
            generated_response += '.'
        
        return generated_response
    except Exception as e:
        print(f"Error generating response for {bot_names[bot_index]}: {e}")
        return None

async def send_message(bot_index, conversation_history, user=None):
    async with bots[bot_index].get_channel(CHANNEL_ID).typing():
        if user:
            response = await generate_response(conversation_history, bot_index, user.id)
        else:
            response = await generate_response(conversation_history, bot_index)
        
        if response:
            sent_message = await bots[bot_index].get_channel(CHANNEL_ID).send(response)
        else:
            print(f"No response generated for {bot_names[bot_index]}. Skipping.")
        return sent_message

async def is_message_funny(message_content):
    prompt = f"""
    Humor Analysis Request:
    Assess the humor content of the following message based on the criteria of unexpectedness, exaggeration, and relevance to common social experiences:

    "{message_content}"

    Criteria:
    1. Unexpectedness: Does the message contain elements that are surprising or not obvious?
    2. Exaggeration: Are there any parts of the message that dramatically overstate or magnify a situation?
    3. Social Relevance: Is the humor relatable to a wide audience by reflecting common social experiences or dilemmas?

    Conclusion:
    Based on the above criteria, determine whether the message should be considered funny. Respond with "Yes" for funny, and "No" for not funny.
    """
    try:
        response = openai_client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=10,
            n=1,
            stop=None,
            temperature=0.7
        )
        is_funny = response.choices[0].message.content.strip().lower()
        return is_funny == "yes"
    except Exception as e:
        print(f"Error determining if message is funny: {e}")
        return False

async def add_reaction(bot_index, message):
    if await is_message_funny(message.content):
        reaction = random.choice(['💀', '😂'])
        reacting_bots = [bot for idx, bot in enumerate(bots) if idx != bot_index]
        for bot in reacting_bots:
            await bot.get_channel(CHANNEL_ID).get_partial_message(message.id).add_reaction(reaction)

async def main(topic, user=None):
    if user:
        user_id = user.id
        conversation_history = last_conversation_history.get(user_id, [])
    else:
        conversation_history = []

    if topic:
        conversation_history.append(f"Topic: {topic}\n\n")
    
    bot_order = list(range(6))  # Create a list of bot indices
    random.shuffle(bot_order)  # Shuffle the bot order randomly

    sent_messages = []  # Store the sent messages

    for bot_index in bot_order:
        sent_message = await send_message(bot_index, conversation_history, user)
        conversation_history.append(f"{bot_names[bot_index]}: {sent_message.content}\n")

        sent_messages.append(sent_message)  # Add the sent message to the list

        await asyncio.sleep(8)  # Wait for 8 seconds before the next bot responds

    # Store the last conversation history for the user
    if user:
        last_conversation_history[user_id] = conversation_history
    
    # Check if there are at least 2 sent messages
    if len(sent_messages) >= 2:
        # Choose a random bot to react to a random message (excluding its own message)
        reaction_bot_index = random.choice(bot_order)
        message_to_react = random.choice([msg for msg in sent_messages if msg.author != bots[reaction_bot_index].user])
        
        await add_reaction(reaction_bot_index, message_to_react)


# context command
@bots[0].tree.command(name='context', description='Start a conversation with a given topic')
@app_commands.describe(topic='The topic of the conversation')
async def context(interaction: discord.Interaction, topic: str):
    await interaction.response.send_message(f"{bot_names[0]} is starting a conversation about '{topic}'...", ephemeral=True)
    await main(topic)

# continue command
@bots[0].tree.command(name='continue', description='Continue the last conversation')
async def continue_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in last_conversation_history:
        await interaction.response.send_message(f"Continuing the conversation...", ephemeral=True)
        await main(None, interaction.user)
    else:
        await interaction.response.send_message("No previous conversation found. Please start a new conversation using /context.", ephemeral=True)

# Event listeners for each bot
for index, bot in enumerate(bots):
    @bot.event
    async def on_ready():
        print(f'{bot_names[index]} has connected to Discord!')
        if index == 0:
            try:
                synced = await bot.tree.sync()
                print(f"Synced {len(synced)} command(s)")
            except Exception as e:
                print(f"Error syncing commands: {e}")
    @bot.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return  # Ignore reactions from bots
        
        if reaction.message.channel.id != CHANNEL_ID:
            return  # Ignore reactions in other channels
        
        if reaction.emoji not in ['💀', '😂']:
            return  # Ignore reactions other than skull or laughing emoji
        
        for bot in bots:
            if reaction.message.author == bot.user:
                continue  # Skip the bot that sent the message
            
            if bot.user == reaction.message.author:
                continue  # Skip the bot if it is the author of the message
            
            await reaction.message.add_reaction(reaction.emoji)

# Run the bots
async def run_bots():
    await asyncio.gather(*[bot.start(token) for bot, token in zip(bots, BOT_TOKENS)])

asyncio.run(run_bots())