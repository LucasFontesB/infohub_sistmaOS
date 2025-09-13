import tkinter as tk
from tkinter import ttk, messagebox
from db import criar_tabelas, get_connection
from adicionar_clientes import ClienteUI        # ajustar se seu arquivo for ui_clientes.py
from clientes import listar_clientes
from ordens import listar_os, adicionar_os, atualizar_os, excluir_os, buscar_os_por_id
from Impressao import imprimir_os
from financeiro.financeiro_view import abrir_financeiro
from datetime import datetime
from estoque.estoque_view import abrir_estoque
from relatorios.relatorios_view import abrir_relatorio_financeiro


TIPOS_EQUIPAMENTOS = ["Computador Desktop", "Notebook", "Impressora", "Outro"]

def abrir_clientes():
    win = tk.Toplevel(root)
    ClienteUI(win)

def abrir_nova_os():
    win = tk.Toplevel(root)
    win.title("Nova Ordem de Serviço")
    win.geometry("620x520")

    frm = tk.Frame(win, padx=10, pady=10)
    frm.pack(fill="both", expand=True)

    # ----- campos -----
    tk.Label(frm, text="Cliente:").grid(row=0, column=0, sticky="w")
    clientes = listar_clientes()
    cliente_opts = [f"{c[0]} - {c[1]}" for c in clientes]  # espera (id, nome, ...)
    cliente_var = tk.StringVar()
    cliente_cb = ttk.Combobox(frm, values=cliente_opts, textvariable=cliente_var, width=45)
    cliente_cb.grid(row=0, column=1, columnspan=3, pady=3, sticky="w")

    tk.Label(frm, text="Tipo equipamento:").grid(row=1, column=0, sticky="w")
    tipo_var = tk.StringVar()
    tipo_cb = ttk.Combobox(frm, values=TIPOS_EQUIPAMENTOS, textvariable=tipo_var, width=30)
    tipo_cb.grid(row=1, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Marca / Modelo:").grid(row=2, column=0, sticky="w")
    marca_entry = tk.Entry(frm, width=40)
    marca_entry.grid(row=2, column=1, columnspan=3, pady=3, sticky="w")

    tk.Label(frm, text="Nº de série:").grid(row=3, column=0, sticky="w")
    serial_entry = tk.Entry(frm, width=30)
    serial_entry.grid(row=3, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Sistema operacional:").grid(row=4, column=0, sticky="w")
    so_entry = tk.Entry(frm, width=30)
    so_entry.grid(row=4, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Senha equipamento:").grid(row=5, column=0, sticky="w")
    senha_entry = tk.Entry(frm, width=30)
    senha_entry.grid(row=5, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Previsão de entrega (YYYY-MM-DD):").grid(row=6, column=0, sticky="w")
    previsao_entry = tk.Entry(frm, width=20)
    previsao_entry.grid(row=6, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Serviço solicitado / Problema:").grid(row=7, column=0, sticky="w")
    serv_solicitado_txt = tk.Text(frm, width=50, height=4)
    serv_solicitado_txt.grid(row=7, column=1, columnspan=3, pady=3, sticky="w")

    tk.Label(frm, text="Serviço executado / Observações:").grid(row=8, column=0, sticky="w")
    serv_executado_txt = tk.Text(frm, width=50, height=4)
    serv_executado_txt.grid(row=8, column=1, columnspan=3, pady=3, sticky="w")

    tk.Label(frm, text="Itens substituídos / consumíveis:").grid(row=9, column=0, sticky="w")
    itens_txt = tk.Text(frm, width=50, height=3)
    itens_txt.grid(row=9, column=1, columnspan=3, pady=3, sticky="w")

    tk.Label(frm, text="Valor serviço (ex: 150.50):").grid(row=10, column=0, sticky="w")
    valor_serv_entry = tk.Entry(frm, width=15)
    valor_serv_entry.grid(row=10, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Valor peças (ex: 80.00):").grid(row=10, column=2, sticky="w")
    valor_pecas_entry = tk.Entry(frm, width=15)
    valor_pecas_entry.grid(row=10, column=3, pady=3, sticky="w")

    tk.Label(frm, text="Garantia (ex: 30 dias):").grid(row=11, column=0, sticky="w")
    garantia_entry = tk.Entry(frm, width=20)
    garantia_entry.grid(row=11, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Status:").grid(row=12, column=0, sticky="w")
    status_entry = tk.Entry(frm, width=30)
    status_entry.grid(row=12, column=1, pady=3, sticky="w")
    status_entry.insert(0, "Em andamento")

    # ----- ações -----
    def salvar_os():
        sel_cliente = cliente_var.get().strip()
        if not sel_cliente:
            messagebox.showerror("Erro", "Selecione um cliente.")
            return
        try:
            cliente_id = int(sel_cliente.split(" - ")[0])
        except Exception:
            messagebox.showerror("Erro", "Seleção de cliente inválida.")
            return

        tipo = tipo_var.get().strip() or "Outro"
        marca = marca_entry.get().strip()
        serial = serial_entry.get().strip()
        so = so_entry.get().strip()
        senha = senha_entry.get().strip()
        previsao = previsao_entry.get().strip() or None
        serv_solicitado = serv_solicitado_txt.get("1.0", "end").strip()
        serv_executado = serv_executado_txt.get("1.0", "end").strip()
        itens = itens_txt.get("1.0", "end").strip()
        status = status_entry.get().strip()
        try:
            valor_serv = float(valor_serv_entry.get().strip()) if valor_serv_entry.get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Valor serviço inválido.")
            return
        try:
            valor_pecas = float(valor_pecas_entry.get().strip()) if valor_pecas_entry.get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Valor peças inválido.")
            return
        garantia = garantia_entry.get().strip()

        # Chama função do módulo ordens.py
        adicionar_os(
            cliente_id=cliente_id,
            tipo_equipamento=tipo,
            servico_solicitado=serv_solicitado,
            marca_modelo=marca,
            numero_serie=serial,
            sistema_operacional=so,
            senha_equipamento=senha,
            servico_executado=serv_executado,
            itens_substituidos=itens,
            valor_servico=valor_serv,
            valor_pecas=valor_pecas,
            previsao_entrega=previsao,
            garantia=garantia,
            status=status
        )

        messagebox.showinfo("OK", "OS adicionada com sucesso.")
        win.destroy()
        refresh_os_list()

    btn_salvar = tk.Button(frm, text="Salvar OS", command=salvar_os, width=15)
    btn_salvar.grid(row=13, column=1, pady=12)

    btn_cancel = tk.Button(frm, text="Cancelar", command=win.destroy, width=15)
    btn_cancel.grid(row=13, column=2, pady=12)

def refresh_os_list():
    # limpa tabela
    for row in tree.get_children():
        tree.delete(row)

    rows = listar_os()  # espera lista de tuples vindas do ordens.listar_os()
    # mapeia defensivamente os índices caso a função listar_os retorne colunas em ordens diferentes
    for r in rows:
        r = list(r)
        _id = r[0] if len(r) > 0 else ""
        data = r[1] if len(r) > 1 else ""
        if data:
            try:
                data = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                pass  # caso a string não esteja no formato esperado, mantém como está
        cliente = r[2] if len(r) > 2 else ""
        equipamento = r[3] if len(r) > 3 else ""
        problema = r[4] if len(r) > 4 else ""
        total = r[5] if len(r) > 5 else ""
        status = r[6] if len(r) > 6 else ""
        if isinstance(total, (int, float)):
            total_display = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif total:
            total_display = str(total)
        else:
            total_display = "-"
        tree.insert("", "end", values=(_id, data, cliente, equipamento, problema, status, total_display))

def abrir_editar_os(os_id):
    os_dados = buscar_os_por_id(os_id)

    if not os_dados:
        messagebox.showerror("Erro", f"OS #{os_id} não encontrada")
        return

    win = tk.Toplevel(root)
    win.title(f"Editar OS #{os_id}")
    win.geometry("620x520")

    frm = tk.Frame(win, padx=10, pady=10)
    frm.pack(fill="both", expand=True)

    # Campos preenchidos
    tk.Label(frm, text="Cliente:").grid(row=0, column=0, sticky="w")
    clientes = listar_clientes()
    cliente_opts = [f"{c[0]} - {c[1]}" for c in clientes]
    cliente_var = tk.StringVar(value=f"{os_dados['cliente_id']} - {os_dados['cliente_nome']}")
    cliente_cb = ttk.Combobox(frm, values=cliente_opts, textvariable=cliente_var, width=45)
    cliente_cb.grid(row=0, column=1, columnspan=3, pady=3, sticky="w")

    tk.Label(frm, text="Tipo equipamento:").grid(row=1, column=0, sticky="w")
    tipo_var = tk.StringVar(value=os_dados['tipo_equipamento'])
    tipo_cb = ttk.Combobox(frm, values=TIPOS_EQUIPAMENTOS, textvariable=tipo_var, width=30)
    tipo_cb.grid(row=1, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Marca / Modelo:").grid(row=2, column=0, sticky="w")
    marca_entry = tk.Entry(frm, width=40)
    marca_entry.grid(row=2, column=1, columnspan=3, pady=3, sticky="w")
    marca_entry.insert(0, os_dados['marca_modelo'])

    tk.Label(frm, text="Nº de série:").grid(row=3, column=0, sticky="w")
    serial_entry = tk.Entry(frm, width=30)
    serial_entry.grid(row=3, column=1, pady=3, sticky="w")
    serial_entry.insert(0, os_dados['numero_serie'])

    tk.Label(frm, text="Sistema operacional:").grid(row=4, column=0, sticky="w")
    so_entry = tk.Entry(frm, width=30)
    so_entry.grid(row=4, column=1, pady=3, sticky="w")
    so_entry.insert(0, os_dados['sistema_operacional'])

    tk.Label(frm, text="Senha equipamento:").grid(row=5, column=0, sticky="w")
    senha_entry = tk.Entry(frm, width=30)
    senha_entry.grid(row=5, column=1, pady=3, sticky="w")
    senha_entry.insert(0, os_dados['senha_equipamento'])

    tk.Label(frm, text="Previsão de entrega (YYYY-MM-DD):").grid(row=6, column=0, sticky="w")
    previsao_entry = tk.Entry(frm, width=20)
    previsao_entry.grid(row=6, column=1, pady=3, sticky="w")
    previsao_entry.insert(0, os_dados.get('previsao_entrega') or "")

    tk.Label(frm, text="Serviço solicitado / Problema:").grid(row=7, column=0, sticky="w")
    serv_solicitado_txt = tk.Text(frm, width=50, height=4)
    serv_solicitado_txt.grid(row=7, column=1, columnspan=3, pady=3, sticky="w")
    serv_solicitado_txt.insert("1.0", os_dados['servico_solicitado'])

    tk.Label(frm, text="Serviço executado / Observações:").grid(row=8, column=0, sticky="w")
    serv_executado_txt = tk.Text(frm, width=50, height=4)
    serv_executado_txt.grid(row=8, column=1, columnspan=3, pady=3, sticky="w")
    serv_executado_txt.insert("1.0", os_dados['servico_executado'])

    tk.Label(frm, text="Itens substituídos / consumíveis:").grid(row=9, column=0, sticky="w")
    itens_txt = tk.Text(frm, width=50, height=3)
    itens_txt.grid(row=9, column=1, columnspan=3, pady=3, sticky="w")
    itens_txt.insert("1.0", os_dados['itens_substituidos'])

    tk.Label(frm, text="Valor serviço (ex: 150.50):").grid(row=10, column=0, sticky="w")
    valor_serv_entry = tk.Entry(frm, width=15)
    valor_serv_entry.grid(row=10, column=1, pady=3, sticky="w")
    valor_serv_entry.insert(0, os_dados['valor_servico'])

    tk.Label(frm, text="Valor peças (ex: 80.00):").grid(row=10, column=2, sticky="w")
    valor_pecas_entry = tk.Entry(frm, width=15)
    valor_pecas_entry.grid(row=10, column=3, pady=3, sticky="w")
    valor_pecas_entry.insert(0, os_dados['valor_pecas'])

    tk.Label(frm, text="Garantia (ex: 30 dias):").grid(row=11, column=0, sticky="w")
    garantia_entry = tk.Entry(frm, width=20)
    garantia_entry.grid(row=11, column=1, pady=3, sticky="w")
    garantia_entry.insert(0, os_dados['garantia'])

    tk.Label(frm, text="Status:").grid(row=12, column=0, sticky="w")
    status_entry = tk.Entry(frm, width=30)
    status_entry.grid(row=12, column=1, pady=3, sticky="w")
    status_entry.insert(0, os_dados['status'])

    # ----- ações -----
    def salvar_alteracoes():
        # pega valores do formulário
        cliente_id = int(cliente_var.get().split(" - ")[0])
        tipo_equipamento = tipo_var.get()
        marca_modelo = marca_entry.get()
        numero_serie = serial_entry.get()
        sistema_operacional = so_entry.get()
        senha_equipamento = senha_entry.get()
        previsao_entrega = previsao_entry.get() or None
        servico_solicitado = serv_solicitado_txt.get("1.0", "end").strip()
        servico_executado = serv_executado_txt.get("1.0", "end").strip()
        itens_substituidos = itens_txt.get("1.0", "end").strip()
        valor_servico = float(valor_serv_entry.get() or 0)
        valor_pecas = float(valor_pecas_entry.get() or 0)
        garantia = garantia_entry.get()
        status = status_entry.get().strip()

        # chama a função de atualização
        atualizar_os(
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
        )

        messagebox.showinfo("OK", f"OS #{os_id} atualizada com sucesso.")
        win.destroy()
        refresh_os_list()

    def confirmar_exclusao():
        if messagebox.askyesno("Confirmação", f"Deseja realmente excluir a OS #{os_id}?"):
            excluir_os(os_id)
            win.destroy()
            refresh_os_list()

    btn_salvar = tk.Button(frm, text="Salvar Alterações", command=salvar_alteracoes, width=15)
    btn_salvar.grid(row=13, column=0, pady=12)

    btn_cancel = tk.Button(frm, text="Cancelar", command=win.destroy, width=15)
    btn_cancel.grid(row=13, column=1, pady=12)

    btn_deletar = tk.Button(frm, text="Deletar", command=confirmar_exclusao)
    btn_deletar.grid(row=13, column=2, pady=12)

    btn_imprimir = tk.Button(frm, text="PDF", command= lambda: imprimir_os(os_id))
    btn_imprimir.grid(row=13, column=3, pady=12)


def on_double_click(event):
    item = tree.selection()
    if not item:
        return
    os_id = tree.item(item[0])["values"][0]
    abrir_editar_os(os_id)

# ----- janela principal -----
root = tk.Tk()
root.title("Sistema de OS")
root.geometry("1500x600")

frame_principal = tk.Frame(root)
frame_principal.pack(fill="both", expand=True)

# lateral
frame_menu = tk.Frame(frame_principal, bg="#2c3e50", width=220)
frame_menu.pack(side="left", fill="y")
frame_menu.pack_propagate(False)

tk.Label(frame_menu, text="InfoHUB", bg="#2c3e50", fg="white", font=("Arial", 16, "bold")).pack(pady=18)

tk.Button(frame_menu, text="Nova OS", width=20, command=abrir_nova_os).pack(pady=6)
tk.Button(frame_menu, text="Gestão de Clientes", width=20, command=abrir_clientes).pack(pady=6)
tk.Button(frame_menu, text="Atualizar lista OS", width=20, command=refresh_os_list).pack(pady=6)
tk.Button(frame_menu, text="Financeiro", width=20, command=abrir_financeiro).pack(pady=6)
tk.Button(frame_menu, text="Estoque", width=20, command= lambda: abrir_estoque(root)).pack(pady=6)
tk.Button(frame_menu, text="Relatórios", width=20, command=abrir_relatorio_financeiro).pack(pady=6)
tk.Button(frame_menu, text="Sair", width=20, command=root.destroy).pack(side="bottom", pady=20)

# conteúdo central
frame_conteudo = tk.Frame(frame_principal)
frame_conteudo.pack(side="left", fill="both", expand=True)

frame_busca = tk.Frame(frame_conteudo)
frame_busca.pack(pady=5)

tk.Label(frame_busca, text="Buscar OS:").pack(side="left", padx=5)

entrada_busca = tk.Entry(frame_busca, width=40)
entrada_busca.pack(side="left", padx=5)


def buscar_os():
    termo = entrada_busca.get().strip().lower()
    for item in tree.get_children():
        tree.delete(item)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT os.id, os.data_entrada, clientes.nome, os.tipo_equipamento, 
               os.servico_solicitado, os.status, os.total
        FROM os
        INNER JOIN clientes ON os.cliente_id = clientes.id
        WHERE LOWER(clientes.nome) LIKE ? OR CAST(os.id AS TEXT) LIKE ?
        """, (f"%{termo}%", f"%{termo}%"))

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        id_, data_entrada, nome, equipamento, problema, status, total = row
        total_formatado = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tree.insert("", "end", values=(id_, data_entrada, nome, equipamento, problema, status, total_formatado))

tk.Button(frame_busca, text="Buscar", command=buscar_os).pack(side="left", padx=5)

# botão para limpar a busca e voltar lista completa
def limpar_busca():
    entrada_busca.delete(0, tk.END)
    refresh_os_list()

tk.Button(frame_busca, text="Limpar", command=limpar_busca).pack(side="left", padx=5)

tk.Label(frame_conteudo, text="Ordens de Serviço", font=("Arial", 16)).pack(pady=10)

cols = ("ID", "Data Entrada", "Cliente", "Equipamento", "Problema", "Status", "Total")
tree = ttk.Treeview(frame_conteudo, columns=cols, show="headings")
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=140 if c != "Problema" else 240, anchor="center")
tree.pack(fill="both", expand=True, padx=10, pady=10)
tree.bind("<Double-1>", on_double_click)

# scrollbar
vsb = ttk.Scrollbar(frame_conteudo, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.place(in_=tree, relx=1.0, relheight=1.0, bordermode="outside")

# ----- init -----
criar_tabelas()
refresh_os_list()

root.mainloop()