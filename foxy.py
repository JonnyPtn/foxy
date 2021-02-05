from datetime import datetime
import discord
from discord.ext import commands
from foxholewar import foxholewar

import discord
import os

bot = commands.Bot(command_prefix = '!')
mapCache = []

def updateMapCache():
    global mapCache
    if not mapCache:
        mapCache = foxholewar.getMapList()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def info(ctx):
    war = foxholewar.getCurrentWar()
    message = "War # " + str(war.warNumber) + "\n"
    conquestStartTime = int(war.conquestStartTime)
    startTime = datetime.utcfromtimestamp(conquestStartTime / 1000)
    message += "Conquest started: " + str(startTime) + "\n"
    if war.conquestEndTime is not None:
        message += "On " + str(datetime.fromtimestamp(war.conquestEndTime)) + " the " + str(war.winner) + " won the war"
    else:
        message += str(war.requiredVictoryTowns) + " required victory towns"
    await ctx.send(message)

@bot.command()
async def maps(ctx):
    updateMapCache()
    message = "Maps: \n"
    for map in mapCache:
        message += map.prettyName + "\n"
    await ctx.send(message)

@bot.command()
async def report(ctx, *args):
    mapName = "".join(args)

    updateMapCache()

    for map in mapCache:
        if map.prettyName == mapName:
            report = foxholewar.getReport(map)
            message = "Day " + str(report.dayOfWar) + " of war in " + mapName + ": \n"
            message += "Total enlistments: " + str(report.totalEnlistments) + "\n"
            message += "Colonial casualties: " + str(report.colonialCasualties) + "\n"
            message += "Warden casualties: " + str(report.wardenCasualties) + "\n"
            await ctx.send(message)
    


bot.run(os.getenv('DISCORD_BOT_TOKEN'))