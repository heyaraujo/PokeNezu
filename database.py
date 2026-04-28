import sqlite3
from pathlib import Path

DB_PATH = Path("pokebot.db")


def conectar():
    return sqlite3.connect(DB_PATH)


def iniciar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT UNIQUE NOT NULL,
        moedas INTEGER DEFAULT 0,
        inicial_escolhido INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pokemons_capturados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()


def garantir_usuario(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (discord_id, moedas, inicial_escolhido) VALUES (?, ?, ?)",
        (str(discord_id), 0, 0)
    )

    conn.commit()
    conn.close()


def usuario_tem_inicial(discord_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT inicial_escolhido FROM usuarios WHERE discord_id = ?", (str(discord_id),))
    resultado = cursor.fetchone()
    conn.close()

    return bool(resultado and resultado[0] == 1)


def marcar_inicial_escolhido(discord_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET inicial_escolhido = 1 WHERE discord_id = ?", (str(discord_id),))
    conn.commit()
    conn.close()


def adicionar_pokemon(discord_id: int, nome: str, nivel: int, hp: int, ataque: int, defesa: int, velocidade: int, inicial: int = 0, moedas_bonus: int = 10):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pokemons_capturados 
    (discord_id, nome, nivel, hp, ataque, defesa, velocidade, inicial)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(discord_id), nome, nivel, hp, ataque, defesa, velocidade, inicial))

    pokemon_id = cursor.lastrowid

    cursor.execute("UPDATE usuarios SET moedas = moedas + ? WHERE discord_id = ?", (moedas_bonus, str(discord_id)))

    conn.commit()
    conn.close()

    return pokemon_id


def atualizar_pokemon(pokemon_id: int, nome: str, hp: int, ataque: int, defesa: int, velocidade: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE pokemons_capturados
    SET nome = ?, hp = ?, ataque = ?, defesa = ?, velocidade = ?
    WHERE id = ?
    """, (nome, hp, ataque, defesa, velocidade, pokemon_id))

    conn.commit()
    conn.close()


def adicionar_nivel_pokemon(pokemon_id: int, quantidade: int = 1):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE pokemons_capturados
    SET nivel = nivel + ?
    WHERE id = ?
    """, (quantidade, pokemon_id))

    conn.commit()
    conn.close()


def listar_pokemons(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT nome, nivel, hp, ataque, defesa, velocidade, inicial, criado_em
    FROM pokemons_capturados
    WHERE discord_id = ?
    ORDER BY id DESC
    LIMIT 25
    """, (str(discord_id),))

    dados = cursor.fetchall()
    conn.close()
    return dados


def primeiro_pokemon(discord_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, nome, nivel, hp, ataque, defesa, velocidade
    FROM pokemons_capturados
    WHERE discord_id = ?
    ORDER BY id ASC
    LIMIT 1
    """, (str(discord_id),))

    dados = cursor.fetchone()
    conn.close()
    return dados


def saldo_usuario(discord_id: int):
    garantir_usuario(discord_id)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT moedas FROM usuarios WHERE discord_id = ?", (str(discord_id),))
    resultado = cursor.fetchone()
    conn.close()

    return resultado[0] if resultado else 0
