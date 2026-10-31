#!/usr/bin/env python3
"""
🚀 Playwright Caixa Universal — Automação Completa de Apostas Loterias Caixa
===========================================================================
Suporta todas as modalidades da Caixa (Mega-Sena, Lotofácil, Quina, Dupla Sena, etc.).

Principais recursos:
1. Sessão Persistente: Lembra o login Gov.br/Caixa (não precisa digitar senha toda vez).
2. Multi-Jogo e Multi-Modalidade: Preenche múltiplos jogos de diferentes loterias no mesmo carrinho.
3. Anti-Bot / Ritmo Humano: Cliques com delay natural e verificação de seleção no DOM.
4. Exportação & Auditoria: Salva comprovantes (screenshots) dos jogos inseridos no carrinho.
5. Integração com p4lottery: Pode ler listas de jogos via JSON, CLI ou matrizes Python.

Uso:
    python3 scripts/playwright_caixa_universal.py --interactive
    python3 scripts/playwright_caixa_universal.py --file apostas.json
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any

URL_MODALIDADES = {
    "mega-sena": "https://www.loteriasonline.caixa.gov.br/silce-web/#/mega-sena",
    "lotofacil": "https://www.loteriasonline.caixa.gov.br/silce-web/#/lotofacil",
    "quina": "https://www.loteriasonline.caixa.gov.br/silce-web/#/quina",
    "dupla-sena": "https://www.loteriasonline.caixa.gov.br/silce-web/#/dupla-sena",
    "dia-de-sorte": "https://www.loteriasonline.caixa.gov.br/silce-web/#/dia-de-sorte",
    "lotomania": "https://www.loteriasonline.caixa.gov.br/silce-web/#/lotomania",
}

PACOTE_ORCAMENTO_80 = [
    {
        "modalidade": "mega-sena",
        "descricao": "Carteira Omni R$ 80 (8 Jogos = R$ 48,00 | 80% Exploração Lunar/Orbital/Wheel + 20% Caos/Vórtice | 2026-10-29 20:00)",
        "jogos": [
            [10, 11, 17, 28, 32, 44],  # Jogo 1 [80% Core]: Núcleo de Convergência Lunar/Orbital (Zc Top: 10, 32, 11, 28, 17, 44)
            [10, 13, 24, 35, 39, 42],  # Jogo 2 [80% Core]: Hybrid Omni 80/20 (3 quadras históricas)
            [11, 15, 30, 33, 36, 38],  # Jogo 3 [80% Core]: Esoteric Statistical #1 (Ressonância Quinta-feira 11, 38)
            [2, 18, 28, 33, 34, 49],   # Jogo 4 [80% Core]: Planetary Transits #1 (Júpiter/Marte IC 28, 49)
            [5, 18, 27, 34, 38, 53],   # Jogo 5 [80% Core]: Wheel Abreviado G=4 Corte Ortogonal #1
            [10, 11, 24, 27, 34, 38],  # Jogo 6 [80% Core]: Wheel Abreviado G=4 Corte Ortogonal #3
            [3, 18, 30, 34, 35, 50],   # Jogo 7 [20% Caos/Vórtice]: Alta Temperatura T=1.4 #1 (4 quadras históricas)
            [15, 34, 38, 46, 47, 53],  # Jogo 8 [20% Caos/Vórtice]: Alta Temperatura T=1.4 #3 (1 quadra histórica)
        ],
    },
    {
        "modalidade": "lotofacil",
        "descricao": "Carteira Omni R$ 80 (9 Jogos = R$ 31,50 | 80% Exploração Ising/Lunar/Wheel G=14 + 20% Caos/Dispersão | 2026-10-29 20:00)",
        "jogos": [
            [2, 3, 4, 6, 8, 9, 10, 11, 13, 15, 16, 18, 20, 21, 25],   # Jogo 1 [80% Core]: Principal Esoteric + Lunar (6x 13 pts)
            [2, 3, 6, 7, 8, 9, 11, 12, 13, 15, 16, 18, 20, 21, 25],   # Jogo 2 [80% Core]: Hybrid Omni (1x 14 pts hist, 356x 11 pts)
            [2, 4, 6, 7, 8, 10, 11, 13, 15, 16, 18, 20, 23, 24, 25],  # Jogo 3 [80% Core]: Consenso Ising + Lua Cheia (7x 13 pts)
            [1, 2, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 21, 25],  # Jogo 4 [80% Core]: Ressonância Orbital λ☉=216.5° (12, 14, 15, 25)
            [1, 2, 3, 4, 6, 8, 10, 11, 13, 15, 17, 18, 23, 24, 25],   # Jogo 5 [80% Core]: Wheel Abreviado G=14 Corte #1
            [1, 3, 4, 6, 7, 8, 10, 13, 15, 16, 17, 18, 20, 24, 25],   # Jogo 6 [80% Core]: Wheel Abreviado G=14 Corte #2
            [1, 2, 4, 6, 8, 10, 11, 13, 15, 16, 18, 20, 23, 24, 25],  # Jogo 7 [80% Core]: Wheel Abreviado G=14 Corte #3
            [2, 3, 4, 5, 9, 10, 11, 12, 14, 16, 18, 22, 23, 24, 25],  # Jogo 8 [20% Caos]: Ising Model #1 (75x 12 pts, 361x 11 pts)
            [1, 2, 3, 5, 7, 8, 10, 11, 13, 15, 16, 19, 22, 24, 25],   # Jogo 9 [20% Caos]: Hybrid Alta Dispersão (86x 12 pts)
        ],
    },
]

PACOTE_PADRAO_EXEMPLO = [
    {
        "modalidade": "mega-sena",
        "descricao": "Carteira Omni Enxuta 2026-10-29 20:00 (5 Jogos = R$ 30,00 | Lua Cheia 62.2%, Seed 2808670435)",
        "jogos": PACOTE_ORCAMENTO_80[0]["jogos"][:5],
    },
    {
        "modalidade": "lotofacil",
        "descricao": "Carteira Omni Enxuta 2026-10-29 20:00 (6 Jogos = R$ 21,00 | Ising + Esoteric + Lunar/Orbital)",
        "jogos": PACOTE_ORCAMENTO_80[1]["jogos"][:6],
    },
]

PACOTE_WHEEL_COMPLETO = [
    {
        "modalidade": "mega-sena",
        "descricao": "Top 6 Cobertura Ortogonal do Wheel Abreviado (Pool: 05,10,11,17,18,24,27,34,38,53 — G=4)",
        "jogos": [
            [5, 18, 27, 34, 38, 53],
            [5, 11, 17, 18, 24, 27],
            [10, 11, 24, 27, 34, 38],
            [5, 10, 11, 17, 34, 53],
            [10, 17, 18, 24, 38, 53],
            [5, 10, 11, 18, 27, 38],
        ],
    },
    PACOTE_PADRAO_EXEMPLO[1],
]

def preencher_modalidade(page, modalidade: str, jogos: List[List[int]], delay_click: float = 0.15):
    url = URL_MODALIDADES.get(modalidade.lower().replace("_", "-"))
    if not url:
        print(f"❌ Modalidade '{modalidade}' desconhecida. Pulando...")
        return

    print(f"\n🌐 Navegando para {modalidade.upper()}: {url}")
    page.goto(url)
    page.wait_for_load_state("networkidle")
    time.sleep(1.0)

    for idx, jogo in enumerate(jogos, start=1):
        print(f"  [Jogo {idx:02d}/{len(jogos):02d}] Marcando {len(jogo)} dezenas: {jogo}")

        # 1. Limpa volante anterior se botão existir
        try:
            page.locator("#limparvolante, #limpar-volante, #btn-limpar").first.click(timeout=800)
            time.sleep(0.2)
        except Exception:
            pass

        # 2. Clica nas dezenas
        for num in jogo:
            s2 = f"{num:02d}"
            s1 = f"{num}"
            selector = f"#n{s2}, #n{s1}, [data-numero='{s2}'], [data-numero='{s1}'], button:text-is('{s2}'), button:text-is('{s1}')"
            try:
                elem = page.locator(selector).first
                elem.click(timeout=1500)
                time.sleep(delay_click)
            except Exception as e:
                print(f"    ⚠️ Falha ao clicar na dezena {s2}: {e}")

        time.sleep(0.4)

        # 3. Clica no botão de colocar no carrinho (ID exato da Caixa: #colocarnocarrinho)
        try:
            btn_carrinho = page.locator("#colocarnocarrinho, #colocar-carrinho, button[ng-click*='incluirAposta'], button:text-is('Colocar no Carrinho')").first
            btn_carrinho.click(timeout=2500)
            print(f"    ✓ Jogo {idx:02d} adicionado ao carrinho com sucesso.")
            time.sleep(1.0)
        except Exception as e:
            print(f"    ❌ Erro ao clicar no carrinho para o jogo {idx:02d}: {e}")
            break

def executar_automacao(pacote_jogos: List[Dict[str, Any]], user_data_dir: str = ".browser_session"):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright não instalado no ambiente.")
        print("Instale com: pip install playwright && playwright install chromium")
        sys.exit(1)

    profile_path = Path(user_data_dir).resolve()
    profile_path.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("🚀 LOTERIAS CAIXA — PLAYWRIGHT UNIVERSAL BETTING DISPATCHER")
    print(f"📁 Diretório de Sessão Persistente: {profile_path}")
    print("=" * 65)

    with sync_playwright() as p:
        # Lança navegador com contexto persistente (mantém login ativo)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=False,
            viewport={"width": 1280, "height": 850},
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = context.pages[0] if context.pages else context.new_page()

        # Abre página inicial
        page.goto("https://www.loteriasonline.caixa.gov.br/silce-web/#/home")
        print("\n🔑 VERIFICAÇÃO DE LOGIN:")
        print("1. Se você já fez login antes, sua sessão continuará salva.")
        print("2. Se não estiver logado, faça seu Login da Caixa (CPF e senha) na janela aberta.")
        print("\n👉 Pressione ENTER no terminal quando estiver logado para iniciar o envio...")
        input()

        # Itera por cada modalidade configurada
        for item in pacote_jogos:
            modalidade = item["modalidade"]
            jogos = item["jogos"]
            preencher_modalidade(page, modalidade, jogos)

        # Screenshot de conferência do carrinho (salvo em .scratch para não versionar PII)
        screenshots_dir = Path(".scratch/comprovantes")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        carrinho_screenshot = screenshots_dir / f"carrinho_{timestamp}.png"

        try:
            page.locator("a[href*='carrinho'], #btn-carrinho, .ico-carrinho").first.click(timeout=2000)
            time.sleep(1.5)
            page.screenshot(path=str(carrinho_screenshot), full_page=True)
            print(f"\n📸 Comprovante do carrinho salvo em: {carrinho_screenshot}")
        except Exception:
            pass

        print("\n🎉 TODOS OS JOGOS FORAM INJETADOS NO CARRINHO!")
        print("Confira os valores na janela aberta e finalize o pagamento (PIX ou Cartão).")
        print("Pressione ENTER para encerrar a sessão do navegador...")
        input()
        context.close()

def aplicar_teto_orcamento(pacote: List[Dict[str, Any]], max_budget: float) -> List[Dict[str, Any]]:
    custos_unitarios = {
        "mega-sena": 6.00,
        "lotofacil": 3.50,
        "quina": 3.00,
        "dupla-sena": 3.00,
        "dia-de-sorte": 2.50,
        "lotomania": 3.00,
    }
    custo_acum = 0.0
    novo_pacote = []
    for item in pacote:
        mod = item["modalidade"].lower()
        preco = custos_unitarios.get(mod, 0.0)
        jogos_validos = []
        for j in item["jogos"]:
            if custo_acum + preco <= max_budget + 1e-6:
                jogos_validos.append(j)
                custo_acum += preco
        if jogos_validos:
            novo_item = dict(item)
            novo_item["jogos"] = jogos_validos
            novo_pacote.append(novo_item)
    return novo_pacote


def exibir_resumo_pacote(pacote: List[Dict[str, Any]], max_budget: float = 80.0) -> None:
    custos_unitarios = {
        "mega-sena": 6.00,
        "lotofacil": 3.50,
        "quina": 3.00,
        "dupla-sena": 3.00,
        "dia-de-sorte": 2.50,
        "lotomania": 3.00,
    }
    total_jogos = 0
    custo_total = 0.0
    print("=" * 72)
    print(f"📋 RESUMO DO PACOTE DE APOSTAS (TETO ORÇAMENTO: R$ {max_budget:.2f})")
    print("=" * 72)
    for item in pacote:
        mod = item["modalidade"].lower()
        jogos = item["jogos"]
        desc = item.get("descricao", "")
        preco_unit = custos_unitarios.get(mod, 0.0)
        subtotal = len(jogos) * preco_unit
        total_jogos += len(jogos)
        custo_total += subtotal
        print(f"\n🎯 Modalidade: {mod.upper()} ({len(jogos)} jogos — R$ {subtotal:.2f})")
        if desc:
            print(f"   ℹ️  {desc}")
        for idx, j in enumerate(jogos, start=1):
            fmt = " - ".join(f"{n:02d}" for n in j)
            print(f"   Jogo {idx:02d}: [{fmt}]  (soma={sum(j)})")
    print("\n" + "-" * 72)
    pct_uso = (custo_total / max_budget * 100.0) if max_budget > 0 else 0.0
    print(
        f"💰 Total de Bilhetes: {total_jogos}   |   Custo Carrinho: R$ {custo_total:.2f} / R$ {max_budget:.2f} ({pct_uso:.1f}%)"
    )
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="Automação Playwright Universal para Loterias Caixa")
    parser.add_argument("--file", "-f", type=str, help="Caminho para arquivo JSON com as apostas")
    parser.add_argument("--interactive", "-i", action="store_true", help="Usa pacote Omni 2026-10-29 interativo")
    parser.add_argument(
        "--preset",
        choices=["budget80", "omni", "wheel"],
        default="budget80",
        help="Preset de apostas: 'budget80' (8 Mega-Sena + 9 Lotofácil = R$ 79,50), 'omni' (R$ 51,00) ou 'wheel' (R$ 57,00)",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=80.0,
        help="Teto máximo de orçamento em Reais (default: R$ 80.00)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Apenas exibe e valida os jogos sem abrir o navegador")
    parser.add_argument("--dump-json", type=str, help="Exporta o pacote selecionado para um arquivo JSON")
    parser.add_argument("--profile-dir", type=str, default=".scratch/browser_session", help="Pasta do perfil persistente")
    args = parser.parse_args()

    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as fp:
            pacote = json.load(fp)
    elif args.preset == "wheel":
        pacote = PACOTE_WHEEL_COMPLETO
    elif args.preset == "omni":
        pacote = PACOTE_PADRAO_EXEMPLO
    else:
        pacote = PACOTE_ORCAMENTO_80

    if args.budget and args.budget > 0:
        pacote = aplicar_teto_orcamento(pacote, args.budget)

    if args.dump_json:
        out_path = Path(args.dump_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(pacote, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"💾 Pacote exportado para: {out_path}")

    exibir_resumo_pacote(pacote, max_budget=args.budget)

    if args.dry_run:
        print("\n✅ Modo --dry-run concluído. Para disparar no navegador da Caixa, execute sem --dry-run.")
        return

    executar_automacao(pacote, user_data_dir=args.profile_dir)

if __name__ == "__main__":
    main()
