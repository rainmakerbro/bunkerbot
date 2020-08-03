import discord
from discord.ext import commands
import logging
import asyncio
import gspread

gc = gspread.service_account(filename = 'C:/Users/Nate/bunker/client_secret.json')

sh = gc.open("bunkerbot's movielist")

print(sh.sheet1.get('A1'))

# Logging of info into console.  Later on we should output this to a file.
logging.basicConfig(level=logging.INFO)

# The bot's name(used for commands and events) and command prefix
bunkerbot = commands.Bot(command_prefix= '.')

# The initial list made to keep movies.  The above code does away with this and outputs to a Google sheet
movielist = ['Annihilation']

# Start of sheet control for adding movies to movielist
add_to_spot = 0

@bunkerbot.event
async def on_ready():
    game = discord.Game('.help')
    await bunkerbot.change_presence(activity=game)
    print('bunkerbot has logged in as {0.user}.'.format(bunkerbot))

@bunkerbot.event
async def on_message(message):
    if message.author == bunkerbot.user:
        return

    if message.content.startswith('.hello'):
        await message.channel.send('Hello!')

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
                add_to_spot = sh.sheet1.append_row([msg.content])
                movielist.append(msg.content)
                await message.channel.send('added to the list!')

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
                movielist.remove(msg.content)
                await message.channel.send('removed from the list!')
            else:
                await message.channel.send("Sorry, I'm not seeing that one, check your spelling and try again!")

    if message.content.startswith('.movies'):
        values = '\n '.join(map(str, (sh.sheet1.col_values(1))))
        await message.channel.send(values)

    if message.content.startswith('.help'):
        await message.channel.send("Ask me to 'add' to add a movie to the list!  To see the list of movies, say 'movies'")

bunkerbot.run(token)
