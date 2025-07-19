import discord
from discord.ext import commands
import datetime
import json
import os
from dotenv import load_dotenv
import requests

# Carrega o .env
dotenv_path = r'C:\Users\jo429\Desktop\GNR\.env'
load_dotenv(dotenv_path)

# Obtém o token do .env
TOKEN = os.getenv("MTM5NjEzMTc4NjE3NzkwODgwNw.Gf7BkV.NXflaNhlifEbnPoWJHNmFpxcUWTx1kqhGYG40M")

if TOKEN is None:
    print("❌ Não foi possível carregar o TOKEN.")
else:
    print("✅ TOKEN carregado com sucesso")

# Configuração do bot e intents
intents = discord.Intents.default()
intents.message_content = True  # Necessário para acessar o conteúdo das mensagens

bot = commands.Bot(command_prefix="!", intents=intents)

# Caminho do ficheiro de registos
FICHEIRO_REGISTOS = "registos.json"

# Carrega registos existentes
if os.path.exists(FICHEIRO_REGISTOS):
    with open(FICHEIRO_REGISTOS, "r") as f:
        registos = json.load(f)
else:
    registos = {}

@bot.event
async def on_ready():
    print(f"✅ Bot está online como {bot.user}")


# Criação dos botões para a interação
class PontoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.pausa_ativa = False  # Flag para controlar se a pausa foi iniciada ou não

    @discord.ui.button(label="🚪 Entrar em Serviço", style=discord.ButtonStyle.green)
    async def entrar_servico(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Registra a entrada no serviço
        user_id = self.user_id
        nome = interaction.user.name
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user_id not in registos:
            registos[user_id] = {"nome": nome, "dias": [], "pausas": []}

        dias = registos[user_id]["dias"]
        
        # Verifica se o usuário já entrou no serviço hoje
        if dias and "entrada" in dias[-1] and "saida" not in dias[-1]:
            await interaction.response.send_message(f"❌ **{nome}**, você já registrou sua entrada hoje! 🚫", ephemeral=True)
            return

        dias.append({"entrada": agora})  # Registra a entrada no serviço
        with open(FICHEIRO_REGISTOS, "w") as f:
            json.dump(registos, f, indent=4)

        embed = discord.Embed(
            title="📅 **Entrada em Serviço Registrada**",
            description=f"**{nome}**, sua entrada no serviço foi registrada com sucesso! ✅",
            color=discord.Color.green()
        )
        embed.add_field(name="Hora de Entrada:", value=f"**{agora}**", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="☕ Pausar", style=discord.ButtonStyle.primary)
    async def pausar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = self.user_id
        nome = interaction.user.name
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Se a pausa não foi iniciada ainda, inicia a pausa
        if not self.pausa_ativa:
            if user_id not in registos:
                registos[user_id] = {"nome": nome, "dias": [], "pausas": []}

            pausas = registos[user_id]["pausas"]
            pausas.append({"inicio": agora})  # Registra o início da pausa
            with open(FICHEIRO_REGISTOS, "w") as f:
                json.dump(registos, f, indent=4)

            embed = discord.Embed(
                title="☕ **Pausa Iniciada**",
                description=f"**{nome}**, sua pausa foi registrada com sucesso às {agora}. Aproveite! 😌",
                color=discord.Color.orange()
            )

            # Atualiza o botão para "Retomar Pausa"
            button.label = "⏯️ Retomar Pausa"
            self.pausa_ativa = True  # Define que a pausa foi iniciada
            await interaction.response.edit_message(embed=embed, view=self)  # Atualiza a mensagem com o novo botão
        else:
            # Se a pausa já foi iniciada, registra o fim da pausa
            pausas = registos[user_id]["pausas"]
            if "fim" in pausas[-1]:
                await interaction.response.send_message(f"❌ **{nome}**, você já finalizou sua pausa!", ephemeral=True)
                return

            pausas[-1]["fim"] = agora  # Registra o fim da pausa
            with open(FICHEIRO_REGISTOS, "w") as f:
                json.dump(registos, f, indent=4)

            # Calcula a duração da pausa
            inicio = datetime.datetime.strptime(pausas[-1]["inicio"], "%Y-%m-%d %H:%M:%S")
            fim = datetime.datetime.strptime(agora, "%Y-%m-%d %H:%M:%S")
            duracao_pausa = fim - inicio

            embed = discord.Embed(
                title="✅ **Pausa Finalizada**",
                description=f"**{nome}**, a pausa foi finalizada com sucesso às {agora}! Duração da pausa: **{duracao_pausa}**.",
                color=discord.Color.green()
            )

            # Atualiza o botão para "Pausar" novamente
            button.label = "☕ Pausar"
            self.pausa_ativa = False  # Define que a pausa foi finalizada
            await interaction.response.edit_message(embed=embed, view=self)  # Atualiza a mensagem com o novo botão

    @discord.ui.button(label="⏹️ Fechar Serviço", style=discord.ButtonStyle.red)
    async def fechar_servico(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Registra o fechamento do serviço
        user_id = self.user_id
        nome = interaction.user.name
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user_id not in registos or not registos[user_id]["dias"]:
            await interaction.response.send_message(f"❌ **{nome}**, você não iniciou o serviço para fechar.", ephemeral=True)
            return

        dias = registos[user_id]["dias"]
        if "saida" in dias[-1]:
            await interaction.response.send_message(f"❌ **{nome}**, o serviço já foi fechado.", ephemeral=True)
            return

        dias[-1]["saida"] = agora  # Registra o fim do serviço
        with open(FICHEIRO_REGISTOS, "w") as f:
            json.dump(registos, f, indent=4)

        # Calcula a duração do serviço
        inicio = datetime.datetime.strptime(dias[-1]["entrada"], "%Y-%m-%d %H:%M:%S")
        fim = datetime.datetime.strptime(agora, "%Y-%m-%d %H:%M:%S")
        duracao_servico = fim - inicio

        embed = discord.Embed(
            title="⏹️ **Serviço Finalizado**",
            description=f"**{nome}**, o seu serviço foi finalizado com sucesso às {agora}! Duração do serviço: **{duracao_servico}**.",
            color=discord.Color.red()
        )

        # Envia para o site (substitua pelo URL correto do seu servidor)
        api_url = "https://gnr-diamond.onrender.com/registrar_servico"  # Substitua pelo URL do seu servidor
        payload = {
            "usuario": nome,
            "entrada": dias[-1]["entrada"],
            "saida": agora,
            "duracao_servico": str(duracao_servico)
        }

        try:
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                await interaction.response.send_message(f"✅ **{nome}**, os dados do seu serviço foram enviados para o site com sucesso!", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ **{nome}**, ocorreu um erro ao enviar os dados para o site: {response.status_code}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **{nome}**, ocorreu um erro ao tentar enviar os dados para o site: {str(e)}", ephemeral=True)


# Comando !ponto
@bot.command()
async def ponto(ctx):
    user_id = str(ctx.author.id)
    view = PontoView(user_id)  # Cria uma nova instância da View com o ID do usuário

    # Envia a mensagem com os botões
    embed = discord.Embed(
        title="📍 **Controle de Ponto**",
        description="Clique no botão abaixo para registrar sua entrada em serviço, pausa ou fechamento do serviço.",
        color=discord.Color.blue()
    )
    embed.add_field(name="🚪 Entrar em Serviço", value="Clique para registrar sua entrada no serviço.", inline=False)
    embed.add_field(name="☕ Pausar", value="Clique para iniciar ou retomar a pausa.", inline=False)
    embed.add_field(name="⏹️ Fechar Serviço", value="Clique para fechar o serviço.", inline=False)

    await ctx.send(embed=embed, view=view)


# Iniciar o bot com o token carregado do .env
bot.run("MTM5NjEzMTc4NjE3NzkwODgwNw.Gf7BkV.NXflaNhlifEbnPoWJHNmFpxcUWTx1kqhGYG40M")
