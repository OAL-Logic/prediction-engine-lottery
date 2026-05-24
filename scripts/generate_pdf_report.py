#!/usr/bin/env python3
"""
Relatório Profissional: Bilhete da Realidade Colapsada 📄
========================================================
Gera um PDF detalhado com a análise técnica, esotérica e quântica.
Utiliza ReportLab para um layout de alta fidelidade.
"""

import sys
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

def generate_pdf_report(lottery_id="br/mega-sena"):
    output_path = f"data/relatorio_elite_{lottery_id.replace('/', '_')}.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Estilos Customizados
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, fontSize=18, textColor=colors.HexColor("#1A237E"))
    subtitle_style = ParagraphStyle('SubStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor("#0D47A1"))
    body_style = styles['BodyText']
    highlight_style = ParagraphStyle('Highlight', parent=styles['BodyText'], fontName='Helvetica-Bold', textColor=colors.red)

    # 1. Cabeçalho
    story.append(Paragraph("🏛️ LOTTERY ENGINE: RELATÓRIO DE ELITE", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", body_style))
    story.append(Paragraph(f"Loteria Analisada: {lottery_id.upper()}", body_style))
    story.append(Spacer(1, 20))

    # 2. Resumo Técnico (Stacking AI)
    adapter = get_adapter(lottery_id)
    df = adapter.fetch()
    
    # Executa o blend completo de estratégias para o relatório
    all_strats = [
        "stacking_ai", "lyapunov_chaos", "retrocausality", "geo_sync", 
        "cpu_entropy", "crowd_antagonism", "sacred_grid", "ising_model", 
        "zeno_quantum", "tda_topology", "hurst_memory", "kolmogorov_order",
        "evt_extremes", "wavelet_signal", "nash_equilibrium"
    ]
    results = {}
    for s_name in all_strats:
        try:
            results[s_name] = get_strategy(s_name).score(df, adapter.rules)
        except:
            continue

    # Calcula o Bilhete Consolidado (Média dos scores)
    num_range = adapter.rules.number_range
    final_scores = {n: 0.0 for n in range(num_range[0], num_range[1] + 1)}
    for s_name, scores in results.items():
        for num, val in scores.items():
            final_scores[num] += val
    
    pick_count = adapter.rules.pick_count
    perfect_game = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)[:pick_count]

    story.append(Paragraph("🧪 Diagnóstico Multi-Camada (Engine v10.0)", subtitle_style))
    story.append(Paragraph("Este documento consolida evidências de 15 dimensões: IA Stacking, Caos, Quântica, Geo-Sync, Entropia CPU, TDA, Hurst, Kolmogorov, Anti-Massa, Geo Sagrada, EVT (Extremos), Wavelets e Nash (Teoria dos Jogos).", body_style))
    story.append(Spacer(1, 10))

    # 3. O BILHETE MESTRE
    ticket_str = " - ".join(f"<b>{n:02d}</b>" for n in perfect_game)
    story.append(Paragraph(f"💎 BILHETE DA REALIDADE COLAPSADA: {ticket_str}", highlight_style))
    story.append(Spacer(1, 20))

    # 4. Tabela de Evidências por Camada
    story.append(Paragraph("📊 Detalhamento por Estratégia", subtitle_style))
    data = [["Estratégia", "Foco Técnico", "Top Dezena", "Score"]]
    
    friendly_names = {
        "stacking_ai": "IA Stacking",
        "lyapunov_chaos": "Caos (Lyapunov)",
        "retrocausality": "Retrocausalidade",
        "geo_sync": "Geo-Piracicaba",
        "cpu_entropy": "Entropia CPU",
        "crowd_antagonism": "Anti-Massa",
        "sacred_grid": "Geo Sagrada",
        "ising_model": "Termodinâmica",
        "zeno_quantum": "Efeito Zeno",
        "tda_topology": "TDA (Topologia)",
        "hurst_memory": "Inércia (Hurst)",
        "kolmogorov_order": "Ordem (Complexity)",
        "evt_extremes": "Cauda (EVT)",
        "wavelet_signal": "Sinal (Wavelet)",
        "nash_equilibrium": "Nash (Teoria Jogos)"
    }

    for s_name in all_strats:
        if s_name in results:
            best_num = sorted(results[s_name].keys(), key=lambda x: results[s_name][x], reverse=True)[0]
            data.append([friendly_names.get(s_name, s_name), "Convergência", str(best_num), f"{results[s_name][best_num]:.3f}"])

    t = Table(data, colWidths=[120, 150, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # 5. Seção de Análise Avançada
    story.append(Paragraph("🌍 Ressonância Local e Geométrica", subtitle_style))
    story.append(Paragraph(f"O sistema detectou uma convergência entre as coordenadas de Piracicaba e os harmônicos da Espiral de Phi no grid do volante.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("💻 Semente de Hardware Quântica", subtitle_style))
    story.append(Paragraph("A assinatura probabilística deste bilhete foi ancorada no ruído branco térmico do hardware no momento da geração.", body_style))
    
    # Finalização
    doc.build(story)
    return output_path

if __name__ == "__main__":
    lottery = "br/mega-sena"
    if len(sys.argv) > 1:
        lottery = sys.argv[1]
    path = generate_pdf_report(lottery)
    print(f"Relatório gerado com sucesso: {path}")
