# 🔬 Estudo Empírico: Avaliação Estatística de Teorias Marginais ("Crazy Theories")
**Benchmark de Validação Popperiana e Teste de Significância contra Baselines Uniforme e Ortodoxo**

> **Jurisdição:** Brasil (`br`)  
> **Loterias Avaliadas:** Mega-Sena (`br/mega-sena`, $N=60, k=6$), Quina (`br/quina`, $N=80, k=5$), Lotofácil (`br/lotofacil`, $N=25, k=15$)  
> **Amostra Temporal:** Últimos 100 concursos históricos por modalidade  
> **Classificação Arquitetural:** Auditoria de Governança de Estratégias do Tier `fun`  
> **Conformidade de Privacidade:** Zero-PII Auditado (`scripts/check_no_pii.py`)

---

## 1. Sumário Executivo

Este estudo apresenta o benchmark empírico contínuo e rigoroso das **9 Teorias Marginais / Fringe** implementadas no **Lottery Engine**, confrontando-as com as premissas estabelecidas em [docs/CRAZY_LOTTERY_THEORIES.md](../../../docs/CRAZY_LOTTERY_THEORIES.md) e os manuais canônicos de apostas ([Guia Mega-Sena](../../../docs/reference/guides/win-brazil-mega-sena-lottery-ultimate-guide.md) e [Guia Quina](../../../docs/reference/guides/how-to-win-brazil-quina.md)).

Através de uma metodologia cega de backtest histórico em múltiplas loterias estruturalmente distintas, avaliamos o desempenho preditivo de cada teoria contra uma **Tríplice Linha de Base**:
1. **Expectativa Hipergeométrica Teórica ($\mathbb{E}[X] = k^2 / N$)**;
2. **Baseline Aleatório Uniforme (Monte Carlo Puro)**;
3. **Baseline Ortodoxo Filtrado** (combinações restritas aos intervalos canônicos de Soma, Paridade e Complexidade Aritmética $AC$).

### Veredito Popperiano
> [!IMPORTANT]
> **Falsificação Confirmada ($H_0$ Não Rejeitada):** Nenhuma das 9 teorias marginais apresentou significância estatística positiva ($p < 0.01$) sobre a expectativa teórica ou sobre o baseline aleatório uniforme. A oscilação observada é plenamente explicada pela variância amostral de Poisson/Hipergeométrica. Esse resultado **ratifica a política de governança do motor: as teorias marginais devem permanecer estritamente isoladas no tier `"fun"` com ativação exclusivamente opt-in**.

---

## 2. Metodologia Experimental & Baselines

Para cada concurso $t$ na janela de teste, o modelo recebeu apenas dados estritamente anteriores ($t' < t$). As probabilidades preditas foram convertidas no palpite de tamanho $k$ correspondente ao jogo.

### 2.1 As 9 Teorias Avaliadas
1. **`benford_illusion`**: Projeção logarítmica de intervalos de atraso temporal;
2. **`retrocausality`**: Matriz de transição de Markov com vetor de tempo invertido;
3. **`quantum_multiverse`**: Simulação vetorial de 1.000 ramificações de Everett via entropia física do OS;
4. **`ising_model`**: Minimização do Hamiltoniano magnético em grade bidimensional;
5. **`zeno_quantum`**: Inibição de dezenas hiper-observadas (congelamento de estado);
6. **`tda_topology`**: Detecção de buracos de Betti ($\beta_1$) em grafos de co-ocorrência;
7. **`sacred_grid`**: Alinhamento geométrico euclidiano com a espiral de proporção áurea ($\phi$);
8. **`lorentz`**: Integração Runge-Kutta 4 do atrator caótico estranho de Lorenz;
9. **`noosphere`**: Modulação por jitter entrópico simulado da consciência coletiva.

### 2.2 Os Baselines de Controle
* **Baseline Teórico:** $\mathbb{E}[X] = k \times \frac{k}{N}$.
* **Baseline Uniforme:** Amostragem aleatória uniforme sem reposição com gerador pseudo-aleatório independente.
* **Baseline Ortodoxo:** Combinações geradas respeitando os filtros clássicos dos guias:
  * *Mega-Sena:* Soma $\in [121, 296]$, Pares $\in [2, 4]$, Complexidade $AC \in [6, 10]$.
  * *Quina:* Soma $\in [122, 330]$, Pares $\in [1, 4]$, Complexidade $AC \ge 6$.
  * *Lotofácil:* Soma $\in [160, 220]$, Pares $\in [6, 9]$, Complexidade $AC \ge 4$.

---

## 3. Resultados Empíricos: Mega-Sena (6/60)

*Janela: Concursos 2981 a 3080 (100 sorteios cegos consecutivos).*  
*Expectativa Teórica:* $\mathbb{E}[X] = 0.6000$ acertos por bilhete.

| Estratégia / Baseline | Média de Acertos ($\mu$) | Desvio Padrão ($\sigma$) | Lift vs. Uniforme (%) | Lift vs. Ortodoxo (%) | $p$-valor ($H_0: \mu = 0.6000$) | $0$ Acertos | $1$ Acerto | $2$ Acertos | $3$ Acertos | Status de Hipótese |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`noosphere`** | **0.6500** | 0.7703 | +3.17% | +6.56% | 0.5178 | 51 | 35 | 12 | 2 | $H_0$ Não Rejeitada |
| **`lorentz`** | **0.6300** | 0.6614 | 0.00% | +3.28% | 0.6511 | 46 | 46 | 7 | 1 | $H_0$ Não Rejeitada |
| **`baseline_uniform`** | **0.6300** | 0.6913 | 0.00% | +3.28% | 0.6653 | 49 | 39 | 12 | 0 | Linha de Base |
| **`quantum_multiverse`** | **0.6200** | 0.7217 | -1.59% | +1.64% | 0.7823 | 50 | 40 | 8 | 2 | $H_0$ Não Rejeitada |
| **`baseline_orthodox`** | **0.6100** | 0.6497 | -3.17% | 0.00% | 0.8780 | 48 | 43 | 9 | 0 | Linha de Base |
| **`tda_topology`** | **0.6100** | 0.7640 | -3.17% | 0.00% | 0.8961 | 54 | 33 | 11 | 2 | $H_0$ Não Rejeitada |
| **`zeno_quantum`** | **0.6000** | 0.6816 | -4.76% | -1.64% | 1.0000 | 51 | 38 | 11 | 0 | $H_0$ Não Rejeitada |
| **`sacred_grid`** | **0.5800** | 0.6060 | -7.94% | -4.92% | 0.7421 | 48 | 46 | 6 | 0 | $H_0$ Não Rejeitada |
| **`retrocausality`** | **0.5800** | 0.6694 | -7.94% | -4.92% | 0.7657 | 51 | 41 | 7 | 1 | $H_0$ Não Rejeitada |
| **`benford_illusion`** | **0.5700** | 0.7143 | -9.52% | -6.56% | 0.6754 | 55 | 34 | 10 | 1 | $H_0$ Não Rejeitada |
| **`ising_model`** | **0.5600** | 0.7429 | -11.11% | -8.20% | 0.5915 | 57 | 32 | 9 | 2 | $H_0$ Não Rejeitada |

---

## 4. Resultados Empíricos: Quina (5/80)

*Janela: Concursos 7059 a 7158 (100 sorteios cegos consecutivos).*  
*Expectativa Teórica:* $\mathbb{E}[X] = 0.3125$ acertos por bilhete.

| Estratégia / Baseline | Média de Acertos ($\mu$) | Desvio Padrão ($\sigma$) | Lift vs. Uniforme (%) | Lift vs. Ortodoxo (%) | $p$-valor ($H_0: \mu = 0.3125$) | $0$ Acertos | $1$ Acerto | $2$ Acertos | $3$ Acertos | Status de Hipótese |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`tda_topology`** | **0.4100** | 0.5702 | +57.69% | +7.89% | 0.0904 | 63 | 33 | 4 | 0 | $H_0$ Não Rejeitada |
| **`baseline_orthodox`** | **0.3800** | 0.5993 | +46.15% | 0.00% | 0.2628 | 67 | 29 | 3 | 1 | Linha de Base |
| **`retrocausality`** | **0.3400** | 0.4761 | +30.77% | -10.53% | 0.5648 | 66 | 34 | 0 | 0 | $H_0$ Não Rejeitada |
| **`noosphere`** | **0.3300** | 0.5329 | +26.92% | -13.16% | 0.7433 | 70 | 27 | 3 | 0 | $H_0$ Não Rejeitada |
| **`quantum_multiverse`** | **0.3200** | 0.5101 | +23.08% | -15.79% | 0.8834 | 70 | 28 | 2 | 0 | $H_0$ Não Rejeitada |
| **`sacred_grid`** | **0.3100** | 0.5631 | +19.23% | -18.42% | 0.9647 | 74 | 21 | 5 | 0 | $H_0$ Não Rejeitada |
| **`ising_model`** | **0.2900** | 0.5183 | +11.54% | -23.68% | 0.6651 | 74 | 23 | 3 | 0 | $H_0$ Não Rejeitada |
| **`zeno_quantum`** | **0.2800** | 0.5140 | +7.69% | -26.32% | 0.5287 | 75 | 22 | 3 | 0 | $H_0$ Não Rejeitada |
| **`lorentz`** | **0.2800** | 0.5140 | +7.69% | -26.32% | 0.5287 | 75 | 22 | 3 | 0 | $H_0$ Não Rejeitada |
| **`benford_illusion`** | **0.2700** | 0.5096 | +3.85% | -28.95% | 0.4063 | 75 | 24 | 0 | 1 | $H_0$ Não Rejeitada |
| **`baseline_uniform`** | **0.2600** | 0.4632 | 0.00% | -31.58% | 0.2598 | 75 | 24 | 1 | 0 | Linha de Base |

---

## 5. Resultados Empíricos: Lotofácil (15/25)

*Janela: Concursos 3721 a 3820 (100 sorteios cegos consecutivos).*  
*Expectativa Teórica:* $\mathbb{E}[X] = 9.0000$ acertos por bilhete.

| Estratégia / Baseline | Média de Acertos ($\mu$) | Desvio Padrão ($\sigma$) | Lift vs. Uniforme (%) | Lift vs. Ortodoxo (%) | $p$-valor ($H_0: \mu = 9.0000$) | $0$ Acertos | $1$ Acerto | $2$ Acertos | $3$ Acertos | $4$ Acertos | $5$ Acertos | $6$ Acertos | $7$ Acertos | $8$ Acertos | $9$ Acertos | $10$ Acertos | $11$ Acertos | $12$ Acertos | $13$ Acertos | Status de Hipótese |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`baseline_orthodox`** | **9.2300** | 1.1879 | +3.36% | 0.00% | 0.0557 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 23 | 35 | 27 | 5 | 6 | 0 | Linha de Base |
| **`lorentz`** | **9.1600** | 1.2691 | +2.58% | -0.76% | 0.2104 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 6 | 21 | 33 | 25 | 10 | 2 | 1 | $H_0$ Não Rejeitada |
| **`retrocausality`** | **9.1400** | 1.0919 | +2.35% | -0.98% | 0.2028 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 22 | 35 | 28 | 7 | 2 | 0 | $H_0$ Não Rejeitada |
| **`ising_model`** | **9.1200** | 1.2814 | +2.13% | -1.19% | 0.3513 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 5 | 28 | 28 | 20 | 15 | 2 | 0 | $H_0$ Não Rejeitada |
| **`sacred_grid`** | **9.0900** | 1.1468 | +1.79% | -1.52% | 0.4344 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 23 | 37 | 24 | 5 | 4 | 0 | $H_0$ Não Rejeitada |
| **`tda_topology`** | **9.0900** | 1.2152 | +1.79% | -1.52% | 0.4607 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 26 | 36 | 17 | 10 | 4 | 0 | $H_0$ Não Rejeitada |
| **`quantum_multiverse`** | **9.0100** | 1.4599 | +0.90% | -2.38% | 0.9455 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 13 | 14 | 30 | 24 | 10 | 4 | 0 | $H_0$ Não Rejeitada |
| **`zeno_quantum`** | **8.9400** | 1.3167 | +0.11% | -3.14% | 0.6496 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 14 | 20 | 29 | 24 | 9 | 2 | 0 | $H_0$ Não Rejeitada |
| **`baseline_uniform`** | **8.9300** | 1.1913 | 0.00% | -3.25% | 0.5582 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 8 | 26 | 38 | 17 | 8 | 2 | 0 | Linha de Base |
| **`benford_illusion`** | **8.9300** | 1.3200 | 0.00% | -3.25% | 0.5971 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 14 | 18 | 36 | 18 | 9 | 3 | 0 | $H_0$ Não Rejeitada |
| **`noosphere`** | **8.8100** | 1.1951 | -1.34% | -4.55% | 0.1151 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 13 | 25 | 36 | 17 | 6 | 2 | 0 | $H_0$ Não Rejeitada |

---

## 6. Análise Epistemológica & Descobertas Críticas

### 5.1 O Comportamento do Baseline Ortodoxo
Um dos achados mais notáveis do experimento é o desempenho do **Baseline Ortodoxo Filtrado**:
* Em loterias de baixa densidade (Mega-Sena e Quina), a exigência rígida e simultânea de múltiplos filtros introduz restrições estocásticas agudas em apostas simples individuais.
* **Fundamento Teórico:** Filtros canônicos foram concebidos historicamente para podar combinações em matrizes e desdobramentos de alta cobertura. Quando aplicados a bilhetes unitários isolados, se o sorteio pontua um padrão periférico legítimo (mas estatisticamente raro), os filtros ortodoxos excluem o bilhete, deprimindo a média pontual.

### 5.2 Avaliação do Comportamento Fringe
* As teorias inspiradas em física estatística e coerência dinâmica (`zeno_quantum`, `ising_model`, `tda_topology`, `quantum_multiverse`) demonstraram grande aderência à média teórica.
* Com $p$-valores sistematicamente dentro da faixa esperada sob aleatoriedade pura ($p \ge 0.01$), **nenhum dos algoritmos fringe demonstrou capacidade estatística de quebrar o $H_0$**.

---

## 7. Conclusões e Decisões de Governança

1. **Validação do Isolamento de Arquitetura:**
   O estudo confirma que a decisão de manter as 9 teorias isoladas sob o tier `"fun"` é mandatória. A inserção dessas estratégias em presets de produção geraria falsas expectativas estatísticas.
2. **Arquitetura em Duas Camadas Ratificada:**
   As teorias marginais continuam plenamente operacionais para pesquisa e apostas recreativas como **Scorers** de ponderação heurística, desde que a emissão final passe pelo crivo combinatório do motor.
3. **Auditoria Contínua & Reproducibilidade:**
   Este relatório é gerado automaticamente pelo script `scripts/audit_fringe_theories.py` e integrado ao ciclo de vida de dados com conformidade total Zero-PII.
