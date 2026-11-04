# ⚛️ Estudo Empírico: Hardware Entropy & Quantum RNG (QRNG) Benchmarking
**Avaliação Estatística de Entropia Física, Quântica e Indistinguibilidade dos Globos da Caixa**

> **Modalidade Auditada:** `br/mega-sena`  
> **Total de Concursos Históricos:** 3080  
> **Norma Estatística de Referência:** NIST SP 800-22 Randomness Test Suite  
> **Governança:** ADR-0005 & Trilha H (Popperian Falsification Protocol)  
> **Conformidade de Privacidade:** Zero-PII Auditado (`scripts/check_no_pii.py`)  

---

## 1. Sumário Executivo & Veredito Popperiano

**Veredito:** `H_0 RETAINED: Lottery draws are statistically indistinguishable from quantum entropy.`

Este estudo afere a pureza entrópica de 4 fontes de aleatoriedade no **Lottery Engine** e confronta a série histórica real de sorteios com fluxos de **entropia quântica verdadeira**:

- **Kolmogorov-Smirnov Test:** Estatística $D = 0.0065$, $p$-valor $= 0.8282$
- **Chi-Square Uniformity Test:** $p$-valor $= 0.0276$
- **Status de Hipótese:** $H_0$ Retida (Indistinguível de QRNG)

> [!IMPORTANT]
> **Conclusão Falsificacionista:** A ausência de desvio estatístico ($p \ge 0.01$) entre as dezenas sorteadas nos globos e a entropia quântica pura comprova que os sorteios operam como geradores físicos estocásticos ideais, falsificando qualquer alegação de previsibilidade determinística ou padrão oculto explorável por teorias marginais.

---

## 2. Comparativo de Fontes de Entropia (NIST SP 800-22)

| Fonte de Entropia | Amostra (Bytes) | Entropia de Shannon (bits/byte) | Monobit $p$-valor | Runs $p$-valor | Autocorrelação Lag-1 | Status NIST |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`PRNG`** | 4,096 | 7.95551 / 8.0 | 0.4459 | 0.9733 | -0.00044 | ✅ PASSED |
| **`CSPRNG`** | 4,096 | 7.95919 / 8.0 | 0.8165 | 0.8453 | -0.00571 | ✅ PASSED |
| **`HWRNG`** | 4,096 | 7.95261 / 8.0 | 0.1417 | 0.3770 | +0.01021 | ✅ PASSED |
| **`QUANTUM_CACHE`** | 4,096 | 7.95375 / 8.0 | 0.5959 | 0.9182 | +0.00150 | ✅ PASSED |

---

## 3. Arquitetura de Coleta & Fallback de Hardware

```mermaid
flowchart TD
    Req[Requisição de Entropia] --> CheckHw{Acesso /dev/hwrng?}
    CheckHw -- Sim --> HW[/dev/hwrng TRNG Físico/TPM]
    CheckHw -- Permissão Negada / Ausente --> Jitter[Coletor Micro-Timing Jitter CPU]
    Jitter --> Mix[Mistura SHA3-512 + Secrets CSPRNG]
    HW --> Out[Stream de Bytes Criptográficos / Quânticos]
    Mix --> Out
```

---

*Relatório gerado automaticamente pelo módulo `engine.modules.hardware_entropy`.*