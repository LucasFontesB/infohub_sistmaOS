import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import get_connection

# Tela de relatórios financeiros
def abrir_relatorio_financeiro():
    win = tk.Toplevel()
    win.title("Relatório Financeiro")
    win.geometry("1450x550")

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

    # Labels para total de receitas e despesas
    frm_totais = tk.Frame(win, padx=10, pady=10)
    frm_totais.pack(fill="x")

    lbl_total_receitas = tk.Label(frm_totais, text="Total Receitas: R$ 0,00", font=("Arial", 12, "bold"))
    lbl_total_receitas.pack(side="left", padx=20)
    lbl_total_despesas = tk.Label(frm_totais, text="Total Despesas: R$ 0,00", font=("Arial", 12, "bold"))
    lbl_total_despesas.pack(side="left", padx=20)
    lbl_saldo = tk.Label(frm_totais, text="Saldo: R$ 0,00", font=("Arial", 12, "bold"))
    lbl_saldo.pack(side="left", padx=20)

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
        total_receitas = 0.0
        total_despesas = 0.0

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
                total_receitas += valor_num
            else:
                saldo -= valor_num
                total_despesas += valor_num

            valor_fmt = f"R$ {valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            saldo_fmt = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            tree.insert("", "end", values=(id_, data_fmt, tipo, descricao, valor_fmt, origem, saldo_fmt))

        # Atualizar labels de totais
        lbl_total_receitas.config(
            text=f"Total Receitas: R$ {total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        lbl_total_despesas.config(
            text=f"Total Despesas: R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        lbl_saldo.config(
            text=f"Saldo: R$ {total_receitas - total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    btn_filtrar.config(command=refresh_relatorio)
    refresh_relatorio()  # carregar inicialmente