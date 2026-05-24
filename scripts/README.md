# 🛠️ Suíte de Scripts Customizados (Operator D)

Este diretório contém ferramentas especializadas desenvolvidas para automatizar estratégias avançadas de loteria, integrando o motor estatístico do `lottery-engine` com técnicas manuais e visualizações 3D.

## 🚀 Ferramentas de Predição

### 1. Jota Silva 6-Jogos (`jota_silva_6.py`)
- **Loteria:** Lotofácil
- **Estratégia:** 13 dezenas fixas (âncoras) + 6 pares variáveis.
- **Diferencial:** Cobre todos os 25 números da Lotofácil em apenas 6 jogos (R$ 18,00).
- **Uso:** `python3 scripts/jota_silva_6.py`

### 2. Cyclical Wheeling (`lotofacil_cycle_wheel.py` & `mega_cycle_wheel.py`)
- **Conceito:** Mapeia o "Wheeling" do mercado financeiro para a loteria.
- **Fases:**
  1. **Phase 1 (CSP):** Identifica números atrasados para fechar o ciclo.
  2. **Phase 2 (Trend):** Completa com números de momentum (Hot).
  3. **Phase 3 (SRE):** Filtra jogos improváveis (Circuit Breaker).
- **Uso:** `python3 scripts/lotofacil_cycle_wheel.py` ou `python3 scripts/mega_cycle_wheel.py`

### 3. Bio-Feedback Pulse (`bio_feedback_pulse.py`)
- **Conceito:** Captura o tempo de reação do usuário em milissegundos para gerar dezenas.
- **Teoria:** O seu "eu futuro" influencia seus reflexos presentes através de micro-pulsos de adrenalina.
- **Uso:** `python3 scripts/bio_feedback_pulse.py`

---

## 📄 Relatórios de Alta Fidelidade (Engine v8.0)

### 4. Gerador de Relatório de Elite (`generate_pdf_report.py`)
Consolida todas as evidências (IA, Caos, Quântica, Geo, CPU, TDA, Zeno, Anti-Massa e Geometria Sagrada) em um documento PDF profissional com 10 dimensões de análise.

- **Dimensões Mapeadas:**
  1. IA de Stacking (Meta-aprendizado)
  2. Termodinâmica (Modelo de Ising)
  3. Atratores Caóticos (Lyapunov)
  4. Retrocausalidade Quântica
  5. Efeito Zeno Quântico (Congelamento)
  6. Topologia TDA (Buracos de Dados)
  7. Sincronizador Geográfico
  8. Semente de Hardware (Entropia CPU)
  9. Filtro Anti-Massa
  10. Geometria Sagrada (Espiral de Phi)
- **Uso:** `python3 scripts/generate_pdf_report.py [ID_DA_LOTERIA]`
- **Exemplo:** `python3 scripts/generate_pdf_report.py br/mega-sena`
- **Output:** Salva o PDF em `data/relatorio_elite_br_mega_sena.pdf`.

---

## 📊 Visualização de Dados Interativa

### 5. Explorer 3D Interativo (`interactive_3d_mega.py`)
O ápice da análise visual, permitindo manipular o "espaço de probabilidade".

- **Eixos:**
  - **X:** Dezena (1-60)
  - **Y:** Frequência Histórica (Momentum)
  - **Z:** Atraso Atual (Pressão de Ciclo)
- **Recursos:**
  - **Legenda Interativa:** Clique para ligar/desligar filtros (Primos, Fibonacci, Elite).
  - **Zoom/Rotação:** Navegação livre no espaço 3D.
  - **Hover:** Diagnóstico técnico instantâneo ao passar o mouse.
- **Dependência:** Requer `plotly`.
- **Instalação e Execução:**
  ```bash
  python3 -m pip install plotly --break-system-packages
  python3 scripts/interactive_3d_mega.py
  ```
- **Output:** Abre o arquivo `data/mega_sena_3d_interactive.html` no navegador.

---

## 🧠 Guia de Interpretação (Espaço 3D)

- **Esferas Verdes (Ciclo):** Números "vencidos" com alta probabilidade de retorno.
- **Esferas Ciano (Hot):** Números em tendência de alta.
- **Esferas Vermelhas (Elite):** As dezenas sugeridas pelo motor para o "Jogo Perfeito".
- **Tamanho da Esfera:** Representa o nível de consenso entre 4 algoritmos diferentes.

---
*Documentação gerada em 11/05/2026 para o projeto Prediction Engine.*
