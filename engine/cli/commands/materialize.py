"""
Interactive & Immersive Materialization Session (`p4lottery materialize`)
=========================================================================
Provides a multi-sensory, game-agnostic & celestial-aware materialization
and visualization session (Terminal + HTML5/WebAudio Chamber) to anchor
intention, cardiac coherence, and synchronicity after bets are placed.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from datetime import date as _date
from engine.modules.esoteric_pipeline import build_environmental_seed

console = Console()

SEPHIROT_ARCHETYPES: dict[int, str] = {
    1: "Kether (Coroa / Origem Primordial)",
    2: "Chokmah (Sabedoria Criativa)",
    3: "Binah (Compreensão & Forma)",
    4: "Chesed (Abundância & Misericórdia)",
    5: "Geburah (Força & Poder de Decisão)",
    6: "Tiphereth (Beleza, Sol & Harmonia Central)",
    7: "Netzach (Vitória & Persistência)",
    8: "Hod (Esplendor & Ressonância Mercurial)",
    9: "Yesod (Fundamento Lunar & Subconsciente)",
    10: "Malkuth (Manifestação Física no Reino)",
    11: "Da'ath (Conhecimento Oculto & Portal de Sincronicidade)",
    12: "Ordem Zodiacal (12 Constelações)",
    13: "Echad / Ahavah (Unidade & Transformação)",
    14: "Temperança & Equilíbrio Alquímico",
    15: "Harmonia Orbital (Líder 72.1% Períodos Gêmeos)",
    16: "Despertar & Rompimento de Limites",
    17: "A Estrela (Esperança, Fé & Visão Futura)",
    18: "Chai (Vida Plena & Magnetismo Lunar)",
    20: "O Julgamento (Renascimento & Chamado)",
    24: "Harmonia Duodecimal Dupla (Júpiter)",
    25: "Plenitude Quântica 5×5 (Líder Z=+3.06 Lua Cheia)",
    27: "Cubo Sagrado 3³ (Trânsito Planetário 1.000)",
    28: "Ciclo Lunar Completo (28 Mansões da Lua)",
    32: "32 Caminhos da Sabedoria (Sepher Yetzirah)",
    33: "Mestre da Elevação & Coocorrência (33,49)",
    34: "Constante Mágica do Quadrado de Júpiter (4×4)",
    38: "Ressonância de Quinta-feira (Z=+1.65)",
    44: "Construtor Material (Líder Períodos Gêmeos 18.6%)",
    49: "Setenário Pleno 7×7 (Par Gêmeo 33-49)",
    53: "Primo de Alta Frequência & Maré Gravitacional",
}


def generate_html_materialization_chamber(
    pacote: list[dict[str, Any]],
    ephemeris: dict[str, Any],
    seed_int: int,
    out_path: str | Path = ".scratch/materializacao_camara.html",
) -> Path:
    """Generate an interactive HTML5 + WebAudio (432Hz/528Hz + Drumroll) Materialization Chamber."""
    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    pacote_json = json.dumps(pacote, ensure_ascii=False)
    eph_json = json.dumps(ephemeris, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>🥁 Câmara Imersiva de Materialização — P4Lottery Omni</title>
<style>
  :root {{
    --bg: #070913;
    --gold: #f5c542;
    --cyan: #38ef7d;
    --violet: #9d50bb;
  }}
  body {{
    margin: 0; padding: 24px;
    background: radial-gradient(circle at center, #141936 0%, #070913 100%);
    color: #eef2ff; font-family: 'Segoe UI', system-ui, sans-serif;
    text-align: center; min-height: 100vh;
  }}
  h1 {{ color: var(--gold); margin-bottom: 6px; letter-spacing: 1px; }}
  .subtitle {{ color: #a5b4fc; font-size: 0.95rem; margin-bottom: 20px; }}
  .mandala-wrap {{
    display: flex; flex-direction: column; align-items: center; margin: 18px auto;
  }}
  .breath-circle {{
    width: 150px; height: 150px; border-radius: 50%;
    background: radial-gradient(circle, rgba(245,197,66,0.45), rgba(56,239,125,0.12));
    border: 2px solid var(--gold);
    display: flex; align-items: center; justify-content: center;
    font-weight: bold; font-size: 1.05rem; color: #fff;
    box-shadow: 0 0 35px rgba(245,197,66,0.35);
    transition: transform 4s ease-in-out, box-shadow 4s ease-in-out;
  }}
  .controls {{ margin: 18px 0; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
  button {{
    background: linear-gradient(135deg, #f5c542, #e09f1f);
    color: #0b0e17; border: none; padding: 12px 22px; border-radius: 999px;
    font-weight: 700; cursor: pointer; font-size: 0.95rem;
    box-shadow: 0 4px 16px rgba(245,197,66,0.3);
  }}
  button:hover {{ transform: translateY(-2px); }}
  .cards {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
    gap: 18px; max-width: 1100px; margin: 20px auto; text-align: left;
  }}
  .card {{
    background: rgba(255,255,255,0.05); border: 1px solid rgba(245,197,66,0.3);
    border-radius: 14px; padding: 16px; backdrop-filter: blur(8px);
  }}
  .ticket-row {{
    padding: 8px 10px; margin: 6px 0; border-radius: 8px;
    background: rgba(0,0,0,0.35); display: flex; justify-content: space-between;
    align-items: center; cursor: pointer; border: 1px solid transparent;
  }}
  .ticket-row.sealed {{
    border-color: var(--cyan); background: rgba(56,239,125,0.14);
  }}
  .ball {{
    display: inline-block; width: 26px; height: 26px; line-height: 26px;
    border-radius: 50%; background: #1e293b; color: var(--gold);
    text-align: center; font-weight: 700; font-size: 0.82rem; margin: 1px;
    border: 1px solid rgba(245,197,66,0.45);
  }}
  .mantra-box {{
    max-width: 780px; margin: 22px auto; padding: 18px;
    border-radius: 12px; border: 1px solid rgba(56,239,125,0.4);
    background: rgba(16, 185, 129, 0.08); font-style: italic;
  }}
</style>
</head>
<body>
  <h1>🥁 QUE RUFEM OS TAMBORES — CÂMARA DE MATERIALIZAÇÃO</h1>
  <div class="subtitle" id="eph-banner"></div>

  <div class="mandala-wrap">
    <div class="breath-circle" id="breathCircle">INSPIRAR (4s)</div>
  </div>

  <div class="controls">
    <button onclick="playDrumrollAndHarmonics()">🥁 Rufar Tambores + Ressonância 432Hz/528Hz</button>
    <button onclick="sealAllTickets()">✨ Consagrar & Selar Todos os 17 Jogos</button>
  </div>

  <div class="mantra-box" id="mantraBox">
    "Minha mente está serena, grata e alinhada com os ciclos da Terra, do Sol e da Lua Cheia.
    A probabilidade encontra o propósito; a abundância flui com sabedoria e paz."
  </div>

  <div class="cards" id="cardsContainer"></div>

<script>
const PACOTE = {pacote_json};
const EPH = {eph_json};
const SEED = {seed_int};

document.getElementById('eph-banner').innerText =
  `Data/Hora: ${{EPH.target_date}} ${{EPH.target_time}} BRT  |  Lua: ${{EPH.lunar_phase_name}} (${{Math.round(EPH.lunar_phase_ratio*100)}}%)  |  Sol: ${{EPH.sun_longitude_deg}}° (${{EPH.sun_zodiac_sign}})  |  Terra: ${{EPH.earth_heliocentric_lon_deg}}° (${{EPH.earth_orbital_speed_kms}} km/s)  |  Seed SHA-256: ${{SEED}}`;

const container = document.getElementById('cardsContainer');
PACOTE.forEach(mod => {{
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `<h3 style="color:#f5c542;margin-top:0">🍀 ${{mod.modalidade.toUpperCase()}} (${{mod.jogos.length}} Jogos)</h3>`;
  mod.jogos.forEach((jogo, idx) => {{
    const row = document.createElement('div');
    row.className = 'ticket-row';
    const balls = jogo.map(n => `<span class="ball">${{String(n).padStart(2,'0')}}</span>`).join('');
    row.innerHTML = `<span><b>#${{String(idx+1).padStart(2,'0')}}</b> ${{balls}}</span><span class="status">🕯️ Toque p/ selar</span>`;
    row.onclick = () => {{
      row.classList.toggle('sealed');
      row.querySelector('.status').innerText = row.classList.contains('sealed') ? '✨ SELADO' : '🕯️ Toque p/ selar';
      playChime(528 + idx * 12);
    }};
    card.appendChild(row);
  }});
  container.appendChild(card);
}});

// Ciclo respiratório 4-4-6
const circle = document.getElementById('breathCircle');
function breathLoop() {{
  circle.innerText = 'INSPIRAR (4s)';
  circle.style.transform = 'scale(1.32)';
  setTimeout(() => {{
    circle.innerText = 'SUSTENTAR (4s)';
    setTimeout(() => {{
      circle.innerText = 'EXPIRAR (6s)';
      circle.style.transform = 'scale(0.92)';
    }}, 4000);
  }}, 4000);
}}
breathLoop();
setInterval(breathLoop, 14000);

let audioCtx = null;
function getAudio() {{
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  return audioCtx;
}}

function playChime(freq) {{
  try {{
    const ctx = getAudio();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
    osc.connect(gain); gain.connect(ctx.destination);
    osc.start(); osc.stop(ctx.currentTime + 1.2);
  }} catch(e) {{}}
}}

function playDrumrollAndHarmonics() {{
  try {{
    const ctx = getAudio();
    // Rufar de tambores sintetizado (2.2s)
    for (let i = 0; i < 28; i++) {{
      setTimeout(() => playChime(110 + (i % 3) * 15), i * 70);
    }}
    setTimeout(() => {{
      playChime(432);
      playChime(528);
    }}, 2000);
  }} catch(e) {{}}
}}

function sealAllTickets() {{
  playDrumrollAndHarmonics();
  document.querySelectorAll('.ticket-row').forEach((row, idx) => {{
    setTimeout(() => {{
      row.classList.add('sealed');
      row.querySelector('.status').innerText = '✨ SELADO';
    }}, idx * 110);
  }});
}}
</script>
</body>
</html>
"""
    dest.write_text(html, encoding="utf-8")
    return dest


def run_materialize(
    target_date: str = "",
    target_time: str = "20:00",
    lat: float = -23.5505,
    lon: float = -46.6333,
    budget: float = 80.0,
    interactive: bool = False,
    export_html: str = ".scratch/materializacao_camara.html",
) -> Path:
    """Execute the interactive terminal drumroll & materialization session and generate the HTML5 chamber."""
    from scripts.playwright_caixa_universal import (
        PACOTE_ENXUTO_4,
        PACOTE_ORCAMENTO_80,
        PACOTE_VARIACOES_CIRURGICO,
        aplicar_teto_orcamento,
    )

    import math
    if not target_date:
        target_date = _date.today().isoformat()
    seed_int, ctx = build_environmental_seed(
        coords=(lat, lon),
        target_date=_date.fromisoformat(target_date[:10]),
        target_time=target_time,
        wind_kmh=28.5,
        pressure_hpa=1009.4,
    )
    eph = dict(ctx.get("celestial_ephemeris", {}))
    l_ratio = float(ctx.get("environmental", {}).get("lunar_phase", 0.622))
    zodiac_signs = [
        "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
        "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes",
    ]
    sun_lon = float(eph.get("sun_longitude_deg", 216.5429))
    earth_lon = float(eph.get("earth_heliocentric_lon_deg", 36.5429))
    eph["lunar_phase_name"] = eph.get("lunar_phase_name", "Full Moon")
    eph["sun_longitude_deg"] = sun_lon
    eph["earth_heliocentric_lon_deg"] = earth_lon
    eph["target_date"] = target_date
    eph["target_time"] = target_time
    eph["lunar_phase_ratio"] = l_ratio
    eph["lunar_illumination"] = (1.0 - math.cos(2.0 * math.pi * l_ratio)) / 2.0
    eph["sun_zodiac_sign"] = zodiac_signs[int(sun_lon // 30) % 12]
    eph["earth_zodiac_sign"] = zodiac_signs[int(earth_lon // 30) % 12]
    eph["earth_orbital_speed_kms"] = eph.get("earth_orbital_velocity_kms", 29.9947)

    if budget <= 40.0:
        base_pacote = PACOTE_ENXUTO_4
    elif budget <= 55.0:
        base_pacote = PACOTE_VARIACOES_CIRURGICO
    else:
        base_pacote = PACOTE_ORCAMENTO_80

    pacote = aplicar_teto_orcamento(base_pacote, budget)
    custos_unit = {"mega-sena": 6.0, "lotofacil": 3.5}
    total_bilhetes = sum(len(it["jogos"]) for it in pacote)
    custo_selado = sum(len(it["jogos"]) * custos_unit.get(it["modalidade"], 0.0) for it in pacote)
    html_path = generate_html_materialization_chamber(pacote, eph, seed_int, out_path=export_html)

    console.print()
    console.print(Panel.fit(
        "[bold yellow]🥁 QUE RUFEM OS TAMBORES — SESSÃO IMERSIVA DE MATERIALIZAÇÃO & ESPIRITUALIDADE[/bold yellow]\n"
        f"[cyan]Data/Hora Alvo:[/cyan] {target_date} {target_time} BRT   |   "
        f"[cyan]Lua:[/cyan] {eph['lunar_phase_name']} ({eph['lunar_phase_ratio']:.1%}, Ilum {eph['lunar_illumination']:.1%})\n"
        f"[cyan]Sol:[/cyan] {eph['sun_longitude_deg']}° ({eph['sun_zodiac_sign']})   |   "
        f"[cyan]Terra:[/cyan] {eph['earth_heliocentric_lon_deg']}° ({eph['earth_zodiac_sign']}, {eph['earth_orbital_speed_kms']} km/s)\n"
        f"[dim]Semente Ambiental SHA-256: {seed_int}   |   Orçamento Selado: R$ {custo_selado:.2f} / R$ {budget:.2f} ({total_bilhetes} Bilhetes)[/dim]",
        border_style="yellow",
    ))

    # 1. Animated Drumroll & Cardiac Coherence Pacer
    with Progress(
        SpinnerColumn("dots12", style="bold yellow"),
        TextColumn("[bold yellow]{task.description}[/bold yellow]"),
        BarColumn(bar_width=38, complete_style="green", finished_style="bold green"),
        console=console,
        transient=False,
    ) as progress:
        t1 = progress.add_task("🥁 Rufando os tambores & sincronizando efemérides...", total=100)
        for _ in range(10):
            time.sleep(0.05 if not interactive else 0.12)
            progress.update(t1, advance=10)

        t2 = progress.add_task("🫁 Coerência Cardíaca (Inspirar 4s • Sustentar 4s • Expirar 6s)...", total=100)
        for _ in range(10):
            time.sleep(0.05 if not interactive else 0.15)
            progress.update(t2, advance=10)

    # 2. Mandala & Sephirot Archetypes Table
    stab = Table(
        title="✨ Arquétipos Espirituais & Cabalísticos (Sephirot) das Dezenas-Núcleo",
        header_style="bold magenta",
        box=None,
        padding=(0, 2),
    )
    stab.add_column("Dezena", justify="right", style="bold yellow")
    stab.add_column("Correspondência Espiritual / Geometria Sagrada", style="cyan")
    stab.add_column("Evidência Histórica (Lua / Órbita)", style="green")

    core_highlights = [
        (5, "Acoplamento Ferromagnético de Ising (Domínio de Spin)"),
        (10, "Convergência Multicritério (Lunar + Orbital + Magnética)"),
        (11, "Ressonância de Ciclo Temporal & Atrasão"),
        (13, "Convergência de Fase Lunar & Acoplamento Ising"),
        (15, "Tunelamento Quântico Ψ & Harmonia de Períodos Gêmeos"),
        (25, "Campo Magnético de Ising & Ressonância de Sizígia"),
        (30, "Líder de Campo Local Ferromagnético (Ising H)"),
        (32, "Convergência Lunar, Magnética e Quântica"),
        (34, "Ruptura de Tensão de Atraso (Z_lag) & Tunelamento Quântico"),
        (44, "Ressonância de Períodos Astronômicos Gêmeos"),
    ]
    for num, evid in core_highlights:
        stab.add_row(f"{num:02d}", SEPHIROT_ARCHETYPES.get(num, "Harmonia Universal"), evid)
    console.print(stab)

    # 3. Interactive Intention Prompt (if interactive)
    intencao_usuario = "Prosperidade com sabedoria, paz familiar, equilíbrio e propósito elevado."
    if interactive:
        console.print("\n[bold cyan]💭 ANCORAGEM DE PENSAMENTO & INTENÇÃO:[/bold cyan]")
        console.print("Digite em uma frase sua intenção positiva para este objetivo (ou pressione ENTER para usar o decreto consagrado):")
        try:
            resp = input("✨ Sua Intenção > ").strip()
            if resp:
                intencao_usuario = resp
        except EOFError:
            pass

    # 4. Ticket-by-Ticket Consecration
    console.print(
        f"\n[bold yellow]🥁 CONSAGRAÇÃO DOS {total_bilhetes} JOGOS FEITOS "
        f"(ORÇAMENTO R$ {custo_selado:.2f} ≤ R$ {budget:.2f}):[/bold yellow]"
    )
    for item in pacote:
        mod = item["modalidade"].upper()
        console.print(f"\n[bold green]🍀 {mod} ({len(item['jogos'])} Bilhetes Selados):[/bold green]")
        for idx, j in enumerate(item["jogos"], start=1):
            fmt = " - ".join(f"{n:02d}" for n in j)
            console.print(f"   [bold white]✦ Jogo {idx:02d}:[/bold white] [bold yellow][{fmt}][/bold yellow]  [dim](soma={sum(j)} • selado ✓)[/dim]")

    console.print()
    console.print(Panel(
        f"[bold green]🕊️ DECRETO DE MATERIALIZAÇÃO SELADO:[/bold green]\n"
        f"[italic]\"{intencao_usuario}\"[/italic]\n\n"
        f"🌐 Câmara Imersiva HTML5 + Áudio 432Hz/528Hz gerada em: [bold cyan]{html_path}[/bold cyan]",
        title="✨ Objetivo Consagrado com Sucesso",
        border_style="green",
    ))
    return html_path
