import os
import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

from database import (
    iniciar_banco,
    adicionar_pokemon,
    atualizar_pokemon,
    adicionar_nivel_pokemon,
    listar_pokemons,
    primeiro_pokemon,
    saldo_usuario,
    usuario_tem_inicial,
    marcar_inicial_escolhido
)

from pokemon_api import (
    buscar_pokemon,
    pokemon_aleatorio,
    gerar_nivel_spawn,
    normalizar_nome,
    eh_inicial,
    verificar_evolucao
)


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CANAL_SPAWN_ID = os.getenv("CANAL_SPAWN_ID")
TEMPO_SPAWN_MINUTOS = int(os.getenv("TEMPO_SPAWN_MINUTOS", "50"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

pokemon_atual = {
    "canal_id": None,
    "pokemon": None,
    "nivel": None
}


INICIAIS_VISUAL = [
    {
        "titulo": "Geração I (Kanto)",
        "pokemons": [
            ("🌱 Bulbasaur", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png"),
            ("🔥 Charmander", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png"),
            ("💧 Squirtle", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png"),
        ]
    },
    {
        "titulo": "Geração II (Johto)",
        "pokemons": [
            ("🌱 Chikorita", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/152.png"),
            ("🔥 Cyndaquil", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/155.png"),
            ("💧 Totodile", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/158.png"),
        ]
    },
    {
        "titulo": "Geração III (Hoenn)",
        "pokemons": [
            ("🌱 Treecko", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/252.png"),
            ("🔥 Torchic", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/255.png"),
            ("💧 Mudkip", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/258.png"),
        ]
    },
    {
        "titulo": "Geração IV (Sinnoh)",
        "pokemons": [
            ("🌱 Turtwig", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/387.png"),
            ("🔥 Chimchar", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/390.png"),
            ("💧 Piplup", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/393.png"),
        ]
    },
    {
        "titulo": "Geração V (Unova)",
        "pokemons": [
            ("🌱 Snivy", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/495.png"),
            ("🔥 Tepig", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/498.png"),
            ("💧 Oshawott", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/501.png"),
        ]
    },
    {
        "titulo": "Geração VI (Kalos)",
        "pokemons": [
            ("🌱 Chespin", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/650.png"),
            ("🔥 Fennekin", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/653.png"),
            ("💧 Froakie", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/656.png"),
        ]
    },
    {
        "titulo": "Geração VII (Alola)",
        "pokemons": [
            ("🌱 Rowlet", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/722.png"),
            ("🔥 Litten", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/725.png"),
            ("💧 Popplio", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/728.png"),
        ]
    },
    {
        "titulo": "Geração VIII (Galar)",
        "pokemons": [
            ("🌱 Grookey", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/810.png"),
            ("🔥 Scorbunny", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/813.png"),
            ("💧 Sobble", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/816.png"),
        ]
    },
    {
        "titulo": "Geração IX (Paldea)",
        "pokemons": [
            ("🌱 Sprigatito", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/906.png"),
            ("🔥 Fuecoco", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/909.png"),
            ("💧 Quaxly", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/912.png"),
        ]
    },
]


ATAQUES = [
    {"nome": "Investida", "tipo": "normal", "poder": 35, "status": None},
    {"nome": "Ataque Rápido", "tipo": "normal", "poder": 45, "status": None},
    {"nome": "Mordida", "tipo": "dark", "poder": 55, "status": None},
    {"nome": "Brasa", "tipo": "fire", "poder": 40, "status": "queimar"},
    {"nome": "Lança-chamas", "tipo": "fire", "poder": 70, "status": "queimar"},
    {"nome": "Bolhas", "tipo": "water", "poder": 40, "status": None},
    {"nome": "Jato d'água", "tipo": "water", "poder": 60, "status": None},
    {"nome": "Chicote de Vinha", "tipo": "grass", "poder": 55, "status": None},
    {"nome": "Folha Navalha", "tipo": "grass", "poder": 65, "status": None},
    {"nome": "Choque do Trovão", "tipo": "electric", "poder": 50, "status": "paralisar"},
]


TIPOS_PTBR = {
    "normal": "Normal",
    "fire": "Fogo",
    "water": "Água",
    "electric": "Elétrico",
    "grass": "Planta",
    "ice": "Gelo",
    "fighting": "Lutador",
    "poison": "Venenoso",
    "ground": "Terra",
    "flying": "Voador",
    "psychic": "Psíquico",
    "bug": "Inseto",
    "rock": "Pedra",
    "ghost": "Fantasma",
    "dragon": "Dragão",
    "dark": "Sombrio",
    "steel": "Aço",
    "fairy": "Fada",
}


VANTAGENS = {
    "fire": {
        "forte": ["grass", "ice", "bug", "steel"],
        "fraco": ["water", "rock", "fire", "dragon"]
    },
    "water": {
        "forte": ["fire", "rock", "ground"],
        "fraco": ["water", "grass", "dragon"]
    },
    "grass": {
        "forte": ["water", "rock", "ground"],
        "fraco": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"]
    },
    "electric": {
        "forte": ["water", "flying"],
        "fraco": ["electric", "grass", "dragon"],
        "imune": ["ground"]
    },
    "ground": {
        "forte": ["fire", "electric", "poison", "rock", "steel"],
        "fraco": ["grass", "bug"],
        "imune": ["flying"]
    },
    "rock": {
        "forte": ["fire", "ice", "flying", "bug"],
        "fraco": ["fighting", "ground", "steel"]
    },
    "ice": {
        "forte": ["grass", "ground", "flying", "dragon"],
        "fraco": ["fire", "water", "ice", "steel"]
    },
    "fighting": {
        "forte": ["normal", "ice", "rock", "dark", "steel"],
        "fraco": ["poison", "flying", "psychic", "bug", "fairy"],
        "imune": ["ghost"]
    },
    "psychic": {
        "forte": ["fighting", "poison"],
        "fraco": ["psychic", "steel"],
        "imune": ["dark"]
    },
    "dark": {
        "forte": ["psychic", "ghost"],
        "fraco": ["fighting", "dark", "fairy"]
    },
    "ghost": {
        "forte": ["psychic", "ghost"],
        "fraco": ["dark"],
        "imune": ["normal"]
    },
    "dragon": {
        "forte": ["dragon"],
        "fraco": ["steel"],
        "imune": ["fairy"]
    },
    "fairy": {
        "forte": ["fighting", "dragon", "dark"],
        "fraco": ["fire", "poison", "steel"]
    },
}


def barra_hp(atual, maximo):
    if maximo <= 0:
        return "░░░░░░░░░░"

    atual = max(0, atual)
    proporcao = atual / maximo
    cheios = round(proporcao * 10)
    vazios = 10 - cheios

    return "█" * cheios + "░" * vazios


def hp_batalha(pokemon):
    _, nome, nivel, hp, ataque, defesa, velocidade = pokemon
    return hp + (nivel * 5)


def multiplicador_tipo(tipo_ataque, tipos_defensor):
    multiplicador = 1.0

    regra = VANTAGENS.get(tipo_ataque)

    if not regra:
        return multiplicador

    for tipo in tipos_defensor:
        if tipo in regra.get("imune", []):
            multiplicador *= 0
        elif tipo in regra.get("forte", []):
            multiplicador *= 2
        elif tipo in regra.get("fraco", []):
            multiplicador *= 0.5

    return multiplicador


def texto_efetividade(multiplicador):
    if multiplicador == 0:
        return "Não teve efeito..."
    if multiplicador >= 2:
        return "Foi super efetivo!"
    if multiplicador < 1:
        return "Não foi muito efetivo."
    return "Dano normal."


def calcular_dano(atacante, ataque_escolhido, defesa_alvo, tipos_defensor, status_atacante=None):
    _, nome, nivel, hp, ataque, defesa, velocidade = atacante

    poder = ataque_escolhido["poder"]
    tipo_ataque = ataque_escolhido["tipo"]

    dano_base = (((ataque + poder + (nivel * 2)) - (defesa_alvo / 2)) / 2)

    if status_atacante == "queimado":
        dano_base *= 0.75

    mult = multiplicador_tipo(tipo_ataque, tipos_defensor)
    dano_final = int(dano_base * mult)

    if mult == 0:
        dano_final = 0

    return max(0, dano_final), mult


def calcular_poder(pokemon):
    _, nome, nivel, hp, ataque, defesa, velocidade = pokemon
    return (nivel * 3) + hp + (ataque * 2) + defesa + velocidade


def ataque_por_nome(nome):
    for ataque in ATAQUES:
        if ataque["nome"] == nome:
            return ataque
    return ATAQUES[0]


def ataques_para_select():
    options = []

    for ataque in ATAQUES:
        tipo = TIPOS_PTBR.get(ataque["tipo"], ataque["tipo"])
        options.append(
            discord.SelectOption(
                label=ataque["nome"],
                description=f"Tipo {tipo} | Poder {ataque['poder']}",
                value=ataque["nome"]
            )
        )

    return options


def aplicar_status(ataque, status_atual):
    if status_atual:
        return status_atual, None

    if ataque["status"] == "queimar":
        if random.randint(1, 100) <= 25:
            return "queimado", "🔥 O alvo ficou queimado!"

    if ataque["status"] == "paralisar":
        if random.randint(1, 100) <= 25:
            return "paralisado", "⚡ O alvo ficou paralisado!"

    return status_atual, None


def dano_status(status, hp_max):
    if status == "queimado":
        return max(3, int(hp_max * 0.08))
    return 0


def texto_status(status):
    if status == "queimado":
        return "🔥 Queimado"
    if status == "paralisado":
        return "⚡ Paralisado"
    return "✅ Normal"


def pode_atacar(status):
    if status == "paralisado":
        if random.randint(1, 100) <= 30:
            return False
    return True


async def tentar_evoluir_pokemon(pokemon_id: int, nome_atual: str, nivel: int):
    try:
        evolucao = await asyncio.wait_for(
            verificar_evolucao(nome_atual, nivel),
            timeout=5
        )
    except Exception:
        return None

    if not evolucao:
        return None

    novo = evolucao["pokemon"]

    atualizar_pokemon(
        pokemon_id=pokemon_id,
        nome=novo["nome"],
        hp=novo["hp"],
        ataque=novo["ataque"],
        defesa=novo["defesa"],
        velocidade=novo["velocidade"]
    )

    return evolucao


async def enviar_spawn(canal: discord.TextChannel):
    pokemon = await pokemon_aleatorio()

    if not pokemon:
        await canal.send("❌ Não consegui buscar um Pokémon na PokeAPI.")
        return

    nivel = gerar_nivel_spawn()

    pokemon_atual["canal_id"] = canal.id
    pokemon_atual["pokemon"] = pokemon
    pokemon_atual["nivel"] = nivel

    embed = discord.Embed(
        title="🌿 Um Pokémon selvagem apareceu!",
        description="Adivinhe o Pokémon e use `/capturar nome` para capturar!",
        color=discord.Color.from_rgb(255, 105, 180)
    )

    embed.add_field(name="Dica", value=f"O nome tem **{len(pokemon['nome'])} letras**.", inline=False)
    embed.add_field(name="Nível", value=str(nivel), inline=True)
    embed.add_field(name="Tipo", value=", ".join(pokemon["tipos_ptbr"]).title(), inline=True)

    if pokemon["imagem"]:
        embed.set_image(url=pokemon["imagem"])

    await canal.send(embed=embed)


def encontrar_canal_spawn():
    if CANAL_SPAWN_ID:
        canal = bot.get_channel(int(CANAL_SPAWN_ID))
        if canal:
            return canal

    for guild in bot.guilds:
        for canal in guild.text_channels:
            permissoes = canal.permissions_for(guild.me)
            if permissoes.send_messages and permissoes.embed_links:
                return canal

    return None


def pokemon_dict_para_tuple(pokemon, nivel):
    return (
        0,
        pokemon["nome"],
        nivel,
        pokemon["hp"],
        pokemon["ataque"],
        pokemon["defesa"],
        pokemon["velocidade"]
    )


class BatalhaNPCView(discord.ui.View):
    def __init__(self, jogador, meu_pokemon, meu_info, pokemon_npc, nivel_npc, nome_npc):
        super().__init__(timeout=120)

        self.jogador = jogador
        self.meu_pokemon = meu_pokemon
        self.meu_info = meu_info
        self.pokemon_npc = pokemon_npc
        self.nivel_npc = nivel_npc
        self.nome_npc = nome_npc

        self.hp_meu_max = hp_batalha(meu_pokemon)
        self.hp_npc_max = hp_batalha(pokemon_dict_para_tuple(pokemon_npc, nivel_npc))

        self.hp_meu = self.hp_meu_max
        self.hp_npc = self.hp_npc_max

        self.status_meu = None
        self.status_npc = None
        self.turno = 1

        self.select = discord.ui.Select(
            placeholder="Escolha seu ataque",
            min_values=1,
            max_values=1,
            options=ataques_para_select()
        )

        self.select.callback = self.escolher_ataque
        self.add_item(self.select)

    async def escolher_ataque(self, interaction: discord.Interaction):
        if interaction.user.id != self.jogador.id:
            await interaction.response.send_message("❌ Essa batalha não é sua.", ephemeral=True)
            return

        ataque_jogador = ataque_por_nome(self.select.values[0])
        ataque_npc = random.choice(ATAQUES)

        meu_id, meu_nome, meu_nivel, meu_hp, meu_ataque, meu_defesa, meu_vel = self.meu_pokemon

        npc_tuple = pokemon_dict_para_tuple(self.pokemon_npc, self.nivel_npc)

        log = []

        if pode_atacar(self.status_meu):
            dano, mult = calcular_dano(
                self.meu_pokemon,
                ataque_jogador,
                self.pokemon_npc["defesa"],
                self.pokemon_npc["tipos"],
                self.status_meu
            )

            self.hp_npc = max(0, self.hp_npc - dano)

            log.append(
                f"🧢 **{meu_nome.title()}** usou **{ataque_jogador['nome']}** e causou `{dano}` de dano. {texto_efetividade(mult)}"
            )

            self.status_npc, msg_status = aplicar_status(ataque_jogador, self.status_npc)
            if msg_status:
                log.append(msg_status)
        else:
            log.append(f"⚡ **{meu_nome.title()}** está paralisado e não conseguiu atacar!")

        if self.hp_npc > 0:
            if pode_atacar(self.status_npc):
                dano, mult = calcular_dano(
                    npc_tuple,
                    ataque_npc,
                    meu_defesa,
                    self.meu_info["tipos"],
                    self.status_npc
                )

                self.hp_meu = max(0, self.hp_meu - dano)

                log.append(
                    f"🤖 **{self.pokemon_npc['nome'].title()}** usou **{ataque_npc['nome']}** e causou `{dano}` de dano. {texto_efetividade(mult)}"
                )

                self.status_meu, msg_status = aplicar_status(ataque_npc, self.status_meu)
                if msg_status:
                    log.append(msg_status)
            else:
                log.append(f"⚡ **{self.pokemon_npc['nome'].title()}** está paralisado e não conseguiu atacar!")

        queimadura_meu = dano_status(self.status_meu, self.hp_meu_max)
        queimadura_npc = dano_status(self.status_npc, self.hp_npc_max)

        if queimadura_meu and self.hp_meu > 0:
            self.hp_meu = max(0, self.hp_meu - queimadura_meu)
            log.append(f"🔥 **{meu_nome.title()}** sofreu `{queimadura_meu}` de dano por queimadura.")

        if queimadura_npc and self.hp_npc > 0:
            self.hp_npc = max(0, self.hp_npc - queimadura_npc)
            log.append(f"🔥 **{self.pokemon_npc['nome'].title()}** sofreu `{queimadura_npc}` de dano por queimadura.")

        embed = discord.Embed(
            title="⚔️ Batalha contra NPC!",
            description="\n".join(log),
            color=discord.Color.red()
        )

        embed.add_field(
            name=f"{self.jogador.display_name}",
            value=(
                f"**{meu_nome.title()}** Nv. {meu_nivel}\n"
                f"❤️ `{self.hp_meu}/{self.hp_meu_max}`\n"
                f"`{barra_hp(self.hp_meu, self.hp_meu_max)}`\n"
                f"Status: {texto_status(self.status_meu)}"
            ),
            inline=True
        )

        embed.add_field(
            name=self.nome_npc,
            value=(
                f"**{self.pokemon_npc['nome'].title()}** Nv. {self.nivel_npc}\n"
                f"❤️ `{self.hp_npc}/{self.hp_npc_max}`\n"
                f"`{barra_hp(self.hp_npc, self.hp_npc_max)}`\n"
                f"Status: {texto_status(self.status_npc)}"
            ),
            inline=True
        )

        terminou = False

        if self.hp_npc <= 0:
            terminou = True
            adicionar_nivel_pokemon(meu_id, 1)

            embed.add_field(
                name="🏆 Vitória!",
                value=f"Seu **{meu_nome.title()}** ganhou **+1 nível**.",
                inline=False
            )

            evolucao = await tentar_evoluir_pokemon(meu_id, meu_nome, meu_nivel + 1)

            if evolucao:
                embed.add_field(
                    name="✨ Evolução automática!",
                    value=f"Seu **{evolucao['nome_antigo'].title()}** evoluiu para **{evolucao['nome_novo'].title()}**!",
                    inline=False
                )

        elif self.hp_meu <= 0:
            terminou = True
            embed.add_field(
                name="💀 Derrota!",
                value="Seu Pokémon desmaiou e não ganhou nível.",
                inline=False
            )
        else:
            self.turno += 1
            embed.set_footer(text=f"Turno {self.turno} — escolha o próximo ataque.")

        if self.pokemon_npc["sprite"]:
            embed.set_thumbnail(url=self.pokemon_npc["sprite"])
        elif self.pokemon_npc["imagem"]:
            embed.set_thumbnail(url=self.pokemon_npc["imagem"])

        if terminou:
            for item in self.children:
                item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


class BatalhaPVPView(discord.ui.View):
    def __init__(self, jogador1, jogador2, p1, p2, p1_info, p2_info):
        super().__init__(timeout=180)

        self.j1 = jogador1
        self.j2 = jogador2
        self.p1 = p1
        self.p2 = p2
        self.p1_info = p1_info
        self.p2_info = p2_info

        self.hp1_max = hp_batalha(p1)
        self.hp2_max = hp_batalha(p2)

        self.hp1 = self.hp1_max
        self.hp2 = self.hp2_max

        self.status1 = None
        self.status2 = None

        self.escolha1 = None
        self.escolha2 = None
        self.turno = 1

        self.select1 = discord.ui.Select(
            placeholder=f"{jogador1.display_name}, escolha seu ataque",
            min_values=1,
            max_values=1,
            options=ataques_para_select()
        )

        self.select2 = discord.ui.Select(
            placeholder=f"{jogador2.display_name}, escolha seu ataque",
            min_values=1,
            max_values=1,
            options=ataques_para_select()
        )

        self.select1.callback = self.callback_jogador1
        self.select2.callback = self.callback_jogador2

        self.add_item(self.select1)
        self.add_item(self.select2)

    async def callback_jogador1(self, interaction: discord.Interaction):
        if interaction.user.id != self.j1.id:
            await interaction.response.send_message("❌ Esse menu não é seu.", ephemeral=True)
            return

        self.escolha1 = ataque_por_nome(self.select1.values[0])
        await interaction.response.send_message("✅ Ataque escolhido. Aguardando o outro jogador.", ephemeral=True)
        await self.processar_turno_se_pronto(interaction)

    async def callback_jogador2(self, interaction: discord.Interaction):
        if interaction.user.id != self.j2.id:
            await interaction.response.send_message("❌ Esse menu não é seu.", ephemeral=True)
            return

        self.escolha2 = ataque_por_nome(self.select2.values[0])
        await interaction.response.send_message("✅ Ataque escolhido. Aguardando o outro jogador.", ephemeral=True)
        await self.processar_turno_se_pronto(interaction)

    async def processar_turno_se_pronto(self, interaction: discord.Interaction):
        if not self.escolha1 or not self.escolha2:
            return

        id1, nome1, nivel1, hp1, ataque1, defesa1, vel1 = self.p1
        id2, nome2, nivel2, hp2, ataque2, defesa2, vel2 = self.p2

        log = []

        ordem = [
            ("j1", self.p1, self.escolha1, self.p2, self.p2_info, self.status1),
            ("j2", self.p2, self.escolha2, self.p1, self.p1_info, self.status2),
        ]

        if vel2 > vel1:
            ordem.reverse()

        for lado, atacante, ataque, defensor, defensor_info, status_atacante in ordem:
            if self.hp1 <= 0 or self.hp2 <= 0:
                break

            atacante_id, atacante_nome, atacante_nivel, atacante_hp, atacante_atq, atacante_def, atacante_vel = atacante
            defensor_id, defensor_nome, defensor_nivel, defensor_hp, defensor_atq, defensor_def, defensor_vel = defensor

            if lado == "j1":
                if not pode_atacar(self.status1):
                    log.append(f"⚡ **{nome1.title()}** está paralisado e não conseguiu atacar!")
                    continue

                dano, mult = calcular_dano(
                    self.p1,
                    ataque,
                    defesa2,
                    self.p2_info["tipos"],
                    self.status1
                )

                self.hp2 = max(0, self.hp2 - dano)
                log.append(f"🔴 **{nome1.title()}** usou **{ataque['nome']}** e causou `{dano}`. {texto_efetividade(mult)}")

                self.status2, msg = aplicar_status(ataque, self.status2)
                if msg:
                    log.append(msg)

            else:
                if not pode_atacar(self.status2):
                    log.append(f"⚡ **{nome2.title()}** está paralisado e não conseguiu atacar!")
                    continue

                dano, mult = calcular_dano(
                    self.p2,
                    ataque,
                    defesa1,
                    self.p1_info["tipos"],
                    self.status2
                )

                self.hp1 = max(0, self.hp1 - dano)
                log.append(f"🔵 **{nome2.title()}** usou **{ataque['nome']}** e causou `{dano}`. {texto_efetividade(mult)}")

                self.status1, msg = aplicar_status(ataque, self.status1)
                if msg:
                    log.append(msg)

        queimadura1 = dano_status(self.status1, self.hp1_max)
        queimadura2 = dano_status(self.status2, self.hp2_max)

        if queimadura1 and self.hp1 > 0:
            self.hp1 = max(0, self.hp1 - queimadura1)
            log.append(f"🔥 **{nome1.title()}** sofreu `{queimadura1}` de dano por queimadura.")

        if queimadura2 and self.hp2 > 0:
            self.hp2 = max(0, self.hp2 - queimadura2)
            log.append(f"🔥 **{nome2.title()}** sofreu `{queimadura2}` de dano por queimadura.")

        embed = discord.Embed(
            title="⚔️ Batalha PvP por Turnos!",
            description="\n".join(log),
            color=discord.Color.red()
        )

        embed.add_field(
            name=self.j1.display_name,
            value=(
                f"**{nome1.title()}** Nv. {nivel1}\n"
                f"❤️ `{self.hp1}/{self.hp1_max}`\n"
                f"`{barra_hp(self.hp1, self.hp1_max)}`\n"
                f"Status: {texto_status(self.status1)}"
            ),
            inline=True
        )

        embed.add_field(
            name=self.j2.display_name,
            value=(
                f"**{nome2.title()}** Nv. {nivel2}\n"
                f"❤️ `{self.hp2}/{self.hp2_max}`\n"
                f"`{barra_hp(self.hp2, self.hp2_max)}`\n"
                f"Status: {texto_status(self.status2)}"
            ),
            inline=True
        )

        terminou = False

        if self.hp1 <= 0 and self.hp2 <= 0:
            terminou = True
            embed.add_field(name="Empate!", value="Os dois Pokémon desmaiaram.", inline=False)

        elif self.hp2 <= 0:
            terminou = True
            adicionar_nivel_pokemon(id1, 1)
            embed.add_field(name="🏆 Vitória!", value=f"{self.j1.mention} venceu! **{nome1.title()}** ganhou +1 nível.", inline=False)

            evolucao = await tentar_evoluir_pokemon(id1, nome1, nivel1 + 1)
            if evolucao:
                embed.add_field(
                    name="✨ Evolução automática!",
                    value=f"**{evolucao['nome_antigo'].title()}** evoluiu para **{evolucao['nome_novo'].title()}**!",
                    inline=False
                )

        elif self.hp1 <= 0:
            terminou = True
            adicionar_nivel_pokemon(id2, 1)
            embed.add_field(name="🏆 Vitória!", value=f"{self.j2.mention} venceu! **{nome2.title()}** ganhou +1 nível.", inline=False)

            evolucao = await tentar_evoluir_pokemon(id2, nome2, nivel2 + 1)
            if evolucao:
                embed.add_field(
                    name="✨ Evolução automática!",
                    value=f"**{evolucao['nome_antigo'].title()}** evoluiu para **{evolucao['nome_novo'].title()}**!",
                    inline=False
                )

        else:
            self.turno += 1
            self.escolha1 = None
            self.escolha2 = None
            embed.set_footer(text=f"Turno {self.turno} — os dois jogadores devem escolher o próximo ataque.")

        if terminou:
            for item in self.children:
                item.disabled = True

        await interaction.message.edit(embed=embed, view=self)


@bot.event
async def on_ready():
    iniciar_banco()

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as erro:
        print(f"Erro ao sincronizar slash commands: {erro}")

    print(f"Bot conectado como {bot.user}")

    if not spawn_automatico.is_running():
        spawn_automatico.start()


@tasks.loop(minutes=TEMPO_SPAWN_MINUTOS)
async def spawn_automatico():
    await bot.wait_until_ready()

    canal = encontrar_canal_spawn()

    if not canal:
        print("Nenhum canal de spawn encontrado.")
        return

    await enviar_spawn(canal)


@bot.tree.command(name="tutorial", description="Mostra o tutorial de como jogar.")
async def tutorial(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📘 Tutorial do PokéBR",
        description="Aprenda como começar e capturar Pokémon.",
        color=discord.Color.blue()
    )

    embed.add_field(name="1️⃣ Comece sua jornada", value="Use `/iniciar`.", inline=False)
    embed.add_field(name="2️⃣ Escolha seu inicial", value="Use `/escolher pokemon:charmander`.", inline=False)
    embed.add_field(name="3️⃣ Capture Pokémon", value="Use `/capturar nome:pikachu`.", inline=False)
    embed.add_field(name="4️⃣ Veja sua coleção", value="Use `/pokemon`.", inline=False)
    embed.add_field(name="5️⃣ Batalhe contra NPC", value="Use `/batalhar_npc` e escolha um ataque.", inline=False)
    embed.add_field(name="6️⃣ Batalhe contra jogador", value="Use `/batalhar usuario:@jogador`.", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="iniciar", description="Comece sua jornada Pokémon.")
async def iniciar(interaction: discord.Interaction):
    if usuario_tem_inicial(interaction.user.id):
        await interaction.response.send_message(
            "✅ Você já começou sua jornada! Use `/pokemon` para ver seus Pokémon.",
            ephemeral=True
        )
        return

    embeds = []

    intro = discord.Embed(
        title="👋 Bem-vindo ao mundo dos Pokémon!",
        description=(
            "Para começar, escolha um Pokémon inicial usando:\n"
            "`/escolher pokemon:nome_do_pokemon`\n\n"
            "Exemplo:\n"
            "`/escolher pokemon:charmander`"
        ),
        color=discord.Color.from_rgb(255, 105, 180)
    )

    intro.set_image(
        url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png"
    )

    embeds.append(intro)

    for grupo in INICIAIS_VISUAL:
        texto = ""

        for nome, imagem in grupo["pokemons"]:
            texto += f"{nome} — [Ver imagem]({imagem})\n"

        embed = discord.Embed(
            title=grupo["titulo"],
            description=texto,
            color=discord.Color.from_rgb(255, 105, 180)
        )

        embed.set_thumbnail(url=grupo["pokemons"][0][1])
        embeds.append(embed)

    await interaction.response.send_message(embeds=embeds)


@bot.tree.command(name="escolher", description="Escolha seu Pokémon inicial.")
@app_commands.describe(pokemon="Nome do Pokémon inicial")
async def escolher(interaction: discord.Interaction, pokemon: str):
    await interaction.response.defer()

    nome = normalizar_nome(pokemon)

    if usuario_tem_inicial(interaction.user.id):
        await interaction.followup.send(
            "❌ Você já escolheu seu Pokémon inicial.",
            ephemeral=True
        )
        return

    if not eh_inicial(nome):
        await interaction.followup.send(
            "❌ Esse Pokémon não está na lista de iniciais. Use `/iniciar` para ver as opções.",
            ephemeral=True
        )
        return

    dados = await buscar_pokemon(nome)

    if not dados:
        await interaction.followup.send(
            "❌ Não consegui buscar esse Pokémon na PokeAPI.",
            ephemeral=True
        )
        return

    adicionar_pokemon(
        discord_id=interaction.user.id,
        nome=dados["nome"],
        nivel=1,
        hp=dados["hp"],
        ataque=dados["ataque"],
        defesa=dados["defesa"],
        velocidade=dados["velocidade"],
        inicial=1,
        moedas_bonus=0
    )

    marcar_inicial_escolhido(interaction.user.id)

    embed = discord.Embed(
        title="🎉 Parabéns!",
        description=f"Seu **{dados['nome'].title()}** agora é nível **1**!",
        color=discord.Color.from_rgb(255, 105, 180)
    )

    embed.add_field(name="Tipo", value=", ".join(dados["tipos_ptbr"]).title(), inline=True)

    if dados["sprite"]:
        embed.set_thumbnail(url=dados["sprite"])

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="capturar", description="Captura o Pokémon selvagem atual.")
@app_commands.describe(nome="Nome do Pokémon que apareceu")
async def capturar(interaction: discord.Interaction, nome: str):
    await interaction.response.defer()

    if pokemon_atual["pokemon"] is None:
        await interaction.followup.send("❌ Não tem nenhum Pokémon selvagem no momento.", ephemeral=True)
        return

    if pokemon_atual["canal_id"] != interaction.channel.id:
        await interaction.followup.send("❌ O Pokémon selvagem não apareceu neste canal.", ephemeral=True)
        return

    pokemon = pokemon_atual["pokemon"]
    nome_digitado = normalizar_nome(nome)
    nome_correto = normalizar_nome(pokemon["nome"])

    if nome_digitado != nome_correto:
        await interaction.followup.send("❌ Nome incorreto! Tente novamente.", ephemeral=True)
        return

    nivel = pokemon_atual["nivel"]

    pokemon_id = adicionar_pokemon(
        discord_id=interaction.user.id,
        nome=pokemon["nome"],
        nivel=nivel,
        hp=pokemon["hp"],
        ataque=pokemon["ataque"],
        defesa=pokemon["defesa"],
        velocidade=pokemon["velocidade"],
        inicial=0,
        moedas_bonus=10
    )

    embed = discord.Embed(
        title="🎉 Pokémon capturado!",
        description=f"{interaction.user.mention}, você capturou **{pokemon['nome'].title()}** nível **{nivel}**!",
        color=discord.Color.from_rgb(255, 105, 180)
    )

    embed.add_field(name="Tipo", value=", ".join(pokemon["tipos_ptbr"]).title(), inline=True)
    embed.add_field(name="Recompensa", value="+10 moedas", inline=True)

    evolucao = await tentar_evoluir_pokemon(pokemon_id, pokemon["nome"], nivel)

    if evolucao:
        embed.add_field(
            name="✨ Evolução automática!",
            value=f"Seu **{evolucao['nome_antigo'].title()}** evoluiu para **{evolucao['nome_novo'].title()}**!",
            inline=False
        )

    if pokemon["sprite"]:
        embed.set_thumbnail(url=pokemon["sprite"])
    elif pokemon["imagem"]:
        embed.set_thumbnail(url=pokemon["imagem"])

    pokemon_atual["canal_id"] = None
    pokemon_atual["pokemon"] = None
    pokemon_atual["nivel"] = None

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="pokemon", description="Mostra seus últimos Pokémon capturados.")
async def pokemon(interaction: discord.Interaction):
    dados = listar_pokemons(interaction.user.id)

    if not dados:
        await interaction.response.send_message(
            "📦 Você ainda não tem nenhum Pokémon. Use `/iniciar` para começar.",
            ephemeral=True
        )
        return

    linhas = []

    for i, item in enumerate(dados, start=1):
        nome, nivel, hp, ataque, defesa, velocidade, inicial, criado_em = item
        tag = "⭐ Inicial" if inicial else "🌿 Capturado"
        linhas.append(f"**{i}. {nome.title()}** — Nv. {nivel} | {tag}")

    embed = discord.Embed(
        title=f"📦 Pokémon de {interaction.user.display_name}",
        description="\n".join(linhas),
        color=discord.Color.purple()
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="info", description="Mostra informações de um Pokémon.")
@app_commands.describe(nome="Nome do Pokémon")
async def info(interaction: discord.Interaction, nome: str):
    await interaction.response.defer()

    pokemon = await buscar_pokemon(nome)

    if not pokemon:
        await interaction.followup.send("❌ Pokémon não encontrado.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🔎 {pokemon['nome'].title()}",
        description=f"ID na Pokédex: **#{pokemon['id']}**",
        color=discord.Color.orange()
    )

    embed.add_field(name="Tipos", value=", ".join(pokemon["tipos_ptbr"]).title(), inline=False)
    embed.add_field(name="HP", value=str(pokemon["hp"]), inline=True)
    embed.add_field(name="Ataque", value=str(pokemon["ataque"]), inline=True)
    embed.add_field(name="Defesa", value=str(pokemon["defesa"]), inline=True)
    embed.add_field(name="Velocidade", value=str(pokemon["velocidade"]), inline=True)

    if pokemon["imagem"]:
        embed.set_image(url=pokemon["imagem"])

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="batalhar", description="Batalha PvP por turnos com ataques, status e vantagem de tipo.")
@app_commands.describe(usuario="Jogador que você quer desafiar")
async def batalhar(interaction: discord.Interaction, usuario: discord.Member):
    await interaction.response.defer()

    if usuario.bot:
        await interaction.followup.send("❌ Você não pode batalhar contra bots.", ephemeral=True)
        return

    if usuario.id == interaction.user.id:
        await interaction.followup.send("❌ Você não pode batalhar contra você mesmo.", ephemeral=True)
        return

    p1 = primeiro_pokemon(interaction.user.id)
    p2 = primeiro_pokemon(usuario.id)

    if not p1:
        await interaction.followup.send("❌ Você ainda não tem Pokémon. Use `/iniciar`.", ephemeral=True)
        return

    if not p2:
        await interaction.followup.send("❌ Esse usuário ainda não tem Pokémon.", ephemeral=True)
        return

    p1_info = await buscar_pokemon(p1[1])
    p2_info = await buscar_pokemon(p2[1])

    if not p1_info or not p2_info:
        await interaction.followup.send("❌ Não consegui buscar dados dos Pokémon na PokeAPI.", ephemeral=True)
        return

    embed = discord.Embed(
        title="⚔️ Batalha PvP por Turnos!",
        description="Os dois jogadores devem escolher um ataque no menu.",
        color=discord.Color.red()
    )

    embed.add_field(
        name=interaction.user.display_name,
        value=(
            f"**{p1[1].title()}** Nv. {p1[2]}\n"
            f"❤️ `{hp_batalha(p1)}/{hp_batalha(p1)}`\n"
            f"`{barra_hp(hp_batalha(p1), hp_batalha(p1))}`\n"
            f"Status: ✅ Normal"
        ),
        inline=True
    )

    embed.add_field(
        name=usuario.display_name,
        value=(
            f"**{p2[1].title()}** Nv. {p2[2]}\n"
            f"❤️ `{hp_batalha(p2)}/{hp_batalha(p2)}`\n"
            f"`{barra_hp(hp_batalha(p2), hp_batalha(p2))}`\n"
            f"Status: ✅ Normal"
        ),
        inline=True
    )

    view = BatalhaPVPView(interaction.user, usuario, p1, p2, p1_info, p2_info)
    await interaction.followup.send(embed=embed, view=view)


@bot.tree.command(name="batalhar_npc", description="Batalhe contra um NPC com ataques, status e vantagem de tipo.")
async def batalhar_npc(interaction: discord.Interaction):
    await interaction.response.defer()

    meu_pokemon = primeiro_pokemon(interaction.user.id)

    if not meu_pokemon:
        await interaction.followup.send(
            "❌ Você ainda não tem Pokémon. Use `/iniciar` primeiro.",
            ephemeral=True
        )
        return

    meu_info = await buscar_pokemon(meu_pokemon[1])

    if not meu_info:
        await interaction.followup.send("❌ Não consegui buscar os dados do seu Pokémon.", ephemeral=True)
        return

    pokemon_npc = await pokemon_aleatorio()

    if not pokemon_npc:
        await interaction.followup.send(
            "❌ Não consegui gerar o Pokémon do NPC.",
            ephemeral=True
        )
        return

    nomes_npc = [
        "Treinador João",
        "Treinadora Ana",
        "Caçador Bruno",
        "Líder Pedro",
        "Jovem Lucas",
        "Rival Misterioso"
    ]

    nome_npc = random.choice(nomes_npc)
    nivel_npc = random.randint(max(1, meu_pokemon[2] - 3), meu_pokemon[2] + 3)

    embed = discord.Embed(
        title="⚔️ Batalha contra NPC!",
        description="Escolha um ataque no menu abaixo.",
        color=discord.Color.red()
    )

    hp_meu = hp_batalha(meu_pokemon)
    hp_npc = hp_batalha(pokemon_dict_para_tuple(pokemon_npc, nivel_npc))

    embed.add_field(
        name=f"{interaction.user.display_name}",
        value=(
            f"**{meu_pokemon[1].title()}** Nv. {meu_pokemon[2]}\n"
            f"❤️ `{hp_meu}/{hp_meu}`\n"
            f"`{barra_hp(hp_meu, hp_meu)}`\n"
            f"Status: ✅ Normal"
        ),
        inline=True
    )

    embed.add_field(
        name=nome_npc,
        value=(
            f"**{pokemon_npc['nome'].title()}** Nv. {nivel_npc}\n"
            f"❤️ `{hp_npc}/{hp_npc}`\n"
            f"`{barra_hp(hp_npc, hp_npc)}`\n"
            f"Status: ✅ Normal"
        ),
        inline=True
    )

    if pokemon_npc["sprite"]:
        embed.set_thumbnail(url=pokemon_npc["sprite"])
    elif pokemon_npc["imagem"]:
        embed.set_thumbnail(url=pokemon_npc["imagem"])

    view = BatalhaNPCView(
        jogador=interaction.user,
        meu_pokemon=meu_pokemon,
        meu_info=meu_info,
        pokemon_npc=pokemon_npc,
        nivel_npc=nivel_npc,
        nome_npc=nome_npc
    )

    await interaction.followup.send(embed=embed, view=view)


@bot.tree.command(name="saldo", description="Mostra seu saldo de moedas.")
async def saldo(interaction: discord.Interaction):
    moedas = saldo_usuario(interaction.user.id)
    await interaction.response.send_message(
        f"💰 {interaction.user.mention}, você tem **{moedas} moedas**.",
        ephemeral=True
    )


@bot.tree.command(name="spawn_teste", description="Força um spawn manual para testar.")
async def spawn_teste(interaction: discord.Interaction):
    await interaction.response.send_message("🌿 Gerando um Pokémon selvagem...", ephemeral=True)
    await enviar_spawn(interaction.channel)


if not TOKEN:
    raise RuntimeError("Token do Discord não encontrado. Configure o arquivo .env.")

bot.run(TOKEN)