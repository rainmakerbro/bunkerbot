import discord
from discord.ext import commands

import logging
import asyncio

# configparser for reading machine specific path and key variables
import configparser

config = configparser.ConfigParser()
config.read('keeperfile.ini')
config.sections()
bunker_token = config['SPECIFIC VALUES']['APIKey']
clientsecretloc = config['SPECIFIC VALUES']['clientSecretLoc']

# Gspread for interacting with Google Sheets
import gspread

gc = gspread.service_account(filename = clientsecretloc)

sh = gc.open("bunkerbot's movielist")
sh2 = sh.worksheet('Sheet2')
shgames = sh.worksheet('Games')
shbooks = sh.worksheet('Books')

# Logging of info into console.  Later on we should output this to a file.
logging.basicConfig(level=logging.INFO)

# The bot's name(used for commands and events) and command prefix
bunkerbot = commands.Bot(command_prefix= '.')

@bunkerbot.event
async def on_ready():
    game = discord.Game('.help')
    await bunkerbot.change_presence(activity=game)
    print('bunkerbot has logged in as {0.user}.'.format(bunkerbot))

@bunkerbot.command(aliases=['add', 'new'])
async def _addtitle(ctx, arg):
    if ctx.author == bunkerbot.user:
        return

    await ctx.channel.send(f'Which {arg} would you like to add?')
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bunkerbot.wait_for('message', check=pred, timeout=30.0)

    except asyncio.TimeoutError:
        await ctx.channel.send('You took too long...')
    else:
        if msg:
            if arg == 'movie':
                sh.sheet1.append_row([msg.content])
                await msg.add_reaction('\U00002705')
                await msg.add_reaction('\U0001F9E7')
            elif arg == 'game':
                shgames.append_row([msg.content])
                await msg.add_reaction('\U0001F3AE')
                await msg.add_reaction('\U00002705')
            elif arg == 'book':
                shbooks.append_row([msg.content])
                await msg.add_reaction('\U0001F4DA')
                await msg.add_reaction('\U00002705')

@bunkerbot.command(name='watched')
async def _watched(ctx, *args):
    if ctx.author == bunkerbot.user:
        return

    watched_item = ' '.join(args)
    print(watched_item)
    watched_cells = sh.sheet1.find(watched_item)
    watched_row = watched_cells.row
    sh.sheet1.delete_rows(watched_row)
    sh2.append_row([watched_item])
    await ctx.add_reaction('\U00002705')
    await ctx.add_reaction('\U0001F440')

@bunkerbot.command(aliases=['list', 'library', 'movies', 'games', 'books'])
async def _list(ctx):
    if ctx.author == bunkerbot.user:
        return

    values = f'{arg}\n '.join(map(str, (sh.sheet1.col_values(1)))) #Change sheet based on ctx?
    await message.channel.send(values)

@bunkerbot.command(aliases=['remove', 'old', 'burn'])
async def _remove(ctx, *args):
    if ctx.author == bunkerbot.user:
        return

    remove_item = ' '.join(args)
    watched_cells = sh.sheet1.find(remove_item)
    watched_row = watched_cells.row
    sh.sheet1.delete_rows(watched_row)
    await msg.add_reaction('\U00002705')
    await msg.add_reaction('\U0001F6BD')


'''@bunkerbot.event
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
            await bunkerbot.process_commands(message)
        else:
            if msg:
                sh.sheet1.append_row([msg.content])
                await msg.add_reaction('\U00002705')
                await msg.add_reaction('\U0001F9E7')
                await bunkerbot.process_commands(message)

    if message.content.startswith('.remove'):
        await message.channel.send('Which movie would you like to remove?')
        def pred(m):
            return m.author == message.author and m.channel == message.channel

        try:
            msg = await bunkerbot.wait_for('message', check=pred, timeout=30.0)

        except asyncio.TimeoutError:
            await message.channel.send('You took too long...')
            await bunkerbot.process_commands(message)
        else:
            if msg:
                watched_cells = sh.sheet1.find(msg.content)
                watched_row = watched_cells.row
                sh.sheet1.delete_rows(watched_row)
                await msg.add_reaction('\U00002705')
                await msg.add_reaction('\U0001F6BD')
                await bunkerbot.process_commands(message)
            else:
                await message.channel.send("Sorry, I'm not seeing that one, check your spelling and try again!")
                await bunkerbot.process_commands(message)

    if message.content.startswith('.watched'):
        await message.channel.send('Which movie did you watch?')
        def pred(m):
            return m.author == message.author and m.channel == message.channel

        try:
            msg = await bunkerbot.wait_for('message', check=pred, timeout=30.0)

        except asyncio.TimeoutError:
            await message.channel.send('My "watched" command timed out, try calling the movie list first so you can copy/paste the title!')
            await bunkerbot.process_commands(message)
        except gspread.exceptions.CellNotFound:
            await message.channel.send("Sorry I'm not seeing that movie, try calling the list first so you can copy/pase the title you watched!")
            await bunkerbot.process_commands(message)
        else:
            if msg:
                watched_cells = sh.sheet1.find(msg.content)
                watched_row = watched_cells.row
                sh.sheet1.delete_rows(watched_row)
                sh2.append_row([msg.content])
                await msg.add_reaction('\U00002705')
                await msg.add_reaction('\U0001F440')
                await bunkerbot.process_commands(message)

    if message.content.startswith('.movies'):
        values = '\n '.join(map(str, (sh.sheet1.col_values(1))))
        await message.channel.send(values)
        await bunkerbot.process_commands(message)

    if message.content.startswith('.help'):
        await message.channel.send("Ask me to '.add' to add a movie to the list! \
          To see the list of movies, say '.movies', or tell me you '.watched' a movie to clear your backlog! \
           If you need to '.remove' a title that we don't want on the list, we do that too!")'''


bunkerbot.run(bunker_token)
