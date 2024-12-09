from typing import Final
import os
from dotenv import load_dotenv
from discord.ext import tasks, commands
from discord import Intents, Client, Message, Poll, utils, Status, app_commands, Interaction, Object
from responses import get_response
from datetime import timedelta, datetime
import asyncio

# load the token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# set up the bot
intents = Intents.default()
intents.message_content = True
intents.presences = True
client = Client(intents=intents, application_id=1315206352712503357)

client.tree = app_commands.CommandTree(client)

bot = commands.Bot(command_prefix="/", intents=intents)

days_since_last_argument = 0

@tasks.loop(hours=24)
async def increment_counter():
    global days_since_last_argument
    days_since_last_argument += 1

async def schedule_daily_message():
    current_time = datetime.now()
    target_time = current_time.replace(hour=17, minute=0, second=0, microsecond=0)

    time_until_target = (target_time - current_time).total_seconds()

    await asyncio.sleep(time_until_target)

    send_daily_message.start()

@tasks.loop(hours=24)
async def send_daily_message():
    channel = client.get_channel(487110352149020687)
    if channel:
        await channel.send(f"Days since last argument involving chris: {days_since_last_argument}")

# message functionality
async def send_message(message, user_message):
    if not user_message:
        print("message was empty because intents were not enabled probably")
        return


    try:
        response = get_response(user_message)
        if response != "":
            await message.channel.send(response)
    except Exception as e:
        print(e)


@client.tree.command(name="gl", description="Check if GL is online.")
async def gl(interaction: Interaction):
    guild = interaction.guild

    member = utils.find(lambda m: m.name == "jrbaconcheeseburger", interaction.guild.members)

    if member:
        if member.status == Status.online:
            await interaction.response.send_message("Hooray! GL is online.")
        else:
            await interaction.response.send_message("GL is not online.")



# handling startup for the bot

@client.event
async def on_ready():


    # Only do this when necessary, discord will time you out for excessive syncing

    guild = Object(id=487110352149020683)
    synced = await client.tree.sync(guild=guild)
    print(f"Commands synced: {len(synced)}")


    print(f"{client.user} is now running. on foe nem\n")


# handling incoming messages

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    username = str(message.author)
    name = str(message.author.name)
    user_message = message.content
    channel = str(message.channel)


    print(f"[{channel}] {username}: {user_message}")



    if str(message.author.name) == "jrbaconcheeseburger":
        await message.channel.send("Chris has sent the following message:\n ")
        await message.channel.send(f"## {message.content} ")

        my_poll = Poll("My question", duration=timedelta(hours=1))
        my_poll.add_answer(text="yes")
        my_poll.add_answer(text="no")

        await message.channel.send(content="", poll=my_poll)

        await asyncio.sleep(10)

        await my_poll.end()
        msg = await client.wait_for("message_edit", check=lambda before, after: after.id == message.id and after.poll and after.poll.is_finalized())   

        my_poll = msg.poll

        results = my_poll.answers

        yes_counts = 0 
        no_counts = 0

        for result in results:
            if result.text == "yes":
                yes_counts = result.vote_count
            else:
                no_counts = result.vote_count
        print(no_counts)
        print(yes_counts)
        if yes_counts > no_counts:
            await message.channel.send("Deemed as provoking, reseting counter.")
    else:
        await send_message(message, user_message)


# main entry point
def main():

    client.run(token=TOKEN)

if __name__ == "__main__":
    main()