from datetime import datetime
import discord
from discord.ext import commands, tasks
from foxholewar import foxholewar

import data_access
import discord
import logging
import os
import asyncio

from PIL import Image

logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix='!')

def getImage(path):
    # Use PIL to convert to png, because discord won't show TGA
    # and save to a local cache
    cachePath = ".imageCache/" + path + ".png"

    if not os.path.isfile(cachePath):
        image = Image.open(path)
        image.save(cachePath, 'PNG')

    return open(cachePath, 'rb')


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name='Foxhole'))
    bot.add_cog(data_access.DataAccess())
    bot.client = foxholewar.Client()


@bot.command()
async def info(ctx):
    """Basic info for the current war"""

    war = bot.client.getCurrentWar()
    embed = discord.Embed(title="War # " + str(war.warNumber))

    startTime = datetime.utcfromtimestamp(war.conquestStartTime / 1000)
    embed.add_field(name="Conquest started", value=str(
        startTime.strftime("%A %d/%m/%y at %H%M")))

    if war.conquestEndTime is not None:
        endTime = datetime.utcfromtimestamp(war.conquestEndTime / 1000)
        embed.add_field(name=str(war.winner) + " Won the war",
                        value=str(endTime.strftime("%A %d/%m/%y at %H%M")))

    await ctx.send(embed=embed)


@bot.command()
async def maps(ctx):
    """Get the list of maps"""

    message = "Maps: \n"
    for map in foxholewar.rawMapNameToPretty.values():
        message += map + "\n"
    await ctx.send(message)


@bot.command()
async def report(ctx, *, arg=None):
    """Get a report on the war, or the given map"""
    await ctx.trigger_typing()
    map = arg
    if not map:
        map = "totals"
    elif not foxholewar.isValidMapName(map):
        await ctx.send("Unrecognised map name: " + map)
        return

    report = await bot.cogs['DataAccess'].generateWarReport(map)
    title = "Situation report"
    if arg is not None:
        title += " For " + arg
    embed = discord.Embed(title=title)

    embed.add_field(name="Total casualties", value="Colonial: " + str(report.totalColonialCasualties) +
                    "\nWarden: " + str(report.totalWardenCasualties), inline=True)
    embed.add_field(name="Last hour casualties", value="Colonial: " + str(report.lastHourColonialCasualties) +
                    "\nWarden: " + str(report.lastHourWardenCasualties), inline=True)
    await ctx.send(embed=embed)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
