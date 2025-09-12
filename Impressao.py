from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from ordens import buscar_os_por_id
import os
from clientes import buscar_cliente_por_id

def criar_cabecalho(c, largura_pagina, altura_pagina):
    logo_path = "assets/logo.png"
    logo_largura = 360
    logo_altura = 360
    x_logo = (largura_pagina - logo_largura) / 2
    y_logo = altura_pagina - logo_altura + 120
    c.drawImage(logo_path, x_logo, y_logo, width=logo_largura, height=logo_altura, preserveAspectRatio=True, mask='auto')

    # Endereço
    endereco = "Av. Guiomar Britto, 30 - Olho D'Água Do Casado - AL"
    c.setFont("Helvetica", 10)
    y_texto = y_logo + 130
    c.drawCentredString(largura_pagina / 2, y_texto, endereco)

    # Telefone / contato
    telefone = "(82) 98228-9554"
    y_texto -= 17
    c.drawCentredString(largura_pagina / 2, y_texto, telefone)

    return y_texto - 10

def imprimir_os(os_id, salvar_em="OSs"):
    os_dados = buscar_os_por_id(os_id)
    if not os_dados:
        print(f"OS #{os_id} não encontrada")
        return

    # Cria pasta para salvar OSs se não existir
    if not os.path.exists(salvar_em):
        os.makedirs(salvar_em)

    cliente_id = os_dados['cliente_id']
    cliente_dados = buscar_cliente_por_id(cliente_id)

    arquivo_pdf = os.path.join(salvar_em, f"OS_{os_id}_{cliente_dados.get('nome', '')}.pdf")
    c = canvas.Canvas(arquivo_pdf, pagesize=A4)

    largura, altura = A4

    y = criar_cabecalho(c, largura, altura)

    y_pos = criar_cabecalho(c, largura, altura)

    c.setFont("Helvetica-Bold", 14)
    y += 20
    c.drawString(50, y - 40, f"Ordem de Serviço Nº {os_id}")



    linha_margem_esq = 40
    linha_margem_dir = largura - 40
    c.setLineWidth(1)
    c.line(linha_margem_esq, y_pos, linha_margem_dir, y_pos)

    y = y_pos - 50

    # --- Cliente ---


    if cliente_dados:
        # título
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Cliente")
        y -= 15  # distância do título para os dados

        # informações do cliente
        c.setFont("Helvetica", 10)
        nome = cliente_dados.get('nome', '')
        telefone = cliente_dados.get('telefone', '')
        email = cliente_dados.get('email', '')
        endereco = cliente_dados.get('endereco', '')

        c.drawString(60, y, f"-> Nome: {nome}   |   Contato: {telefone}")
        y -= 15

        if email:
            c.drawString(60, y, f"-> E-mail: {email}")
            y -= 15

        if endereco:
            c.drawString(60, y, f"-> Endereço: {endereco}")
            y -= 20

    y -= 25

    # Equipamento
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Equipamento")
    c.setFont("Helvetica", 10)
    y -= 15
    c.drawString(60, y, f"-> Tipo: {os_dados['tipo_equipamento']}")
    y -= 15
    c.drawString(60, y, f"-> Marca/Modelo: {os_dados['marca_modelo']}")
    y -= 15
    c.drawString(60, y, f"-> Nº de série: {os_dados['numero_serie']}")
    y -= 15
    c.drawString(60, y, f"-> Sistema: {os_dados['sistema_operacional']}")
    y -= 15
    c.drawString(60, y, f"-> Senha: {os_dados['senha_equipamento']}")
    y -= 30

    # Serviços
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Serviço solicitado / Problema:")
    c.setFont("Helvetica", 10)
    y -= 15

    for linha in os_dados['servico_solicitado'].splitlines():
        linha = linha.strip()
        if linha:  # só adiciona se não for linha vazia
            c.drawString(60, y, f"• {linha}")
            y -= 15

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Serviço executado / Observações:")
    c.setFont("Helvetica", 10)
    y -= 15

    for linha in os_dados['servico_executado'].splitlines():
        linha = linha.strip()
        if linha:  # só adiciona se não for linha vazia
            c.drawString(60, y, f"• {linha}")
            y -= 15

    # Itens substituídos
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Itens substituídos / consumíveis:")
    c.setFont("Helvetica", 10)
    y -= 15

    for linha in os_dados['itens_substituidos'].splitlines():
        linha = linha.strip()
        if linha:  # só adiciona se não for linha vazia
            c.drawString(60, y, f"• {linha}")
            y -= 15

    y -= 5
    c.setLineWidth(1)  # espessura da linha
    c.line(50, y, largura - 50, y)
    y -= 15

    # Valores
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Valor serviço: R$ {os_dados['valor_servico']:.2f}")
    y -= 15
    c.drawString(50, y, f"Valor peças: R$ {os_dados['valor_pecas']:.2f}")
    y -= 15
    total = os_dados['valor_servico'] + os_dados['valor_pecas']
    c.drawString(50, y, f"Total: R$ {total:.2f}")
    y -= 15
    dias = "Dias"
    c.drawString(50, y, f"Garantia: {os_dados['garantia']} {dias}")
    y -= 15
    c.drawString(50, y, f"Status: {os_dados.get('status','')}")

    # Salvar PDF
    c.save()
    print(f"OS #{os_id} salva em {arquivo_pdf}")

    # Opcional: abrir PDF automaticamente (Windows)
    try:
        os.startfile(arquivo_pdf)
    except:
        pass