import youtube_dl
import asyncio
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


async def get_music_url(url):
    if not is_url(url):
        result = YoutubeSearch(url, max_results=1).to_dict()[0]['link']
        url = f'https://www.youtube.com{result}'
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=url, download=False))
    return {'url': data['url'], 'video_url': url, 'title': data['title']}
