from discord import Embed


def cup_embed(title, description, url=None):
    emb = Embed(title=title, url=url,
                description=description, color=0x0df7e6).set_footer(text="teacup")
    return emb