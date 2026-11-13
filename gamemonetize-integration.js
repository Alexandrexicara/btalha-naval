/* Integração exclusiva com o SDK HTML5 da GameMonetize. */
(function () {
  "use strict";
  window.__gmSdkReady = false;
  window.__gmAdPlaying = false;
  window.__gmAdRequestInProgress = false;
  window.__gmLastAdAt = 0;
  const MIN_AD_INTERVAL_MS = 60000;

  window.__gmPauseGame = function () {
    window.__gmAdPlaying = true;
    try {
      if (window.audioCtx && window.audioCtx.state === "running") window.audioCtx.suspend();
      const fireButton = document.getElementById("bn2-fire-btn");
      if (fireButton) fireButton.disabled = true;
      console.log("⏸️ Jogo pausado durante anúncio GameMonetize.");
    } catch (error) { console.warn("Falha ao pausar o jogo:", error); }
  };

  window.__gmResumeGame = function () {
    window.__gmAdPlaying = false;
    try {
      // O áudio será retomado por playSound() após uma interação do jogador.
      // Não chamar AudioContext.resume() aqui: SDK_GAME_START pode ocorrer sem gesto do usuário.
      const fireButton = document.getElementById("bn2-fire-btn");
      if (fireButton && !window.gameOver) fireButton.disabled = false;
      console.log("▶️ Jogo retomado após anúncio GameMonetize.");
    } catch (error) { console.warn("Falha ao retomar o jogo:", error); }
  };

  function solicitarAnuncio(origem) {
    if (!window.__gmSdkReady || typeof window.sdk === "undefined" ||
        typeof window.sdk.showBanner !== "function") {
      console.info("GameMonetize ainda não está pronto; anúncio ignorado.");
      return false;
    }
    if (window.__gmAdPlaying || window.__gmAdRequestInProgress) return false;
    const agora = Date.now();
    if (agora - window.__gmLastAdAt < MIN_AD_INTERVAL_MS) return false;

    window.__gmAdRequestInProgress = true;
    window.__gmLastAdAt = agora;
    try {
      console.log("📺 Solicitando anúncio GameMonetize:", origem);
      window.sdk.showBanner();
      return true;
    } catch (error) {
      window.__gmLastAdAt = 0;
      console.warn("Falha ao solicitar anúncio GameMonetize:", error);
      return false;
    } finally {
      window.setTimeout(function () {
        window.__gmAdRequestInProgress = false;
      }, 5000);
    }
  }

  window.__gmOnReady = function () {
    window.__gmSdkReady = true;
    console.log("✅ Integração GameMonetize pronta.");
  };
  window.avisarFimFase = function (faseConcluida) {
    return solicitarAnuncio("fim da fase " + faseConcluida);
  };
  window.avisarInicioFase = function () {};
  window.mostrarAnuncioGameMonetize = function () {
    if (!window.__gmSdkReady) {
      alert("O sistema de anúncios ainda está carregando. Tente novamente em instantes.");
      return false;
    }
    return solicitarAnuncio("pedido manual do jogador");
  };
})();
