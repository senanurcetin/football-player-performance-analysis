#!/usr/bin/env python3
"""Deterministic offline repair of five NEXUS Football Power BI visual formats.

Uses existing Desktop captures as defect evidence; no new screenshots requested.
No BigQuery work, no DAX logic edit, no model/relationship or data deletion.
"""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

DEFAULT=Path(r"C:\Users\MONSTER\Documents\NEXUS-Football-PBI\FootballPlayerAnalysis")
ITEMS={
 "Report/definition/pages/292e3d92e92693c05047/visuals/0839d8ed3d7479a01f32/visual.json":
  ('percent_axis','1000000D','1D',2),
 "Report/definition/pages/tooltip_transfer_p011/visuals/tt011_stats_0001/visual.json":
  ('tooltip_money','€0.0M','€0.0,,"M"',1),
 "Report/definition/pages/tooltip_pred_p012/visuals/tt012_stats_0001/visual.json":
  ('tooltip_money','€0.0M','€0.0,,"M"',1),
 "Report/definition/pages/1f4c5c8000149b2e2be8/visuals/3ccd5a45594119af9bb7/visual.json":
  ('donut_label',"'Category, percent of total'","'Percent of total'",1),
}
def sha(b):return hashlib.sha256(b).hexdigest()
def patch(root):
 changes={}
 metadata={}
 for rel,(kind,before,after,n) in ITEMS.items():
  p=root/rel
  if not p.is_file():raise RuntimeError("Expected visual file missing: "+rel)
  raw=p.read_bytes()
  original=json.loads(raw.decode("utf-8-sig"))
  assert 'visual' in original and 'query' in original['visual']
  if kind=='percent_axis':
   obj=original['visual']['objects']
   for section in ('valueAxis','labels'):
    value=obj[section][0]['properties']['labelDisplayUnits']['expr']['Literal']['Value']
    if value not in (before,after):raise RuntimeError(f"Unexpected {section} units: {value}")
   old=json.dumps(before,ensure_ascii=False).encode("utf-8")
   new=json.dumps(after,ensure_ascii=False).encode("utf-8")
  elif kind=='tooltip_money':
   projs=original['visual']['query']['queryState']['Values']['projections']
   x=[f for f in projs if f.get('format') in (before,after)]
   if len(x)!=1:raise RuntimeError(f"Expected one currency format: {rel}")
   assert "Average " in x[0].get('queryRef','')
   old=json.dumps(before,ensure_ascii=False).encode("utf-8")
   new=json.dumps(after,ensure_ascii=False).encode("utf-8")
  elif kind=='donut_label':
   assert original['visual']['visualType']=='donutChart'
   old=json.dumps(before,ensure_ascii=False).encode("utf-8")
   new=json.dumps(after,ensure_ascii=False).encode("utf-8")
  else:raise RuntimeError("Unrecognized patch")
  old_hits=raw.count(old)
  new_hits=raw.count(new)
  target_fixed=(kind=='percent_axis' and all(
   original['visual']['objects'][s][0]['properties']['labelDisplayUnits']['expr']['Literal']['Value']==after
   for s in ('valueAxis','labels')))
  if old_hits==0 and (target_fixed or new_hits==n):
   metadata[rel]='already_fixed'
   continue
  if old_hits!=n:raise RuntimeError(f"Unexpected source format count for {rel}: old={old_hits}, expected={n}")
  corrected=raw.replace(old,new)
  afterjson=json.loads(corrected.decode("utf-8-sig"))
  expected_obj=json.loads(raw.decode("utf-8-sig"))
  # Field projection and measure name are identical before and after.
  if kind=='percent_axis':
   for section in ('valueAxis','labels'):
    expected_obj['visual']['objects'][section][0]['properties']['labelDisplayUnits']['expr']['Literal']['Value']=after
  elif kind=='tooltip_money':
   for projection in expected_obj['visual']['query']['queryState']['Values']['projections']:
    if projection.get('format')==before:projection['format']=after
  elif kind=='donut_label':
   expected_obj['visual']['objects']['labels'][0]['properties']['labelStyle']['expr']['Literal']['Value']=after
  if expected_obj!=afterjson:raise RuntimeError("Unexpected JSON change "+rel)
  changes[p]=(raw,corrected)
  metadata[rel]=kind
 return changes,metadata

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--apply',action='store_true')
 parser.add_argument('--project',type=Path,default=DEFAULT)
 args=parser.parse_args()
 root=args.project
 if not (root/'FootballPlayerAnalysis.pbip').is_file():raise RuntimeError('PBIP descriptor missing')
 allvisuals=list((root/'Report/definition/pages').rglob('visual.json'))
 if len(allvisuals)!=308:raise RuntimeError(f'Expected 308 original visuals, got {len(allvisuals)}')
 changes,metadata=patch(root)
 print('AUDITED_VISUALS',len(allvisuals),'TARGETED',len(metadata),'NEED_PATCH',len(changes))
 print('TARGETS',json.dumps(metadata,ensure_ascii=False))
 if not args.apply:
  print('VISUAL_FORMAT_PREFLIGHT_OK_NO_CHANGES')
  return
 if not changes:
  print('VISUAL_FORMAT_ALREADY_FIXED')
  return
 if 'powerbi/workintech' not in root.as_posix().lower():
  # Guard the actual opened Desktop source against concurrent edits.
  proc=subprocess.run(['tasklist','/FI','IMAGENAME eq PBIDesktop.exe','/NH'],capture_output=True,text=True,timeout=15)
  if 'pbidesktop.exe' in proc.stdout.lower():raise RuntimeError('Power BI Desktop must be closed before patching active project files')
 files=sorted(f for f in root.rglob('*') if f.is_file() and '.pbi' not in f.relative_to(root).parts)
 if len(files)<900:raise RuntimeError('Full backup safeguard: too few files')
 original_sha={str(f.relative_to(root)):sha(f.read_bytes()) for f in files}
 backupdir=root.parent/'Backups'
 backupdir.mkdir(parents=True,exist_ok=True)
 stamp=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
 backup=backupdir/('FootballPlayerAnalysis-before-visual-format-fix-'+stamp+'.zip')
 with zipfile.ZipFile(backup,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.relative_to(root).as_posix())
 with zipfile.ZipFile(backup) as z:
  if z.testzip() is not None or len(z.namelist())!=len(files):
   raise RuntimeError('Backup integrity failed; no PBIP files changed')
 for path,(raw,corrected) in changes.items():
  if path.read_bytes()!=raw:raise RuntimeError('Concurrent change detected: '+str(path))
  with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.nexus-visual-format-',delete=False) as tmp:
   staged=Path(tmp.name);tmp.write(corrected)
  try:os.replace(staged,path)
  finally:
   if staged.exists():staged.unlink()
 remaining,_=patch(root)
 if remaining:raise RuntimeError('Post-edit residual defects; restore from '+str(backup))
 for f in allvisuals:json.loads(f.read_text('utf-8-sig'))
 assert len(list((root/'Report/definition/pages').rglob('visual.json')))==308
 actual={str(f.relative_to(root)) for f in files if sha(f.read_bytes())!=original_sha[str(f.relative_to(root))]}
 expected={str(p.relative_to(root)) for p in changes}
 if actual!=expected:raise RuntimeError('Unexpected PBIP changes; restore from '+str(backup))
 record={'status':'TARGETED_VISUAL_FORMAT_SOURCE_PATCH_PASS',
         'source_page_count':13,'source_visual_count':308,
         'changed_files':sorted(actual),'changed_types':dict(metadata),
         'full_backup':str(backup),
         'dax_measure_formulas_changed':False,
         'model_relationships_changed':False,
         'screenshots_reused':'27 October genuine Desktop captures; NO NEW SCREENSHOTS',
         'runtime_render_verified':False}
 audit=backupdir/('NEXUS-visual-format-repair-'+stamp+'.json')
 audit.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 print('TARGETED_VISUAL_FORMAT_SOURCE_PATCH_PASS',len(actual),'files')
 print('BACKUP',backup)
 print('AUDIT',audit)
 print('DESKTOP_RENDER_NOT_VERIFIED_NO_SCREENSHOT_REQUESTED')
if __name__=='__main__':
 try:main()
 except Exception as e:
  print('VISUAL_FORMAT_PATCH_STOPPED',type(e).__name__,str(e),file=__import__('sys').stderr)
  raise SystemExit(2)
