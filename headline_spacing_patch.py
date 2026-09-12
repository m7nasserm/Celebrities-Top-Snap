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

path.write_text(html, encoding="utf-8")
print("Automatic two-line headline spacing applied")
