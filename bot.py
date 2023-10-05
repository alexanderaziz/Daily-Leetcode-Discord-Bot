import discord
import asyncio
import datetime
from bs4 import BeautifulSoup
import requests

from discord import app_commands
from discord.ext import commands

TOKEN = 'MTE1NDkwNjc1MTk0NzI1NTg1OQ.G30zzv.u9IvdohrXYF5fKl9QnLLRto84xvneFTvuxqIdw'
intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False


client = discord.Client(intents=intents)



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await schedule_daily_message()
    await new_text_channel('leetcode!!!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$'):
        message.content = message.content[1:]

        if message.content == 'hello':
            await message.channel.send('Hello!')
        elif message.content == 'leetcode':
            await message.channel.send('Here is your leetcode problem')
        else:
            print(f'${message.content} is not a valid command therefore nothing sent in channel')
    else:
        return


async def schedule_daily_message():

    if(True):
        link = await daily_leetcode_scraper()
        channel = client.get
        await channel.send("Daily LeetCode Challenge: " + link + " \nPost your solutions in #put something here!")
        return

    while True:
        now = datetime.datetime.now()
        # then = now + datetime.timedelta(days=1)
        then = now.replace(hour=22, minute=1, second = 1)

        if(now > then):
            then = now.replace(day=now.day + 1)

        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        channel = client.get_channel(1154919387539718189)

        link = await daily_leetcode_scraper()
        await channel.send("Daily LeetCode Challenge: " + link + " \nPost your solutions in #put something here!" )


#Complete this later
# async def announcement_all_guilds(annoucement_string):
#     for guild in client.guilds:
#         guild.get_channel()
async def daily_leetcode_scraper():
    page_to_scrape = requests.get("https://leetcode.com/problemset/all/")
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    links = soup.findAll("a", href = True)
    problem_links = []
    for link in links:
        if(link['href'].startswith('/problems/')):
            problem_links.append(link['href'])


    now = datetime.datetime.now()
    for x in problem_links:
        if(x[-10:] == str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2)):
            return "https://leetcode.com" + x

    #send error message in channel which is initialized
    return "NULL: ERROR"


async def new_text_channel(new_channel_name):

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == new_channel_name:
                print("Channel: " + new_channel_name + " already exists so nothing happens")
                return

    await guild.create_text_channel(new_channel_name)
    return



client.run(TOKEN)
