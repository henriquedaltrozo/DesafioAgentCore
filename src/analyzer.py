import json
import pandas as pd
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import matplotlib
import io
import base64
from reportlab.platypus import Image as ReportLabImage

# Configurar matplotlib para não usar GUI
matplotlib.use('Agg')

class Analyzer:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = None
        self.df = None
        
    def load_data(self):
        """Carrega os dados do arquivo JSON"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
            
            # Criar DataFrame com as reclamações
            self.df = pd.DataFrame(self.data['reclamacoes'])
            self.df['data'] = pd.to_datetime(self.df['data'])
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def analyze_categories(self):
        """Analisa as categorias mais citadas"""
        if self.df is None:
            return None
            
        categoria_counts = self.df['categoria'].value_counts()
        total_reclamacoes = len(self.df)
        
        categoria_analysis = {}
        for categoria, count in categoria_counts.items():
            percentage = (count / total_reclamacoes) * 100
            categoria_analysis[categoria] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return categoria_analysis
    
    def analyze_status(self):
        """Analisa os status das reclamações"""
        if self.df is None:
            return None
            
        status_counts = self.df['status'].value_counts()
        total_reclamacoes = len(self.df)
        
        status_analysis = {}
        for status, count in status_counts.items():
            percentage = (count / total_reclamacoes) * 100
            status_analysis[status] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return status_analysis
    
    def analyze_trends(self):
        """Analisa tendências por data"""
        if self.df is None:
            return None
            
        # Agrupa por data
        trends = self.df.groupby('data').size().reset_index(name='count')
        
        # Análise por semana
        self.df['week'] = self.df['data'].dt.isocalendar().week
        weekly_trends = self.df.groupby('week').size()
        
        return {
            'daily_trends': trends,
            'weekly_trends': weekly_trends,
            'date_range': {
                'start': self.df['data'].min().strftime('%Y-%m-%d'),
                'end': self.df['data'].max().strftime('%Y-%m-%d')
            }
        }
    
    def get_top_issues(self, top_n=5):
        """Retorna os principais problemas por categoria"""
        if self.df is None:
            return None
            
        top_issues = {}
        for categoria in self.df['categoria'].unique():
            categoria_df = self.df[self.df['categoria'] == categoria]
            # Pegar os títulos mais comuns desta categoria
            titles = categoria_df['titulo'].value_counts().head(top_n)
            top_issues[categoria] = titles.to_dict()
        
        return top_issues
    
    def generate_summary_text(self):
        """Gera um resumo textual com insights"""
        if self.df is None:
            return "Erro: Dados não carregados"
        
        metadata = self.data['metadata']
        categoria_analysis = self.analyze_categories()
        status_analysis = self.analyze_status()
        trends = self.analyze_trends()
        
        summary = f"""
RELATÓRIO DE ANÁLISE DE RECLAMAÇÕES - {metadata['fonte']}

DADOS GERAIS:
• Total de reclamações: {metadata['total_reclamacoes']}
• Período analisado: {trends['date_range']['start']} a {trends['date_range']['end']}
• Data da extração: {metadata['data_extracao']}

CATEGORIAS MAIS CITADAS:
"""
        
        # Top 3 categorias
        sorted_categories = sorted(categoria_analysis.items(), key=lambda x: x[1]['count'], reverse=True)
        for i, (categoria, data) in enumerate(sorted_categories[:3], 1):
            summary += f"{i}. {categoria}: {data['count']} reclamações ({data['percentage']}%)\n"
        
        summary += f"\nDISTRIBUIÇÃO POR STATUS:\n"
        
        for status, data in status_analysis.items():
            summary += f"• {status}: {data['count']} ({data['percentage']}%)\n"
        
        # Insights adicionais
        summary += f"\nINSIGHTS IMPORTANTES:\n"
        
        # Taxa de resolução
        resolvidos = status_analysis.get('Resolvido', {}).get('count', 0)
        taxa_resolucao = (resolvidos / metadata['total_reclamacoes']) * 100
        summary += f"• Taxa de resolução: {taxa_resolucao:.1f}%\n"
        
        # Problemas não resolvidos
        nao_resolvidos = status_analysis.get('Não resolvido', {}).get('count', 0)
        nao_respondidas = status_analysis.get('Não respondida', {}).get('count', 0)
        problemas_pendentes = nao_resolvidos + nao_respondidas
        taxa_pendencia = (problemas_pendentes / metadata['total_reclamacoes']) * 100
        summary += f"• Problemas pendentes: {problemas_pendentes} ({taxa_pendencia:.1f}%)\n"
        
        # Categoria mais problemática
        categoria_top = sorted_categories[0]
        summary += f"• Categoria mais problemática: {categoria_top[0]} ({categoria_top[1]['percentage']}% das reclamações)\n"
        
        # Análise de palavras-chave nos títulos
        all_titles = ' '.join(self.df['titulo'].str.lower())
        palavras_comuns = ['app', 'cartão', 'pix', 'conta', 'problema', 'erro', 'não', 'banco']
        palavras_encontradas = []
        for palavra in palavras_comuns:
            if palavra in all_titles:
                count = all_titles.count(palavra)
                palavras_encontradas.append((palavra, count))
        
        if palavras_encontradas:
            palavras_encontradas.sort(key=lambda x: x[1], reverse=True)
            summary += f"• Palavras mais mencionadas nos títulos: {', '.join([f'{p[0]} ({p[1]}x)' for p in palavras_encontradas[:3]])}\n"
        
        return summary
    
    def create_charts(self):
        """Cria gráficos para o relatório"""
        charts = []
        
        if self.df is None:
            return charts
        
        # Gráfico 1: Distribuição por categorias
        plt.figure(figsize=(10, 6))
        categoria_counts = self.df['categoria'].value_counts()
        plt.pie(categoria_counts.values, labels=categoria_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Distribuição de Reclamações por Categoria')
        
        # Salvar como bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        charts.append(('categoria_pie', img_buffer.getvalue()))
        plt.close()
        
        # Gráfico 2: Distribuição por status
        plt.figure(figsize=(10, 6))
        status_counts = self.df['status'].value_counts()
        colors_status = ['#2ecc71', '#e74c3c', '#f39c12', '#3498db']
        plt.bar(status_counts.index, status_counts.values, color=colors_status[:len(status_counts)])
        plt.title('Distribuição de Reclamações por Status')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Quantidade')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        charts.append(('status_bar', img_buffer.getvalue()))
        plt.close()
        
        # Gráfico 3: Timeline das reclamações
        plt.figure(figsize=(12, 6))
        daily_counts = self.df.groupby('data').size()
        plt.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=6)
        plt.title('Timeline de Reclamações')
        plt.xlabel('Data')
        plt.ylabel('Número de Reclamações')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        charts.append(('timeline', img_buffer.getvalue()))
        plt.close()
        
        return charts
    
    def generate_pdf_report(self, output_path="relatorio_reclamacoes.pdf"):
        """Gera o relatório em PDF"""
        if self.df is None:
            return False
        
        # Garantir que o diretório results existe
        import os
        results_dir = "../results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)
        
        # Se apenas o nome do arquivo foi fornecido, colocar na pasta results
        if not os.path.dirname(output_path):
            output_path = os.path.join(results_dir, output_path)
        
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                alignment=TA_JUSTIFY
            )
            
            # Conteúdo do PDF
            story = []
            
            # Título
            story.append(Paragraph("RELATÓRIO DE ANÁLISE DE RECLAMAÇÕES", title_style))
            story.append(Spacer(1, 20))
            
            # Informações gerais
            metadata = self.data['metadata']
            info_text = f"""
            <b>Fonte:</b> {metadata['fonte']}<br/>
            <b>Total de Reclamações:</b> {metadata['total_reclamacoes']}<br/>
            <b>Data de Extração:</b> {metadata['data_extracao']}<br/>
            """
            story.append(Paragraph(info_text, normal_style))
            story.append(Spacer(1, 20))
            
            # Resumo executivo
            story.append(Paragraph("RESUMO EXECUTIVO", heading_style))
            summary_text = self.generate_summary_text()
            # Converter quebras de linha para HTML
            summary_html = summary_text.replace('\n', '<br/>')
            story.append(Paragraph(summary_html, normal_style))
            story.append(Spacer(1, 20))
            
            # Tabela de categorias
            story.append(Paragraph("ANÁLISE DETALHADA POR CATEGORIA", heading_style))
            categoria_analysis = self.analyze_categories()
            
            # Dados da tabela
            table_data = [['Categoria', 'Quantidade', 'Percentual']]
            for categoria, data in sorted(categoria_analysis.items(), key=lambda x: x[1]['count'], reverse=True):
                table_data.append([categoria, str(data['count']), f"{data['percentage']}%"])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Tabela de status
            story.append(Paragraph("ANÁLISE POR STATUS", heading_style))
            status_analysis = self.analyze_status()
            
            table_data = [['Status', 'Quantidade', 'Percentual']]
            for status, data in sorted(status_analysis.items(), key=lambda x: x[1]['count'], reverse=True):
                table_data.append([status, str(data['count']), f"{data['percentage']}%"])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Adicionar gráficos
            story.append(PageBreak())
            story.append(Paragraph("GRÁFICOS E VISUALIZAÇÕES", heading_style))
            
            charts = self.create_charts()
            for chart_name, chart_data in charts:
                img_buffer = io.BytesIO(chart_data)
                img = ReportLabImage(img_buffer, width=6*inch, height=3.6*inch)
                story.append(img)
                story.append(Spacer(1, 20))
            
            # Construir PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return False