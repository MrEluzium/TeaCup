from discord import Embed


def cup_embed(title, description, url=None):
    emb = Embed(title=title, url=url,
                description=description,
                color=0x0df7e6).set_footer(text="teacup")
    return emb


def queue_cup_embed(queue):
    if not queue:
        return cup_embed(title='No queue at this moment', description='Use -play to add more :D')
    else:
        final = ""
        iteration = 1
        for data in queue:
            video_url, title, duration, author = data['video_url'], data['title'], data['duration'], data['author']
            order = ['Now', 'Next'][iteration - 1] if iteration < 3 else iteration
            final += f"{order}) [{title}]({video_url}) [{author}]\n\n"
            iteration += 1
        emb = Embed(title="",
                    description=final,
                    color=0x0df7e6)
        emb.set_author(name="Queue")
        emb.set_footer(text="teacup")
        return emb
