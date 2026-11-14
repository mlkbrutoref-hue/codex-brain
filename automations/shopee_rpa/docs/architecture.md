# Arquitetura do Sistema — AI Commerce Content Factory

> **OUTDATED:** documento preservado como referência histórica dos módulos existentes. A arquitetura oficial está em [`../brain/ARCHITECTURE.md`](../brain/ARCHITECTURE.md); em caso de divergência, o Brain prevalece.

Este documento estabelece os alicerces arquiteturais, módulos, contratos de dados e papéis dos componentes do projeto.

---

## 1. Visão Geral e Papéis no Ecossistema

O sistema é desenhado como uma fábrica autônoma de conteúdo em vídeo de alta conversão para produtos de afiliados, com a seguinte divisão de responsabilidades:

- **Pipeline Python (Runtime Principal):** `PipelineOrchestrator` conduz os jobs, providers e transformações determinísticas.
- **Codex (Engenharia/Operação):** Mantém e verifica o projeto; não é dependência de runtime do pipeline.
- **Antigravity (Provider Operacional Opcional):** Ponte futura para tarefas estruturadas e Browser Agent. Chamadas reais exigem autorização explícita e cota disponível.
- **Shopee Affiliate API (Fonte de Verdade):** Fornecedora primária e autoritativa de todas as informações comerciais, técnicas e visuais do produto.
- **Google Flow (Geração Visual — `TO_BE_VERIFIED`):** Motor de síntese de imagens e takes de vídeo hiper-realistas ancorados na persona da Nina.
- **FFmpeg (Montagem e Renderização):** Mecanismo de corte, junção, sincronização audiovisual, queima de legendas e masterização em resolução vertical (1080x1920).
- **Nina (`persona_main_v1`):** Persona e âncora fixa de identidade visual em todas as produções.

---

## 2. Mapa de Diretórios e Módulos do Sistema

```
ai-commerce-content-factory/
│
├── app/
│   ├── core/                  # Configurações globais, utilitários, logging e clientes base
│   ├── models/                # Dataclasses e contratos de dados
│   ├── providers/             # Adaptadores de serviços externos e APIs
│   │   ├── shopee/            # Cliente e adaptador da Shopee Affiliate API
│   │   ├── visual/            # Adaptadores de geração visual (Flow, Fallback Manual)
│   │   └── voice/             # Adaptadores futuros de síntese de voz (TTS)
│   │
│   ├── creative/              # Lógica de geração e modelagem de conteúdo criativo
│   │   ├── briefs/            # Geradores de briefing de produto e persona
│   │   ├── hooks/             # Banco e gerador de ganchos de alta retenção
│   │   ├── scripts/           # Roteirizadores com calibragem de tom e fala pt-BR
│   │   ├── storyboards/       # Fatiamento de roteiro em tomadas e planos visuais
│   │   └── prompts/           # Construtores de prompts positivos e negativos para IA
│   │
│   ├── validation/            # Portões de qualidade automáticos (Quality Gates)
│   │   ├── facts/             # Validação factual de roteiros
│   │   ├── media.py           # QA técnico via ffprobe
│   │   └── visual.py          # QA semântico, inclusive NOT_EXECUTED
│   │
│   ├── media/                 # Processamento e manipulação de arquivos de mídia
│   │   ├── inventory.py       # Ordenação e integridade básica dos takes
│   │   └── ffmpeg/            # Locator, fixtures sintéticas e assembly atômico
│   │
│   ├── platforms/             # Exportadores customizados por rede social
│   │   ├── shopee_video/      # Formatação para o formato nativo Shopee Video
│   │   └── instagram_reels/   # Formatação para o formato nativo Instagram Reels
│   │
│   └── orchestration/         # Máquina de estados dos Jobs e pipeline controller
│
├── data/                      # Armazenamento estruturado de dados de execução
│   ├── products/              # Catálogo local de produtos baixados/cacheados
│   ├── personas/              # Perfis canônicos de personas
│   │   └── nina_v1/           # Nina v1.0 (persona.json, referências, prompts)
│   ├── jobs/                  # Metadados e histórico de execução de jobs
│   ├── analytics/             # Logs de métricas e performance futura
│   └── cache/                 # Cache temporário de downloads e respostas de API
│
├── output/                    # Pasta de entrega de produtos e pacotes gerados
├── tests/                     # Bateria de testes unitários e de integração
├── docs/                      # Documentação técnica viva do projeto
├── config/                    # Arquivos de configuração de ambiente e parâmetros
└── scripts/                   # Utilitários e scripts de linha de comando
```

---

## 3. Contrato Estrutural de Output (`output/<job_id>/`)

Cada execução de produção gera um pacote isolado e autodocumentado na pasta de output:

```
output/<job_id>/
│
├── product.json               # Dados brutos retornados pela Shopee Affiliate API
├── facts.json                 # Fatos categorizados (CONFIRMED_FACTS, INFERRED, UNKNOWN)
├── creative_brief.json        # Briefing criativo com formato, ângulo e foco
├── script.json                # Roteiro falado completo com timing previsto
├── storyboard.json            # Divisão detalhada de cenas, planos e descrições
│
├── prompts/                   # Prompts exatos injetados para geração de imagem/vídeo
│   ├── scene_01_prompt.txt
│   └── ...
│
├── generated/                 # Mídias visuais puras retornadas pelo Flow ou manuais
│   ├── take_01.mp4
│   └── ...
│
├── audio/                     # Arquivos de voz sintetizados e trilhas
│   ├── voice_full.mp3
│   └── background_music.mp3
│
├── subtitles/                 # Legendas sincronizadas
│   ├── subtitles.srt
│   └── subtitles.ass
│
├── master/                    # Renderização master intermediária em alta qualidade
│   └── master.mp4
│
├── platforms/                 # Versões finais prontas para publicação
│   ├── shopee.mp4
│   └── instagram.mp4
│
├── content/                   # Textos de acompanhamento, postagens e tags
│   ├── shopee.txt
│   ├── instagram.txt
│   └── hashtags.json
│
├── validation.json            # Relatório detalhado dos quality gates de validação
└── manifest.json              # Manifesto do job com timestamps, hashes e status final
```

---

## 4. Política de Fatos e Blindagem Comercial (Fact Safety)

Para assegurar integridade comercial e legal:
- **`CONFIRMED_FACTS`:** O roteiro só pode expressar afirmações objetivas que tenham confirmação explícita na Shopee API.
- **`INFERRED_CONTEXT`:** Permite construir conexão emocional e situações de uso plausíveis.
- **`UNKNOWN`:** Se um atributo não está comprovado na API, é terminantemente proibido inventá-lo ou supor atributos técnicos/médicos.
