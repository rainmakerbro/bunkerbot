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
shmovies = sh.sheet1
shwatched = sh.worksheet('Watched')
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

#Takes user category and awaits a title message to add to Sheet1
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


#Watched takes a user entered title, removes from the main list,
#adds to the 'Sheet2' watched list
@bunkerbot.command(name='watched')
async def _watched(ctx, *args):
    if ctx.author == bunkerbot.user:
        return

    watched_item = ' '.join(args)
    watched_cells = sh.sheet1.find(watched_item)
    watched_row = watched_cells.row
    sh.sheet1.delete_rows(watched_row)
    sh2.append_row([watched_item])
    await ctx.add_reaction('\U00002705')
    await ctx.add_reaction('\U0001F440')

#Displays full list of designated type in private message
@bunkerbot.command(aliases=['movies', 'games', 'books'])
async def _list(ctx):
    if ctx.author == bunkerbot.user:
        return

    if ctx.invoked_with == 'movies':
        chosensheet = 'sh' + ctx.invoked_with
        values = f'\n '.join(map(str, (shmovies.col_values(1))))
    if ctx.invoked_with == 'games':
        chosensheet = 'sh' + ctx.invoked_with
        values = f'\n '.join(map(str, (shgames.col_values(1))))
    if ctx.invoked_with == 'books':
        chosensheet = 'sh' + ctx.invoked_with
        values = f'\n '.join(map(str, (shbooks.col_values(1))))

    listtype = str.capitalize(ctx.invoked_with)
    await ctx.author.send(f'{listtype} list: \n')
    await ctx.author.send(values)

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

bunkerbot.run(bunker_token)
