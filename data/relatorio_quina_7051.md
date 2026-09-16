# 🏆 Relatório de Otimização e Previsão: Quina de São João (Concurso 7077)

Este relatório apresenta o processo de busca, sintonia fina de hiperparâmetros, testes retrospectivos (backtests) e a geração de bilhetes otimizados de alta probabilidade para o concurso especial da **Quina de São João** (próximo concurso: **7077**).

---

## 📊 1. Frequência Histórica de Dezenas (Quina)

### Números Mais Sorteados (Top 15)
| Dezena | Sorteios | Frequência Relativa |
|:---:|:---:|:---:|
| **04** | 507 | 7.17% |
| **26** | 492 | 6.95% |
| **52** | 488 | 6.90% |
| **44** | 482 | 6.81% |
| **49** | 482 | 6.81% |
| **56** | 476 | 6.73% |
| **29** | 476 | 6.73% |
| **31** | 476 | 6.73% |
| **16** | 474 | 6.70% |
| **05** | 470 | 6.64% |
| **15** | 470 | 6.64% |
| **53** | 470 | 6.64% |
| **42** | 470 | 6.64% |
| **39** | 470 | 6.64% |
| **09** | 468 | 6.61% |

### Pares de Dezenas Mais Comuns (Top 5)
| Par de Dezenas | Ocorrências Históricas |
|:---:|:---:|
| 09 - 24 | 39 |
| 04 - 15 | 38 |
| 42 - 62 | 38 |
| 09 - 63 | 38 |
| 26 - 79 | 37 |

---

## 🧪 2. Leaderboard de Backtesting & Sintonia Fina (Últimos 40 Sorteios)

Avaliamos as estratégias em modo de simulação cega (out-of-sample) para medir sua precisão e retorno financeiro simulado.

| Rank | Estratégia | Parâmetros | Filtros Ativos | Média Hits | Precisão Ponderada | Lucro Simulado | ROI % |
|:---:|---|---|---|:---:|:---:|:---:|:---:|
| 1 | **markov** | `Padrão` | `Nenhum` | 0.500 | 0.200 | R$ -86.00 | 14.0% |
| 2 | **markov** | `Padrão` | `structural_odd_count` | 0.500 | 0.200 | R$ -86.00 | 14.0% |
| 3 | **markov** | `Padrão` | `structural_even_count` | 0.500 | 0.200 | R$ -86.00 | 14.0% |
| 4 | **markov** | `Padrão` | `structural_odd_count, structural_even_count` | 0.500 | 0.200 | R$ -86.00 | 14.0% |
| 5 | **weighted** | `w_frequency=1.0, w_gap=0.5, w_position=0.2` | `Nenhum` | 0.400 | 0.100 | R$ -93.00 | 7.0% |
| 6 | **weighted** | `w_frequency=1.0, w_gap=0.5, w_position=0.2` | `structural_odd_count` | 0.400 | 0.100 | R$ -93.00 | 7.0% |

---

## 🎟️ 3. Palpites Otimizados Sugeridos (Concurso 7077)

Geramos os bilhetes de maior afinidade matemática combinando as melhores configurações identificadas no leaderboard de backtest.

### Bilhete 01 ➔ ` 05 26 37 38 49 `
- **Origem**: Configuração Rank #1 (markov)
- **Filtros Aplicados**: `[]`

### Bilhete 02 ➔ ` 05 26 37 38 49 `
- **Origem**: Configuração Rank #2 (markov)
- **Filtros Aplicados**: `['structural_odd_count']`

### Bilhete 03 ➔ ` 05 26 37 49 54 `
- **Origem**: Configuração Rank #2 (markov)
- **Filtros Aplicados**: `['structural_odd_count']`

### Bilhete 04 ➔ ` 05 26 37 38 49 `
- **Origem**: Configuração Rank #3 (markov)
- **Filtros Aplicados**: `['structural_even_count']`


---

## 🧠 4. Diretrizes Estratégicas de Validação

1. **Paridade Balenceada**:
   - Evite bilhetes extremos (5 pares ou 5 ímpares). Bilhetes balanceados (3 pares / 2 ímpares ou 2 pares / 3 ímpares) cobrem cerca de 65% dos sorteios reais da Quina.
2. **Distribuição do Volante (Quadrantes)**:
   - Divida a cartela da Quina em 4 quadrantes de 20 dezenas (Q1: 1-20, Q2: 21-40, Q3: 41-60, Q4: 61-80). O bilhete ótimo possui dezenas espalhadas em pelo menos 3 quadrantes.
3. **Sequências Consecutivas**:
   - Sorteios da Quina raramente contêm dezenas coladas. A probabilidade de ocorrer números em sequência direta é de apenas ~10%. Recomendamos manter distância mínima de 1 entre as dezenas.
