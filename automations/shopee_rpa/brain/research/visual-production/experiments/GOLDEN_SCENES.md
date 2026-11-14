# Golden Scenes

**STATUS:** `DEFINED / NOT_EXECUTED`

Golden scenes são templates estáveis para comparação. O SKU real e seus facts devem ser aprovados antes da execução; “frasco”, “gaveta” ou “organizador” abaixo descrevem geometria experimental, não alegações sobre um produto comercial específico.

## Seleção de assets reais

Um produto só pode ocupar um golden slot quando:

- imagens oficiais/autorizadas mostram frente, lateral e mecanismo necessário;
- material, partes móveis e uso demonstrado são fatos confirmados;
- não há texto/logo pequeno essencial ao endpoint, salvo experimento específico;
- a referência está limpa e o arquivo original pode ser preservado;
- o produto não muda entre conditions/blocks;
- a ação não exige claim de eficácia.

A mesma referência canônica da Nina, roupa, cabelo e ambiente deve ser usada em todas as conditions que exigem persona.

## Frozen baseline comum

- aspect intent vertical 9:16;
- um único ambiente doméstico por scene;
- uma fonte dominante motivada e uma fill ambiente estável;
- câmera estática por padrão; mudança somente no E-04;
- uma unidade de produto, props mínimos e posições marcadas;
- sem fala, texto gerado ou áudio como variável;
- duração suportada escolhida no preflight e congelada dentro do experimento;
- um output por run quando a UI permitir;
- prompt base sem adjetivos promocionais ou claims.

## GS-A — Low Risk / static product reveal

**Produto-arquétipo:** organizador rígido, fosco, geometricamente simples, apoiado sobre bancada.  
**Persona:** ausente; nenhuma mão.  
**Ambiente:** bancada de cozinha/sala com poucos anchors fixos.  
**Ação:** produto permanece imóvel; somente uma mudança mínima de atenção visual permitida no plano-base, sem transformação física.  
**Câmera:** medium-close estática, perspectiva de smartphone normal, DOF moderada.  
**Luz:** janela lateral suave + ambiente fraco.  
**Riscos previstos:** product morph `LOW`, lighting/continuity `LOW`, hands/identity/physics `NONE`.  
**Uso:** baseline de qualidade e controle negativo; não é a principal cena de E-01/E-05 porque quase não desafia ação.

**Acceptance anchors:** contorno, número de partes, cor, escala relativa, posição na bancada, sombra e background não mudam.

## GS-B — Hand/Product Risk / one-hand presentation

**Produto-arquétipo:** frasco rígido fosco ou pequeno aparelho rígido de geometria simples, com face frontal identificável.  
**Persona:** somente torso inferior/antebraço e uma mão; rosto fora do quadro para isolar mãos/produto.  
**Ambiente:** bancada doméstica, produto inicialmente apoiado.  
**Ação atômica:** mão direita pega o produto por uma zona lateral definida, eleva poucos centímetros, orienta a face frontal para a câmera e sustenta.  
**Câmera:** medium-close estática à altura da bancada.  
**Luz:** janela frontal-lateral suave, highlights compatíveis com acabamento.  
**Riscos previstos:** hand interaction `HIGH`, product morph `MEDIUM/HIGH`, occlusion `MEDIUM`, identity `NONE`.  
**Uso:** core E-05 para mitigação de grip/occlusion; benchmark de anatomia e product fidelity.

**Acceptance anchors:** exatamente uma mão e um produto; cinco dedos plausíveis quando visíveis; grip na zona definida; face crítica permanece legível; produto não deforma nem flutua.

## GS-C — Physics Risk / sliding organizer drawer

**Produto-arquétipo:** gaveta organizadora rígida em trilho sob prateleira, com puxador e estrutura fixa visíveis.  
**Persona:** uma mão/antebraço; rosto fora do quadro.  
**Ambiente:** armário/prateleira com três props internos distintos e congelados.  
**Ação atômica base:** mão direita segura o puxador e desloca a gaveta para fora em eixo único até parar aberta.  
**Ação multi-step experimental:** abrir, remover um prop, recolocá-lo e fechar; somente usada como nível de `action_complexity` em E-01.  
**Câmera:** 3/4 lateral estática, mostrando estrutura fixa, trilho e curso.  
**Luz:** uma fonte lateral suave, interior legível, sombra coerente com translação.  
**Riscos previstos:** physics `HIGH`, product morph `HIGH`, hand `MEDIUM`, continuity `HIGH`, identity `NONE`.  
**Uso:** E-01 e E-02; useful E-05 product/physics.

**Acceptance anchors:** estrutura superior imóvel, trilho/eixo constantes, uma gaveta, três props sem duplicação, grip contínuo, final state coerente.

## GS-D — Identity + Product Risk / Nina presents product

**Produto-arquétipo:** frasco/aparelho rígido fosco simples, frente identificável e sem texto fino como endpoint principal.  
**Persona:** Nina em medium shot, rosto e cabelo totalmente visíveis, roupa canônica congelada.  
**Ambiente:** banheiro/quarto doméstico simples, sem espelho no quadro.  
**Ação:** Nina já segura o produto à altura do peito, orienta a face frontal alguns graus para a câmera e mantém o resultado; amplitude curta para não transformar E-03/E-04 em teste de física.
**Câmera base:** eye-level estática, perspectiva normal de smartphone, DOF moderada, framing UI-safe.  
**Luz base:** janela 45° suave + ambiente real fraco; pele e produto expostos sem clipping.  
**Riscos previstos:** identity `HIGH`, product morph `HIGH`, hand `MEDIUM`, continuity `HIGH`, physics `LOW/MEDIUM`.  
**Uso:** E-03 input matrix e E-04 UGC believability; useful E-05 identity/product mitigation.

**Acceptance anchors:** identidade canônica, rosto/cabelo/roupa, uma pessoa, uma mão ativa conforme referência, geometria/cor/face do produto, ambiente e direção de luz.

## Risk coverage

| Scene | LOW baseline | Hands | Product | Physics | Identity | Continuity | Primary experiments |
|---|---:|---:|---:|---:|---:|---:|---|
| GS-A | forte | none | low | none | none | low | controle negativo |
| GS-B | fraco | high | medium/high | medium | none | medium | E-05 core |
| GS-C | fraco | medium | high | high | none | high | E-01, E-02 |
| GS-D | fraco | medium | high | low/medium | high | high | E-03, E-04 |

## Scene freeze record

Antes de cada experimento, uma versão imutável deve registrar:

- golden scene ID/version e SKU/facts usados;
- reference asset IDs/hashes;
- exact initial/final state;
- environment anchors e prop count;
- camera/light baseline;
- action semantics e duration/aspect;
- risk profile previsto antes de observar outputs;
- lista de variáveis congeladas e única variável independente.

O golden template pode evoluir entre experimentos, mas nunca durante uma coorte. Mudança cria nova versão e invalida comparação direta com a anterior.
