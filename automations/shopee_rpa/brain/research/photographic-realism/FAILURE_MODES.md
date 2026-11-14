# Falhas e riscos

Capability: **Photographic Realism / assisted scene direction**. Não são defeitos automaticamente detectados pelo runtime. A taxonomia completa está em AI_TELLS.md.

| FAILURE | TRIGGER | IMPACT | EVIDENCE | DETECTION | MITIGATION | RESIDUAL_RISK |
|---|---|---|---|---|---|---|
| F01 Texture-as-realism | Pedir poros/grain sem câmera/luz | Aparência gravada, não integração | INFERRED S08/S13/S19 | Escala e material contraditórios | BP05/BP08 | Provider pode ignorar escopo local |
| F02 Identity drift | Pessoa da cena vira autoridade corporal | Nina muda corpo/rosto/idade | Instrução canônica do usuário | Comparar duas canônicas e política | BP10, recuperação existente | Regiões ocultas permanecem REVIEW |
| F03 Camera physics fail | “85 mm” em selfie impossível, telefone errado | Perspectiva/topologia incoerentes | DOCUMENTED S07/S14 + INFERRED risco | Alcançabilidade, escala, espelho | BP01 | Distância exata desconhecida sem calibração |
| F04 Cutout integration | Sujeito e fundo dirigidos separadamente | Luz/foco/apoio divergentes | INFERRED S03/atlas | Check integração | BP02/BP03/BP06 | Ajustes locais legítimos podem parecer distintos |
| F05 False AI diagnosis | Punir limpeza, simetria, HDR ou retoque | “Corrigir” foto válida, perder estilo | OBSERVED atlas, DOCUMENTED S12 | Exigir contradição específica | Não usar taxonomia como detector | Autenticidade não inferível só da aparência |
| F06 Fake exact reconstruction | Estimar EXIF/Kelvin com certeza | Direção e relatório inventados | OBSERVED conflito R02 | Conferir fonte, metadata e confiança | BP11 | EXIF também pode ser editado |
| F07 Global beautification | Grade dourado, sharpening/bloom geral | Material/pele mudam, cena genérica | DOCUMENTED S17/S20/S22; INFERRED | Halos/cor sem origem | BP07/BP09 | Preferência do público requer teste |
| F08 Prompt placebo | Módulo genérico apresentado como garantia | Sem melhoria demonstrada | UNKNOWN provider efficacy | Comparar pares/versionar | AB01–AB08 | Stochasticity/confounds |
| F09 Scope overwrite | Refazer foto aprovada ao adicionar texto | Perde pose/roupa/identidade | Instruções recentes do operador | Antes/depois e invariantes | Edit scope somente gráfico | Provider raster não garante pixels idênticos |
| F10 Evidence laundering | Pin não autenticado contado como foto comprovada | Conclusão baseada em origem incerta | UNKNOWN Pinterest | Proveniência/pixels distintos | Marcar P03/P04 secundárias | Autoria pode continuar desconhecida |
| F11 QA carried forward | Usar PASS de arquivo anterior após edição | Aprovação sem evidência | Política do projeto | Hash final versus review | BP12 | Nem toda região é visível |
| F12 A/B overclaim | Dez variáveis, seed inexistente, seleção favorável | Causalidade falsa | INFERRED método | Comparar inputs/registro de descartes | Pré-registro e relato de confounds | Pares qualitativos não dão generalização estatística |
