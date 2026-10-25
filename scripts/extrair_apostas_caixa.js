/**
 * Extrator Completo de Apostas Caixa (Console DevTools F12)
 * Execute na página: https://www.loteriasonline.caixa.gov.br/silce-web/#/apostas
 */
(function extrairApostasCompletas() {
  console.log("🔍 Mapeando apostas na tela...");

  const itens = Array.from(document.querySelectorAll('.card-aposta, .aposta-item, [ng-repeat*="aposta"], .item-aposta, tr.ng-scope, .panel-default'));
  const lista = [];

  itens.forEach((el, idx) => {
    const txt = (el.innerText || '').trim();
    if (!txt) return;

    // Procura concurso, data e números
    const concursoMatch = txt.match(/Concurso[:\s]*(\d+)/i) || txt.match(/(\d{4,5})/);
    const dataMatch = txt.match(/(\d{2}\/\d{2}\/\d{4})/);
    const dezenasMatch = txt.match(/(\d{2}(?:\s*-\s*\d{2}|\s*,\s*\d{2}|\s+\d{2}){4,})/);

    lista.push({
      indice: idx + 1,
      resumo_bruto: txt.replace(/\n+/g, ' | '),
      concurso: concursoMatch ? concursoMatch[1] : null,
      data: dataMatch ? dataMatch[1] : null,
      dezenas: dezenasMatch ? dezenasMatch[0] : null
    });
  });

  if (lista.length === 0) {
    // Se não encontrou elementos padrão, pega todo o container de apostas
    const container = document.querySelector('.conteudo-minhas-apostas, .area-apostas, main, #conteudo') || document.body;
    const textoGeral = container.innerText.trim();
    console.log("Visualização do texto completo:");
    console.log(textoGeral);
    copy(textoGeral);
    console.log("📋 O texto da tela foi copiado para a área de transferência!");
  } else {
    console.log(`✓ Encontradas ${lista.length} apostas!`);
    console.table(lista);
    copy(JSON.stringify(lista, null, 2));
    console.log("📋 O JSON com as apostas foi copiado para a área de transferência (Ctrl+V)!");
  }
})();
