from db import get_connection


def adicionar_cliente(nome, telefone, email, endereco):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clientes (nome, telefone, email, endereco)
        VALUES (?, ?, ?, ?)
    """, (nome, telefone, email, endereco))
    conn.commit()
    conn.close()

def listar_clientes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, telefone, email, endereco FROM clientes")
    clientes = cur.fetchall()
    conn.close()
    return clientes

def atualizar_cliente(cliente_id, nome, telefone, email, endereco):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE clientes 
        SET nome=?, telefone=?, email=?, endereco=? 
        WHERE id=?
    """, (nome, telefone, email, endereco, cliente_id))
    conn.commit()
    conn.close()

def excluir_cliente(cliente_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()

def buscar_cliente_por_id(cliente_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, telefone, email, endereco
        FROM clientes
        WHERE id = ?
    """, (cliente_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nome": row[1],
            "telefone": row[2],
            "email": row[3],
            "endereco": row[4]
        }
    return None