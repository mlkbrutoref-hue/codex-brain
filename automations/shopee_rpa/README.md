# AI Commerce Content Factory

> **OUTDATED:** esta visão geral é mantida como introdução histórica e ainda pode descrever capacidades planejadas como se estivessem completas. A fonte canônica é [`brain/README.md`](brain/README.md), seguindo a hierarquia definida no Project Brain.

Fábrica automatizada de conteúdo audiovisual original para criadores e afiliados de e-commerce, unindo dados oficiais de produtos, persona virtual consistente e geração visual com Inteligência Artificial.

---

## 💡 O que é o Projeto?

O **AI Commerce Content Factory** é um ecossistema projetado para transformar dados de produtos da Shopee em vídeos verticais originais de alta retenção e conversão (estilo Achadinhos / Lifestyle), estrelados por uma criadora virtual brasileira fixa chamada **Nina**.

Diferente de sistemas legados de download ou reedição de vídeos de terceiros, este projeto cria **conteúdo 100% autoral**:
- Roteiros dinâmicos e adaptados à linguagem informal brasileira;
- Storyboards com tomadas específicas de produto e lifestyle;
- Geração de takes visuais hiper-realistas orientados por persona;
- Masterização e renderização automática com cortes, voz, trilha e legendas;
- Empacotamento de variantes para **Shopee Video** e **Instagram Reels**.

---

## 🏗️ Arquitetura do Sistema

O fluxo central de geração opera na seguinte cadeia:

```
Shopee Affiliate API (Fonte de Verdade do Produto)
        ↓
PipelineOrchestrator Python (Runtime Principal)
        ↓
Nina (Identidade Visual Fixa / Persona v1.0)
        ↓
Google Flow (Geração Visual Hiper-realista)
        ↓
FFmpeg (Montagem, Sincronia de Áudio, Legendas e Render)
        ↓
Shopee Video + Instagram Reels (Pacote Pronto)
```

### Papéis Definidos no Ecossistema:
- **Pipeline Python:** É o runtime principal. Gerencia estados, providers e transformações sem depender de agente externo.
- **Codex:** Atua na engenharia e operação assistida do projeto.
- **Antigravity:** Provider operacional opcional para tarefas estruturadas e futura operação via navegador; exige autorização explícita e cota disponível.
- **Shopee Affiliate API:** A **fonte única de verdade** sobre preços, especificações, imagens oficiais e links rastreáveis de afiliados.
- **Google Flow:** Motor planejado para geração visual. `ManualFlowProvider` está disponível; `AntigravityFlowProvider` está preparado, mas não foi comprovado live nesta retomada.
- **Nina (`persona_main_v1`):** Persona oficial e âncora fixa de identidade visual e estética humana.
- **FFmpeg:** Montador preparado para H.264/AAC em 1080x1920 e 30 FPS; execução real aguarda o binário no `PATH`.

---

## 📁 Estrutura do Projeto

```
ai-commerce-content-factory/
├── app/
│   ├── core/                  # Utilitários, logging e base
│   ├── models/                # Schemas de dados e contratos
│   ├── providers/             # Adaptadores (Shopee, Visual, Voice, Creative)
│   ├── creative/              # Briefs, hooks, roteiros, storyboards e prompts
│   ├── validation/            # Quality gates (Fatos, Persona, Visual, Conteúdo)
│   ├── media/                 # Processamento de mídia e FFmpeg
│   ├── platforms/             # Exportadores Shopee Video e Instagram Reels
│   └── orchestration/         # Pipeline controller e job states
├── data/
│   ├── products/              # Catálogo de dados de produtos
│   ├── personas/nina_v1/      # Perfil, prompts e referências da Nina
│   ├── jobs/                  # Histórico e estado dos jobs
│   ├── analytics/             # Métricas de execução
│   └── cache/                 # Cache de respostas e mídias
├── output/                    # Pacotes finais gerados por job
├── docs/                      # Documentação completa de arquitetura e pipeline
├── tests/                     # Bateria de testes
├── config/                    # Configurações de execução
└── scripts/                   # Utilitários e scripts CLI
```

---

## 🚀 Como Começar (Para Desenvolvedores & Codex)

1. **Configuração de Ambiente:**
   ```bash
   cp .env.example .env
   ```
2. **Documentação Essencial:**
   - [docs/status.md](docs/status.md): Status atual da fase de preparação.
   - [docs/handoff.md](docs/handoff.md): Instruções detalhadas de handoff para o Codex.
   - [docs/pipeline.md](docs/pipeline.md): Ciclo de 16 etapas e máquina de estados dos jobs.
   - [docs/persona.md](docs/persona.md): Manual e restrições da Nina.
   - [docs/content-formats.md](docs/content-formats.md): Os 7 formatos de vídeo.
   - [docs/flow-integration.md](docs/flow-integration.md): Workflow do Google Flow e fallback manual.
   - [docs/providers.md](docs/providers.md): Contratos de integração e interfaces.

3. **Validação local:**
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   python -m compileall -q app tests scripts
   ```
   O runtime do pipeline usa somente a biblioteca padrão. Para executar o validador de frontmatter `quick_validate.py`, instale separadamente as dependências de desenvolvimento declaradas em `requirements-dev.txt`.
