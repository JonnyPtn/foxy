from datetime import datetime
import discord
from discord.ext import commands
from foxholewar import foxholewar

import discord
import os

from PIL import Image

bot = commands.Bot(command_prefix = '!')
mapCache = []

def getImage(path):
    # Use PIL to convert to png, because discord won't show TGA
    # and save to a local cache
    cachePath = ".imageCache/" + path + ".png"

    if not os.path.isfile(cachePath):
        image = Image.open(path)
        image.save(cachePath, 'PNG')
    
    return open(cachePath, 'rb')

def updateMapCache():
    global mapCache
    if not mapCache:
        mapCache = foxholewar.getMapList()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name='Foxhole'))

@bot.command()
async def info(ctx):
    """Basic info for the current war"""

    war = foxholewar.getCurrentWar()
    embed = discord.Embed(title="War # " + str(war.warNumber))

    startTime = datetime.utcfromtimestamp(war.conquestStartTime / 1000)
    embed.add_field(name="Conquest started", value=str(startTime.strftime("%A %d/%m/%y at %H%M")))

    if war.conquestEndTime is not None:
        endTime = datetime.utcfromtimestamp(war.conquestEndTime / 1000)
        embed.add_field(name=str(war.winner) + " Won the war", value= str(endTime.strftime("%A %d/%m/%y at %H%M")))

    await ctx.send(embed=embed)

@bot.command()
async def maps(ctx):
    """Get the list of maps"""

    updateMapCache()
    message = "Maps: \n"
    for map in mapCache:
        message += map.prettyName + "\n"
    await ctx.send(message)


@bot.command()
async def report(ctx, *args):
    """Get a report for the given map"""

    mapName = " ".join(args)
    updateMapCache()

    for map in mapCache:
        if map.prettyName == mapName:
            report = map.getReport()
            message = "Day " + str(report.dayOfWar) + " of war in " + mapName + ": \n"
            message += "Total enlistments: " + str(report.totalEnlistments) + "\n"
            message += "Colonial casualties: " + str(report.colonialCasualties) + "\n"
            message += "Warden casualties: " + str(report.wardenCasualties) + "\n"
            await ctx.send(message)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))