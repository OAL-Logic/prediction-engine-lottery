# 🎟️ Registro de Apostas: Mega-Sena — Concurso 3076

- **Data do Sorteio:** 27/10/2026 21h00
- **Modalidade:** Mega-Sena (`br/mega-sena`)
- **Estimativa de Prêmio:** R$ 305.000.000,00
- **Estratégia:** Fechamento Combinatório Reduzido $C(12, 6, 4, 6)$ + Convergência de Ciclo
- **Pool de Elite Selecionado (12 dezenas):** `[01, 10, 14, 16, 19, 28, 32, 34, 41, 43, 52, 59]`
- **Dezenas Chave do Ciclo 65:** `[32, 34, 59]`
- **Investimento Total:** 6 apostas simples $\times$ R$ 6,00 = R$ 36,00

---

## 📋 Bilhetes Registrados

| Bilhete | Dezenas Apostadas | Soma | Pares / Ímpares | Primos | Moldura | Dezenas do Ciclo |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **01** | `01 · 28 · 41 · 43 · 52 · 59` | 224 | 2P / 4I | 3 | 4 | `[59]` |
| **02** | `10 · 19 · 32 · 41 · 43 · 52` | 197 | 3P / 3I | 3 | 3 | `[32]` |
| **03** | `14 · 19 · 34 · 41 · 52 · 59` | 219 | 3P / 3I | 3 | 3 | `[34, 59]` |
| **04** | `01 · 16 · 19 · 32 · 34 · 59` | 161 | 3P / 3I | 2 | 2 | `[32, 34, 59]` |
| **05** | `01 · 10 · 16 · 28 · 34 · 41` | 130 | 4P / 2I | 1 | 3 | `[34]` |
| **06** | `14 · 16 · 28 · 32 · 41 · 59` | 190 | 4P / 2I | 2 | 2 | `[32, 59]` |

---

## 🔍 Como Conferir os Resultados Após o Sorteio

Após a realização do sorteio oficial às 21h00, atualize a base de dados do motor:

```bash
./p4lottery fetch br/mega-sena
```

E execute a conferência automática do fechamento:

```bash
./p4lottery compare-bets br/mega-sena -n "1 28 41 43 52 59"
```
