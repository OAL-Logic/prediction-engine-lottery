/**
 * 🎰 CAIXA BOLÃO DEVTOOLS SNIPPET — SCRAPER & FILTRO INTELIGENTE (F12 CONSOLE)
 * ===========================================================================
 * Cole este script diretamente no Console do Chrome DevTools (F12) enquanto
 * estiver no portal da Caixa (https://www.loteriasonline.caixa.gov.br/silce-web/)
 * na aba de Bolões da Mega-Sena ou Mega da Virada!
 * 
 * O que ele faz:
 * 1. Mapeia todos os cards de bolão gerados pelas lotéricas na tela.
 * 2. Filtra bolões com jogos de MAIS DE 6 NÚMEROS (7, 8, 9, 10+ dezenas).
 * 3. Cruza com os números de elite históricos da Mega da Virada ([10, 05, 34, 33, 41, 58, 51, 03...]).
 * 4. Exibe uma tabela interativa colorida (console.table) ranqueada por probabilidade.
 * 5. Permite adicionar automaticamente a cota desejada ao carrinho!
 * 
 * Uso rápido:
 *    // Executa análise padrão buscando jogos com >= 7 dezenas
 *    caixaBuscarBoloes();
 * 
 *    // Ou personalizando filtros:
 *    caixaBuscarBoloes({
 *        minDezenas: 8,                       // Apenas bolões com jogos de 8 ou mais números
 *        dezenasAlvo: [10, 5, 34, 33, 41],    // Números que você quer priorizar
 *        maxPrecoCota: 120.00,                // Teto de valor por cota
 *        adicionarMelhorAoCarrinho: false     // Mude para true para clicar no carrinho direto
 *    });
 */

window.caixaBuscarBoloes = function (opcoes = {}) {
    const {
        minDezenas = 7,
        dezenasAlvo = [10, 5, 34, 33, 41, 58, 51, 3, 32, 35, 56, 17, 36, 59, 12, 4, 37, 23],
        maxPrecoCota = null,
        adicionarMelhorAoCarrinho = false
    } = opcoes;

    console.clear();
    console.log("%c🎰 INICIANDO SCAN DE BOLÕES CAIXA — BUSCA POR JOGOS > 6 DEZENAS 🎰", "color: #ffcc00; font-size: 14px; font-weight: bold; background: #222; padding: 6px; border-radius: 4px;");

    // 1. Mapeia cards de bolão
    const seletoresCards = [
        '.card-bolao', '.item-bolao', '[ng-repeat*="bolao"]', '.bolao-item',
        '.card-aposta', '.box-bolao', '.card-jogo', 'div[class*="bolao"]'
    ];
    let cards = Array.from(document.querySelectorAll(seletoresCards.join(', '))).filter(el => {
        const txt = (el.innerText || '').toLowerCase();
        return txt.includes('cota') || txt.includes('bolão') || txt.includes('bolao');
    });

    if (cards.length === 0) {
        cards = Array.from(document.querySelectorAll('div, li, tr')).filter(el => {
            if (el.children.length > 25 || el.children.length < 2) return false;
            const txt = el.innerText || '';
            return (txt.includes('Cota') || txt.includes('COTA')) && txt.includes('R$');
        });
    }

    if (cards.length === 0) {
        console.warn("%c⚠️ Nenhum card de bolão encontrado na página atual. Certifique-se de estar na aba 'Bolão' ou 'Bolão CAIXA'.", "color: #ff4444; font-weight: bold; font-size: 12px;");
        return [];
    }

    console.log(`✓ Mapeados ${cards.length} cards de bolão na tela.`);

    // Tabela multiplicadora de combinações da Mega-Sena C(n, 6)
    const combTable = { 6: 1, 7: 7, 8: 28, 9: 84, 10: 210, 11: 462, 12: 924, 13: 1716, 14: 3003, 15: 5005 };

    const boloesEncontrados = [];

    cards.forEach((card, index) => {
        const txt = card.innerText || '';
        if (!txt.trim()) return;

        // Preço da Cota
        const precoMatch = txt.match(/R\$\s*([\d\.,]+)/i);
        const preco = precoMatch ? parseFloat(precoMatch[1].replace('.', '').replace(',', '.')) : 0.0;

        // Cotas
        const cotasMatch = txt.match(/(\d+)\s*(?:de|\/)\s*(\d+)\s*cotas?/i) || txt.match(/(\d+)\s*cotas?\s*dispon[íi]ve/i);
        const cotasDisp = cotasMatch ? parseInt(cotasMatch[1]) : 1;
        const cotasTotal = (cotasMatch && cotasMatch[2]) ? parseInt(cotasMatch[2]) : null;

        // Quantidade de dezenas por jogo
        let maxDezenas = 6;
        const qtdNumMatch = txt.match(/(\d+)\s*(?:jogos?|apostas?)\s*de\s*(\d+)\s*(?:n[úu]meros|dezenas)/gi) ||
                            txt.match(/(\d+)\s*(?:n[úu]meros|dezenas)/gi);
        const detalhesJogos = [];

        if (qtdNumMatch) {
            qtdNumMatch.forEach(m => {
                detalhesJogos.push(m);
                const nMatch = m.match(/(\d+)\s*(?:n[úu]meros|dezenas)/i);
                if (nMatch) {
                    const n = parseInt(nMatch[1]);
                    if (n > maxDezenas) maxDezenas = n;
                }
            });
        }

        // Dezenas contidas no card
        const dezenasSet = new Set();
        const blocosDezenas = Array.from(card.querySelectorAll('.dezena, .bola, .numero, span, button'))
            .map(e => e.innerText.trim())
            .filter(t => /^\d{1,2}$/.test(t) && parseInt(t) >= 1 && parseInt(t) <= 60);

        blocosDezenas.forEach(d => dezenasSet.add(parseInt(d)));
        const dezenasArray = Array.from(dezenasSet).sort((a,b) => a - b);

        // Se dezenasArray > maxDezenas, atualiza maxDezenas
        if (dezenasArray.length > maxDezenas) {
            maxDezenas = dezenasArray.length;
        }

        // Filtros
        if (maxDezenas < minDezenas) return;
        if (maxPrecoCota && preco > maxPrecoCota) return;

        // Cálculo de Score
        const fatorComb = combTable[maxDezenas] || 1;
        let score = fatorComb * 10;

        let matchesAlvo = [];
        if (dezenasAlvo && dezenasAlvo.length > 0) {
            matchesAlvo = dezenasArray.filter(d => dezenasAlvo.includes(d));
            score += matchesAlvo.length * 15;
        }

        if (preco > 0) {
            score += (fatorComb / preco) * 5;
        }

        const btnCompra = card.querySelector('button[ng-click*="carrinho"], button[ng-click*="comprar"], button.btn-comprar, button:not([disabled])');

        boloesEncontrados.push({
            id: index,
            element: card,
            btnCompra: btnCompra,
            "Jogos/Dezenas": detalhesJogos.join(' | ') || `${maxDezenas} dezenas`,
            "Dezenas Jogo": maxDezenas,
            "Cota (R$)": preco.toFixed(2),
            "Cotas Disp": cotasDisp + (cotasTotal ? `/${cotasTotal}` : ''),
            "Dezenas de Ouro": matchesAlvo.join(', ') || 'N/D',
            "Dezenas Totais": dezenasArray.join(', ') || 'Sob clique',
            "Score": Math.round(score * 10) / 10
        });
    });

    boloesEncontrados.sort((a, b) => b.Score - a.Score);

    if (boloesEncontrados.length === 0) {
        console.warn(`❌ Nenhum bolão com jogos de >= ${minDezenas} dezenas passou no filtro.`);
        console.info("💡 Tente executar: caixaBuscarBoloes({ minDezenas: 6 }) para ver todos.");
        return [];
    }

    console.log(`%c🎉 ENCONTRADOS ${boloesEncontrados.length} BOLÕES DE ALTA CHANCE COM >= ${minDezenas} DEZENAS!`, "color: #00ff88; font-size: 13px; font-weight: bold;");
    
    // Mostra tabela formatada
    const tabelaExibicao = boloesEncontrados.map(b => ({
        "Card #": b.id,
        "Estrutura de Jogos": b["Jogos/Dezenas"],
        "Dezenas/Jogo": b["Dezenas Jogo"],
        "Preço Cota": `R$ ${b["Cota (R$)"]}`,
        "Cotas Disp.": b["Cotas Disp"],
        "Dezenas de Ouro": b["Dezenas de Ouro"],
        "Score Eficiência": b.Score
    }));
    console.table(tabelaExibicao);

    // Expõe função auxiliar para comprar bolão por ID
    window.caixaComprarBolao = function(cardId) {
        const item = boloesEncontrados.find(b => b.id === cardId);
        if (item && item.btnCompra) {
            item.btnCompra.scrollIntoView({ behavior: 'smooth', block: 'center' });
            item.btnCompra.click();
            console.log(`%c✓ Cota do Card #${cardId} adicionada ao carrinho!`, "color: #00ff88; font-weight: bold;");
        } else {
            console.error(`❌ Botão de compra do Card #${cardId} não localizado.`);
        }
    };

    if (adicionarMelhorAoCarrinho && boloesEncontrados[0] && boloesEncontrados[0].btnCompra) {
        console.log(`%c🛒 Inserindo no carrinho o Bolão TOP 1 (Card #${boloesEncontrados[0].id})...`, "color: #00e5ff; font-weight: bold;");
        boloesEncontrados[0].btnCompra.scrollIntoView({ behavior: 'smooth', block: 'center' });
        boloesEncontrados[0].btnCompra.click();
    } else {
        console.log("%c💡 Para adicionar qualquer bolão ao carrinho, execute: %ccaixaComprarBolao(NUMERO_DO_CARD)", "color: #ccc;", "color: #ffea00; font-weight: bold;");
    }

    return boloesEncontrados;
};

// Execução imediata no carregamento do console
console.log("%c✅ Extrator de Bolões Caixa Carregado! Digite: caixaBuscarBoloes()", "color: #00ff88; font-weight: bold;");
