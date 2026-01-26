import os
import calendar
from datetime import datetime, date
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
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

    def validar_regras_negocio(self, mes_alvo, ano_alvo):
        """Aplica as travas de datas solicitadas"""
        hoje = date.today()
        data_alvo = date(ano_alvo, mes_alvo, 1)
        data_atual_base = date(hoje.year, hoje.month, 1)

        diferenca_meses = (data_atual_base.year - data_alvo.year) * 12 + (data_atual_base.month - data_alvo.month)

        if diferenca_meses > 3:
            raise ValueError(f"Bloqueado: Não é permitido gerar folhas com mais de 3 meses de atraso.\nMês solicitado: {mes_alvo}/{ano_alvo}")

        if data_alvo > data_atual_base:
            if diferenca_meses == -1:
                if hoje.day < 20:
                    raise ValueError(f"Bloqueado: A folha do próximo mês ({mes_alvo}/{ano_alvo}) só pode ser gerada a partir do dia 20.")
            elif diferenca_meses < -1:
                 raise ValueError(f"Bloqueado: Não é permitido gerar folhas tão adiante no tempo.")

    def obter_nome_feriado(self, data_obj, feriados_lib):
        fixos = {
            (1, 1): "Confraternização Universal", (21, 4): "Tiradentes", (1, 5): "Dia do Trabalho",
            (7, 9): "Independência do Brasil", (12, 10): "Nossa Sra. Aparecida", (2, 11): "Finados",
            (15, 11): "Proclamação da República", (20, 11): "Consciência Negra", (25, 12): "Natal"
        }
        if (data_obj.day, data_obj.month) in fixos: return fixos[(data_obj.day, data_obj.month)]

        nome = feriados_lib.get(data_obj)
        if not nome: return None

        traducoes = {
            "Mardi Gras": "Carnaval", "Carnival": "Carnaval", "Good Friday": "Sexta-feira Santa",
            "Corpus Christi": "Corpus Christi", "Easter Sunday": "Páscoa", "Ash Wednesday": "Quarta-feira de Cinzas"
        }
        for eng, pt in traducoes.items():
            if eng in nome: return pt
        return nome

    def aplicar_fundo_cinza(self, cell):
        shading_elm = parse_xml(r'<w:shd {} w:fill="D9D9D9"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def gerar(self, funcionario, mes, ano, caminho_saida_pdf):
        # --- 0. VALIDAÇÃO ---
        try:
            self.validar_regras_negocio(mes, ano)
        except ValueError as e:
            raise e

        # --- PREPARAÇÃO DE FERIADOS ---
        feriados_br = holidays.BR(subdiv='MG', years=ano)
        feriados_municipais = {f"{ano}-06-13": "Santo Antônio", f"{ano}-06-19": "Corpus Christi"}
        for d_str, nome in feriados_municipais.items():
            try:
                d = datetime.strptime(d_str, "%Y-%m-%d").date()
                feriados_br.append({d: nome})
            except: pass

        doc = Document()
        
        # Margens Otimizadas
        for section in doc.sections:
            section.top_margin = Cm(0.5)
            section.bottom_margin = Cm(0.5)
            section.left_margin = Cm(1.0)
            section.right_margin = Cm(1.0)

        mes_extenso = MESES[int(mes)]

        # --- 1. CABEÇALHO ---
        if os.path.exists(self.cabecalho_img_path):
            try:
                doc.add_picture(self.cabecalho_img_path, width=Cm(19))
            except: self._criar_cabecalho_manual(doc)
        else:
            self._criar_cabecalho_manual(doc)

        self.add_spacer(doc, pt_size=2)

        # --- 2. DADOS DO FUNCIONÁRIO ---
        table_info = doc.add_table(rows=3, cols=2)
        table_info.style = 'Table Grid'
        
        self.celula_texto(table_info.cell(0, 0), f"Nome: {funcionario['nome']}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        self.celula_texto(table_info.cell(0, 1), f"Matrícula: {funcionario['matricula']}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        
        cell_lotacao = table_info.cell(1, 0)
        cell_lotacao.merge(table_info.cell(1, 1))
        self.celula_texto(cell_lotacao, f"Lotação: {funcionario.get('lotacao', '')}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        
        self.celula_texto(table_info.cell(2, 0), f"Cargo: {funcionario.get('cargo', '')}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        self.celula_texto(table_info.cell(2, 1), f"Mês de Referência: {mes_extenso}/{ano}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)

        self.add_spacer(doc, pt_size=4)

        # --- 3. TABELA DE PONTO (12 COLUNAS) ---
        table = doc.add_table(rows=0, cols=12)
        table.style = 'Table Grid'
        table.autofit = False
        table.allow_autofit = False

        # --- LARGURAS (Suas alterações mantidas) ---
        larguras = [
            1.55,                                  # 0: Dia/Sem (Unificado)
            1.55, 1.55, 1.55, 1.55,                # 1-4: J1
            1.55, 1.55, 1.55, 1.55,                # 5-8: J2
            1.55, 1.55,                            # 9-10: Extra
            1.55                                   # 11: Assinatura
        ]

        # --- Linha 1: Títulos Macro ---
        row_h1 = table.add_row()
        self.definir_altura_linha(row_h1, 0.8)
        
        self.celula_texto(row_h1.cells[0], "Dados", size=7)
        # Coluna 0 não mescla mais
        
        self.celula_texto(row_h1.cells[1], "Primeira Jornada", size=7)
        row_h1.cells[1].merge(row_h1.cells[4])
        
        self.celula_texto(row_h1.cells[5], "Segunda Jornada", size=7)
        row_h1.cells[5].merge(row_h1.cells[8])
        
        self.celula_texto(row_h1.cells[9], "H. Extra", size=7)
        row_h1.cells[9].merge(row_h1.cells[10])

        self.celula_texto(row_h1.cells[11], "Visto/Obs", size=7)

        # --- Linha 2: Subtítulos ---
        row_h2 = table.add_row()
        self.definir_altura_linha(row_h2, 0.5)
        
        cols_titulos = [
            "Dia/Sem", 
            "Entr", "Rub", "Saída", "Rub", 
            "Entr", "Rub", "Saída", "Rub", 
            "Entr", "Saída", 
            "Assinatura"
        ]
        
        for i, tit in enumerate(cols_titulos):
            self.celula_texto(row_h2.cells[i], tit, bold=True, size=6)
            row_h2.cells[i].width = Cm(larguras[i])

        # --- 4. PREENCHIMENTO DOS DIAS ---
        _, num_dias = calendar.monthrange(ano, mes)
        
        # Pega férias do JSON (Segurança caso não exista a chave)
        lista_ferias = funcionario.get('ferias', [])

        # Função auxiliar para verificar férias
        def verificar_ferias(data_obj, lista_f):
            if not lista_f: return False
            for p in lista_f:
                try:
                    ini = datetime.strptime(p['inicio'], "%Y-%m-%d").date()
                    fim = datetime.strptime(p['fim'], "%Y-%m-%d").date()
                    if ini <= data_obj <= fim: return True
                except: continue
            return False

        for dia in range(1, num_dias + 1):
            data = date(ano, mes, dia)
            idx_sem = data.weekday()
            nome_sem = DIAS_SEMANA[idx_sem]
            feriado = self.obter_nome_feriado(data, feriados_br)
            em_ferias = verificar_ferias(data, lista_ferias)

            row = table.add_row()
            self.definir_altura_linha(row, 0.60) 

            for i, w in enumerate(larguras):
                row.cells[i].width = Cm(w)

            # Texto Unificado
            texto_dia_sem = f"{dia:02d} - {nome_sem}"
            self.celula_texto(row.cells[0], texto_dia_sem, size=8)

            bloquear = False
            texto_bloqueio = ""

            # Ordem de prioridade: Férias > Feriado > Fim de Semana
            if em_ferias:
                bloquear = True
                texto_bloqueio = "FÉRIAS"
            elif feriado:
                bloquear = True
                texto_bloqueio = f"FERIADO - {feriado.upper()}"
            elif idx_sem == 5: bloquear = True; texto_bloqueio = "SÁBADO"
            elif idx_sem == 6: bloquear = True; texto_bloqueio = "DOMINGO"

            if bloquear:
                for cell in row.cells:
                    self.aplicar_fundo_cinza(cell)
                
                # Mescla do índice 1 até 11
                cell_inicio = row.cells[1]
                cell_fim = row.cells[11]
                cell_inicio.merge(cell_fim)
                
                self.celula_texto(cell_inicio, texto_bloqueio, bold=True, size=7)

        self.add_spacer(doc, pt_size=4)

        # --- 5. RODAPÉ ---
        p = doc.add_paragraph("Reconheço a exatidão destas anotações:")
        p.style.font.size = Pt(8)
        p.paragraph_format.space_after = Pt(2)

        table_ass = doc.add_table(rows=1, cols=3)
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

    # --- MÉTODOS AUXILIARES ---
    def definir_altura_linha(self, row, cm_val):
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        row.height = Cm(cm_val)

    def add_spacer(self, doc, pt_size=5):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        run = p.add_run()
        run.font.size = Pt(pt_size)

    def _criar_cabecalho_manual(self, doc):
        """
        Cabeçalho Ajustado: 
        Logo alinhada à direita e Texto à esquerda para aproximação.
        Larguras corrigidas para somar 19cm.
        """
        header_table = doc.add_table(rows=1, cols=2)
        header_table.autofit = False
        
        # AJUSTE: Soma deve ser ~19cm (2.5 + 16.5)
        header_table.columns[0].width = Cm(2.5)
        header_table.columns[1].width = Cm(16.5) 
        
        cell_logo = header_table.cell(0, 0)
        cell_texto = header_table.cell(0, 1)

        if os.path.exists(self.logo_path):
            try:
                p = cell_logo.paragraphs[0]
                run = p.add_run()
                run.add_picture(self.logo_path, width=Cm(2.2))
                # Imã: Logo para a DIREITA
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT 
            except: cell_logo.text = "LOGO"
        else: cell_logo.text = "LOGO"

        p_empresa = cell_texto.paragraphs[0]
        # Imã: Texto para a ESQUERDA
        p_empresa.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_empresa.paragraph_format.left_indent = Cm(0.3)
        p_empresa.paragraph_format.space_after = Pt(0)
        
        run_title = p_empresa.add_run("Associação Municipal de Apoio Comunitário\n")
        run_title.bold = True
        run_title.font.size = Pt(14)
        
        p_empresa.add_run("Rua Espírito Santo, 434 – Centro / Juiz de Fora – MG\n")
        run_folha = p_empresa.add_run("FOLHA DE PONTO")
        run_folha.bold = True
        run_folha.font.size = Pt(12)

    def celula_texto(self, cell, text, bold=False, size=10, align=WD_ALIGN_PARAGRAPH.CENTER):
        cell.text = text
        if cell.paragraphs:
            p = cell.paragraphs[0]
            p.alignment = align
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            if p.runs:
                run = p.runs[0]
                run.font.bold = bold
                run.font.size = Pt(size)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER