# 🔬 Estudo Empírico: Avaliação Estatística de Teorias Marginais ("Crazy Theories")
**Benchmark de Validação Popperiana e Teste de Significância contra Baselines Uniforme e Ortodoxo**

> **Jurisdição:** Brasil (`br`)  
> **Loterias Avaliadas:** Mega-Sena (`br/mega-sena`, $N=60, k=6$) e Quina (`br/quina`, $N=80, k=5$)  
> **Amostra Temporal:** Últimos 100 concursos históricos (Mega-Sena 2981–3080 e Quina 7059–7158)  
> **Classificação Arquitetural:** Auditoria de Governança de Estratégias do Tier `fun`  
> **Conformidade de Privacidade:** Zero-PII Auditado (`scripts/check_no_pii.py`)

---

## 1. Sumário Executivo

Este estudo apresenta o benchmark empírico rigoroso das **9 Teorias Marginais / Fringe** implementadas no **Lottery Engine**, confrontando-as com as premissas estabelecidas em [docs/CRAZY_LOTTERY_THEORIES.md](../../../docs/CRAZY_LOTTERY_THEORIES.md) e os manuais canônicos de apostas ([Guia Mega-Sena](../../../docs/reference/guides/win-brazil-mega-sena-lottery-ultimate-guide.md) e [Guia Quina](../../../docs/reference/guides/how-to-win-brazil-quina.md)).

Através de uma metodologia cega de backtest histórico em duas loterias estruturalmente distintas, avaliamos o desempenho preditivo de cada teoria contra uma **Tríplice Linha de Base**:
1. **Expectativa Hipergeométrica Teórica ($\mathbb{E}[X]$)**;
2. **Baseline Aleatório Uniforme (Monte Carlo Puro)**;
3. **Baseline Ortodoxo Filtrado** (combinações restritas aos intervalos canônicos de Soma, Paridade e Complexidade Aritmética $AC$).

### Veredito Popperiano
> [!IMPORTANT]
> **Falsificação Confirmada ($H_0$ Não Rejeitada):** Nenhuma das 9 teorias marginais apresentou significância estatística positiva ($p < 0.01$) sobre a expectativa teórica ou sobre o baseline aleatório uniforme. A oscilação observada é plenamente explicada pela variância amostral de Poisson/Hipergeométrica. Esse resultado **ratifica a política de governança do motor: as teorias marginais devem permanecer estritamente isoladas no tier `"fun"` com ativação exclusivamente opt-in**.

---

## 2. Metodologia Experimental & Baselines

Para cada concurso $t$ na janela de teste, o modelo recebeu apenas dados estritamente anteriores ($t' < t$). As probabilidades preditas foram convertidas no palpite de tamanho $k$ correspondente ao jogo ($k=6$ para Mega-Sena e $k=5$ para Quina).

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
* **Baseline Teórico:** $\mathbb{E}[X]_{\text{Mega}} = 6 \times \frac{6}{60} = \mathbf{0.6000}$; $\mathbb{E}[X]_{\text{Quina}} = 5 \times \frac{5}{80} = \mathbf{0.3125}$.
* **Baseline Uniforme:** Amostragem aleatória uniforme sem reposição com gerador pseudo-aleatório independente.
* **Baseline Ortodoxo:** Combinações geradas respeitando os filtros clássicos dos guias:
  * *Mega-Sena:* Soma $\in [121, 296]$, Pares $\in [2, 4]$, Complexidade $AC \in [6, 10]$.
  * *Quina:* Soma $\in [122, 330]$, Pares $\in [1, 4]$, Complexidade $AC \ge 6$.

---

## 3. Resultados Empíricos: Mega-Sena (6/60)

*Janela: Concursos 2981 a 3080 ($100$ sorteios cegos consecutivos).*  
*Expectativa Teórica:* $\mathbb{E}[X] = 0.6000$ acertos por bilhete.

| Estratégia / Baseline | Média de Acertos ($\mu$) | Desvio Padrão ($\sigma$) | Lift vs. Uniforme (%) | Lift vs. Ortodoxo (%) | $p$-valor ($H_0: \mu = 0.6$) | $0$ Acertos | $1$ Acerto | $2$ Acertos | $3$ Acertos | Status de Hipótese |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`zeno_quantum`** | **0.6400** | 0.7180 | +1.59% | +56.10% | 0.5787 | 49 | 39 | 11 | 1 | $H_0$ Não Rejeitada |
| **`tda_topology`** | **0.6300** | 0.7057 | 0.00% | +53.66% | 0.6717 | 49 | 40 | 10 | 1 | $H_0$ Não Rejeitada |
| **`lorentz`** | **0.6300** | 0.6765 | 0.00% | +53.66% | 0.6584 | 47 | 44 | 8 | 1 | $H_0$ Não Rejeitada |
| **`baseline_uniform`** | **0.6300** | 0.6913 | 0.00% | +53.66% | 0.6653 | 49 | 39 | 12 | 0 | Linha de Base |
| **`retrocausality`** | **0.6000** | 0.6513 | -4.76% | +46.34% | 1.0000 | 48 | 45 | 6 | 1 | $H_0$ Não Rejeitada |
| **`ising_model`** | **0.5900** | 0.7398 | -6.35% | +43.90% | 0.8928 | 55 | 32 | 12 | 1 | $H_0$ Não Rejeitada |
| **`noosphere`** | **0.5900** | 0.6046 | -6.35% | +43.90% | 0.8690 | 47 | 47 | 6 | 0 | $H_0$ Não Rejeitada |
| **`sacred_grid`** | **0.5800** | 0.6060 | -7.94% | +41.46% | 0.7421 | 48 | 46 | 6 | 0 | $H_0$ Não Rejeitada |
| **`benford_illusion`** | **0.5700** | 0.7143 | -9.52% | +39.02% | 0.6754 | 55 | 34 | 10 | 1 | $H_0$ Não Rejeitada |
| **`quantum_multiverse`** | **0.5700** | 0.6553 | -9.52% | +39.02% | 0.6481 | 52 | 39 | 9 | 0 | $H_0$ Não Rejeitada |
| **`baseline_orthodox`** | **0.4100** | 0.6211 | -34.92% | 0.00% | **0.0029** | 66 | 27 | 7 | 0 | $H_0$ Rejeitada (Abaixo) |

---

## 4. Resultados Empíricos: Quina (5/80)

*Janela: Concursos 7059 a 7158 ($100$ sorteios cegos consecutivos).*  
*Expectativa Teórica:* $\mathbb{E}[X] = 0.3125$ acertos por bilhete.

| Estratégia / Baseline | Média de Acertos ($\mu$) | Desvio Padrão ($\sigma$) | Lift vs. Uniforme (%) | Lift vs. Ortodoxo (%) | $p$-valor ($H_0: \mu = 0.3125$) | $0$ Acertos | $1$ Acerto | $2$ Acertos | $3$ Acertos | Status de Hipótese |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`ising_model`** | **0.3400** | 0.5724 | +30.77% | +41.67% | 0.6320 | 71 | 24 | 5 | 0 | $H_0$ Não Rejeitada |
| **`zeno_quantum`** | **0.3400** | 0.5545 | +30.77% | +41.67% | 0.6210 | 70 | 26 | 4 | 0 | $H_0$ Não Rejeitada |
| **`tda_topology`** | **0.3100** | 0.5449 | +19.23% | +29.17% | 0.9635 | 73 | 23 | 4 | 0 | $H_0$ Não Rejeitada |
| **`sacred_grid`** | **0.3100** | 0.5631 | +19.23% | +29.17% | 0.9647 | 74 | 21 | 5 | 0 | $H_0$ Não Rejeitada |
| **`retrocausality`** | **0.2900** | 0.4777 | +11.54% | +20.83% | 0.6387 | 72 | 27 | 1 | 0 | $H_0$ Não Rejeitada |
| **`quantum_multiverse`** | **0.2900** | 0.4777 | +11.54% | +20.83% | 0.6387 | 72 | 27 | 1 | 0 | $H_0$ Não Rejeitada |
| **`noosphere`** | **0.2800** | 0.4940 | +7.69% | +16.67% | 0.5121 | 74 | 24 | 2 | 0 | $H_0$ Não Rejeitada |
| **`benford_illusion`** | **0.2700** | 0.5096 | +3.85% | +12.50% | 0.4063 | 75 | 24 | 0 | 1 | $H_0$ Não Rejeitada |
| **`baseline_uniform`** | **0.2600** | 0.4632 | 0.00% | +8.33% | 0.2598 | 75 | 24 | 1 | 0 | Linha de Base |
| **`baseline_orthodox`** | **0.2400** | 0.4292 | -7.69% | 0.00% | 0.0944 | 76 | 24 | 0 | 0 | Linha de Base |
| **`lorentz`** | **0.2100** | 0.4094 | -19.23% | -12.50% | **0.0139** | 79 | 21 | 0 | 0 | $H_0$ Rejeitada (Abaixo) |

---

## 5. Análise Epistemológica & Descobertas Críticas

### 5.1 O Comportamento do Baseline Ortodoxo
Um dos achados mais notáveis do experimento foi o desempenho do **Baseline Ortodoxo Filtrado**:
* Na Mega-Sena, a exigência rígida simultânea de Soma ($121 \le S \le 296$), Paridade balanceada ($2$ a $4$ pares) e Complexidade $AC \in [6, 10]$ obteve uma média de apenas **$0.4100$ acertos**, pontuando significativamente abaixo da expectativa pura ($p = 0.0029$).
* **Explicação Matemática:** A imposição estrita de múltiplos filtros simultâneos em um único bilhete causa uma "super-restrição geométrica". Quando concursos reais apresentam dezenas atípicas (ex: somas baixas com dezenas consecutivas ou dominância de uma mesma dezena), os filtros tradicionais excluem sistematicamente o evento sorteado. Os filtros ortodoxos são eficazes para podar o espaço amostral em desdobramentos de grande escala, mas em apostas simples individuais podem introduzir viés negativo artificial.

### 5.2 Avaliação do Comportamento Fringe
* As teorias inspiradas em física estatística e coerência dinâmica (`zeno_quantum`, `ising_model`, `tda_topology`) demonstraram grande aderência à média teórica (variando entre $0.59$ e $0.64$ na Mega-Sena e $0.31$ a $0.34$ na Quina).
* No entanto, com $p$-valores variando entre $0.57$ e $0.96$, **nenhum desses algoritmos demonstrou capacidade estatística de furar a barreira estocástica do sorteio**.
* O `lorentz` no espaço denso da Quina ($5/80$) sofreu concentração excessiva de atrator estranho, pontuando abaixo da média aleatória ($0.2100$, $p = 0.0139$), evidenciando o perigo de atratores matemáticos que ignoram a homogeneidade do globo físico.

---

## 6. Conclusões e Decisões de Governança

1. **Validação do Isolamento de Arquitetura:**
   O estudo confirma que a decisão de manter as 9 teorias isoladas sob o tier `"fun"` é tecnicamente mandatória. A permissão de entrada dessas estratégias em presets de produção causaria distorções não fundamentadas em evidência.
2. **Arquitetura em Duas Camadas Ratificada:**
   As teorias marginais podem continuar a ser utilizadas por pesquisadores e apostadores recreativos como **geradores de pesos (Scorers)**, desde que a emissão final passe pelo crivo de viabilidade combinatória do motor.
3. **Reproducibilidade & Auditoria:**
   Todos os artefatos de benchmark estão commitados e auditáveis via script em conformidade total com a política No-PII do repositório.
