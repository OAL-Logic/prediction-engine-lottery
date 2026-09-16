---
type: report
subtype: relatorio-final
game: "Lotofácil"
lottery: "br/lotofacil"
concurso: 3780
date: 2026-09-15
tags: [prediction-engine, relatorio, lottery/analysis, chi-squared]
---

# Relatório Final — Concurso 3780 (Lotofácil)

## 0. Nota de transparência

O pedido original referenciava uma tarefa em background com ID `boh8d1qsp` (leaderboard esoteric/statistical). Essa tarefa **não existe** — consultei o sistema de tarefas diretamente (`TaskOutput`, task_id `boh8d1qsp`) e o retorno foi `No task found`. Em vez de inventar números, executei os dois leaderboards agora, ao vivo, com dados reais. Nenhum valor neste relatório foi inferido ou estimado — todos vêm de saída real de comando, capturada nesta sessão.

---

## 1. Comandos executados (exatos, em ordem)

```bash
lottery leaderboard br/lotofacil --strategies esoteric
lottery leaderboard br/lotofacil --strategies statistical
lottery calibrate br/lotofacil --strategies esoteric --draws 15
lottery suggest br/lotofacil --strategy voting:moon_phase,solar,weather,weighted --filters sum_range,parity --esoteric-mode --count 2
```

Nota: a primeira tentativa do `suggest` usou `--strategy moon_phase,solar,weather,weighted` (sem o prefixo `voting:`), que no engine não produz um ensemble único — produz 4 previsões separadas (uma por estratégia) mais um painel de consenso por votos. Como o pedido era por **duas tickets finais** (um resultado só), corrigi para a sintaxe de ensemble real (`voting:s1,s2,...`, documentada no próprio `--help` do `suggest`) e re-executei. O resultado abaixo é da segunda execução (a correta).

---

## 2. Leaderboard — grupo `esoteric` (br/lotofacil)

| Rank | Estratégia | Stability% | Δ real/rand | Composite | Avaliação |
|---|---|---|---|---|---|
| 🥇 | numerology | 25% | +0.0680 | 0.626 | DISCRIMINADOR |
| 🥈 | noosphere | 100% | +0.0000 | 0.500 | DISCRIMINADOR |
| 🥉 | sefirot | 100% | +0.0000 | 0.500 | DISCRIMINADOR |
| 4 | ley_lines | 99% | +0.0000 | 0.495 | RUÍDO |
| 5 | kabbalistic | 25% | +0.0153 | 0.279 | RUÍDO |
| 6 | moon_phase | 25% | -0.0020 | 0.126 | RUÍDO |
| 7 | solar | 25% | -0.2969 | 0.126 | INVERTIDO |
| 8 | fibonacci | 25% | -0.0256 | 0.126 | INVERTIDO |

Melhor: `numerology` (composite=0.626). 3 estratégias cruzam o limiar de 0.50 (discriminadores genuínos, pela metodologia de estabilidade do engine): `numerology`, `noosphere`, `sefirot`.

## 3. Leaderboard — grupo `statistical` (br/lotofacil)

| Rank | Estratégia | Stability% | Δ real/rand | Composite | Avaliação |
|---|---|---|---|---|---|
| 🥇 | momentum | 25% | +0.0983 | 0.626 | DISCRIMINADOR |
| 🥈 | streak | 25% | +0.0941 | 0.626 | DISCRIMINADOR |
| 🥉 | void | 25% | +0.0387 | 0.512 | DISCRIMINADOR |
| 4 | crowd_avoidance | 100% | +0.0000 | 0.500 | DISCRIMINADOR |
| 5 | markov | 25% | -0.1120 | 0.126 | INVERTIDO |
| 6 | bayesian | 25% | -0.2407 | 0.126 | INVERTIDO |
| 7 | weighted | 25% | -0.0800 | 0.126 | INVERTIDO |
| 8 | monte_carlo | 25% | -0.0387 | 0.126 | INVERTIDO |
| 9 | pattern | 25% | -0.0597 | 0.126 | INVERTIDO |
| 10 | spectral | 25% | -0.0731 | 0.126 | INVERTIDO |

Puladas por histórico insuficiente: `cycle`, `harmonic`, `stability`, `fisher`. Melhor: `momentum` (composite=0.626). 4 cruzam o limiar: `momentum`, `streak`, `void`, `crowd_avoidance`.

**Observação honesta:** `weighted` — a estratégia estatística usada no ensemble final (seção 5) — apareceu como **INVERTIDO** (composite=0.126) nesta metodologia específica de estabilidade/injeção de ruído. Isso não é o mesmo teste que o qui-quadrado da seção 6; é uma medida de robustez sob perturbação, calculada sobre uma janela pequena (`window=50`, `trials=3`). Não escondo esse resultado: ele reforça a mesma conclusão geral do relatório — nenhuma estratégia aqui demonstrou vantagem preditiva robusta e estável.

---

## 4. Calibração empírica — `esoteric`, 15 sorteios (`--draws 15`)

| Rank | Estratégia | Média acertos | Lift | Lift% | Lucro líq. | ROI% | Precisão | N |
|---|---|---|---|---|---|---|---|---|
| 1 | planetary_transits | 9.267 | 1.030 | +3.0% | R$ -39,00 | 13.3% | 0.13 | 15 |
| 2 | numerology | 9.133 | 1.015 | +1.5% | R$ -21,00 | 53.3% | 0.53 | 15 |
| 3 | moon_phase | 9.067 | 1.007 | +0.7% | R$ -39,00 | 13.3% | 0.13 | 15 |
| 4 | noosphere | 9.067 | 1.007 | +0.7% | R$ -39,00 | 13.3% | 0.13 | 15 |
| 5 | kabbalistic | 8.933 | 0.993 | -0.7% | R$ -45,00 | 0.0% | 0.00 | 15 |
| 6 | fibonacci | 8.867 | 0.985 | -1.5% | R$ -45,00 | 0.0% | 0.00 | 15 |
| 7 | solar | 8.800 | 0.978 | -2.2% | R$ -33,00 | 26.7% | 0.27 | 15 |

Baseline aleatório: **9.000** acertos esperados/sorteio (escolher 15 de 25). Todos os lifts ficam entre 0.978 e 1.030 — ou seja, **dentro de ±3% do acaso puro**, com apenas 15 sorteios de amostra (estatisticamente pequeno demais para significância; o próprio engine avisa isso no rodapé do comando). Nenhuma estratégia esotérica teve lucro líquido positivo nesta janela.

---

## 5. Tickets finais geradas — Concurso 3780

Comando: `lottery suggest br/lotofacil --strategy voting:moon_phase,solar,weather,weighted --filters sum_range,parity --esoteric-mode --count 2`

**Semente ambiental (`--weather-seed`, implícita por `--esoteric-mode`):**
Data 2026-09-15 · Coords (-23.5505, -46.6333) · Temp 15.4°C · Precip 9.6mm · Kp solar 3.0 · Fase lunar 13% · Maré 47% → **seed determinística: 423038994** (reprodutível; não é sinal de probabilidade de vitória).

### 🎟️ Ticket 1
**1, 2, 4, 5, 6, 9, 10, 11, 15, 20, 21, 22, 23, 24, 25** (soma=198)
Acertos históricos: 11 pontos → 351 vezes · 12 pontos → 68 vezes · 13 pontos → 6 vezes

### 🎟️ Ticket 2
**1, 2, 4, 5, 6, 7, 9, 10, 13, 14, 18, 21, 22, 24, 25** (soma=181)
Acertos históricos: 11 pontos → 340 vezes · 12 pontos → 67 vezes · 13 pontos → 7 vezes

Contexto de correlação no momento da geração: Fase lunar Waxing Crescent (13.2% do ciclo), maré normal; clima solar "unsettled" (Kp 3.3); Noosphere Jitter "Coherent" (score 0.424). Filtros estruturais aplicados: `sum_range` (soma dentro da faixa dinâmica de tolerância) e `parity` (balanço par/ímpar) — ambas as somas (198 e 181) ficam próximas da média teórica de 195 para uma escolha de 15 números em pool 1–25.

---

## 6. Justificativa honesta — teste qui-quadrado (χ²)

```
Bucket lunar de hoje: Q1 (0–20%) (Waxing Crescent)   Bucket solar: unsettled (Kp 3–5)
Sorteios históricos combinados neste bucket: 742
χ² = 9.69   p = 0.9957   → não significativo — consistente com sorteios aleatórios
```

**O que este teste faz, exatamente:** compara a distribuição de frequência dos números sorteados historicamente nos 742 sorteios que caíram no mesmo "bucket" lunar/solar de hoje contra a distribuição de frequência geral de todo o histórico, via teste qui-quadrado de aderência (`scipy.stats.chisquare`).

**Resultado:** p=0.9957 está extremamente longe do limiar convencional de significância (p<0.05) — na verdade, é quase o valor máximo possível (p→1 significa "a distribuição observada é praticamente idêntica à esperada por acaso"). χ²=9.69 com esse p confirma: **não há evidência estatística de que o bucket lunar/solar de hoje influencie quais números saem.**

Isso é **consistente com o que se espera de um sorteio idôneo**: cada sorteio da Lotofácil é um evento aleatório independente, sem memória do sorteio anterior nem de condições ambientais externas (fase da lua, clima, atividade solar). Os resultados das seções 3 e 4 reforçam a mesma conclusão por ângulos diferentes — nenhuma estratégia (esotérica ou estatística) demonstrou vantagem preditiva robusta acima do acaso quando testada com rigor (janela pequena, custo de reprodução honesto, "Chi² gate" do próprio engine). As duas tickets da seção 5 são geradas por um ensemble de sinais reais (lua, sol, clima, frequência histórica) e passam por filtros estruturais válidos — mas isso **não muda a probabilidade matemática de acerto**, que permanece a mesma de qualquer combinação válida de 15 números em 25. O propósito do engine, documentado no próprio README ("Chi² gate", "Honest defaults"), é justamente ser transparente sobre isso em vez de vender uma falsa promessa.

---

## 7. Diff de código desta sessão

Resumo (`git diff --stat` entre a tag de segurança `backup/from-pre-merge-2026-09-15` e o HEAD atual):

```
51 files changed, 3385 insertions(+), 56 deletions(-)
```

25 commits novos nesta sessão: 24 `feat:` (uma nova capacidade cada, commitada individualmente) + 1 `fix:` (bug de reprodutibilidade do `--weather-seed` — as buscas de clima/sismo/Kp solar não tinham cache, então duas chamadas no mesmo dia podiam pegar leituras diferentes da API ao vivo e gerar seeds diferentes; corrigido com cache de 24h por (lat, lon, data)) + 1 `chore:` (bump de versão 11.2.0 → 11.3.0 e entrada no CHANGELOG.md).

Principais arquivos novos: 22 novos comandos CLI em `engine/cli/commands/*.py` (`record`, `pattern-search`, `filter-funnel`, `filter-assistant`, `profile`, `calibrate`-adjacent `seed-audit`, etc.), 3 widgets desktop novos em `desktop/src/widgets/*.py`, e um arquivo de teste correspondente para cada um em `tests/*.py` (todos passando, isolados de `data/lottery.db` real via paths temporários/monkeypatch). `engine/cli/main.py` ganhou ~226 linhas de wiring dos novos comandos.

Lista completa de commits: `git log --oneline backup/from-pre-merge-2026-09-15..HEAD`.

---

## 8. Roadmap de paridade de features com o SamLotto

Baseado em `detailed_features.md` (catálogo técnico do SamLotto reverse-engineered), **não** no dump de disassembly (`BinaryNinja_SamLotto_linear.txt`), conforme solicitado.

| Seção do catálogo SamLotto | Status antes desta sessão | Status agora |
|---|---|---|
| 1. Banco de dados (MDB: `lottery`, `drawings`, `filters`, `perdiction`, `nsSearch`, `nsStat`) | Equivalente via DuckDB + JSON particionado, já existia | Sem mudança arquitetural — `nsSearch` ganhou equivalente funcional (linha abaixo) |
| 2. Motor de análise estatística (frequência, hot/cold, intervalo, soma, par/ímpar, consecutivos, primos) | Já coberto (`number-heat`, `streak-report`, `gap-forecast`, `analyze`) | + `number-lifecycle` (dossiê histórico por número) e `batch-grade` (screening estrutural em lote) |
| 3. Sistema de filtros (base, avançado Adv1/2/3, **Assistant Filter**, **Pattern Matching**, grupos, **Elimination Tracking**) | Existiam 100+ filtros vetorizados (`engine/modules/filters/`) **mas nenhum comando CLI os usava** | **Maior lacuna fechada nesta sessão**: `filter-funnel` (Elimination Tracking real), `filter-assistant` (wizard guiado = Assistant Filter), `pattern-search` (= nsSearch/Pattern Matching) |
| 4. Geração de números (aleatório, filtrado, wheeling, execuções salvas) | Já coberto (`wheel`, `genetic-wheel`, `suggest --filters`) | + `random-baseline` formaliza o controle aleatório puro como referência honesta |
| 5. UI/UX (grids de dados, **PopupCalculator**, **DrawingsUpdate**, CheckWinning) | Grid de dados e CheckWinning (aba `verification.py`) já existiam | + Quick Calculator (PopupCalculator) e Pattern Search dialog no desktop. `record` (= DrawingsUpdate) só tem versão CLI — **ainda falta o formulário desktop** |
| 6. Conectividade & licenciamento (senha do MDB, chave de registro) | Fora de escopo | Continua fora de escopo — seria replicar o mecanismo de proteção de outro produto, não uma funcionalidade de análise; não faz sentido para uma ferramenta própria e independente |

**Próximo passo sugerido, se o objetivo é fechar 100% do catálogo:** um diálogo desktop para `record` (formulário `DrawingsUpdate`), e um drill-down de detalhes para `pattern-search` no desktop (`nsSearchDetails`). Fora isso, a paridade funcional com o catálogo do SamLotto está, na prática, coberta.
