#!/usr/bin/env python3
"""
🎰 Caixa Bolão Hunter & Scraper (Playwright & Chrome DevTools)
============================================================
Varre e filtra bolões oficiais da Caixa Econômica Federal (SILCE-Web)
focando em jogos de alta probabilidade (> 6 números) e dezenas estratégicas
para a Mega da Virada / Mega-Sena.

Funcionalidades:
1. Sessão Persistente (.scratch/browser_session) - reaproveita o login já feito.
2. Navega automaticamente para a aba de Bolões da modalidade.
3. Scrape de todos os cards de bolão disponíveis da rede lotérica.
4. Filtro por quantidade de dezenas (> 6 dezenas: jogos de 7, 8, 9, 10+ números).
5. Filtro & Ranking por dezenas estratégicas (ex: dezenas mais frequentes da Virada).
6. Opção de adicionar cotas selecionadas diretamente ao carrinho de compras!

Uso:
    python3 scripts/caixa_bolao_hunter.py --min-dezenas 7
    python3 scripts/caixa_bolao_hunter.py --min-dezenas 8 --numeros 10,05,34,33,41,58
    python3 scripts/caixa_bolao_hunter.py --min-dezenas 7 --add-to-cart
"""

import sys
import os
import re
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

URLS = {
    "mega-sena": "https://www.loteriasonline.caixa.gov.br/silce-web/#/mega-sena",
    "mega-da-virada": "https://www.loteriasonline.caixa.gov.br/silce-web/#/mega-sena/especial",
    "lotofacil": "https://www.loteriasonline.caixa.gov.br/silce-web/#/lotofacil",
    "quina": "https://www.loteriasonline.caixa.gov.br/silce-web/#/quina",
    "dupla-sena": "https://www.loteriasonline.caixa.gov.br/silce-web/#/dupla-sena",
}

# Dezenas históricas de elite da Mega da Virada e Mega-Sena
TOP_DEZENAS_VIRADA_DEFAULT = [10, 5, 34, 33, 41, 58, 51, 3, 32, 35, 56, 17, 36, 59, 12, 4, 37, 23]


def extrair_dados_cards_js() -> str:
    """
    Script JavaScript executado dentro do navegador para extrair
    com fidelidade os cards de bolão do DOM do SILCE.
    """
    return r"""
    () => {
        const resultado = [];
        // Mapeia possíveis containers de bolão no Angular
        const cards = Array.from(document.querySelectorAll(
            '.card-bolao, .item-bolao, [ng-repeat*="bolao"], .bolao-item, ' +
            '.card-aposta, .box-bolao, .card-jogo, div[class*="bolao"]'
        )).filter(el => {
            const txt = (el.innerText || '').toLowerCase();
            return txt.includes('cota') || txt.includes('bolão') || txt.includes('bolao');
        });

        // Se não encontrou seletores específicos, busca cartões genéricos que tenham 'cota' e 'R$'
        const alvos = cards.length > 0 ? cards : Array.from(document.querySelectorAll('div, li, tr')).filter(el => {
            if (el.children.length > 20 || el.children.length < 2) return false;
            const txt = (el.innerText || '');
            return (txt.includes('Cota') || txt.includes('COTA')) && txt.includes('R$');
        });

        alvos.forEach((card, idx) => {
            const txt = card.innerText || '';
            if (!txt.trim()) return;

            // Extrai valor da cota
            const precoMatch = txt.match(/R\$\s*([\d\.,]+)/i);
            const preco = precoMatch ? parseFloat(precoMatch[1].replace('.', '').replace(',', '.')) : 0.0;

            // Extrai número de cotas
            const cotasMatch = txt.match(/(\d+)\s*(?:de|\/)\s*(\d+)\s*cotas?/i) || txt.match(/(\d+)\s*cotas?\s*dispon[íi]ve/i);
            const cotasDisp = cotasMatch ? parseInt(cotasMatch[1]) : 1;
            const cotasTotal = (cotasMatch && cotasMatch[2]) ? parseInt(cotasMatch[2]) : null;

            // Extrai padrão de dezenas e jogos (ex: '1 jogo de 8 dezenas', '2 jogos de 7 números')
            let maxDezenas = 6;
            const qtdNumMatch = txt.match(/(\d+)\s*(?:jogos?|apostas?)\s*de\s*(\d+)\s*(?:n[úu]meros|dezenas)/gi) ||
                                txt.match(/(\d+)\s*(?:n[úu]meros|dezenas)/gi);

            const detalhesJogos = [];
            if (qtdNumMatch) {
                qtdNumMatch.forEach(m => {
                    detalhesJogos.push(m);
                    const nMatch = m.match(/(\d+)\s*(?:n[úu]meros|dezenas)/i);
                    if (nMatch) {
                        const n = parseInt(nMatch[1]);
                        if (n > maxDezenas) maxDezenas = n;
                    }
                });
            }

            // Extrai as dezenas impressas no card
            const dezenasSet = new Set();
            const dezenasMatch = txt.match(/\b([0-5]?\d|60)\b/g);
            // Procura números no formato dezena
            const blocosDezenas = Array.from(card.querySelectorAll('.dezena, .bola, .numero, span, button'))
                .map(e => e.innerText.trim())
                .filter(t => /^\d{1,2}$/.test(t) && parseInt(t) >= 1 && parseInt(t) <= 60);

            blocosDezenas.forEach(d => dezenasSet.add(parseInt(d)));

            // Localiza botão de compra/carrinho
            const btnCompra = card.querySelector('button[ng-click*="carrinho"], button[ng-click*="comprar"], button.btn-comprar, button:not([disabled])');
            const temBotao = !!btnCompra;

            resultado.push({
                index: idx,
                texto_resumo: txt.replace(/\s+/g, ' ').slice(0, 200),
                preco_cota: preco,
                cotas_disponiveis: cotasDisp,
                cotas_total: cotasTotal,
                max_dezenas: maxDezenas,
                detalhes_jogos: detalhesJogos,
                dezenas: Array.from(dezenasSet).sort((a,b) => a - b),
                pode_comprar: temBotao
            });
        });

        return resultado;
    }
    """


def extrair_dezenas_virada_historico() -> List[int]:
    """Retorna lista de dezenas ranqueadas da história da Mega da Virada."""
    return TOP_DEZENAS_VIRADA_DEFAULT


def calcular_score_bolao(
    bolao: Dict[str, Any],
    dezenas_alvo: List[int],
    min_dezenas: int = 6
) -> float:
    """
    Calcula um score para o bolão:
    1. Bônus exponencial para jogos com > 6 números (7, 8, 9, 10 dezenas).
    2. Bônus por número de dezenas coincidentes com o conjunto estratégico.
    3. Custo-benefício da cota.
    """
    score = 0.0
    max_d = bolao.get("max_dezenas", 6)

    # Multiplicador de chances combinatórias (fórmula C(n, 6))
    combinacoes = {
        6: 1,
        7: 7,
        8: 28,
        9: 84,
        10: 210,
        11: 462,
        12: 924,
        13: 1716,
        14: 3003,
        15: 5005,
    }
    fator_cobertura = combinacoes.get(max_d, 1)
    score += fator_cobertura * 10.0

    # Bônus por dezenas estratégicas encontradas
    dezenas_bolao = set(bolao.get("dezenas", []))
    if dezenas_bolao and dezenas_alvo:
        match_count = len(dezenas_bolao.intersection(set(dezenas_alvo)))
        score += match_count * 15.0

    # Relação valor da cota
    preco = bolao.get("preco_cota", 0.0)
    if preco > 0:
        # Pontua melhor cotas eficientes em relação ao número de jogos cobertos
        score += (fator_cobertura / preco) * 5.0

    return round(score, 2)


def executar_hunter(
    modalidade: str = "mega-da-virada",
    min_dezenas: int = 7,
    numeros_filtro: Optional[List[int]] = None,
    max_preco: Optional[float] = None,
    add_to_cart: bool = False,
    user_data_dir: str = ".scratch/browser_session",
    headless: bool = False
):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright não instalado. Instale com: pip install playwright")
        sys.exit(1)

    url = URLS.get(modalidade.lower().replace("_", "-"), URLS["mega-da-virada"])
    dezenas_estrategicas = numeros_filtro or extrair_dezenas_virada_historico()

    profile_path = Path(user_data_dir).resolve()
    profile_path.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🎯 CAIXA BOLÃO HUNTER & SCRAPER — MEGA DA VIRADA / MEGA-SENA")
    print("=" * 70)
    print(f"📌 Modalidade: {modalidade.upper()}")
    print(f"🎯 Critério Mínimo: Jogos com >={min_dezenas} dezenas (Mais de 6 números)")
    print(f"🔮 Dezenas Estratégicas Chave: {dezenas_estrategicas[:10]}...")
    if max_preco:
        print(f"💰 Teto por Cota: R$ {max_preco:.2f}")
    print(f"📁 Perfil de Navegador Persistente: {profile_path}")
    print("=" * 70)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            viewport={"width": 1366, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = context.pages[0] if context.pages else context.new_page()

        print(f"\n🌐 Navegando para: {url}")
        page.goto(url)
        page.wait_for_load_state("networkidle")
        time.sleep(1.5)

        # 1. Garante que estamos na aba Especial / Mega da Virada se for o caso
        if "virada" in modalidade or "especial" in url:
            try:
                aba_esp = page.locator("a:text-is('Especial'), button:text-is('Especial'), #abaEspecial, [href*='especial'], button:has-text('Mega da Virada')").first
                if aba_esp.count() > 0 and aba_esp.is_visible():
                    aba_esp.click(timeout=1500)
                    time.sleep(1.0)
                    print("  ✨ Aba Especial / Mega da Virada verificada.")
            except Exception:
                pass

        # 2. Localiza e ativa a aba de BOLÃO
        print("\n🔍 Buscando aba de Bolão CAIXA...")
        aba_bolao_encontrada = False
        seletores_aba_bolao = [
            "a:has-text('Bolão')",
            "button:has-text('Bolão')",
            "a:has-text('Bolão CAIXA')",
            "button:has-text('Bolão CAIXA')",
            "a:has-text('BOLÃO')",
            "button:has-text('BOLÃO')",
            "#aba-bolao",
            "#btn-bolao",
            "[href*='bolao']",
            "[ng-click*='bolao']",
            "[ng-click*='Bolao']",
            "li:has-text('Bolão')",
        ]

        for sel in seletores_aba_bolao:
            try:
                loc = page.locator(sel).first
                if loc.count() > 0 and loc.is_visible():
                    loc.scroll_into_view_if_needed(timeout=800)
                    loc.click(timeout=1500)
                    time.sleep(1.5)
                    aba_bolao_encontrada = True
                    print(f"  ✓ Aba Bolão ativada via seletor: {sel}")
                    break
            except Exception:
                continue

        if not aba_bolao_encontrada:
            print("  ⚠️ Atenção: A aba de Bolão não foi clicada automaticamente.")
            print("  👉 Se o navegador estiver aberto, clique na aba 'Bolão' ou 'Bolão CAIXA'.")
            print("  👉 Pressione ENTER aqui quando estiver na tela com os cartões de bolão...")
            input()

        # Aguarda renderização dos cards
        time.sleep(2.0)

        # Rola a página para disparar lazy loading de todos os bolões
        print("📜 Rolando página para carregar todos os bolões disponíveis...")
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 1000);")
            time.sleep(0.6)
        page.evaluate("window.scrollTo(0, 0);")
        time.sleep(0.5)

        # 3. Executa o scraper dos cards
        print("🔍 Extraindo e analisando bolões do portal...")
        dados_brutos = page.evaluate(extrair_dados_cards_js())

        if not dados_brutos:
            print("⚠️ Nenhum card com texto de cota/bolão foi localizado via automação.")
            print("ℹ️ Dica: As vendas de bolões online encerram às 19h30 para o sorteio do dia.")
            print("Se você tiver a lista de bolões na tela, verifique se a lotérica/concurso está disponível.")
            return

        print(f"✓ Total de bolões detectados no DOM: {len(dados_brutos)}")

        # 4. Filtragem & Ranking
        candidatos = []
        for b in dados_brutos:
            # Filtro de dezenas mínimas (> 6 números)
            if b.get("max_dezenas", 6) < min_dezenas:
                # Se não detectou max_dezenas via texto, mas temos dezenas listadas
                if len(b.get("dezenas", [])) < min_dezenas:
                    continue

            # Filtro de preço teto
            if max_preco and b.get("preco_cota", 0.0) > max_preco:
                continue

            score = calcular_score_bolao(b, dezenas_estrategicas, min_dezenas)
            b["score"] = score
            candidatos.append(b)

        candidatos.sort(key=lambda x: x["score"], reverse=True)

        print("\n" + "=" * 70)
        print(f"🏆 TOP BOLÕES ENCONTRADOS COM APOSTAS DE {min_dezenas}+ DEZENAS")
        print("=" * 70)

        if not candidatos:
            print(f"❌ Nenhum bolão com {min_dezenas}+ dezenas encontrado nesta página no momento.")
            print("ℹ️ Sugestão: Tente diminuir o critério para 7 ou 6 dezenas, ou tente mais cedo.")
            return

        for i, c in enumerate(candidatos[:10], start=1):
            dezenas_str = ", ".join(f"{d:02d}" for d in c.get("dezenas", [])) or "Dezenas ocultas / sob clique"
            max_d = c.get("max_dezenas", 6)
            detalhes = c.get("detalhes_jogos") or f"{max_d} dezenas"
            print(f"[{i:02d}] 🏷️ Card #{c['index']} | Score: {c['score']} pts")
            print(f"     📊 Estrutura: {detalhes}")
            print(f"     💰 Cota: R$ {c.get('preco_cota', 0.0):.2f} | Cotas Disp: {c.get('cotas_disponiveis')}")
            print(f"     🎲 Dezenas: [{dezenas_str}]")
            print(f"     📝 Resumo: {c.get('texto_resumo')[:110]}...")
            print("-" * 70)

        # Salva em JSON para auditoria
        output_file = Path(".scratch/boloes_encontrados.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(candidatos, f, indent=2, ensure_ascii=False)
        print(f"💾 Relatório detalhado salvo em: {output_file}")

        # 5. Adicionar ao carrinho se solicitado
        if add_to_cart and candidatos:
            melhor = candidatos[0]
            idx_card = melhor["index"]
            print(f"\n🛒 Adicionando ao carrinho a melhor cota selecionada (Card #{idx_card})...")
            try:
                # Localiza o card correspondente e clica no botão de adicionar/comprar
                cards_locator = page.locator(".card-bolao, .item-bolao, [ng-repeat*='bolao'], .bolao-item, .box-bolao, .card-jogo")
                if cards_locator.count() > idx_card:
                    card_el = cards_locator.nth(idx_card)
                    btn_buy = card_el.locator("button:has-text('Carrinho'), button:has-text('Comprar'), button:has-text('Cota'), button[ng-click*='carrinho']").first
                    btn_buy.click(timeout=2000)
                    time.sleep(1.0)
                    print("✓ Cota adicionada ao carrinho com sucesso!")
            except Exception as e:
                print(f"⚠️ Não foi possível clicar automaticamente no botão de compra: {e}")
                print("👉 Você pode clicar manualmente na janela do navegador aberta.")

        print("\n👉 Pressione ENTER para finalizar a sessão do Playwright...")
        input()


def main():
    parser = argparse.ArgumentParser(description="Caixa Bolão Hunter & Scraper")
    parser.add_argument("--modalidade", default="mega-da-virada", help="Modalidade (mega-da-virada, mega-sena, lotofacil)")
    parser.add_argument("--min-dezenas", type=int, default=7, help="Quantidade mínima de dezenas por jogo no bolão (ex: 7, 8, 9, 10)")
    parser.add_argument("--numeros", type=str, help="Dezenas específicas separadas por vírgula (ex: 10,05,34,33,41,58)")
    parser.add_argument("--max-preco", type=float, help="Preço máximo aceito por cota (R$)")
    parser.add_argument("--add-to-cart", action="store_true", help="Adicionar automaticamente a melhor cota ao carrinho")
    parser.add_argument("--user-data-dir", default=".scratch/browser_session", help="Diretório do perfil Playwright")
    parser.add_argument("--headless", action="store_true", help="Executar em modo headless sem janela")

    args = parser.parse_args()

    numeros_list = None
    if args.numeros:
        numeros_list = [int(n.strip()) for n in args.numeros.split(",") if n.strip().isdigit()]

    executar_hunter(
        modalidade=args.modalidade,
        min_dezenas=args.min_dezenas,
        numeros_filtro=numeros_list,
        max_preco=args.max_preco,
        add_to_cart=args.add_to_cart,
        user_data_dir=args.user_data_dir,
        headless=args.headless
    )


if __name__ == "__main__":
    main()
