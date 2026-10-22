#!/usr/bin/env python3
import unittest
from pathlib import Path
from check_table_wikilinks import inspect_text,skip_file,protected_lines,format_wikilink

class TableLinks(unittest.TestCase):
 def kinds(self,s):return {x['kind'] for x in inspect_text(s)['issues']}
 def table(self,link):return '| 카드 | 처리 |\n|---|---|\n| '+link+' | 누적 |\n'
 def test_plain_alias_fails(self):self.assertIn('unescaped_alias_pipe',self.kinds(self.table('[[A|제목]]')))
 def test_escaped_alias_passes(self):self.assertFalse(self.kinds(self.table(r'[[A\|제목]]')))
 def test_header_phantom_detected(self):self.assertIn('table_cell_count',self.kinds('| 카드 | 처리 | |\n|---|---|---|\n| [[A\\|제목]] | 누적 |\n'))
 def test_non_table_unchanged(self):self.assertFalse(self.kinds('문장 [[A|제목]]\n\n## [[B|제목]]\n'))
 def test_frontmatter_protected(self):self.assertFalse(self.kinds('---\nlinks: "[[A|B]]"\n---\n'))
 def test_fence_protected(self):self.assertFalse(self.kinds('```markdown\n'+self.table('[[A|B]]')+'```\n'))
 def test_tilde_fence_protected(self):self.assertFalse(self.kinds('~~~\n'+self.table('[[A|B]]')+'~~~\n'))
 def test_long_fence_with_short_run(self):self.assertFalse(self.kinds('````markdown\n```\n'+self.table('[[A|B]]')+'```\n````\n'))
 def test_raw_marker(self):self.assertFalse(self.kinds('<!-- RAW ORIGINAL BEGIN -->\n'+self.table('[[A|B]]')+'<!-- RAW ORIGINAL END -->\n'))
 def test_after_raw_is_checked(self):self.assertIn('unescaped_alias_pipe',self.kinds('<!-- RAW ORIGINAL BEGIN -->\nraw\n<!-- RAW ORIGINAL END -->\n'+self.table('[[A|B]]')))
 def test_raw_heading(self):self.assertFalse(self.kinds('## Raw Original Content\n'+self.table('[[A|B]]')))
 def test_fake_raw_heading_inside_fence(self):self.assertIn('unescaped_alias_pipe',self.kinds('```\n## Raw Original Content\n```\n\n'+self.table('[[A|B]]')))
 def test_blockquote_table(self):self.assertIn('unescaped_alias_pipe',self.kinds(''.join('> '+x for x in self.table('[[A|B]]').splitlines(keepends=True))))
 def test_blockquote_escaped(self):self.assertFalse(self.kinds(''.join('> '+x for x in self.table(r'[[A\|B]]').splitlines(keepends=True))))
 def test_one_column(self):self.assertIn('unescaped_alias_pipe',self.kinds('| 카드 |\n|---|\n| [[A|B]] |\n'))
 def test_single_brackets_filename(self):self.assertFalse(self.kinds(self.table('[[notes-28-[draft] sample items]]')))
 def test_nested_markdown_link_label(self):self.assertFalse(self.kinds(self.table('[[Camp] 설명](https://example.org)')))
 def test_heading_and_block(self):self.assertFalse(self.kinds(self.table(r'[[A#^block\|제목]]')))
 def test_embed_width(self):self.assertIn('unescaped_alias_pipe',self.kinds(self.table('![[figure.png|300]]')))
 def test_escape_parity(self):self.assertIn('unescaped_alias_pipe',self.kinds(self.table(r'[[A\\|B]]')))
 def test_multiple_links(self):self.assertEqual(sum(x['kind']=='unescaped_alias_pipe' for x in inspect_text(self.table('[[A|B]] / [[C|D]]'))['issues']),2)
 def test_inline_literal_not_active(self):self.assertNotIn('unescaped_alias_pipe',self.kinds(self.table('`[[A|B]]`')))
 def test_unbalanced_link(self):self.assertIn('unbalanced_or_nested_wikilink',self.kinds(self.table('[[A')))
 def test_missing_close(self):self.assertIn('unbalanced_or_nested_wikilink',self.kinds(self.table('B]]')))
 def test_fm_raw_type(self):self.assertTrue(skip_file(Path('/v/x.md'),Path('/v'),'---\ntype: transcript\n---\n'))
 def test_raw_note_name(self):self.assertTrue(skip_file(Path('/v/2026 X - AI 요약.md'),Path('/v'),'text'))
 def test_exclude_prefix(self):self.assertTrue(skip_file(Path('/v/Refs/a.md'),Path('/v'),'text',('Refs/',)))
 def test_no_default_exclude(self):self.assertIsNone(skip_file(Path('/v/Refs/a.md'),Path('/v'),'text'))
 def test_crlf(self):self.assertFalse(self.kinds(self.table(r'[[A\|B]]').replace('\n','\r\n')))
 def test_source_is_not_mutated(self):
  s=self.table('[[A|B]]');before=s;inspect_text(s);self.assertEqual(s,before)
 def test_format_table(self):self.assertEqual(format_wikilink('A#Heading','Title',in_table=True),r'[[A#Heading\|Title]]')
 def test_format_prose(self):self.assertEqual(format_wikilink('A','Title'),'[[A|Title]]')
 def test_format_embed(self):self.assertEqual(format_wikilink('figure.png','300',in_table=True,embed=True),r'![[figure.png\|300]]')
 def test_format_rejects_padding(self):
  with self.assertRaises(ValueError):format_wikilink('A   ','Title',in_table=True)

 def test_triple_escape_is_not_clean(self):self.assertIn('overescaped_alias_separator',self.kinds(self.table(r'[[A\\\|B]]')))
 def test_double_escape_is_not_clean(self):self.assertIn('overescaped_alias_separator',self.kinds(self.table(r'[[A\\|B]]')))
 def test_format_rejects_escaped_target(self):
  with self.assertRaises(ValueError):format_wikilink('A\\','B',in_table=True)
 def test_single_escape_not_overescaped(self):self.assertNotIn('overescaped_alias_separator',self.kinds(self.table(r'[[A\|B]]')))
if __name__=='__main__':unittest.main()
