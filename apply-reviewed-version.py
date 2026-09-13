#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

p = Path(sys.argv[1])

# Preserve the existing reviewed patch set first.
subprocess.run([sys.executable, 'deploy_patch.py', str(p)], check=True)
text = p.read_text(encoding='utf-8')

# Add the shared two-tool navigation to the generated Celebrities page.
css_anchor = "  footer.note{ padding:14px 24px 26px; color:var(--muted); font-size:14px; line-height:1.8; border-top:1px solid var(--line); background:var(--panel); }\n"
# The source has used both 14px and 14.375px across reviewed builds.
css_anchor_alt = "  footer.note{ padding:14px 24px 26px; color:var(--muted); font-size:14.375px; line-height:1.8; border-top:1px solid var(--line); background:var(--panel); }\n"
css = '''  .tool-tabs{display:flex;align-items:center;gap:14px;white-space:nowrap;}\n  .tool-tabs a{display:inline-block;padding:4px 0 5px;border-bottom:3px solid transparent;color:var(--muted);font-size:22.5px;font-weight:500;text-decoration:none;line-height:1.3;}\n  .tool-tabs a:hover{color:var(--accent);}\n  .tool-tabs a[aria-current="page"]{color:var(--accent);border-bottom-color:var(--accent);font-weight:700;}\n  .tool-tabs span{color:var(--line);font-size:21px;user-select:none;}\n  .tool-tabs a:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px;}\n  @media(max-width:650px){\n    header{flex-wrap:wrap;}\n    header .mark{order:0;}\n    header .brand-logo{order:1;margin-inline-start:auto;}\n    header>div:nth-child(2){order:2;flex-basis:100%;min-width:0;}\n    .tool-tabs{gap:7px;max-width:100%;justify-content:center;}\n    .tool-tabs a{font-size:clamp(10px,3vw,15px);}\n    .tool-tabs span{font-size:15px;}\n  }\n'''
if '.tool-tabs{' not in text:
    anchor = css_anchor_alt if css_anchor_alt in text else css_anchor
    if anchor not in text:
        raise SystemExit('Could not find CSS insertion point for tool tabs')
    text = text.replace(anchor, anchor + css, 1)

old_headers = [
    '''    <div>\n      <h1>Celebrities Top Snap</h1>\n      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس ٩:١٦</p>\n    </div>''',
    '''    <div>\n      <h1>Celebrities Top Snap</h1>\n      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس 9:16</p>\n    </div>'''
]
new_header = '''    <div>\n      <nav class="tool-tabs" aria-label="Video tools"><a href="./" aria-current="page">Celebrities Top Snap</a><span aria-hidden="true">|</span><a href="screenshot.html">Screenshot Top Snap</a></nav>\n    </div>'''
for old_header in old_headers:
    if old_header in text:
        text = text.replace(old_header, new_header, 1)
        break
else:
    old_nav = '<nav class="tool-tabs" aria-label="Video tools"><a href="screenshot.html">Screenshot Top Snap</a><span aria-hidden="true">|</span><a href="./" aria-current="page">Celebrities Top Snap</a></nav>'
    fixed_nav = '<nav class="tool-tabs" aria-label="Video tools"><a href="./" aria-current="page">Celebrities Top Snap</a><span aria-hidden="true">|</span><a href="screenshot.html">Screenshot Top Snap</a></nav>'
    if old_nav in text:
        text = text.replace(old_nav, fixed_nav, 1)
    text = text.replace('      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس ٩:١٦</p>\n', '', 1)
    text = text.replace('      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس 9:16</p>\n', '', 1)

edge_jump_script = r'''<script id="preview-edge-jump-patch">
(() => {
  function installPreviewEdgeJump(){
    const scrubber = document.querySelector('#scrubber');
    if(!scrubber || scrubber.dataset.edgeJumpInstalled === '1') return false;
    const stepper = scrubber.closest('.preview-stepper, .range-stepper') || scrubber.parentElement;
    if(!stepper) return false;
    const buttons = Array.from(stepper.querySelectorAll('button'));
    if(buttons.length < 2) return false;
    scrubber.dataset.edgeJumpInstalled = '1';
    const leftButton = buttons[0];
    const rightButton = buttons[buttons.length - 1];
    function jump(toEnd){
      const raw = toEnd ? scrubber.max : scrubber.min;
      const fallback = toEnd ? 100 : 0;
      scrubber.value = String(raw === '' ? fallback : Number(raw));
      scrubber.dispatchEvent(new Event('input', {bubbles:true}));
      scrubber.dispatchEvent(new Event('change', {bubbles:true}));
    }
    function bind(button, toEnd){
      button.addEventListener('pointerdown', event => {
        if(event.button !== 0) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        jump(toEnd);
      }, true);
      button.addEventListener('click', event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        jump(toEnd);
      }, true);
    }
    bind(leftButton, false);
    bind(rightButton, true);
    return true;
  }
  function start(){
    if(installPreviewEdgeJump()) return;
    const observer = new MutationObserver(() => {
      if(installPreviewEdgeJump()) observer.disconnect();
    });
    observer.observe(document.documentElement, {childList:true, subtree:true});
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();
</script>'''

def inject_edge_jump(html):
    if 'id="preview-edge-jump-patch"' in html:
        return html
    marker = html.rfind('</body>')
    if marker == -1:
        return html
    return html[:marker] + edge_jump_script + '\n' + html[marker:]

def normalize_screenshot_tabs(html):
    desired = '<nav class="tool-tabs" aria-label="Video tools"><a href="./">Celebrities Top Snap</a><span aria-hidden="true">|</span><a href="screenshot.html" aria-current="page">Screenshot Top Snap</a></nav>'
    old = '<nav class="tool-tabs" aria-label="Video tools"><a href="screenshot.html" aria-current="page">Screenshot Top Snap</a><span aria-hidden="true">|</span><a href="./">Celebrities Top Snap</a></nav>'
    if old in html:
        return html.replace(old, desired, 1)
    return html

def patch_screenshot_export(html):
    # Arc can successfully display these embedded images while HTMLImageElement.decode()
    # still rejects them. Avoid forcing a second decode before export; wait for the
    # normal image load state instead. This leaves the rendered pixels unchanged.
    risky_preload = '''      await Promise.all(Object.values(state.bgImages).map(img=>img.decode()));
      await textboxImg.decode();state.textboxImg=textboxImg;'''
    safe_preload = r'''      const waitForRenderableImage = img => {
        if(img.complete && img.naturalWidth > 0) return Promise.resolve();
        return new Promise((resolve,reject)=>{
          const cleanup=()=>{
            img.removeEventListener('load',onLoad);
            img.removeEventListener('error',onError);
          };
          const onLoad=()=>{cleanup();resolve();};
          const onError=()=>{cleanup();reject(new Error('تعذّر تحميل أحد عناصر الصورة'));};
          img.addEventListener('load',onLoad,{once:true});
          img.addEventListener('error',onError,{once:true});
          if(img.complete){
            cleanup();
            if(img.naturalWidth > 0) resolve();
            else reject(new Error('تعذّر تحميل أحد عناصر الصورة'));
          }
        });
      };
      await Promise.all(Object.values(state.bgImages).map(waitForRenderableImage));
      await waitForRenderableImage(textboxImg);
      state.textboxImg=textboxImg;'''
    if risky_preload in html:
        html = html.replace(risky_preload, safe_preload, 1)

    start_token = 'const music=await loadMusicBuffer();'
    end_token = "finishExport(new Blob([output.target.buffer],{type:'video/mp4'}),'mp4');"
    start = html.find(start_token)
    end = html.find(end_token, start if start >= 0 else 0)
    if start < 0 or end < 0:
        return html
    # Preserve the existing indentation before the start token.
    line_start = html.rfind('\n', 0, start) + 1
    start = line_start
    end += len(end_token)

    replacement = r'''      const music=await loadMusicBuffer();
      const {Output,Mp4OutputFormat,WebMOutputFormat,BufferTarget,CanvasSource,AudioBufferSource,Quality}=window.Mediabunny;
      const length=Math.round(DURATION_S*music.sampleRate);
      const soundtrack=audioCtx.createBuffer(music.numberOfChannels,length,music.sampleRate);
      for(let channel=0;channel<music.numberOfChannels;channel++){
        soundtrack.getChannelData(channel).set(music.getChannelData(channel).subarray(0,length));
      }

      async function encodeFrameByFrame(kind){
        const isMp4=kind==='mp4';
        const videoQuality=new Quality({bitrate:8_000_000});
        const audioQuality=new Quality({bitrate:160_000});
        let videoCodec='avc';
        let audioCodec='aac';
        let format=new Mp4OutputFormat();
        if(isMp4){
          const avcSupported=await window.Mediabunny.canEncodeVideo('avc',{width:canvas.width,height:canvas.height,quality:videoQuality});
          if(!avcSupported) throw new Error('H.264 encoding is unavailable in this browser');
          if(!(await window.Mediabunny.canEncodeAudio('aac'))){
            window.MediabunnyAacEncoder.registerAacEncoder();
          }
        }else{
          format=new WebMOutputFormat();
          audioCodec='opus';
          if(!(await window.Mediabunny.canEncodeAudio('opus'))){
            throw new Error('Opus audio encoding is unavailable in this browser');
          }
          if(await window.Mediabunny.canEncodeVideo('vp9',{width:canvas.width,height:canvas.height,quality:videoQuality})){
            videoCodec='vp9';
          }else if(await window.Mediabunny.canEncodeVideo('vp8',{width:canvas.width,height:canvas.height,quality:videoQuality})){
            videoCodec='vp8';
          }else{
            throw new Error('This browser cannot encode H.264, VP9, or VP8 video');
          }
        }
        const localOutput=new Output({format,target:new BufferTarget()});
        output=localOutput;
        const video=new CanvasSource(canvas,{codec:videoCodec,quality:videoQuality});
        localOutput.addVideoTrack(video,{frameRate:FPS});
        const audio=new AudioBufferSource({codec:audioCodec,quality:audioQuality});
        localOutput.addAudioTrack(audio);
        exportStatus.textContent=isMp4 ? 'جارٍ تجهيز MP4…' : 'جارٍ تجهيز WebM المتوافق…';
        await localOutput.start();
        await audio.add(soundtrack);
        for(let frame=0;frame<TOTAL_FRAMES;frame++){
          renderFrame(frame);
          await video.add(frame/FPS,1/FPS,{keyFrame:frame%(FPS*2)===0});
          exportStatus.textContent=(isMp4 ? 'جارٍ تصدير MP4… ' : 'جارٍ تصدير WebM… ')+(frame+1)+' / '+TOTAL_FRAMES;
          if(frame%5===0)await new Promise(resolve=>setTimeout(resolve,0));
        }
        exportStatus.textContent=isMp4 ? 'جارٍ إنهاء ملف MP4…' : 'جارٍ إنهاء ملف WebM…';
        await localOutput.finalize();
        return new Blob([localOutput.target.buffer],{type:isMp4?'video/mp4':'video/webm'});
      }

      let exportedBlob;
      let exportedExt='mp4';
      try{
        exportedBlob=await encodeFrameByFrame('mp4');
      }catch(mp4Error){
        console.warn('MP4/H.264 export unavailable; retrying frame-by-frame WebM.',mp4Error);
        if(output){try{await output.cancel();}catch{}}
        output=null;
        exportedExt='webm';
        exportStatus.textContent='MP4 غير مدعوم في هذا المتصفح — جارٍ التحويل تلقائياً إلى WebM…';
        exportedBlob=await encodeFrameByFrame('webm');
      }
      finishExport(exportedBlob,exportedExt);'''

    html = html[:start] + replacement + html[end:]
    html = html.replace(
        'يُصدَّر الفيديو بصيغة MP4 بدقة 1080×1920 بمعدل ثابت 30 إطاراً/ثانية، مع معالجة كل إطار للحفاظ على سلاسة الحركة. يتطلب متصفحاً حديثاً يدعم WebCodecs مثل Chrome أو Edge.',
        'يُصدَّر الفيديو بدقة 1080×1920 وبمعدل ثابت 30 إطاراً/ثانية مع معالجة كل إطار للحفاظ على سلاسة الحركة. يستخدم MP4/H.264 عند دعمه، ويتحوّل تلقائياً إلى WebM/VP9 أو VP8 عند الحاجة.'
    )
    html = html.replace("exportStatus.textContent='تعذّر تصدير MP4: '+error.message;", "exportStatus.textContent='تعذّر تصدير الفيديو: '+error.message;")
    return html

text = inject_edge_jump(text)
p.write_text(text, encoding='utf-8')

screenshot_source = Path('screenshot.html')
screenshot_target = p.parent / 'screenshot.html'
if not screenshot_source.exists():
    raise SystemExit('screenshot.html is missing from repository root')
screenshot_text = screenshot_source.read_text(encoding='utf-8')
screenshot_text = normalize_screenshot_tabs(screenshot_text)
screenshot_text = patch_screenshot_export(screenshot_text)
screenshot_target.write_text(inject_edge_jump(screenshot_text), encoding='utf-8')

print('Top Snap tabs fixed; preview edge jumps preserved; Screenshot export avoids Arc image decode failures and keeps the smooth browser fallback')
