import discord
import asyncio
from cup_embed import cup_embed, queue_cup_embed
from discord.ext import tasks, commands
from youtube import get_music_url
from settings import TOKEN
from os import name as os_name
guild_data = {'pattern': {'queue': [], 'msg': {'now': None, 'queue:': None}}}

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


async def set_activity():
    activities = ['#StayHome', f'on {len(bot.guilds)} servers!', 'Cake is a lie!']
    cur_activity = discord.Game(activities[0])
    await bot.change_presence(status=discord.Status.online, activity=cur_activity)


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
    await set_activity()
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        await on_guild_join(guild)


@bot.event
async def on_reaction_add(reaction, user):
    if user and reaction.me:
        await play_next(reaction.message)


@bot.command(name='play', aliases=['p'])
async def play(ctx, *text):
    text = ' '.join(text)
    if await connect(ctx):
        await add_queue(ctx, text)


@bot.command(name='connect', aliases=['join'])
async def connect(ctx):
    voice = ctx.guild.voice_client
    if voice and ctx.author.voice:
        await voice.move_to(ctx.author.voice.channel)
    elif ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        emb = cup_embed(title="There is a problem :(",
                        description="You must join the voice channel first.")
        await ctx.send(embed=emb, delete_after=5)
        if ctx.message:
            await asyncio.sleep(5)
            await ctx.message.delete()
        return False
    return True


@bot.command(name='disconnect', aliases=['leave'])
async def disconnect(ctx):
    if ctx.message:
        await ctx.message.delete()
    voice = ctx.guild.voice_client
    if voice:
        await voice.disconnect()


# @bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    try:
        if guild_data[ctx.guild.id]['msg']['queue']:
            await guild_data[ctx.guild.id]['msg']['queue'].delete()
            guild_data[ctx.guild.id]['msg']['queue'] = None
        emb = queue_cup_embed(guild_data[ctx.guild.id]['queue'])
    except KeyError:
        await guild_data_setup(ctx)
        emb = queue_cup_embed(guild_data[ctx.guild.id]['queue'])

    msg_queue = await ctx_message_send(ctx, embed=emb)
    guild_data[ctx.guild.id]['msg']['queue'] = msg_queue


@bot.command(name='stop', aliases=['s'])
async def stop(ctx):
    if ctx.message:
        await ctx.message.delete()
    if ctx.guild.voice_client.is_playing():
        ctx.guild.voice_client.stop()


async def add_queue(ctx, text):
    global guild_data

    data = await get_music_url(text, ctx)
    if data:
        video_url, title, duration, author = data['video_url'], data['title'], data['duration'], data['author']
        try:
            guild_data[ctx.guild.id]['queue'].append(data)
        except KeyError:
            await guild_data_setup(ctx)
            guild_data[ctx.guild.id]['queue'].append(data)
        if ctx.message:
            await ctx.message.delete()
        if len(guild_data[ctx.guild.id]['queue']) == 1:
            await play_next(ctx)
        else:
            emb = cup_embed(title="Queued",
                            url=video_url,
                            description=f"{title} [{author}]")
            await ctx.send(embed=emb, delete_after=4)
            await queue(ctx)


async def play_next(ctx):
    data = guild_data[ctx.guild.id]['queue'][0]
    url, video_url, title, duration, author = data['url'], data['video_url'], data['title'], data['duration'], data['author']
    if ctx.guild.voice_client:
        ctx.guild.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
        emb = cup_embed(title="Now playing",
                        url=video_url,
                        description=f"{title} [{author}]")
        msg_now = await ctx_message_send(ctx, embed=emb)
        guild_data[ctx.guild.id]['msg']['now'] = msg_now
        await queue(ctx)
    await asyncio.sleep(duration)

    guild_data[ctx.guild.id]['queue'].pop(0)
    await guild_data[ctx.guild.id]['msg']['now'].delete()
    if guild_data[ctx.guild.id]['msg']['queue']:
        await guild_data[ctx.guild.id]['msg']['queue'].delete()
        guild_data[ctx.guild.id]['msg']['queue'] = None
    if len(guild_data[ctx.guild.id]['queue']):
        msg_next = await ctx_message_send(ctx, 'playing next...', delete_after=1)
        await msg_next.add_reaction("\u23E9")


async def ctx_message_send(ctx, content=None, embed=None, delete_after=None):
    if type(ctx) is discord.message.Message:
        msg = await ctx.channel.send(content=content, embed=embed, delete_after=delete_after)
    else:
        msg = await ctx.send(content=content, embed=embed, delete_after=delete_after)
    return msg


async def guild_data_setup(ctx):
    global guild_data
    guild_data = {ctx.guild.id: {'queue': [], 'msg': {'now': None, 'queue': None}}}


async def voice_check(voice_client):
    if voice_client is None:
        await asyncio.sleep(90)
        if voice_client is None and voice_client.is_playing() is False and voice_client.is_paused() is False:
            await voice_client.disconnect()


bot.run(TOKEN)
