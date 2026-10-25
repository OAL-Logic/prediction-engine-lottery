# 🏷️ Guia Oficial de Preços, Apostas Múltiplas e Teimosinha das Loterias Caixa

Este documento consolida a especificação matemática, financeira e operacional de todas as loterias da Caixa Econômica Federal vigentes após os reajustes de preços (válidos a partir de julho de 2025).

Ele documenta as apostas simples, a fórmula e tabelas completas de **apostas com mais números (desdobramentos/apostas múltiplas)**, os ciclos e valores da **Teimosinha**, e a integração programática com o arquivo [`data/pricing_and_multiple_bets.yaml`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/PRJ%20Prediction%20Engine/lottery/data/pricing_and_multiple_bets.yaml) e o módulo [`engine.modules.pricing`](file:///mnt/c/Users/ag/Documents/Obsidian/PKM/Workspace/PRJ%20Prediction%20Engine/lottery/engine/modules/pricing.py).

---

## 1. 💵 Tabela Geral de Preços das Apostas Simples

| Modalidade | Dezenas do Jogo Simples ($k$) | Preço Anterior | Preço Vigente Atual | Frequência Semanal | Dias de Sorteio |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Mega-Sena** | 6 | R$ 5,00 | **R$ 6,00** | 3× / semana | Terças, Quintas e Sábados |
| **Lotofácil** | 15 | R$ 3,00 | **R$ 3,50** | 6× / semana | Segunda a Sábado |
| **Quina** | 5 | R$ 2,50 | **R$ 3,00** | 6× / semana | Segunda a Sábado |
| **Dupla Sena** | 6 | R$ 2,50 | **R$ 3,00** | 2× / semana | Quartas e Sábados |
| **+Milionária** | 6 (+ 2 trevos) | R$ 6,00 | **R$ 6,00** | 2× / semana | Quartas e Sábados |
| **Lotomania** | 50 | R$ 3,00 | **R$ 3,00** | 3× / semana | Terças, Quintas e Sextas |
| **Dia de Sorte** | 7 | R$ 2,50 | **R$ 2,50** | 3× / semana | Terças, Quintas e Sábados |
| **Super Sete** | 7 colunas | R$ 2,50 | **R$ 3,00** | 3× / semana | Segundas, Quartas e Sextas |
| **Loteca** | 14 jogos | R$ 3,00 | **R$ 4,00** | 1× / semana | Fins de semana |
| **Timemania** | 10 | R$ 3,50 | **R$ 3,50** | 3× / semana | Terças, Quintas e Sábados |

---

## 2. 📐 Fundamento Matemático das Apostas Múltiplas

Uma aposta múltipla oficial da Caixa consiste em marcar mais números no volante do que a quantidade mínima exigida.  
Matematicamente, a Caixa fatura a aposta cobrando a soma de todas as subcombinações possíveis de tamanho $k$ contidas no conjunto de $N$ dezenas escolhidas:

$$\text{Combinações Geradas} = \binom{N}{k} = \frac{N!}{k!(N - k)!}$$

$$\text{Preço do Concurso} = \binom{N}{k} \times \text{Preço da Aposta Simples}$$

### Efeito Multiplicador de Prêmios
Quando você joga uma aposta múltipla e acerta $m$ dezenas sorteadas, você não ganha apenas 1 prêmio. O bilhete premia em múltiplos níveis conforme a distribuição hipergeométrica:

$$\text{Prêmios no Nível } t = \binom{m}{t} \times \binom{N - m}{k - t}$$

*Exemplo*: Em uma aposta de **8 dezenas na Mega-Sena** ($\binom{8}{6} = 28$ jogos = R$ 168,00), se você acertar **4 dezenas (Quadra)**, você receberá:
$$\binom{4}{4} \times \binom{8 - 4}{6 - 4} = 1 \times \binom{4}{2} = 6 \text{ Quadras pagas de uma vez!}$$

---

## 3. 📊 Tabelas Completas de Jogos com Mais Números

### 3.1 🟢 Mega-Sena (Base: R$ 6,00 | $k=6$)
*Permite apostar de 6 a 20 dezenas:*

| Dezenas ($N$) | Equivalência em Jogos $\binom{N}{6}$ | Custo 1 Sorteio | Teimosinha 3x (1 Sem.) | Teimosinha 6x (2 Sem.) | Teimosinha 12x (1 Mês) | Chance de Sena |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6** | 1 | **R$ 6,00** | R$ 18,00 | R$ 36,00 | R$ 72,00 | 1 em 50.063.860 |
| **7** | 7 | **R$ 42,00** | R$ 126,00 | R$ 252,00 | R$ 504,00 | 1 em 7.151.980 |
| **8** | 28 | **R$ 168,00** | R$ 504,00 | R$ 1.008,00 | R$ 2.016,00 | 1 em 1.787.995 |
| **9** | 84 | **R$ 504,00** | R$ 1.512,00 | R$ 3.024,00 | R$ 6.048,00 | 1 em 595.998 |
| **10** | 210 | **R$ 1.260,00** | R$ 3.780,00 | R$ 7.560,00 | R$ 15.120,00 | 1 em 238.399 |
| **11** | 462 | **R$ 2.772,00** | R$ 8.316,00 | R$ 16.632,00 | R$ 33.264,00 | 1 em 108.363 |
| **12** | 924 | **R$ 5.544,00** | R$ 16.632,00 | R$ 33.264,00 | R$ 66.528,00 | 1 em 54.182 |
| **13** | 1.716 | **R$ 10.296,00** | R$ 30.888,00 | R$ 61.776,00 | R$ 123.552,00 | 1 em 29.175 |
| **14** | 3.003 | **R$ 18.018,00** | R$ 54.054,00 | R$ 108.108,00 | R$ 216.216,00 | 1 em 16.671 |
| **15** | 5.005 | **R$ 30.030,00** | R$ 90.090,00 | R$ 180.180,00 | R$ 360.360,00 | 1 em 10.003 |
| **16** | 8.008 | **R$ 48.048,00** | R$ 144.144,00 | R$ 288.288,00 | R$ 576.576,00 | 1 em 6.252 |
| **17** | 12.376 | **R$ 74.256,00** | R$ 222.768,00 | R$ 445.536,00 | R$ 891.072,00 | 1 em 4.045 |
| **18** | 18.564 | **R$ 111.384,00** | R$ 334.152,00 | R$ 668.304,00 | R$ 1.336.608,00 | 1 em 2.697 |
| **19** | 27.132 | **R$ 162.792,00** | R$ 488.376,00 | R$ 976.752,00 | R$ 1.953.504,00 | 1 em 1.845 |
| **20** | 38.760 | **R$ 232.560,00** | R$ 697.680,00 | R$ 1.395.360,00 | R$ 2.790.720,00 | 1 em 1.292 |

---

### 3.2 🟣 Lotofácil (Base: R$ 3,50 | $k=15$)
*Permite apostar de 15 a 20 dezenas:*

| Dezenas ($N$) | Equivalência em Jogos $\binom{N}{15}$ | Custo 1 Sorteio | Teimosinha 6x (1 Sem.) | Teimosinha 12x (2 Sem.) | Teimosinha 24x (1 Mês) | Chance de 15 Pontos |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **15** | 1 | **R$ 3,50** | R$ 21,00 | R$ 42,00 | R$ 84,00 | 1 em 3.268.760 |
| **16** | 16 | **R$ 56,00** | R$ 336,00 | R$ 672,00 | R$ 1.344,00 | 1 em 204.298 |
| **17** | 136 | **R$ 476,00** | R$ 2.856,00 | R$ 5.712,00 | R$ 11.424,00 | 1 em 24.035 |
| **18** | 816 | **R$ 2.856,00** | R$ 17.136,00 | R$ 34.272,00 | R$ 68.544,00 | 1 em 4.006 |
| **19** | 3.876 | **R$ 13.566,00** | R$ 81.396,00 | R$ 162.792,00 | R$ 325.584,00 | 1 em 843 |
| **20** | 15.504 | **R$ 54.264,00** | R$ 325.584,00 | R$ 651.168,00 | R$ 1.302.336,00 | 1 em 211 |

---

### 3.3 🪙 Quina (Base: R$ 3,00 | $k=5$)
*Permite apostar de 5 a 15 dezenas:*

| Dezenas ($N$) | Equivalência em Jogos $\binom{N}{5}$ | Custo 1 Sorteio | Teimosinha 6x (1 Sem.) | Teimosinha 12x (2 Sem.) | Teimosinha 24x (1 Mês) | Chance da Quina |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5** | 1 | **R$ 3,00** | R$ 18,00 | R$ 36,00 | R$ 72,00 | 1 em 24.040.016 |
| **6** | 6 | **R$ 18,00** | R$ 108,00 | R$ 216,00 | R$ 432,00 | 1 em 4.006.669 |
| **7** | 21 | **R$ 63,00** | R$ 378,00 | R$ 756,00 | R$ 1.512,00 | 1 em 1.144.763 |
| **8** | 56 | **R$ 168,00** | R$ 1.008,00 | R$ 2.016,00 | R$ 4.032,00 | 1 em 429.286 |
| **9** | 126 | **R$ 378,00** | R$ 2.268,00 | R$ 4.536,00 | R$ 9.072,00 | 1 em 190.794 |
| **10** | 252 | **R$ 756,00** | R$ 4.536,00 | R$ 9.072,00 | R$ 18.144,00 | 1 em 95.396 |
| **11** | 462 | **R$ 1.386,00** | R$ 8.316,00 | R$ 16.632,00 | R$ 33.264,00 | 1 em 52.035 |
| **12** | 792 | **R$ 2.376,00** | R$ 14.256,00 | R$ 28.512,00 | R$ 57.024,00 | 1 em 30.354 |
| **13** | 1.287 | **R$ 3.861,00** | R$ 23.166,00 | R$ 46.332,00 | R$ 92.664,00 | 1 em 18.679 |
| **14** | 2.002 | **R$ 6.006,00** | R$ 36.036,00 | R$ 72.072,00 | R$ 144.144,00 | 1 em 12.008 |
| **15** | 3.003 | **R$ 9.009,00** | R$ 54.054,00 | R$ 108.108,00 | R$ 216.216,00 | 1 em 8.005 |

---

### 3.4 🎭 Dupla Sena (Base: R$ 3,00 | $k=6$)
*Permite apostar de 6 a 15 dezenas (cada bilhete participa de 2 sorteios consecutivos do concurso):*

| Dezenas ($N$) | Equivalência em Jogos $\binom{N}{6}$ | Custo 1 Sorteio | Teimosinha 3x | Teimosinha 6x | Teimosinha 12x | Chance de Sena |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6** | 1 | **R$ 3,00** | R$ 9,00 | R$ 18,00 | R$ 36,00 | 1 em 15.890.700 |
| **7** | 7 | **R$ 21,00** | R$ 63,00 | R$ 126,00 | R$ 252,00 | 1 em 2.270.100 |
| **8** | 28 | **R$ 84,00** | R$ 252,00 | R$ 504,00 | R$ 1.008,00 | 1 em 567.525 |
| **9** | 84 | **R$ 252,00** | R$ 756,00 | R$ 1.512,00 | R$ 3.024,00 | 1 em 189.175 |
| **10** | 210 | **R$ 630,00** | R$ 1.890,00 | R$ 3.780,00 | R$ 7.560,00 | 1 em 75.670 |
| **11** | 462 | **R$ 1.386,00** | R$ 4.158,00 | R$ 8.316,00 | R$ 16.632,00 | 1 em 34.395 |
| **12** | 924 | **R$ 2.772,00** | R$ 8.316,00 | R$ 16.632,00 | R$ 33.264,00 | 1 em 17.197 |
| **13** | 1.716 | **R$ 5.148,00** | R$ 15.444,00 | R$ 30.888,00 | R$ 61.776,00 | 1 em 9.260 |
| **14** | 3.003 | **R$ 9.009,00** | R$ 27.027,00 | R$ 54.054,00 | R$ 108.108,00 | 1 em 5.291 |
| **15** | 5.005 | **R$ 15.015,00** | R$ 45.045,00 | R$ 90.090,00 | R$ 180.180,00 | 1 em 3.174 |

---

### 3.5 📅 Dia de Sorte (Base: R$ 2,50 | $k=7$)
*Permite apostar de 7 a 15 dezenas (mais 1 Mês de Sorte de 1 a 12):*

| Dezenas ($N$) | Equivalência em Jogos $\binom{N}{7}$ | Custo 1 Sorteio | Teimosinha 3x (1 Sem.) | Teimosinha 6x (2 Sem.) | Teimosinha 12x (1 Mês) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **7** | 1 | **R$ 2,50** | R$ 7,50 | R$ 15,00 | R$ 30,00 |
| **8** | 8 | **R$ 20,00** | R$ 60,00 | R$ 120,00 | R$ 240,00 |
| **9** | 36 | **R$ 90,00** | R$ 270,00 | R$ 540,00 | R$ 1.080,00 |
| **10** | 120 | **R$ 300,00** | R$ 900,00 | R$ 1.800,00 | R$ 3.600,00 |
| **11** | 330 | **R$ 825,00** | R$ 2.475,00 | R$ 4.950,00 | R$ 9.900,00 |
| **12** | 792 | **R$ 1.980,00** | R$ 5.940,00 | R$ 11.880,00 | R$ 23.760,00 |
| **13** | 1.716 | **R$ 4.290,00** | R$ 12.870,00 | R$ 25.740,00 | R$ 51.480,00 |
| **14** | 3.432 | **R$ 8.580,00** | R$ 25.740,00 | R$ 51.480,00 | R$ 102.960,00 |
| **15** | 6.435 | **R$ 16.087,50** | R$ 48.262,50 | R$ 96.525,00 | R$ 193.050,00 |

---

### 3.6 🍀 +Milionária (Base: R$ 6,00 | $k=6$ dezenas + 2 trevos)
*Permite combinar de 6 a 12 dezenas com 2 a 6 trevos. Fórmula: $\binom{N}{6} \times \binom{T}{2} \times 6,00$:*

| Dezenas + Trevos | Jogos Simples $\binom{N}{6} \times \binom{T}{2}$ | Custo 1 Sorteio | Teimosinha 2x (1 Sem.) | Teimosinha 4x (2 Sem.) | Teimosinha 5x |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **6 dezenas + 2 trevos** | 1 | **R$ 6,00** | R$ 12,00 | R$ 24,00 | R$ 30,00 |
| **6 dezenas + 3 trevos** | 3 | **R$ 18,00** | R$ 36,00 | R$ 72,00 | R$ 90,00 |
| **6 dezenas + 4 trevos** | 6 | **R$ 36,00** | R$ 72,00 | R$ 144,00 | R$ 180,00 |
| **6 dezenas + 5 trevos** | 10 | **R$ 60,00** | R$ 120,00 | R$ 240,00 | R$ 300,00 |
| **6 dezenas + 6 trevos** | 15 | **R$ 90,00** | R$ 180,00 | R$ 360,00 | R$ 450,00 |
| **7 dezenas + 2 trevos** | 7 | **R$ 42,00** | R$ 84,00 | R$ 168,00 | R$ 210,00 |
| **7 dezenas + 3 trevos** | 21 | **R$ 126,00** | R$ 252,00 | R$ 504,00 | R$ 630,00 |
| **7 dezenas + 4 trevos** | 42 | **R$ 252,00** | R$ 504,00 | R$ 1.008,00 | R$ 1.260,00 |
| **7 dezenas + 5 trevos** | 70 | **R$ 420,00** | R$ 840,00 | R$ 1.680,00 | R$ 2.100,00 |
| **7 dezenas + 6 trevos** | 105 | **R$ 630,00** | R$ 1.260,00 | R$ 2.520,00 | R$ 3.150,00 |
| **8 dezenas + 2 trevos** | 28 | **R$ 168,00** | R$ 336,00 | R$ 672,00 | R$ 840,00 |
| **8 dezenas + 3 trevos** | 84 | **R$ 504,00** | R$ 1.008,00 | R$ 2.016,00 | R$ 2.520,00 |
| **8 dezenas + 4 trevos** | 168 | **R$ 1.008,00** | R$ 2.016,00 | R$ 4.032,00 | R$ 5.040,00 |
| **9 dezenas + 2 trevos** | 84 | **R$ 504,00** | R$ 1.008,00 | R$ 2.016,00 | R$ 2.520,00 |
| **9 dezenas + 3 trevos** | 252 | **R$ 1.512,00** | R$ 3.024,00 | R$ 6.048,00 | R$ 7.560,00 |
| **10 dezenas + 2 trevos** | 210 | **R$ 1.260,00** | R$ 2.520,00 | R$ 5.040,00 | R$ 6.300,00 |
| **11 dezenas + 2 trevos** | 462 | **R$ 2.772,00** | R$ 5.544,00 | R$ 11.088,00 | R$ 13.860,00 |
| **12 dezenas + 2 trevos** | 924 | **R$ 5.544,00** | R$ 11.088,00 | R$ 22.176,00 | R$ 27.720,00 |

---

## 4. 🔁 Regras da Teimosinha por Modalidade

| Modalidade | Concursos Consecutivos Permitidos | Ciclo Padrão Recomendado | Sorteios na Semana |
| :--- | :--- | :---: | :--- |
| **Mega-Sena** | 2, 3, 4, 6, 8, 9 ou 12 | **3x** (1 semana cheia) | Ter, Qui, Sáb |
| **Lotofácil** | 3, 6, 12, 18 ou 24 | **6x** (1 semana cheia) | Seg a Sáb |
| **Quina** | 3, 6, 12, 18 ou 24 | **6x** (1 semana cheia) | Seg a Sáb |
| **Dupla Sena** | 2, 3, 4, 6, 8, 9 ou 12 | **3x** (~1,5 semana) | Qua, Sáb |
| **Lotomania** | 2, 4 ou 8 | **2x** (~1 semana) | Ter, Qui, Sex |
| **Dia de Sorte** | 3, 6, 9 ou 12 | **3x** (1 semana cheia) | Ter, Qui, Sáb |
| **+Milionária** | 2, 3, 4 ou 5 | **2x** (1 semana cheia) | Qua, Sáb |

---

## 5. 💡 Fechamentos Algorítmicos vs. Apostas Múltiplas Oficiais

Os fechamentos matemáticos (*Wheeling Systems* e *Covering Designs*) utilizam algoritmos de otimização combinatória (MILP / Programação Linear Inteira Mista) para cobrir o mesmo conjunto de dezenas com garantia formal de prêmio, mas eliminando combinações redundantes:

| Cenário de Jogo | Caixa Aposta Múltipla Oficial | Algoritmo de Fechamento Matemático | Economia de Capital | Garantia se o Sorteio cair no Pool |
| :--- | :--- | :--- | :---: | :--- |
| **Mega-Sena: 10 dezenas** | 210 jogos = **R$ 1.260,00** | 3 jogos $C(10,6,4,6)$ = **R$ 18,00** | **98,6%** | **100% Quadra garantida** (+35,7% de chance de Quina/Sena) |
| **Mega-Sena: 12 dezenas** | 924 jogos = **R$ 5.544,00** | 6 jogos $C(12,6,4,6)$ = **R$ 36,00** | **99,4%** | **100% Quadra garantida** (+24,0% de chance de Quina/Sena) |
| **Lotofácil: 18 dezenas** | 816 jogos = **R$ 2.856,00** | 6 jogos $C(18,15,13,15)$ = **R$ 21,00** | **99,3%** | **100% 13 pontos garantidos** (+ prêmios de 14/15) |
| **Quina: 12 dezenas** | 792 jogos = **R$ 2.376,00** | 8 jogos $C(12,5,3,5)$ = **R$ 24,00** | **99,0%** | **100% Terno garantido** (+ chances de Quadra/Quina) |

---

## 6. 💻 Como Usar no Código e no CLI

### Acessar Dados Estruturados em Python:
```python
from engine.modules.pricing import get_lottery_pricing, calculate_bet_cost, get_multiple_bets

# 1. Consultar preço da aposta simples
pricing = get_lottery_pricing("br/mega-sena")
print(pricing["single_bet"]["price"])  # 6.0

# 2. Calcular custo de aposta múltipla
cost_10 = calculate_bet_cost("br/mega-sena", n_numbers=10)
print(cost_10)  # 1260.0

# 3. Calcular custo com Teimosinha (3 concursos)
cost_teimosinha = calculate_bet_cost("br/mega-sena", n_numbers=10, consecutive_draws=3)
print(cost_teimosinha)  # 3780.0
```

### Comandos de Terminal CLI:
```bash
# Consultar probabilidades e custo unitário oficial
./p4lottery odds br/mega-sena
./p4lottery odds br/lotofacil
./p4lottery odds br/quina

# Gerar pacote Teimosinha completo com cálculo de apostas simples, múltiplas e fechamento
./p4lottery teimosinha br/mega-sena --draws 3
./p4lottery teimosinha br/lotofacil --draws 6
./p4lottery teimosinha br/quina --draws 6
```
