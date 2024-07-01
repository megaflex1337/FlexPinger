import nextcord
from nextcord.ext import commands, tasks
from mcstatus import MinecraftServer
import asyncio
import json

print("    ███╗░░░███╗███████╗░██████╗░░█████╗░░██████╗████████╗░█████╗░████████╗██╗░░░██╗░██████╗")
print("    ████╗░████║██╔════╝██╔════╝░██╔══██╗██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║░░░██║██╔════╝")
print("    ██╔████╔██║█████╗░░██║░░██╗░███████║╚█████╗░░░░██║░░░███████║░░░██║░░░██║░░░██║╚█████╗░")
print("    ██║╚██╔╝██║██╔══╝░░██║░░╚██╗██╔══██║░╚═══██╗░░░██║░░░██╔══██║░░░██║░░░██║░░░██║░╚═══██╗")
print("    ██║░╚═╝░██║███████╗╚██████╔╝██║░░██║██████╔╝░░░██║░░░██║░░██║░░░██║░░░╚██████╔╝██████╔╝")
print("    ╚═╝░░░░░╚═╝╚══════╝░╚═════╝░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝░░░╚═╝░░░░╚═════╝░╚════╝░ ")
print("")
print("          github - https://github.com/megaflex1337     /      discord - megaflexgg              ")
print("")
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

TOKEN = config["TOKEN"]
CHANNEL_ID = config["CHANNEL_ID"]
CORRECT_CHANNEL_URL = config["CORRECT_CHANNEL_URL"]
UPDATE_INTERVAL = config["UPDATE_INTERVAL"]
SERVER_IP = config["SERVER_IP"]
ACTIVITY = config["ACTIVITY"]


intents = nextcord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix='%', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    activity = nextcord.Game(name=ACTIVITY)
    await bot.change_presence(activity=activity)

    update_server_status.start()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"Эту команду можно использовать только в канале: {CORRECT_CHANNEL_URL}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Команда не найдена.")
    else:
        await ctx.send(f"Произошла ошибка: {error}")


@bot.check
async def globally_block_dms(ctx):
    if ctx.guild is None:
        return True  
    return ctx.channel.id == CHANNEL_ID


@bot.command()
async def серв(ctx):
    await send_server_status(ctx.channel)


async def send_server_status(channel):
    try:
        
        server = MinecraftServer.lookup(SERVER_IP)
        
        
        status = server.status()
        ping = round(status.latency)  
        online_players = status.players.online
        max_players = status.players.max
        

        embed = nextcord.Embed(
            title="Server Status",
            description=f"IP сервера: {SERVER_IP}",
            color=nextcord.Color.green() if online_players > 0 else nextcord.Color.red()
        )
        embed.add_field(name="Пинг", value=f"{ping} ms", inline=False)
        embed.add_field(name="Онлайн", value=f"{online_players}/{max_players} игроков", inline=False)
        embed.set_footer(text="https://github.com/megaflex1337")
        
    except Exception as e:
        embed = nextcord.Embed(
            title="Ошибка",
            description=f"Не удалось получить информацию о сервере: {e}",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="https://github.com/megaflex1337")
        print(f'Ошибка: {e}')

    await channel.send(embed=embed)


@tasks.loop(minutes=UPDATE_INTERVAL)
async def update_server_status():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        async for message in channel.history(limit=100):
            if message.author == bot.user:
                await message.delete()
        await send_server_status(channel)


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


bot.run(TOKEN)
