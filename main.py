from typing import Final
import os
import textwrap
from dotenv import load_dotenv
from discord.ext import tasks, commands
from discord import Intents, Client, Message, Poll, utils, Status, app_commands, Interaction, Object, VoiceChannel
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
intents.members = True
client = Client(intents=intents, application_id=1315206352712503357)

client.tree = app_commands.CommandTree(client)

bot = commands.Bot(command_prefix="/", intents=intents)

days_since_last_argument = 16

@tasks.loop(hours=24)
async def increment_counter():
    global days_since_last_argument
    days_since_last_argument += 1


@tasks.loop(hours=24)
async def send_daily_message():
    await client.wait_until_ready()

    # hard coding the time for testing purposes
    current_time = datetime.now()
    target_time = current_time.replace(hour=1, minute=0, second=0, microsecond=0)

    if current_time >= target_time:
        target_time += timedelta(hours=24)


    time_until_target = (target_time - current_time).total_seconds()
    print(time_until_target)
    await asyncio.sleep(time_until_target)

    channel = client.get_channel(487110352149020687)

    if channel:
        await channel.send(f"Days since last argument: **{days_since_last_argument}**")
    


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

@client.tree.command(name="setcounter", description="Manually set argument counter.")
async def setcounter(interaction: Interaction, num: int):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Look at this fool trying to use an admin command when he aint even admin ROFL")
        return

    global days_since_last_argument
    days_since_last_argument = num

    await interaction.response.send_message(f"Counter set to `{num}`", ephemeral=True)

@client.tree.command(name="washingmachine", description="Moves someone around a bunch in hopes of getting their attention when deafened.")
async def washingmachine(interaction: Interaction, member: str):
    guild = interaction.guild
    target_member = utils.find(lambda m: m.name == member, guild.members)

    if not target_member:
        await interaction.response.send_message("User not found", ephemeral=True)
        return

    if not target_member.voice or not target_member.voice.channel:
        await interaction.response.send_message("Member not in voice channel", ephemeral=True)

    original_channel = target_member.voice.channel

    target_channel_1 = utils.find(lambda c: c.name == "1" and isinstance(c, VoiceChannel), guild.channels)
    target_channel_2 = utils.find(lambda d: d.name == "2" and isinstance(d, VoiceChannel), guild.channels)

    if not target_channel_1 or not target_channel_2:
        await interaction.respond.send_message("Voice channels not found", ephemeral=True)
        return

    await interaction.response.send_message(f"**{target_member}** has been put in the washing machine.")
    
    try:
        for i in range(5):
            if i == 4:
                await target_member.move_to(original_channel)
            else:
                await target_member.move_to(target_channel_1)
                await asyncio.sleep(0.5)
                await target_member.move_to(target_channel_2)

    except Exception as e:
        await interaction.respond.send_message("Failed to move member.", ephemeral=True)

@client.tree.command(name="provoke", description="Check if a user is provoking by letting the server review their recent messages.")
async def provoke(interaction: Interaction, username: str):
    # Find user
    guild = interaction.guild
    format_user = username.strip().lower()
    user = utils.find(lambda m: m.name.lower() == format_user, guild.members)

    for member in guild.members:
        print(member.name)
    

    if not user:
        await interaction.response.send_message(f"User '{username}' not found.")
        return

    # get channel and last 100 messages
    channel = interaction.channel
    messages = [msg async for msg in channel.history(limit=200)]

    # filter
    provokers_messages = [msg for msg in messages if msg.author == user]
    last_10_provoker_msg = provokers_messages[:10]

    # checks if they sent 10 messages in the last 100
    if not last_10_provoker_msg:
        await interaction.response.send_message(f"Not enough recent evidence for {username}.")
        return

    # combine messages into single 
    # message_content = "\n".join([f"\n[{msg.created_at.strftime('%I:%M %p')}]  {username}: {msg.content if msg.content else '*** User sent a picture. ***'}" for msg in reversed(last_10_provoker_msg)])
    message_content = "\n".join([f"\n[{msg.created_at.strftime('%I:%M %p')}]  {username}: " + 
        textwrap.fill(
            msg.content if msg.content else '*** User sent a picture. ***', 
            width=60, 
            subsequent_indent=' ' * (len(f"[{msg.created_at.strftime('%I:%M %p')}]  {username}: "))) for msg in reversed(last_10_provoker_msg)])

    formatted_message = f"```\n{message_content}```"


    await interaction.response.send_message(f"## Recent chat logs for {username}:\n\n{formatted_message}")

    jury = utils.find(lambda r: r.name == "Provoking Jury", guild.roles)
    if jury:
        jury = jury.mention
    else:
        jury = "Jury,"  

    poll_message = await channel.send(content=f"{jury}")

    my_poll = Poll("Was this person excessively provoking?", duration=timedelta(hours=1))
    my_poll.add_answer(text="Yes")
    my_poll.add_answer(text="No")
    my_poll.add_answer(text="Can't say for sure")

    await channel.send(content="", poll=my_poll)

    await asyncio.sleep(600)

    _, msg = await asyncio.gather(
        my_poll.end(), 
        client.wait_for(
            'message', 
            check=lambda m: m.reference and m.reference.message_id and m.reference.message_id == my_poll.message.id and m.type.value == 46))

    my_poll = (await my_poll.message.fetch()).poll

    results = my_poll.answers

    yes_counts = 0 
    no_counts = 0
    maybe_counts = 0

    for result in results:
        if result.text == "Yes":
            yes_counts = result.vote_count
        elif result.text == "Can't say for sure":
            maybe_counts = result.vote_count
        else:
            no_counts = result.vote_count

    
    if yes_counts > no_counts and yes_counts > maybe_counts:
        await channel.send(f"The jury has deemed {username} to be excessively provoking. Resetting counter.")
        global days_since_last_argument
        days_since_last_argument = 0
    else:
        await channel.send(f"{username}'s messages weren't deemed to be excessively provoking.")


"""
        await message.channel.send(content="", poll=my_poll)

        await asyncio.sleep(10)

        _, msg = await asyncio.gather(my_poll.end(), client.wait_for('message', check=lambda m: m.reference and m.reference.message_id and m.reference.message_id == my_poll.message.id and m.type.value == 46))
        my_poll = (await my_poll.message.fetch()).poll
"""



# handling startup for the bot

@client.event
async def on_ready():


    # Only do this when necessary, discord will time you out for excessive syncing

    # guild = Object(id=487110352149020683)
    # client.tree.copy_global_to(guild=guild)
    # synced = await client.tree.sync()
    # print(f"Commands synced: {len(synced)}")

    if not send_daily_message.is_running():
        send_daily_message.start()

    if not increment_counter.is_running():
        increment_counter.start()

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


    # if str(message.author.name) == "asdasd":
    #     await message.channel.send("Chris has sent the following message:\n ")
    #     await message.channel.send(f"## {message.content} ")

    #     my_poll = Poll("My question", duration=timedelta(hours=1))
    #     my_poll.add_answer(text="yes")
    #     my_poll.add_answer(text="no")

    #     await message.channel.send(content="", poll=my_poll)

    #     await asyncio.sleep(10)

    #     _, msg = await asyncio.gather(my_poll.end(), client.wait_for('message', check=lambda m: m.reference and m.reference.message_id and m.reference.message_id == my_poll.message.id and m.type.value == 46))
    #     my_poll = (await my_poll.message.fetch()).poll

    #     print("got here")

    #     results = my_poll.answers

    #     yes_counts = 0 
    #     no_counts = 0

    #     for result in results:
    #         if result.text == "yes":
    #             yes_counts = result.vote_count
    #         else:
    #             no_counts = result.vote_count
    #     if yes_counts > no_counts:
    #         await message.channel.send("Deemed as provoking, reseting counter.")
    # else:
    await send_message(message, user_message)


# main entry point
def main():

    client.run(token=TOKEN)

if __name__ == "__main__":
    main()