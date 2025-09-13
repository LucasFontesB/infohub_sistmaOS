import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import get_connection

# Tela de relatórios financeiros
def abrir_relatorio_financeiro():
    win = tk.Toplevel()
    win.title("Relatório Financeiro")
    win.geometry("1450x500")

    frm_filtros = tk.Frame(win, padx=10, pady=10)
    frm_filtros.pack(fill="x")

    tk.Label(frm_filtros, text="Data Início (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
    data_inicio_var = tk.StringVar()
    tk.Entry(frm_filtros, textvariable=data_inicio_var, width=15).grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frm_filtros, text="Data Fim (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5)
    data_fim_var = tk.StringVar()
    tk.Entry(frm_filtros, textvariable=data_fim_var, width=15).grid(row=0, column=3, padx=5, pady=5)

    btn_filtrar = tk.Button(frm_filtros, text="Filtrar")
    btn_filtrar.grid(row=0, column=4, padx=10, pady=5)

    # Treeview do relatório
    cols = ("ID", "Data", "Tipo", "Descrição", "Valor", "Origem", "Saldo")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Função para atualizar o relatório
    def refresh_relatorio():
        for row in tree.get_children():
            tree.delete(row)

        data_inicio = data_inicio_var.get().strip()
        data_fim = data_fim_var.get().strip()

        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT id, data, tipo, descricao, valor, origem FROM lancamentos WHERE 1=1"
        params = []
        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)
        query += " ORDER BY data ASC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        saldo = 0.0
        for r in rows:
            id_, data, tipo, descricao, valor, origem = r

            # Formatar data
            try:
                data_fmt = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                data_fmt = data

            # Formatar valor
            valor_num = float(valor)
            if tipo.lower() == "receita":
                saldo += valor_num
            else:
                saldo -= valor_num
            valor_fmt = f"R$ {valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            saldo_fmt = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            tree.insert("", "end", values=(id_, data_fmt, tipo, descricao, valor_fmt, origem, saldo_fmt))

    btn_filtrar.config(command=refresh_relatorio)
    refresh_relatorio()  # carregar inicialmente