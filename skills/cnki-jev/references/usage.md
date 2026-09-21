# Configuration and usage

## Install separately

From the repository:

```sh
python3 scripts/install.py --target codex
python3 scripts/install.py --target codex --only-jev
# New install of both packages:
python3 scripts/install.py --target codex --with-jev
# Update only an existing extension, backing it up:
python3 scripts/install.py --target codex --only-jev --upgrade
```

Use `claude` or `workbuddy` for the other environments. All commands accept
`--project /path/to/project` and `--dry-run`. A base-only upgrade leaves a previously
installed extension untouched; use `--with-jev --upgrade` to update both.
Neither installer sets credentials nor enables a paid service.

## Configuration

Copy [config.example.json](config.example.json) to a **local research directory**
as `jev-config.local.json`. The example is disabled and contains no credentials.
Set these only within the user's authorization:

| Field | Meaning |
|---|---|
| enabled | Explicit boolean opt-in; false makes no network request |
| mode | off / shadow (paid independent comparison) / assist (paid proposals) |
| allow_abstract_upload | Explicit permission for titles and abstracts to TypeSafe |
| criteria | Exact frozen criteria string from the research task |
| questions | 1–20 named necessary inclusion conditions; all must be covered |
| model | Official Jev model ID; pin a version for reproducible evaluation |
| min_probability | Minimum probability of the selected option; 0.95 is an unvalidated example |
| max_calls | Maximum attempted paid requests in this task, including failures |
| budget_usd | Local estimated budget; zero blocks all uncached calls |
| input_usd_per_million | Current verified TypeSafe input price; zero blocks activation |
| on_failure | baseline (return to ordinary agent review) or pause |

Keep TYPESAFE_API_KEY in the process environment through your usual secret manager.
No credentials are read from JSON. This release supports only the official
`https://api.typesafe.ai/v1/systemone` endpoint; gateway pricing/contracts are not
interchangeable. It follows no HTTP redirects and makes no automatic retries.
Prices are deliberately not embedded: verify the current provider rate before use.

For each paper all conditions are evaluated in one request. Each has explicit
`meets`, `violates`, and `insufficient` options. The endpoint receives only title,
abstract, model and question definitions. No article URL, account metadata, PDF,
full text, screening history or complete database is transmitted. Review material
before enabling upload if its contents are sensitive.

## Run against an existing research task

Use absolute installed paths outside the repository. This repository example reads
the frozen task without changing it:

```sh
python3 skills/cnki-jev/scripts/decide.py \
  --task /local/research/task.sqlite \
  --id cnki:SYNTHETIC:demo-1 \
  --config /local/research/jev-config.local.json \
  --output /local/research/proposal-001.json
```

The paper ID above is synthetic; use the ID from your actual task's import/queue.
Outputs must be new paths. Exit code 0 means a proposal, disabled mode, or an
explicit baseline handoff; check `status` and `route`. Exit code 2 means configured
pause. Exit code 1 means invalid local input/state; no successful result is claimed.
A failure after output creation can leave an empty output file; inspect it and use
a new output path. Completed responses remain recoverable from the sidecar cache.

Proposal outputs deliberately omit the base ledger's required `decision`,
`reason`, and `evidence`. `candidate` is not a final judgment. They include atomic
answers, routing, requested mode, resolved model, material hash, request key and
accounting. Confidence is recorded separately from selected-option probability.
All exclusions require review; low-probability answers become insufficient.

## Preserve the evidence chain

After verifying evidence, construct the ordinary screening JSON and use
`cnki-resume/scripts/workflow.py ... screen --id ... --input reviewed.json`.
For example (synthetic evidence):

```json
{
  "decision": "include",
  "reason": "原文摘要明确符合三个纳入条件；已核对 Jev 建议",
  "basis": "abstract",
  "access_level": "abstract_only",
  "evidence": "本合成示例使用中国企业样本实证检验创新产出。",
  "decision_provenance": {
    "engine": "cnki-jev",
    "mode": "assist",
    "request_key": "copy from proposal",
    "resolved_model": "copy from proposal",
    "material_hash": "copy from proposal",
    "reviewer": "llm",
    "reviewed": true
  }
}
```

Replace every example with the observed source and actual reviewer (`llm` or
`human`). Before applying, confirm paper identity, unchanged source material and
criteria, and that the reviewer actually checked the quote. Metadata records the
review; it is not proof that review happened. Existing `screen` stores this extra
provenance in the research ledger and audit snapshot while preserving the standard
Excel evidence columns and decision-change invalidation. No base schema migration
is needed. Jev's sidecar is not itself an editable base ledger or import file.

## Budget, cache and recovery

The sidecar is always `<task.sqlite>.jev.sqlite`; keep it with the base task.
Task identity, full policy, rate, limits, criteria and question set are bound on
first use. `enabled`, `mode`, upload consent and fallback route may change without
resetting accounting. Other policy changes are rejected: plan a separately
budgeted evaluation explicitly instead of silently reusing old judgments.

Before each attempt the helper atomically reserves `(UTF-8 request bytes + 4096)`
tokens at the configured input rate. This is conservative **local estimation**,
not a proven tokenizer bound or a guarantee about a provider invoice. Once usage
arrives, accounting keeps the larger of that reservation and reported input usage
at the configured rate. No refund is assumed for errors/timeouts/crashes. The
provider's invoice and provider-side spending limit remain authoritative. This
helper assumes the official input-only rate contract; recheck it before enabling.

The call limit is a strict local attempted-request cap with transactional
reservations. Independent processes using the same task cannot spend the same
remaining slot. Creating another task/sidecar creates another budget; do not do
that to bypass a user's total spending authorization.

Identical requests use cached validated answers without another charge. The key
includes the actual title/abstract, atomic questions, requested model and adapter
version. `jev-latest` entries expire across UTC dates; resolved model is retained.
For consistent evaluation use a pinned model. Modes share cached answers but
compute their routes independently. A cache hit reports `status: cached`.

Failed calls stay charged to the local reservation. An explicit `--retry-failed`
allows another attempt and consumes another slot/reservation. A `pending` call
may have reached the provider before interruption: it is never automatically
reissued, even with that flag. Use baseline review for that item and reconcile
usage with the provider. Other papers can continue within the remaining budget.
The helper does not claim provider idempotency or cancellation support.

## Validation and limits

Automated tests use injected synthetic API responses, never credentials, paid calls
or real CNKI papers. They verify routing, isolation, opt-in, limits, caching,
concurrency, response rejection and evidence-chain integration. They cannot prove
Chinese literature screening accuracy or that your account can reach the live API.

Before production, compare a human-labeled set covering relevant, irrelevant and
borderline cases. Separate threshold tuning from held-out evaluation. Measure
recall, inclusion precision, false exclusions, review rate, end-to-end time and
cost. Shadow mode must keep baseline judgments independent. Do not claim accuracy
improvements from structured-output guarantees or vendor performance benchmarks.

Official contract checked 2026-09-21:
- [HTTP API](https://docs.typesafe.ai/api)
- [Atomic questions](https://docs.typesafe.ai/primitives)
- [Confidence versus probability](https://docs.typesafe.ai/confidence)
