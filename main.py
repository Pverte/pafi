#Imports of the necessary libraries requests for web resquest, discord for the discord bot, json for formatting the informations received by the api
import requests
import discord
import json
from io import BytesIO
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import binascii
from PIL import Image
import start
import time

NUM_CLUSTERS = 5


intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
)

def deezerinfo(ctx):
    """
    Input : Deezer link
    Output : artist, artistimage, link, coverimage, albumname"""
    global artist,  artistimage, coverimage, albumname, title, bpm
    if "deezer.page.link" in ctx:
        ctx = requests.get(ctx).url
    if "?" in ctx:
        ctx = ctx.split("?", 1)[0]
    apilink = ctx.split("/")[-2:]
    apilink = "https://api.deezer.com/" + apilink[0] + "/" + apilink[1]
    print(apilink)
    informations = requests.get(apilink)
    text = informations.json()
    deezerinfo.link= text["link"]
    if "album" in apilink:
        artist = text["artist"]["name"]
        artistimage = text["artist"]["picture_medium"]
        deezerinfo.date = text["release_date"]
        coverimage = text["cover_medium"]
        albumname = text["title"]
    if "track" in apilink:
        artist = text["artist"]["name"]
        artistimage = text["artist"]["picture_medium"]
        deezerinfo.date = text["release_date"]
        coverimage = text["album"]["cover_medium"]
        title = text["title"]
        albumname = text["album"]["title"]
        bpm = text["bpm"]
    if "artist" in apilink:
        artist=text["name"]
        artistimage=text["picture_medium"]
        coverimage=text["picture_big"]
        deezerinfo.nb_album=text["nb_album"]
        deezerinfo.nb_fan=text["nb_fan"]

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
    global pverte, errorschan
    pverte = bot.get_user(577089415369981952)
    errorschan = bot.get_channel(963776434428592198)
    print(f'We have logged in as {bot.user}')
    await errorschan.send("Je suis prêt !")
@bot.event
async def on_application_command_error(ctx, error):
    """
    Send an error message telling the message that triggerer the error and the error itself into the errorschan
    """
    e = discord.Embed(
    color = discord.Colour.red(),
    title = "Error",
    description="AN ERROR JUST OCCURED, IT HAS BEEN SENT TO THE DEVELOPERS.")
    await errorschan.send(f"<@577089415369981952> an error just occured with the command {ctx.command} : {error}")
    await ctx.respond(embed=e)

@bot.slash_command(guild_ids=[694443902526029854], name="help", description="Need help about the bot ? Send this command")
async def help(ctx):
    await ctx.respond("Hey!")

@bot.slash_command(guild_ids=[694443902526029854], name="deezer", description="Let's find some Deezer Music !")
async def deezer(ctx, link):
    await ctx.defer()
    deezerinfo(link)
    print(deezerinfo.link)
    if "album" in deezerinfo.link:
        print(link)
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
            value=f"[Deezer]({deezerinfo.link})"
        )
        e.add_field(
            name="Release date",
            value =deezerinfo.date
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name= f"By {artist}", icon_url=artistimage)
        await ctx.respond(embed=e)
    elif "track" in deezerinfo.link:
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
        e.add_field(
            name="Release date",
            value =deezerinfo.date,
            inline=True
        )
        e.set_thumbnail(url=coverimage)
        e.add_field(
            name="Listen it here :",
            value=f"[Deezer]({deezerinfo.link})",
            inline=False
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name= f"By {artist}", icon_url=artistimage)
        await ctx.respond(embed=e)
    elif "artist" in deezerinfo.link:
        print(coverimage)
        e = discord.Embed(
            color = covercolor(coverimage),
            )
        e.add_field(
            name="Artist",
            value=artist,
            inline=False
        )
        print(artist)
        e.add_field(
            name="Number of fans on Deezer",
            value=deezerinfo.nb_fan,
            inline= True
        )
        print(deezerinfo.nb_fan)
        e.add_field(
            name="Numbers of albums",
            value=deezerinfo.nb_album,
            inline=True
        )
        print(deezerinfo.nb_album)
        e.set_thumbnail(url=coverimage)
        e.add_field(
            name="Listen it here :",
            value=f"[Deezer]({deezerinfo.link})",
            inline=False
        )
        print(deezerinfo.link)
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name=artist, icon_url=artistimage)
        await ctx.respond(embed=e)
@bot.slash_command(name='greet', description='Greet someone!', guild_ids=[694443902526029854])
async def greet(ctx, name=''):
    await ctx.respond(f'Hello {name}!')
bot.run(start.token)