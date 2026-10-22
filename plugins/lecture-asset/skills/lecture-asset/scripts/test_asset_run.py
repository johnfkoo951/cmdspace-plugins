#!/usr/bin/env python3
"""Regression fixtures for check_asset_run.py: each test reproduces a miss from a real run."""
import os,subprocess,sys,tempfile,time,unittest
from pathlib import Path
HERE=Path(__file__).parent
HUB='Outputs/Lectures/2026-01-01-sample/2026-01-01 샘플 행사 - 제목.lecture.md'
EV='Assets/Lecture Cards/2026-01-01 샘플 행사'
CARD=EV+'/주장은 문장으로 쓴다.md'
CORR='Assets/Transcription/corrections.yaml'
GOOD_CARD='---\ntype: lecture-chunk\nlectures:\n  - "[[2026-01-01 샘플 행사 - 제목.lecture]]"\n---\n# 주장\n> [!quote]+ 발췌\n\n## 연결\n- [[공통-01-원소화-기준]]\n'

class Gate(unittest.TestCase):
 def run_gate(self,files,extra=(),skill_age=None):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);root=base/'Main';(base/'Wiki/Concepts').mkdir(parents=True);(base/'Wiki/Concepts/Concept.md').write_text('x')
   skill=base/'SKILL.md';skill.write_text('x')
   if skill_age is not None:os.utime(skill,(time.time()-skill_age,)*2)
   base_files={HUB:'---\ntranscript: "[[t]]"\n---\n## 회고\n[[09-회고]]\n',CARD:GOOD_CARD,
    'Assets/Lecture Cards/_Shared/공통-01-원소화-기준.md':'x','Outputs/Lectures/2026-01-01-sample/09-회고.md':'x',
    'Outputs/Lectures/2026-01-01-sample/t.md':'x',CORR:'# Last updated: 2026-01-02\n# 2026-01-02 추가 — x\n'}
   base_files.update(files)
   for k,v in base_files.items():
    f=root/k;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(v)
   cmd=[sys.executable,str(HERE/'check_asset_run.py'),'--root',str(root),'--hub',HUB,'--cards-dir',EV,'--skill-file',str(skill),*extra]
   r=subprocess.run(cmd,capture_output=True,text=True,cwd=root)
   return r.returncode,r.stdout
 def test_clean_run_passes(self):self.assertEqual(self.run_gate({})[0],0)
 def test_card_without_shared_asset_fails(self):
  code,out=self.run_gate({CARD:GOOD_CARD.replace('[[공통-01-원소화-기준]]','[[09-회고]]')});self.assertEqual(code,1);self.assertIn('shared card library',out)
 def test_link_to_other_lecture_card_counts(self):
  other='Assets/Lecture Cards/2025-12-01 이전 행사/위임은 아는 일에만 성립한다.md'
  code,out=self.run_gate({other:'x',CARD:GOOD_CARD.replace('[[공통-01-원소화-기준]]','[[위임은 아는 일에만 성립한다]]')});self.assertEqual(code,0,out)
 def test_explicit_shared_narrows_library(self):
  other='Assets/Lecture Cards/2025-12-01 이전 행사/위임은 아는 일에만 성립한다.md'
  code,out=self.run_gate({other:'x',CARD:GOOD_CARD.replace('[[공통-01-원소화-기준]]','[[위임은 아는 일에만 성립한다]]')},['--shared','Assets/Lecture Cards/_Shared']);self.assertEqual(code,1)
 def test_missing_links_section_fails(self):
  code,out=self.run_gate({CARD:GOOD_CARD.replace('## 연결','## 메모')});self.assertIn('links) section',out)
 def test_english_links_heading_passes(self):self.assertEqual(self.run_gate({CARD:GOOD_CARD.replace('## 연결','## Links')})[0],0)
 def test_wiki_uri_wrong_path_fails(self):
  code,out=self.run_gate({CARD:GOOD_CARD+'[w](obsidian://open?vault=Wiki&file=Concept)\n'});self.assertIn('URI target missing',out)
 def test_wiki_uri_right_path_passes(self):
  code,out=self.run_gate({CARD:GOOD_CARD+'[w](obsidian://open?vault=Wiki&file=Concepts%2FConcept)\n'});self.assertEqual(code,0,out)
 def test_ambiguous_basename_fails(self):
  code,out=self.run_gate({'Outputs/Lectures/other/09-회고.md':'y'});self.assertIn('path-qualified',out)
 def test_hub_without_retro_fails(self):
  code,out=self.run_gate({HUB:'---\ntranscript: "[[t]]"\n---\n본문\n'});self.assertIn('retrospective',out)
 def test_stale_corrections_header_fails(self):
  code,out=self.run_gate({CORR:'# Last updated: 2026-01-01\n# 2026-01-02 추가 — x\n'},['--corrections',CORR]);self.assertIn('bump',out)
 def test_corrections_not_checked_unless_given(self):self.assertEqual(self.run_gate({CORR:'# Last updated: 2026-01-01\n# 2026-01-02 추가 — x\n'})[0],0)
 def test_skill_changed_mid_run_fails(self):
  code,out=self.run_gate({},['--started-at','2000-01-01T00:00']);self.assertIn('changed during the run',out)
 def test_skill_unchanged_passes(self):
  self.assertEqual(self.run_gate({},['--started-at','2099-01-01T00:00'],skill_age=60)[0],0)
 def test_raw_not_preserved_fails(self):
  with tempfile.NamedTemporaryFile('w',suffix='.txt',delete=False) as f:f.write('[00:01] 원문 그대로')
  try:
   code,out=self.run_gate({'Outputs/Lectures/2026-01-01-sample/t.md':'[00:01] 다듬은 원문'},['--preserve',f.name+'::Outputs/Lectures/2026-01-01-sample/t.md'])
   self.assertIn('NOT preserved',out)
  finally:os.unlink(f.name)
if __name__=='__main__':unittest.main()
