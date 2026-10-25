#!/usr/bin/env python3
"""Gerenciador e Auditor de Rollout & Apostas Favoritas (.local).

Lê os arquivos protegidos history.local/*.local.yaml e audita o status de
concursos em andamento na Caixa sem vazar PII nem expor apostas em repositórios públicos.

Uso:
  python3 scripts/rollout_status.py
"""

import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.cli.utils import get_adapter

ROLLOUT_FILE = ROOT / "history.local" / "rollout.local.yaml"
FAVORITAS_FILE = ROOT / "history.local" / "favoritas.local.yaml"

def main():
    print("=" * 70)
    print("🎰 PAINEL DE CONTROLE DE ROLLOUT & JOGO RESPONSÁVEL (.local)")
    print("=" * 70)

    if not ROLLOUT_FILE.exists():
        print(f"❌ Arquivo não encontrado: {ROLLOUT_FILE}")
        return

    with open(ROLLOUT_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    ativos = data.get("rollout_ativo", [])
    print(f"📌 Ciclos Ativos Concorrendo na Caixa: {len(ativos)}\n")

    for ciclo in ativos:
        cid = ciclo.get("id")
        mod = ciclo.get("modalidade")
        tipo = ciclo.get("tipo")
        ini = ciclo.get("concurso_inicial")
        fim = ciclo.get("concurso_final")
        jogos = ciclo.get("jogos", [])

        print(f"🔹 [{mod.upper()}] {cid}")
        print(f"   Tipo: {tipo} | Concursos: {ini} a {fim} | Total de Jogos: {len(jogos)}")

        # Busca dados atualizados da loteria
        try:
            adapter = get_adapter(mod)
            df = adapter.fetch()
            last_draw = df.iloc[-1]
            last_id = int(last_draw["draw_id"])
            last_date = str(last_draw["date"])[:10]
            print(f"   📡 Caixa Status: Último sorteio apurado: {last_id} ({last_date})")

            # Verifica concursos pendentes
            pendentes = [c for c in range(max(ini, last_id + 1), fim + 1)]
            if pendentes:
                print(f"   ⏳ Concursos Restantes a Disputar: {pendentes} (Próximo: {pendentes[0]})")
            else:
                print("   🏁 Ciclo concluído!")

        except Exception as e:
            print(f"   ⚠️ Não foi possível sincronizar com a Caixa: {e}")

        for j in jogos:
            jid = j.get("id_jogo")
            nums = j.get("dezenas")
            ref = f" ({j.get('ref_favorita')})" if j.get('ref_favorita') else ""
            print(f"      • {jid}: {nums}{ref}")

        print("-" * 70)

    # Favoritas
    if FAVORITAS_FILE.exists():
        with open(FAVORITAS_FILE, "r", encoding="utf-8") as f:
            favs = yaml.safe_load(f).get("favoritas", {})
        ms_count = len(favs.get("mega_sena", []))
        lf_count = len(favs.get("lotofacil", []))
        print(f"\n⭐ Apostas Favoritas Catalogadas: Mega-Sena ({ms_count}) | Lotofácil ({lf_count})")
        print("   (Para ver detalhes das favoritas, consulte history.local/favoritas.local.yaml)")

    print("=" * 70)

if __name__ == "__main__":
    main()
