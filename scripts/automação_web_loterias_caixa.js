/**
 * Utilitário de Automação Web para Loterias Caixa (Console / Bookmarklet)
 * 
 * Preenche e adiciona apostas no carrinho do portal Loterias Online da Caixa.
 * Funciona para Mega-Sena, Lotofácil, Quina, Dupla Sena, etc.
 * 
 * Uso genérico:
 * 1. Abra o portal oficial e faça login: https://www.loteriasonline.caixa.gov.br/
 * 2. Navegue até o volante da modalidade desejada.
 * 3. Abra o DevTools (F12) -> aba Console.
 * 4. Cole este script e execute passando sua matriz de jogos:
 * 
 *    preencherApostasCaixa([
 *      [4, 9, 11, 17, 48, 56],
 *      [5, 10, 15, 20, 25, 30]
 *    ]);
 */

async function preencherApostasCaixa(jogos, opcoes = {}) {
  const {
    delayCliqueNum = 140,
    delayAntesCarrinho = 350,
    delayEntreJogos = 750,
    seletorBotaoCarrinho = '#colocar-carrinho'
  } = opcoes;

  if (!Array.isArray(jogos) || jogos.length === 0) {
    console.error("❌ Erro: informe uma lista de jogos válida (ex: [[1, 2, 3, 4, 5, 6], ...]).");
    return;
  }

  const wait = (ms) => new Promise(res => setTimeout(res, ms));

  console.log(`🎰 Iniciando preenchimento de ${jogos.length} aposta(s)...`);

  for (let i = 0; i < jogos.length; i++) {
    const jogo = jogos[i];
    console.log(`[${i + 1}/${jogos.length}] Marcando dezenas: ${jogo.join(', ')}`);

    for (const n of jogo) {
      const s = n.toString().padStart(2, '0');
      const el = document.getElementById('n' + s) ||
                 document.querySelector('[data-numero="' + s + '"]') ||
                 Array.from(document.querySelectorAll('button, a, span')).find(x => x.textContent.trim() === s);

      if (el) {
        el.click();
      } else {
        console.warn(`⚠️ Dezena ${s} não encontrada no volante visual.`);
      }
      await wait(delayCliqueNum);
    }

    await wait(delayAntesCarrinho);

    const btn = document.querySelector(seletorBotaoCarrinho) ||
                Array.from(document.querySelectorAll('button')).find(b => {
                  const t = (b.innerText || '').toLowerCase();
                  return t.includes('carrinho') || t.includes('incluir');
                });

    if (btn) {
      btn.click();
      console.log(`✓ Jogo ${i + 1} colocado no carrinho.`);
    } else {
      console.error(`❌ Botão de adicionar ao carrinho não encontrado no jogo ${i + 1}. Interrompendo automação.`);
      break;
    }

    await wait(delayEntreJogos);
  }

  console.log(`🎉 Processo concluído! Revise suas ${jogos.length} aposta(s) no carrinho.`);
}

// Carteiras prontas para o sorteio de 2026-10-29 20:00 (Omni + Efemérides + Lunar/Orbital)
const JOGOS_MEGA_2026_10_29 = [
  [10, 11, 17, 28, 32, 44],
  [10, 13, 24, 35, 39, 42],
  [11, 15, 30, 33, 36, 38],
  [2, 18, 28, 33, 34, 49],
  [3, 18, 30, 34, 35, 50]
];

const JOGOS_LOTOFACIL_2026_10_29 = [
  [2, 3, 4, 6, 8, 9, 10, 11, 13, 15, 16, 18, 20, 21, 25],
  [2, 3, 6, 7, 8, 9, 11, 12, 13, 15, 16, 18, 20, 21, 25],
  [2, 4, 6, 7, 8, 10, 11, 13, 15, 16, 18, 20, 23, 24, 25],
  [1, 2, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 21, 25],
  [1, 2, 3, 4, 6, 8, 10, 11, 13, 15, 17, 18, 23, 24, 25],
  [1, 3, 4, 6, 7, 8, 10, 13, 15, 16, 17, 18, 20, 24, 25]
];

// Expõe globalmente no console do navegador
if (typeof window !== 'undefined') {
  window.preencherApostasCaixa = preencherApostasCaixa;
  window.JOGOS_MEGA_2026_10_29 = JOGOS_MEGA_2026_10_29;
  window.JOGOS_LOTOFACIL_2026_10_29 = JOGOS_LOTOFACIL_2026_10_29;
}
