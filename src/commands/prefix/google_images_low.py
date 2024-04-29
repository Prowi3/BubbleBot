import discord
import requests
import urllib.parse
import random
import json
from bs4 import BeautifulSoup
from discord.ext import commands

sent_image_links = []

def get_image_links(search_query, max_images=10):
    search_query_encoded = urllib.parse.quote(search_query)
    search_url = f"https://www.google.com/search?q={search_query_encoded}&tbm=isch&safe=active"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(search_url, headers=headers)
    image_links = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        div_tags = soup.find_all("div", class_="rg_meta")

        for div_tag in div_tags:
            metadata = json.loads(div_tag.text)
            if "ou" in metadata:
                image_links.append(metadata["ou"])

    return image_links[:max_images]

@commands.command(name="ser", aliases=["search"])
async def google_images_low(ctx, *, search_query: str):
    image_links = get_image_links(search_query)

    if image_links:
        selected_image_link = random.choice(image_links)
        sent_image_links.append(selected_image_link)

        search_query_decoded = urllib.parse.unquote(search_query)
        embed = discord.Embed(color=0x9FC6F6, title=f"You searched for: {search_query_decoded}")
        embed.set_image(url=selected_image_link)

        await ctx.send(embed=embed)
    else:
        await ctx.send("No suitable images found.")

def setup(bot):
    bot.add_command(google_images_low)
