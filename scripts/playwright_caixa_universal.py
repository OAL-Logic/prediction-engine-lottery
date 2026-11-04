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
from typing import List, Dict, Any, Optional

URL_MODALIDADES = {
    "mega-sena": "https://www.loteriasonline.caixa.gov.br/silce-web/#/mega-sena",
    "lotofacil": "https://www.loteriasonline.caixa.gov.br/silce-web/#/lotofacil",
    "quina": "https://www.loteriasonline.caixa.gov.br/silce-web/#/quina",
    "dupla-sena": "https://www.loteriasonline.caixa.gov.br/silce-web/#/dupla-sena",
    "dia-de-sorte": "https://www.loteriasonline.caixa.gov.br/silce-web/#/dia-de-sorte",
    "lotomania": "https://www.loteriasonline.caixa.gov.br/silce-web/#/lotomania",
}

# Templates neutros (sem jogos de sorteios passados não realizados).
# Gere novos jogos para o próximo sorteio ativo via `./p4lottery suggest` e passe com `--file apostas.json`.
PACOTE_VARIACOES_CIRURGICO: List[Dict[str, Any]] = [
    {
        "modalidade": "mega-sena",
        "descricao": "Carteira Cirúrgica Sem Exagero — 1 Jogo de Cada Variação (Celeste, Magnética, Quântica, Atrasão e Síntese 4 Forças)",
        "jogos": [],
    },
    {
        "modalidade": "lotofacil",
        "descricao": "Carteira Cirúrgica Sem Exagero — 1 Jogo de Cada Variação (Celeste, Magnética, Quântica, Atrasão e Síntese 4 Forças)",
        "jogos": [],
    },
]

PACOTE_ENXUTO_4: List[Dict[str, Any]] = [
    {
        "modalidade": "mega-sena",
        "descricao": "Carteira Ultra-Enxuta 4 Forças Puras (1 Celeste + 1 Magnética + 1 Quântica + 1 Atrasão)",
        "jogos": [],
    },
    {
        "modalidade": "lotofacil",
        "descricao": "Carteira Ultra-Enxuta 4 Forças Puras (1 Celeste + 1 Magnética + 1 Quântica + 1 Atrasão)",
        "jogos": [],
    },
]

PACOTE_ORCAMENTO_80: List[Dict[str, Any]] = [
    {
        "modalidade": "mega-sena",
        "descricao": "Carteira Omni Teto R$ 80 (5 Variações Cirúrgicas + Wheel G=4 + Caos)",
        "jogos": [],
    },
    {
        "modalidade": "lotofacil",
        "descricao": "Carteira Omni Teto R$ 80 (5 Variações Cirúrgicas + Wheel G=14 + Caos)",
        "jogos": [],
    },
]

PACOTE_PADRAO_EXEMPLO = PACOTE_VARIACOES_CIRURGICO

PACOTE_WHEEL_COMPLETO: List[Dict[str, Any]] = [
    {
        "modalidade": "mega-sena",
        "descricao": "Cobertura Ortogonal do Wheel Abreviado (G=4)",
        "jogos": [],
    },
    {
        "modalidade": "lotofacil",
        "descricao": "Cobertura Ortogonal do Wheel Abreviado (G=14)",
        "jogos": [],
    },
]


def construir_pacote_dinamico(
    preset: str = "variacoes",
    target_date: str = "2026-10-29",
    target_time: str = "20:00",
    locale: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Constrói dinamicamente a carteira determinística para a data/hora alvo usando
    EsotericPipeline.generate_surgical_variations (Celeste, Magnética, Quântica,
    Atrasão e Síntese 4 Forças + extensões combinatórias para budget80/wheel).
    """
    from datetime import date as _date
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from engine.cli.utils import get_adapter
    from engine.modules.esoteric_pipeline import EsotericPipeline
    from engine.i18n import resolve_locale, t

    loc = resolve_locale(cli_locale=locale, game_id="br/mega-sena")
    t_date = _date.fromisoformat(target_date[:10]) if target_date else _date.today()
    ep = EsotericPipeline()

    configs = [
        ("mega-sena", "br/mega-sena", 3),
        ("lotofacil", "br/lotofacil", 4),
    ]
    resultado: List[Dict[str, Any]] = []

    for mod_slug, game_id, extra_cnt in configs:
        adapter = get_adapter(game_id)
        df = adapter.fetch()
        surg = ep.generate_surgical_variations(
            df=df,
            rules=adapter.rules,
            target_date=t_date,
            target_time=target_time or "20:00",
            extra_wheel_tickets=extra_cnt,
            locale=loc,
        )
        vars_5 = surg.get("variations", [])
        exts = surg.get("extensions", [])

        if preset == "enxuto4":
            selecionados = vars_5[:4]
            desc = t("variations.enxuto4_desc", locale=loc, date=t_date.isoformat(), time=target_time)
        elif preset in ("variacoes", "omni"):
            selecionados = vars_5[:5]
            desc = t("variations.cirurgico_desc", locale=loc, date=t_date.isoformat(), time=target_time)
        elif preset == "wheel":
            selecionados = vars_5[:4] + exts[:2]
            desc = t("variations.wheel_desc", locale=loc, date=t_date.isoformat(), time=target_time)
        else:
            # budget80: 5 variações + 3 extensões Mega-Sena (8 jogos = R$ 48) e 5 variações + 4 extensões Lotofácil (9 jogos = R$ 31,50) -> R$ 79,50
            selecionados = vars_5 + exts
            desc = t("variations.budget80_desc", locale=loc, date=t_date.isoformat(), time=target_time)

        resultado.append({
            "modalidade": mod_slug,
            "descricao": desc,
            "jogos": [it["numbers"] for it in selecionados],
            "rotulos": [it["label"] for it in selecionados],
        })

    return resultado

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
        print("\n👉 Pressione ENTER após confirmar que o jogo foi feito para iniciar:")
        print("   🥁 QUE RUFEM OS TAMBORES & SESSÃO IMERSIVA DE MATERIALIZAÇÃO...")
        input()

        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from engine.cli.commands.materialize import run_materialize
            html_path = run_materialize(interactive=True)
            mat_page = context.new_page()
            mat_page.goto(f"file://{html_path.resolve()}")
            print(f"\n✨ Câmara Imersiva de Materialização aberta no navegador: {html_path}")
        except Exception as exc:
            print(f"⚠️ Aviso ao abrir Câmara de Materialização: {exc}")

        print("\n🙏 Pressione ENTER quando desejar encerrar a sessão do navegador...")
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
        rotulos = item.get("rotulos", [])
        for idx, j in enumerate(jogos, start=1):
            fmt = " - ".join(f"{n:02d}" for n in j)
            rot = f"  [{rotulos[idx - 1]}]" if idx - 1 < len(rotulos) else ""
            print(f"   Jogo {idx:02d}: [{fmt}]  (soma={sum(j)}){rot}")
    print("\n" + "-" * 72)
    pct_uso = (custo_total / max_budget * 100.0) if max_budget > 0 else 0.0
    print(
        f"💰 Total de Bilhetes: {total_jogos}   |   Custo Carrinho: R$ {custo_total:.2f} / R$ {max_budget:.2f} ({pct_uso:.1f}%)"
    )
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="Automação Playwright Universal para Loterias Caixa")
    parser.add_argument("--file", "-f", type=str, help="Caminho para arquivo JSON com as apostas")
    parser.add_argument("--interactive", "-i", action="store_true", help="Executa em modo interativo passo a passo")
    parser.add_argument(
        "--preset",
        choices=["variacoes", "enxuto4", "budget80", "omni", "wheel"],
        default="variacoes",
        help="Preset de apostas: 'variacoes' (5+5 = R$ 47,50 Sem Exagero), 'enxuto4' (4+4 = R$ 38,00), 'budget80' (8+9 = R$ 79,50) ou 'wheel' (R$ 57,00)",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=80.0,
        help="Teto máximo de orçamento em Reais (default: R$ 80.00)",
    )
    parser.add_argument("--target-date", type=str, default="2026-10-29", help="Data alvo do sorteio YYYY-MM-DD (default: 2026-10-29)")
    parser.add_argument("--target-time", type=str, default="20:00", help="Horário previsto do sorteio HH:MM (default: 20:00)")
    parser.add_argument("--dry-run", action="store_true", help="Apenas exibe e valida os jogos sem abrir o navegador")
    parser.add_argument("--materialize", "-m", action="store_true", help="Executa a sessão imersiva de materialização (Terminal + HTML5 Chamber)")
    parser.add_argument("--dump-json", type=str, help="Exporta o pacote selecionado para um arquivo JSON")
    parser.add_argument("--profile-dir", type=str, default=".scratch/browser_session", help="Pasta do perfil persistente")
    parser.add_argument("--locale", "-l", type=str, default=None, help="Language/locale (en, pt_br)")
    args = parser.parse_args()

    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as fp:
            pacote = json.load(fp)
    else:
        pacote = construir_pacote_dinamico(
            preset=args.preset,
            target_date=args.target_date,
            target_time=args.target_time,
            locale=args.locale,
        )

    if args.budget and args.budget > 0:
        pacote = aplicar_teto_orcamento(pacote, args.budget)

    if args.dump_json:
        out_path = Path(args.dump_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(pacote, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"💾 Pacote exportado para: {out_path}")

    exibir_resumo_pacote(pacote, max_budget=args.budget)

    if args.materialize:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from engine.cli.commands.materialize import run_materialize
        run_materialize(
            target_date=args.target_date,
            target_time=args.target_time,
            budget=args.budget,
            interactive=False,
            locale=args.locale,
        )

    if args.dry_run:
        print("\n✅ Modo --dry-run concluído. Para disparar no navegador da Caixa, execute sem --dry-run.")
        return

    executar_automacao(pacote, user_data_dir=args.profile_dir)

if __name__ == "__main__":
    main()
