# Regras acionáveis

As regras físicas são estáveis; aplicação a prompts é INFERRED até execução. Validação é manual conforme REALISM CHECK, sem gate automático novo.

| RULE | SCOPE | EVIDENCE | RATIONALE | EXCEPTIONS_OR_LIMITS | VALIDATION |
|---|---|---|---|---|---|
| BP01 Fixar posição/distância de câmera e escala antes de focal/estilo | Pessoas/selfies/produtos | DOCUMENTED S07/S14 | Perspectiva deve fechar | Edição gráfica preserva câmera existente | Check perspectiva/escala; AB03 |
| BP02 Nomear fonte dominante e origem do fill | Cena fotográfica | DOCUMENTED S01–S03, INFERRED prompt | Uma luz comum conecta superfícies | Estúdio multifonte uniforme é válido | Check iluminação/sombras; AB01 |
| BP03 Revisar bloqueador, receptor e apoio, sem halo preto obrigatório | Contatos/sombras | DOCUMENTED física S02/S03, INFERRED aplicação | Ocultação/luz dependem do espaço | Transparência/fill podem enfraquecer sombra | Check contato; AB04 |
| BP04 Descrever acabamento oficial de cada material | Produtos/roupas | DOCUMENTED S04–S06/S11 | Mesmo campo, respostas diferentes | Material não conhecido permanece UNKNOWN | Check material/reflexo; AB07 |
| BP05 Limitar detalhe à escala/foco resolvidos | Pele/cabelo/tecido | DOCUMENTED S08–S11/S13; INFERRED direção | Detalhe uniforme pode contradizer captura | Macro/retoque controlado mudam aparência | Inspeção tamanho publicação e 100%; AB02 |
| BP06 Declarar foco e transição por profundidade | DOF | DOCUMENTED S13 | Blur não é recorte semântico | Modo retrato/stacking podem modificar | Check foco/bokeh; AB05 |
| BP07 Preservar hierarquia luminosa sem forçar clipping/grain | Exposição | DOCUMENTED S12/S18/S19 | HDR/denoise podem ser reais | Cena e pipeline determinam limites | Check exposição/processamento; AB06 |
| BP08 Condicionar imperfeição à causa, região e escala | Todas | INFERRED a partir de atlas/S15–S21 | Evitar decoração de defeitos | Pode haver zero imperfeições visíveis | Check óptica/textura; AB06 |
| BP09 Separar cor do objeto, luz, spill e grade | Cor | DOCUMENTED S17/S22, INFERRED direção | Paleta gráfica não deve laranjar pele | Grade intencional autorizado | Check cor; AB08 |
| BP10 Preservar autoridade Nina/produto/cena/estilo | Nina/post | Instrução do usuário e AGENTS | Referência de pose não redefine identidade | Provider com uma referência exige limitação registrada | QA canônicas/proporções/branding |
| BP11 Registrar desconhecido em vez de inventar parâmetros | Reverse analysis | OBSERVED conflito R02 | Problema inverso não único | EXIF/bastidores reais podem fornecer valor | Atlas e spec com classes de evidência |
| BP12 Revisar arquivo final por hash e corrigir apenas falha concreta | Pós-provider | Instrução do usuário/QA existente | Edição cria arquivo novo e risco novo | Máximo uma correção por tentativa Nina | REALISM CHECK e recovery existente |
