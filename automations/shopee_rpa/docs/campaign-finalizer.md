# Campaign Finalizer / Ready-to-Post Packager

O finalizer recebe um `campaign_id`, lê os três manifests existentes, confere arquivos, hashes e QA, e cria `ready_to_post/campaign_<id>/`. Ele não gera nem edita imagens.

```powershell
python scripts/finalize_campaign.py e2e_full_content_factory_20260928_0955
```

Entradas obrigatórias dentro de `output/<campaign_id>/`:

- `manifests/campaign_manifest.json`;
- manifests de `carousel`, `product_stories` e `lifestyle_stories` referenciados pelo manifest da campanha;
- cada asset final e seu QA;
- `content/caption.txt`;
- `content/hashtags.txt`.

`content/posting_recommendation.json` é opcional. Sem ele, `recommended_time`, `confidence` e `evidence_type` ficam `UNKNOWN`, com motivo explícito. Valores aceitos para `evidence_type`: `OBSERVED_ACCOUNT_DATA`, `EXTERNAL_HEURISTIC`, `EDITORIAL_LOGIC`, `UNKNOWN`. Valores aceitos para `confidence`: `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`.

QA `REVIEW` exige `qa/user_approvals.json` ou `--approvals caminho.json` com registros vinculados aos hashes atuais:

```json
{
  "campaign_id": "example",
  "approvals": [
    {
      "asset_id": "product_story_01",
      "status": "APPROVED_BY_USER",
      "approved_by": "user",
      "approved_at": "2026-10-04T10:00:00-03:00",
      "reason": "Revisado visualmente e aceito.",
      "asset_sha256": "...",
      "qa_sha256": "..."
    }
  ]
}
```

Uma aprovação não substitui `FAIL`. Execuções idênticas reutilizam o pacote validado sem reescrever arquivos. Um pacote existente com fingerprint diferente nunca é sobrescrito silenciosamente.
