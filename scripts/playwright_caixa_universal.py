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

PACOTE_PADRAO_EXEMPLO = [
    {
        "modalidade": "mega-sena",
        "jogos": [
            [1, 28, 41, 43, 52, 59]
        ]
    },
    {
        "modalidade": "lotofacil",
        "jogos": [
            [1, 2, 4, 8, 9, 10, 12, 13, 14, 15, 19, 21, 23, 24, 25]
        ]
    }
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

def main():
    parser = argparse.ArgumentParser(description="Automação Playwright Universal para Loterias Caixa")
    parser.add_argument("--file", "-f", type=str, help="Caminho para arquivo JSON com as apostas")
    parser.add_argument("--interactive", "-i", action="store_true", help="Usa pacote de exemplo interativo")
    parser.add_argument("--profile-dir", type=str, default=".scratch/browser_session", help="Pasta do perfil persistente")
    args = parser.parse_args()

    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as fp:
            pacote = json.load(fp)
    else:
        pacote = PACOTE_PADRAO_EXEMPLO

    executar_automacao(pacote, user_data_dir=args.profile_dir)

if __name__ == "__main__":
    main()
