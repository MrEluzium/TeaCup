import discord
import asyncio
from discord import Embed
from discord.ext import commands
from youtube import get_music_url
from settings import TOKEN
from os import name as os_name

if os_name == 'nt':
    print('Boot on Windows. opus loaded automatically.')
else:
    discord.opus.load_opus('libopus.so')
    print('Boot on Linux. libopus.so loaded')

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -nostats -loglevel 0'
}

bot = commands.Bot(command_prefix='--')


@bot.event
async def on_guild_join(guild):
    print(
        f'\nJoined {guild.name}\n'
        f'ID: {guild.id}\n'
        f'Region: {guild.region}\n'
        f'Amount: {len(guild.members)}')


@bot.event
async def on_guild_remove(guild):
    print(
        f'\nRemoved {guild.name}'
        f' ID: {guild.id}'
        f' Amount: {len(guild.members)}')


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        await on_guild_join(guild)


@bot.command(name='play', aliases=['p'])
async def play(ctx, *text):
    text = ' '.join(text)
    await connect(ctx)
    try:
        data = await get_music_url(text)
        url, video_url, title = data['url'], data['video_url'], data['title']
        if ctx.guild.voice_client:
            ctx.guild.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
            emb = cup_embed(title="Now playng",
                                  url=video_url,
                                  description=f"{title} [{ctx.author.mention}]")
            await ctx.send(embed=emb)
            if not discord.opus.is_loaded():
                print('No opus loaded!')
    except IndexError:
        emb = cup_embed(title="There is a problem :(",
                        description=f"Sorry, I can't find {text}.")
        await ctx.send(embed=emb)


@bot.command(name='connect', aliases=['join'])
async def connect(ctx):
    voice = ctx.guild.voice_client
    if voice:
        await voice.move_to(ctx.author.voice.channel)
    elif ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        emb = cup_embed(title="There is a problem :(",
                        description="You must join the voice channel first.")
        await ctx.send(embed=emb)


@bot.command(name='loop')
async def loop(ctx):
    voice = ctx.guild.voice_client
    if voice:
        await ctx.send(type(voice.latency()))


@bot.command(name='stop', aliases=['s'])
async def stop(ctx):
    if ctx.guild.voice_client.is_playing():
        ctx.guild.voice_client.stop()


@bot.command(name='pause')
async def pause(ctx):
    if ctx.guild.voice_client.is_playing():
        ctx.guild.voice_client.pause()


@bot.command(name='resume')
async def resume(ctx):
    if ctx.guild.voice_client.is_paused():
        ctx.guild.voice_client.resume()


@bot.command(name='disconnect', aliases=['leave'])
async def disconnect(ctx):
    voice = ctx.guild.voice_client
    if voice:
        await voice.disconnect()


async def voice_check(voice_client):
    if voice_client is None:
        await asyncio.sleep(90)
        if voice_client is None and voice_client.is_playing() is False and voice_client.is_paused() is False:
            await voice_client.disconnect()


def cup_embed(title, description, url=None):
    emb = Embed(title=title, url=url,
                description=description, color=0x0df7e6).set_footer(text="teacup")
    return emb


async def get_channel(guild):
    print(guild.voice_client)
    # guild.me.voice.disconnect()
    # return guild.me.voice.channel

bot.run(TOKEN)
