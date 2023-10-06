import discord
import asyncio
import datetime
from bs4 import BeautifulSoup
import requests
import constants

from discord import app_commands
from discord.ext import commands

TOKEN = constants.TOKEN
intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await schedule_daily_message(True)


async def global_setup():
    await new_category_global(constants.CATEGORY_NAME)
    await new_text_channel_global(constants.ANOUNCEMENT_CHANNEL_NAME, constants.CATEGORY_NAME)
    await schedule_daily_message(True)



@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild = message.guild
    if message.content.startswith('$'):
        message.content = message.content[1:]

        if message.content == 'hello':
            await message.channel.send('Hello!')

        elif message.content == 'help':
            await message.channel.send('List of Commands:\n'
                                       '$help  -  Shows a list of commands\n'
                                       '$setup -  Creates the designated channel and category for the bot to work\n'
                                       '\n'
                                       'In case the bot stops working:\n'
                                       '1. delete all categories associated with bot\n'
                                       '2. make sure no channels/categories conflict with the bots naming scheme, Currently it is: "' + constants.CATEGORY_NAME + '" and ' + '"' + constants.ANOUNCEMENT_CHANNEL_NAME + '"\n'
                                       '3. use $setup')
        elif message.content == 'setup':
            if message.author.guild_permissions.administrator:
                await setup_local(message)
            else:
                await message.channel.send('You do not have permissions to use this command. You must be an admin')
        else:
            print(f'${message.content} is not a valid command therefore nothing sent in channel')
    else:
        return



async def setup_local(message):
    guild = message.guild
    #check if you have required perms in guild here

    await message.channel.send('Setting up....')

    await new_category_local(guild, constants.CATEGORY_NAME)
    await new_text_channel_local(guild, constants.ANOUNCEMENT_CHANNEL_NAME, constants.CATEGORY_NAME)

    t = datetime.datetime.now()
    new_solution_text_channel = str(t.year) + "-" + str(t.month) + "-" + str(t.day) + "-solutions"
    await new_text_channel_local(guild, new_solution_text_channel, constants.CATEGORY_NAME)

    link = await daily_leetcode_scraper()
    await announcement_local(guild, "@everyone\nDaily LeetCode Challenge: " + link + " \nPost your solutions in #put something here!")

    await message.channel.send('Done setting up see #' + constants.ANOUNCEMENT_CHANNEL_NAME + ' for the daily leetcode')
    await message.channel.send(
        'Please do not change the naming of the category/channels created by this bot, however you may move them around')



#calls announcement_global at the end eventually
async def schedule_daily_message(initial):
    link = await daily_leetcode_scraper()
    t = datetime.datetime.now()

    new_solution_text_channel = str(t.year) + "-" +  str(t.month) + "-"+ str(t.day) + "-solutions"
    text = "@everyone \nDaily LeetCode Challenge: " + link + " \nPost your solutions in #" + new_solution_text_channel
    if (initial):
        await announcement_global(text)
    else:
        while True:
            now = datetime.datetime.now()
            then = now.replace(hour=constants.ANOUNCEMENT_HOUR, minute=constants.ANOUNCEMENT_MINUTE, second=0)

            if (now > then):
                then = now.replace(day=now.day + 1)

            wait_time = (then - now).total_seconds()
            await asyncio.sleep(wait_time)

            await announcement_global(text)

    t = datetime.datetime.now()
    await new_text_channel_global(new_solution_text_channel, constants.CATEGORY_NAME)

    await lock_yesterday_solution(new_solution_text_channel)


async def lock_yesterday_solution(new_solution_text_channel):
    t = datetime.datetime.now()
    yesterday = t.replace(day=t.day - 1)
    old_channel_name = str(yesterday.year) + "-" +  str(yesterday.month) + "-" + str(yesterday.day) + "-solutions"
    for guild in client.guilds:
        for category in guild.categories:
            if(category.name == constants.CATEGORY_NAME):
                for channel in category.text_channels:
                    if(channel.name == old_channel_name):
                        await channel.set_permissions(guild.default_role, send_messages=False, read_messages=True)
                        await channel.edit(name="🔒" + old_channel_name)
                        for new_channel in category.text_channels:
                            if new_channel.name == new_solution_text_channel:
                                await channel.move(after=new_channel)


async def announcement_global(announcement_string):
    for guild in client.guilds:
        await announcement_local(guild, announcement_string)

async def announcement_local(guild, announcement_string):
    for category in guild.categories:
        if category.name == constants.CATEGORY_NAME:
            for channel in category.text_channels:
                if channel.name == constants.ANOUNCEMENT_CHANNEL_NAME:
                    await channel.send(announcement_string)


async def daily_leetcode_scraper():
    page_to_scrape = requests.get("https://leetcode.com/problemset/all/")
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    links = soup.findAll("a", href=True)
    problem_links = []
    for link in links:
        if (link['href'].startswith('/problems/')):
            problem_links.append(link['href'])

    now = datetime.datetime.now()
    for x in problem_links:
        if (x[-10:] == str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2)):
            return "https://leetcode.com" + x

    # send error message in channel which is initialized
    return "NULL: ERROR"

async def new_text_channel_global(new_channel_name, category_name):
    for guild in client.guilds:
        await new_text_channel_local(guild, new_channel_name, category_name)

async def new_text_channel_local(guild, new_channel_name, category_name):
    for category in guild.categories:
        if (category.name == category_name):
            channel_found = False
            for channel in category.text_channels:
                if channel.name == new_channel_name:
                    channel_found = True
            if (not channel_found):
                await category.create_text_channel(new_channel_name)
    return

async def new_category_global(new_category_name):
    for guild in client.guilds:
        found_category = False
        for category in guild.categories:
            if category.name == new_category_name:
                found_category = True

        if not found_category:
            await guild.create_category(new_category_name)
    return

async def new_category_local(guild, new_category_name):
    found_category = False
    for category in guild.categories:
        if category.name == new_category_name:
            found_category = True

    if not found_category:
        await guild.create_category(new_category_name)



client.run(TOKEN)
