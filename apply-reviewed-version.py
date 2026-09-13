#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

p = Path(sys.argv[1])

# Preserve the existing reviewed patch set first.
subprocess.run([sys.executable, 'deploy_patch.py', str(p)], check=True)
text = p.read_text(encoding='utf-8')

# Add the shared two-tool navigation to the generated Celebrities page.
css_anchor = "  footer.note{ padding:14px 24px 26px; color:var(--muted); font-size:14.375px; line-height:1.8; border-top:1px solid var(--line); background:var(--panel); }\n"
css = '''  .tool-tabs{display:flex;align-items:center;gap:14px;white-space:nowrap;}\n  .tool-tabs a{display:inline-block;padding:4px 0 5px;border-bottom:3px solid transparent;color:var(--muted);font-size:22.5px;font-weight:500;text-decoration:none;line-height:1.3;}\n  .tool-tabs a:hover{color:var(--accent);}\n  .tool-tabs a[aria-current="page"]{color:var(--accent);border-bottom-color:var(--accent);font-weight:700;}\n  .tool-tabs span{color:var(--line);font-size:21px;user-select:none;}\n  .tool-tabs a:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px;}\n  @media(max-width:650px){\n    header{flex-wrap:wrap;}\n    header .mark{order:0;}\n    header .brand-logo{order:1;margin-inline-start:auto;}\n    header>div:nth-child(2){order:2;flex-basis:100%;min-width:0;}\n    .tool-tabs{gap:7px;max-width:100%;justify-content:center;}\n    .tool-tabs a{font-size:clamp(10px,3vw,15px);}\n    .tool-tabs span{font-size:15px;}\n  }\n'''
if '.tool-tabs{' not in text:
    if css_anchor not in text:
        raise SystemExit('Could not find CSS insertion point for tool tabs')
    text = text.replace(css_anchor, css_anchor + css, 1)

old_headers = [
    '''    <div>\n      <h1>Celebrities Top Snap</h1>\n      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس ٩:١٦</p>\n    </div>''',
    '''    <div>\n      <h1>Celebrities Top Snap</h1>\n      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس 9:16</p>\n    </div>'''
]
# Fixed tab positions: Celebrities first, Screenshot second.
new_header = '''    <div>\n      <nav class="tool-tabs" aria-label="Video tools"><a href="./" aria-current="page">Celebrities Top Snap</a><span aria-hidden="true">|</span><a href="screenshot.html">Screenshot Top Snap</a></nav>\n    </div>'''
for old_header in old_headers:
    if old_header in text:
        text = text.replace(old_header, new_header, 1)
        break
else:
    if 'class="tool-tabs"' not in text:
        raise SystemExit('Expected Celebrities header block not found')
    old_nav = '<nav class="tool-tabs" aria-label="Video tools"><a href="screenshot.html">Screenshot Top Snap</a><span aria-hidden="true">|</span><a href="./" aria-current="page">Celebrities Top Snap</a></nav>'
    fixed_nav = '<nav class="tool-tabs" aria-label="Video tools"><a href="./" aria-current="page">Celebrities Top Snap</a><span aria-hidden="true">|</span><a href="screenshot.html">Screenshot Top Snap</a></nav>'
    text = text.replace(old_nav, fixed_nav, 1)
    text = text.replace('      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس ٩:١٦</p>\n', '', 1)
    text = text.replace('      <p>صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس 9:16</p>\n', '', 1)

# Override only the preview scrubber's double-arrow buttons. The left button
# jumps to the first frame and the right button jumps to the last frame.
# Capture-phase listeners suppress the older one-step/press-and-hold behavior,
# while every other slider button keeps its existing behavior.
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
        raise SystemExit('Could not find </body> for preview edge-jump patch')
    return html[:marker] + edge_jump_script + '\n' + html[marker:]

def normalize_screenshot_tabs(html):
    desired = '<nav class="tool-tabs" aria-label="Video tools"><a href="./">Celebrities Top Snap</a><span aria-hidden="true">|</span><a href="screenshot.html" aria-current="page">Screenshot Top Snap</a></nav>'
    variants = [
        '<nav class="tool-tabs" aria-label="Video tools"><a href="screenshot.html" aria-current="page">Screenshot Top Snap</a><span aria-hidden="true">|</span><a href="./">Celebrities Top Snap</a></nav>',
        desired,
    ]
    for variant in variants:
        if variant in html:
            return html.replace(variant, desired, 1)
    raise SystemExit('Expected Screenshot Top Snap tab navigation not found')

text = inject_edge_jump(text)
p.write_text(text, encoding='utf-8')

# The Pages artifact is the public folder, so publish the second self-contained tool there too.
# Keep the same tab positions as Celebrities, switch only the active state, and apply
# the same preview-control behavior while copying it.
screenshot_source = Path('screenshot.html')
screenshot_target = p.parent / 'screenshot.html'
if not screenshot_source.exists():
    raise SystemExit('screenshot.html is missing from repository root')
screenshot_text = screenshot_source.read_text(encoding='utf-8')
screenshot_text = normalize_screenshot_tabs(screenshot_text)
screenshot_target.write_text(inject_edge_jump(screenshot_text), encoding='utf-8')

print('Top Snap tabs fixed in place; inactive tab stays muted; preview double arrows jump to start/end in both tools')
