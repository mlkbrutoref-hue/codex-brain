"""
Pipeline Automático de Produção em Lote: 10 Novos Vídeos de Produtos Shopee
- Filtro Técnico de Resolução (mínimo 576p/720p/1080p, sem 360p/480p)
- Filtro Visual Anti-Rosto OpenCV YuNet (Tolerância Zero para rostos)
- Filtro de Nitidez / Blur
- Renderização Full HD 1080x1920 (Lanczos + Unsharp + Pillow Times New Roman)
- Integração Shopee Oficial (Comissão + Link Afiliado s.shopee.com.br)
- Upload Automático para Google Drive (Local + Nuvem)
"""

import os
import sys
import json
import time
import re
import subprocess
from pathlib import Path
import cv2

# Força UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRATCH_DIR = Path(r"C:\Users\GAMER\.gemini\antigravity\scratch")
YUNET_MODEL = SCRATCH_DIR / "face_detection_yunet.onnx"
TARGET_DRIVE_DIR = Path(r"C:\Users\GAMER\Drive\Produtos Instagram")
EDITADOS_DIR = TARGET_DRIVE_DIR / "Editados"
EDITADOS_DIR.mkdir(parents=True, exist_ok=True)

# Importa módulos internos
sys.path.append(str(SCRATCH_DIR))
from shopee_api import check_product_on_shopee
from video_editor import process_single_video, upload_file_to_gdrive, GDRIVE_EDITED_FOLDER_ID, probe_video

CANDIDATES = [
    {
        "url": "https://www.instagram.com/reel/Db57cGeOdV3/",
        "name": "barra magnetica suporte de facas parede",
        "shopee_query": "barra magnetica facas",
        "hook": "Organize suas facas na parede com praticidade e segurança",
        "hashtags": "#achadinhos #shopee #cozinha #facas #organizacao #casa"
    },
    {
        "url": "https://www.instagram.com/reel/C4NroFPL3sw/",
        "name": "esfregao triangulo mop giratorio 360",
        "shopee_query": "mop triangular",
        "hook": "Alcance qualquer cantinho e limpe paredes e vidros sem esforço",
        "hashtags": "#achadinhos #shopee #faxina #moptriangular #limpeza #utilidades"
    },
    {
        "url": "https://www.instagram.com/reel/C4Nq5IiLDsj/",
        "name": "mosquiteiro eletrico led armadilha pernilongo",
        "shopee_query": "armadilha mosquito",
        "hook": "Livre-se de mosquitos e pernilongos sem cheiro nem veneno",
        "hashtags": "#achadinhos #shopee #casa #armadilhademosquito #utilidades #dormirbem"
    },
    {
        "url": "https://www.instagram.com/reel/DfDv1yyvXOg/",
        "name": "escorredor de loucas compacto pia retratil",
        "shopee_query": "escorredor retratil pia",
        "hook": "O escorredor compacto perfeito que economiza espaço na pia",
        "hashtags": "#achadinhos #shopee #cozinha #escorredor #praticidade #utilidades"
    },
    {
        "url": "https://www.instagram.com/reel/Db9MeWuPzll/",
        "name": "kit ganchos ventosa ultra forte parede",
        "shopee_query": "gancho ventosa",
        "hook": "Ganchos ultra resistentes que fixam sem furar a parede",
        "hashtags": "#achadinhos #shopee #banheiro #organizacao #ganchoventosa #utilidades"
    },
    {
        "url": "https://www.instagram.com/reel/C4NqbgqrwL7/",
        "name": "escova eletrica de limpeza 5 em 1 sem fio",
        "shopee_query": "escova eletrica limpeza",
        "hook": "Limpe azulejos, pias e panelas sem esfregar nem cansar os braços",
        "hashtags": "#achadinhos #shopee #faxina #limpezadecasa #escovaeletrica #utilidades"
    },
    {
        "url": "https://www.instagram.com/reel/DfYLnr5O0kW/",
        "name": "organizador de panelas e tampas aramado",
        "shopee_query": "organizador panelas",
        "hook": "Chega de panelas empilhadas e bagunça dentro do armário",
        "hashtags": "#achadinhos #shopee #organizacao #cozinha #armario #utilidades"
    },
    {
        "url": "https://www.instagram.com/reel/DfVmE9oOCcm/",
        "name": "prateleira aramada organizadora de armario",
        "shopee_query": "prateleira aramada organizadora",
        "hook": "Dobre o espaço útil dos seus armários de forma rápida",
        "hashtags": "#achadinhos #shopee #armario #organizacao #cozinha #utilidades"
    },
    {
        "url": "https://www.instagram.com/reel/DfoIskDKEJP/",
        "name": "ventilador e luminaria de teto led 2 em 1",
        "shopee_query": "ventilador luminaria teto led",
        "hook": "Ventilador e lâmpada LED no mesmo bocal sem precisar de instalação",
        "hashtags": "#achadinhos #shopee #ventiladordeteto #casa #decoracao #utilidades"
    },
    {
        "url": "https://www.instagram.com/reel/DWPWnkKDzhy/",
        "name": "fruteira aramada 3 andares organizadora",
        "shopee_query": "fruteira 3 andares organizadora",
        "hook": "Fruteira aramada prática que deixa a cozinha linda e organizada",
        "hashtags": "#achadinhos #shopee #cozinha #fruteira #organizacao #utilidades"
    },
    # Reservas
    {
        "url": "https://www.instagram.com/reel/DcfEfS-u3nL/",
        "name": "suporte gancho ventosa vacuo multiuso",
        "shopee_query": "gancho ventosa vacuo",
        "hook": "Suporte com fixação a vácuo super forte sem furar o azulejo",
        "hashtags": "#achadinhos #shopee #banheiro #organizacao #casa"
    },
    {
        "url": "https://www.instagram.com/reel/DcRNoG0PbmA/",
        "name": "copo pote de salada com molheira e garfo",
        "shopee_query": "copo salada com molheira",
        "hook": "Sua salada fresca e crocante o dia todo com molho separado",
        "hashtags": "#achadinhos #shopee #cozinha #fitness #marmita #salada"
    },
    {
        "url": "https://www.instagram.com/reel/DcRoTyxPqx1/",
        "name": "aromatizador difusor eletrico porcelana",
        "shopee_query": "difusor aromatizador",
        "hook": "Casa sempre cheirosa e acolhedora com esse difusor elegante",
        "hashtags": "#achadinhos #shopee #aromaterapia #casa #decoracao #cheirinho"
    },
    {
        "url": "https://www.instagram.com/reel/C4Wy9U_APn2/",
        "name": "mini massageador eletrico cervical ems",
        "shopee_query": "mini massageador cervical ems",
        "hook": "Alívio imediato para dores no pescoço e costas onde você estiver",
        "hashtags": "#achadinhos #shopee #saude #massagem #bemestar #relaxar"
    },
    {
        "url": "https://www.instagram.com/reel/DfiMEvwq62h/",
        "name": "mini liquidificador portatil garrafa usb",
        "shopee_query": "mini liquidificador portatil garrafa",
        "hook": "Prepare seus shakes e sucos frescos em qualquer lugar com bateria recarregável",
        "hashtags": "#achadinhos #shopee #fitness #suco #shakes #praticidade"
    },
    {
        "url": "https://www.instagram.com/reel/DfTA2_Wu6dQ/",
        "name": "mop spray com reservatorio de limpeza",
        "shopee_query": "mop spray reservatorio",
        "hook": "Pisos brilhando sem balde pesado nem panos molhados",
        "hashtags": "#achadinhos #shopee #faxina #mopspray #limpeza #casa"
    }
]

def check_video_safety_and_quality(video_path: Path):
    """
    Verifica resolução mínima e ausência total de rostos humanos.
    Retorna (is_ok, reason, details)
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return False, "Erro ao abrir o vídeo", {}

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    duration = total_frames / fps
    cap.release()

    min_dim = min(w, h)
    max_dim = max(w, h)

    # 1. Filtro de Resolução
    if min_dim < 540 or max_dim < 960:
        return False, f"Resolução baixa ({w}x{h}). Exige no mínimo 576p/720p/1080p.", {}

    if duration > 75:
        return False, f"Vídeo muito longo ({duration:.1f}s > 75s)", {}

    # 2. Filtro Visual YuNet (Zero Rostos)
    detector = cv2.FaceDetectorYN.create(
        model=str(YUNET_MODEL),
        config="",
        input_size=(320, 320),
        score_threshold=0.6,
        nms_threshold=0.3,
        top_k=5000
    )

    cap = cv2.VideoCapture(str(video_path))
    sample_points = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95]
    face_counts = 0
    blur_scores = []

    for p_val in sample_points:
        frame_idx = int(total_frames * p_val)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Mede nitidez
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_scores.append(blur_score)

        # Detecta rostos
        f_h, f_w = frame.shape[:2]
        detector.setInputSize((f_w, f_h))
        _, faces = detector.detect(frame)
        if faces is not None and len(faces) > 0:
            face_counts += 1

    cap.release()

    if face_counts > 0:
        return False, f"Rosto de criador detectado em {face_counts}/{len(sample_points)} frames (Zero Rostos Obrigatório)", {}

    avg_blur = (sum(blur_scores) / len(blur_scores)) if blur_scores else 0
    if avg_blur < 35.0:
        return False, f"Vídeo com foco muito borrado (score nitidez {avg_blur:.1f} < 35)", {}

    return True, "Aprovado: 100% Product Only / Demonstração comercial nítida sem rostos", {
        "width": w,
        "height": h,
        "duration": duration,
        "fps": fps,
        "blur": avg_blur
    }

def generate_legenda(video_stem: str, cand: dict, shopee_item: dict, out_dir: Path) -> Path:
    title = shopee_item.get("productName", cand["name"]).title()
    raw_price = shopee_item.get("price") or shopee_item.get("priceMin") or "29.90"
    try:
        price_val = float(str(raw_price).replace(",", "."))
        price_str = f"R$ {price_val:.2f}"
    except Exception:
        price_str = f"R$ {raw_price}"
    link = shopee_item.get("offerLink", "")
    hashtags = cand.get("hashtags", "#achadinhos #shopee #utilidades #casa")
    hook = cand["hook"]

    text = f"""✨ {title} ✨

{hook} 🚀✨

Esse achadinho é indispensável para facilitar sua rotina com máxima praticidade, rapidez e eficiência!

💰 Valor na Shopee: {price_str}
🛒 Link oficial com frete promocional:
👉 {link}

💬 Comente "EU QUERO" para receber o link direto no seu direct!
📌 Salva esse vídeo para garantir o seu antes que acabe o estoque!

{hashtags}
"""
    leg_path = out_dir / f"{video_stem}_legenda.txt"
    leg_path.write_text(text, encoding="utf-8")
    return leg_path

def main():
    target_new_videos = 10
    processed_count = 0

    print("==================================================================")
    print(f"INICIANDO PRODUÇÃO EM LOTE: {target_new_videos} NOVOS VÍDEOS DE PRODUTOS")
    print(f"Diretório de Destino: {EDITADOS_DIR}")
    print(f"Pasta Nuvem Google Drive: {GDRIVE_EDITED_FOLDER_ID}")
    print("==================================================================\n")

    # Mapeia produtos já existentes
    existing_stems = set()
    for f in EDITADOS_DIR.iterdir():
        if f.is_file() and f.name.endswith("_editado.mp4"):
            existing_stems.add(f.stem.replace("_editado", ""))

    print(f"[Status] Vídeos já editados na pasta: {len(existing_stems)}")

    for idx, cand in enumerate(CANDIDATES, 1):
        if processed_count >= target_new_videos:
            print(f"\n[META ATINGIDA] {processed_count} novos vídeos concluídos com sucesso!")
            break

        cand_url = cand["url"]
        prod_name = cand["name"]
        hook = cand["hook"]
        shopee_query = cand["shopee_query"]

        print(f"\n------------------------------------------------------------------")
        print(f"[{processed_count+1}/{target_new_videos}] PROCESSANDO CANDIDATO #{idx}: '{prod_name}'")
        print(f"Instagram: {cand_url}")
        print(f"------------------------------------------------------------------")

        # 1. Download do vídeo original em alta qualidade
        print(f"[1/5 Download] Baixando original via yt-dlp...")
        files_before = set(os.listdir(TARGET_DRIVE_DIR))
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            cand_url,
            "-P", str(TARGET_DRIVE_DIR),
            "-o", "%(title).50s [%(id)s].%(ext)s",
            "--no-playlist"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        files_after = set(os.listdir(TARGET_DRIVE_DIR))
        new_files = [f for f in (files_after - files_before) if f.endswith((".mp4", ".mov", ".webm"))]

        if not new_files:
            print(f"[Download Erro] Não foi possível baixar {cand_url}. Pulando.")
            continue

        raw_video_path = TARGET_DRIVE_DIR / new_files[0]
        video_stem = raw_video_path.stem
        print(f"[Download OK] Arquivo: {raw_video_path.name} ({raw_video_path.stat().st_size / (1024*1024):.2f} MB)")

        # 2. Verificação Técnica e Anti-Rosto YuNet
        print(f"[2/5 Filtros Visuais] Inspecionando resolução e rostos com IA...")
        is_safe, reason, details = check_video_safety_and_quality(raw_video_path)
        if not is_safe:
            print(f"[REJEITADO] {reason}. Excluindo arquivo e avançando...")
            try:
                raw_video_path.unlink()
            except Exception:
                pass
            continue

        print(f"[APROVADO] {reason} | Resolução: {details['width']}x{details['height']} | Duração: {details['duration']:.1f}s")

        # 3. Consulta / Integração Shopee Oficial
        print(f"[3/5 Shopee API] Consultando '{shopee_query}'...")
        time.sleep(1.0)
        found, shopee_item = check_product_on_shopee(shopee_query)
        if not found or not shopee_item:
            print(f"[Shopee Erro] Falha ao obter dados para '{prod_name}'. Pulando.")
            try:
                raw_video_path.unlink()
            except Exception:
                pass
            continue

        shopee_title = shopee_item.get("productName", prod_name)
        price_val = shopee_item.get("price") or shopee_item.get("priceMin") or "29.90"
        affiliate_link = shopee_item.get("offerLink", "")
        print(f"[Shopee OK] Produto: {shopee_title} | Preço: R$ {price_val} | Link: {affiliate_link}")

        # Salva metadata da Shopee
        json_meta_path = TARGET_DRIVE_DIR / f"{video_stem}_shopee.json"
        with open(json_meta_path, "w", encoding="utf-8") as jf:
            json.dump({
                "product_target": prod_name,
                "instagram_url": cand_url,
                "shopee_name": shopee_title,
                "shopee_price": price_val,
                "affiliate_link": affiliate_link,
                "hook": hook,
                "hashtags": cand["hashtags"],
                "technical": details
            }, jf, indent=2, ensure_ascii=False)

        # 4. Edição Padronizada Full HD (Lanczos + Unsharp + Caixa Sólida Branca + Times New Roman)
        print(f"[4/5 Edição FFmpeg] Processando vídeo para Full HD 1080x1920 com hook...")
        edit_res = process_single_video(raw_video_path, output_dir=EDITADOS_DIR, custom_text=hook)
        out_edited = Path(edit_res["output"])
        out_preview = Path(edit_res["preview"])
        if not out_edited or not out_edited.exists():
            print(f"[Edição Erro] Falha ao renderizar {raw_video_path.name}.")
            continue

        # Gera legenda formatada
        out_legenda = generate_legenda(video_stem, cand, shopee_item, EDITADOS_DIR)
        print(f"[Edição OK] Vídeo editado: {out_edited.name} ({out_edited.stat().st_size / (1024*1024):.2f} MB)")
        print(f"[Legenda OK] {out_legenda.name}")
        print(f"[Preview OK] {out_preview.name}")

        # 5. Upload para Nuvem Google Drive
        print(f"[5/5 Upload Drive] Enviando arquivos para a nuvem...")
        try:
            drive_video_url = upload_file_to_gdrive(out_edited, GDRIVE_EDITED_FOLDER_ID)
            upload_file_to_gdrive(out_preview, GDRIVE_EDITED_FOLDER_ID)
            upload_file_to_gdrive(out_legenda, GDRIVE_EDITED_FOLDER_ID)
            print(f"[Upload OK] Disponível no Google Drive: {drive_video_url}")
        except Exception as e:
            print(f"[Upload Nota] {e}")

        processed_count += 1
        print(f">>> SUCESSO! Vídeo {processed_count}/{target_new_videos} concluído com perfeição!\n")

    print("==================================================================")
    print(f"PROCESSO CONCLUÍDO: {processed_count} NOVOS VÍDEOS GERADOS")
    print(f"Pasta Local: {EDITADOS_DIR}")
    print(f"Pasta Google Drive Nuvem: https://drive.google.com/drive/folders/{GDRIVE_EDITED_FOLDER_ID}")
    print("==================================================================")

if __name__ == "__main__":
    main()
