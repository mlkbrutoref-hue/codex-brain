# 🚀 Automação de Vídeos de Produtos Shopee para Instagram Reels

Este módulo faz parte do ecossistema **Codex Brain** e implementa uma esteira completa e automatizada de mineração, curadoria com IA, edição Full HD e publicação de vídeos de produtos virais da Shopee para o Instagram Reels.

---

## 🌟 Principais Recursos

1. **Curadoria Inteligente de Reels Virais**:
   - Mineração automática através de perfis de alta performance de achadinhos no Brasil (`rotinadecasa.sh`, `achadosdiegobr`, `ceciliadunni`, `casaa_eden`, etc.).
   - Priorização baseada em pontuação de relevância e termos virais.
   - Eliminação de conteúdos não relacionados (carros, setups gamer, vlogs, receitas genéricas, etc.).

2. **Filtro Visual Anti-Rosto por IA (Zero Rostos)**:
   - Integração com a rede neural **OpenCV YuNet ONNX**.
   - Amostragem de múltiplos frames em cada vídeo.
   - Tolerância ZERO para rostos de criadores: garante 100% de foco no produto e demonstração de uso.

3. **Filtros Técnicos de Qualidade**:
   - Rejeição imediata de resoluções baixas (360p / 480p descartados).
   - Validação de nitidez via variância Laplaciana (descarta vídeos borrados/pixelados).
   - Duração comercial estrita (vídeos de até 60s).

4. **Edição Profissional em Full HD (1080x1920)**:
   - Redimensionamento e upscaling via **FFmpeg** com algoritmo **Lanczos**.
   - Filtro de nitidez de borda (**unsharp**) e ajuste de saturação/contraste.
   - Renderização da caixa sólida branca e tipografia **Times New Roman** nativa em 1080x1920 via **Pillow**.

5. **Integração com a API Oficial de Afiliados Shopee**:
   - Consulta GraphQL em tempo real para obter título, preço e link oficial (`s.shopee.com.br`).
   - Fallback resiliente com a mutação `generateShortLink` para garantir que todo produto gere comissão de afiliado.

6. **Geração Completa de Conteúdo e Upload**:
   - Geração automática de `_editado.mp4`, thumbnail de preview `_preview.jpg` e texto pronto `_legenda.txt`.
   - Sincronização automática com a pasta local e nuvem do Google Drive.

---

## 📁 Estrutura de Arquivos

```text
automations/shopee_reels/
├── batch_produce_10_videos.py   # Orquestrador da esteira de lote (meta diária)
├── instagram_automation.py     # Harvester e explorador de perfis do Instagram
├── video_editor.py             # Motor de edição FFmpeg + Pillow + Google Drive
├── shopee_api.py               # Módulo GraphQL de afiliados Shopee Brasil
├── product_matcher.py          # Comparador semântico estrito de produtos
├── requirements.txt            # Dependências Python
├── .env.example                # Modelo de variáveis de ambiente
└── README.md                   # Esta documentação
```

---

## ⚙️ Configuração e Instalação

### 1. Pré-requisitos
- Python 3.10 ou superior
- FFmpeg instalado no sistema e acessível no PATH
- Modelo `face_detection_yunet.onnx` disponível para detecção de rostos

### 2. Instalar dependências
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` baseado no `.env.example`:
```env
SHOPEE_APP_ID=seu_app_id
SHOPEE_SECRET=seu_secret
GDRIVE_EDITED_FOLDER_ID=seu_folder_id_no_drive
```

---

## 🚀 Como Executar

### Produção em lote (ex: 10 novos vídeos prontos):
```bash
python batch_produce_10_videos.py
```

O script cuidará automaticamente do download da melhor stream, checagem de resolução, teste de rostos por IA, consulta da Shopee, renderização em 1080x1920 e upload no Google Drive.
