#!/usr/bin/env python3
"""Produce synthetic screening/evidence examples without contacting CNKI."""
import argparse
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/cnki-resume/scripts/workflow.py'
spec = importlib.util.spec_from_file_location('workflow', SCRIPT)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


def demo(output):
    root = Path(output).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=False)
    task = root / 'task.sqlite'
    w.init(task, dict(topic='数字化与创新（全部为合成演示）', query='合成数据，无真实检索',
                     criteria='中国企业；实证研究；创新产出', stages=['screening', 'extraction'],
                     platform='合成演示，不是知网结果'))
    db = w.connect(task)
    try:
        with db:
            records = [dict(title=title, url='https://example.org/synthetic-' + str(n),
                            database='SYNTHETIC', record_id=str(n), site_rank=n, year='2025',
                            retrieved_at=w.now(), authors=['合成作者'], source='合成期刊', abstract=abstract)
                       for n, (title, abstract) in enumerate([
                           ('数字化与企业创新（合成）', '合成示例：使用中国企业面板样本研究数字化与专利产出的关系。'),
                           ('数字化教学（合成）', '合成示例：研究中学课堂教学。'),
                           ('数字化与组织变化（合成）', '合成示例：摘要不足以判断研究对象及方法。')], 1)]
            ids = [r['id'] for r in w.import_records(db, records)]
            for pid, rec, decision, reason in zip(ids, records, ['include', 'exclude', 'uncertain'],
                ['样本、方法和创新结果符合标准', '研究对象为中学课堂，不符合企业样本标准', '需全文确认样本和方法']):
                w.screen(db, pid, dict(decision=decision, reason=reason, basis='abstract',
                                      access_level='abstract_only', evidence=rec['abstract']))
            w.extract(db, ids[0], dict(access_level='abstract_only', fields={
                'question': dict(value='数字化与专利产出的关系（合成）', quote=records[0]['abstract'], locator='摘要', source=records[0]['url']),
                'sample': dict(value='中国企业面板样本；数量未知（合成）', quote=records[0]['abstract'], locator='摘要', source=records[0]['url']),
                'method': None, 'mechanism': None}))
            result = w.export(db, root / 'report')
        print('SYNTHETIC ONLY — not actual CNKI results')
        print('Resume ledger: ' + str(task))
        print('Workbook: ' + result['workbook'])
    finally:
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New local demo folder')
    args = parser.parse_args()
    try:
        demo(args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')
