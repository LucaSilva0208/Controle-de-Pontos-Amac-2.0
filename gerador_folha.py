import os
import calendar
from datetime import datetime, date
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx2pdf import convert
import holidays

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]

class GeradorFolhaPonto:
    def __init__(self, modelo_path=None):
        pasta_script = os.path.dirname(os.path.abspath(__file__))
        self.pasta_modelos = os.path.join(pasta_script, "modelos")
        self.logo_path = os.path.join(self.pasta_modelos, "logo.png")
        self.cabecalho_img_path = os.path.join(self.pasta_modelos, "cabecalho.png")

        if os.path.exists(self.logo_path):
            print(f"[OK] Logo detectada: {self.logo_path}")

    def obter_nome_feriado_ptbr(self, data_obj, feriados_lib):
        """
        Retorna o nome do feriado em Português garantido.
        Prioriza verificação por DATA para evitar nomes em inglês.
        """
        # 1. Feriados Nacionais Fixos (Prioridade Máxima)
        fixos = {
            (1, 1): "Confraternização Universal",
            (21, 4): "Tiradentes",
            (1, 5): "Dia do Trabalho",
            (7, 9): "Independência do Brasil",
            (12, 10): "Nossa Sra. Aparecida",
            (2, 11): "Finados",
            (15, 11): "Proclamação da República",
            (20, 11): "Dia da Consciência Negra",
            (25, 12): "Natal"
        }
        
        if (data_obj.day, data_obj.month) in fixos:
            return fixos[(data_obj.day, data_obj.month)]

        # 2. Verifica na biblioteca (para Móveis e Locais)
        nome_original = feriados_lib.get(data_obj)
        
        if not nome_original:
            return None # Não é feriado

        # 3. Tradução manual de feriados móveis comuns
        traducoes_moveis = {
            "Mardi Gras": "Carnaval",
            "Carnival": "Carnaval",
            "Good Friday": "Sexta-feira Santa",
            "Corpus Christi": "Corpus Christi",
            "Easter Sunday": "Páscoa"
        }
        
        # Verifica se alguma chave em inglês está contida no nome original
        for eng, pt in traducoes_moveis.items():
            if eng in nome_original:
                return pt
        
        # Se não achou tradução mas tem nome (ex: feriado municipal adicionado manualmente), retorna ele
        return nome_original

    def gerar(self, funcionario, mes, ano, caminho_saida_pdf):
        # --- PREPARAÇÃO ---
        feriados_br = holidays.BR(subdiv='MG', years=ano)
        
        # Feriados Municipais Manuais
        feriados_extras = {
            f"{ano}-06-13": "Santo Antônio",
            f"{ano}-06-19": "Corpus Christi" # Reforço
        }
        for data_str, nome in feriados_extras.items():
            try:
                d = datetime.strptime(data_str, "%Y-%m-%d").date()
                feriados_br.append({d: nome})
            except ValueError: pass

        doc = Document()
        
        # --- LAYOUT SUPER COMPACTO (A4 ÚNICO) ---
        # Margens mínimas seguras para impressão
        for section in doc.sections:
            section.top_margin = Cm(0.6)
            section.bottom_margin = Cm(0.6)
            section.left_margin = Cm(1.0)
            section.right_margin = Cm(1.0)

        mes_extenso = MESES[int(mes)]

        # --- 1. CABEÇALHO ---
        if os.path.exists(self.cabecalho_img_path):
            try:
                # 19cm é largura segura com margens de 1cm
                doc.add_picture(self.cabecalho_img_path, width=Cm(19))
            except:
                self._criar_cabecalho_manual(doc)
        else:
            self._criar_cabecalho_manual(doc)

        # Espaçador mínimo
        self.add_spacer(doc, pt_size=4)

        # --- 2. DADOS DO FUNCIONÁRIO (Compacto) ---
        table_info = doc.add_table(rows=3, cols=2)
        table_info.style = 'Table Grid'
        
        # Fonte tamanho 9 para economizar espaço
        self.celula_texto(table_info.cell(0, 0), f"Nome: {funcionario['nome']}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        self.celula_texto(table_info.cell(0, 1), f"Matrícula: {funcionario['matricula']}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        
        cell_lotacao = table_info.cell(1, 0)
        cell_lotacao.merge(table_info.cell(1, 1))
        self.celula_texto(cell_lotacao, f"Lotação: {funcionario.get('lotacao', '')}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        
        self.celula_texto(table_info.cell(2, 0), f"Cargo: {funcionario.get('cargo', '')}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        self.celula_texto(table_info.cell(2, 1), f"Função/Ref: {mes_extenso}/{ano}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)

        self.add_spacer(doc, pt_size=4)

        # --- 3. TABELA DE PONTO ---
        table = doc.add_table(rows=0, cols=11)
        table.style = 'Table Grid'
        
        # Cabeçalhos
        row_header1 = table.add_row()
        self.celula_texto(row_header1.cells[0], "Dados", size=8)
        row_header1.cells[0].merge(row_header1.cells[1])
        self.celula_texto(row_header1.cells[2], "Primeira Jornada", size=8)
        row_header1.cells[2].merge(row_header1.cells[5])
        self.celula_texto(row_header1.cells[6], "Segunda Jornada", size=8)
        row_header1.cells[6].merge(row_header1.cells[9])
        self.celula_texto(row_header1.cells[10], "H. Extra", size=8)

        row_header2 = table.add_row()
        headers = ["Dia", "Sem", "Entr", "Rub", "Saída", "Rub", "Entr", "Rub", "Saída", "Rub", "Assinatura"]
        for i, h in enumerate(headers):
            # Fonte 7 no cabeçalho
            self.celula_texto(row_header2.cells[i], h, bold=True, size=7)

        # --- 4. DIAS (FONTE 7 PARA CABER TUDO) ---
        _, num_dias = calendar.monthrange(ano, mes)
        
        for dia in range(1, num_dias + 1):
            data_atual = date(ano, mes, dia)
            idx_semana = data_atual.weekday()
            nome_semana = DIAS_SEMANA[idx_semana]
            
            # Busca nome em PT-BR usando nossa função robusta
            feriado_nome = self.obter_nome_feriado_ptbr(data_atual, feriados_br)

            row = table.add_row()
            # Altura da linha automática, mas fonte pequena ajuda
            
            self.celula_texto(row.cells[0], f"{dia:02d}", size=7)
            self.celula_texto(row.cells[1], nome_semana, size=7)

            bloquear = False
            texto_bloqueio = ""

            if feriado_nome:
                bloquear = True
                texto_bloqueio = f"FERIADO - {feriado_nome.upper()}"
            elif idx_semana == 5:
                bloquear = True
                texto_bloqueio = "SÁBADO"
            elif idx_semana == 6:
                bloquear = True
                texto_bloqueio = "DOMINGO"

            if bloquear:
                cell_inicio = row.cells[2]
                cell_fim = row.cells[9]
                cell_inicio.merge(cell_fim)
                # Negrito e fonte 7 para o bloqueio
                self.celula_texto(cell_inicio, texto_bloqueio, bold=True, size=7)

        self.add_spacer(doc, pt_size=6)

        # --- 5. RODAPÉ COMPACTO ---
        p = doc.add_paragraph("Reconheço a exatidão destas anotações:")
        p.style.font.size = Pt(8)
        p.paragraph_format.space_after = Pt(10) # Espaço para assinatura

        table_ass = doc.add_table(rows=1, cols=3)
        # Fonte 8 no rodapé
        self.celula_texto(table_ass.cell(0, 0), "_______________________\nAssinatura Empregado", size=8)
        self.celula_texto(table_ass.cell(0, 1), "Data: ____/____/____", size=8)
        self.celula_texto(table_ass.cell(0, 2), "_______________________\nAssinatura Chefia", size=8)

        # --- SALVAR ---
        docx_temp = caminho_saida_pdf.replace(".pdf", ".docx")
        os.makedirs(os.path.dirname(caminho_saida_pdf), exist_ok=True)
        
        doc.save(docx_temp)
        try:
            convert(docx_temp, caminho_saida_pdf)
        except Exception as e:
            print(f"Erro PDF: {e}")
            raise e
        finally:
            if os.path.exists(docx_temp):
                os.remove(docx_temp)

    def add_spacer(self, doc, pt_size=5):
        """Adiciona um parágrafo vazio com tamanho controlado"""
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        run = p.add_run()
        run.font.size = Pt(pt_size)

    def _criar_cabecalho_manual(self, doc):
        header_table = doc.add_table(rows=1, cols=2)
        header_table.autofit = False
        header_table.columns[0].width = Cm(3.8)
        header_table.columns[1].width = Cm(15.2) # Ajustado para nova margem
        
        cell_logo = header_table.cell(0, 0)
        cell_texto = header_table.cell(0, 1)

        if os.path.exists(self.logo_path):
            try:
                p = cell_logo.paragraphs[0]
                run = p.add_run()
                run.add_picture(self.logo_path, width=Cm(3.5))
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            except:
                cell_logo.text = "LOGO"
        else:
            cell_logo.text = "LOGO"

        p_empresa = cell_texto.paragraphs[0]
        p_empresa.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_empresa.paragraph_format.space_after = Pt(0)
        
        run_title = p_empresa.add_run("Associação Municipal de Apoio Comunitário\n")
        run_title.bold = True
        run_title.font.size = Pt(12) # Fonte menor no cabeçalho
        
        p_empresa.add_run("Rua Espírito Santo, 434 – Centro / Juiz de Fora – MG\n")
        run_folha = p_empresa.add_run("FOLHA DE PONTO")
        run_folha.bold = True
        run_folha.font.size = Pt(11)

    def celula_texto(self, cell, text, bold=False, size=10, align=WD_ALIGN_PARAGRAPH.CENTER):
        cell.text = text
        if cell.paragraphs:
            p = cell.paragraphs[0]
            p.alignment = align
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0) # Garante linha compacta
            if p.runs:
                run = p.runs[0]
                run.font.bold = bold
                run.font.size = Pt(size)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER