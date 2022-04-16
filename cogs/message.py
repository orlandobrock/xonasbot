import discord
import random
from discord.ext import commands
from cogs.start import connect_database

class Mensagem(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if str(message.author.id) == '418920478883708929':
            if randomic(10) == 1: #Chance do Jonas tomar uma foda-se
                add_foda()
                if randomic(50) == 1: #Chance de aparecer um video na hora do foda-se
                    await message.reply(file=discord.File('./video.mp4'))    
                else:
                    await message.reply("Foda-se Jonas")
                    
    @commands.command(name='foda', description='Prestação de contas de quantas vezes o Jonas tomou um foda-se.')
    async def foda(self, ctx):
        embedVar = discord.Embed(title="**Prestação de contas sobre foda-se Jonas**", description=f'**Jonas já tomou {get_contagem_foda_se()} foda-se :pray_tone1: **', color=0xd16079)
        await ctx.reply(embed=embedVar)


def randomic(chance):
    return round(random.randint(1, (1/chance) * 100))

def add_foda():
     banco = connect_database()
     cursor = banco.cursor()
     cursor.execute(f"UPDATE estatisticas SET contagem = (SELECT contagem from estatisticas) + 1 WHERE nome_estatistica = 'foda-se'")
     banco.commit()
     banco.close()

def get_contagem_foda_se():
     banco = connect_database()
     cursor = banco.cursor()
     cursor.execute(f"select contagem from estatisticas where nome_estatistica = 'foda-se' LIMIT 1")
     contagem = cursor.fetchone()
     return contagem[0]

def setup(client):
    client.add_cog(Mensagem(client))