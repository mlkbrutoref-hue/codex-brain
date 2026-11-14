# Single Story Rendering — Failure Modes

| Falha | Sinal | Resposta |
|---|---|---|
| Texto gerado dentro da foto | erros ortográficos ou palavras extras | pedir base sem texto e compor localmente |
| Overflow | bbox sai da zona | reduzir dentro do limite ou `TEXT_LAYOUT_FAIL` |
| Fonte ilegível | tamanho abaixo do mínimo | falhar e encurtar/reformular a copy no pacote |
| Contraste baixo | ratio abaixo do alvo | escolher outra cor, backdrop ou caixa |
| Produto coberto | overlay invade atributo essencial | mover ou reduzir componente; manter a base |
| Provider ignora safe zone | produto ocupa área reservada | adaptar layout; edição localizada; regenerar por último |
| Produto deformado | forma/cor/rótulo divergem | `FAIL`; editar localmente ou regenerar base |
| QA sem inspeção | checks semânticos ausentes | resultado `REVIEW`, nunca `PASS` automático |
| Fonte ausente | arquivo TrueType não existe | falhar com mensagem explícita |
| Correção cara | regeneração por erro de copy | rerenderizar apenas overlay e final |
