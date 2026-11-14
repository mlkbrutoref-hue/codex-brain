"""Audit evidence only: no device connection, network access or runtime changes."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from PIL import Image
from app.mobile.shopee_video import Screen, ShopeeVideoPublisher, RpaError
from app.mobile.shopee_video import matching_product_rows, validation_checks
from app.media.ffmpeg.locator import FFmpegLocator


def main():
    report = {"scope": "OFFLINE_ONLY; synthetic reproductions are not Shopee behavior"}
    unrelated = Screen('<hierarchy><node package="com.shopee.br"><node text="Mochila esperada"/><node><node text="Outro produto"/><node text="Adicionar"/></node></node></hierarchy>')
    report["unrelated_single_add_match"] = matching_product_rows(unrelated, "mochila", "Mochila esperada")
    xml = '<hierarchy><node package="com.shopee.br" resource-id="com.shopee.br:id/iv_video_preview" bounds="[0,0][10,10]"/><node package="com.shopee.br" resource-id="com.shopee.br:id/et_caption" text="Descricao #mochila"/><node package="com.shopee.br" resource-id="com.shopee.br:id/tv_product_title" text="Mochila esperada"/><node package="com.shopee.br" resource-id="com.shopee.br:id/btn_post" enabled="true" clickable="true"/></hierarchy>'
    screen = Screen(xml)
    with tempfile.TemporaryDirectory() as temporary:
        config = dict(job_id="audit_first", serial="AUDIT_FAKE", video_sha256="a" * 64,
                      caption="Descricao", hashtags=["mochila"], video_path="/fake.mp4")
        image = Image.new("RGB", (10, 10), "gray")
        device = SimpleNamespace(shell=lambda command: SimpleNamespace(exit_code=0, output="a" * 64 + " /fake.mp4"), screenshot=lambda: image)
        worker = ShopeeVideoPublisher(device, config, temporary)
        worker.observe = lambda: screen
        worker.session["selection_evidence"] = dict(files=[], visual_preview_reviewed=False,
            preview_pixel_sha256=hashlib.sha256(image.tobytes()).hexdigest())
        media_ok = worker.media_matches()
        report["unreviewed_preview"] = dict(visual_preview_reviewed=False, media_matches=media_ok,
            validation=validation_checks(screen, worker.expected_caption, "Mochila esperada", media_ok, True))
        worker.reserve_attempt()
        second = ShopeeVideoPublisher(device, dict(config, job_id="audit_second"), temporary)
        actions = []
        second.observe = lambda: screen
        second.checkpoint = lambda *args, **kwargs: None
        second.select_media = lambda: actions.append("select_media")
        second.fill_caption = lambda: actions.append("fill_caption")
        second.select_product = lambda: actions.append("select_product")
        second.ensure_shopee_only = lambda: actions.append("ensure_shopee_only")
        second.publish = second.reserve_attempt
        try:
            second.run_prepared(publish=True)
        except RpaError as error:
            report["previous_attempt_new_job"] = dict(actions_before_block=actions, error=str(error))
    source_files = ["app/mobile/shopee_video.py", "app/mobile/discovery.py",
        "scripts/publish_shopee_android.py", "scripts/probe_shopee_android.py",
        "scripts/research_shopee_hashtags.py", "scripts/prepare_shopee_android_resume.py",
        "app/providers/shopee/client.py", "app/providers/shopee/live.py",
        "app/providers/shopee/queries.py", "scripts/execute_kbeauty_research.py",
        "scripts/research_bolsas_shopee.py", "app/validation/media.py",
        "app/platforms/shopee_video/exporter.py", "app/publishing/assisted.py",
        "tests/publishing/test_shopee_android.py", "tests/publishing/test_assisted.py"]
    report["source_sha256"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_files}
    session_path = ROOT / "debug/shopee_android/shopee_android_usb_20261006_01/session.json"
    session = json.loads(session_path.read_text(encoding="utf-8"))
    report["recorded_attempt"] = {key: session.get(key) for key in
        ("job_id", "state", "publish_attempted", "profile_return_observed", "publication_confirmation", "validation")}
    report["recorded_attempt"]["last_error"] = session["transitions"][-1]["error"]
    report["recorded_attempt"]["session_sha256"] = hashlib.sha256(session_path.read_bytes()).hexdigest()
    report["user_reported_success"] = "User stated 'Ok mano deu tudo'; external post ID and exact content not independently reconciled."
    media = ROOT / "debug/shopee_android/latest_product_video.mp4"
    binary = FFmpegLocator(ROOT).resolve("ffprobe")
    report["media_probe"] = {"status": "NOT_EXECUTED", "reason": "FFPROBE_NOT_FOUND"}
    if binary and media.is_file():
        result = subprocess.run([str(binary), "-v", "error", "-show_entries",
            "stream=codec_type,codec_name,width,height,avg_frame_rate,bit_rate:format=duration,size,bit_rate",
            "-of", "json", str(media)], capture_output=True, text=True, timeout=30, check=True)
        report["media_probe"] = dict(status="OBSERVED_LOCAL_FILE", sha256=hashlib.sha256(media.read_bytes()).hexdigest(), metadata=json.loads(result.stdout))
    destination = Path(__file__).with_name("offline-evidence-2026-10-06.json")
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
