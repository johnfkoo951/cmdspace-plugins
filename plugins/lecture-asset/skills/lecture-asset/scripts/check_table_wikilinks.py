#!/usr/bin/env python3
"""Read-only check of wikilinks inside Markdown tables.
Usage: python3 check_table_wikilinks.py --root VAULT file.md [folder ...] [--exclude PREFIX ...] [--json]
Transcript/raw notes are skipped (type: transcript or a ' - 전사본' / ' - AI 요약' file name).
--exclude skips vault-relative path prefixes, e.g. a folder of imported references.
Requires markdown-it-py. Does not repair targets, seeds, raw sources, or files.
Exit: 0 clean in checked scope; 1 findings; 2 read/dependency error.
"""
from pathlib import Path
import argparse,json,os,re,sys
try:
 from markdown_it import MarkdownIt
except ImportError:
 raise SystemExit('Missing markdown-it-py. Install it in the selected Python environment; no files were checked.')
WL=re.compile(r'!?\[\[((?:(?!\[\[|\]\])[^\n])+)\]\]')
PARSER=MarkdownIt('commonmark').enable('table')

def escaped(text,index):
 n=0;index-=1
 while index>=0 and text[index]=='\\':n+=1;index-=1
 return n%2==1

def plain(line):return re.sub(r'^\s*(?:>\s*)+','',line).strip()

def cells(line):
 z=plain(line);out=[];start=0
 for i,c in enumerate(z):
  if c=='|' and not escaped(z,i):out.append(z[start:i].strip());start=i+1
 out.append(z[start:].strip())
 if out and out[0]=='':out.pop(0)
 if out and out[-1]=='':out.pop()
 return out

def protected_lines(text):
 lines=text.splitlines(keepends=True);mask=[False]*len(lines)
 front=bool(lines and lines[0].lstrip('﻿').strip()=='---');fence=None;raw=False;raw_heading=False
 for i,line in enumerate(lines):
  z=plain(line);f=re.match(r'^(`{3,}|~{3,})',z)
  if front:
   mask[i]=True
   if i and line.strip()=='---':front=False
   continue
  if fence:
   mask[i]=True
   if f and f[1][0]==fence[0] and len(f[1])>=len(fence):fence=None
   continue
  if raw_heading:mask[i]=True;continue
  if raw:
   mask[i]=True
   if re.search(r'(?:<!--|%%)\s*(?:RAW[ _-]*ORIGINAL[ _-]*(?:END|STOP)|(?:END|STOP)[ _-]*RAW)',line,re.I):raw=False
   continue
  if f:fence=f[1];mask[i]=True;continue
  if re.search(r'(?:<!--|%%)\s*(?:RAW[ _-]*ORIGINAL[ _-]*(?:BEGIN|START)|(?:BEGIN|START)[ _-]*RAW)',line,re.I):
   mask[i]=True;raw=not bool(re.search(r'(?:RAW[ _-]*ORIGINAL[ _-]*(?:END|STOP)|(?:END|STOP)[ _-]*RAW)',line,re.I));continue
  if re.match(r'^#{1,6}\s+(?:Raw Original Content|Original Transcript|원문 원본|원문 보존)\s*$',z,re.I):raw_heading=True;mask[i]=True
 return lines,mask

def code_ranges(line):
 runs=list(re.finditer(r'`+',line));out=[];i=0
 while i<len(runs):
  op=runs[i]
  if escaped(line,op.start()):i+=1;continue
  j=next((j for j in range(i+1,len(runs)) if len(runs[j][0])==len(op[0]) and not escaped(line,runs[j].start())),None)
  if j is None:i+=1;continue
  out.append((op.start(),runs[j].end()));i=j+1
 return out

def markdown_link_ranges(line):
 out=[];i=0
 while i<len(line):
  if line[i]!='[' or escaped(line,i):i+=1;continue
  depth=1;j=i+1
  while j<len(line) and depth:
   if not escaped(line,j):
    if line[j]=='[':depth+=1
    elif line[j]==']':depth-=1
   j+=1
  if depth or j>=len(line) or line[j]!='(':i+=1;continue
  d=1;k=j+1
  while k<len(line) and d:
   if not escaped(line,k):
    if line[k]=='(':d+=1
    elif line[k]==')':d-=1
   k+=1
  if d:i+=1;continue
  out.append((i,k));i=k
 return out

def links(line):
 cr=code_ranges(line)+markdown_link_ranges(line)
 for m in WL.finditer(line):
  if escaped(line,m.start()) or any(a<=m.start()<b for a,b in cr):continue
  yield m

def tables(text):
 ls,mask=protected_lines(text)
 # Keep original line numbers; protect data before asking the real table tokenizer.
 safe=''.join(('\n' if x.endswith('\n') else '') if m else x for x,m in zip(ls,mask))
 spans=[]
 for t in PARSER.parse(safe):
  if t.type=='table_open' and t.map:spans.append(tuple(t.map))
 return ls,mask,spans

def skip_file(path,root,text,exclude=()):
 rel=path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
 if any(rel.startswith(x) for x in exclude):return 'excluded scope'
 fm=text.split('---',2)[1] if text.startswith('---\n') and len(text.split('---',2))>=3 else ''
 if re.search(r'^type:\s*[\"\']?(?:transcript|raw-source|raw_source|recording)[\"\']?\s*$',fm,re.M):return 'raw/transcript type'
 if re.search(r' - (?:전사본|AI 요약|Transcript|AI Summary)(?: [A-Z0-9]+)?\.md$',path.name):return 'immutable source-note filename'
 return None

def inspect_text(text):
 ls,mask,spans=tables(text);issues=[];checked=0
 for a,b in spans:
  # Scope is tables with active wikilinks or damaged bracket remnants, not all table styles.
  if not any('[[' in ls[i] or ']]' in ls[i] for i in range(a,b)):continue
  checked+=1;width=len(cells(ls[a]))
  for i in range(a,b):
   if mask[i]:continue
   row=ls[i];remaining=row
   for m in links(row):
    inner=m[1]
    bad=[j for j,c in enumerate(inner) if c=='|' and not escaped(inner,j)]
    if bad:issues.append({'line':i+1,'kind':'unescaped_alias_pipe','message':'Inside a table use [[target\\|alias]], including embeds.'})
    first=inner.find('|')
    if first>=0:
     n=0;j=first-1
     while j>=0 and inner[j]=='\\':n+=1;j-=1
     if n>1:issues.append({'line':i+1,'kind':'overescaped_alias_separator','message':'Use exactly one backslash before the alias separator; extra backslashes can become part of the link target.'})
    remaining=remaining.replace(m[0],'')
   for x,y in sorted(code_ranges(remaining)+markdown_link_ranges(remaining),reverse=True):remaining=remaining[:x]+remaining[y:]
   if re.search(r'(?<!\\)(?:\[\[|\]\])',remaining):issues.append({'line':i+1,'kind':'unbalanced_or_nested_wikilink','message':'Inspect split, missing or nested brackets; do not guess a target.'})
   if i!=a+1 and len(cells(row))!=width:issues.append({'line':i+1,'kind':'table_cell_count','message':f'Header has {width} cells; this row has {len(cells(row))}. Check alias escapes and phantom columns.'})
 return {'issues':issues,'tables_checked':checked,'protected_lines':sum(mask)}

def paths_from(inputs):
 seen=set()
 for q in inputs:
  p=Path(q)
  if p.is_file():candidates=[p]
  elif p.is_dir():
   candidates=[]
   for root,dirs,files in os.walk(p,followlinks=False):
    dirs[:]=[d for d in dirs if not d.startswith('.') and d not in ['node_modules','__pycache__']]
    candidates += [Path(root)/n for n in files if n.endswith('.md')]
  else:yield p;continue
  for f in candidates:
   r=f.resolve()
   if r not in seen:seen.add(r);yield f

def format_wikilink(target, alias=None, *, in_table=False, embed=False):
 """Format raw target/label strings. Does not resolve or create any file."""
 if not target or target != target.strip() or target.endswith('\\') or any(x in target for x in ('|','[[',']]','\n','\r')):
  raise ValueError('Use an exact unpadded target; pass its label separately.')
 if alias is not None and any(x in alias for x in ('[[',']]','\n','\r')):
  raise ValueError('A label must remain within one wikilink and one line.')
 body=target if alias is None else target+'|'+alias
 if in_table:body=''.join(('\\' if c=='|' and not escaped(body,i) else '')+c for i,c in enumerate(body))
 return ('!' if embed else '')+'[['+body+']]'

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path.cwd());ap.add_argument('--json',action='store_true');ap.add_argument('--exclude',nargs='*',default=[]);ap.add_argument('paths',nargs='+');args=ap.parse_args();root=args.root.resolve()
 report={'files_checked':0,'tables_checked':0,'skipped':[],'issues':[],'errors':[]}
 for path in paths_from(args.paths):
  try:text=path.read_bytes().decode('utf-8')
  except (OSError,UnicodeError) as e:report['errors'].append({'file':str(path),'error':str(e)});continue
  reason=skip_file(path.resolve(),root,text,args.exclude)
  if reason:report['skipped'].append({'file':str(path),'reason':reason});continue
  if '[[' not in text and ']]' not in text:report['files_checked']+=1;continue
  result=inspect_text(text);report['files_checked']+=1;report['tables_checked']+=result['tables_checked']
  report['issues'] += [{'file':str(path),**i} for i in result['issues']]
 if args.json:print(json.dumps(report,ensure_ascii=False,indent=2))
 else:
  print(f"files={report['files_checked']} tables={report['tables_checked']} issues={len(report['issues'])} skipped={len(report['skipped'])} read_errors={len(report['errors'])}")
  for i in report['issues']:print(f"{i['file']}:{i['line']}: {i['kind']}: {i['message']}")
  for e in report['errors']:print(e)
 return 2 if report['errors'] else 1 if report['issues'] else 0
if __name__=='__main__':raise SystemExit(main())
