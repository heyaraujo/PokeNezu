import os
import psycopg2
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


def _guild(guild_id):
    return str(guild_id) if guild_id else "global"


def iniciar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        guild_id TEXT NOT NULL DEFAULT 'global',
        discord_id TEXT NOT NULL,
        moedas INTEGER DEFAULT 0,
        inicial_escolhido INTEGER DEFAULT 0,
        pokemon_ativo_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pokemons_capturados (
        id SERIAL PRIMARY KEY,
        guild_id TEXT NOT NULL DEFAULT 'global',
        discord_id TEXT NOT NULL,
        nome TEXT NOT NULL,
        nivel INTEGER NOT NULL,
        hp INTEGER NOT NULL,
        ataque INTEGER NOT NULL,
        defesa INTEGER NOT NULL,
        velocidade INTEGER NOT NULL,
        inicial INTEGER DEFAULT 0,
        vendido INTEGER DEFAULT 0,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insignias (
        id SERIAL PRIMARY KEY,
        guild_id TEXT NOT NULL DEFAULT 'global',
        discord_id TEXT NOT NULL,
        nome TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracoes_servidor (
        guild_id TEXT PRIMARY KEY,
        canal_spawn_id TEXT,
        canal_ginasio_id TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketplace (
        id SERIAL PRIMARY KEY,
        guild_id TEXT NOT NULL DEFAULT 'global',
        pokemon_id INTEGER NOT NULL,
        seller_id TEXT NOT NULL,
        preco INTEGER NOT NULL,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS guild_id TEXT DEFAULT 'global'")
    cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS pokemon_ativo_id INTEGER")
    cursor.execute("ALTER TABLE pokemons_capturados ADD COLUMN IF NOT EXISTS guild_id TEXT DEFAULT 'global'")
    cursor.execute("ALTER TABLE pokemons_capturados ADD COLUMN IF NOT EXISTS vendido INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE insignias ADD COLUMN IF NOT EXISTS guild_id TEXT DEFAULT 'global'")
    cursor.execute("ALTER TABLE marketplace ADD COLUMN IF NOT EXISTS guild_id TEXT DEFAULT 'global'")
    cursor.execute("ALTER TABLE marketplace ADD COLUMN IF NOT EXISTS ativo INTEGER DEFAULT 1")
    cursor.execute("ALTER TABLE configuracoes_servidor ADD COLUMN IF NOT EXISTS canal_spawn_id TEXT")
    cursor.execute("ALTER TABLE configuracoes_servidor ADD COLUMN IF NOT EXISTS canal_ginasio_id TEXT")

    cursor.execute("ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS usuarios_discord_id_key")

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS usuarios_guild_discord_unique
    ON usuarios (guild_id, discord_id)
    """)

    conn.commit()
    cursor.close()
    conn.close()


def garantir_usuario(discord_id: int, guild_id=None):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO usuarios (guild_id, discord_id, moedas, inicial_escolhido)
    VALUES (%s, %s, 0, 0)
    ON CONFLICT (guild_id, discord_id) DO NOTHING
    """, (guild_id, str(discord_id)))

    conn.commit()
    cursor.close()
    conn.close()


def usuario_tem_inicial(discord_id: int, guild_id=None):
    garantir_usuario(discord_id, guild_id)
    guild_id = _guild(guild_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT inicial_escolhido
    FROM usuarios
    WHERE guild_id = %s AND discord_id = %s
    """, (guild_id, str(discord_id)))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    return bool(resultado and resultado[0] == 1)


def marcar_inicial_escolhido(discord_id: int, guild_id=None):
    garantir_usuario(discord_id, guild_id)
    guild_id = _guild(guild_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE usuarios
    SET inicial_escolhido = 1
    WHERE guild_id = %s AND discord_id = %s
    """, (guild_id, str(discord_id)))

    conn.commit()
    cursor.close()
    conn.close()


def adicionar_pokemon(discord_id, nome, nivel, hp, ataque, defesa, velocidade, inicial=0, moedas_bonus=10, guild_id=None):
    garantir_usuario(discord_id, guild_id)
    guild_id = _guild(guild_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pokemons_capturados
    (guild_id, discord_id, nome, nivel, hp, ataque, defesa, velocidade, inicial)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """, (
        guild_id,
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

    cursor.execute("""
    UPDATE usuarios
    SET moedas = moedas + %s
    WHERE guild_id = %s AND discord_id = %s
    """, (moedas_bonus, guild_id, str(discord_id)))

    cursor.execute("""
    UPDATE usuarios
    SET pokemon_ativo_id = COALESCE(pokemon_ativo_id, %s)
    WHERE guild_id = %s AND discord_id = %s
    """, (pokemon_id, guild_id, str(discord_id)))

    conn.commit()
    cursor.close()
    conn.close()

    return pokemon_id


def atualizar_pokemon(pokemon_id, nome, hp, ataque, defesa, velocidade):
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


def adicionar_nivel_pokemon(pokemon_id, quantidade=1):
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


def listar_pokemons(discord_id, guild_id=None):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT nome, nivel, hp, ataque, defesa, velocidade, inicial, criado_em
    FROM pokemons_capturados
    WHERE discord_id = %s AND guild_id = %s AND COALESCE(vendido, 0) = 0
    ORDER BY id DESC
    LIMIT 25
    """, (str(discord_id), guild_id))

    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados


def primeiro_pokemon(discord_id, guild_id=None):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, nome, nivel, hp, ataque, defesa, velocidade
    FROM pokemons_capturados
    WHERE discord_id = %s AND guild_id = %s AND COALESCE(vendido, 0) = 0
    ORDER BY id ASC
    LIMIT 1
    """, (str(discord_id), guild_id))

    dados = cursor.fetchone()
    cursor.close()
    conn.close()
    return dados


def definir_pokemon_ativo(discord_id, pokemon_id, guild_id=None):
    garantir_usuario(discord_id, guild_id)
    guild_id = _guild(guild_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM pokemons_capturados
    WHERE id = %s AND discord_id = %s AND guild_id = %s AND COALESCE(vendido, 0) = 0
    """, (pokemon_id, str(discord_id), guild_id))

    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        conn.close()
        return False

    cursor.execute("""
    UPDATE usuarios
    SET pokemon_ativo_id = %s
    WHERE guild_id = %s AND discord_id = %s
    """, (pokemon_id, guild_id, str(discord_id)))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def pokemon_ativo(discord_id, guild_id=None):
    garantir_usuario(discord_id, guild_id)
    guild_id = _guild(guild_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT p.id, p.nome, p.nivel, p.hp, p.ataque, p.defesa, p.velocidade
    FROM usuarios u
    JOIN pokemons_capturados p ON p.id = u.pokemon_ativo_id
    WHERE u.guild_id = %s
      AND u.discord_id = %s
      AND p.guild_id = %s
      AND COALESCE(p.vendido, 0) = 0
    LIMIT 1
    """, (guild_id, str(discord_id), guild_id))

    dados = cursor.fetchone()
    cursor.close()
    conn.close()

    if dados:
        return dados

    return primeiro_pokemon(discord_id, guild_id)


def saldo_usuario(discord_id, guild_id=None):
    garantir_usuario(discord_id, guild_id)
    guild_id = _guild(guild_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT moedas
    FROM usuarios
    WHERE guild_id = %s AND discord_id = %s
    """, (guild_id, str(discord_id)))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    return resultado[0] if resultado else 0


def adicionar_insignia(discord_id, nome, guild_id=None):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO insignias (guild_id, discord_id, nome)
    VALUES (%s, %s, %s)
    """, (guild_id, str(discord_id), nome))

    conn.commit()
    cursor.close()
    conn.close()


def listar_insignias(discord_id, guild_id=None):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT nome, criado_em
    FROM insignias
    WHERE guild_id = %s AND discord_id = %s
    ORDER BY criado_em DESC
    """, (guild_id, str(discord_id)))

    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados


def configurar_canal_spawn(guild_id, canal_id):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO configuracoes_servidor (guild_id, canal_spawn_id)
    VALUES (%s, %s)
    ON CONFLICT (guild_id)
    DO UPDATE SET canal_spawn_id = EXCLUDED.canal_spawn_id
    """, (guild_id, str(canal_id)))

    conn.commit()
    cursor.close()
    conn.close()


def buscar_canal_spawn(guild_id):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT canal_spawn_id
    FROM configuracoes_servidor
    WHERE guild_id = %s
    LIMIT 1
    """, (guild_id,))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    return int(resultado[0]) if resultado and resultado[0] else None


def configurar_canal_ginasio(guild_id, canal_id):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO configuracoes_servidor (guild_id, canal_ginasio_id)
    VALUES (%s, %s)
    ON CONFLICT (guild_id)
    DO UPDATE SET canal_ginasio_id = EXCLUDED.canal_ginasio_id
    """, (guild_id, str(canal_id)))

    conn.commit()
    cursor.close()
    conn.close()


def buscar_canal_ginasio(guild_id):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT canal_ginasio_id
    FROM configuracoes_servidor
    WHERE guild_id = %s
    LIMIT 1
    """, (guild_id,))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    return int(resultado[0]) if resultado and resultado[0] else None


def criar_anuncio_marketplace(discord_id, pokemon_id, preco, guild_id=None):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM pokemons_capturados
    WHERE id = %s AND discord_id = %s AND guild_id = %s AND COALESCE(vendido, 0) = 0
    """, (pokemon_id, str(discord_id), guild_id))

    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        conn.close()
        return None

    cursor.execute("""
    UPDATE pokemons_capturados
    SET vendido = 1
    WHERE id = %s AND guild_id = %s
    """, (pokemon_id, guild_id))

    cursor.execute("""
    INSERT INTO marketplace (guild_id, pokemon_id, seller_id, preco, ativo)
    VALUES (%s, %s, %s, %s, 1)
    RETURNING id
    """, (guild_id, pokemon_id, str(discord_id), preco))

    anuncio_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return anuncio_id


def listar_marketplace_ativos(guild_id=None, limite=15):
    guild_id = _guild(guild_id)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.id,
        p.id,
        m.seller_id,
        m.preco,
        p.nome,
        p.nivel,
        p.hp,
        p.ataque,
        p.defesa,
        p.velocidade
    FROM marketplace m
    JOIN pokemons_capturados p ON p.id = m.pokemon_id
    WHERE m.guild_id = %s AND COALESCE(m.ativo, 1) = 1
    ORDER BY m.id DESC
    LIMIT %s
    """, (guild_id, limite))

    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    return dados


def comprar_marketplace_item(comprador_id, anuncio_id, guild_id=None):
    guild_id = _guild(guild_id)
    comprador_id = str(comprador_id)

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT m.id, m.seller_id, m.pokemon_id, m.preco, p.nome
        FROM marketplace m
        JOIN pokemons_capturados p ON p.id = m.pokemon_id
        WHERE m.id = %s AND m.guild_id = %s AND COALESCE(m.ativo, 1) = 1
        FOR UPDATE
        """, (anuncio_id, guild_id))

        anuncio = cursor.fetchone()

        if not anuncio:
            conn.rollback()
            return {"ok": False, "erro": "Anúncio não encontrado ou já comprado."}

        _, seller_id, pokemon_id, preco, nome = anuncio

        if str(seller_id) == comprador_id:
            conn.rollback()
            return {"ok": False, "erro": "Você não pode comprar seu próprio Pokémon."}

        garantir_usuario(comprador_id, guild_id)
        garantir_usuario(seller_id, guild_id)

        cursor.execute("""
        SELECT moedas
        FROM usuarios
        WHERE guild_id = %s AND discord_id = %s
        FOR UPDATE
        """, (guild_id, comprador_id))

        saldo = cursor.fetchone()

        if not saldo or saldo[0] < preco:
            conn.rollback()
            return {"ok": False, "erro": "Você não tem moedas suficientes."}

        cursor.execute("""
        UPDATE usuarios
        SET moedas = moedas - %s
        WHERE guild_id = %s AND discord_id = %s
        """, (preco, guild_id, comprador_id))

        cursor.execute("""
        UPDATE usuarios
        SET moedas = moedas + %s
        WHERE guild_id = %s AND discord_id = %s
        """, (preco, guild_id, str(seller_id)))

        cursor.execute("""
        UPDATE pokemons_capturados
        SET discord_id = %s, vendido = 0
        WHERE id = %s AND guild_id = %s
        """, (comprador_id, pokemon_id, guild_id))

        cursor.execute("""
        UPDATE marketplace
        SET ativo = 0
        WHERE id = %s AND guild_id = %s
        """, (anuncio_id, guild_id))

        cursor.execute("""
        UPDATE usuarios
        SET pokemon_ativo_id = COALESCE(pokemon_ativo_id, %s)
        WHERE guild_id = %s AND discord_id = %s
        """, (pokemon_id, guild_id, comprador_id))

        conn.commit()
        return {"ok": True, "pokemon": nome, "preco": preco}

    except Exception as erro:
        conn.rollback()
        return {"ok": False, "erro": str(erro)}

    finally:
        cursor.close()
        conn.close()