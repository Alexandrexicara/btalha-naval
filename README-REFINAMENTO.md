# Operação Maré de Ferro — refinamento de design

Esta versão mantém a integração Playgama e adiciona decisões de design e conteúdo autoral ao jogo:

- identidade visual própria e painel de missão;
- cinco objetivos de fase diferentes;
- sonar tático de uso único por fase;
- sistema de precisão com bônus por desempenho;
- sequência de vitórias que influencia a pontuação;
- progressão de interface e feedback de combate;
- remoção de resultado manipulado: vitória/derrota segue o resultado real da batalha;
- botão único e contextual para anúncio recompensado;
- interstitial continua solicitado na transição entre fases.

A arte vetorial da insígnia foi desenhada especificamente para esta versão, e os efeitos sonoros são produzidos pelo próprio jogo.


## Salvamento Playgama
- O progresso agora usa `bridge.storage.get/set`.
- A chave `mare_de_ferro_save` guarda a próxima fase, placar e sequência.
- O save acontece ao concluir cada fase, antes da transição/interstitial.
- O progresso é carregado antes de iniciar a primeira partida.


## GameMonetize

A integração de anúncios foi preparada para o GameMonetize HTML5 SDK oficial.
O `index.html` contém `window.SDK_OPTIONS` e carrega `https://api.gamemonetize.com/sdk.js`.
Antes do envio ao GameMonetize, substitua `COLOQUE_SEU_GAME_ID_AQUI` pelo Game ID da página My Games.
Os eventos `SDK_GAME_PAUSE` e `SDK_GAME_START` pausam/retomam o jogo e o áudio. O anúncio é solicitado com `sdk.showBanner()` nas transições de fase e no botão de vida extra.
O Playgama Bridge continua presente somente para o salvamento de progresso; os anúncios do Playgama foram desativados.
