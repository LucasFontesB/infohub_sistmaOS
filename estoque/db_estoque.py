import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.abspath(os.path.join(BASE_DIR, "..", "ordens_servico.db"))

def get_connection():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de produtos/estoque
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,
        quantidade INTEGER DEFAULT 0,
        preco_compra REAL DEFAULT 0.0,  -- preço unitário de compra
        preco_venda REAL DEFAULT 0.0,   -- preço unitário de venda
        data_cadastro TEXT DEFAULT (date('now'))
    )
    """)

    conn.commit()
    conn.close()
    print("Tabelas verificadas/criadas com sucesso.")