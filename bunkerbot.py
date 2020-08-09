import discord
from discord.ext import commands

import logging
import asyncio
import os

# Gspread for interacting with Google Sheets
import gspread

gc = gspread.service_account(filename = 'C:/Users/Nate/bunker/client_secret.json')

sh = gc.open("bunkerbot's movielist")
sh2 = sh.worksheet('Sheet2')


# Logging of info into console.  Later on we should output this to a file.
logging.basicConfig(level=logging.INFO)

# The bot's name(used for commands and events) and command prefix
bunkerbot = commands.Bot(command_prefix= '.')
bunker_token = os.environ.get('BUNKER_TOKEN')


@bunkerbot.event
async def on_ready():
    game = discord.Game('.help')
    await bunkerbot.change_presence(activity=game)
    print('bunkerbot has logged in as {0.user}.'.format(bunkerbot))

@bunkerbot.event
async def on_message(message):
    if message.author == bunkerbot.user:
        return

    if message.content.startswith('.add'):
        await message.channel.send('Which movie would you like to add?')
        def pred(m):
            return m.author == message.author and m.channel == message.channel

        try:
            msg = await bunkerbot.wait_for('message', check=pred, timeout=30.0)

        except asyncio.TimeoutError:
            await message.channel.send('You took too long...')
        else:
            if msg:
                sh.sheet1.append_row([msg.content])
                await msg.add_reaction('✔️')

    if message.content.startswith('.remove'):
        await message.channel.send('Which movie would you like to remove?')
        def pred(m):
            return m.author == message.author and m.channel == message.channel

        try:
            msg = await bunkerbot.wait_for('message', check=pred, timeout=30.0)

        except asyncio.TimeoutError:
            await message.channel.send('You took too long...')
        else:
            if msg:
                watched_cells = sh.sheet1.find(msg.content)
                watched_row = watched_cells.row
                sh.sheet1.delete_rows(watched_row)
                await msg.add_reaction('✔️')
            else:
                await message.channel.send("Sorry, I'm not seeing that one, check your spelling and try again!")

    if message.content.startswith('.watched'):
        await message.channel.send('Which movie did you watch?')
        def pred(m):
            return m.author == message.author and m.channel == message.channel

        try:
            msg = await bunkerbot.wait_for('message', check=pred, timeout=30.0)

        except asyncio.TimeoutError:
            await message.channel.send('My "watched" command timed out, try calling the movie list first so you can copy/paste the title!')
        except gspread.exceptions.CellNotFound:
            await message.channel.send("Sorry I'm not seeing that movie, try calling the list first so you can copy/pase the title you watched!")
        else:
            if msg:
                watched_cells = sh.sheet1.find(msg.content)
                watched_row = watched_cells.row
                sh.sheet1.delete_rows(watched_row)
                sh2.append_row([msg.content])
                await msg.add_reaction('✔️')
                await msg.add_reaction('👀')

    if message.content.startswith('.movies'):
        values = '\n '.join(map(str, (sh.sheet1.col_values(1))))
        await message.channel.send(values)

    if message.content.startswith('.help'):
        await message.channel.send("Ask me to '.add' to add a movie to the list!  To see the list of movies, say '.movies', or tell me you '.watched' a movie to clear your backlog!  If you need to '.remove' a title that we don't want on the list, we do that too!")

bunkerbot.run(bunker_token)
