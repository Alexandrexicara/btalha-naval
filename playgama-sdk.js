let sdkPronta = false;
let rewardedListenerRegistrado = false;
let rewardedEmAndamento = false;
let rewardedCallback = null;
let progressoCarregado = false;
let progressoSaveEmAndamento = Promise.resolve();

// A QA da Playgama precisa detectar uma chamada real ao Storage.
// O jogo salva progresso em mudanças significativas (fim de fase) e carrega ao iniciar.
window.aguardarProgresso = function(){ return window.__progressoPronto || Promise.resolve(); };
let resolverProgressoPronto;
window.__progressoPronto = new Promise(resolve => { resolverProgressoPronto = resolve; });

async function carregarProgressoPlaygama() {
  try {
    if (!bridge?.storage?.get) { resolverProgressoPronto(); return; }
    const data = await bridge.storage.get('mare_de_ferro_save');
    if (data) {
      const save = typeof data === 'string' ? JSON.parse(data) : data;
      if (typeof save.currentPhase === 'number') currentPhase = Math.min(Math.max(save.currentPhase, 1), totalPhases || 5);
      if (typeof save.playerScore === 'number') playerScore = save.playerScore;
      if (typeof save.enemyScore === 'number') enemyScore = save.enemyScore;
      if (Array.isArray(save.battleHistory)) battleHistory = save.battleHistory;
      if (typeof save.phaseStreak === 'number') phaseStreak = save.phaseStreak;
      console.log('💾 Progresso carregado:', save);
    } else {
      console.log('💾 Nenhum progresso anterior encontrado. Novo jogo.');
    }
  } catch (e) {
    console.warn('⚠️ Não foi possível carregar o progresso:', e);
  } finally {
    progressoCarregado = true;
    resolverProgressoPronto();
  }
}

window.salvarProgressoPlaygama = async function(nextPhase) {
  if (!sdkPronta || !bridge?.storage?.set) return false;
  const save = {
    currentPhase: nextPhase,
    playerScore: playerScore || 0,
    enemyScore: enemyScore || 0,
    battleHistory: Array.isArray(battleHistory) ? battleHistory : [],
    phaseStreak: phaseStreak || 0,
    updatedAt: Date.now()
  };
  // Serializar evita diferenças de suporte entre plataformas e mantém uma única chave.
  progressoSaveEmAndamento = progressoSaveEmAndamento.then(() => bridge.storage.set('mare_de_ferro_save', JSON.stringify(save)));
  try {
    await progressoSaveEmAndamento;
    console.log('💾 PROGRESSO SALVO NO PLAYGAMA:', save);
    return true;
  } catch (e) {
    console.error('❌ Falha ao salvar progresso:', e);
    return false;
  }
};

(function(){
  const s = document.createElement('script');
  s.src = 'https://bridge.playgama.com/v1/stable/playgama-bridge.js';
  s.async = true;
  s.onload = async function(){
    try {
      await window.bridge.initialize();
      sdkPronta = true;
      console.log('✅ Playgama Bridge PRONTO');

      if (bridge.advertisement?.setMinimumDelayBetweenInterstitial) {
        // A plataforma usa 60s como padrão; mantemos um intervalo seguro.
        bridge.advertisement.setMinimumDelayBetweenInterstitial(30);
      }

      registrarEventosRewarded();
      carregarProgressoPlaygama();

      setTimeout(async () => {
        if (bridge.platform?.sendMessage) {
          try { await bridge.platform.sendMessage('game_ready'); } catch(e) {}
        }
      }, 1000);
    } catch(e) {
      console.error('❌ Erro ao inicializar Playgama Bridge:', e);
    }
  };
  s.onerror = () => console.error('❌ Não foi possível carregar o Playgama Bridge');
  document.head.appendChild(s);
})();

function configurarPausaGameMonetize() {
  window.__gmPauseGame = function() {
    try {
      window.__gmAdPlaying = true;
      if (window.audioCtx && window.audioCtx.state === 'running') window.audioCtx.suspend();
      const fireBtn = document.getElementById('bn2-fire-btn');
      if (fireBtn) fireBtn.disabled = true;
      console.log('⏸️ Game pausado para anúncio GameMonetize.');
    } catch (e) { console.warn('Falha ao pausar jogo:', e); }
  };
  window.__gmResumeGame = function() {
    try {
      window.__gmAdPlaying = false;
      if (window.audioCtx && window.audioCtx.state === 'suspended') window.audioCtx.resume();
      const fireBtn = document.getElementById('bn2-fire-btn');
      if (fireBtn && !window.gameOver) fireBtn.disabled = false;
      console.log('▶️ Jogo retomado após anúncio GameMonetize.');
    } catch (e) { console.warn('Falha ao retomar jogo:', e); }
  };
}

function mostrarAnuncioGameMonetize() {
  if (window.__gmAdPlaying) return Promise.resolve(false);
  if (typeof sdk === 'undefined' || typeof sdk.showBanner !== 'function') {
    console.warn('⚠️ GameMonetize SDK ainda não está pronto.');
    return Promise.resolve(false);
  }
  return new Promise((resolve) => {
    let finalizado = false;
    const concluir = (ok) => {
      if (finalizado) return;
      finalizado = true;
      resolve(!!ok);
    };
    const anterior = window.__gmRewardWaiting;
    window.__gmRewardWaiting = function(ok) {
      if (anterior) { try { anterior(ok); } catch (e) {} }
      concluir(ok);
    };
    try {
      console.log('📺 GameMonetize: solicitando anúncio...');
      sdk.showBanner();
      // Alguns ambientes não disparam callback quando não há anúncio disponível.
      setTimeout(() => {
        if (!finalizado && !window.__gmAdPlaying) concluir(false);
      }, 15000);
    } catch (e) {
      console.warn('⚠️ GameMonetize showBanner falhou:', e);
      window.__gmRewardWaiting = null;
      concluir(false);
    }
  });
}

async function avisarFimFase(numero) {
  if (bridge?.platform?.sendMessage) {
    try { await bridge.platform.sendMessage('level_completed', { level: numero || 1 }); } catch(e) {}
  }
  // GameMonetize usa showBanner() para a solicitação de anúncio.
  return mostrarAnuncioGameMonetize();
}

function mostrarVideoRecompensa() {
  // O SDK HTML5 oficial do GameMonetize expõe showBanner(), não um método
  // rewarded separado. A vida extra só é liberada quando SDK_GAME_START
  // confirma que o anúncio terminou.
  if (window.__gmRewardWaiting || window.__gmAdPlaying) return Promise.resolve(false);
  if (typeof sdk === 'undefined' || typeof sdk.showBanner !== 'function') {
    alert('⏳ GameMonetize ainda está carregando os anúncios.');
    return Promise.resolve(false);
  }
  return new Promise((resolve) => {
    window.__gmRewardWaiting = function(ok) {
      if (ok && typeof window.concederVidaExtra === 'function') window.concederVidaExtra();
      resolve(!!ok);
    };
    try {
      console.log('🎁 GameMonetize: anúncio para vida extra.');
      sdk.showBanner();
    } catch (e) {
      window.__gmRewardWaiting = null;
      console.warn('⚠️ Erro no anúncio de vida extra:', e);
      resolve(false);
    }
  });
}

configurarPausaGameMonetize();

async function avisarInicioFase(numero) {
  if (!sdkPronta) return;
  if (bridge.platform?.sendMessage) {
    try { await bridge.platform.sendMessage('level_started', { level: numero || 1 }); } catch(e) {}
  }
}

// Exibe o interstitial no momento correto da transição de fase.
async function avisarFimFase(numero) {
  if (!sdkPronta) return;

  if (bridge.platform?.sendMessage) {
    try { await bridge.platform.sendMessage('level_completed', { level: numero || 1 }); } catch(e) {}
  }

  const ad = bridge.advertisement;
  if (!ad?.showInterstitial) {
    console.warn('⚠️ showInterstitial não disponível');
    return;
  }

  if (ad.isInterstitialSupported === false) {
    console.warn('⚠️ Interstitial não suportado nesta plataforma');
    return;
  }

  try {
    console.log('📺 Solicitando interstitial: level_completed');
    await ad.showInterstitial('level_completed');
    console.log('✅ Solicitação de interstitial concluída');
  } catch (e) {
    console.warn('⚠️ Interstitial falhou:', e);
  }
}

async function irParaProximaFase() {
  if (typeof window.avancarParaProximaFase === 'function') {
    await window.avancarParaProximaFase();
  }
}

// Retorna true SOMENTE quando o SDK informar o estado "rewarded".
function mostrarVideoRecompensa() {
  // IMPORTANTE PARA O TESTE DA PLAYGAMA:
  // A chamada do Rewarded deve ser feita diretamente pelo Bridge.
  // Não usar servidor/API próprio para substituir esta chamada.
  if (!window.bridge || !bridge.advertisement) {
    alert('⏳ Carregando anúncios...');
    return Promise.resolve(false);
  }

  const ad = bridge.advertisement;
  if (typeof ad.showRewarded !== 'function') {
    alert('❌ showRewarded não está disponível.');
    return Promise.resolve(false);
  }

  if (ad.isRewardedSupported === false) {
    alert('❌ Anúncio recompensado não suportado nesta plataforma.');
    return Promise.resolve(false);
  }

  if (rewardedEmAndamento) return Promise.resolve(false);

  registrarEventosRewarded();
  rewardedEmAndamento = true;

  return new Promise((resolve) => {
    let finalizado = false;

    const finalizar = (sucesso) => {
      if (finalizado) return;
      finalizado = true;
      rewardedCallback = null;
      rewardedEmAndamento = false;

      if (sucesso && typeof window.concederVidaExtra === 'function') {
        window.concederVidaExtra();
      }
      resolve(!!sucesso);
    };

    rewardedCallback = finalizar;

    console.log("🎬 PLAYGAMA REWARDED: chamando bridge.advertisement.showRewarded('extra_life')");

    // CHAMADA PRINCIPAL — placement explícito do anúncio recompensado.
    // A plataforma deve interceptar esta chamada durante o teste.
    try {
      const retorno = ad.showRewarded('extra_life');
      if (retorno && typeof retorno.catch === 'function') {
        retorno.catch((e) => {
          console.warn('⚠️ showRewarded falhou:', e);
          finalizar(false);
        });
      }
    } catch (e) {
      console.warn('⚠️ Erro ao chamar showRewarded:', e);
      finalizar(false);
    }
  });
}
