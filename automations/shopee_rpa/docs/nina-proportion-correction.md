# Correção das proporções da Nina — 26/09/2026

## Resultado e evidência

Política compartilhada de identidade/corpo/câmera integrada aos geradores lifestyle, Story de produto e PromptBuilder de cenas. Três fotografias novas foram produzidas pelo imagegen built-in do Codex com as duas referências canônicas. O runtime local não chama esse provider por conta própria.

Saídas e revisão estão em `output/nina_proportion_validation/`. Cada caso preserva solicitação, plano, prompt efetivamente enviado, original gerado, imagem-base, final 1080x1920, revisão semântica, QA, hashes e manifest. `correction_prompt_template.txt` demonstra o prompt de recuperação; o runtime o compõe com cena e defeitos reais.

## Diagnóstico

| Achado | Evidência local | Correção |
|---|---|---|
| Regras dispersas e descrição corporal genérica | PromptBuilder usava rosto e look 35mm; Story de produto usava apenas proporções genéricas; lifestyle tinha ajuste corporal isolado | Política única em proportion_rules.txt, consumida pelos três geradores |
| Cenas com close/diagonal sem distância | Biblioteca lifestyle pedia braço dobrado, close e diagonal sem limites concretos | Campos estruturados de câmera substituídos por distância e orientação adequadas a espelho, selfie direta ou telefone apoiado |
| Foto facial contém perspectiva de selfie próxima | Inspeção de persona_master; 360 contém vistas em pé | Rosto identifica a pessoa; 360 define a silhueta. Proibido copiar a geometria do close para corpo inteiro |
| QA anatômico genérico | Ausência dos sete códigos requeridos; resultado anterior permitia PASS com checks gerais | Sete checks obrigatórios nos dois pipelines estáticos e no VisualQAResult compartilhado |
| Revisão podia ser reutilizada em outro PNG | Estados sem vínculo com arquivo e referências | SHA-256 da imagem final e das duas referências; motivo explícito por check |
| Normalização aceitava recorte arbitrário | ImageOps.fit sem limite prévio | Bloqueio UNSAFE_BODY_CROP acima de 5% de área; escala uniforme preservada |
| Recuperação não tinha fluxo executável | Apenas instruções genéricas de regeneração | Pedido persistido, hooks de provider/reviewer, uma tentativa e reavaliação final |

A contribuição exata de lente, distância e condicionamento do modelo para os erros anteriores é uma hipótese plausível, não causalidade demonstrada. Três novas saídas não são um benchmark estatístico antes/depois. A pesquisa local anterior de câmera/distância está em `brain/research/visual-production/SOURCES.md` (S-CAMERA-02); não foi feita nova pesquisa externa nesta auditoria.

## Política e limites

- Mesma identidade facial, cabelo, tom de pele, idade aparente e silhueta reconhecível.
- Corpo slim-to-average, em linha com o 360 e o ajuste moderado pedido pelo usuário. Nenhuma redução progressiva a cada geração.
- Cabeça, tronco, cintura, quadris e membros coerentes; noção de lente principal de celular, sem ultra-wide/fisheye.
- Distâncias de 1.5–2 m ao espelho, 0.7–0.9 m para selfie direta e 1.8–2.5 m para celular apoiado são defaults de direção a validar visualmente, não metadados medidos da imagem gerada.
- Nenhum peso numérico de referência foi inventado: os dois arquivos são fornecidos e seus papéis declarados no prompt.
- O limite de recorte de 5% é uma escolha conservadora de engenharia; não detecta anatomia nem garante que todo recorte menor seja seguro. O final ainda precisa de inspeção.
- Anatomia escondida ou duvidosa exige REVIEW; ausência de espelho é registrada como não aplicável ao check de espelho. Os nomes terminam em FAIL para compatibilidade com o pedido: status PASS significa que aquele defeito não foi observado.

## QA e recuperação

`HEAD_BODY_RATIO_FAIL`, `TORSO_WIDTH_FAIL`, `WAIST_SHAPE_FAIL`, `LIMB_PROPORTION_FAIL`, `MIRROR_PERSPECTIVE_FAIL`, `BODY_IDENTITY_DRIFT` e `OVERWEIGHT_INTERPRETATION_FAIL` são checks qualitativos, sem score inventado.

Sem revisão válida: REVIEW / AWAITING_VISUAL_REVIEW. Defeito constatado: FAIL / REGENERATION_REQUIRED. Dúvida anatômica após inspeção: REVIEW / REGENERATION_REQUIRED. Nenhum desses casos entra como READY ou no histórico de aprovados.

A revisão é vinculada ao arquivo final e às duas referências. Hash é rastreabilidade, não prova independente de qualidade; o revisor continua responsável pela avaliação visual. O modelo local não mede anatomia automaticamente.

Os pipelines aceitam `correction_provider(prompt, reference_paths)` e `visual_reviewer(final_path, reference_paths)`. Com ambos, uma correção é gerada, normalizada, revisada e submetida a todos os gates. A primeira tentativa fica preservada e a nova fica em `correction_01`; `recovery_resolution.json` aponta o resultado. Sem callbacks, o agente Codex consome `anatomy_recovery.json` e usa imagegen. Não há loop contínuo de geração. Persistindo defeito após a tentativa, manter FAIL/REVIEW.

## Testes reais

1. `01_mirror`: selfie em pé no espelho, camiseta e jeans. PASS visual; cabeça/corpo equilibrados e pés presentes. Roupa limita avaliação exata do contorno das coxas.
2. `02_casual_selfie`: autorretrato lifestyle sentado, telefone apoiado com temporizador. PASS visual; mãos/pernas plausíveis; volume natural da pose sentada considerado. Não é selfie de braço estendido, que continua exigindo validação específica futura.
3. `03_routine`: rotina de café na cozinha, regata e shorts. PASS visual; cintura e membros comparáveis ao 360. Margem inferior pequena, porém pés presentes.

As avaliações foram feitas pelo agente sobre os três finais e ambas as referências; não são aprovação estética do usuário. Nenhum defeito anatômico bloqueante foi observado nestas três saídas; por isso não foi necessário um retry visual real. O caminho de recuperação foi exercitado em testes sintéticos de fluxo, sem fingir que imagens sintéticas comprovam qualidade visual.

## Arquivos e validação

Lista exata de criados/modificados: `output/nina_proportion_validation/files_changed.json`. O working tree já tinha alterações de outras tarefas; nenhum commit, reset ou limpeza foi feito.

Dry run: três planos válidos com política, referências e câmera. Suíte completa final: 106/106, sem falhas ou erros. Verificação registrada em `output/nina_proportion_validation/test_results.json`.

## Próximo passo

Usar esta política e o QA obrigatório nas próximas produções; ampliar o conjunto de validação com selfies de braço estendido, perfis e outras roupas sem substituir as referências canônicas por imagens geradas.
