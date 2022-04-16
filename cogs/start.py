from itertools import cycle
import sqlite3
import discord
from discord.ext import commands, tasks
import json

with open("misc/./mensagens.json", "r") as f:
    data = json.load(f)



status = cycle(data['status'])
update = data['update']


class Start(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Xonas bot está online!')
        self.change_status.start()
        banco = connect_database()

        if not(get_att_status(banco)):
            channel = self.client.get_channel(924043463857668128)
            embedVar = discord.Embed(title=update.get('title'), description=update.get('description'), color=0x00ff00)
            embedVar.set_thumbnail(url=update.get('thumb'))
            embedVar.add_field(name=update.get('name_notas'), value=update.get('notas'), inline=False) 
            embedVar.set_footer(text=update.get('cabecalho'))
            await channel.send(embed=embedVar)
            set_att_status(banco, True)

            

    @tasks.loop(minutes=60)
    async def change_status(self):
        await self.client.change_presence(activity=discord.Game(next(status)))


def connect_database():
    banco = sqlite3.connect('database/./banco.db')
    return banco

def get_att_status(banco):
    cursor = banco.cursor()
    cursor.execute("SELECT att_message from stats")
    return cursor.fetchall()[0][0]

def set_att_status(banco, status):
    cursor = banco.cursor()
    cursor.execute(f"UPDATE stats SET att_message = {status}")
    banco.commit()

def setup(client):
    client.add_cog(Start(client))