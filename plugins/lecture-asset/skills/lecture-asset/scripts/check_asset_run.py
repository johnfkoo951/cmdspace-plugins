#!/usr/bin/env python3
"""Read-only closing gate for one lecture-asset run.
Catches misses seen in real runs: the skill changed mid-run, new cards without a link into the
shared card library, obsidian:// URIs with a wrong path, ambiguous basename links, a stale
corrections header, a hub without its retrospective link, and a raw transcript that was edited.
Usage (vault root):
 python3 check_asset_run.py --root "$PWD" --hub "<projects>/<event>/<hub>.lecture.md" --cards-dir "<cards>/<event>" \
  --started-at 2026-01-01T12:00 [--shared "<shared>" ...] [--corrections "<corrections.yaml>"] \
  [--touched file.md ... | --touched-from list.txt] [--preserve RAW::NOTE.md ...]
--shared: folders whose notes count as the shared library (default: the parent of --cards-dir).
--preserve: RAW is the exact source text (recorder export, or the pasted block saved to a file);
 split a pasted block into its parts first (summary part -> AI summary note, transcript part -> transcript note).
Exit: 0 no FAIL; 1 FAIL present; 2 bad input. WARN lines need a human look but do not fail.
"""
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse,parse_qs
import argparse,hashlib,os,re,sys
BASE=None  # parent of all vaults, for obsidian:// checks; default is the parent of --root
SKIP_DIRS={'.obsidian','.trash','.git','.smart-env','node_modules','__pycache__'}
WL=re.compile(r'\[\[([^\[\]\n]+?)\]\]')
URI=re.compile(r'obsidian://[^\s)\]"\'>]+')
SKILL_FILE=Path(__file__).resolve().parent.parent/'SKILL.md'
LINKS_HEAD=re.compile(r'^## (?:연결|Links|Connections)\s*$',re.M)
RETRO=re.compile(r'회고|retrospective',re.I)
CORR_SECTION=re.compile(r'^# (\d{4}-\d{2}-\d{2}) (?:추가|added)',re.M|re.I)
out={'FAIL':[],'WARN':[],'OK':[]}
def say(level,msg):out[level].append(msg)

def index_vault(root):
 by_name={};paths=set()
 for d,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[x for x in dirs if x not in SKIP_DIRS]
  for n in files:
   rel=os.path.relpath(os.path.join(d,n),root).replace(os.sep,'/');paths.add(rel)
   key=n[:-3] if n.endswith('.md') else n
   by_name.setdefault(key,[]).append(rel)
 return by_name,paths

def strip_code(text):
 text=re.sub(r'^(`{3,}|~{3,}).*?^\1',' ',text,flags=re.S|re.M)
 return re.sub(r'`[^`\n]*`',' ',text)

def resolve(link,by_name,paths):
 """Return (status, matches). Mirrors Obsidian: exact path, path suffix, else unique basename."""
 t=link.replace('\\|','|').split('|')[0].split('#')[0].strip()
 if not t:return 'self',[]
 if '/' in t:
  cand=[p for p in paths if p in (t,t+'.md') or p.endswith('/'+t) or p.endswith('/'+t+'.md')]
  return ('ok' if len(cand)==1 else 'missing' if not cand else 'ambiguous'),cand
 m=by_name.get(t,[])
 return ('ok' if len(m)==1 else 'missing' if not m else 'ambiguous'),m

def check_links(rel,text,by_name,paths):
 targets=[]
 for raw in WL.findall(strip_code(text)):
  st,m=resolve(raw,by_name,paths)
  if st=='ok':targets.append(m[0])
  elif st=='ambiguous':say('FAIL',f'{rel}: [[{raw}]] matches {len(m)} files - use a path-qualified link ({", ".join(m[:3])})')
  elif st=='missing':say('WARN',f'{rel}: [[{raw}]] unresolved - confirm it is an intended seed, not a typo')
 for u in URI.findall(strip_code(text)):check_uri(rel,u)
 return targets

def check_uri(rel,u):
 p=urlparse(u);q=parse_qs(p.query);vault=(q.get('vault') or [''])[0]
 vroot=BASE/vault if vault else None
 if not vroot or not vroot.is_dir():say('WARN',f'{rel}: URI vault "{vault}" not found under {BASE}: {u[:90]}');return
 fp=(q.get('filepath') or [None])[0];f=(q.get('file') or [None])[0]
 if fp is not None:ok=(vroot/fp).is_file()
 elif f is not None:ok=(vroot/f).is_file() or (vroot/(f+'.md')).is_file()
 else:return
 if ok:say('OK',f'{rel}: URI ok -> {vault}/{fp or f}')
 else:say('FAIL',f'{rel}: URI target missing in {vault}: {fp or f}')

def frontmatter(text):
 m=re.match(r'^---\n(.*?)\n---',text,re.S);return m.group(1) if m else ''

def check_skill_drift(skill,started):
 if not skill.is_file():say('WARN',f'skill file not found: {skill}');return
 mt=datetime.fromtimestamp(skill.stat().st_mtime)
 if started and mt>started:say('FAIL',f'SKILL.md changed during the run ({mt:%m-%d %H:%M} > start) - re-read it and apply new steps')
 else:say('OK','skill drift checked')

def rel_dir(root,p):
 return (root/p).resolve().relative_to(root).as_posix().rstrip('/')+'/'

def main():
 ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
 ap.add_argument('--root',type=Path,default=Path.cwd());ap.add_argument('--hub',required=True)
 ap.add_argument('--cards-dir',required=True);ap.add_argument('--started-at')
 ap.add_argument('--shared',nargs='*',default=[],help='vault-relative folders that count as the shared card library')
 ap.add_argument('--corrections',help='vault-relative path of the STT corrections file, if you keep one')
 ap.add_argument('--touched',nargs='*',default=[]);ap.add_argument('--touched-from',help='file with one vault-relative path per line')
 ap.add_argument('--preserve',nargs='*',default=[],help='RAW::NOTE pairs, raw bytes must appear unchanged in NOTE')
 ap.add_argument('--vaults-base',type=Path,help='folder that holds all vaults (default: parent of --root)')
 ap.add_argument('--skill-file',type=Path,default=SKILL_FILE,help='SKILL.md to watch for mid-run changes')
 a=ap.parse_args();root=a.root.resolve()
 global BASE
 BASE=(a.vaults_base or root.parent).resolve()
 if a.touched_from:a.touched+= [l.strip() for l in Path(a.touched_from).read_text('utf-8').splitlines() if l.strip()]
 hub=root/a.hub;cards_dir=root/a.cards_dir
 if not hub.is_file() or not cards_dir.is_dir():print('hub or cards-dir not found');return 2
 started=datetime.fromisoformat(a.started_at) if a.started_at else None
 if not started:say('WARN','no --started-at: skill changes during the run cannot be checked')
 by_name,paths=index_vault(root)
 check_skill_drift(a.skill_file,started)
 hub_rel=hub.relative_to(root).as_posix();hub_stem=hub.name[:-3];hub_text=hub.read_text('utf-8')
 cards_rel=rel_dir(root,a.cards_dir)
 shared=[rel_dir(root,s) for s in a.shared] or [rel_dir(root,Path(a.cards_dir).parent)]
 # hub
 check_links(hub_rel,hub_text,by_name,paths)
 if not RETRO.search(hub_text):say('FAIL','hub: no link to the retrospective note (step 8)')
 if not re.search(r'^transcript:',frontmatter(hub_text),re.M):say('FAIL','hub: frontmatter transcript: missing')
 # cards: every card in the event folder + touched lecture-chunk notes
 accum=[root/t for t in a.touched if (root/t).is_file() and not (root/t).is_relative_to(cards_dir) and re.search(r'^type:\s*"?lecture-chunk',(root/t).read_text('utf-8'),re.M)]
 cards=sorted(cards_dir.glob('*.md'))+accum
 n_new=len(list(cards_dir.glob('*.md')))
 cm=re.search(r'^chunkCount:\s*(\d+)',frontmatter(hub_text),re.M)
 if cm and int(cm.group(1)) not in (n_new,n_new+len(accum)):say('WARN',f'hub chunkCount={cm.group(1)} but cards are {n_new} new + {len(accum)} accumulated')
 seen=set()
 for c in cards:
  if c in seen:continue
  seen.add(c);rel=c.relative_to(root).as_posix();text=c.read_text('utf-8')
  if hub_stem not in frontmatter(text):say('FAIL',f'{rel}: lectures: does not include the hub')
  if not LINKS_HEAD.search(text):say('FAIL',f'{rel}: no "## 연결" (links) section')
  if '[!quote]' not in text:say('WARN',f'{rel}: no [!quote] lecture excerpt')
  tg=check_links(rel,text,by_name,paths)
  outside=[t for t in tg if any(t.startswith(s) for s in shared) and not t.startswith(cards_rel) and t!=rel]
  if rel.startswith(cards_rel) and not outside:say('FAIL',f'{rel}: no link into the shared card library outside this event folder')
 say('OK',f'cards checked: {len(seen)} ({n_new} in event folder)')
 # other touched notes
 for t in a.touched:
  f=root/t
  if not f.is_file():say('FAIL',f'touched file missing: {t}');continue
  if f.suffix=='.md' and f not in seen and f!=hub:check_links(t,f.read_text('utf-8'),by_name,paths)
 # corrections header
 if a.corrections:
  cr=root/a.corrections
  if not cr.is_file():say('WARN',f'corrections file not found: {a.corrections}')
  else:
   ct=cr.read_text('utf-8');m=re.search(r'Last updated:\s*(\d{4}-\d{2}-\d{2})',ct)
   newest=max(CORR_SECTION.findall(ct),default='')
   if m and m.group(1)<newest:say('FAIL',f'corrections header says {m.group(1)} but newest section is {newest} - bump "Last updated"')
   else:say('OK','corrections header date current')
 # raw transcript preserved byte-for-byte
 for pair in a.preserve:
  rp,_,np_=pair.partition('::');raw=Path(rp).read_bytes().strip();note=(root/np_).read_bytes()
  h=hashlib.sha256(raw).hexdigest()[:16];ok=raw in note
  say('OK' if ok else 'FAIL',f'{np_}: raw source {"preserved" if ok else "NOT preserved"} byte-for-byte (sha256 {h}, {len(raw)} bytes)')
 for lv in ('FAIL','WARN','OK'):
  for m in out[lv]:print(f'{lv}  {m}')
 print(f"summary: FAIL={len(out['FAIL'])} WARN={len(out['WARN'])} OK={len(out['OK'])}")
 return 1 if out['FAIL'] else 0
if __name__=='__main__':raise SystemExit(main())
