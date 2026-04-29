import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


DATABASE_URL = os.getenv("DATABASE_URL")


def get_database_url():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não configurada no Render.")

    if "sslmode=" not in DATABASE_URL:
        parsed = urlparse(DATABASE_URL)
        query = dict(parse_qsl(parsed.query))
        query["sslmode"] = "require"
        parsed = parsed._replace(query=urlencode(query))
        return urlunparse(parsed)

    return DATABASE_URL


def conectar():
    return psycopg2.connect(get_database_url())


def iniciar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        discord_id TEXT UNIQUE NOT NULL,
        moedas INTEGER DEFAULT 0,
        inicial_escolhido INTEGER DEFAULT 0,
        pokemon_ativo_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pokemons_capturados (
        id SERIAL PRIMARY KEY,
        discord_id TEXT NOT NULL,
        nome TEXT NOT NULL,
        nivel INTEGER NOT NULL,
        hp INTEGER NOT NULL,
        ataque INTEGER NOT NULL,
        defesa INTEGER NOT NULL,
        velocidade INTEGER NOT NULL,
        inicial INTEGER DEFAULT 0,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insignias (
        id SERIAL PRIMARY KEY,
        discord_id TEXT NOT NULL,
        nome TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def garantir_usuario(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO usuarios (discord_id, moedas, inicial_escolhido)
    VALUES (%s, %s, %s)
    ON CONFLICT (discord_id) DO NOTHING
    """, (str(discord_id), 0, 0))

    conn.commit()
    cursor.close()
    conn.close()


def usuario_tem_inicial(discord_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT inicial_escolhido FROM usuarios WHERE discord_id = %s",
        (str(discord_id),)
    )

    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    return bool(resultado and resultado[0] == 1)


def marcar_inicial_escolhido(discord_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE usuarios SET inicial_escolhido = 1 WHERE discord_id = %s",
        (str(discord_id),)
    )

    conn.commit()
    cursor.close()
    conn.close()


def adicionar_pokemon(
    discord_id: int,
    nome: str,
    nivel: int,
    hp: int,
    ataque: int,
    defesa: int,
    velocidade: int,
    inicial: int = 0,
    moedas_bonus: int = 10
):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pokemons_capturados
    (discord_id, nome, nivel, hp, ataque, defesa, velocidade, inicial)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """, (
        str(discord_id),
        nome,
        nivel,
        hp,
        ataque,
        defesa,
        velocidade,
        inicial
    ))

    pokemon_id = cursor.fetchone()[0]

    cursor.execute(
        "UPDATE usuarios SET moedas = moedas + %s WHERE discord_id = %s",
        (moedas_bonus, str(discord_id))
    )

    cursor.execute("""
    UPDATE usuarios
    SET pokemon_ativo_id = COALESCE(pokemon_ativo_id, %s)
    WHERE discord_id = %s
    """, (pokemon_id, str(discord_id)))

    conn.commit()
    cursor.close()
    conn.close()

    return pokemon_id


def atualizar_pokemon(pokemon_id: int, nome: str, hp: int, ataque: int, defesa: int, velocidade: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE pokemons_capturados
    SET nome = %s, hp = %s, ataque = %s, defesa = %s, velocidade = %s
    WHERE id = %s
    """, (nome, hp, ataque, defesa, velocidade, pokemon_id))

    conn.commit()
    cursor.close()
    conn.close()


def adicionar_nivel_pokemon(pokemon_id: int, quantidade: int = 1):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE pokemons_capturados
    SET nivel = nivel + %s
    WHERE id = %s
    """, (quantidade, pokemon_id))

    conn.commit()
    cursor.close()
    conn.close()


def listar_pokemons(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT nome, nivel, hp, ataque, defesa, velocidade, inicial, criado_em
    FROM pokemons_capturados
    WHERE discord_id = %s
    ORDER BY id DESC
    LIMIT 25
    """, (str(discord_id),))

    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados


def listar_pokemons_com_id(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, nome, nivel, hp, ataque, defesa, velocidade, inicial, criado_em
    FROM pokemons_capturados
    WHERE discord_id = %s
    ORDER BY id DESC
    LIMIT 25
    """, (str(discord_id),))

    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados


def definir_pokemon_ativo(discord_id: int, pokemon_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id FROM pokemons_capturados
    WHERE id = %s AND discord_id = %s
    """, (pokemon_id, str(discord_id)))

    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        conn.close()
        return False

    cursor.execute("""
    UPDATE usuarios
    SET pokemon_ativo_id = %s
    WHERE discord_id = %s
    """, (pokemon_id, str(discord_id)))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def pokemon_ativo(discord_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT p.id, p.nome, p.nivel, p.hp, p.ataque, p.defesa, p.velocidade
    FROM usuarios u
    JOIN pokemons_capturados p ON p.id = u.pokemon_ativo_id
    WHERE u.discord_id = %s
    LIMIT 1
    """, (str(discord_id),))

    dados = cursor.fetchone()

    cursor.close()
    conn.close()

    if dados:
        return dados

    return primeiro_pokemon(discord_id)


def primeiro_pokemon(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, nome, nivel, hp, ataque, defesa, velocidade
    FROM pokemons_capturados
    WHERE discord_id = %s
    ORDER BY id ASC
    LIMIT 1
    """, (str(discord_id),))

    dados = cursor.fetchone()

    cursor.close()
    conn.close()

    return dados


def saldo_usuario(discord_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT moedas FROM usuarios WHERE discord_id = %s",
        (str(discord_id),)
    )

    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    return resultado[0] if resultado else 0


def adicionar_insignia(discord_id: int, nome: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO insignias (discord_id, nome)
    VALUES (%s, %s)
    """, (str(discord_id), nome))

    conn.commit()
    cursor.close()
    conn.close()


def listar_insignias(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT nome, criado_em
    FROM insignias
    WHERE discord_id = %s
    ORDER BY criado_em DESC
    """, (str(discord_id),))

    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados