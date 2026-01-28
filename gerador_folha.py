import os
import calendar
from datetime import datetime, date, timedelta
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
    def __init__(self):
        # OBS: O código atual desenha a folha do zero, ignorando a "Regra de Ouro" de usar template.
        # O parâmetro modelo_path foi removido pois não era utilizado.
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
            raise ValueError(f"Bloqueado: Não é permitido gerar folhas com mais de 3 meses de retrocesso.\nMês solicitado: {mes_alvo}/{ano_alvo}")

        if data_alvo > data_atual_base:
            if diferenca_meses == -1:
                if hoje.day < 20:
                    raise ValueError(f"Bloqueado: A folha do próximo mês ({mes_alvo}/{ano_alvo}) só pode ser gerada a partir do dia 20.")
            elif diferenca_meses < -1:
                 raise ValueError(f"Bloqueado: Não é permitido gerar folhas tão adiante no tempo.")

    def calcular_corpus_christi(self, ano):
        """Calcula Corpus Christi matematicamente (Páscoa + 60 dias)"""
        a = ano % 19
        b = ano // 100
        c = ano % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        mes_pascoa = (h + l - 7 * m + 114) // 31
        dia_pascoa = ((h + l - 7 * m + 114) % 31) + 1
        
        data_pascoa = date(ano, mes_pascoa, dia_pascoa)
        return data_pascoa + timedelta(days=60)

    def obter_nome_feriado(self, data_obj, feriados_lib):
        fixos = {
            (1, 1): "Confraternização Universal", 
            (21, 4): "Tiradentes", 
            (1, 5): "Dia do Trabalho",
            (13, 6): "Santo Antônio", # Padroeiro JF
            (7, 9): "Independência do Brasil", 
            (12, 10): "Nossa Sra. Aparecida", 
            (2, 11): "Finados",
            (15, 11): "Proclamação da República", 
            (20, 11): "Consciência Negra", 
            (25, 12): "Natal"
        }
        if (data_obj.day, data_obj.month) in fixos: 
            return fixos[(data_obj.day, data_obj.month)]

        nome = feriados_lib.get(data_obj)
        
        if nome:
            traducoes = {
                "Mardi Gras": "Carnaval", "Carnival": "Carnaval", 
                "Good Friday": "Sexta-feira Santa",
                "Corpus Christi": "Corpus Christi", 
                "Easter Sunday": "Páscoa", "Ash Wednesday": "Quarta-feira de Cinzas"
            }
            for eng, pt in traducoes.items():
                if eng in nome:
                    return pt
            return nome
            
        return None

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
        data_corpus = self.calcular_corpus_christi(ano)
        feriados_br.append({data_corpus: "Corpus Christi"})

        doc = Document()
        
        # Margens Estreitas (Economia de espaço vertical)
        for section in doc.sections:
            section.top_margin = Cm(0.5)
            section.bottom_margin = Cm(0.5)
            section.left_margin = Cm(1.0)
            section.right_margin = Cm(1.0)

        mes_extenso = MESES[int(mes)]

        # --- 1. CABEÇALHO ---
        self._inserir_cabecalho(doc)

        # Espaçador reduzido
        self.add_spacer(doc, pt_size=1)

        # --- 2. DADOS DO FUNCIONÁRIO ---
        table_info = doc.add_table(rows=3, cols=2)
        table_info.style = 'Table Grid'
        
        unidade = funcionario.get('unidade', funcionario.get('lotacao', ''))

        self.celula_texto(table_info.cell(0, 0), f"Nome: {funcionario['nome']}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        self.celula_texto(table_info.cell(0, 1), f"Matrícula: {funcionario['matricula']}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        
        cell_lotacao = table_info.cell(1, 0)
        cell_lotacao.merge(table_info.cell(1, 1))
        self.celula_texto(cell_lotacao, f"Lotação: {unidade}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        
        self.celula_texto(table_info.cell(2, 0), f"Cargo: {funcionario.get('cargo', '')}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)
        self.celula_texto(table_info.cell(2, 1), f"Mês de Referência: {mes_extenso}/{ano}", align=WD_ALIGN_PARAGRAPH.LEFT, size=9)

        # Espaçador reduzido
        self.add_spacer(doc, pt_size=2)

        # --- 3. TABELA DE PONTO (12 COLUNAS) ---
        table = doc.add_table(rows=0, cols=12)
        table.style = 'Table Grid'
        table.autofit = False
        table.allow_autofit = False

        # Larguras
        larguras = [
            1.55, 1.55, 1.55, 1.55, 1.55, 1.55, 
            1.55, 1.55, 1.55, 1.55, 1.55, 1.55
        ]

        # Linha 1: Títulos Macro
        row_h1 = table.add_row()
        self.definir_altura_linha(row_h1, 0.7) # Reduzi levemente header
        
        self.celula_texto(row_h1.cells[0], "Dados", size=7)
        self.celula_texto(row_h1.cells[1], "Primeira Jornada", size=7)
        row_h1.cells[1].merge(row_h1.cells[4])
        self.celula_texto(row_h1.cells[5], "Segunda Jornada", size=7)
        row_h1.cells[5].merge(row_h1.cells[8])
        self.celula_texto(row_h1.cells[9], "H. Extra", size=7)
        row_h1.cells[9].merge(row_h1.cells[10])
        self.celula_texto(row_h1.cells[11], "Visto/Obs", size=7)

        # Linha 2: Subtítulos
        row_h2 = table.add_row()
        self.definir_altura_linha(row_h2, 0.5)
        
        cols_titulos = [
            "Dia/Sem", "Entr", "Rub", "Saída", "Rub", 
            "Entr", "Rub", "Saída", "Rub", 
            "Entr", "Saída", "Assinatura"
        ]
        
        for i, tit in enumerate(cols_titulos):
            self.celula_texto(row_h2.cells[i], tit, bold=True, size=6)
            row_h2.cells[i].width = Cm(larguras[i])

        # --- 4. PREENCHIMENTO DOS DIAS ---
        _, num_dias = calendar.monthrange(ano, mes)
        
        lista_ferias = funcionario.get('ferias', [])

        def verificar_ferias(data_obj, lista_f):
            if not lista_f:
                return False
            for p in lista_f:
                try:
                    ini = datetime.strptime(p['inicio'], "%Y-%m-%d").date()
                    fim = datetime.strptime(p['fim'], "%Y-%m-%d").date()
                    if ini <= data_obj <= fim:
                        return True
                except:
                    continue
            return False

        for dia in range(1, num_dias + 1):
            data = date(ano, mes, dia)
            idx_sem = data.weekday()
            nome_sem = DIAS_SEMANA[idx_sem]
            feriado = self.obter_nome_feriado(data, feriados_br)
            em_ferias = verificar_ferias(data, lista_ferias)

            row = table.add_row()
            # --- AJUSTE DE ALTURA PARA CABER NA FOLHA ---
            self.definir_altura_linha(row, 0.61) 

            for i, w in enumerate(larguras):
                row.cells[i].width = Cm(w)

            texto_dia_sem = f"{dia:02d} - {nome_sem}"
            self.celula_texto(row.cells[0], texto_dia_sem, size=8)

            bloquear = False
            texto_bloqueio = ""

            if em_ferias:
                bloquear = True
                texto_bloqueio = "FÉRIAS"
            elif feriado:
                bloquear = True
                texto_bloqueio = f"FERIADO - {feriado.upper()}"
            elif idx_sem == 5: 
                bloquear = True
                texto_bloqueio = "SÁBADO"
            elif idx_sem == 6: 
                bloquear = True
                texto_bloqueio = "DOMINGO"

            if bloquear:
                for cell in row.cells:
                    self.aplicar_fundo_cinza(cell)
                
                cell_inicio = row.cells[1]
                cell_fim = row.cells[11]
                cell_inicio.merge(cell_fim)
                self.celula_texto(cell_inicio, texto_bloqueio, bold=True, size=7)

        # Espaçador mínimo
        self.add_spacer(doc, pt_size=2)

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
        
        dir_saida = os.path.dirname(caminho_saida_pdf)
        if dir_saida:
            os.makedirs(dir_saida, exist_ok=True)
        
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

    def _inserir_cabecalho(self, doc):
        """
        Estratégia Simplificada:
        1. Tenta inserir 'cabecalho.png' como uma imagem única e completa (Logo + Texto).
        2. Se a imagem não existir, cria um cabeçalho manual apenas com texto (Fallback).
        """
        if os.path.exists(self.cabecalho_img_path):
            try:
                doc.add_picture(self.cabecalho_img_path, width=Cm(19.9))
                # Ajuste: Centralizar e remover espaçamento padrão do parágrafo da imagem
                last_p = doc.paragraphs[-1]
                last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                last_p.paragraph_format.left_indent = Cm(-0.4)
                last_p.paragraph_format.space_after = Pt(0)
                return
            except Exception as e:
                print(f"Erro ao inserir imagem de cabeçalho: {e}")
        
        # Fallback para o manual se a imagem falhar ou não existir
        self._criar_cabecalho_manual(doc)

    def _criar_cabecalho_manual(self, doc):
        """
        Fallback: Cria um cabeçalho simples (apenas texto e logo se houver)
        caso a imagem principal não exista.
        """
        header_table = doc.add_table(rows=1, cols=2)
        header_table.autofit = False
        
        # Coluna da Logo (menor) e Texto (maior)
        header_table.columns[0].width = Cm(3.0)
        header_table.columns[1].width = Cm(19.0) 
        
        cell_logo = header_table.cell(0, 0)
        cell_texto = header_table.cell(0, 1)

        # --- LOGO (Alinhada à Direita) ---
        if os.path.exists(self.logo_path):
            try:
                p = cell_logo.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(self.logo_path, width=Cm(2.5))
            except Exception as e:
                print(f"Erro logo: {e}")
                cell_logo.text = "LOGO"
        else:
            cell_logo.text = "LOGO"
        
        # Centraliza a logo verticalmente
        cell_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # --- TEXTO CENTRALIZADO COM HIERARQUIA ---
        p_empresa = cell_texto.paragraphs[0]
        p_empresa.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_empresa.paragraph_format.space_after = Pt(0)
        
        # 1. Nome da Associação (GRANDE e NEGRITO)
        run_title = p_empresa.add_run("Associação Municipal de Apoio Comunitário\n")
        run_title.bold = True
        run_title.font.size = Pt(14)
        
        # 2. Endereço Completo (PEQUENO e NORMAL)
        run_end = p_empresa.add_run("Rua Espírito Santo, 434 – Centro / Juiz de Fora – MG / Cep: 36010-040\n\n")
        run_end.bold = False
        run_end.font.size = Pt(9)
        
        # 3. Título (GRANDE e NEGRITO)
        run_folha = p_empresa.add_run("FOLHA DE PONTO")
        run_folha.bold = True
        run_folha.font.size = Pt(14)
        
        # Centraliza o texto verticalmente
        cell_texto.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

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