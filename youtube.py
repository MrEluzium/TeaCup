import youtube_dl
import asyncio
from cup_embed import cup_embed
from youtube_search import YoutubeSearch
from validators import url as is_url

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(params=ytdl_format_options)


async def get_music_url(url, ctx):
    searched_url = None
    try:
        for i in range(3):
            if not is_url(url):
                result = YoutubeSearch(url, max_results=3).to_dict()[0]['url_suffix']
                print(result)
                searched_url = f"https://www.youtube.com{result}"
            final_url = searched_url if searched_url else url
            print(final_url)
            loop = asyncio.get_event_loop()
            try:
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=final_url, download=False))
                break
            except youtube_dl.utils.DownloadError:
                i += 1
        return {'url': data['url'],
                'video_url': final_url,
                'title': data['title'],
                'duration': data['duration'],
                'author': ctx.author.mention}
    except IndexError:
        emb = cup_embed(title="There is a problem :(",
                        description=f"Sorry, I can't find {url}.")
        await ctx.send(embed=emb, delete_after=5)
        if ctx.message:
            await asyncio.sleep(5)
            await ctx.message.delete()
