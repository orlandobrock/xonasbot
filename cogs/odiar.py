import sqlite3
import discord
import random
from datetime import datetime, timedelta

from discord.ext import commands
# from cogs.message import randomic

from cogs.start import connect_database

class Mensagem(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.command(name='odiar', description='Ganha seus HJCOIN (Hate Jonas Coin). Pode ser usado uma vez por dia!')
    async def odiar(self, ctx):
        if verifica_user(ctx.author.id) == 0:
            cadastrar_usuario(ctx.author.id)
        if not(valida_resgate(ctx.author.id)):
            sorteio = aumentar_odio(ctx.author.id)
            embedVar = discord.Embed(title="", description=f"Você resgatou {sorteio} HJCOIN :coin: ", color=0x00ff00)
            await ctx.reply(embed=embedVar)
        else:
            embedVar = discord.Embed(title="", description="Você já resgatou os seus HJCOIN hoje :coin: ", color=0x00ff00)
            await ctx.reply(embed=embedVar)
            

def verifica_user(id): #verifica se existe o usuario no banco ctx.author.id
    banco = connect_database()
    cursor = banco.cursor()
    cursor.execute(f"SELECT id FROM usuarios where id = '{id}'")
    return len(cursor.fetchall())
    banco.close()

def aumentar_odio(id, resgate = datetime.now(), sorteio = random.randint(1, 2)):
     banco = connect_database()
     cursor = banco.cursor()
     cursor.execute(f"UPDATE odiar_points SET pontos = (select pontos FROM odiar_points where id_usuario = {id})+{sorteio}, ultimo_resgate = '{resgate}' WHERE id_usuario = {id}")
     banco.commit()
     banco.close()
     return sorteio

def cadastrar_usuario(id):
     banco = connect_database()
     cursor = banco.cursor()
     cursor.execute(f"INSERT INTO usuarios (id) VALUES ({id})")
     banco.commit()
     cursor.execute(f"INSERT INTO odiar_points (id_usuario, pontos) VALUES ({id}, 0)")
     banco.commit()
     banco.close()

def valida_resgate(id):
    banco = connect_database()
    cursor = banco.cursor()
    cursor.execute(f'SELECT ultimo_resgate FROM odiar_points where id_usuario = {id}')
    resgate = cursor.fetchone()[0]
    if(resgate is None):
        print('passou')
        return False
    else:
        resgatado = datetime.strptime(resgate, "%Y-%m-%d %H:%M:%S.%f")
        hora_resgate = resgatado + timedelta(days=1)
        if hora_resgate > datetime.now():
            return True
        else:
            return False

def randomic(chance):
    return round(random.randint(1, (1/chance) * 100))

def setup(client):
    client.add_cog(Mensagem(client))