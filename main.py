#Imports of the necessary libraries requests for web resquest, discord for the discord bot, json for formatting the informations received by the api
import requests
import discord
from discord.ext import commands
import json
#For the color of the embed depending of the cover of the music
from io import BytesIO
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import binascii
from PIL import Image

import miscs #import miscs file with the facts, and the errors codes
import time
import spotipy #import spotipy module for the spotify api
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv #To import the token of the bot
import os #For acessing files
import sys

load_dotenv() #load the token of the bot
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
NUM_CLUSTERS = 5 #Number of colors to be extracted from the cover
user_admin_id = 577089415369981952 #The id of the admin, can be changed

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET) #acess to the credentials for spotify api
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

intents = discord.Intents( #Discord intents
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
    if "deezer" not in ctx:
        print("bad link")
        return 1, "wrong-link-deezer", "", "deezer"
    apilink = ctx.split("/")[-2:]
    apilink = "https://api.deezer.com/" + apilink[0] + "/" + apilink[1]
    print(apilink)
    informations = requests.get(apilink)
    text = informations.json()
    if "error" in text:
        print("Error in the link")
        return 1, text["error"]["code"], "", "deezer"
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
    return artist, what, title, "deezer"

def deezerlink(name, what, title):
    """
    Input : the artist name, the title and what type is it
    Output : the link of the music
    """
    if what == "artist":
        link = "https://www.deezer.com/search?q=" + name
    else:
        link = "https://www.deezer.com/search?q=" + name + " " + title
    return link

def spotifyinfo(ctx):
    """
    Input : Spotify link
    Output : the artist name, the title and what type is it"""
    if "?" in ctx:
        ctx = ctx.split("?", 1)[0]
    print(ctx)
    if "spotify" not in ctx:
        print("bad link")
        return 1, "wrong-link-spotify", "", "spotify"
    if "album" in ctx:
        requests = sp.album(ctx)
        artist = requests["artists"][0]["name"]
        title = requests["uri"].split("/")[-1]
        what = "album"
    if "track" in ctx:
        requests = sp.track(ctx)
        artist = requests["artists"][0]["name"]
        title = requests["uri"].split("/")[-1]
        what = "track"
    if "artist" in ctx:
        requests = sp.artist(ctx)
        artist = requests["uri"].split("/")[-1]
        what = "artist"
        title = ""
    spotifyinfo.link=requests["external_urls"]["spotify"]
    return artist, what, title, "spotify"



def getinfosfromspotifyapi(artist, what, title, platform):
    if artist==1:
        print("Received the error " + str(what) + " From " + platform)
        return {"error": what}
    if what == "track":
        if platform == "spotify":
            results=sp.track(title)
            infos= {
                "name": results["name"],
                "artist": results["artists"][0]["name"],
                "album": results["album"]["name"],
                "cover": results["album"]["images"][0]["url"],
                "link": results["external_urls"]["spotify"],
                "artistlink": results["artists"][0]["external_urls"]["spotify"],
                "type": "track",
                "artistcover": results["album"]["images"][0]["url"],
                "date": results["album"]["release_date"]
            }
        else:
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
        if platform == "spotify":
            results=sp.album(title)
            infos= {
                "name": results["name"],
                "artist": results["artists"][0]["name"],
                "cover": results["images"][0]["url"],
                "link": results["external_urls"]["spotify"],
                "artistlink": results["artists"][0]["external_urls"]["spotify"],
                "type": results["type"],
                "artistcover": sp.artist(results["artists"][0]["id"])["images"][0]["url"],
                "date": results["release_date"]

            }
        else:
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
        if platform == "spotify":
            results=sp.artist(artist)
        else:
            results = sp.search(q='artist:' + artist, type="artist")
        print(results)
        #returns the name of the artist, the link to the artist's image, the link to the artist's page on spotify,  the number of followers of the artist
        
        if platform == "spotify":
            infos = {
                "name": results["name"], 
                "link": results["external_urls"]["spotify"], 
                "followers": results["followers"]["total"], 
                "type": results["type"],
                "cover": results["images"][0]["url"]
            }
        else:
            infos = {
                "name": results["artists"]["items"][0]["name"], 
                "link": results["artists"]["items"][0]["external_urls"]["spotify"], 
                "followers": results["artists"]["items"][0]["followers"]["total"], 
                "type": results["artists"]["items"][0]["type"],
                "cover": results["artists"]["items"][0]["images"][0]["url"]
            }
        return infos

def waiting(ctx):
    """
    The bot give a fact about music to the utilisator while he is looking for the informations about the music
    """
    e = discord.Embed(
        title="While I'm looking for the informations about the music, here a fact about music : ",
        description=miscs.facts[np.random.randint(0, len(miscs.facts))],
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


bot = discord.Bot(command_prefix='aa', intents=intents)

@bot.event
async def on_ready():
    global pverte, errorschan
    pverte = bot.get_user(user_admin_id)
    errorschan = bot.get_channel(963776434428592198)
    print(f'We have logged in as {bot.user}')
    await errorschan.send("Je suis prêt !")
    #while True:
    print("updated the number of servers to " + str(len(bot.guilds)))
    await bot.change_presence(activity=discord.Game(name='Version 0.2 || Finding your music ! Find commands with /help | '+ str(len(bot.guilds)) + " servers"))
        #await time.sleep(3600)
@bot.event
async def on_application_command_error(ctx, error):
    """
    Send an error message telling the message that triggerer the error and the error itself into the errorschan
    """
    if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title=f"Slow it down !",description=f"Try again in {error.retry_after:.2f}s.", color=discord.Color.red())
            await ctx.send(embed=em)
            return
    if isinstance(error, spotipy.client.SpotifyException):
        if error.http_status == 401 or 403:
            await ctx.send("Oops token issue, please tell Pverte to fix it.")
            return
        if error.http_status == 404:
            await ctx.send("This music doesn't exist.")
            return
        if error.http_status == 429:
            await ctx.send("You're doing too much. Try again in a few seconds.")
            return
        if error.http_status == 500 or 502 or 503 or 504:
            await ctx.send("The server is down. Try again later.")
            return
    e = discord.Embed(
    color = discord.Colour.red(),
    title = "Error",
    description="AN ERROR JUST OCCURED, IT HAS BEEN SENT TO THE DEVELOPERS.")
    e.set_footer(text="Pverte don't know how to code, always making errors, I did anything it's his fault.")
    await errorschan.send(f"<@user_admin_id> an error just occured with the command {ctx.command} : {error}")
    await ctx.edit(embed=e)

@commands.cooldown(1, 10, commands.BucketType.user)
@bot.slash_command(name="deezer", description="Let's find some Deezer Music !")
async def deezer(ctx, link):
    e = discord.Embed(
        title="While I'm looking for the informations about the music, here a fact about music : ",
        description=miscs.facts[np.random.randint(0, len(miscs.facts))],
        color=0x00ff00)
    await ctx.respond(content="I'm looking for the informations about the music, please wait", embed=e)
    print(deezerinfo(link))
    infos = getinfosfromspotifyapi(*(deezerinfo(link)))
    if "error" in infos:
        file = discord.File("error.png")
        print("hey error !")
        errcode = infos["error"]
        e= discord.Embed(
        title="Error",
        description="Error : "+str(errcode)+", "+miscs.error[errcode],
        color=discord.Colour.red())
        e.set_thumbnail(url="attachment://error.png")
        await ctx.edit(file=file, content="An error just occured :", embed=e)
        return
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
        e.set_author(name=infos["name"], icon_url=(infos["cover"]))
    time.sleep(1)
    await ctx.edit(content="", embed=e)

@commands.cooldown(1, 10, commands.BucketType.user)
@bot.slash_command(name="spotify", description="Let's find some Spotify Music !")
async def spotify(ctx, link):
    print("Entered the spotify function")
    e = discord.Embed(
        title="While I'm looking for the informations about the music, here a fact about music : ",
        description=miscs.facts[np.random.randint(0, len(miscs.facts))],
        color=0x00ff00)
    await ctx.respond(content="I'm looking for the informations about the music, please wait", embed=e)
    info = getinfosfromspotifyapi(*(spotifyinfo(link)))
    if "error" in info:
        file = discord.File("error.png")
        print("hey error !")
        errcode = info["error"]
        e= discord.Embed(
        title="Error",
        description="Error : "+str(errcode)+", "+miscs.error[errcode],
        color=discord.Colour.red())
        e.set_thumbnail(url="attachment://error.png")
        await ctx.edit(file=file, content="An error just occured :", embed=e)
        return
    if "album" in spotifyinfo.link:
        print(link)
        print(info["cover"])
        e = discord.Embed(
            color = covercolor(info["cover"]),
            )
        e.add_field(
            name="Album name",
            value=info["name"],
            inline= False
        )
        e.set_thumbnail(url=info["cover"])
        e.add_field(
            name="Listen it here :",
            value=f"[Spotify]({spotifyinfo.link})"
        )
        e.add_field(
            name="Release date",
            value =info["date"]
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name="By " + info["artist"], icon_url=(info["artistcover"]))
    elif "track" in spotifyinfo.link:
        print(info["cover"])
        e = discord.Embed(
            color = covercolor(info["cover"]),
            )
        e.add_field(
            name="Title",
            value=info["name"],
            inline=False
        )
        e.add_field(
            name="Album name",
            value=info["album"],
            inline= True
        )
        e.add_field(
            name="Release date",
            value =info["date"],
            inline=True
        )
        e.set_thumbnail(url=info["cover"])
        e.add_field(
            name="Listen it here :",
            value=f"[Spotify]({spotifyinfo.link})",
            inline=False
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name= f"By " + info["artist"], icon_url=(info["artistcover"]))
    elif "artist" in spotifyinfo.link:
        print(info["cover"])
        e = discord.Embed(
            color = covercolor(info["cover"]),
            )
        e.add_field(
            name="Artist",
            value=info["name"],
            inline=False
        )
        e.add_field(
            name="Number of fans on Spotify",
            value=info["followers"],
            inline= True
        )
        e.set_thumbnail(url=info["cover"])
        e.add_field(
            name="Listen it here :",
            value=f"[Spotify]({spotifyinfo.link})",
            inline=False
        )
        e.add_field(
            name="\u200B",
            value="Bot by [Pverte](https://pverte.me)",
            inline=False
        )
        e.set_author(name=info["name"], icon_url=(info["cover"]))
    time.sleep(4)
    await ctx.edit(content="", embed=e)

@commands.cooldown(1, 10, commands.BucketType.user)
@bot.slash_command(name='help', description='Get help about the bot')
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
    e.add_field(
        name="/spotify",
        value="Let's find some Spotify Music ! Enter a link to a Spotify album or a Spotify track, and the bot will send you the informations about it.",
        inline=False
    )
    e.add_field(
        name="/invite",
        value="Invite the bot to your server !",
        inline=False
    )
    e.set_author(name=f"By {pverte}", icon_url=pverte.avatar)

    await ctx.respond(embed=e)

@commands.cooldown(1, 10, commands.BucketType.user)
@bot.slash_command(name="invite", description="Get the link to invite the bot to your server")
async def invite(ctx):
    e = discord.Embed(
        color = discord.Colour.blue(),
        title = "Invite the bot to your server",
        description="Here is the link to invite the bot to your server :")
    e.add_field(
        name="Invite the bot to your server",
        value=f"[Invite the bot to your server](https://discordapp.com/oauth2/authorize?client_id={bot.user.id}&permissions=2147609600&scope=bot%20applications.commands)",
        inline=False
    )
    e.set_author(name=f"By {pverte}", icon_url=pverte.avatar)
    await ctx.respond(embed=e)

@commands.cooldown(1, 10, commands.BucketType.user)
@bot.command(name="broadcast", description="Broadcast a message to all the servers the bot is in", guild_ids=[694443902526029854])
async def broadcast(ctx, *, message, color="52152219"):
    """In case the user want to change the color of the embed, he can add a color code after the message"""
    color1 = int(color[0:2], 16) #more readable
    color2 = int(color[2:5], 16) #same
    color3 = int(color[5:7], 16) #same
    sucess = 0 #number of servers the bot has sent the message to
    if ctx.author.id == user_admin_id: #if the user is the admin
        print("Broadcast en cours avec en message : " + message)
        """Broadcast a message to all the servers the bot is in. Command only for Pverte"""
        for guild in bot.guilds:
            print("Envoi du message à " + guild.name)
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text:
                    try:
                        e = discord.Embed(
                            color = discord.Color.from_rgb(color1, color2, color3),
                            title = "Announcement from Pverte !",
                            description=message
                        )
                        e.set_author(name=f"Message from Pverte  !", icon_url=pverte.avatar)
                        e.set_footer(text=f"If you want to disable these announcements, use the command /settings disable-announcements")
                        await channel.send(embed=e)
                        print("Message envoyé à " + guild.name + " dans le channel " + channel.name + " Success !")
                        sucess = sucess + 1
                    except Exception as e: 
                        print(e)
                        continue
                    else:
                        break
        await ctx.respond(f"{sucess} message(s) envoyé(s) !")

bot.run(TOKEN) # Run the bot