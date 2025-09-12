import tkinter as tk
from tkinter import ttk, messagebox
from clientes import adicionar_cliente, listar_clientes, atualizar_cliente, excluir_cliente
from db import criar_tabelas

class ClienteUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Clientes")
        self.root.geometry("750x400")

        frame_form = tk.Frame(self.root)
        frame_form.pack(pady=10)

        # Campos do formulário
        tk.Label(frame_form, text="Nome:").grid(row=0, column=0)
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_nome.grid(row=0, column=1)

        tk.Label(frame_form, text="Telefone:").grid(row=1, column=0)
        self.entry_tel = tk.Entry(frame_form, width=30)
        self.entry_tel.grid(row=1, column=1)

        tk.Label(frame_form, text="Email:").grid(row=2, column=0)
        self.entry_email = tk.Entry(frame_form, width=30)
        self.entry_email.grid(row=2, column=1)

        tk.Label(frame_form, text="Endereço:").grid(row=3, column=0)
        self.entry_end = tk.Entry(frame_form, width=30)
        self.entry_end.grid(row=3, column=1)

        # Botões
        btn_salvar = tk.Button(frame_form, text="Adicionar Cliente", command=self.salvar_cliente)
        btn_salvar.grid(row=4, column=0, pady=10)

        btn_editar = tk.Button(frame_form, text="Editar Cliente", command=self.editar_cliente)
        btn_editar.grid(row=4, column=1, pady=10)

        btn_excluir = tk.Button(frame_form, text="Excluir Cliente", command=self.excluir_cliente)
        btn_excluir.grid(row=4, column=2, pady=10)

        # Tabela de clientes
        cols = ("ID", "Nome", "Telefone", "Email", "Endereço")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col=="ID" else 150)
        self.tree.pack(fill="both", expand=True)

        # Evento de seleção
        self.tree.bind("<<TreeviewSelect>>", self.preencher_campos)

        criar_tabelas()
        self.atualizar_lista()

    def salvar_cliente(self):
        nome = self.entry_nome.get()
        telefone = self.entry_tel.get()
        email = self.entry_email.get()
        endereco = self.entry_end.get()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório")
            return

        adicionar_cliente(nome, telefone, email, endereco)
        self.atualizar_lista()
        self.limpar_campos()

    def editar_cliente(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar")
            return

        cliente_id = self.tree.item(selecionado[0])["values"][0]
        nome = self.entry_nome.get()
        telefone = self.entry_tel.get()
        email = self.entry_email.get()
        endereco = self.entry_end.get()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório")
            return

        atualizar_cliente(cliente_id, nome, telefone, email, endereco)
        self.atualizar_lista()
        self.limpar_campos()

    def excluir_cliente(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir")
            return

        cliente_id = self.tree.item(selecionado[0])["values"][0]

        confirm = messagebox.askyesno("Confirmar", "Deseja realmente excluir este cliente?")
        if confirm:
            excluir_cliente(cliente_id)
            self.atualizar_lista()
            self.limpar_campos()

    def atualizar_lista(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in listar_clientes():
            self.tree.insert("", "end", values=c)

    def preencher_campos(self, event):
        selecionado = self.tree.selection()
        if not selecionado:
            return
        cliente = self.tree.item(selecionado[0])["values"]
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, cliente[1])
        self.entry_tel.delete(0, tk.END)
        self.entry_tel.insert(0, cliente[2])
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, cliente[3])
        self.entry_end.delete(0, tk.END)
        self.entry_end.insert(0, cliente[4])

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_tel.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_end.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteUI(root)
    root.mainloop()