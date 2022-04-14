#Imports of the necessary libraries requests for web resquest, discord for the discord bot, json for formatting the informations received by the api
import traceback
import requests
import discord
from discord.ext import commands
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
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


NUM_CLUSTERS = 5


intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
)

def deezerinfo(ctx):
    """
    Input : Deezer link
    Output : the artist name, the title and what type is it"""
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
        title = text["title"]
        what = "album"
    if "track" in apilink:
        artist = text["artist"]["name"]
        title = text["title"]
        what = "track"
    if "artist" in apilink:
        artist=text["name"]
        what = "artist"
        title = text["name"]
    return artist, what, title

def getinfosfromspotifyapi(artist, what, title):
    client_credentials_manager = SpotifyClientCredentials(client_id=start.client_id, client_secret=start.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    if what == "track":
        results = sp.search(q='track:' + title + ' artist:' + artist, type=what)
        #returns the name of the name of the track, the name of the artist, the name of the album, the link to the album cover, the link to the track, the link to the artist
        infos = {
            "name": results["tracks"]["items"][0]["name"], 
            "artist": results["tracks"]["items"][0]["artists"][0]["name"], 
            "album": results["tracks"]["items"][0]["album"]["name"], 
            "cover": results["tracks"]["items"][0]["album"]["images"][0]["url"], 
            "link": results["tracks"]["items"][0]["external_urls"]["spotify"], 
            "artistlink": results["tracks"]["items"][0]["artists"][0]["external_urls"]["spotify"], 
            "type": results["tracks"]["items"][0]["type"],
            "artistcover": sp.artist(results["tracks"]["items"][0]["artists"][0]["id"])["images"][0]["url"],
            "date": results["tracks"]["items"][0]["album"]["release_date"]
        }
        return infos
    if what == "album":
        results = sp.search(q='album:' + title + ' artist:' + artist, type="album")
        infos = {
            "name": results["albums"]["items"][0]["name"], 
            "artist": results["albums"]["items"][0]["artists"][0]["name"], 
            "cover": results["albums"]["items"][0]["images"][0]["url"], 
            "link": results["albums"]["items"][0]["external_urls"]["spotify"], 
            "artistlink": results["albums"]["items"][0]["artists"][0]["external_urls"]["spotify"],
            "type": results["albums"]["items"][0]["type"],
            "artistcover": sp.artist(results["albums"]["items"][0]["artists"][0]["id"])["images"][0]["url"],
            "date": results["albums"]["items"][0]["release_date"]
        }
        return infos
    if what == "artist":
        results = sp.search(q='artist:' + artist, type="artist")
        print(results)
        #returns the name of the artist, the link to the artist's image, the link to the artist's page on spotify,  the number of followers of the artist
        infos = {
            "name": results["artists"]["items"][0]["name"], 
            "cover": results["artists"]["items"][0]["images"][0]["url"], 
            "link": results["artists"]["items"][0]["external_urls"]["spotify"], 
            "followers": results["artists"]["items"][0]["followers"]["total"],
            "type": results["artists"]["items"][0]["type"],
            "artistcover": results["artists"]["items"][0]["images"][0]["url"]
        }
        return infos

def waiting(ctx):
    """
    The bot give a fact about music to the utilisator while he is looking for the informations about the music
    """
    e = discord.Embed(
        title="While I'm looking for the informations about the music, here a fact about music : ",
        description=start.facts[np.random.randint(0, len(start.facts))],
        color=0x00ff00)


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


bot = discord.Bot(activity=discord.Game(name='Finding your music ! Find commands with /help'), intents=intents)

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

@bot.slash_command(guild_ids=[694443902526029854], name="deezer", description="Let's find some Deezer Music !")
async def deezer(ctx, link):
    e = discord.Embed(
        title="While I'm looking for the informations about the music, here a fact about music : ",
        description=start.facts[np.random.randint(0, len(start.facts))],
        color=0x00ff00)
    await ctx.respond(content="I'm looking for the informations about the music, please wait", embed=e)
    print(deezerinfo(link))
    infos = getinfosfromspotifyapi(*(deezerinfo(link)))
    if "album" in deezerinfo.link:
        print(link)
        print(infos["cover"])
        e = discord.Embed(
            color = covercolor(infos["cover"]),
            )
        e.add_field(
            name="Album name",
            value=infos["name"],
            inline= False
        )
        e.set_thumbnail(url=infos["cover"])
        e.add_field(
            name="Listen it here :",
            value=f"[Deezer]({deezerinfo.link}) \n [Spotify]({infos['link']})"
        )
        e.add_field(
            name="Release date",
            value =infos["date"]
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name="By " + infos["artist"], icon_url=(infos["artistcover"]))
    elif "track" in deezerinfo.link:
        print(infos["cover"])
        e = discord.Embed(
            color = covercolor(infos["cover"]),
            )
        e.add_field(
            name="Title",
            value=infos["name"],
            inline=False
        )
        e.add_field(
            name="Album name",
            value=infos["album"],
            inline= True
        )
        e.add_field(
            name="Release date",
            value =infos["date"],
            inline=True
        )
        e.set_thumbnail(url=infos["cover"])
        e.add_field(
            name="Listen it here :",
            value=f"[Deezer]({deezerinfo.link}) \n [Spotify]({infos['link']})"
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name= f"By " + infos["artist"], icon_url=(infos["artistcover"]))
    elif "artist" in deezerinfo.link:
        print(infos["cover"])
        e = discord.Embed(
            color = covercolor(infos["cover"]),
            )
        e.add_field(
            name="Artist",
            value=infos["name"],
            inline=False
        )
        e.add_field(
            name="Number of fans on Spotify",
            value=infos["followers"],
            inline= True
        )
        e.set_thumbnail(url=infos["cover"])
        e.add_field(
            name="Listen it here :",
            value=f"[Deezer]({deezerinfo.link}) \n [Spotify]({infos['link']})"
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name=infos["name"], icon_url=(infos["artistcover"]))
    time.sleep(1)
    await ctx.edit(content="", embed=e)

@bot.slash_command(name='greet', description='Greet someone!', guild_ids=[694443902526029854])
async def greet(ctx, name=''):
    await ctx.respond(f'Hello {name}!')

@bot.slash_command(name='help', description='Get help about the bot', guild_ids=[694443902526029854])
async def help(ctx):
    e = discord.Embed(
        color = discord.Colour.blue(),
        title = "Help",
        description="Here is the list of commands you can use with the bot :")
    e.add_field(
        name="/help",
        value="Get the list of commands you can use with the bot",
        inline=False
    )
    e.add_field(
        name="/deezer",
        value="Let's find some Deezer Music ! Enter a link to a Deezer album or a Deezer track, and the bot will send you the informations about it.",
        inline=False
    )
    e.add_field(
        name="/greet",
        value="Greet someone! Enter the name of the person you want to greet, and the bot will greet you. (yeah it's a test)",
        inline=False
    )
    e.set_author(name=f"By {pverte}", icon_url=pverte.avatar)
    time.sleep(4)
    await ctx.respond(embed=e)
bot.run(start.token)