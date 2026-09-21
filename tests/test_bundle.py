import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import bibtexparser
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/cnki-export/scripts/convert.py"
spec = importlib.util.spec_from_file_location("converter", SCRIPT)
conv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conv)
spec2 = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install.py")
installer = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(installer)


def record(**updates):
    rec = dict(title="生成式 AI 与企业创新（合成）", authors=["张三", "欧阳修"],
               authors_complete=True, journal="测试期刊", year="2026", pages="1–9")
    rec.update(updates)
    return rec


class ConversionTests(unittest.TestCase):
    def test_single_chinese_independent_parser(self):
        text, count, _ = conv.render([record()])
        entries = bibtexparser.loads(text).entries
        self.assertEqual(count, 1)
        self.assertEqual(len(entries), 1)
        self.assertIn("欧阳修", entries[0]["author"])
        self.assertEqual(entries[0]["pages"], "1--9")

    def test_batch_keys_and_special_characters(self):
        special = "AI & 50% {创新}_# $ ~ ^ \\"
        text, count, _ = conv.render([record(title=special), record(title="另一个题名")])
        entries = bibtexparser.loads(text).entries
        self.assertEqual(len(entries), count)
        self.assertEqual(len({e["ID"] for e in entries}), 2)
        self.assertIn(r"\%", entries[0]["title"])
        self.assertIn(r"\textbackslash{}", entries[0]["title"])

    def test_doi_dedup_and_conflict(self):
        a = record(doi="https://doi.org/10.1234/TEST")
        b = record(doi="10.1234/test")
        self.assertEqual(conv.render([a, b])[1], 1)
        with self.assertRaises(ValueError):
            conv.render([a, record(doi="10.1234/test", year="2025")])

    def test_distinct_ids_preserved(self):
        self.assertEqual(conv.render([record(doi="10.1234/a"), record(doi="10.1234/b")])[1], 2)

    def test_missing_year_omitted(self):
        text, _, warnings = conv.render([record(year="")])
        self.assertNotIn("year", bibtexparser.loads(text).entries[0])
        self.assertTrue(warnings)

    def test_incomplete_authors_rejected(self):
        for authors in (["张三等"], ["张三", "…"], ["John et al."], []):
            with self.assertRaises(ValueError):
                conv.render([record(authors=authors)])
        with self.assertRaises(ValueError):
            conv.render([record(authors_complete=False)])

    def test_ris_multirecord_and_continuation(self):
        raw = "TY  - JOUR\nTI  - 合成\n  题名\nAU  - 张三\nJO  - 期刊\nPY  - 2025/01/01\nSP  - 1\nEP  - 9\nER  -\n"
        records = conv.parse_tagged(raw + raw.replace("合成", "另一个"), "ris")
        self.assertEqual(conv.render(records)[1], 2)
        self.assertEqual(records[0]["title"], "合成 题名")
        with self.assertRaises(ValueError):
            conv.parse_tagged(raw.replace("ER  -\n", ""), "ris")

    def test_endnote(self):
        raw = "%0 Journal Article\n%T 合成题名\n%A 张三\n%A 李四\n%J 测试期刊\n%D 2026\n"
        entries = bibtexparser.loads(conv.render(conv.parse_tagged(raw, "endnote"))[0]).entries
        self.assertEqual(len(entries), 1)
        self.assertIn("李四", entries[0]["author"])
        with self.assertRaises(ValueError):
            conv.parse_tagged(raw.replace("Journal Article", "Book"), "endnote")

    def test_invalid_metadata(self):
        for patch in (dict(year="unknown"), dict(doi="not-doi"), dict(url="javascript:foo"),
                      dict(url="https://example.org/?token=secret"), dict(type="book")):
            with self.assertRaises(ValueError):
                conv.render([record(**patch)])

    def test_cli_encoding_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = Path(tmp) / "in.json", Path(tmp) / "out.bib"
            src.write_bytes(json.dumps([record()], ensure_ascii=False).encode("gb18030"))
            command = [sys.executable, str(SCRIPT), str(src), "--format", "json",
                       "--encoding", "gb18030", "--output", str(dest)]
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(bibtexparser.loads(dest.read_text()).entries), 1)
            before = dest.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(dest.read_bytes(), before)


class PackagingTests(unittest.TestCase):
    def test_frontmatter(self):
        skills = list((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 12)
        for skill in skills:
            meta = yaml.safe_load(skill.read_text().split("---", 2)[1])
            self.assertEqual(meta["name"], skill.parent.name)
            self.assertIsInstance(meta["description"], str)
        self.assertTrue((ROOT / "agents/cnki-researcher.md").exists())

    def test_install_targets_and_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(installer.install("codex", tmp, True), 12)
            self.assertFalse((Path(tmp) / ".agents").exists())
            installer.install("codex", tmp)
            self.assertTrue((Path(tmp) / ".agents/skills/cnki-export/scripts/convert.py").exists())
            with self.assertRaises(FileExistsError):
                installer.install("codex", tmp)
            installer.install("claude", tmp)
            self.assertTrue((Path(tmp) / ".claude/agents/cnki-researcher.md").exists())


if __name__ == "__main__":
    unittest.main()
