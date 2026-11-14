"""Record the paused campaign's manual reference research; never generates assets."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / 'output/e2e_content_factory_test_20260927_1505'
R = ROOT / 'references'
NOW = datetime.now(timezone.utc).isoformat()
if (C / 'REFERENCE_CHECKPOINT.json').exists():
    raise SystemExit('Checkpoint já registrado; preservar evidências. Não executar novamente.')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Capture every pre-existing campaign file BEFORE adding checkpoint sidecars.
baseline = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in C.rglob('*') if p.is_file()}
write(C / 'qa/pre_reference_preservation_baseline.json', {'captured_at': NOW, 'files': baseline})

refs = []
def ref(rid, source, path, category, camera, light, composition, pose, environment, why, url=None, image_url=None, limits=None):
    p = ROOT / path
    record = dict(reference_id=rid, source=source, source_url=url, image_url=image_url,
        date_collected=NOW, date_note='Data de registro nesta biblioteca; não é data de publicação.',
        local_path=path, sha256=sha(p), category=category,
        asset_type=['photographic_scene_reference'] if source == 'Pinterest' else ['user_style_reference'],
        priority='SCENE_SECONDARY' if source == 'Pinterest' else 'USER_PRIMARY',
        visual_style='Fotografia doméstica/editorial feminina; ver análise específica.',
        camera=camera, lighting=light, composition=composition, pose=pose, environment=environment,
        why_selected=why, review_status='VISUALLY_INSPECTED', reviewed_at=NOW,
        authenticity='Aparência fotográfica observada; origem/câmera e ausência de IA não autenticadas.' if source == 'Pinterest' else 'Exemplo enviado pelo usuário; autoridade de estilo, não prova de fotografia real.',
        usage='Direção e consulta interna; não publicar nem copiar pixels, identidade, texto, marcas ou watermark.',
        limitations=limits or [])
    refs.append(record)

ref('P01_MIRROR', 'Pinterest', 'references/pinterest/beauty/mirror.jpg', ['carousel_covers','lifestyle/mirror','product_scenes/beauty'],
    'Selfie de espelho vertical, celular ao lado do rosto, corte acima da cintura.', 'Luz doméstica suave, neutra/quente, granulação visível.',
    'Rosto na metade superior, parede simples, robe preenchendo a base.', 'Sentada/frontal, uma mão segura o telefone.', 'Banheiro neutro.',
    'Lógica de celular e fundo simples compatíveis com a capa enviada pelo usuário.',
    'https://uk.pinterest.com/pin/mirror-selfie--794111346795483355/',
    'https://i.pinimg.com/736x/6d/1a/e1/6d1ae12a3ea489fbccd31feb8a9c4db9.jpg',
    ['Adaptar para 3:4 com espaço de headline; não copiar cabelo, rosto ou corpo da pessoa.'])
ref('P02_VANITY', 'Pinterest', 'references/pinterest/beauty/vanity.jpg', ['carousel_cta','product_scenes/beauty','product_scenes/organization'],
    'Vertical, câmera oblíqua ligeiramente acima da bancada.', 'Lâmpadas de espelho e ambiente difuso.',
    'Objetos em alturas diferentes sobre bandeja; reflexo cria profundidade.', 'Sem pessoa.', 'Penteadeira branca com rosa e objetos de uso diário.',
    'Fundo fotográfico de fechamento e hierarquia de objetos; compatível com paleta Nina.',
    'https://www.pinterest.com/pin/my-absolute-favorite--1759287346258436/',
    'https://i.pinimg.com/originals/29/21/3d/29213d9c13396c44559fb4bbbb04d211.jpg',
    ['Página do Pin retornou 403; vínculo Pin/imagem encontrado em busca de imagens e arquivo inspecionado.', 'Reduzir decoração e substituir cosméticos de marcas por produtos oficiais da campanha.'])
ref('P03_GRWM', 'Pinterest', 'references/pinterest/beauty/grwm.jpg', ['product_scenes/beauty','compositions'],
    'Vertical, oblíqua para baixo, bancada em diagonal.', 'Lâmpadas quentes com ambiente mais frio.',
    'Objetos de uso na frente, espelho ao lado, área de parede no alto.', 'Sem pessoa física; tela mostra tutorial.', 'Penteadeira com quarto refletido.',
    'Organização vivida e camadas espaciais para produtos internos e Story de espelho.',
    'https://in.pinterest.com/pin/980307043884292108/',
    'https://i.pinimg.com/736x/09/0b/20/090b2076dd788fed6d5f84b8186727c9.jpg',
    ['Não copiar vídeo, pessoa na tela, neon, marcas ou layout exato; retirar tablet na adaptação.'])
ref('P04_MORNING', 'Pinterest', 'references/pinterest/morning/coffee.jpg', ['lifestyle/morning'],
    'Plano aberto horizontal, câmera externa, altura aproximada do tronco.', 'Janela lateral quente.',
    'Pessoa à direita, cozinha e bancada à esquerda.', 'Em pé apoiada na bancada, caneca nas duas mãos.', 'Cozinha doméstica.',
    'Ação simples e luz matinal compatíveis com a manhã já planejada.',
    'https://in.pinterest.com/pin/happy-young-woman-drinking-morning-coffee-in-kitchen-by-prostockstudios-photos-ad-ad-woman-young-happy-dri--678776975069075092/',
    'https://i.pinimg.com/736x/e7/aa/b4/e7aab4dc463d27f8391a46a0168c9598.jpg',
    ['Prévia stock com watermark Envato, mantida intacta; somente direção, sem reutilização de pixels.', 'Não é selfie; adaptar como foto casual com temporizador em 9:16, sem copiar cenário rústico.'])
ref('P05_AFTERNOON', 'Pinterest', 'references/pinterest/afternoon/desk.jpg', ['lifestyle/afternoon'],
    'Plano médio/aberto horizontal, câmera externa oblíqua à mesa.', 'Janela lateral difusa.',
    'Pessoa à direita, laptop e mesa diagonal à esquerda.', 'Sentada, mão apoiada na cabeça e outra na caneca.', 'Mesa de estudos com planta.',
    'Ação de pausa e profundidade real de mesa úteis à rotina da tarde.',
    'https://in.pinterest.com/pin/young-tired-student-woman-study-online-at-home-with-laptop-in-the-morning-with-cup-of-coffee-young-student-woman-study--469148486180506981/',
    'https://i.pinimg.com/736x/c7/f2/06/c7f2064b7a16fc508c919da8a578e9a7.jpg',
    ['Prévia atribuída a Maria Kovalevskaya/500px, watermark preservado; direção apenas.', 'Foto stock: reduzir pose de ensaio, adaptar 9:16; braço anatômico esquerdo da Nina mantém tatuagem.'])
ref('P06_NIGHT', 'Pinterest', 'references/pinterest/night/bed.jpg', ['lifestyle/night','lifestyle/bedroom'],
    'Selfie próxima na altura do colchão; braço em primeiro plano ampliado.', 'Luz ambiente clara, sem aparência noturna.',
    'Rosto alto à esquerda, tecido ocupando base, quarto neutro.', 'Deitada, queixo apoiado na mão.', 'Cama com roupa clara.',
    'Gestual relaxado e ponto de vista da cama; complementar ao exemplo noturno prioritário do usuário.',
    'https://in.pinterest.com/pin/1030620696006905257/',
    'https://i.pinimg.com/736x/49/46/16/49461699264a7475f5b2ef0bfb3620d8.jpg',
    ['Não transferir ampliação do braço nem proporções.', 'A referência é diurna: luz noturna e edredom rosa vêm dos exemplos do usuário; usar telefone apoiado/temporizador para reduzir risco.'])

user_specs = [
 ('U_STORY','data/brands/nina_v1/references/story_style_master.png','product_story','Produto central/inferior, headline branca acima, pills e box na base.','Fotografia quente em mesa de madeira.','Sem pessoa.','Paleta blush/creme, serifas e doodles; ignorar da série.'),
 ('U_VANITY','data/brands/nina_lifestyle_v1/references/vanity_mirror_skincare.png','lifestyle/makeup','Espelho, rosto alto, bancada ocupada à frente.','Luz interna neutra.','Sentada com telefone e gesto casual.','Objetos usados e enquadramento espontâneo.'),
 ('U_TOWEL','data/brands/nina_lifestyle_v1/references/night_towel_eye_patches.png','lifestyle/night','Selfie íntima com joelho e tigela em primeiro plano.','Luz baixa quente e luzinhas.','Toalha no cabelo, olhos fechados.','Calma, textura doméstica e imperfeição.'),
 ('U_BED','data/brands/nina_lifestyle_v1/references/bed_plush_relax.png','lifestyle/bedroom','Quadro inclinado, rosto parcial, edredom rosa e pelúcias.','Ambiente noturno doméstico.','Deitada sob edredom.','Conforto real e texto branco curto.'),
 ('U_FITNESS','data/brands/nina_lifestyle_v1/references/fitness_mirror_tumbler.png','lifestyle/gym','Close no espelho; telefone parcialmente cobre rosto.','Luz interior neutra.','Tumbler e fone, mão no telefone.','Rotina fitness com uso plausível de objetos.'),
 ('U_TOPDOWN','data/brands/nina_lifestyle_v1/references/robe_topdown_selfcare.png','lifestyle/skincare','Câmera alta, rosto cortado, bancada lateral.','Luz difusa de banheiro.','Robe e bancada vista de cima.','Texto pequeno e cena vivida, não copiar exagero de perspectiva.'),
 ('U_PEACE','data/brands/nina_lifestyle_v1/references/robe_mirror_peace.png','lifestyle/mirror','Espelho vertical, penteadeira cheia na base.','Luz doméstica branca.','Robe e gesto de paz.','Espontaneidade e reflexo fisicamente plausível.'),
 ('U_CLEANSER','data/brands/nina_lifestyle_v1/references/night_face_cleanser.png','lifestyle/skincare','Close inclinado, frasco no canto inferior.','Luz de banheiro.','Rosto com espuma e produto segurado.','Ação cotidiana e horário discreto; não copiar tatuagens da pessoa.')]
for rid,path,cat,comp,light,pose,why in user_specs:
    ref(rid,'USER',path,[cat],'Celular vertical; observar enquadramento específico.',light,comp,pose,'Ambiente doméstico.',why)
for name,rid in [('371960.png','U_FEED_COVER'),('371961.png','U_FEED_INNER')]:
    dst=R/'user/carousel'/name;dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(Path('C:/Users/GAMER/Downloads/gmail_todos_61_arquivos_2026-09-24')/name,dst)
    ref(rid,'USER',dst.relative_to(ROOT).as_posix(),['carousel_covers' if 'COVER' in rid else 'carousel_inner'],
        'Retrato de celular próximo; cover em espelho, interno demonstração.', 'Luz doméstica quente/neutra.',
        'Nina domina foto; serifas brancas, pill rosa, caixa branca arredondada e pequenos desenhos.',
        'Selfie / uso de maquiagem.', 'Quarto real com profundidade.',
        'Exemplos originais de feed fornecidos pelo usuário; autoridade de estilo, nunca de identidade corporal.')

write(R/'library.json', {'schema_version':1,'updated_at':NOW,'status':'MANUAL_RESEARCH_LIBRARY','references':refs,
    'identity_authorities':['data/personas/nina_v1/references/persona_master.png','data/personas/nina_v1/references/nina_360_master.png'],
    'product_authority':'Imagem oficial Shopee do item validado; Pinterest não define produto.',
    'legacy_candidates':'data/research/lifestyle_story/pinterest_references.json: links históricos não selecionados sem inspeção.',
    'indexes':{cat:[r['reference_id'] for r in refs if cat in r['category']] for cat in sorted({c for r in refs for c in r['category']})}})

dna = {
 'VISUAL_DNA':'Fotografia doméstica com textura, blush/creme/madeira; peças comerciais com serifas brancas e acentos rosas, lifestyle discreto.',
 'COMPOSITION_DNA':'Feed: pessoa ou produto grande, profundidade doméstica e espaços para copy. Story produto: hero centro/inferior. Lifestyle: cortes casuais e objetos vividos.',
 'LIGHTING_DNA':'Janela difusa de dia; lâmpadas quentes à noite; preservar sombras naturais e variação doméstica, sem pele plastificada.',
 'CAMERA_DNA':'Celular plausível, espelho coerente ou temporizador declarado; sem ultra-wide excessivo, sem rosto/braço ampliado nem torso comprimido.',
 'POSE_DNA':'Gestos de uso e descanso, mão no telefone/caneca ou apoio simples; anatomia natural, sem impor corpo da referência externa.',
 'ENVIRONMENT_DNA':'Quarto, banheiro/penteadeira, cozinha e mesa com sinais de uso; rosa como detalhe, não cenário artificial totalmente rosa.',
 'TEXT_PLACEMENT_DNA':'Produto/feed: serif branca, pill blush, subheadline, box claro, doodles pequenos fora de rosto/produto. Lifestyle: frase curta/horário, sem estrutura de anúncio. O selo da série não é obrigatório e é omitido nos Stories.',
 'LIFESTYLE_DNA':'Sensação de momento cotidiano fotografado; roupa confortável, pequenas assimetrias e objetos afetivos; Nina sempre pelas duas referências canônicas.'}
write(R/'style_dna.json', {'analyzed_at':NOW,'user_references':[r['reference_id'] for r in refs if r['source']=='USER'],
    'scope_note':'Analisados 8 exemplos canônicos e 2 exemplos do feed. Não alegamos revisão integral dos 61 arquivos.',**dna})

assets=[]
def asset(aid,pin,user,req,keep,adapt,cam,light,comp,person=False,product=None):
    assets.append(dict(asset_id=aid, status='DIRECTION_READY_AWAITING_USER_CHECKPOINT',
      visual_requirements=req, best_reference=pin, priority_user_references=user,
      reference_analysis={
       'WHAT_TO_KEEP':keep,'WHAT_TO_ADAPT':adapt,
       'WHAT_NOT_TO_COPY':'Rosto/corpo/cabelo da pessoa, marcas, textos, watermark, cenário exclusivo ou composição pixel a pixel.',
       'NINA_INTEGRATION':'Usar face master + 360, slim-to-average estável, regras compartilhadas, tatuagem anatômica esquerda; não usar posts como identidade.' if person else 'Nina não aparece; aplicar identidade editorial da marca.',
       'PRODUCT_INTEGRATION':('Imagem oficial do item '+str(product)+' controla geometria/material/cor; nenhum produto do Pinterest é substituto.') if product else 'Sem demonstração de produto novo; se inserir item comercial, anexar sua imagem oficial validada.',
       'CAMERA_DIRECTION':cam,'LIGHTING_DIRECTION':light,'COMPOSITION_DIRECTION':comp},
      identity_reference_paths=['data/personas/nina_v1/references/persona_master.png','data/personas/nina_v1/references/nina_360_master.png'] if person else [],
      official_product_reference=(C/'product_validation/official_images'/f'{product}.png').relative_to(ROOT).as_posix() if product else None,
      scene_reference_path=next(r['local_path'] for r in refs if r['reference_id']==pin),
      generation_allowed=False))
asset('CAROUSEL_COVER','P01_MIRROR',['U_FEED_COVER','U_VANITY'],['3:4','Nina','beauty','headline-safe'],
 'Selfie de espelho, fundo neutro e textura de celular.','Trocar pessoa por Nina; robe confortável fechado, bancada parcial e headline na metade inferior.',
 'Telefone ao lado do rosto, câmera frontal via espelho sem segundo telefone; recuar para plano médio.', 'Luz doméstica suave e quente.',
 'Rosto na metade superior; headline abaixo, pill rosa curta e subheadline; afastar a câmera para não usar ultra-wide.',True)
asset('CAROUSEL_PRODUCT_1','P01_MIRROR',['U_VANITY','U_FEED_INNER'],['3:4','uso do kit','identidade'],
 'Ambiente e luz de banheiro, ação casual.','Nina com tiara e munhequeiras oficiais; telefone apoiado, mãos longe do rosto, sem repetir selfie da capa.',
 'Temporizador, plano médio 3/4, distância suficiente para ver pulsos.', 'Difusa de banheiro.',
 'Nina lateral; kit legível e região inferior reservada ao texto.',True,22098810537)
asset('CAROUSEL_PRODUCT_2','P02_VANITY',['U_STORY','U_FEED_INNER'],['3:4','necessaire','organização'],
 'Agrupamento de objetos e bancada real.','Necessaire oficial vazia; cosméticos externos como cenário, sem sugerir conteúdo incluso.',
 'Vista oblíqua alta, aproximadamente 45 graus; não flat lay idêntico.', 'Janela lateral suave.',
 'Pouch à esquerda, zíper visível, texto à direita em área calma.',False,15966566854)
asset('CAROUSEL_PRODUCT_3','P03_GRWM',['U_STORY','U_FEED_INNER'],['3:4','espelho','reflexo coerente'],
 'Profundidade bancada/quarto.','Retirar tablet; espelho rosa de orelhas de gato e suporte oficiais, sem transformar em espelho iluminado.',
 'Câmera oblíqua na altura do objeto, reflexo apenas do quarto.', 'Luz lateral doméstica.',
 'Produto central, poucos itens secundários; headline curta acima.',False,58200603232)
asset('CAROUSEL_PRODUCT_4','P03_GRWM',['U_STORY','U_FEED_INNER'],['3:4','tapete plano','pincéis'],
 'Bancada com instrumentos de maquiagem.','Tapete oficial plano sobre superfície seca e pincéis ao lado; nenhuma demonstração de lavagem inventada.',
 'Câmera quase superior, distância natural do objeto.', 'Luz suave de janela.',
 'Diagonal do tapete e pincéis, relevo visível; composição diferente do espelho. Para lavagem, buscar nova cena adequada antes.',False,22398938260)
asset('CAROUSEL_FINAL_CTA','P02_VANITY',['U_FEED_COVER','U_STORY'],['3:4','fundo fotográfico','pergunta CTA keyword'],
 'Bancada real, luz e camadas.','Simplificar objetos; frascos neutros desfocados, sem marcas; reservar centro calmo.',
 'Oblíqua mais aberta que os slides de produto.', 'Quente e suave, coerente com abertura.',
 'Bancada na base e contexto visível; pergunta, CTA e keyword sobre fotografia, sem virar tela gráfica.')
asset('PRODUCT_STORY_1','P02_VANITY',['U_STORY'],['9:16','hero kit','sem Nina'],
 'Bancada feminina e luz doméstica.','Tiara rosa e duas munhequeiras oficiais como protagonistas; retirar excesso de cosméticos.',
 'Plano de objeto em 3/4, tiara inteira sem cortar arco.', 'Janela quente com sombra suave.',
 'Kit centro/inferior; serif branca no alto, pill factual e caixa de benefício na base.',False,22098810537)
asset('PRODUCT_STORY_2','P03_GRWM',['U_STORY'],['9:16','espelho hero','reflexo'],
 'Bancada em diagonal e quarto refletido.','Espelho oficial rosa; nenhuma luz embutida, nenhum tablet ou pessoa de tutorial.',
 'Plano de produto oblíquo, controlar reflexo e proporção base/orelhas.', 'Quente doméstica.',
 'Espelho abaixo do centro, apoio/porta-bijuteria legíveis; topo com título e base para box.',False,58200603232)
asset('LIFESTYLE_MORNING','P04_MORNING',['U_PEACE','U_STORY'],['9:16','café','temporizador'],
 'Pessoa junto à bancada, caneca e luz lateral.','Nina, cozinha contemporânea doméstica, roupa confortável e postura menos de ensaio.',
 'Telefone apoiado a cerca de 2–3 m; plano 3/4 natural, não alegar braço estendido.', 'Janela de manhã.',
 'Nina à direita e contexto de cozinha; texto curto no espaço livre.',True)
asset('LIFESTYLE_AFTERNOON','P05_AFTERNOON',['U_VANITY'],['9:16','pausa','mesa'],
 'Mesa diagonal, laptop, caneca e apoio relaxado.','Nina com roupa do dia, ambiente menos decorado, manter a mesma casa plausível.',
 'Telefone apoiado, plano médio lateral; mãos longe da lente.', 'Janela de tarde difusa.',
 'Nina e caneca no centro-direita; laptop parcial embaixo; sem copiar mesa inteira ou pose exata.',True)
asset('LIFESTYLE_NIGHT','P06_NIGHT',['U_BED','U_TOWEL'],['9:16','cama','luz noturna','sem braço ampliado'],
 'Altura baixa da câmera, cama e gesto de descanso.','Nina com camiseta confortável e edredom rosa do DNA do usuário; trocar luz diurna por abajur.',
 'Telefone apoiado fora do quadro a distância confortável; não transferir braço em primeiro plano da referência.', 'Abajur quente, sombra real e ruído sutil.',
 'Rosto e ombro no terço superior; edredom predominante, pequeno texto em área lisa.',True)
write(C/'campaign/reference_map.json',dict(created_at=NOW,campaign_id=C.name,assets=assets,
 generation_gate='PAUSED_AWAITING_USER_REFERENCE_CHECKPOINT',workflow_enforcement='MANUAL_AGENT_POLICY; runtime não alterado',
 style_dna='references/style_dna.json',library='references/library.json'))

for period in ('morning','afternoon','night'):
    p=C/'lifestyle_stories'/period/'generated_source.png'
    write(p.parent/'reference_status.json',dict(classification='PRE_REFERENCE_GENERATION',accepted=False,
        preserved=True,image_path=p.relative_to(ROOT).as_posix(),sha256=sha(p),
        reason='Gerada antes de seleção/análise/mapeamento Pinterest; somente comparação.',
        known_observation='Tatuagem apareceu no braço anatômico direito; correção solicitada falhou por limite do provider, sem novo arquivo.' if period=='afternoon' else 'Sem aprovação no novo fluxo.',
        successful_corrections=0,provider_correction_calls=1 if period=='afternoon' else 0))

write(C/'research/viral_research_followup.json',dict(date=NOW,status='PARTIAL',verified_recent_viral_posts=0,
 searches=['site:instagram.com/reel/ skincare September 2026 (janela 30 dias)','site:tiktok.com skincare routine 2026-09'],
 result='Busca não forneceu post recente com data e métricas verificáveis. TikTok bloqueou acesso por robots; resultados TikTok Shop são páginas de produto, não posts virais.',
 classification='UNKNOWN para viralidade; fontes secundárias anteriores continuam registradas em sources.json.',
 rejected_as_viral_evidence=['https://shop.tiktok.com/us/pdp/dive-in-skincare-routine-by-torriden-hydrating-serum-cleansing-foam/1729466664354616232'],
 warning='Data de atualização do agregador não é data do post. Pins antigos são referências visuais atemporais, não prova de tendência recente.',
 next_action='Verificar posts primários e métricas visíveis antes de declarar TREND_RESEARCH PASS; sem substituir pelos Pins.'))

unchanged=all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in baseline.items())
write(C/'qa/reference_checkpoint_integrity.json',dict(checked_at=NOW,previous_files_unchanged=unchanged,
 previous_file_count=len(baseline),reference_count=len(refs),pinterest_inspected=6,asset_map_count=len(assets),
 map_paths_exist=all((ROOT/a['scene_reference_path']).is_file() for a in assets),new_generated_images=0,
 test_scope='Integridade dos arquivos/metadados e cobertura do mapa; suíte de runtime não reexecutada pois app não mudou.'))
assert unchanged
write(C/'REFERENCE_CHECKPOINT.json',dict(PROCESS_CORRECTED='YES',PINTEREST_STAGE_ADDED='YES',
 MY_REFERENCES_ANALYZED='YES',REFERENCE_STYLE_DNA=dna,PINTEREST_REFERENCES_FOUND=6,
 CAROUSEL_COVER_REFERENCE='P01_MIRROR',CAROUSEL_FINAL_CTA_REFERENCE='P02_VANITY',
 PRODUCT_STORY_REFERENCES=['P02_VANITY','P03_GRWM'],LIFESTYLE_MORNING_REFERENCE='P04_MORNING',
 LIFESTYLE_AFTERNOON_REFERENCE='P05_AFTERNOON',LIFESTYLE_NIGHT_REFERENCE='P06_NIGHT + U_BED + U_TOWEL',
 REFERENCE_MAP_CREATED='YES',CAROUSEL_GENERATOR_SEARCHED='YES',CAROUSEL_GENERATOR_FOUND='NO',
 CAROUSEL_GENERATOR_LOCATION=None,IF_NOT_FOUND='CAROUSEL_INTEGRATION_GAP: pesquisa/copy/imagens oficiais existem; renderização multi-slide 3:4 integrada não localizada neste checkout.',
 CURRENT_CAMPAIGN_PRESERVED='YES',READY_TO_CONTINUE_GENERATION='NO',
 blockers=['Aguardar conferência explícita do checkpoint pelo usuário.','Integração do carrossel não localizada; não improvisar compositor.','Pesquisa de viralidade primária recente ainda parcial.'],
 provider_note='Última correção teve 429 usage_limit_reached; disponibilidade não retestada nesta pausa.',
 scope='Processo assistido/documentado corrigido; nenhum gate automático de runtime novo.',
 generated_in_this_checkpoint=0))
print(json.dumps({'preserved':unchanged,'references':len(refs),'mapped_assets':len(assets),'new_images_generated':0}))
