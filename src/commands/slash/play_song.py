import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import shutil
import asyncio

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @commands.slash_command(name="play_song", description="Download and play a song from a YouTube URL")
    async def play_song(self, ctx: discord.ApplicationContext,
                        url: discord.Option(str, description="YouTube URL of the song to play"),
                        channel: discord.Option(discord.VoiceChannel, description="Select the Voice Channel that you want to play the song") = None, 
                        cancel: discord.Option(bool, description="Cancel the song that is Playing if any") = False):

        if channel is None:
            await ctx.respond("Please specify a voice channel.")
            return

        if cancel:
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.stop()
                await ctx.respond("Song canceled.")
            else:
                await ctx.respond("No song is currently playing.")
            return

        try:
            if self.voice_client is None or not self.voice_client.is_connected():
                self.voice_client = await channel.connect()

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'ffmpeg_location': shutil.which('ffmpeg'),
                'ffprobe_location': shutil.which('ffprobe'),
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = f"{info['title']}.mp3"

            source = discord.FFmpegPCMAudio(filename)
            self.voice_client.play(source)

            await ctx.respond(f"Bubble is playing {info['title']} in {channel.name}.")

            while self.voice_client.is_playing():
                await asyncio.sleep(1)

            await ctx.respond("Song finished playing.")

            await self.voice_client.disconnect()

        except Exception as e:
            await ctx.respond(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(Play(bot))
