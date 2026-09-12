import re,sys
p=sys.argv[1]
s=open(p,encoding='utf-8').read()
def rep(old,new):
 global s
 if old not in s: raise SystemExit('Expected source block not found: '+old[:80])
 s=s.replace(old,new,1)
rep('  .color-dot-row{ display:flex; gap:72px; flex-wrap:wrap; flex-shrink:0; justify-content:flex-start; padding-right:40px; }','  .color-dot-row{ display:flex; gap:clamp(8px,3vw,72px); flex-wrap:nowrap; flex-shrink:0; justify-content:flex-start; padding-right:clamp(0px,2.5vw,40px); width:100%; min-width:0; }\n  .color-dot-row .color-dot{ flex:1 1 0; width:auto; min-width:0; max-width:52px; }')
rep('  .settings-sliders{ display:flex; flex-direction:column; gap:38px; flex:0 0 408px; min-width:0; }\n  .settings-sliders .slider-row label{ flex:0 0 148px; min-width:0; white-space:nowrap; }\n  .settings-sliders .intensity-row label{ flex-basis:148px; }','''  .settings-sliders{ display:flex; flex-direction:column; gap:38px; flex:1 1 620px; width:100%; max-width:720px; min-width:0; }
  .settings-sliders .slider-row{ display:grid; grid-template-columns:minmax(280px,1fr) 148px; align-items:center; gap:18px; width:100%; }
  .settings-sliders .slider-row label,.settings-sliders .intensity-row label{ grid-column:2; grid-row:1; min-width:0; white-space:nowrap; }
  .settings-sliders .slider-row input[type=range]{ grid-column:1; grid-row:1; width:100%; max-width:none; min-width:0; }''')
rep('  @media (max-width:700px){ .anim-grid-sq{ grid-template-rows:repeat(2,minmax(0,1fr)); } .settings-row{ padding-right:0; } }','''  @media (max-width:700px){
    .image-columns{align-items:stretch;width:100%;}
    .image-col-main,.image-col-anim{width:100%;max-width:100%;}
    .color-dot-row{justify-content:center;gap:clamp(5px,2vw,12px);width:100%;max-width:360px;padding-inline:0;margin-inline:auto;align-self:center;}
    .color-dot-row .color-dot{flex:0 1 52px;width:clamp(42px,12vw,52px);max-width:52px;}
    .anim-grid-sq{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));grid-template-rows:1fr;gap:6px;width:min(100%,380px);max-width:380px;margin-inline:auto;align-self:center;}
    .anim-grid-sq>.center-img-btn{grid-column:auto;grid-row:auto;width:100%;height:auto;aspect-ratio:1;}
    .anim-sq{width:100%;max-width:none;aspect-ratio:1;border-radius:10px;font-size:0;}
    .anim-sq svg,.center-img-btn svg{width:22px;height:22px;stroke:currentColor;stroke-width:2;fill:none;stroke-linecap:round;stroke-linejoin:round;flex:none;}
    .settings-row{padding-right:0;width:100%;max-width:100%;overflow:visible;}
    .settings-sliders{flex:1 1 auto;width:100%;max-width:100%;min-width:0;}
    .settings-sliders .slider-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(118px,auto);align-items:center;gap:12px;width:100%;min-width:0;}
    .settings-sliders .slider-row label,.settings-sliders .intensity-row label{grid-column:2;grid-row:1;flex:none;width:auto;min-width:0;white-space:nowrap;}
    .settings-sliders .slider-row input[type=range]{grid-column:1;grid-row:1;width:100%;max-width:none;min-width:0;box-sizing:border-box;margin-inline:6px;}
  }''')
rep('  .center-img-btn img{ width:28px; height:28px; object-fit:contain; }','  .anim-sq svg, .center-img-btn svg{ width:28px; height:28px; stroke:currentColor; stroke-width:2; fill:none; stroke-linecap:round; stroke-linejoin:round; }')
icons={
'zoomIn':'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2M8.5 11h5M11 8.5v5"/></svg>',
'zoomOut':'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2M8.5 11h5"/></svg>',
'slideRight':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg>',
'slideLeft':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M10 7l-5 5 5 5"/></svg>',
'slideUp':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M7 10l5-5 5 5"/></svg>',
'slideDown':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M7 14l5 5 5-5"/></svg>'}
for k,svg in icons.items():
 pat=r'(<button class="anim-sq(?: active)?" data-v="'+k+r'" title="([^"]+)")>.*?</button>'
 m=re.search(pat,s)
 if not m: raise SystemExit('Animation button not found: '+k)
 s=s[:m.start()]+m.group(1)+' aria-label="'+m.group(2)+'">'+svg+'</button>'+s[m.end():]
pat=r'<button type="button" class="anim-sq center-img-btn" id="centerImgBtn" title="توسيط الصورة" aria-label="توسيط الصورة">.*?</button>'
m=re.search(pat,s)
if not m: raise SystemExit('Center button not found')
svg='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5"/><path d="M9 9h6v6H9z"/></svg>'
s=s[:m.start()]+'<button type="button" class="anim-sq center-img-btn" id="centerImgBtn" title="توسيط الصورة" aria-label="توسيط الصورة">'+svg+'</button>'+s[m.end():]
rep('''      const baseW = im.naturalW * baseScale * im.scale;
      const baseH = im.naturalH * baseScale * im.scale;
      const scale = baseScale * im.scale * anim.scaleFactor * introScale;
      const dw = im.naturalW*scale, dh = im.naturalH*scale;''','''      const anchorFx = 0.5, anchorFy = 0.25;
      const coverW = im.naturalW * baseScale;
      const coverH = im.naturalH * baseScale;
      const coverCx = FRAME.x + FRAME.w/2 + im.offsetX;
      const coverCy = FRAME.y + FRAME.h/2 + im.offsetY;
      const coverDrawX = coverCx - coverW/2;
      const coverDrawY = coverCy - coverH/2;
      const manualAnchorX = coverDrawX + anchorFx*coverW;
      const manualAnchorY = coverDrawY + anchorFy*coverH;
      const manualW = coverW * im.scale;
      const manualH = coverH * im.scale;
      const manualDrawX = manualAnchorX - anchorFx*manualW;
      const manualDrawY = manualAnchorY - anchorFy*manualH;
      const totalExtraScale = anim.scaleFactor * introScale;
      const dw = manualW * totalExtraScale;
      const dh = manualH * totalExtraScale;''')
rep('''        // Anchor zoom around the middle of the image's upper half (not the dead
        // center) — that's roughly where faces tend to sit, so zooming in/out
        // doesn't drift them out of frame or clip them.
        const anchorFx = 0.5, anchorFy = 0.25;
        const baseCx = FRAME.x + FRAME.w/2 + im.offsetX;
        const baseCy = FRAME.y + FRAME.h/2 + im.offsetY;
        const baseDrawX = baseCx - baseW/2;
        const baseDrawY = baseCy - baseH/2;
        const anchorCanvasX = baseDrawX + anchorFx*baseW;
        const anchorCanvasY = baseDrawY + anchorFy*baseH;
        drawX = anchorCanvasX - anchorFx*dw;
        drawY = anchorCanvasY - anchorFy*dh;''','''        const animAnchorX = manualDrawX + anchorFx*manualW;
        const animAnchorY = manualDrawY + anchorFy*manualH;
        drawX = animAnchorX - anchorFx*dw;
        drawY = animAnchorY - anchorFy*dh;''')
rep('''        const cx = FRAME.x + FRAME.w/2 + im.offsetX + anim.offX;
        const cy = FRAME.y + FRAME.h/2 + im.offsetY + anim.offY;
        drawX = cx - dw/2;
        drawY = cy - dh/2;''','''        drawX = manualDrawX - (dw-manualW)/2 + anim.offX;
        drawY = manualDrawY - (dh-manualH)/2 + anim.offY;''')
rep('    let y = TEXT_BOX.y;','''    const sublineLayer = state.texts.find(layer => layer.kind === "subline") || state.texts[1];
    let singleLineSublineOffset = 0;
    if(sublineLayer && sublineLayer.text && sublineLayer.text.trim()){
      const sublineFont = `${sublineLayer.size}px 'PFDinMedium'`;
      const fullSublineLines = wrapLines(sublineLayer.text, sublineFont, maxWidth);
      if(fullSublineLines.length === 1) singleLineSublineOffset = 20;
    }
    let y = TEXT_BOX.y + singleLineSublineOffset;''')
rep('      y += 8;','      y += 1.6;')
rep('      state.image.offsetX = 0; state.image.offsetY = 0;','''      state.image.offsetX = 0;
      const uploadBaseScale = Math.max(FRAME.w/img.naturalWidth, FRAME.h/img.naturalHeight);
      const fittedH = img.naturalHeight * uploadBaseScale;
      state.image.offsetY = Math.max(0, (fittedH - FRAME.h) / 2);''')
open(p,'w',encoding='utf-8').write(s)
print('Reviewed patches applied successfully')
