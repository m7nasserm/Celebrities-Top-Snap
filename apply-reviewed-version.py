#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
p=Path(sys.argv[1])
# Preserve the existing reviewed patch set, then apply this approved copy change.
subprocess.run([sys.executable, 'deploy_patch.py', str(p)], check=True)
text=p.read_text(encoding='utf-8')
old='صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس ٩:١٦'
new='صورة + نص + موسيقى ← فيديو جاهز للنشر بمقاس 9:16'
if old not in text:
    raise SystemExit('Expected Arabic ٩:١٦ subtitle not found')
text=text.replace(old,new,1)
p.write_text(text,encoding='utf-8')
print('Reviewed version applied with Latin 9:16 subtitle')

# Apply the approved Snapchat header icon using the existing theme gradient.
import re
text=p.read_text(encoding='utf-8')
text,n=re.subn(r'  \.brand-logo\{[^\n]+', '  .brand-logo{flex:none;margin-inline-start:auto;width:clamp(44px,5vw,56px);aspect-ratio:1;border-radius:19%;background:var(--accent-grad);overflow:hidden;}\\n  .brand-logo svg{display:block;width:100%;height:100%;}',text,count=1)
assert n == 1, 'Expected header logo style'
old='<div class="brand-logo" role="img" aria-label="MBC"></div>'
assert old in text, 'Expected MBC header'
text=text.replace(old,Path('snapchat-header.html').read_text(encoding='utf-8'),1)
p.write_text(text,encoding='utf-8')
