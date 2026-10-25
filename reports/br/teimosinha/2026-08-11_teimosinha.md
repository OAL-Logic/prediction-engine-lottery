---
type: prediction-report
subtype: teimosinha
date: 2026-08-11 21:30:07
tags: [lottery, teimosinha, mega-sena, lotofacil, prediction-engine]
---

# Relatório de Jogo para Teimosinha

Gerado em: **2026-08-11 21:30:07**

> ⚠️ **Aviso importante:** Loterias são eventos aleatórios e independentes. Este relatório usa análise estatística, backtest e filtros estruturais para escolher jogos com maior alinhamento a padrões históricos, mas **não há garantia de prêmio**. Jogue com responsabilidade.

## Resumo dos Jogos Escolhidos

| Loteria | Números | Teimosinha |
|---------|---------|------------|
| Mega-Sena | 01, 05, 34, 37, 42, 60 | 12 sorteios consecutivos |
| Lotofácil | 01, 02, 05, 06, 07, 08, 10, 14, 15, 16, 19, 21, 22, 23, 25 | 24 sorteios consecutivos |

---

## 1. Mega-Sena

- **Números:** 01, 05, 34, 37, 42, 60
- **Soma:** 179
- **Média histórica esperada:** 183.0
- **Score composto:** 0.5338

### Estratégias testadas e backtest

| Estratégia | Média de acertos | Máx. acertos | Sorteios com 4+ |
|------------|------------------|--------------|-----------------|
| weighted | 1.05 | 4 | 1 |
| markov | 0.75 | 2 | 0 |
| bayesian | 0.55 | 2 | 0 |
| monte_carlo | 0.60 | 2 | 0 |
| spectral | 0.75 | 2 | 0 |
| cycle | 0.75 | 1 | 0 |
| crowd_avoidance | 0.65 | 2 | 0 |
| streak | 1.05 | 3 | 0 |
| advanced | 0.40 | 1 | 0 |
| structural | 0.50 | 2 | 0 |

### Contribuição do score

| Componente | Valor |
|------------|-------|
| Votos das estratégias | 1.0000 |
| Backtest | 0.1175 |
| Frequência | 0.1117 |
| Lacunas/ciclos | 0.6236 |
| Filtros estruturais | 0.9239 |

### Números quentes (últimos 100 sorteios): 06, 58, 27, 42, 21, 30, 60, 32, 01, 05
### Números atrasados: 36, 41, 04, 52, 57, 29, 09, 26, 44, 13

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

- **Números:** 01, 02, 05, 06, 07, 08, 10, 14, 15, 16, 19, 21, 22, 23, 25
- **Soma:** 194
- **Média histórica esperada:** 195.0
- **Score composto:** 0.6970

### Estratégias testadas e backtest

| Estratégia | Média de acertos | Máx. acertos | Sorteios com 11+ |
|------------|------------------|--------------|------------------|
| weighted | 9.50 | 12 | 20 |
| markov | 9.45 | 11 | 20 |
| bayesian | 9.00 | 11 | 20 |
| crowd_avoidance | 9.10 | 11 | 20 |
| structural | 9.10 | 11 | 20 |
| positional | 9.30 | 12 | 20 |

### Contribuição do score

| Componente | Valor |
|------------|-------|
| Votos das estratégias | 1.0000 |
| Backtest | 0.6161 |
| Frequência | 0.6040 |
| Lacunas/ciclos | 0.4012 |
| Filtros estruturais | 0.7464 |

### Números quentes (últimos 100 sorteios): 05, 01, 09, 02, 03, 23, 11, 14, 15, 06
### Números atrasados: 07, 10, 19, 16

### Pares mais frequentes

| Par | Ocorrências |
|-----|-------------|
| 11-20 | 1435 |
| 10-25 | 1426 |
| 13-20 | 1422 |
| 10-20 | 1420 |
| 20-25 | 1416 |
| 14-20 | 1407 |
| 10-11 | 1397 |
| 09-10 | 1392 |
| 01-10 | 1391 |
| 10-14 | 1388 |

---

## 3. Metodologia

1. **Dados históricos:** carregados do banco DuckDB local (`data/lottery.db`), com os sorteios mais recentes buscados da Caixa.
2. **Estratégias:** cada estratégia do `lottery` CLI foi executada para gerar múltiplos candidatos, com temperaturas determinística (0.3) e exploratória (1.0).
3. **Backtest:** para cada estratégia, simulou-se prever os últimos 50 sorteios usando apenas os dados anteriores, medindo acertos médios e máximos.
4. **Frequências e ciclos:** calculou-se frequência, atraso e gap médio de cada número nos últimos 100 sorteios e no histórico completo.
5. **Filtros estruturais:** cada candidato foi avaliado por soma, paridade, dezenas, colunas finais e consecutividade.
6. **Score composto:** combinou-se votos das estratégias, desempenho no backtest, frequência, lacunas e harmonia estrutural com pesos fixos.
7. **Otimização:** selecionou-se o melhor bilhete por loteria e refinou-se trocando um número por vez para maximizar o score.

## 4. Ressalvas

- Nenhum modelo consegue prever sorteios verdadeiramente aleatórios; o que se busca é **evitar combinações anômalas** e alinhar o jogo a padrões históricos estáveis.
- 'Teimosinha' não altera a probabilidade por sorteio, apenas mantém a mesma aposta por vários sorteios consecutivos.
- Resultados passados (backtest) não garantem resultados futuros.
