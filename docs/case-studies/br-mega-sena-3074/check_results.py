#!/usr/bin/env python3
"""Conferidor Automático de Resultados & Validador de Prova Criptográfica.

Estudo de Caso: br/mega-sena (Concurso 3074).

Uso:
  python3 docs/case-studies/br-mega-sena-3074/check_results.py
Ou passando manualmente as dezenas sorteadas:
  python3 docs/case-studies/br-mega-sena-3074/check_results.py --numbers "4 10 17 48 53 56"
"""

import sys
import argparse
import hashlib
import json
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from engine.cli.utils import get_adapter
from engine.wheels import evaluate_prizes

CASE_DIR = Path(__file__).parent
COMMITMENT_FILE = CASE_DIR / "br-mega-sena-3074-commitment.yaml"
LOCAL_BETS_FILE = CASE_DIR / "br-mega-sena-3074-bets.local.yaml"

def main():
    parser = argparse.ArgumentParser(description="Verificador de Resultados — br/mega-sena Concurso 3074")
    parser.add_argument("--numbers", "-n", help="Dezenas sorteadas separadas por espaço (ex: '4 10 17 48 53 56')")
    parser.add_argument("--bets-file", "-b", help="Caminho para o arquivo YAML contendo os bilhetes reais (se omitido usa .local.yaml)")
    args = parser.parse_args()

    # 1. Carrega dados públicos de pré-compromisso
    if not COMMITMENT_FILE.exists():
        print(f"❌ Arquivo de compromisso não encontrado: {COMMITMENT_FILE}")
        return

    with open(COMMITMENT_FILE, "r", encoding="utf-8") as f:
        commitment = yaml.safe_load(f)

    expected_hash = commitment.get("cryptographic_proof", {}).get("tickets_sha256")
    lottery_id = commitment.get("lottery_id", "br/mega-sena")
    target_draw = commitment.get("draw_number", 3074)

    # 2. Localiza arquivo de apostas
    bets_path = Path(args.bets_file) if args.bets_file else LOCAL_BETS_FILE
    if not bets_path.exists():
        print("=" * 60)
        print(f"🔒 MODO PÚBLICO: Verificação de Hash de Pré-Compromisso ({lottery_id})")
        print("=" * 60)
        print(f"Concurso Alvo: {target_draw}")
        print(f"Hash SHA-256 Registrado: {expected_hash}")
        print(f"\n⚠️ O arquivo de apostas local ({bets_path.name}) não está presente neste clone/fork.")
        print("O autor manteve os bilhetes em sigilo pré-sorteio para evitar duplicidade de apostas.")
        print("Para auditar após o sorteio, forneça o arquivo revelado com --bets-file <arquivo.yaml>.")
        return

    with open(bets_path, "r", encoding="utf-8") as f:
        bets_data = yaml.safe_load(f)

    tickets = bets_data.get("tickets", [])
    pool = bets_data.get("pool", [])

    # 3. Validação Criptográfica de Autenticidade
    canonical_json = json.dumps(tickets, separators=(',', ':'))
    calculated_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    print("=" * 60)
    print("🔐 AUDITORIA CRIPTOGRÁFICA DE PRÉ-COMPROMISSO")
    print("=" * 60)
    print(f"Hash Esperado:   {expected_hash}")
    print(f"Hash Calculado:  {calculated_hash}")

    if calculated_hash.lower() == expected_hash.lower():
        print("✅ PROVA VÁLIDA: A matriz de 24 jogos confere exatamente com o registro pré-sorteio!")
    else:
        print("❌ FALHA DE INTEGRIDADE: Os bilhetes fornecidos não coincidem com o hash pré-compromissado.")
        return

    # 4. Obtenção do Resultado
    winning_numbers = None
    if args.numbers:
        winning_numbers = sorted([int(x) for x in args.numbers.replace(",", " ").split()])
    else:
        print(f"\n📡 Buscando resultado oficial do concurso {target_draw} via adaptador Caixa ({lottery_id})...")
        try:
            adapter = get_adapter(lottery_id)
            df = adapter.fetch()
            row = df[df["draw_id"] == target_draw]
            if not row.empty:
                winning_numbers = sorted(row.iloc[0]["numbers"])
                print(f"✓ Concurso {target_draw} encontrado no banco oficial!")
            else:
                print(f"⚠️ Concurso {target_draw} ainda não foi apurado pela Caixa.")
                print("Você pode passar as dezenas sorteadas manualmente com:")
                print("  python3 docs/case-studies/br-mega-sena-3074/check_results.py --numbers 'D1 D2 D3 D4 D5 D6'")
                return
        except Exception as e:
            print(f"Erro ao buscar da Caixa: {e}")
            return

    print("=" * 60)
    print(f"🎯 CONFERÊNCIA OFICIAL — {lottery_id.upper()} CONCURSO {target_draw}")
    print("=" * 60)
    print(f"Dezenas Sorteadas: {winning_numbers}")
    
    hits_in_pool = sorted(list(set(pool).intersection(set(winning_numbers))))
    print(f"Dezenas Acertadas no Pool ({len(hits_in_pool)}/{len(pool)}): {hits_in_pool}")
    print("-" * 60)

    prizes = evaluate_prizes(tickets, winning_numbers)

    print("\n📊 RESUMO DE PREMIAÇÕES DOS 24 JOGOS:")
    print(f"  🏆 Sena (6 acertos):   {prizes.get(6, 0)}")
    print(f"  🥈 Quina (5 acertos):  {prizes.get(5, 0)}")
    print(f"  🥉 Quadra (4 acertos): {prizes.get(4, 0)}")
    print(f"  🔹 Terno (3 acertos):  {prizes.get(3, 0)}")
    print(f"  🔹 Duque (2 acertos):  {prizes.get(2, 0)}")

    print("\n🔍 DETALHAMENTO BILHETE A BILHETE:")
    for idx, t in enumerate(tickets, 1):
        m = sorted(list(set(t).intersection(set(winning_numbers))))
        count = len(m)
        tag = ""
        if count == 6: tag = " ⭐ SENA!"
        elif count == 5: tag = " 🥈 QUINA!"
        elif count == 4: tag = " 🥉 QUADRA!"
        elif count == 3: tag = " (Terno)"
        print(f"  Bilhete {idx:02d}: {t} -> {count} acertos {m}{tag}")

    print("=" * 60)

if __name__ == "__main__":
    main()
