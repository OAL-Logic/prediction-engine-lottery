# Dia e Mês da Sorte — Loterias & Numerologia

Um aplicativo interativo, vibrante e descontraído inspirado na numerologia da espiritualista Márcia Sensitiva, projetado para calcular o dia, mês e dia da semana da sorte com base no dia de nascimento, além de gerar palpites inteligentes e fornecer um calendário interativo de melhores datas para apostar na loteria.

---

### User Review & Critical Decisions

> [!IMPORTANT]
> **Decisões confirmadas com o usuário na Fase 1:**
> - **Estilo Visual**: Vibrante e descontraído com tema de loterias, trevo da sorte de 4 folhas e tons esmeralda/dourado, com cartelas nítidas e contraste de alto padrão.
> - **Recursos Inclusos**: Calculadora do número da sorte (dias, meses e dia da semana), Gerador de Palpites de Loterias (Mega-Sena, Quina, Lotofácil e Personalizado) e Calendário Interativo de Apostas com destaque de confluências cósmicas.
> - **Idioma**: Bilíngue nativo (Português do Brasil e Inglês), com troca instantânea em um clique no cabeçalho.

---

## 1. Overview & Core Concept

- **O que faz**:
  1. **Calculadora Numerológica Instantânea**: O usuário insere sua data de nascimento (ou dia de nascimento) e o app calcula o dígito reduzido (1 a 9) com a fórmula de Márcia Sensitiva (soma dos dígitos do dia até obter um número unitário).
  2. **Perfil da Sorte Detalhado**: Exibe os dias do mês propícios, os meses mais afortunados e o dia da semana ideal para apostar.
  3. **Gerador de Palpites Harmonizados**: Gera combinações para Mega-Sena (6 dezenas de 1 a 60), Lotofácil (15 dezenas de 1 a 25) e Quina (5 dezenas de 1 a 80), incorporando obrigatoriamente o número pessoal, dias associados e números ressonantes.
  4. **Calendário Interativo de Melhores Datas**: Visualizador de calendário mensal que destaca os dias da sorte, o dia da semana favorito e alerta quando o mês atual é o mês da sorte do usuário ("Confluência Tripla de Sorte").
  5. **Salvar e Copiar Jogos**: Armazenamento local (`localStorage`) para salvar bilhetes favoritos e botão de cópia formatada para levar à casa lotérica ou aplicativo de loterias.

- **Público-Alvo**: Apostadores de loterias, entusiastas de astrologia/numerologia e qualquer pessoa que queira escolher datas estratégicas para decisões importantes e jogos da sorte.

---

## 2. User Experience & Visual Design

### Fluxo de Uso
1. **Entrada Amigável**: Campo interativo para selecionar a data de nascimento ou roleta direta com os 31 dias do mês, com cálculo e animação em tempo real.
2. **Revelação do Número**: Animação de revelação com som sutil de sorte (Web Audio API) exibindo o número-chave (1 a 9) e sua vibração.
3. **Cartões de Orientação (3 Pilares)**:
   - *Dias da Sorte*: Grade com as datas do mês (ex: 10, 19, 28 para o 1).
   - *Meses da Sorte*: Meses de maior vibração (ex: Janeiro e Outubro).
   - *Dia da Semana Ideal*: O dia perfeito para ir à lotérica (ex: Domingo).
4. **Próxima Grande Data ("Super Data")**: Destaque cronológico da próxima data no calendário que une o dia da sorte ao dia da semana ideal.
5. **Aba do Gerador de Palpites**: Seleção da modalidade (Mega-Sena, Quina, Lotofácil), gerador com efeito de giro das bolinhas e opção de salvar/copiar bilhete.
6. **Aba do Calendário Interativo**: Navegação mês a mês com marcação visual dos dias quentes e filtro de sorte.

### Identidade Visual & Tema
- **Aesthetic**: Festivo, afortunado e contemporâneo — esmeralda profundo (`#064e3b` / `#047857`), dourado radiante (`#d97706` / `#f59e0b`), trevos verdes vivos (`#10b981`), superfícies brancas com cantos suaves e tipografia limpa.
- **Tipografia**:
  - Títulos: `Outfit` / `Plus Jakarta Sans` para destaque numérico forte e festivo.
  - Corpo: Sans-serif legível com números tabulares (`tabular-nums`) para as bolinhas de loteria e tabelas de datas.
- **Top Bar Contract (3 Zonas)**:
  - Zona 1: Logomarca "Trevo da Sorte" com ícone de 4 folhas.
  - Zona 2: Links simples de navegação em uma linha (Calculadora, Palpites, Calendário, Regras).
  - Zona 3: Alternador de Idioma (PT-BR / EN) e botão de Novo Cálculo.

---

## 3. Key Product Decisions & Trade-Offs

- **Cálculo Local & Imediato**:
  - *Abordagem*: 100% no cliente sem necessidade de cadastro, garantindo resposta instantânea e privacidade total.
  - *Por que*: Usuários querem descobrir seus números em segundos, testar datas de familiares e salvar palpites offline.
- **Algoritmo de Palpites Fundamentado**:
  - *Abordagem*: O gerador de loterias não é apenas aleatório puro (`Math.random()`), mas sim sementeado pelos números da sorte do usuário (número base, dias do mês correlacionados e múltiplos/complementos pitagóricos), completando o restante com distribuição harmônica de pares e ímpares.
  - *Por que*: Respeita a intenção da numerologia e fornece palpites com valor simbólico autêntico.
- **Suporte Bilíngue Centralizado**:
  - *Abordagem*: Dicionário estruturado com tipagem TypeScript estrita para alternância instantânea entre PT-BR e EN sem recarregar o app.

---

## 4. Technical Architecture & Data Strategy

### Component Hierarchy & Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                       TopNavigation                          │
│   [Trevo da Sorte]      [Calculadora | Palpites | Calendário]  [PT/EN]
└──────────────────────────────┬───────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
   ┌───────────────────────────┐ ┌───────────────────────────┐
   │    BirthdateInputHero     │ │   LuckyProfileDashboard   │
   │  (Day picker / Date input)│ │  • Número da Sorte (1-9)  │
   │  • Cálculo de redução     │ │  • Dias do Mês favoráveis │
   │  • Som de celebração      │ │  • Meses de Ouro          │
   └────────────┬──────────────┘ │  • Dia da Semana Sagrado  │
                │                └─────────────┬─────────────┘
                ▼                              ▼
   ┌───────────────────────────┐ ┌───────────────────────────┐
   │    LotteryGeneratorView   │ │    LuckyCalendarView      │
   │  • Mega-Sena (6 / 1-60)   │ │  • Visão Mensal Dinâmica  │
   │  • Lotofácil (15 / 1-25)  │ │  • Dias Marcados          │
   │  • Quina (5 / 1-80)       │ │  • Alerta de Confluência  │
   │  • Salvar / Copiar Jogos  │ │  • Próxima data de aposta │
   └───────────────────────────┘ └───────────────────────────┘
                │                              │
                └──────────────┬───────────────┘
                               ▼
   ┌───────────────────────────────────────────────────────────┐
   │                LocalStorage Saved Bets                    │
   │       (Bilhetes salvos, histórico, cópia rápida)          │
   └───────────────────────────────────────────────────────────┘
```

### Estrutura de Dados & Regras da Márcia Sensitiva (Mapeamento Completo)
- **Cálculo**:
  ```ts
  function getLuckyNumber(day: number): number {
    let sum = Math.floor(day / 10) + (day % 10);
    while (sum > 9) {
      sum = Math.floor(sum / 10) + (sum % 10);
    }
    return sum;
  }
  ```
- **Tabela Mestre**:
  - Número 1: Dias [10, 19, 28], Meses [1, 10], Dia Semana: 0 (Domingo)
  - Número 2: Dias [2, 11, 21, 29], Meses [2, 11], Dia Semana: 1 (Segunda)
  - Número 3: Dias [3, 12, 21, 30], Meses [3, 12], Dia Semana: 2 (Terça)
  - Número 4: Dias [4, 13, 22, 31], Meses [4, 1], Dia Semana: 3 (Quarta)
  - Número 5: Dias [5, 14, 23], Meses [5, 2], Dia Semana: 4 (Quinta)
  - Número 6: Dias [6, 15, 24], Meses [6, 3], Dia Semana: 5 (Sexta)
  - Número 7: Dias [7, 16, 25], Meses [7, 4], Dia Semana: 6 (Sábado)
  - Número 8: Dias [8, 17, 26], Meses [8], Dia Semana: 0 (Domingo)
  - Número 9: Dias [9, 18, 27], Meses [9, 6], Dia Semana: 1 (Segunda)
