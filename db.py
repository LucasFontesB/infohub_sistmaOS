import sqlite3

DB_NAME = "ordens_servico.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        email TEXT,
        endereco TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS os (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_entrada TEXT NOT NULL,
        previsao_entrega TEXT,
        cliente_id INTEGER NOT NULL,
        tipo_equipamento TEXT NOT NULL,
        marca_modelo TEXT,
        numero_serie TEXT,
        sistema_operacional TEXT,
        senha_equipamento TEXT,
        servico_solicitado TEXT NOT NULL,
        servico_executado TEXT,
        itens_substituidos TEXT,
        valor_servico REAL DEFAULT 0,
        valor_pecas REAL DEFAULT 0,
        total REAL GENERATED ALWAYS AS (valor_servico + valor_pecas) VIRTUAL,
        garantia TEXT,
        status TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            os_id INTEGER,
            origem TEXT,
            observacoes TEXT
        )
        """)

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