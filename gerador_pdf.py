from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import webbrowser
import tempfile


class GeradorFolhaPDF:
    def __init__(self):
        """
        Inicializa o gerador de folha de ponto.
        Não requer nome de arquivo, pois o PDF será gerado na memória.
        """
        pass

    def gerar_folha_memoria(self, nome, cargo, matricula, mes, status):
        """
        Gera a folha de ponto em memória e retorna um buffer BytesIO.
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        largura, altura = A4

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, altura - 50, "PONTO CERTO — FOLHA DE PONTO")

        c.setFont("Helvetica", 11)
        c.drawString(50, altura - 90, f"Funcionário: {nome}")
        c.drawString(50, altura - 115, f"Cargo: {cargo}")
        c.drawString(50, altura - 140, f"Matrícula: {matricula}")
        c.drawString(50, altura - 165, f"Mês: {mes}")
        c.drawString(50, altura - 190, f"Status: {status}")

        # Linha separadora
        c.line(50, altura - 210, largura - 50, altura - 210)

        # Tabela simulada
        y = altura - 250
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, "Data")
        c.drawString(160, y, "Entrada")
        c.drawString(260, y, "Saída")
        c.drawString(360, y, "Assinatura")

        c.setFont("Helvetica", 10)
        y -= 25
        for i in range(1, 23):  # 22 dias simulados
            c.drawString(60, y, f"{i:02d}/{datetime.now().month:02d}")
            c.drawString(160, y, "08:00")
            c.drawString(260, y, "17:00")
            c.line(360, y - 2, 520, y - 2)  # linha para assinatura
            y -= 20
            if y < 80:  # quebra de página
                c.showPage()
                y = altura - 80

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def abrir_pdf_memoria(self, buffer):
        """
        Abre o PDF gerado em memória no visualizador padrão do sistema.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(buffer.read())
            tmp.flush()
            webbrowser.open_new(tmp.name)
