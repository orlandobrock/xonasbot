import discord
from discord.ext import commands
import youtube_dl
from youtube_search import YoutubeSearch
import asyncio
import validators

class Music(commands.Cog):    
    def __init__(self, client):
        self.client = client
        self.song_list = []
        self.repeat = False,
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'preferredcodec': 'mp3',
            'quiet': True,
            'warnings': 'no-warnings',
            'cookiefile': 'cookies.txt',
            "extract_flat": "in_playlist"
        }

    @commands.command(name='stop', description='Parar a musica e limpar a lista de reprodução.')
    async def stop(self, ctx):
        if ctx.voice_client is None or ctx.author.voice is None:
            await ctx.send('Você não pode fazer isso agora', delete_after=5)
        else:
            ctx.voice_client.resume()
            self.song_list = []
            embedVar = discord.Embed(title="", description="Reprodução interrompida e lista de reprodução limpa", color=0xd16079)
            await ctx.send(embed=embedVar, delete_after=5)
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            else: 
                await ctx.send('O Jonas não está em nenhuma canal de voz')
    

    @commands.command(name='skip', description='Pular a musica atual')
    async def skip(self, ctx):
        if ctx.voice_client is None or ctx.author.voice is None:
            await ctx.send('Você não pode fazer isso agora', delete_after=5)
        else:
            ctx.voice_client.pause()
            embedVar = discord.Embed(title="", description=f"Pulando para a proxima música {self.song_list[1].get('title')}", color=0x84a8c2)
            await ctx.send(embed=embedVar)
            await self.play_next(ctx)

    async def join_vc(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Você não está em uma canal de voz", delete_after=5)
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

    @commands.command(name='repeat', description='Ativar repetição de musica (instavel, recomendo não usar por enquanto)')
    async def repeat(self, ctx):
        if self.repeat:
            self.repeat = False
            embedVar = discord.Embed(title="", description=f"Modo repetição ativado", color=0x00ff00)
        else:
            self.repeat = True
            embedVar = discord.Embed(title="", description=f"Modo repetição desativado", color=0x00ff00)
        await ctx.send(embed=embedVar)

    @commands.command(name='play', description='Tocar musica. !play [URL|Nome da musica]. Só funciona com música do **YOUTUBE** por enquanto.')
    async def play(self, ctx, *, url):
        await self.join_vc(ctx)
        vc = ctx.voice_client

        if not(validators.url(url)):
            url = YoutubeSearch(url).to_dict()[0].get('id')

        await self.add_songs(ctx, self.get_info(url))
        if not vc.is_playing():
            vc.play(discord.FFmpegOpusAudio(self.get_stream(self.song_list[0]), before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=lambda e:asyncio.run_coroutine_threadsafe(self.play_next(ctx),self.client.loop))
            embedVar = discord.Embed(title="**Tocando agora**", description=f"{self.song_list[0].get('title')}", color=0xbdbdbd)
            await ctx.send(embed=embedVar)
    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
                await ctx.send("Por Favor insira o [Nome da musica | URL]", delete_after=5)



    async def play_next(self, ctx):
        vc = ctx.voice_client
        if len(self.song_list) > 1 or self.repeat and len(self.song_list) >=1:
            if not self.repeat:
                pass
            else: 
                del self.song_list[0]
            vc.play(discord.FFmpegOpusAudio(self.get_stream(self.song_list[0]), before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=lambda e:asyncio.run_coroutine_threadsafe(self.play_next(ctx),self.client.loop))
        else:
            if not vc.is_playing():
                asyncio.run_coroutine_threadsafe(vc.disconnect(), self.client.loop)
                asyncio.run_coroutine_threadsafe(ctx.send("Sem musicas na lista de reprodução", delete_after=5), self.client.loop) 
            
    def get_stream(self, url):
        if url.get('type') == 'playlist':
            with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url.get('url'), download=False)
                return info['formats'][0]['url']
        else:
            return url.get('url')

    def get_info(self, query):
        try:
            with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(query, download=False)
        except youtube_dl.utils.ExtractorError:
            self.get_info(query)
            print('ta dando erro porra')
        return info

    async def add_songs(self, ctx, info):
        if info.get('_type') == 'playlist':
            i = 1
            for i,entry in enumerate(info.get("entries"), start=1):
                self.song_list.append({"title": entry.get('title'),"type": "playlist", "playlist_name": info.get('title'),'url': entry.get('id')})
            embedVar = discord.Embed(title="", description=f"Foram adicionadas {i} na queue: {self.song_list[len(self.song_list)-1].get('playlist_name')}", color=0xf5ec78)
            await ctx.send(embed=embedVar)
        else:
            self.song_list.append({"title": info['title'], "type": "video","url": info['formats'][0]['url']})
            embedVar = discord.Embed(title="", description=f"Musica {self.song_list[len(self.song_list)-1].get('title')} adicionada a lista de reprodução", color=0xf5ec78)
            await ctx.send(embed=embedVar)

    @commands.command(name='pause', description='Pausa a música atual.')
    async def pause(self, ctx):
        if ctx.voice_client is None or ctx.author.voice is None:
            await ctx.send('Você não pode fazer isso agora', delete_after=5)
        else:
            ctx.voice_client.pause()
            embedVar = discord.Embed(title="", description=f"**Pausado**", color=0x00ff00)
            await ctx.send(embed=embedVar)
        
    @commands.command(name='resume', description='Retoma a musica.')
    async def resume(self, ctx):
        if ctx.voice_client is None or ctx.author.voice is None:
            await ctx.send('Você não pode fazer isso agora', delete_after=5)
        else:
            ctx.voice_client.resume()
            embedVar = discord.Embed(title="", description=f"**Reproduzindo**", color=0x00ff00)
            await ctx.send(embed=embedVar, delete_after=5)

def setup(client):
    client.add_cog(Music(client))