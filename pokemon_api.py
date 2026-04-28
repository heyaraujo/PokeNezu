import aiohttp
import random


POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon"
SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species"

TIPOS_PTBR = {
    "normal": "normal",
    "fire": "fogo",
    "water": "água",
    "electric": "elétrico",
    "grass": "planta",
    "ice": "gelo",
    "fighting": "lutador",
    "poison": "venenoso",
    "ground": "terra",
    "flying": "voador",
    "psychic": "psíquico",
    "bug": "inseto",
    "rock": "pedra",
    "ghost": "fantasma",
    "dragon": "dragão",
    "dark": "sombrio",
    "steel": "aço",
    "fairy": "fada"
}

INICIAIS = {
    "kanto": ["bulbasaur", "charmander", "squirtle"],
    "johto": ["chikorita", "cyndaquil", "totodile"],
    "hoenn": ["treecko", "torchic", "mudkip"],
    "sinnoh": ["turtwig", "chimchar", "piplup"],
    "unova": ["snivy", "tepig", "oshawott"],
    "kalos": ["chespin", "fennekin", "froakie"],
    "alola": ["rowlet", "litten", "popplio"],
    "galar": ["grookey", "scorbunny", "sobble"],
    "paldea": ["sprigatito", "fuecoco", "quaxly"]
}

EMOJIS_INICIAIS = {
    "bulbasaur": "🌱", "charmander": "🔥", "squirtle": "💧",
    "chikorita": "🌿", "cyndaquil": "🔥", "totodile": "💧",
    "treecko": "🌱", "torchic": "🔥", "mudkip": "💧",
    "turtwig": "🌱", "chimchar": "🔥", "piplup": "💧",
    "snivy": "🌱", "tepig": "🔥", "oshawott": "💧",
    "chespin": "🌱", "fennekin": "🔥", "froakie": "💧",
    "rowlet": "🌱", "litten": "🔥", "popplio": "💧",
    "grookey": "🌱", "scorbunny": "🔥", "sobble": "💧",
    "sprigatito": "🌱", "fuecoco": "🔥", "quaxly": "💧"
}


async def buscar_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            if resposta.status != 200:
                return None
            return await resposta.json()


async def buscar_pokemon(nome_ou_id):
    dados = await buscar_json(f"{POKEAPI_URL}/{str(nome_ou_id).lower()}")

    if not dados:
        return None

    stats = {item["stat"]["name"]: item["base_stat"] for item in dados["stats"]}

    imagem = dados["sprites"]["other"]["official-artwork"]["front_default"]
    if not imagem:
        imagem = dados["sprites"]["front_default"]

    sprite = dados["sprites"]["front_default"]

    tipos = [tipo["type"]["name"] for tipo in dados["types"]]
    tipos_ptbr = [TIPOS_PTBR.get(tipo, tipo) for tipo in tipos]

    return {
        "id": dados["id"],
        "nome": dados["name"],
        "altura": dados["height"],
        "peso": dados["weight"],
        "imagem": imagem,
        "sprite": sprite,
        "hp": stats.get("hp", 0),
        "ataque": stats.get("attack", 0),
        "defesa": stats.get("defense", 0),
        "velocidade": stats.get("speed", 0),
        "tipos": tipos,
        "tipos_ptbr": tipos_ptbr
    }


async def pokemon_aleatorio():
    numero = random.randint(1, 1025)
    return await buscar_pokemon(numero)


def gerar_nivel_spawn():
    return random.randint(1, 35)


def normalizar_nome(nome: str):
    return nome.strip().lower()


def eh_inicial(nome: str):
    nome = normalizar_nome(nome)
    for lista in INICIAIS.values():
        if nome in lista:
            return True
    return False


def texto_iniciais():
    linhas = []

    nomes_geracoes = {
        "kanto": "Geração I (Kanto)",
        "johto": "Geração II (Johto)",
        "hoenn": "Geração III (Hoenn)",
        "sinnoh": "Geração IV (Sinnoh)",
        "unova": "Geração V (Unova)",
        "kalos": "Geração VI (Kalos)",
        "alola": "Geração VII (Alola)",
        "galar": "Geração VIII (Galar)",
        "paldea": "Geração IX (Paldea)"
    }

    for geracao, pokemons in INICIAIS.items():
        linha_pokes = []
        for p in pokemons:
            emoji = EMOJIS_INICIAIS.get(p, "⭐")
            linha_pokes.append(f"{emoji} {p.title()}")

        linhas.append(f"**{nomes_geracoes[geracao]}**\n" + " • ".join(linha_pokes))

    return "\n\n".join(linhas)


def procurar_evolucao_na_arvore(no, nome_atual: str, nivel_atual: int):
    especie_atual = no["species"]["name"]

    if especie_atual == nome_atual:
        for evolucao in no.get("evolves_to", []):
            detalhes = evolucao.get("evolution_details", [])
            if not detalhes:
                continue

            detalhe = detalhes[0]
            nivel_minimo = detalhe.get("min_level")

            if nivel_minimo and nivel_atual >= nivel_minimo:
                return evolucao["species"]["name"], nivel_minimo

        return None

    for evolucao in no.get("evolves_to", []):
        resultado = procurar_evolucao_na_arvore(evolucao, nome_atual, nivel_atual)
        if resultado:
            return resultado

    return None


async def verificar_evolucao(nome_pokemon: str, nivel_atual: int):
    especie = await buscar_json(f"{SPECIES_URL}/{nome_pokemon.lower()}")

    if not especie or not especie.get("evolution_chain"):
        return None

    cadeia_url = especie["evolution_chain"]["url"]
    cadeia = await buscar_json(cadeia_url)

    if not cadeia:
        return None

    resultado = procurar_evolucao_na_arvore(cadeia["chain"], nome_pokemon.lower(), nivel_atual)

    if not resultado:
        return None

    novo_nome, nivel_minimo = resultado
    novo_pokemon = await buscar_pokemon(novo_nome)

    if not novo_pokemon:
        return None

    return {
        "nome_antigo": nome_pokemon,
        "nome_novo": novo_nome,
        "nivel_minimo": nivel_minimo,
        "pokemon": novo_pokemon
    }
