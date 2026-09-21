#!/usr/bin/env python3
"""Offline CNKI research ledger and evidence workbooks (Python 3.9+, stdlib only)."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from datetime import datetime, timezone
from urllib.parse import urlsplit
from xml.sax.saxutils import escape
import zipfile

STAGES = ('screening', 'download', 'extraction', 'citation')
FIELDS = {
    'question': '研究问题', 'theory': '理论基础', 'data_source': '数据来源',
    'sample': '研究对象与样本量', 'period': '样本时间', 'outcome': '被解释变量与测量',
    'exposure': '解释变量与测量', 'controls': '控制变量', 'method': '模型与识别策略',
    'endogeneity': '内生性处理', 'robustness': '稳健性检验',
    'mechanism': '机制检验', 'heterogeneity': '异质性分析',
    'findings': '主要结论与效应', 'limitations': '作者陈述的局限',
}
DECISIONS = {'include': '纳入', 'exclude': '排除', 'uncertain': '待判断'}
ACCESS = ('metadata_only', 'abstract_only', 'preview', 'full_text')


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def required(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be non-empty text')
    return value.strip()


def source_url(value):
    required(value, 'url')
    p = urlsplit(value)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Use a public source URL without credentials')
    if re.search(r'(token|cookie|session|ticket|signature|password|auth)=', p.query, re.I):
        raise ValueError('Do not persist session-bearing URLs')
    return value


def identity(rec):
    raw_doi = rec.get('doi') or ''
    if not isinstance(raw_doi, str):
        raise ValueError('DOI must be text')
    doi = raw_doi.strip().lower()
    doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:\s*)', '', doi)
    if doi:
        if not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
            raise ValueError('Invalid DOI')
        return 'doi:' + doi
    if rec.get('database') and rec.get('record_id'):
        return 'cnki:' + required(rec['database'], 'database') + ':' + required(rec['record_id'], 'record_id')
    # A source URL is a locator, not proof that matching titles are the same paper.
    return 'url:' + hashlib.sha256(source_url(rec['url']).encode()).hexdigest()[:24]


def connect(path):
    if not Path(path).is_file():
        raise ValueError('Task does not exist; run init first')
    db = sqlite3.connect(str(path), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    version = db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    if not version or json.loads(version[0]) != 1:
        db.close()
        raise ValueError('Unsupported ledger version')
    return db


def init(path, config):
    if not isinstance(config, dict):
        raise ValueError('Config must be an object')
    for key in ('topic', 'query', 'criteria'):
        required(config.get(key), key)
    if config.get('required_access', 'available') not in ('available', 'full_text'):
        raise ValueError('required_access must be available or full_text')
    stages = config.get('stages', ['screening', 'extraction'])
    if not isinstance(stages, list) or not stages or len(set(stages)) != len(stages) or any(s not in STAGES for s in stages):
        raise ValueError('stages must be a non-empty unique list of supported stages')
    if 'extraction' in stages and 'screening' not in stages:
        raise ValueError('extraction requires screening')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb'):
        pass
    db = sqlite3.connect(str(path))
    try:
        with db:
            db.executescript('''
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE papers (id TEXT PRIMARY KEY, metadata TEXT NOT NULL, screening TEXT, extraction TEXT);
CREATE TABLE stages (paper_id TEXT REFERENCES papers(id), stage TEXT, status TEXT NOT NULL,
 reason TEXT NOT NULL DEFAULT '', artifact TEXT, updated_at TEXT NOT NULL, PRIMARY KEY(paper_id,stage));
CREATE TABLE events (id INTEGER PRIMARY KEY, at TEXT, paper_id TEXT, action TEXT, detail TEXT);
''')
            config = dict(config, stages=stages, created_at=now())
            db.executemany('INSERT INTO meta VALUES (?,?)', [('schema_version', '1'), ('config', dump(config))])
    finally:
        db.close()
    return {'task': str(path.resolve()), 'stages': stages}


def config(db):
    return json.loads(db.execute("SELECT value FROM meta WHERE key='config'").fetchone()[0])


def event(db, pid, action, detail):
    db.execute('INSERT INTO events(at,paper_id,action,detail) VALUES (?,?,?,?)', (now(), pid, action, dump(detail)))


def paper(db, pid):
    row = db.execute('SELECT * FROM papers WHERE id=?', (pid,)).fetchone()
    if row is None:
        raise ValueError('Unknown paper: ' + pid)
    return row


def stage(db, pid, name):
    row = db.execute('SELECT * FROM stages WHERE paper_id=? AND stage=?', (pid, name)).fetchone()
    if row is None:
        raise ValueError('Stage not requested for this task: ' + name)
    return row


def set_stage(db, pid, name, status, reason='', artifact=None):
    stage(db, pid, name)
    db.execute('UPDATE stages SET status=?,reason=?,artifact=?,updated_at=? WHERE paper_id=? AND stage=?',
               (status, reason, dump(artifact) if artifact else None, now(), pid, name))
    event(db, pid, name + ':' + status, {'reason': reason, 'artifact': artifact})


def import_records(db, records):
    if not isinstance(records, list):
        raise ValueError('Input must be an array of records')
    result = []
    for rec in records:
        if not isinstance(rec, dict):
            raise ValueError('Each record must be an object')
        for key in ('title', 'url', 'retrieved_at'):
            required(rec.get(key), key)
        source_url(rec['url'])
        pid = identity(rec)
        existing = db.execute('SELECT id,metadata FROM papers WHERE id=?', (pid,)).fetchone()
        candidates = []
        for row in db.execute('SELECT id,metadata FROM papers'):
            other = json.loads(row['metadata'])
            same_record = (rec.get('database') and rec.get('record_id') and
                           rec.get('database') == other.get('database') and rec.get('record_id') == other.get('record_id'))
            same_doi = rec.get('doi') and other.get('doi') and identity(rec) == identity(other)
            same_locator = (rec['url'] == other['url'] and
                            (identity(rec).startswith('url:') or identity(other).startswith('url:')))
            if same_record or same_doi or same_locator or row['id'] == pid:
                if same_record and rec.get('doi') and other.get('doi') and identity(rec) != identity(other):
                    raise ValueError('Conflicting DOI for the same CNKI record')
                candidates.append(row)
        if len(candidates) > 1:
            raise ValueError('Multiple existing identities match; resolve duplicates before import')
        if candidates:
            existing = candidates[0]
            pid = existing['id']  # Keep the original stable key when new metadata adds a DOI.
        if existing:
            old = json.loads(existing['metadata'])
            if any(old.get(k) and rec.get(k) and old[k] != rec[k] for k in ('title', 'year', 'authors', 'record_id', 'database')):
                raise ValueError('Conflicting duplicate metadata for ' + pid)
            # Enrich missing metadata without overwriting earlier evidence/results.
            enriched = dict(old)
            for key, val in rec.items():
                if not enriched.get(key) and val:
                    enriched[key] = val
            db.execute('UPDATE papers SET metadata=? WHERE id=?', (dump(enriched), pid))
            result.append({'id': pid, 'status': 'existing'})
            continue
        warnings = []
        for row in db.execute('SELECT id,metadata FROM papers'):
            other = json.loads(row['metadata'])
            if re.sub(r'\s+', '', other['title']).casefold() == re.sub(r'\s+', '', rec['title']).casefold() and other.get('year') == rec.get('year'):
                warnings.append(row['id'])
        db.execute('INSERT INTO papers(id,metadata) VALUES (?,?)', (pid, dump(rec)))
        for s in config(db)['stages']:
            db.execute('INSERT INTO stages(paper_id,stage,status,updated_at) VALUES (?,?,?,?)', (pid, s, 'pending', now()))
        event(db, pid, 'import', {'possible_duplicates': warnings})
        result.append({'id': pid, 'status': 'added', 'possible_duplicates': warnings})
    return result


def screen(db, pid, value):
    if not isinstance(value, dict):
        raise ValueError('Screening input must be an object')
    paper(db, pid)
    stage(db, pid, 'screening')
    if value.get('decision') not in DECISIONS:
        raise ValueError('decision must be include, exclude or uncertain')
    for key in ('reason', 'evidence'):
        required(value.get(key), key)
    if value.get('basis') not in ('title', 'abstract', 'full_text'):
        raise ValueError('basis must be title, abstract or full_text')
    if value.get('access_level') not in ACCESS:
        raise ValueError('Invalid access_level')
    if value['basis'] == 'full_text' and value['access_level'] != 'full_text':
        raise ValueError('Full-text screening requires full-text access')
    if value['basis'] == 'abstract' and value['access_level'] == 'metadata_only':
        raise ValueError('Abstract screening requires an available abstract')
    previous = paper(db, pid)['screening']
    stored = dict(value, criteria=config(db)['criteria'])
    if previous and json.loads(previous) == stored:
        return {'id': pid, 'status': 'unchanged'}
    db.execute('UPDATE papers SET screening=?,extraction=NULL WHERE id=?', (dump(stored), pid))
    set_stage(db, pid, 'screening', 'done')
    for s in db.execute("SELECT stage FROM stages WHERE paper_id=? AND stage='extraction'", (pid,)).fetchall():
        decision = value['decision']
        status = {'include': 'pending', 'exclude': 'skipped', 'uncertain': 'blocked'}[decision]
        set_stage(db, pid, s[0], status, '' if decision == 'include' else 'Screening: ' + decision)
    event(db, pid, 'screening-evidence', stored)
    return {'id': pid, 'decision': value['decision']}


def extract(db, pid, value):
    if not isinstance(value, dict):
        raise ValueError('Extraction input must be an object')
    p = paper(db, pid)
    stage(db, pid, 'extraction')
    if not p['screening'] or json.loads(p['screening'])['decision'] != 'include':
        raise ValueError('Extraction requires an included screening decision')
    if value.get('access_level') not in ('abstract_only', 'preview', 'full_text'):
        raise ValueError('Extraction needs readable abstract, preview or full text')
    fields = value.get('fields')
    if not isinstance(fields, dict) or not fields or set(fields) - set(FIELDS):
        raise ValueError('fields must contain supported extraction fields')
    for name, cell in fields.items():
        if cell is None:
            continue
        if not isinstance(cell, dict):
            raise ValueError(name + ': use an evidence object or null')
        for key in ('value', 'quote', 'locator', 'source'):
            required(cell.get(key), name + '.' + key)
        if value['access_level'] == 'abstract_only' and cell['locator'] != '摘要':
            raise ValueError('Abstract evidence locator must be 摘要')
    if not any(cell for cell in fields.values()):
        raise ValueError('Provide at least one evidenced field')
    db.execute('UPDATE papers SET extraction=? WHERE id=?', (dump(value), pid))
    needs_full_text = config(db).get('required_access') == 'full_text' and value['access_level'] != 'full_text'
    set_stage(db, pid, 'extraction', 'blocked' if needs_full_text else 'done',
              'Full text required; partial evidence saved' if needs_full_text else '')
    event(db, pid, 'extraction-evidence', value)
    return {'id': pid, 'fields': sum(c is not None for c in fields.values()), 'access_level': value['access_level']}


def fingerprint(path):
    p = Path(path).expanduser().resolve()
    if not p.is_file() or p.stat().st_size == 0:
        raise ValueError('Missing or empty artifact: ' + str(p))
    digest = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return {'path': str(p), 'sha256': digest.hexdigest(), 'bytes': p.stat().st_size}


def eligible(db, pid, name):
    if name == 'extraction':
        p = paper(db, pid)
        return bool(p['screening'] and json.loads(p['screening'])['decision'] == 'include')
    return True


def mark(db, pid, name, status, reason='', path=None, identity_verified=False):
    current = stage(db, pid, name)
    if status == 'done':
        if name in ('screening', 'extraction'):
            raise ValueError('Use screen/extract to validate evidence before completion')
        if not path or not identity_verified:
            raise ValueError('Completion requires --artifact and --identity-verified after reading the file')
        artifact = fingerprint(path)
        if name == 'download':
            with Path(artifact['path']).open('rb') as f:
                if f.read(5) != b'%PDF-':
                    raise ValueError('Artifact is not a PDF; CAJ/HTML must not be marked PDF-complete')
        artifact['identity_verified'] = True
    else:
        artifact = None
        if status not in ('running', 'blocked', 'failed', 'pending'):
            raise ValueError('Invalid status')
        if current['status'] == 'done':
            raise ValueError('Completed stage cannot be reset here; missing files are detected by queue')
        if status == 'running' and (current['status'] != 'pending' or not eligible(db, pid, name)):
            raise ValueError('Only an eligible pending stage can be claimed')
        if status in ('blocked', 'failed', 'pending'):
            required(reason, 'reason')
    set_stage(db, pid, name, status, reason, artifact)
    return {'id': pid, 'stage': name, 'status': status}


def queue(db):
    # Never automatically requeue an in-flight transfer; inspect it first.
    for row in db.execute("SELECT * FROM stages WHERE status='done' AND artifact IS NOT NULL").fetchall():
        artifact = json.loads(row['artifact'])
        try:
            actual = fingerprint(artifact['path'])
            valid = actual['sha256'] == artifact['sha256']
        except (OSError, ValueError):
            valid = False
        if not valid:
            set_stage(db, row['paper_id'], row['stage'], 'pending', 'Saved file missing or changed; verify before retry')
    result = []
    for row in db.execute('SELECT s.*,p.metadata FROM stages s JOIN papers p ON s.paper_id=p.id ORDER BY p.rowid,s.rowid'):
        item = dict(row)
        item['title'] = json.loads(item.pop('metadata'))['title']
        item['eligible'] = eligible(db, item['paper_id'], item['stage'])
        if item['status'] not in ('done', 'skipped'):
            item['next_action'] = ('inspect_active_operation' if item['status'] == 'running' else
                                   'resolve_blocker_then_reset' if item['status'] in ('failed', 'blocked') else
                                   'process' if item['eligible'] else 'wait_for_screening')
            result.append(item)
    return result


def status(db):
    return {'config': config(db), 'papers': db.execute('SELECT count(*) FROM papers').fetchone()[0],
            'stages': [dict(r) for r in db.execute('SELECT stage,status,count(*) AS count FROM stages GROUP BY stage,status')]}


def tables(db):
    screening = [['文献ID', '原始序号', '题名', '作者', '年份', '来源', '链接', '摘要', '筛选结论', '理由', '判断依据', '证据', '可访问层级', '筛选标准']]
    evidence = [['文献ID', '题名', '链接', '可访问层级'] + list(FIELDS.values())]
    sources = [['文献ID', '题名', '字段', '提取内容', '原文证据', '证据位置', '证据来源']]
    for row in db.execute('SELECT * FROM papers ORDER BY rowid'):
        m = json.loads(row['metadata'])
        s = json.loads(row['screening']) if row['screening'] else {}
        authors = m.get('authors', '')
        if isinstance(authors, list):
            authors = '；'.join(authors)
        if m.get('authors_complete') is False:
            authors = str(authors) + '（作者列表不完整）'
        screening.append([row['id'], m.get('site_rank', ''), m['title'], authors, m.get('year', ''), m.get('source', m.get('journal', '')), m['url'], m.get('abstract', ''), DECISIONS.get(s.get('decision'), '未筛选'), s.get('reason', ''), s.get('basis', ''), s.get('evidence', ''), s.get('access_level', m.get('access_level', 'metadata_only')), config(db)['criteria']])
        if s.get('decision') != 'include':
            continue
        e = json.loads(row['extraction']) if row['extraction'] else {}
        cells = []
        for name, label in FIELDS.items():
            cell = e.get('fields', {}).get(name)
            cells.append(cell['value'] if cell else '未提取/证据不足')
            if cell:
                sources.append([row['id'], m['title'], label, cell['value'], cell['quote'], cell['locator'], cell['source']])
        evidence.append([row['id'], m['title'], m['url'], e.get('access_level', '未提取')] + cells)
    progress = [['文献ID', '阶段', '状态', '原因', '文件位置', '更新时间']]
    for r in db.execute('SELECT * FROM stages ORDER BY rowid'):
        a = json.loads(r['artifact']) if r['artifact'] else {}
        progress.append([r['paper_id'], r['stage'], r['status'], r['reason'], a.get('path', ''), r['updated_at']])
    manifest = [['项目', '内容']] + [[k, dump(v) if isinstance(v, (list, dict)) else str(v)] for k, v in config(db).items()]
    return {'文献筛选表': screening, '实证研究对照表': evidence, '原文证据': sources, '任务进度': progress, '检索与筛选规则': manifest}


def xml_text(value):
    text = str(value)
    if len(text) > 32767:
        raise ValueError('Excel cell exceeds 32767 characters; shorten evidence quote before export')
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]', text):
        raise ValueError('Invalid XML character in workbook input')
    return escape(text)


def column(number):
    result = ''
    while number:
        number, r = divmod(number - 1, 26)
        result = chr(65 + r) + result
    return result


def write_xlsx(path, sheets):
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    rel = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        overrides = ''.join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % i for i in range(1, len(sheets) + 1))
        z.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' + overrides + '</Types>')
        z.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="' + rel + '/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', '<workbook xmlns="' + ns + '" xmlns:r="' + rel + '"><sheets>' + ''.join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (name, i, i) for i, name in enumerate(sheets, 1)) + '</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join('<Relationship Id="rId%d" Type="%s/worksheet" Target="worksheets/sheet%d.xml"/>' % (i, rel, i) for i in range(1, len(sheets) + 1)) + '<Relationship Id="styles" Type="' + rel + '/styles" Target="styles.xml"/></Relationships>')
        z.writestr('xl/styles.xml', '<styleSheet xmlns="' + ns + '"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF24476B"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
        for i, rows in enumerate(sheets.values(), 1):
            body = []
            for n, row in enumerate(rows, 1):
                cells = ''.join('<c r="%s%d" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (column(c), n, int(n == 1), xml_text(v)) for c, v in enumerate(row, 1))
                body.append('<row r="%d">%s</row>' % (n, cells))
            z.writestr('xl/worksheets/sheet%d.xml' % i, '<worksheet xmlns="' + ns + '"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols><col min="1" max="%d" width="28" customWidth="1"/></cols><sheetData>' % len(rows[0]) + ''.join(body) + '</sheetData><autoFilter ref="A1:%s%d"/></worksheet>' % (column(len(rows[0])), len(rows)))


def export(db, directory):
    queue(db)  # Revalidate recorded artifacts before reporting completion.
    dest = Path(directory)
    if dest.exists():
        raise FileExistsError('Choose a new output folder; exports never overwrite')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.cnki-export-', dir=str(dest.parent)) as tmp:
        temp = Path(tmp)
        data = tables(db)
        write_xlsx(temp / '研究工作表.xlsx', data)
        for name, rows in data.items():
            with (temp / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as f:
                # Prevent spreadsheet formulas when CSV is opened in Excel.
                csv.writer(f).writerows([["'" + str(v) if str(v).lstrip().startswith(('=', '+', '-', '@')) else v for v in row] for row in rows])
        snapshot = {'config': config(db), 'papers': [dict(r) for r in db.execute('SELECT * FROM papers')], 'stages': [dict(r) for r in db.execute('SELECT * FROM stages')], 'events': [dict(r) for r in db.execute('SELECT * FROM events')]}
        (temp / 'task-snapshot.json').write_text(dump(snapshot), encoding='utf-8')
        # mkdir is exclusive: concurrent exports cannot replace each other.
        dest.mkdir()
        for f in temp.iterdir():
            os.replace(str(f), str(dest / f.name))
    return {'directory': str(dest.resolve()), 'workbook': str((dest / '研究工作表.xlsx').resolve()), 'papers': len(data['文献筛选表']) - 1}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', required=True, help='Local SQLite task file')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init'); p.add_argument('--config', required=True)
    p = sub.add_parser('import'); p.add_argument('--input', required=True)
    for cmd in ('screen', 'extract'):
        p = sub.add_parser(cmd); p.add_argument('--id', required=True); p.add_argument('--input', required=True)
    p = sub.add_parser('mark')
    p.add_argument('--id', required=True); p.add_argument('--stage', choices=STAGES, required=True)
    p.add_argument('--status', choices=('pending', 'running', 'blocked', 'failed', 'done'), required=True)
    p.add_argument('--reason', default=''); p.add_argument('--artifact'); p.add_argument('--identity-verified', action='store_true')
    sub.add_parser('queue'); sub.add_parser('status')
    p = sub.add_parser('export'); p.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        value = None
        if hasattr(args, 'input') or hasattr(args, 'config'):
            value = json.loads(Path(getattr(args, 'input', None) or args.config).read_text(encoding='utf-8-sig'))
        if args.command == 'init':
            result = init(args.task, value)
        else:
            db = connect(args.task)
            try:
                with db:
                    db.execute('BEGIN IMMEDIATE')
                    if args.command == 'import': result = import_records(db, value)
                    elif args.command == 'screen': result = screen(db, args.id, value)
                    elif args.command == 'extract': result = extract(db, args.id, value)
                    elif args.command == 'mark': result = mark(db, args.id, args.stage, args.status, args.reason, args.artifact, args.identity_verified)
                    elif args.command == 'queue': result = queue(db)
                    elif args.command == 'status': result = status(db)
                    else: result = export(db, args.output)
            finally:
                db.close()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
