from financeiro.db_financeiro import criar_tabelas
import tkinter as tk
from tkinter import ttk, messagebox
from financeiro.db_financeiro import get_connection

def abrir_financeiro():
    win = tk.Toplevel()
    win.title("Financeiro - InfoHub")
    win.geometry("860x350")

    frm = tk.Frame(win, padx=10, pady=10)
    frm.pack(fill="x")  # aqui pode usar pack, mas dentro do frm só grid

    # Linha 0
    tk.Label(frm, text="Data Início (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    data_inicio_var = tk.StringVar()
    tk.Entry(frm, textvariable=data_inicio_var, width=15).grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(frm, text="Data Fim (YYYY-MM-DD):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    data_fim_var = tk.StringVar()
    tk.Entry(frm, textvariable=data_fim_var, width=15).grid(row=0, column=3, sticky="w", padx=5, pady=5)

    # Ajuste do peso das colunas para não ficarem “grudadas” na direita
    frm.grid_columnconfigure(0, weight=0)
    frm.grid_columnconfigure(1, weight=1)
    frm.grid_columnconfigure(2, weight=0)
    frm.grid_columnconfigure(3, weight=1)

    # Botão filtrar
    def filtrar():
        refresh_lancamentos(data_inicio_var.get(), data_fim_var.get())

    tk.Button(frm, text="Filtrar", command=filtrar, width=12).grid(row=0, column=4, padx=5)

    # Treeview
    cols = ("id", "data", "tipo", "descricao", "valor", "os_id", "origem", "observacoes")
    tree = ttk.Treeview(frm, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c.capitalize())
    tree.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=10)

    frm.grid_rowconfigure(1, weight=1)
    frm.grid_columnconfigure(4, weight=1)

    # ----- Função para popular a Treeview -----
    def refresh_lancamentos(data_inicio=None, data_fim=None):
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT id, data, tipo, descricao, valor, os_id, origem, observacoes FROM lancamentos WHERE 1=1"
        params = []

        # Filtro por datas
        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)

        query += " ORDER BY data DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", "end", values=r)

    # Popula inicialmente
    refresh_lancamentos()

    # Cabeçalhos
    tree.heading("id", text="ID")
    tree.heading("data", text="Data")
    tree.heading("tipo", text="Tipo")
    tree.heading("descricao", text="Descrição")
    tree.heading("valor", text="Valor")
    tree.heading("os_id", text="OS #")
    tree.heading("origem", text="Origem")
    tree.heading("observacoes", text="Observações")

    # Ajuste de largura das colunas
    tree.column("id", width=40)
    tree.column("data", width=80)
    tree.column("tipo", width=80)
    tree.column("descricao", width=200)
    tree.column("valor", width=80)
    tree.column("os_id", width=50)
    tree.column("origem", width=80)
    tree.column("observacoes", width=150)

    # ----- Função para carregar os dados -----
    def refresh_tree():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, data, tipo, descricao, valor, os_id, origem, observacoes FROM lancamentos ORDER BY data DESC")
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", "end", values=r)

    refresh_tree()

    # ----- Botões de ação -----
    btn_frame = tk.Frame(frm)
    btn_frame.grid()

    def adicionar_lancamento():
        from financeiro.financeiro_form import abrir_form_lancamento
        abrir_form_lancamento(refresh_tree)

    def editar_lancamento():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um lançamento para editar")
            return
        lanc_id = tree.item(selected[0])["values"][0]
        from financeiro.financeiro_form import abrir_form_lancamento
        abrir_form_lancamento(refresh_tree, lanc_id)

    def deletar_lancamento():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um lançamento para deletar")
            return
        lanc_id = tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"Deletar lançamento #{lanc_id}?"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM lancamentos WHERE id=?", (lanc_id,))
            conn.commit()
            conn.close()
            refresh_tree()

    tk.Button(btn_frame, text="Adicionar", width=15, command=adicionar_lancamento).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Editar", width=15, command=editar_lancamento).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Deletar", width=15, command=deletar_lancamento).pack(side="left", padx=5)

criar_tabelas()
