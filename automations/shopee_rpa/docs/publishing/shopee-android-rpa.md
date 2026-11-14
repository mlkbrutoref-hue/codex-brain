# Shopee Video Android RPA — experimento USB

Status: EXPERIMENTAL; a evidência do aparelho determina o progresso. Escopo autorizado em 06/10/2026: somente postagem Shopee Video no Android real R9QYA0227VX, com publicação real permitida. O usuário informou que os seis vídeos mais recentes são de produtos; o primeiro teste começa pelo mais recente. Isto não retoma Instagram, TikTok, emulador, cloud ou geração de conteúdo.

## Pesquisa e contrato do teste

Fontes consultadas em 06/10/2026:

- [Android Developers: ADB](https://developer.android.com/tools/adb), documentação oficial, DOCUMENTED. Orienta a seleção explícita de serial e a distinção entre device/offline/unauthorized.
- [openatx: uiautomator2](https://github.com/openatx/uiautomator2), documentação do mantenedor, DOCUMENTED. Fundamenta seletores, waits, dump_hierarchy, screenshot, set_text e captura de toast. Não prova seletores nem sucesso de publicação Shopee.
- Capturas locais em `debug/shopee_android/`, OBSERVED. Shopee BR, SDK 36, 720x1600; Python 3.14 e uiautomator2 3.7.0. Seletores do app são FAST_CHANGING; atualizar após mudança de versão, activity ou falha de condição.

Hipótese: seletores semânticos e validação de estado conseguem completar uma postagem no aparelho informado. Critério: mídia identificada, texto lido de volta, produto inequívoco vinculado, Postar habilitado, nenhuma verificação de conta/erro e evidência posterior positiva. Resultado permanece pendente até confirmação real. Fixtures não provam publicação.

Entrada pretendida: serial, video_path/nome/data/hash, product_query/título/termos, caption e hashtags. Saída: estado, transições com timestamps, XML/PNG e confirmação observada. Concurrency=1. Nenhum conteúdo comercial fica fixo no núcleo.

Regras: IDs antes de descrições, depois texto e estrutura. Coordenadas somente se derivadas da árvore atual e registradas. Espera com timeout observa condições; não usar sleeps fixos como confirmação. Não repetir o clique final, inclusive após timeout ou conexão interrompida. Um resultado incerto deve exigir reconciliação com o perfil para evitar duplicação. Login, CAPTCHA, SMS ou verificação exigem intervenção humana. Não instalar mecanismos de evasão.

## Descobertas iniciais

- Aparelho conectado em ADB. A tela inicial observada era o perfil da Nina (`ReactActivity_`), não SSZMediaActivity. `content-desc=click to post video` abriu a câmera SSZMediaActivity.
- Entrada da biblioteca: `com.shopee.br:id/ll_gallery_entrance`.
- Galeria: `com.shopee.br:id/rv_gallery`; abas `content-desc=Tudo`, `Vídeo`, `Foto`. A aba Vídeo expõe `selected=true` após escolha.
- Célula: `iv_picture`, `ll_check`, `check`, `tv_duration`. A árvore não fornece nome/caminho do arquivo. Consulta somente leitura ao MediaStore fornece identidade e ordem temporal; duração e preview precisam corroborar a associação à célula.
- Avanço: `com.shopee.br:id/tv_pick_next`, inicialmente `enabled=false`. Não chamar a seleção válida só porque o toque retornou.

Falhas a tratar: galeria reordenada (verificar metadados e preview), múltiplos produtos equivalentes (parar), texto truncado (ler campo completo), seletor mudou (capturar e parar), envio incerto (não repostar), verificação de conta (parar sem registrar códigos). A documentação e o protótipo não recebem DESIGN_RESEARCHED nem READY por esta pesquisa limitada.
