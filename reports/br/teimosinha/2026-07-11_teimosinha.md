---
type: prediction-report
subtype: teimosinha
date: 2026-07-11 18:25:54
tags: [lottery, teimosinha, mega-sena, lotofacil, prediction-engine]
---

# Relatório de Jogo para Teimosinha

Gerado em: **2026-07-11 18:25:54**

> ⚠️ **Aviso importante:** Loterias são eventos aleatórios e independentes. Este relatório usa análise estatística, backtest e filtros estruturais para escolher jogos com maior alinhamento a padrões históricos, mas **não há garantia de prêmio**. Jogue com responsabilidade.

## Resumo dos Jogos Escolhidos

| Loteria | Números | Teimosinha |
|---------|---------|------------|
| Mega-Sena | 05, 17, 28, 32, 52, 55 | 12 sorteios consecutivos |
| Lotofácil | 01, 03, 04, 05, 06, 10, 12, 14, 15, 18, 19, 20, 21, 22, 25 | 24 sorteios consecutivos |

---

## 1. Mega-Sena

- **Números:** 05, 17, 28, 32, 52, 55
- **Soma:** 189
- **Média histórica esperada:** 183.0
- **Score composto:** 0.5590

### Estratégias testadas e backtest

| Estratégia | Média de acertos | Máx. acertos | Sorteios com 4+ |
|------------|------------------|--------------|-----------------|
| weighted | 0.40 | 2 | 0 |
| markov | 0.60 | 2 | 0 |
| bayesian | 0.50 | 2 | 0 |
| monte_carlo | 0.75 | 2 | 0 |
| spectral | 0.55 | 2 | 0 |
| cycle | 0.50 | 3 | 0 |
| crowd_avoidance | 0.60 | 2 | 0 |
| streak | 0.40 | 2 | 0 |
| advanced | 0.70 | 4 | 1 |
| structural | 0.55 | 2 | 0 |

### Contribuição do score

| Componente | Valor |
|------------|-------|
| Votos das estratégias | 1.0000 |
| Backtest | 0.0925 |
| Frequência | 0.0983 |
| Lacunas/ciclos | 0.8738 |
| Filtros estruturais | 0.9009 |

### Números quentes (últimos 100 sorteios): 06, 09, 42, 27, 01, 14, 44, 58, 60, 15
### Números atrasados: 43, 37, 23, 38, 50, 20, 12, 36, 41, 53

### Pares mais frequentes

| Par | Ocorrências |
|-----|-------------|
| 05-27 | 43 |
| 04-52 | 41 |
| 38-53 | 41 |
| 23-53 | 41 |
| 36-53 | 41 |
| 42-49 | 40 |
| 06-34 | 40 |
| 05-11 | 40 |
| 41-53 | 40 |
| 41-58 | 40 |

---

## 2. Lotofácil

- **Números:** 01, 03, 04, 05, 06, 10, 12, 14, 15, 18, 19, 20, 21, 22, 25
- **Soma:** 195
- **Média histórica esperada:** 195.0
- **Score composto:** 0.6931

### Estratégias testadas e backtest

| Estratégia | Média de acertos | Máx. acertos | Sorteios com 4+ hits |
|------------|------------------|--------------|----------------------|
| weighted | 9.40 | 11 | 20 |
| markov | 8.95 | 11 | 20 |
| bayesian | 8.80 | 11 | 20 |
| crowd_avoidance | 8.65 | 11 | 20 |
| structural | 9.05 | 12 | 20 |
| positional | 9.70 | 13 | 20 |

### Contribuição do score

| Componente | Valor |
|------------|-------|
| Votos das estratégias | 1.0000 |
| Backtest | 0.6061 |
| Frequência | 0.6140 |
| Lacunas/ciclos | 0.3821 |
| Filtros estruturais | 0.7431 |

### Números quentes (últimos 100 sorteios): 05, 10, 18, 25, 01, 06, 03, 13, 24, 11
### Números atrasados: 09, 14, 15, 21

### Pares mais frequentes

| Par | Ocorrências |
|-----|-------------|
| 10-25 | 1423 |
| 11-20 | 1423 |
| 10-20 | 1415 |
| 13-20 | 1412 |
| 20-25 | 1408 |
| 14-20 | 1398 |
| 10-11 | 1392 |
| 09-10 | 1386 |
| 01-10 | 1386 |
| 10-14 | 1380 |

---

## 3. Metodologia

1. **Dados históricos:** carregados do banco DuckDB local (`data/lottery.db`), com os sorteios mais recentes buscados da Caixa.
2. **Estratégias:** cada estratégia do `lottery` CLI foi executada para gerar múltiplos candidatos, com temperaturas determinística (0.3) e exploratória (1.0).
3. **Backtest:** para cada estratégia, simulou-se prever os últimos 20 sorteios usando apenas os dados anteriores, medindo acertos médios e máximos.
4. **Frequências e ciclos:** calculou-se frequência, atraso e gap médio de cada número nos últimos 100 sorteios e no histórico completo.
5. **Filtros estruturais:** cada candidato foi avaliado por soma, paridade, dezenas, colunas finais e consecutividade.
6. **Score composto:** combinou-se votos das estratégias, desempenho no backtest, frequência, lacunas e harmonia estrutural com pesos fixos.
7. **Otimização:** selecionou-se o melhor bilhete por loteria e refinou-se trocando um número por vez para maximizar o score.

## 4. Ressalvas

- Nenhum modelo consegue prever sorteios verdadeiramente aleatórios; o que se busca é **evitar combinações anômalas** e alinhar o jogo a padrões históricos estáveis.
- 'Teimosinha' não altera a probabilidade por sorteio, apenas mantém a mesma aposta por vários sorteios consecutivos.
- Resultados passados (backtest) não garantem resultados futuros.
