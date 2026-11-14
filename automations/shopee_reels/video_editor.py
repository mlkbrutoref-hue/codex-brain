r"""
Automação de Edição de Vídeos de Produtos (Etapa 3)
Substituição de frase sobreposta por retângulo branco sólido com texto preto centralizado.
Tecnologias: FFmpeg + FFprobe + Pillow (Times New Roman) + Upload Automático para o Google Drive.

Garante compatibilidade total com celular:
- MP4 H.264 High Profile, yuv420p, avc1
- Áudio AAC-LC 48kHz 256k (se houver áudio original)
- Faststart habilitado
- CRF 10 (alta fidelidade visual)
- Verificação de integridade pós-exportação (FFprobe + decodificação nula)
- Upload automático para o Google Drive na nuvem com link de acesso imediato.
"""

import os
import re
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

# Garante saída UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Caminhos padrão do sistema
WINDOWS_FONT_TIMES = r"C:\Windows\Fonts\times.ttf"
DEFAULT_LOCAL_DIR = r"C:\Users\GAMER\Drive\Produtos Instagram"
DEFAULT_OUTPUT_DIR = r"C:\Users\GAMER\Drive\Produtos Instagram\Editados"

# IDs Oficiais no Google Drive na Nuvem (diogob.sousa1@gmail.com)
GDRIVE_MAIN_FOLDER_ID = "1Cz9pi-M_Ukb4Jvgd4QKM1ooTEB_arlns"     # Produtos Instagram
GDRIVE_EDITED_FOLDER_ID = "1gUoigEzQ_zTSCGhKE5BqIdKG4OKyKKk-"   # Editados

def get_binary_paths() -> Tuple[str, str]:
    custom_ffmpeg = r"C:\Users\GAMER\Documents\Codex\2026-08-30\files-pasted-by-the-user-projeto\work\tools\ffmpeg\ffmpeg.exe"
    custom_ffprobe = r"C:\Users\GAMER\Documents\Codex\2026-08-30\files-pasted-by-the-user-projeto\work\tools\ffmpeg\ffprobe.exe"
    ffmpeg_bin = shutil.which("ffmpeg") or (custom_ffmpeg if os.path.exists(custom_ffmpeg) else "ffmpeg")
    ffprobe_bin = shutil.which("ffprobe") or (custom_ffprobe if os.path.exists(custom_ffprobe) else "ffprobe")
    return ffmpeg_bin, ffprobe_bin

FFMPEG_BIN, FFPROBE_BIN = get_binary_paths()

PRODUCT_HOOK_TEMPLATES = {
    "amassador de alho inox": "O segredo do alho picadinho sem esforço nem cheiro na mão",
    "mini selador de embalagens": "Nunca mais perca comida com pacote aberto na despensa",
    "dispenser de detergente": "Sua pia limpa e organizada com apenas um toque",
    "mini processador triturador": "Pique temperos em segundos sem sujar nenhuma tábua",
    "cortador e ralador de legumes": "Corte legumes perfeitos na velocidade da luz",
    "skincare": "POV: seu próximo desejo de skincare é esse aqui",
    "banho": "Agora meu banho tem um toque de spa",
    "padrao": "Essa novidade prática vai transformar a sua rotina"
}

def probe_video(file_path: Path) -> Dict[str, Any]:
    """Inspeciona o arquivo com ffprobe (mesmo sem extensão) e retorna metadados."""
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_entries",
        "stream=codec_type,codec_name,width,height,duration,avg_frame_rate,bit_rate:format=duration,format_name",
        "-of", "json",
        str(file_path.resolve())
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise ValueError(f"FFprobe falhou ao inspecionar '{file_path}': {res.stderr}")

    data = json.loads(res.stdout)
    streams = data.get("streams", [])
    format_info = data.get("format", {})

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not video_stream:
        raise ValueError(f"O arquivo '{file_path}' não contém faixa de vídeo válida.")

    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    orientation = "portrait" if height >= width else "landscape"

    fps_raw = video_stream.get("avg_frame_rate", "30/1")
    if "/" in fps_raw:
        num, den = fps_raw.split("/")
        fps = round(float(num) / float(den), 2) if float(den) != 0 else 30.0
    else:
        fps = float(fps_raw) if fps_raw else 30.0

    duration = float(format_info.get("duration") or video_stream.get("duration") or 0.0)

    return {
        "path": file_path,
        "width": width,
        "height": height,
        "orientation": orientation,
        "fps": fps,
        "duration": duration,
        "has_audio": audio_stream is not None,
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
        "format": format_info.get("format_name")
    }

def calculate_overlay_box(width: int, height: int, manual_box: Optional[str] = None) -> Tuple[int, int, int, int, int]:
    if manual_box:
        try:
            parts = [int(p.strip()) for p in manual_box.split(",")]
            if len(parts) == 4:
                x, y, w, h = parts
                font_size = max(16, int(h * 0.28))
                return x, y, w, h, font_size
        except Exception:
            print(f"[Aviso] Coordenadas manuais inválidas '{manual_box}', usando cálculo automático.")

    scale = width / 720.0
    box_w = int(round(616 * scale))
    box_h = int(round(158 * scale))
    box_x = int(round((width - box_w) / 2))
    box_y = int(round(232 * (height / 1280.0)))
    font_size = int(round(44 * scale))

    box_w = min(box_w, width - 20)
    box_x = max(10, box_x)
    box_y = max(10, min(box_y, height - box_h - 10))

    return box_x, box_y, box_w, box_h, font_size

def resolve_new_phrase(custom_text: Optional[str], video_meta: Dict[str, Any], json_metadata_path: Optional[Path]) -> str:
    if custom_text and custom_text.strip():
        return custom_text.strip()

    if json_metadata_path and json_metadata_path.exists():
        try:
            with open(json_metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                target = data.get("product_target", "").lower()
                for key, hook in PRODUCT_HOOK_TEMPLATES.items():
                    if key in target or target in key:
                        return hook
                caption = data.get("caption", "").lower()
                for key, hook in PRODUCT_HOOK_TEMPLATES.items():
                    if key in caption:
                        return hook
        except Exception:
            pass

    return PRODUCT_HOOK_TEMPLATES["padrao"]

def wrap_text_into_lines(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    words = text.split()
    if not words:
        return [""]

    bbox_single = draw.textbbox((0, 0), text, font=font)
    if (bbox_single[2] - bbox_single[0]) <= max_width:
        if len(words) <= 4:
            return [text]

    mid = len(words) // 2
    best_split = [ " ".join(words[:mid]), " ".join(words[mid:]) ]
    
    w1 = draw.textbbox((0, 0), best_split[0], font=font)[2]
    w2 = draw.textbbox((0, 0), best_split[1], font=font)[2]
    
    if max(w1, w2) <= max_width:
        return best_split

    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        w = draw.textbbox((0, 0), test_line, font=font)[2]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_overlay_png(width: int, height: int, text: str, box_x: int, box_y: int, box_w: int, box_h: int, initial_font_size: int, output_png: Path) -> Path:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    rect_box = [box_x, box_y, box_x + box_w, box_y + box_h]
    draw.rectangle(rect_box, fill=(255, 255, 255, 255), outline=None)

    font_size = initial_font_size
    font = None
    font_candidates = [
        WINDOWS_FONT_TIMES,
        r"C:\Windows\Fonts\timesbd.ttf",
        r"C:\Windows\Fonts\arial.ttf"
    ]
    for fc in font_candidates:
        if os.path.exists(fc):
            try:
                font = ImageFont.truetype(fc, font_size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    padding_x = int(box_w * 0.06)
    padding_y = int(box_h * 0.10)
    max_text_w = box_w - (padding_x * 2)
    max_text_h = box_h - (padding_y * 2)

    lines = []
    for sz in range(font_size, max(14, int(font_size * 0.55)), -2):
        try:
            curr_font = ImageFont.truetype(WINDOWS_FONT_TIMES, sz) if os.path.exists(WINDOWS_FONT_TIMES) else font
        except Exception:
            curr_font = font
        lines = wrap_text_into_lines(text, curr_font, max_text_w, draw)
        
        line_heights = []
        line_widths = []
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=curr_font)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])
        
        line_spacing = int(sz * 0.3)
        total_text_h = sum(line_heights) + (len(lines) - 1) * line_spacing
        total_text_w = max(line_widths) if line_widths else 0

        if total_text_w <= max_text_w and total_text_h <= max_text_h:
            font = curr_font
            break

    line_bboxes = [draw.textbbox((0, 0), l, font=font) for l in lines]
    line_heights = [b[3] - b[1] for b in line_bboxes]
    line_widths = [b[2] - b[0] for b in line_bboxes]
    line_spacing = int(font.size * 0.25) if hasattr(font, "size") else 6
    total_h = sum(line_heights) + (len(lines) - 1) * line_spacing

    curr_y = box_y + (box_h - total_h) / 2
    for l, lw, lh, b in zip(lines, line_widths, line_heights, line_bboxes):
        curr_x = box_x + (box_w - lw) / 2
        draw.text((curr_x - b[0], curr_y - b[1]), l, font=font, fill=(0, 0, 0, 255))
        curr_y += lh + line_spacing

    img.save(str(output_png), "PNG")
    return output_png

def export_edited_video(input_path: Path, overlay_png: Path, output_path: Path, has_audio: bool) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Filtro de qualidade máxima:
    # 1. Upscale/conformidade para 1080x1920 (9:16) via Lanczos de alta fidelidade
    # 2. Realce de nitidez de bordas (unsharp) para destacar detalhes do produto
    # 3. Ajuste sutil de contraste e saturação para cores mais vibrantes no feed
    # 4. Sobreposição da caixa branca e texto vetorial Full HD
    filter_complex = (
        "[0:v:0]scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,"
        "unsharp=lx=5:ly=5:la=0.6:cx=3:cy=3:ca=0.3,"
        "eq=contrast=1.03:saturation=1.05[base];"
        "[base][1:v:0]overlay=0:0:format=yuv420[v]"
    )

    cmd = [
        FFMPEG_BIN,
        "-hide_banner",
        "-y",
        "-i", str(input_path.resolve()),
        "-i", str(overlay_png.resolve()),
        "-filter_complex", filter_complex,
        "-map", "[v]"
    ]

    if has_audio:
        cmd.extend([
            "-map", "0:a:0?",
            "-c:a", "aac",
            "-profile:a", "aac_low",
            "-ar", "48000",
            "-b:a", "256k"
        ])
    else:
        cmd.extend(["-an"])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "10",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-tag:v", "avc1",
        "-movflags", "+faststart",
        str(output_path.resolve())
    ])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Erro no FFmpeg ao exportar o vídeo: {res.stderr}")

    return output_path

def verify_output_video(output_path: Path, expected_duration: float) -> Tuple[bool, str]:
    if not output_path.exists() or output_path.stat().st_size == 0:
        return False, "Arquivo exportado não existe ou está vazio."

    try:
        info = probe_video(output_path)
    except Exception as e:
        return False, f"Falha na validação com FFprobe: {e}"

    if info["width"] == 0 or info["height"] == 0:
        return False, "Vídeo sem resolução válida."

    test_cmd = [
        FFMPEG_BIN,
        "-v", "error",
        "-i", str(output_path.resolve()),
        "-f", "null",
        "-"
    ]
    res_test = subprocess.run(test_cmd, capture_output=True, text=True)
    if res_test.returncode != 0:
        return False, f"Erro de decodificação no arquivo final: {res_test.stderr}"

    return True, f"OK: {info['width']}x{info['height']}, {info['duration']:.2f}s, Codec {info['video_codec']}"

def extract_preview_frame(video_path: Path, preview_path: Path, timestamp: float = 1.5) -> Path:
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-ss", str(timestamp),
        "-i", str(video_path.resolve()),
        "-vframes", "1",
        "-q:v", "2",
        str(preview_path.resolve())
    ]
    subprocess.run(cmd, capture_output=True)
    return preview_path

def upload_file_to_gdrive(local_file: Path, parent_id: str) -> Optional[str]:
    """Envia o arquivo para o Google Drive na nuvem via CLI oficial gdrive."""
    try:
        gdrive_cmd = shutil.which("gdrive") or "gdrive.cmd"
        res = subprocess.run(
            [gdrive_cmd, "mutate", "upload", str(local_file.resolve()), "--parent", parent_id],
            capture_output=True, text=True, shell=True
        )
        if res.returncode == 0:
            match = re.search(r"\(ID:\s*([^\)]+)\)", res.stdout)
            if match:
                file_id = match.group(1).strip()
                return f"https://drive.google.com/file/d/{file_id}/view"
    except Exception as e:
        print(f"[Upload Google Drive] Nota: {e}")
    return None

def process_single_video(
    video_path: Path,
    output_dir: Path,
    custom_text: Optional[str] = None,
    manual_box: Optional[str] = None,
    upload_gdrive: bool = True
) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"PROCESSANDO VÍDEO: {video_path.name}")
    print(f"=======================================================")

    print(f"[1] Sondando características originais com FFprobe...")
    meta = probe_video(video_path)
    print(f"    - Resolução: {meta['width']}x{meta['height']} ({meta['orientation']})")
    print(f"    - Duração: {meta['duration']:.2f}s | FPS: {meta['fps']} | Áudio: {'Sim' if meta['has_audio'] else 'Não'}")

    json_path = video_path.parent / (video_path.stem + "_shopee.json")
    if not json_path.exists():
        json_path = None

    print(f"[2] Definindo a nova frase em português...")
    phrase = resolve_new_phrase(custom_text, meta, json_path)
    print(f"    - Frase selecionada: \"{phrase}\"")

    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    bx, by, bw, bh, fsize = calculate_overlay_box(TARGET_WIDTH, TARGET_HEIGHT, manual_box)
    print(f"[3] Coordenadas da caixa branca (Full HD 1080x1920): x={bx}, y={by}, w={bw}, h={bh} | Fonte: {fsize}px")

    temp_dir = Path(r"C:\Users\GAMER\.gemini\antigravity\scratch\temp_edit")
    temp_dir.mkdir(parents=True, exist_ok=True)
    overlay_png = temp_dir / f"overlay_{video_path.stem}.png"
    print(f"[4] Desenhando overlay em Full HD com Pillow (Times New Roman)...")
    create_overlay_png(TARGET_WIDTH, TARGET_HEIGHT, phrase, bx, by, bw, bh, fsize, overlay_png)

    output_name = f"{video_path.stem}_editado.mp4"
    output_video_path = output_dir / output_name
    print(f"[5] Exportando vídeo editado via FFmpeg (Full HD 1080x1920, Lanczos, Unsharp, H.264 High, CRF 10)...")
    export_edited_video(video_path, overlay_png, output_video_path, meta["has_audio"])
    out_size_mb = output_video_path.stat().st_size / (1024 * 1024)
    print(f"    - Arquivo salvo: {output_video_path} ({out_size_mb:.2f} MB)")

    print(f"[6] Realizando conferência de integridade com FFprobe e decodificação total...")
    valid, msg = verify_output_video(output_video_path, meta["duration"])
    if not valid:
        print(f"    [ERRO DE VALIDAÇÃO] {msg}")
    else:
        print(f"    [VALIDAÇÃO APROVADA] {msg}")

    preview_path = output_dir / f"{video_path.stem}_preview.jpg"
    extract_preview_frame(output_video_path, preview_path, timestamp=min(2.0, meta["duration"] / 2))
    print(f"    - Quadro de preview salvo em: {preview_path}")

    # Upload automático para o Google Drive na nuvem
    gdrive_link = None
    if upload_gdrive and valid:
        print(f"[7] Enviando para o Google Drive na Nuvem (Pasta 'Editados')...")
        gdrive_link = upload_file_to_gdrive(output_video_path, GDRIVE_EDITED_FOLDER_ID)
        if gdrive_link:
            print(f"    - Link no Google Drive: {gdrive_link}")
        upload_file_to_gdrive(preview_path, GDRIVE_EDITED_FOLDER_ID)

    if json_path and json_path.exists():
        dest_json = output_dir / f"{output_video_path.stem}_shopee.json"
        shutil.copy2(json_path, dest_json)
        if upload_gdrive:
            upload_file_to_gdrive(dest_json, GDRIVE_EDITED_FOLDER_ID)

    return {
        "input": str(video_path),
        "output": str(output_video_path),
        "preview": str(preview_path),
        "phrase": phrase,
        "box": {"x": bx, "y": by, "w": bw, "h": bh},
        "verified": valid,
        "size_mb": out_size_mb,
        "width": meta["width"],
        "height": meta["height"],
        "duration": meta["duration"],
        "gdrive_link": gdrive_link or f"https://drive.google.com/drive/folders/{GDRIVE_EDITED_FOLDER_ID}"
    }

def main():
    parser = argparse.ArgumentParser(description="Automação de Edição de Vídeos de Produtos com FFmpeg, Pillow e Google Drive")
    parser.add_argument("--input", "-i", type=str, help="Caminho de um arquivo de vídeo ou de uma pasta com vídeos.")
    parser.add_argument("--text", "-t", type=str, help="Frase personalizada para substituir a original.")
    parser.add_argument("--box", "-b", type=str, help="Coordenadas manuais da caixa no formato 'x,y,w,h'.")
    parser.add_argument("--output-dir", "-o", type=str, default=DEFAULT_OUTPUT_DIR, help="Pasta de destino local.")
    parser.add_argument("--no-upload", action="store_true", help="Desativa o envio automático para o Google Drive.")
    args = parser.parse_args()

    input_target = Path(args.input) if args.input else Path(DEFAULT_LOCAL_DIR)
    out_dir = Path(args.output_dir)

    videos_to_process = []
    if input_target.is_file():
        videos_to_process.append(input_target)
    elif input_target.is_dir():
        for f in input_target.iterdir():
            if f.is_file() and not f.name.endswith(("_editado.mp4", "_preview.jpg", ".json")):
                try:
                    probe_video(f)
                    videos_to_process.append(f)
                except Exception:
                    pass

    if not videos_to_process:
        print(f"[Aviso] Nenhum vídeo encontrado para processar em '{input_target}'.")
        return

    print(f"Encontrados {len(videos_to_process)} vídeos para editar.")
    results = []
    for vid in videos_to_process:
        try:
            res = process_single_video(vid, out_dir, args.text, args.box, upload_gdrive=not args.no_upload)
            results.append(res)
        except Exception as e:
            print(f"[Erro ao processar {vid.name}]: {e}")

    print("\n" + "=" * 55)
    print("RELATÓRIO DE PROCESSAMENTO DA ETAPA 3")
    print("=" * 55)
    for r in results:
        print(f"- Vídeo Original: {Path(r['input']).name}")
        print(f"  Vídeo Editado (Local): {r['output']} ({r['size_mb']:.2f} MB)")
        print(f"  Link no Google Drive: {r['gdrive_link']}")
        print(f"  Nova Frase: \"{r['phrase']}\"")
        print(f"  Status de Reprodução e Integridade: {'Aprovado' if r['verified'] else 'Falhou'}")
        print("-" * 55)

if __name__ == "__main__":
    main()
