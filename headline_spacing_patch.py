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
  const userAdjustedLineSpacing = state.texts.map(() => false);
  let compactHeadlineSpacing = false;

  function syncHeadlineLineSpacing(){
    const headline = state.texts[0];
    const headlineFont = `${headline.size}px 'PFDinXBlack'`;
    const wraps = wrapLines(headline.text, headlineFont, TEXT_BOX.w).length > 1;
    // On the first render, the text cards may not exist yet; update them once
    // they are created, while avoiding DOM work during every export frame.
    const firstSlider = document.querySelector('#textLayersWrap input[data-field="lineSpacing"]');
    if(wraps === compactHeadlineSpacing && firstSlider) return;
    compactHeadlineSpacing = wraps;
    state.texts.forEach((layer, idx)=>{
      layer.lineSpacing = wraps && !userAdjustedLineSpacing[idx] ? 0 : preferredTextLineSpacing[idx];
      const slider = document.querySelector(`#textLayersWrap input[data-field="lineSpacing"][data-idx="${idx}"]`);
      if(!slider) return;
      slider.value = layer.lineSpacing;
      slider.disabled = false;
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
replace_once('        state.texts[idx].lineSpacing = +e.target.value;',
             '        preferredTextLineSpacing[idx] = +e.target.value;\n        userAdjustedLineSpacing[idx] = true;\n        state.texts[idx].lineSpacing = +e.target.value;')

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

replace_once('  input[type=range]{ -webkit-appearance:none;', '''  .range-stepper{ display:flex; align-items:center; gap:7px; direction:ltr; width:100%; min-width:0; }
  .range-stepper input[type=range]{ flex:1 1 0; min-width:0; width:100%; max-width:none; margin:0; }
  .range-stepper button{ position:relative; flex:0 0 25px; width:25px; height:25px; padding:0; border:1px solid var(--line); border-radius:7px; background:var(--panel); color:var(--accent); cursor:pointer; touch-action:none; user-select:none; -webkit-user-select:none; -webkit-touch-callout:none; }
  .range-stepper button::before,.range-stepper button.range-step-plus::after{ content:""; position:absolute; left:50%; top:50%; width:11px; height:2px; border-radius:2px; background:currentColor; transform:translate(-50%,-50%); }
  .range-stepper button.range-step-plus::after{ transform:translate(-50%,-50%) rotate(90deg); }
  .range-stepper.preview-stepper button{ display:grid; place-items:center; }
  .range-stepper.preview-stepper button::before,.range-stepper.preview-stepper button::after{ display:none; }
  .range-stepper.preview-stepper button svg{ width:18px; height:18px; fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; pointer-events:none; }
  .range-stepper button:hover{ background:var(--panel-2); border-color:var(--accent); }
  .range-stepper button:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }
  .slider-row .range-stepper{ flex:1; max-width:440px; }
  .intensity-row .range-stepper{ max-width:292px; }
  .settings-sliders .slider-row .range-stepper{ grid-column:1; grid-row:1; width:100%; max-width:none; }
  .settings-sliders .slider-row .range-stepper input[type=range]{ grid-column:auto; grid-row:auto; margin:0; width:100%; max-width:none; }
  .scrubber-row .time-label{ flex:0 0 104px; width:104px; white-space:nowrap; }
  .scrubber-row .range-stepper{ flex:1; }
  @media (max-width:700px){ .range-stepper{ gap:5px; } .range-stepper button{ flex-basis:23px; width:23px; height:23px; } }
  input[type=range]{ -webkit-appearance:none;''')

replace_once('  /* ---------------- playback ---------------- */', '''  // Give every range input, including the dynamically created text controls,
  // one-unit adjustments without changing its native drag step or input event.
  document.querySelectorAll('input[type="range"]').forEach(input=>{
    const stepper = document.createElement('div');
    stepper.className = 'range-stepper';
    if(input.id === 'scrubber') stepper.classList.add('preview-stepper');
    const label = input.closest('.field, .slider-row')?.querySelector('label')?.textContent.trim() ||
      (input.id === 'scrubber' ? 'وقت المعاينة' : input.id);
    function adjust(direction){
      if(input.disabled) return;
      const min = Number(input.min || 0);
      const max = Number(input.max || 100);
      const next = Math.max(min, Math.min(max, Number(input.value) + direction));
      if(next === Number(input.value)) return;
      input.value = String(next);
      input.dispatchEvent(new Event('input', {bubbles:true}));
    }
    function makeButton(direction, action){
      const button = document.createElement('button');
      button.type = 'button';
      button.className = direction > 0 ? 'range-step-plus' : 'range-step-minus';
      if(input.id === 'scrubber'){
        const arrows = direction > 0 ? 'M3 4l5 5-5 5 M9 4l5 5-5 5' : 'M15 4l-5 5 5 5 M9 4l-5 5 5 5';
        button.innerHTML = `<svg viewBox="0 0 18 18" aria-hidden="true"><path d="${arrows}"/></svg>`;
      }
      button.setAttribute('aria-label', action + ' ' + label);
      let holdDelay, repeatInterval;
      function stop(){
        clearTimeout(holdDelay);
        clearInterval(repeatInterval);
      }
      button.addEventListener('pointerdown', event=>{
        if(event.button !== 0) return;
        event.preventDefault();
        stop();
        adjust(direction);
        holdDelay = setTimeout(()=>{
          repeatInterval = setInterval(()=>adjust(direction), 75);
        }, 350);
      });
      button.addEventListener('pointerup', stop);
      button.addEventListener('pointercancel', stop);
      button.addEventListener('pointerleave', stop);
      window.addEventListener('blur', stop);
      button.addEventListener('click', event=>{
        if(event.detail === 0) adjust(direction); // Keyboard and assistive tech.
      });
      return button;
    }
    input.before(stepper);
    stepper.append(makeButton(-1, 'تقليل'), input, makeButton(1, 'زيادة'));
    if(input.id !== 'scrubber'){
      const originalValue = Number(input.defaultValue);
      let firstThumbDown = false, lastDownAt = 0, secondThumbDown = false;
      let secondDownX = 0, secondDownY = 0;
      function isOnThumb(event){
        const rect = input.getBoundingClientRect();
        const min = Number(input.min || 0), max = Number(input.max || 100);
        const fraction = max > min ? (Number(input.value) - min) / (max - min) : 0;
        const direction = getComputedStyle(input).direction === 'rtl' ? 1 - fraction : fraction;
        const centerX = rect.left + 8 + Math.max(0, rect.width - 16) * direction;
        return Math.abs(event.clientX - centerX) <= 13 &&
          Math.abs(event.clientY - (rect.top + rect.height / 2)) <= 16;
      }
      function restoreDefault(){
        const min = Number(input.min || 0), max = Number(input.max || 100);
        const value = Math.max(min, Math.min(max, originalValue));
        input.value = String(value);
        input.dispatchEvent(new Event('input', {bubbles:true}));
      }
      input.addEventListener('pointerdown', event=>{
        if(event.button !== 0) return;
        const onThumb = isOnThumb(event);
        secondThumbDown = onThumb && firstThumbDown && event.timeStamp - lastDownAt < 650;
        firstThumbDown = onThumb;
        lastDownAt = event.timeStamp;
        secondDownX = event.clientX; secondDownY = event.clientY;
      });
      input.addEventListener('pointerup', event=>{
        // On touch screens, browsers may not emit dblclick after two taps.
        if(event.pointerType === 'touch' && secondThumbDown &&
           Math.hypot(event.clientX - secondDownX, event.clientY - secondDownY) < 10){
          restoreDefault();
          secondThumbDown = false;
        }
      });
      input.addEventListener('pointercancel', ()=>{ secondThumbDown = false; });
      input.addEventListener('dblclick', event=>{
        if(!secondThumbDown) return; // A double-click on the track keeps its native behavior.
        event.preventDefault();
        restoreDefault();
        secondThumbDown = false;
      });
    }
  });

  /* ---------------- playback ---------------- */''')
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

# Keep the existing sliders and their listeners intact. The suggestion is
# offered only after all dynamically generated controls are initialized.
replace_once('          <div id="textLayersWrap" class="text-columns"></div>',
             '''          <div id="textLayersWrap" class="text-columns"></div>
          <div id="textLayoutSuggestion" class="text-layout-suggestion" hidden>
            <span id="textSuggestionMessage">اقتراح: عنوان بسطر واحد ونص فرعي بسطرين — حجم 63/60 وتباعد 20/15 بكسل</span>
            <button type="button" id="applyTextLayoutSuggestion">تطبيق الاقتراح</button>
          </div>''')
replace_once('  .text-layer-card{', '''  .text-layout-suggestion{ display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-top:12px; padding:10px 12px; border:1px solid #d5cff0; border-radius:10px; background:#F3EAFD; color:var(--text); font-size:14px; line-height:1.5; }
  .text-layout-suggestion[hidden],.text-layout-suggestion button[hidden]{ display:none; }
  .text-layout-suggestion button{ flex:none; border:1px solid var(--accent); background:var(--panel); color:var(--accent); border-radius:8px; padding:7px 10px; font:600 14px 'Tajawal',sans-serif; cursor:pointer; }
  .text-layout-suggestion button:hover{ background:var(--panel-2); }
  .text-layer-card{''')
replace_once('  /* ---------------- playback ---------------- */', '''  // The subline may never exceed the headline size minus three pixels.
  // Allow 17px at the headline's existing 20px minimum.
  const headlineSizeSlider = textLayersWrap.querySelector('input[data-field="size"][data-idx="0"]');
  const sublineSizeSlider = textLayersWrap.querySelector('input[data-field="size"][data-idx="1"]');
  function syncSublineSizeLimit(){
    const limit = state.texts[0].size - 3;
    sublineSizeSlider.min = '17';
    sublineSizeSlider.max = String(limit);
    if(state.texts[1].size > limit){
      sublineSizeSlider.value = String(limit);
      sublineSizeSlider.dispatchEvent(new Event('input', {bubbles:true}));
    }
  }
  headlineSizeSlider.addEventListener('input', syncSublineSizeLimit);
  syncSublineSizeLimit();

  // Optional 2+2 to 1+2 text layout. Attach after the slider controls so
  // suggestion failures cannot prevent their creation.
  const textSuggestion = document.getElementById('textLayoutSuggestion');
  const textSuggestionMessage = document.getElementById('textSuggestionMessage');
  const applyTextSuggestion = document.getElementById('applyTextLayoutSuggestion');
  function updateTextSuggestion(){
    const [headline, subline] = state.texts;
    if(!headline?.text?.trim() || !subline?.text?.trim()){
      textSuggestion.hidden = true;
      return;
    }
    const lines = (layer, size, font) => wrapLines(layer.text, `${size}px '${font}'`, TEXT_BOX.w).length;
    const fits = lines(headline, headline.size, 'PFDinXBlack') === 2 &&
      lines(subline, subline.size, 'PFDinMedium') === 2 &&
      lines(headline, 63, 'PFDinXBlack') === 1 &&
      lines(subline, 60, 'PFDinMedium') === 2;
    textSuggestion.hidden = !fits;
    if(fits){
      textSuggestionMessage.textContent = 'اقتراح: عنوان بسطر واحد ونص فرعي بسطرين — حجم 63/60 وتباعد 20/15 بكسل';
      applyTextSuggestion.hidden = false;
    }
  }
  textLayersWrap.addEventListener('input', event=>{
    if(event.target.matches('textarea[data-field="text"],input[data-field="size"]')) updateTextSuggestion();
  });
  applyTextSuggestion.addEventListener('click', ()=>{
    if(textSuggestion.hidden) return;
    const changes = [
      [0, 'size', 63], [1, 'size', 60],
      [0, 'lineSpacing', 20], [1, 'lineSpacing', 15]
    ];
    const controls = changes.map(([idx, field]) =>
      textLayersWrap.querySelector(`input[data-field="${field}"][data-idx="${idx}"]`));
    if(controls.some(control => !control)){
      textSuggestionMessage.textContent = 'تعذّر تطبيق الاقتراح؛ يرجى إعادة تحميل الصفحة';
      return;
    }
    changes.forEach(([, , value], idx)=>{
      controls[idx].value = String(value);
      controls[idx].dispatchEvent(new Event('input', {bubbles:true}));
    });
    textLayersWrap.querySelectorAll('.text-layer-card').forEach(card=>{
      if(!card.querySelector('.adv-body').classList.contains('open')) card.querySelector('.adv-toggle').click();
    });
    textSuggestion.hidden = false;
    textSuggestionMessage.textContent = '✓ تم تطبيق حجم 63/60 وتباعد 20/15 بكسل — يمكنك تعديل القيم يدوياً';
    applyTextSuggestion.hidden = true;
  });
  document.fonts.ready.then(updateTextSuggestion).catch(()=>{});

  /* ---------------- playback ---------------- */''')

path.write_text(html, encoding="utf-8")
print("Automatic two-line headline spacing applied")

p=path
# Apply the approved Snapchat header icon using the existing theme gradient.
import re
text=p.read_text(encoding='utf-8')
text,n=re.subn(r'  \.brand-logo\{[^\n]+', '  .brand-logo{flex:none;margin-inline-start:auto;width:clamp(44px,5vw,56px);aspect-ratio:1;border-radius:19%;background:var(--accent-grad);overflow:hidden;}\\n  .brand-logo svg{display:block;width:100%;height:100%;}',text,count=1)
assert n == 1, 'Expected header logo style'
old='<div class="brand-logo" role="img" aria-label="MBC"></div>'
assert old in text, 'Expected MBC header'
text=text.replace(old,Path('snapchat-header.html').read_text(encoding='utf-8'),1)
p.write_text(text,encoding='utf-8')
