# database.py atualizado com canal de ginásio

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
    CREATE TABLE IF NOT EXISTS configuracoes_servidor (
        guild_id TEXT PRIMARY KEY,
        canal_spawn_id TEXT,
        canal_ginasio_id TEXT
    )
    """)

    cursor.execute("""
    ALTER TABLE configuracoes_servidor
    ADD COLUMN IF NOT EXISTS canal_ginasio_id TEXT
    """)

    conn.commit()
    cursor.close()
    conn.close()

def configurar_canal_ginasio(guild_id: int, canal_id: int):
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

def buscar_canal_ginasio(guild_id: int):
    guild_id = _guild(guild_id)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT canal_ginasio_id
    FROM configuracoes_servidor
    WHERE guild_id = %s
    """, (guild_id,))

    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    return int(resultado[0]) if resultado and resultado[0] else None
