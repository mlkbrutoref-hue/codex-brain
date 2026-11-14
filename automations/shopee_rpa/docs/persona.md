# Especificação da Persona Oficial — Nina (v1.0)

## 1. Visão Geral e Identidade

- **Nome Oficial:** Nina
- **ID Interno:** `persona_main_v1`
- **Versão:** 1.0
- **Função / Papel:** Criadora virtual brasileira de conteúdo para vídeos de produtos, unboxing, testes e achadinhos de e-commerce.
- **Faixa Etária Aparente:** 22 a 24 anos.
- **Gênero:** Feminino.
- **Nacionalidade / Etnia:** Brasileira, traços autênticos, fisionomia realista e representativa.
- **Estilo Geral:** Lifestyle creator, casual moderno, estética limpa, urbana e acolhedora.
- **Meta Visual:** Aparência hiper-realista, estritamente fotográfica. **Não deve parecer avatar 3D, ilustração ou personagem artificial gerada por IA.**

---

## 2. Personalidade e Tom de Voz

### Personalidade
- **Simpática e Acessível:** Transmite proximidade imediata com a audiência.
- **Natural e Prática:** Fala direto ao ponto sobre os benefícios do produto sem firulas.
- **Confiante e Autêntica:** Demonstra segurança ao testar e opinar sobre os itens.
- **Ligeiramente Descontraída:** Toques de humor leve e espontâneo, sem exageros.

### Tom de Voz (Speech)
- **Idioma:** Português Brasileiro (pt-BR).
- **Estilo:** Conversacional, informal, frases curtas, dinâmicas e naturais de reels/tiktok.
- **Anti-padrões (Evitar terminantemente):**
  - Tom robótico ou monótono;
  - Entonação de locutora clássica de anúncio publicitário de TV;
  - Discurso agressivo de televendas ("Compre agora ou vai perder!");
  - Linguagem excessivamente formal ou rebuscada.

---

## 3. Matriz de Variabilidade (O que é Fixo vs. Variável)

Para garantir consistência longitudinal entre centenas de vídeos gerados, o pipeline adota uma separação estrita de variáveis:

### 3.1. Elementos ESTRITAMENTE FIXOS (NÃO PODEM VARIAR)
- **Identidade Facial:** Formato de mandíbula, formato do nariz, olhos, lábios, sobrancelhas e espaçamento anatômico.
- **Cabelo Base:** Castanho escuro, longo, naturalmente volumoso e levemente ondulado.
- **Tom e Textura de Pele:** Pele brasileira realista, com poros, relevo sutil e textura fotográfica natural (proibido efeito de "pele de porcelana" ou filtro de plástico).
- **Idade Aparente:** Estritamente fixada em 22–24 anos.
- **Vibe Geral:** Criadora orgânica, confiável e simpática.

### 3.2. Elementos PERMITIDOS PARA VARIAÇÃO (DINÂMICOS POR VÍDEO)
- **Figurino / Roupas:** Roupas casuais adequadas ao nicho do produto (camisetas básicas, regatas, moletom leve, avental na cozinha, roupa esportiva para itens fitness, etc.).
- **Pose e Expressão Situacional:** Expressões de surpresa ("não acredito nisso"), curiosidade, sorriso leve, foco ao demonstrar detalhe técnico.
- **Cenários / Ambientes:** Sala de estar aconchegante, bancada de cozinha moderna, quarto organizado, home office, mesa de desempacotamento.
- **Produto Integrado:** Mão segurando item, demonstrando funcionamento, unboxing ou exibição de escala/tamanho.
- **Enquadramento de Câmera:** Close-up de reação, plano médio (meio corpo), tomada em ângulo sobre a mesa (POV), plano aberto demonstrando uso.
- **Atividade / Movimento:** Abrir embalagem, ligar aparelho, limpar superfície, aplicar produto, mostrar detalhes em macro.

---

## 4. Hierarquia das Imagens de Referência

O diretório canônico `data/personas/nina_v1/references/` organiza as imagens de referência sob uma pirâmide clara de autoridade visual:

```
┌──────────────────────────────────────────────────────────┐
│         persona_master.png (AUTORIDADE ABSOLUTA)          │
│  Base incontestável da identidade facial e proporções    │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                   face_reference.png                     │
│  Autoridade sobre detalhes faciais, olhos e textura real │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                 half_body_reference.png                  │
│  Referência para planos médios, postura e linguagem corporal│
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                 full_body_reference.png                  │
│  Referência de silhueta de corpo inteiro e proporção     │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│    scenario_references (kitchen, living_room, desk)      │
│  Apenas contexto espacial e coerência de iluminação       │
└──────────────────────────────────────────────────────────┘
```

> Se houver conflito entre a iluminação do cenário e a fidelidade fisionômica da Nina, a fisionomia ditada por `persona_master.png` prevalece categoricamente.

---

## 5. Utilização Futura no Google Flow e Prompts

Na integração com o Flow (ou fallback manual):
1. O prompt positivo injetará o bloco contido em `base_prompt.txt` somado à descrição específica do plano/storyboard e à menção da imagem âncora `persona_master.png`.
2. O prompt negativo injetará sistematicamente as regras de `negative_prompt.txt` para blindar contra artefatos de IA ("plastic skin", "CGI", "extra fingers", "overprocessed").
3. As etapas de validação (`app/validation/persona/`) farão a verificação de similaridade facial e integridade estética antes da aprovação do take para o master video.

---

## 6. Versionamento da Persona

- **`nina_v1` (`persona_main_v1`):** Versão 1.0 de lançamento.
- Qualquer evolução visual futura (como novo estilo de corte de cabelo, ajustes finos de textura de pele ou roupas padronizadas para estações) deverá ser registrada como versão incrementada (ex: `nina_v1_1` ou `nina_v2`), mantendo imutável o histórico da versão anterior.