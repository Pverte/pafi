#Imports of the necessary libraries requests for web resquest, discord for the discord bot, json for formatting the informations received by the api
import requests
import discord
import json
from discord.ext import commands
from discord.commands import Option
from io import BytesIO
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import binascii
from PIL import Image
import start

NUM_CLUSTERS = 5


intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
)

def getinfodeezer(ctx):
    """
    Input : Deezer Album link
    Output : artist, artistimage, link, coverimage, albumname"""
    global artist,  artistimage, link, coverimage, albumname, title, bpm
    ctx = str(ctx)
    apilink = "https://api.deezer.com/" + ctx[-16:]
    print(apilink)
    informations = requests.get(apilink)
    text = informations.json()
    if "album" in apilink:
        artist = text["artist"]["name"]
        artistimage = text["artist"]["picture_medium"]
        link= text["link"]
        coverimage = text["cover_medium"]
        albumname = text["title"]
    if "track" in apilink:
        artist = text["artist"]["name"]
        artistimage = text["artist"]["picture_medium"]
        link= text["link"]
        coverimage = text["album"]["cover_medium"]
        title = text["title"]
        albumname = text["album"]["title"]
        bpm = text["bpm"]

def covercolor(coverurl):
    response = requests.get(coverurl)
    im = Image.open(BytesIO(response.content))
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)

    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = np.histogram(vecs, len(codes))    # count occurrences

    index_max = np.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    readableHex = int(hex(int(colour.replace("#", ""), 16)), 0)
    print(readableHex)
    return readableHex

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(guild_ids=[694443902526029854], name="help", description="Need help about the bot ? Send this command")
async def help(ctx):
    await ctx.respond("Hey!")

@bot.slash_command(guild_ids=[694443902526029854], name="deezer", description="Let's find some Deezer Music.")
async def deezer(ctx, link):
    if "deezer.com" in link:
        if "album" in link:
            print(link)
            getinfodeezer(link)
            print(coverimage)
            e = discord.Embed(
                color = covercolor(coverimage),
                )
            e.add_field(
                name="Album name",
                value=albumname,
                inline= False
            )
            e.set_thumbnail(url=coverimage)
            e.add_field(
                name="Listen it here :",
                value=f"[Deezer]({link})"
            )
            e.add_field(
                name="\u200B",
                value="Bot by [Pverte](https://pverte.me)",
                inline=False
            )
            e.set_author(name= f"By {artist}", icon_url=artistimage)
            await ctx.respond(embed=e)
        elif "track" in link:
            print(link)
            getinfodeezer(link)
            print(coverimage)
            e = discord.Embed(
                color = covercolor(coverimage),
                )
            e.add_field(
                name="Title",
                value=title,
                inline=False
            )
            e.add_field(
                name="Album name",
                value=albumname,
                inline= True
            )
            if bpm == 0:
                bpm1 = "Unavailable"
            else :
                bpm1 = bpm
            e.add_field(
                name="BPM",
                value=bpm1,
                inline=True
            )
            e.set_thumbnail(url=coverimage)
            e.add_field(
                name="Listen it here :",
                value=f"[Deezer]({link})",
                inline=False
            )
            e.add_field(
                name="\u200B",
                value="Bot by [Pverte](https://pverte.me)",
                inline=False
            )
            e.set_author(name= f"By {artist}", icon_url=artistimage)
            await ctx.respond(embed=e)
    else:
        await ctx.respond("I don't see this as a deezer link, please restart, it have to look like htpps://deezer.com/album/302127")
@bot.slash_command(name='greet', description='Greet someone!', guild_ids=[694443902526029854])
async def greet(ctx, name=''):
    await ctx.respond(f'Hello {name}!')
bot.run(start.token)