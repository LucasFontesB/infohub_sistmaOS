from db import get_connection
from datetime import datetime

def buscar_os_por_id(os_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            o.id,
            o.cliente_id,
            c.nome as cliente_nome,
            o.tipo_equipamento,
            o.marca_modelo,
            o.numero_serie,
            o.sistema_operacional,
            o.senha_equipamento,
            o.previsao_entrega,
            o.servico_solicitado,
            o.servico_executado,
            o.itens_substituidos,
            o.valor_servico,
            o.valor_pecas,
            o.garantia,
            o.status
        FROM os o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE o.id = ?
    """, (os_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    # transforma em dicionário
    os_dados = {
        "id": row[0],
        "cliente_id": row[1],
        "cliente_nome": row[2],
        "tipo_equipamento": row[3],
        "marca_modelo": row[4],
        "numero_serie": row[5],
        "sistema_operacional": row[6],
        "senha_equipamento": row[7],
        "previsao_entrega": row[8],
        "servico_solicitado": row[9],
        "servico_executado": row[10],
        "itens_substituidos": row[11],
        "valor_servico": row[12],
        "valor_pecas": row[13],
        "garantia": row[14],
        "status": row[15]
    }

    return os_dados

def adicionar_os(cliente_id, tipo_equipamento, servico_solicitado, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    data_entrada = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO os (
        data_entrada, previsao_entrega, cliente_id, tipo_equipamento,
        marca_modelo, numero_serie, sistema_operacional, senha_equipamento,
        servico_solicitado, servico_executado, itens_substituidos,
        valor_servico, valor_pecas, garantia, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data_entrada,
        kwargs.get("previsao_entrega"),
        cliente_id,
        tipo_equipamento,
        kwargs.get("marca_modelo"),
        kwargs.get("numero_serie"),
        kwargs.get("sistema_operacional"),
        kwargs.get("senha_equipamento"),
        servico_solicitado,
        kwargs.get("servico_executado"),
        kwargs.get("itens_substituidos"),
        kwargs.get("valor_servico", 0),
        kwargs.get("valor_pecas", 0),
        kwargs.get("garantia"),
        kwargs.get("status"),
    ))

    conn.commit()
    conn.close()
    print("OS adicionada com sucesso!")

def listar_os():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT os.id, os.data_entrada, clientes.nome, os.tipo_equipamento, os.servico_solicitado, os.total, os.status 
    FROM os
    JOIN clientes ON os.cliente_id = clientes.id
    """)
    ordens = cursor.fetchall()
    conn.close()
    return ordens

def atualizar_os(
    os_id,
    cliente_id,
    tipo_equipamento,
    marca_modelo,
    numero_serie,
    sistema_operacional,
    senha_equipamento,
    previsao_entrega,
    servico_solicitado,
    servico_executado,
    itens_substituidos,
    valor_servico,
    valor_pecas,
    garantia,
    status
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE os
        SET cliente_id=?,
            tipo_equipamento=?,
            marca_modelo=?,
            numero_serie=?,
            sistema_operacional=?,
            senha_equipamento=?,
            previsao_entrega=?,
            servico_solicitado=?,
            servico_executado=?,
            itens_substituidos=?,
            valor_servico=?,
            valor_pecas=?,
            garantia=?,
            status=?
        WHERE id=?
    """, (
        cliente_id,
        tipo_equipamento,
        marca_modelo,
        numero_serie,
        sistema_operacional,
        senha_equipamento,
        previsao_entrega,
        servico_solicitado,
        servico_executado,
        itens_substituidos,
        valor_servico,
        valor_pecas,
        garantia,
        status,
        os_id
    ))
    conn.commit()
    conn.close()
    print(f"OS #{os_id} atualizada com sucesso!")

def excluir_os(os_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM os WHERE id=?", (os_id,))
    conn.commit()
    conn.close()