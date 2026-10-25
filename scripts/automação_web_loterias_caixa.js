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

// Expõe globalmente no console do navegador
if (typeof window !== 'undefined') {
  window.preencherApostasCaixa = preencherApostasCaixa;
}
