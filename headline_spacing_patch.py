#!/usr/bin/env python3
"""Keep both text layers' line-spacing at zero while the headline wraps."""
from pathlib import Path
import sys

path = Path(sys.argv[1])
html = path.read_text(encoding="utf-8")

def replace_once(old, new):
    global html
    if html.count(old) != 1:
        raise SystemExit(f"Expected exactly one occurrence of {old[:70]!r}")
    html = html.replace(old, new, 1)

replace_once('  function drawTextLayers(t){', '''  // Save each slider's manually selected value so it can return when the
  // headline fits on one line again.
  const preferredTextLineSpacing = state.texts.map(layer => layer.lineSpacing);
  let compactHeadlineSpacing = false;

  function syncHeadlineLineSpacing(){
    const headline = state.texts[0];
    const headlineFont = `${headline.size}px 'PFDinXBlack'`;
    const wraps = wrapLines(headline.text, headlineFont, TEXT_BOX.w).length > 1;
    // On the first render, the text cards may not exist yet; update them once
    // they are created, while avoiding DOM work during every export frame.
    const firstSlider = document.querySelector('#textLayersWrap input[data-field="lineSpacing"]');
    if(wraps === compactHeadlineSpacing && firstSlider && firstSlider.disabled === wraps) return;
    compactHeadlineSpacing = wraps;
    state.texts.forEach((layer, idx)=>{
      layer.lineSpacing = wraps ? 0 : preferredTextLineSpacing[idx];
      const slider = document.querySelector(`#textLayersWrap input[data-field="lineSpacing"][data-idx="${idx}"]`);
      if(!slider) return;
      slider.value = layer.lineSpacing;
      slider.disabled = wraps;
      const label = slider.closest('.field').querySelector('[data-out="lineSpacing"]');
      if(label) label.textContent = layer.lineSpacing + 'px';
    });
  }

  function drawTextLayers(t){''')

replace_once('    let y = TEXT_BOX.y + singleLineSublineOffset;',
             '''    syncHeadlineLineSpacing();
    const headlineLayer = state.texts[0];
    const headlineLineCount = headlineLayer.text.trim() ?
      wrapLines(headlineLayer.text, `${headlineLayer.size}px 'PFDinXBlack'`, maxWidth).length : 0;
    const headlineIsSingle = headlineLineCount === 1;
    const offsetSublineByFive = headlineLineCount === 2 && singleLineSublineOffset === 20;
    let y = TEXT_BOX.y + (sublineLayer && !sublineLayer.text.trim() ? 50 : headlineIsSingle ? singleLineSublineOffset : 0);''')
replace_once('      const lineHeight = layer.size * 1.28 + (layer.lineSpacing||0);',
             '      const lineHeight = layer.size * 1.28 + (layer.lineSpacing||0);\n      if(idx === 1 && offsetSublineByFive) y += 5;')

replace_once('          <div id="textLayersWrap" class="text-columns"></div>',
             '''          <div id="textLayersWrap" class="text-columns"></div>
          <div id="textLayoutSuggestion" class="text-layout-suggestion" hidden>
            <span>اقتراح تنسيق: عنوان بسطر واحد ونص فرعي بسطرين — الحجم 63/60 والتباعد 20/15 بكسل</span>
            <button type="button" id="applyTextLayoutSuggestion">تطبيق الاقتراح</button>
          </div>''')
replace_once('  .text-layer-card{', '''  .text-layout-suggestion{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:12px; padding:10px 12px; border:1px solid #d5cff0; border-radius:10px; background:#F3EAFD; color:var(--text); font-size:14px; line-height:1.5; }
  .text-layout-suggestion[hidden]{ display:none; }
  .text-layout-suggestion button{ flex:none; border:1px solid var(--accent); background:var(--panel); color:var(--accent); border-radius:8px; padding:7px 10px; font:600 14px 'Tajawal',sans-serif; cursor:pointer; }
  .text-layout-suggestion button:hover{ background:var(--panel-2); }
  @media (max-width:700px){ .text-layout-suggestion{ flex-wrap:wrap; } }
  .text-layer-card{''')

replace_once('  const textLayersWrap = document.getElementById("textLayersWrap");', '''  const textLayersWrap = document.getElementById("textLayersWrap");
  const textLayoutSuggestion = document.getElementById("textLayoutSuggestion");
  function updateTextLayoutSuggestion(){
    const [headline, subline] = state.texts;
    if(!headline.text.trim() || !subline.text.trim()){
      textLayoutSuggestion.hidden = true;
      return;
    }
    const count = (layer, size, family) =>
      wrapLines(layer.text, `${size}px '${family}'`, TEXT_BOX.w).length;
    textLayoutSuggestion.hidden = !(
      count(headline, headline.size, 'PFDinXBlack') === 2 &&
      count(subline, subline.size, 'PFDinMedium') === 2 &&
      count(headline, 63, 'PFDinXBlack') === 1 &&
      count(subline, 60, 'PFDinMedium') === 2
    );
  }
  document.getElementById("applyTextLayoutSuggestion").addEventListener("click", ()=>{
    if(textLayoutSuggestion.hidden) return;
    state.texts.forEach((layer, idx)=>{
      layer.size = idx === 0 ? 63 : 60;
      layer.lineSpacing = idx === 0 ? 20 : 15;
      preferredTextLineSpacing[idx] = layer.lineSpacing;
      userAdjustedLineSpacing[idx] = true;
      const card = textLayersWrap.children[idx];
      for(const field of ['size', 'lineSpacing']){
        card.querySelector(`[data-field="${field}"]`).value = layer[field];
        card.querySelector(`[data-out="${field}"]`).textContent = layer[field] + 'px';
      }
    });
    renderCurrent();
    updateTextLayoutSuggestion();
  });''')

replace_once('card.querySelector(\'[data-field="text"]\').addEventListener("input", e=>{ state.texts[idx].text = e.target.value; renderCurrent(); });',
             'card.querySelector(\'[data-field="text"]\').addEventListener("input", e=>{ state.texts[idx].text = e.target.value; renderCurrent(); updateTextLayoutSuggestion(); });')
replace_once('        card.querySelector(\'[data-out="size"]\').textContent = e.target.value+"px";\n        renderCurrent();',
             '        card.querySelector(\'[data-out="size"]\').textContent = e.target.value+"px";\n        renderCurrent();\n        updateTextLayoutSuggestion();')
replace_once('  renderTextLayers();\n\n  /* ---------------- music controls ---------------- */',
             '  renderTextLayers();\n  updateTextLayoutSuggestion();\n\n  /* ---------------- music controls ---------------- */')
replace_once('        state.texts[idx].lineSpacing = +e.target.value;',
             '        preferredTextLineSpacing[idx] = +e.target.value;\n        state.texts[idx].lineSpacing = +e.target.value;')

replace_once('  let previewT = TYPE_END_FRAME/(FPS*DURATION); // start the static editor view past the typing-in animation',
             '  let previewT = 0; // start the preview at the beginning of the video')

replace_once('  .center-img-btn:active{ transform:scale(.94); border-color:var(--accent); background:#F3EAFD; }',
             '  .center-img-btn:active{ border-color:var(--accent); background:#F3EAFD; }')
replace_once('''  .center-img-btn.pressed{ border-color:var(--accent); background:#F3EAFD; box-shadow:0 0 0 4px rgba(125,42,231,.18); animation:center-button-press .5s ease-out; }
  @keyframes center-button-press{
    0%{ transform:scale(.94); }
    60%{ transform:scale(1.03); }
    100%{ transform:scale(1); }
  }
  @media (prefers-reduced-motion:reduce){ .center-img-btn.pressed{ animation:none; } }''',
             '  .center-img-btn.pressed{ border-color:var(--accent); background:#F3EAFD; box-shadow:0 0 0 4px rgba(125,42,231,.18); }')

replace_once('  .transport{ display:flex; gap:10px; align-items:center; }',
             '  .transport{ display:flex; gap:10px; align-items:center; }\n  .transport .btn{ font-weight:500; }\n  .transport .transport-icon{ color:var(--accent); }\n  #resetBtn .transport-icon{ font-size:24px; line-height:18px; }')
replace_once('<button class="btn btn-ghost" id="playBtn">▶ تشغيل المعاينة</button>',
             '<button class="btn btn-ghost" id="playBtn"><span class="transport-icon" aria-hidden="true">▶</span> تشغيل المعاينة</button>')
replace_once('<button class="btn btn-ghost" id="resetBtn">↺ البداية</button>',
             '<button class="btn btn-ghost" id="resetBtn"><span class="transport-icon" aria-hidden="true">↺</span> البداية</button>')
replace_once('playBtn.textContent = "▶ تشغيل المعاينة";',
             'playBtn.innerHTML = \'<span class="transport-icon" aria-hidden="true">▶</span> تشغيل المعاينة\';')
replace_once('playBtn.textContent = "⏸ إيقاف مؤقت";',
             'playBtn.innerHTML = \'<span class="transport-icon" aria-hidden="true">⏸</span> إيقاف مؤقت\';')

# 299 frames at 30 fps: 9 seconds and 29 frames of media.
replace_once('  const W = 1080, H = 1920, FPS = 30, DURATION = 10;',
             '  const W = 1080, H = 1920, FPS = 30, DURATION = 299 / FPS;')
replace_once('<span class="time-label" id="timeLabel">0.0 / 10.0s</span>',
             '<span class="time-label" id="timeLabel">0.00 / 9.97s</span>')
replace_once('<input type="range" id="scrubber" min="0" max="300" step="1" value="45">',
             '<input type="range" id="scrubber" min="0" max="299" step="1" value="0">')
replace_once('timeLabel.textContent = secs.toFixed(1)+" / "+DURATION.toFixed(1)+"s";',
             'timeLabel.textContent = secs.toFixed(2)+" / "+DURATION.toFixed(2)+"s";')
replace_once('scrubber.value = Math.round(previewT*300);',
             'scrubber.value = Math.round(previewT*299);')
replace_once('previewT = (+e.target.value)/300;',
             'previewT = (+e.target.value)/299;')

# Embed the supplied logo to keep the published site self-contained. Its alpha
# channel masks the existing purple gradient so the artwork matches the theme.
logo_data = Path(__file__).with_name('mbc-logo.b64').read_text(encoding='ascii').strip()
replace_once('  header h1{font-size:22.5px;',
             '  .brand-logo{ flex:none; margin-inline-start:auto; width:clamp(86px, 11vw, 126px); aspect-ratio:800 / 350; background:var(--accent-grad); --logo-mask:url("data:image/png;base64,' + logo_data + '"); -webkit-mask:var(--logo-mask) center / contain no-repeat; mask:var(--logo-mask) center / contain no-repeat; }\n  header h1{font-size:22.5px;')
replace_once('  </header>\n\n  <main>',
             '    <div class="brand-logo" role="img" aria-label="MBC"></div>\n  </header>\n\n  <main>')

path.write_text(html, encoding="utf-8")
print("Automatic two-line headline spacing applied")
