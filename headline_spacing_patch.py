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
  let automaticSpacingMode = '';

  function syncHeadlineLineSpacing(){
    const headline = state.texts[0];
    const headlineFont = `${headline.size}px 'PFDinXBlack'`;
    const wraps = wrapLines(headline.text, headlineFont, TEXT_BOX.w).length > 1;
    const subline = state.texts[1];
    const sublineFont = `${subline.size}px 'PFDinMedium'`;
    const bothSingle = Boolean(headline.text.trim() && subline.text.trim()) &&
      !wraps && wrapLines(subline.text, sublineFont, TEXT_BOX.w).length === 1;
    const mode = wraps ? 'wrapped' : bothSingle ? 'single' : 'manual';
    // On the first render, the text cards may not exist yet; update them once
    // they are created, while avoiding DOM work during every export frame.
    const firstSlider = document.querySelector('#textLayersWrap input[data-field="lineSpacing"]');
    if(mode === automaticSpacingMode && firstSlider && firstSlider.disabled === (mode !== 'manual')) return;
    automaticSpacingMode = mode;
    state.texts.forEach((layer, idx)=>{
      layer.lineSpacing = wraps ? 0 : bothSingle && idx === 0 ? 20 : preferredTextLineSpacing[idx];
      const slider = document.querySelector(`#textLayersWrap input[data-field="lineSpacing"][data-idx="${idx}"]`);
      if(!slider) return;
      slider.value = layer.lineSpacing;
      slider.disabled = wraps || (bothSingle && idx === 0);
      const label = slider.closest('.field').querySelector('[data-out="lineSpacing"]');
      if(label) label.textContent = layer.lineSpacing + 'px';
    });
  }

  function drawTextLayers(t){''')

replace_once('    let y = TEXT_BOX.y + singleLineSublineOffset;',
             '    syncHeadlineLineSpacing();\n    let y = TEXT_BOX.y + singleLineSublineOffset;')
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
