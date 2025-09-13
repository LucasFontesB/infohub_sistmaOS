import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from db import get_connection
from estoque.db_estoque import criar_tabelas
from financeiro.financeiro_form import abrir_form_lancamento

def abrir_estoque(root):
    win = tk.Toplevel(root)
    win.title("Gestão de Estoque")
    win.geometry("1200x550")

    tk.Label(win, text="Estoque de Produtos", font=("Arial", 16)).pack(pady=10)

    cols = ("ID", "Nome", "Categoria", "Quantidade", "Preço Compra", "Preço Venda", "Data Cadastro")
    tree = ttk.Treeview(win, columns=cols, show="headings")

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=130 if c != "Nome" else 200, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.place(in_=tree, relx=1.0, relheight=1.0, bordermode="outside")

    def realizar_venda():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para vender.")
            return

        item = tree.item(selected[0])
        # Supondo que a ordem das colunas seja: ID, Nome, Categoria, Quantidade, Preço Compra, Preço Venda, Data
        id_, nome, categoria, qtd, preco_compra_fmt, preco_venda_fmt, data_fmt = item['values']

        try:
            qtd = int(qtd)
            preco_venda = float(preco_venda_fmt.replace("R$ ", "").replace(".", "").replace(",", "."))
        except:
            messagebox.showerror("Erro", "Erro ao ler quantidade ou preço de venda do produto.")
            return

        venda = tk.simpledialog.askinteger(
            "Quantidade a vender",
            f"Quantidade disponível: {qtd}\nQuantas unidades deseja vender de '{nome}'?",
            minvalue=1, maxvalue=qtd
        )

        if venda is None:
            return

        # Atualizar estoque
        nova_qtd = qtd - venda
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?", (nova_qtd, id_))
        conn.commit()
        conn.close()

        # Abrir lançamento financeiro como receita
        descricao = f"Venda de {venda} unidade(s) de {nome}"
        valor_total = venda * preco_venda
        abrir_form_lancamento(
            refresh_callback=lambda: None,
            tipo="Receita",
            descricao=descricao,
            valor=valor_total,
            origem="Estoque"
        )

        carregar_estoque()

    def carregar_estoque():
        for item in tree.get_children():
            tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, categoria, quantidade, preco_compra, preco_venda, data_cadastro 
            FROM produtos
        """)
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            id_, nome, categoria, qtd, preco_compra, preco_venda, data = r

            # Formatar preços
            preco_compra_fmt = f"R$ {preco_compra:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            preco_venda_fmt = f"R$ {preco_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # Formatar data
            data_fmt = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y") if data else ""

            # Inserir na Treeview
            tree.insert("", "end", values=(id_, nome, categoria, qtd, preco_compra_fmt, preco_venda_fmt, data_fmt))

    # ----- adicionar produto -----
    def adicionar_produto():
        top = tk.Toplevel(win)
        top.title("Adicionar Produto")

        # Nome
        tk.Label(top, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        nome_entry = tk.Entry(top)
        nome_entry.grid(row=0, column=1, padx=5, pady=5)

        # Categoria
        tk.Label(top, text="Categoria:").grid(row=1, column=0, padx=5, pady=5)
        cat_entry = tk.Entry(top)
        cat_entry.grid(row=1, column=1, padx=5, pady=5)

        # Quantidade
        tk.Label(top, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5)
        qtd_entry = tk.Entry(top)
        qtd_entry.grid(row=2, column=1, padx=5, pady=5)

        # Preço de compra
        tk.Label(top, text="Preço de Compra (unitário):").grid(row=3, column=0, padx=5, pady=5)
        preco_compra_entry = tk.Entry(top)
        preco_compra_entry.grid(row=3, column=1, padx=5, pady=5)

        # Total de compra (calculado automaticamente)
        tk.Label(top, text="Preço Total de Compra:").grid(row=4, column=0, padx=5, pady=5)
        preco_total_entry = tk.Entry(top)
        preco_total_entry.grid(row=4, column=1, padx=5, pady=5)

        # Preço de venda
        tk.Label(top, text="Preço de Venda (unitário):").grid(row=5, column=0, padx=5, pady=5)
        preco_venda_entry = tk.Entry(top)
        preco_venda_entry.grid(row=5, column=1, padx=5, pady=5)

        # --- eventos para calcular automaticamente ---
        def calcular_total(event=None):
            try:
                qtd = int(qtd_entry.get())
                preco_unit = float(preco_compra_entry.get())
                preco_total_entry.delete(0, tk.END)
                preco_total_entry.insert(0, f"{preco_unit * qtd:.2f}")
            except:
                pass

        def calcular_unitario(event=None):
            try:
                qtd = int(qtd_entry.get())
                preco_total = float(preco_total_entry.get())
                if qtd != 0:
                    preco_compra_entry.delete(0, tk.END)
                    preco_compra_entry.insert(0, f"{preco_total / qtd:.2f}")
            except:
                pass

        preco_compra_entry.bind("<FocusOut>", calcular_total)
        preco_total_entry.bind("<FocusOut>", calcular_unitario)
        qtd_entry.bind("<FocusOut>", calcular_total)

        # --- salvar ---
        def salvar():
            nome = nome_entry.get().strip()
            categoria = cat_entry.get().strip()
            try:
                qtd = int(qtd_entry.get())
                preco_compra = float(preco_compra_entry.get())
                preco_total = float(preco_total_entry.get())
                preco_venda = float(preco_venda_entry.get())
            except ValueError:
                messagebox.showerror("Erro", "Quantidade e preços devem ser numéricos!")
                return

            if not nome:
                messagebox.showerror("Erro", "O nome é obrigatório!")
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produtos (nome, categoria, quantidade, preco_compra, preco_venda, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, categoria, qtd, preco_compra, preco_venda, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()

            abrir_form_lancamento(
                refresh_callback=lambda: None,
                tipo="Despesa",
                descricao=f"Entrada de {qtd} unidade(s) de {nome}",
                valor=preco_total,
                origem="Estoque"
            )

            top.destroy()
            carregar_estoque()

        tk.Button(top, text="Salvar", command=salvar).grid(row=6, column=0, columnspan=2, pady=10)

    # ----- editar produto -----
    def editar_produto():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
        item = tree.item(selected[0])
        id_, nome, categoria, qtd, preco_compra_fmt, preco_venda_fmt, data_fmt = item['values']

        top = tk.Toplevel(win)
        top.title("Editar Produto")

        # Nome
        tk.Label(top, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        nome_entry = tk.Entry(top)
        nome_entry.insert(0, nome)
        nome_entry.grid(row=0, column=1, padx=5, pady=5)

        # Categoria
        tk.Label(top, text="Categoria:").grid(row=1, column=0, padx=5, pady=5)
        cat_entry = tk.Entry(top)
        cat_entry.insert(0, categoria)
        cat_entry.grid(row=1, column=1, padx=5, pady=5)

        # Quantidade
        tk.Label(top, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5)
        qtd_entry = tk.Entry(top)
        qtd_entry.insert(0, qtd)
        qtd_entry.grid(row=2, column=1, padx=5, pady=5)

        # Preço de Compra
        tk.Label(top, text="Preço de Compra:").grid(row=3, column=0, padx=5, pady=5)
        preco_compra_entry = tk.Entry(top)
        preco_compra_entry.insert(0, preco_compra_fmt.replace("R$ ", "").replace(".", "").replace(",", "."))
        preco_compra_entry.grid(row=3, column=1, padx=5, pady=5)

        # Preço de Venda
        tk.Label(top, text="Preço de Venda:").grid(row=4, column=0, padx=5, pady=5)
        preco_venda_entry = tk.Entry(top)
        preco_venda_entry.insert(0, preco_venda_fmt.replace("R$ ", "").replace(".", "").replace(",", "."))
        preco_venda_entry.grid(row=4, column=1, padx=5, pady=5)

        # Salvar alterações
        def salvar_edicao():
            novo_nome = nome_entry.get().strip()
            nova_cat = cat_entry.get().strip()
            try:
                nova_qtd = int(qtd_entry.get())
                novo_preco_compra = float(preco_compra_entry.get())
                novo_preco_venda = float(preco_venda_entry.get())
            except ValueError:
                messagebox.showerror("Erro", "Quantidade e preços devem ser numéricos!")
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE produtos
                SET nome=?, categoria=?, quantidade=?, preco_compra=?, preco_venda=?
                WHERE id=?
            """, (novo_nome, nova_cat, nova_qtd, novo_preco_compra, novo_preco_venda, id_))
            conn.commit()
            conn.close()

            top.destroy()
            carregar_estoque()

        tk.Button(top, text="Salvar", command=salvar_edicao).grid(row=5, column=0, columnspan=2, pady=10)

    # ----- ajustar estoque -----
    def ajustar_estoque():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para ajustar o estoque.")
            return

        item = tree.item(selected[0])
        # Ordem das colunas: ID, Nome, Categoria, Quantidade, Preço Compra, Preço Venda, Data
        id_, nome, categoria, qtd, preco_compra_fmt, preco_venda_fmt, data_fmt = item['values']

        ajuste = tk.simpledialog.askinteger(
            "Ajuste de Estoque",
            f"Digite a quantidade a adicionar/remover do produto '{nome}':\n(use negativo para remover)",
            initialvalue=0
        )
        if ajuste is None:
            return

        nova_qtd = int(qtd) + ajuste
        if nova_qtd < 0:
            messagebox.showerror("Erro", "Quantidade não pode ser negativa!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?", (nova_qtd, id_))
        conn.commit()
        conn.close()
        carregar_estoque()

    # ----- botões -----
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Adicionar Produto", command=adicionar_produto).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Realizar Venda", command=realizar_venda).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Editar Produto", command=editar_produto).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Ajustar Estoque", command=ajustar_estoque).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Atualizar Lista", command=carregar_estoque).pack(side="left", padx=5)

    carregar_estoque()

criar_tabelas()
