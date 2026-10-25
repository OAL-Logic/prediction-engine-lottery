# Case Study: Live Skin in the Game — br/mega-sena (Concurso 3074)

Estudo de caso prático de pré-compromisso criptográfico (*Cryptographic Proof of Pre-commitment*) aplicando a esteira analítica e o fechamento combinatório do `p4lottery` para o concurso **3074** da Mega-Sena.

---

## 1. Metadados do Registro

- **Lottery Registry ID**: `br/mega-sena`
- **Concurso Alvo**: `3074`
- **Data do Concurso**: 24/10/2026
- **Prêmio Estimado**: R$ 230.000.000,00
- **Preço da Aposta Simples**: R$ 6,00 (Vigente / Reajuste Caixa)
- **Modo de Aposta**: Fechamento Abreviado Otimizado $C(10, 6, \text{garantia}=4)$
- **Quantidade de Apostas Simples**: 24 jogos
- **Custo Total Investido**: R$ 144,00 (vs. R$ 1.260,00 no desdobramento tradicional de 10 dezenas na Caixa — **economia de 88,57%**)

---

## 2. Metodologia Analítica & Seleção do Pool

Com base no histórico completo de 3.073 sorteios acumulados até o concurso 3073 (22/10/2026), o motor combinou as seguintes estratégias de pontuação:
- **`bayesian`**: Dirichlet-Multinomial com decaimento temporal para frequência recente.
- **`weighted`**: Equilíbrio multivariado de atrasos (*gaps*) e posições de sorteio.
- **`momentum`**: Detecção de oscilação e aceleração no curto prazo.
- **`advanced`**: Filtro de equilíbrio estrutural de primos, paridade e complexidade.

### Pool de Consenso Selecionado (10 dezenas):
$$\mathbf{Pool} = [04, 05, 09, 10, 11, 17, 43, 48, 53, 56]$$

---

## 3. Protocolo de Pré-Compromisso Criptográfico (Zero Risco & Anti-Cópia)

Em repositórios públicos, a publicação explícita de jogos antes do sorteio introduz o risco teórico de **diluição de prêmio** caso múltiplos jogadores registrem os mesmos volantes. 

Para eliminar esse risco preservando 100% da integridade científica e a prova irrefutável de registro prévio:
- Os 24 bilhetes brutos gerados estão salvos exclusivamente no arquivo local do operador: `br-mega-sena-3074-bets.local.yaml` (protegido pelas regras do `.gitignore`).
- O hash criptográfico imutável é commitado publicamente antes do sorteio:

```yaml
cryptographic_proof:
  scheme: "SHA-256 Pre-commitment Hash"
  tickets_sha256: "3e2af5ca05762dd01b1e8d3819e64585b66afd610bb035d8e7be626bfd176dae"
```

> **Garantia Matemática**: É computacionalmente impossível forjar uma matriz de 24 jogos após o sorteio que resulte exatamente no hash `3e2af5ca...`. O commit no Git com timestamp pré-sorteio sela a prova de autenticidade.

---

## 4. Conferência Pós-Sorteio

Após a apuração oficial da Caixa, o operador ou qualquer auditor pode executar a verificação completa (que valida a integridade do hash e computa os acertos):

```bash
# Conferência automática via API Caixa:
python3 docs/case-studies/br-mega-sena-3074/check_results.py

# Ou informando as dezenas sorteadas:
python3 docs/case-studies/br-mega-sena-3074/check_results.py --numbers "04 10 17 48 53 56"
```
