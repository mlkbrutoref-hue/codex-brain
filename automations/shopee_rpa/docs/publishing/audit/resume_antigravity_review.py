"""Recover an authorized Antigravity review via its official conversation CLI.

No Android connection, runtime modification or credential access. One serial turn.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONVERSATION = "a2f2534b-741c-4a7c-a74d-9cdeea45d74d"
AGY = Path(r"C:\Users\GAMER\AppData\Local\agy\bin\agy.exe")


def main():
    supplement = "--c14" in sys.argv[1:]
    prompt = (
        "Consolide agora o parecer independente da auditoria que voce ja inspecionou nesta conversa. "
        "Nao use nenhuma ferramenta, nao execute comandos, nao tente salvar arquivos, nao faca novas leituras. "
        "Retorne somente o texto final do parecer em portugues, ate 700 palavras, para o Codex salvar. "
        "Trate C02, C04, C05 e C14 com CONFIRMADO / CORRECAO_NECESSARIA / UNKNOWN, "
        "referencias de funcao/linha do codigo que voce realmente leu e limites da evidência. "
        "Avalie HIGH como exposicao contratual/operacional e nao probabilidade de banimento; "
        "diferencie controles propostos e implementados. Se algum ponto nao foi revisado, marque UNKNOWN. "
        "A restricao publica referenciada no relatorio e Shopee Video 4.1(g), e as propostas de piloto "
        "sao condicionais a interface autorizada ou operacao manual. Nao faca pesquisa adicional. "
        "A tarefa anterior expirou durante inspecao; precisamos apenas da conclusao textual com o contexto ja obtido."
    )
    if supplement:
        source = ROOT / "scripts/probe_shopee_android.py"
        lines = source.read_text(encoding="utf-8").splitlines()
        excerpt = "\n".join(f"{index + 1}: {line}" for index, line in enumerate(lines) if 86 <= index + 1 <= 109)
        prompt = (
            "Conclua somente o ponto C14 que ficou UNKNOWN no seu parecer. Nao use ferramentas ou comandos, "
            "nao faca novas leituras nem gravacao. O Codex fornece abaixo o trecho atual e literal de "
            "scripts/probe_shopee_android.py, linhas 86-109, SHA256 do arquivo completo: "
            + hashlib.sha256(source.read_bytes()).hexdigest() + ".\n\n" + excerpt + "\n\n"
            "Avalie exclusivamente se o bloqueio de publicacao por text protege tambem selecao por resourceId "
            "e se essa ferramenta tem a validacao/ledger do worker antes do clique. Declare CONFIRMADO / "
            "CORRECAO_NECESSARIA / UNKNOWN, citando as linhas, a limitacao de ser analise estatica e "
            "a correcao recomendada. Nao forneca comando para efetuar publicacao por essa lacuna. "
            "Nao execute testes ou acoes Android. Retorne parecer complementar em portugues ate 350 palavras."
        )
    started = datetime.now(timezone.utc).isoformat()
    arguments = [str(AGY), "--conversation", CONVERSATION, "-p", prompt,
                 "--output-format", "text", "--mode", "plan", "--sandbox",
                 "--print-timeout", "150s"]
    result = subprocess.run(arguments, cwd=ROOT, stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, encoding="utf-8", errors="replace",
                            timeout=180, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    body = result.stdout.strip()
    folder = Path(__file__).parent
    output = folder / ("antigravity-c14-2026-10-06.md" if supplement else "antigravity-review-2026-10-06.md")
    record = dict(conversation_id=CONVERSATION, method="official agy CLI conversation recovery",
                  started_at=started, completed_at=datetime.now(timezone.utc).isoformat(),
                  exit_code=result.returncode, output_characters=len(body),
                  independent_response_received=bool(body), credits_used=None)
    if result.returncode == 0 and body:
        output.write_text("# Parecer independente do Antigravity\n\n"
                          "Origem: resposta textual do CLI oficial agy, retomada da conversa "
                          + CONVERSATION + ". Salvamento realizado pelo Codex.\n\n" + body + "\n", encoding="utf-8")
        record.update(path=str(output), sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    else:
        record["delivery_status"] = "NO_VERIFIED_REVIEW_OUTPUT"
    (folder / ("antigravity-c14-recovery-2026-10-06.json" if supplement else "antigravity-recovery-2026-10-06.json")).write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))
    return 0 if result.returncode == 0 and body else 1


if __name__ == "__main__":
    raise SystemExit(main())
