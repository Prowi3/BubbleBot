import discord
from discord.ext import commands
import httpx
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
from noise import pnoise2
import random
import math

fonts = ['Roboto-Black', 'SpaceMono-Regular', 'SpaceMono-Bold', 'DancingScript-Bold', 'Rubik-Bold', 'Arial-Black']
is_rendering = False

class DrawNoise(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="draw_noise", description='Draw an image using Noise')
    async def draw_noise(self, ctx: discord.ApplicationContext,
        font: discord.Option(str, choices=fonts) = None, *, text: str = '', octaves: int = 1, lacunarity: float = 5.0, persistence: float = 0.5):
        global is_rendering
        
        if is_rendering:
            await ctx.send("Sorry, an image is already being rendered.")
            return
        
        is_rendering = True
        
        await ctx.defer()
        
        try:
            width, height = 1080, 1080
            gradient_image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(gradient_image)
            
            scale = 300.0
            hue_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            offset_x = random.uniform(0, 1000)
            offset_y = random.uniform(0, 1000)
            
            x_coords = np.arange(width) + offset_x
            y_coords = np.arange(height) + offset_y
            x_coords, y_coords = np.meshgrid(x_coords, y_coords)
            
            pnoise2_vectorized = np.vectorize(pnoise2)
            noise_values = pnoise2_vectorized(x_coords / scale, y_coords / scale, octaves = octaves, persistence = persistence, lacunarity = lacunarity, repeatx=1024, repeaty=1024, base=1)
            
            r, g, b = hue_color
            r_values = np.clip(r + noise_values * 100, 0, 255).astype(np.uint8)
            g_values = np.clip(g + noise_values * 100, 0, 255).astype(np.uint8)
            b_values = np.clip(b + noise_values * 100, 0, 255).astype(np.uint8)
            rgb_values = np.stack([r_values, g_values, b_values], axis=-1)
            gradient_image = Image.fromarray(rgb_values)

            if text:
                draw = ImageDraw.Draw(gradient_image)
                font_size = int(math.sqrt(width * height) / len(text)) + 25
                font_path = f"miscellaneous/Fonts/{font}.ttf"
                font = ImageFont.truetype(font_path, font_size)
                text_width, text_height = draw.textsize(text, font=font)
                x = round((width - text_width) / 2) + 1
                y = round((height - text_height) / 2) + 2
                text_image = Image.new('RGB', (width, height))
                text_draw = ImageDraw.Draw(text_image)
                text_draw.text((x, y), text=text, fill=(255, 255, 255), font=font)

                gradient_image = ImageChops.soft_light(gradient_image, text_image)
                
            await ctx.respond("Here's your image.")
            gradient_image.save('gradient.png')
            await ctx.send(file=discord.File('gradient.png'))
            is_rendering = False
        
        except Exception as e:
            is_rendering = False
            await ctx.respond(f"An error occurred: {str(e)}")

def setup(bot):
    bot.add_cog(DrawNoise(bot))