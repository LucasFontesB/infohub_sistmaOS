import tkinter as tk
from tkinter import ttk, messagebox
from financeiro.db_financeiro import get_connection
from datetime import datetime
from ordens import listar_os

def abrir_form_lancamento(refresh_callback, lanc_id=None, tipo=None, descricao=None, valor=None, origem=None):
    win = tk.Toplevel()
    win.title("Lançamento Financeiro")
    win.geometry("450x400")

    frm = tk.Frame(win, padx=10, pady=10)
    frm.pack(fill="both", expand=True)

    # ----- Campos -----
    tk.Label(frm, text="Data (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
    data_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    tk.Entry(frm, textvariable=data_var, width=20).grid(row=0, column=1, sticky="w")

    tk.Label(frm, text="Tipo:").grid(row=1, column=0, sticky="w")
    tipo_var = tk.StringVar(value="Despesa")
    tipo_cb = ttk.Combobox(frm, values=["Receita", "Despesa"], textvariable=tipo_var, width=18)
    tipo_cb.grid(row=1, column=1, sticky="w")

    tk.Label(frm, text="Descrição:").grid(row=2, column=0, sticky="w")
    descricao_txt = tk.Text(frm, width=30, height=3)
    descricao_txt.grid(row=2, column=1, pady=3, sticky="w")

    tk.Label(frm, text="Valor:").grid(row=3, column=0, sticky="w")
    valor_var = tk.StringVar(value="0.00")
    tk.Entry(frm, textvariable=valor_var, width=20).grid(row=3, column=1, sticky="w")

    tk.Label(frm, text="Origem / OS:").grid(row=4, column=0, sticky="w")
    # Opção de selecionar uma OS ou "Outro"
    os_list = listar_os()
    os_opts = [f"OS #{r[0]}" for r in os_list] + ["Outro"]
    origem_var = tk.StringVar(value="Outro")
    origem_cb = ttk.Combobox(frm, values=os_opts, textvariable=origem_var, width=25)
    origem_cb.grid(row=4, column=1, sticky="w")

    tk.Label(frm, text="Observações:").grid(row=5, column=0, sticky="nw")
    observ_txt = tk.Text(frm, width=30, height=4)
    observ_txt.grid(row=5, column=1, pady=3, sticky="w")

    tipo_var.set(tipo or "Despesa")
    descricao_txt.insert("1.0", descricao or "")
    valor_var.set(str(valor) if valor is not None else "0.00")
    origem_var.set(origem or "Outro")

    # ----- Função para salvar -----
    def salvar():
        data = data_var.get().strip()
        tipo = tipo_var.get().strip()
        descricao = descricao_txt.get("1.0", "end").strip()
        observacoes = observ_txt.get("1.0", "end").strip()
        try:
            valor = float(valor_var.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido")
            return

        # verifica origem
        origem = origem_var.get()
        os_id = None
        if origem.startswith("OS #"):
            os_id = int(origem.replace("OS #", ""))
        elif origem == "Outro":
            os_id = None

        if not descricao:
            messagebox.showerror("Erro", "Descrição é obrigatória")
            return

        conn = get_connection()
        cur = conn.cursor()
        if lanc_id:  # Editar lançamento existente
            cur.execute("""
                UPDATE lancamentos
                SET data=?, tipo=?, descricao=?, valor=?, os_id=?, origem=?, observacoes=?
                WHERE id=?
            """, (data, tipo, descricao, valor, os_id, origem, observacoes, lanc_id))
        else:  # Novo lançamento
            cur.execute("""
                INSERT INTO lancamentos (data, tipo, descricao, valor, os_id, origem, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (data, tipo, descricao, valor, os_id, origem, observacoes))
        conn.commit()
        conn.close()

        messagebox.showinfo("OK", "Lançamento salvo com sucesso!")
        refresh_callback()
        win.destroy()

    # ----- Botões -----
    tk.Button(frm, text="Salvar", width=15, command=salvar).grid(row=6, column=0, pady=15)
    tk.Button(frm, text="Cancelar", width=15, command=win.destroy).grid(row=6, column=1, pady=15)

    # ----- Se for edição, carregar dados existentes -----
    if lanc_id:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT data, tipo, descricao, valor, os_id, origem, observacoes FROM lancamentos WHERE id=?", (lanc_id,))
        r = cur.fetchone()
        conn.close()
        if r:
            data_var.set(r[0])
            tipo_var.set(r[1])
            descricao_txt.insert("1.0", r[2])
            valor_var.set(str(r[3]))
            origem_var.set(r[5] or "Outro")
            observ_txt.insert("1.0", r[6] or "")