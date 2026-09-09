#!/usr/bin/env python3
"""Offline journal-citation conversion. No network or credential access."""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit


def clean(value):
    if not isinstance(value, str):
        raise ValueError("metadata values must be strings")
    return unicodedata.normalize("NFC", " ".join(value.split()))


def escape(value):
    mapping = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
               "&": r"\&", "%": r"\%", "_": r"\_", "#": r"\#",
               "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(mapping.get(c, c) for c in value)


def parse_tagged(text, kind):
    records, tags, last = [], {}, None
    def finish():
        nonlocal tags, last
        if not tags:
            return
        def first(*keys):
            return next((tags[k][0] for k in keys if tags.get(k)), "")
        if kind == "ris":
            if first("TY").upper() != "JOUR":
                raise ValueError("RIS supports TY JOUR only")
            rec = dict(title=first("TI", "T1"), authors=tags.get("AU", tags.get("A1", [])),
                       journal=first("JO", "JF", "T2"), year=first("PY", "Y1"),
                       volume=first("VL"), issue=first("IS"), pages=first("SP"),
                       doi=first("DO"), url=first("UR"))
            if first("EP"):
                if not rec["pages"]:
                    raise ValueError("EP without SP")
                rec["pages"] += "--" + first("EP")
        else:
            if first("0").lower() not in ("journal article", "journal", "期刊文章"):
                raise ValueError("EndNote supports journal articles only")
            rec = dict(title=first("T"), authors=tags.get("A", []), journal=first("J"),
                       year=first("D"), volume=first("V"), issue=first("N"),
                       pages=first("P"), doi=first("R"), url=first("U"))
        if rec["year"]:
            match = re.match(r"^(\d{4})(?:$|[/.-])", rec["year"])
            if not match:
                raise ValueError("invalid publication year/date")
            rec["year"] = match[1]
        rec.update(type="article", authors_complete=True)
        records.append(rec)
        tags, last = {}, None
    pattern = r"^([A-Z][A-Z0-9])  -\s?(.*)$" if kind == "ris" else r"^%([A-Z0-9])\s?(.*)$"
    for line in text.splitlines():
        match = re.match(pattern, line)
        if match:
            tag, value = match.groups()
            if (kind == "ris" and tag == "TY") or (kind == "endnote" and tag == "0"):
                if tags:
                    if kind == "ris":
                        raise ValueError("RIS record missing ER")
                    finish()
            if kind == "ris" and tag == "ER":
                finish()
                continue
            tags.setdefault(tag, []).append(value)
            last = tag
        elif line.strip():
            if last is None or not line[0].isspace():
                raise ValueError("unrecognized tagged input line")
            tags[last][-1] += " " + line.strip()
    if tags:
        if kind == "ris":
            raise ValueError("RIS record missing ER")
        finish()
    return records


def normalize(rec):
    if not isinstance(rec, dict):
        raise ValueError("each record must be an object")
    if rec.get("type", "article") != "article":
        raise ValueError("only journal article records supported")
    if rec.get("authors_complete") is not True:
        raise ValueError("verify full author list and set authors_complete=true")
    authors = rec.get("authors")
    if not isinstance(authors, list) or not authors:
        raise ValueError("authors must be a non-empty array")
    authors = [clean(a) for a in authors]
    if any(not a or re.search(r"等$|…|\.\.\.|\bet\s+al\b|^others$", a, re.I) for a in authors):
        raise ValueError("incomplete author list")
    out = {"authors": authors}
    for key in ("title", "journal", "year", "volume", "issue", "pages", "doi", "url", "cnki_id"):
        value = clean(rec.get(key, ""))
        if value:
            out[key] = value
    if not out.get("title") or not out.get("journal"):
        raise ValueError("title and journal are required")
    if "year" in out and not re.fullmatch(r"\d{4}", out["year"]):
        raise ValueError("year must be a four-digit string")
    if "doi" in out:
        out["doi"] = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", out["doi"], flags=re.I).lower()
        if not re.fullmatch(r"10\.\d{4,9}/\S+", out["doi"]):
            raise ValueError("invalid DOI")
    if "url" in out:
        parsed = urlsplit(out["url"])
        if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username:
            raise ValueError("URL must be an ordinary http(s) source URL")
        if re.search(r"(?:token|ticket|session|password|cookie|authorization)=", parsed.query, re.I):
            raise ValueError("remove credential/session parameters from source URL")
    return out


def render(records):
    unique, seen, warnings = [], {}, []
    for rec in records:
        rec = normalize(rec)
        identity = ("doi", rec["doi"]) if rec.get("doi") else (
            ("cnki", rec["cnki_id"]) if rec.get("cnki_id") else
            ("fallback", rec["title"], rec.get("year", ""), rec["journal"], tuple(rec["authors"])))
        if identity in seen:
            prior = seen[identity]
            if any(prior[k] != v for k, v in rec.items() if k in prior and k != "url"):
                raise ValueError("conflicting duplicate metadata; verify source")
            for k, v in rec.items():
                prior.setdefault(k, v)
            warnings.append("duplicate record merged")
            continue
        seen[identity] = rec
        unique.append((identity, rec))
    if not unique:
        raise ValueError("no citation records")
    entries = []
    for identity, rec in unique:
        key = "cnki" + rec.get("year", "nd") + "_" + hashlib.sha256(
            json.dumps(identity, ensure_ascii=False).encode()).hexdigest()[:16]
        fields = {"title": "{" + escape(rec["title"]) + "}",
                  "author": " and ".join("{" + escape(a) + "}" for a in rec["authors"]),
                  "journal": escape(rec["journal"])}
        for src, dst in (("year", "year"), ("volume", "volume"), ("issue", "number"),
                         ("pages", "pages"), ("doi", "doi"), ("url", "url")):
            if src in rec:
                value = rec[src]
                if src == "pages":
                    value = re.sub(r"(?<=\d)\s*[-–—]+\s*(?=\d)", "--", value)
                fields[dst] = escape(value)
        entries.append("@article{" + key + ",\n" + ",\n".join(
            "  " + k + " = {" + v + "}" for k, v in fields.items()) + "\n}")
        if not rec.get("year"):
            warnings.append(key + ": year missing; omitted")
    return "% Converted offline from verified metadata; not a native CNKI export.\n\n" + "\n\n".join(entries) + "\n", len(unique), warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=("json", "ris", "endnote"), required=True)
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw = args.input.read_text(encoding=args.encoding)
        records = json.loads(raw) if args.format == "json" else parse_tagged(raw, args.format)
        if isinstance(records, dict):
            records = [records]
        if not isinstance(records, list):
            raise ValueError("JSON input must be a record or array of records")
        result, count, warnings = render(records)
        with args.output.open("x", encoding="utf-8") as dest:
            dest.write(result)
        print(json.dumps({"entries": count, "warnings": warnings}, ensure_ascii=False))
    except (ValueError, OSError, UnicodeError, LookupError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
