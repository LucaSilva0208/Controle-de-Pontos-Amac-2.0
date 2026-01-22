from docx import Document
import calendar
import os
from docx2pdf import convert

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

class GeradorFolhaPonto:
    def __init__(self, modelo_path="modelos/folha_base.docx"):
        self.modelo_path = modelo_path

    def gerar(self, funcionario, mes, ano):
        mes_extenso = MESES[int(mes)]
        nome_limpo = funcionario["nome"].replace(" ", "_")

        docx_saida = f"saida/{nome_limpo}_{mes}_{ano}.docx"
        pdf_saida = f"saida/pdf/{nome_limpo}_{mes}_{ano}.pdf"

        os.makedirs("saida/pdf", exist_ok=True)

        doc = Document(self.modelo_path)

        self.substituir_texto(doc, {
            "{{NOME}}": funcionario["nome"],
            "{{MATRICULA}}": funcionario["matricula"],
            "{{CARGO}}": funcionario["cargo"],
            "{{MES}}": mes_extenso,
            "{{ANO}}": str(ano)
        })

        self.preencher_tabela(doc, int(mes), int(ano))
        doc.save(docx_saida)

        # Converte o Word preenchido em PDF
        convert(docx_saida, pdf_saida)

        return pdf_saida

    def substituir_texto(self, doc, mapa):
        for p in doc.paragraphs:
            for k, v in mapa.items():
                if k in p.text:
                    p.text = p.text.replace(k, v)

    def preencher_tabela(self, doc, mes, ano):
        dias = calendar.monthrange(ano, mes)[1]
        tabela = doc.tables[0]

        for dia in range(1, dias + 1):
            row = tabela.add_row()
            row.cells[0].text = str(dia)
