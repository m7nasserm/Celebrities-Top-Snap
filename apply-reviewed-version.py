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
