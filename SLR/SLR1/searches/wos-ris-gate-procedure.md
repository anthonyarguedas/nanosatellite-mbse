# WoS one-record RIS gate: private operator procedure

This is the versioned, manual normal-interface procedure for the bounded Web of
Science Core Collection export preflight. It is **not** a browser adapter,
record enumerator, or discovery runner. The current query plan remains the
normative source for the frozen expressions and all live controls.

The tracked material is deliberately limited to this procedure, an offline
parser/validator, and synthetic tests. It contains no frozen expression text,
source result route, session value, source record, or native export.

## Boundaries

- Use a clean operator-owned browser profile and the normal interface. Do not
  automate sign-in, access challenges, or the high-volume export route.
- Do not inspect result cards or perform screening. The aggregate-control work
  retains only a query digest, source total, control booleans, and timestamps
  in private evidence.
- Use a private, ignored directory for every runtime artifact. Create it with
  owner-only permissions, for example `mkdir -m 700 "$PRIVATE"`. Never commit
  native RIS, normalized output, merged output, cited-reference sidecars,
  query text, source identifiers, titles, abstracts, session routes, cookies,
  credentials, or browser-profile material.
- A challenge, authentication redirect, control ambiguity, export failure,
  changed total, or identity mismatch is `source_total: null`; do not import a
  partial result.

## Live operator checklist

1. Obtain the exact frozen expression from the current query plan without
   retyping or changing it. Record its SHA-256 only in the safe attestation.
2. For `WS-BG1`, `WS-BG2`, `WS-BC1`, and `WS-BT2`, confirm Core Collection
   only; Editions All with every currently available Core Collection edition
   checked; Topic; publication dates 2011-01-01 through 2026-08-10; English
   as a submitted Language row rather than a UI locale; no Document Type;
   recorded Exact Search state; Relevance; and 50 per page.
   Retain only aggregate observations; do not read cards.
3. For the `WS-A1` bounded sentinel, make two fresh passes under the same
   controls. Each pass must have source total one and rank one.
4. In each pass use ordinary Export and RIS for other reference software. Use
   range 1--1 and the displayed Custom selection (30); do not select the
   high-volume export route. Preserve the untouched native RIS in `$PRIVATE`.
5. Confirm the native RIS has one complete record and the required accession,
   DOI, title, author, year, abstract, edition, and cited-reference tags.
   Normalize a private copy with the approved normalizer and run the approved
   merger smoke test before calling the offline verifier.

The absence of a stable browser-card identity is not repaired by this
procedure. For this one-record preflight, the source-native RIS accession order
is the identity basis. Bulk enumeration remains a separate final-run gate.

## Safe attestation

Create one private JSON file for each export pass. It must contain exactly this
shape; the digest is of the exact frozen expression, not the expression itself.

```json
{
  "schema": "wos-ris-gate-attestation/v1",
  "query_sha256": "<64-lowercase-hex-digest>",
  "source_total": 1,
  "controls": {
    "core_collection_only": true,
    "editions_all": true,
    "topic_field": true,
    "english": true,
    "date_window": true,
    "no_document_type": true,
    "exact_search_state_recorded": true,
    "relevance_sort": true,
    "page_size_50": true,
    "query_exact": true
  },
  "ordinary_export": {
    "ris_other_reference_software": true,
    "fast_5000_not_selected": true,
    "range_one_to_one": true,
    "custom_selection_30": true,
    "download_completed": true,
    "authentication_or_login_redirect": false
  }
}
```

The verifier rejects additional fields so an attestation cannot accidentally
carry a route, source output, or browser context.

## Offline verification

`searches/tools/wos_ris_gate.py` uses only the Python standard library. It
performs no browser or network work, takes no query option, prints only a
control-artifact digest and pass state, refuses to overwrite artifacts, and
requires an owner-only output directory. The cited-reference sidecar is private
source output: it retains cited-reference values but replaces the source
identifier with an opaque digest.

Run the following only after the private native, normalized, merged, and
attestation artifacts exist:

```sh
python3 searches/tools/wos_ris_gate.py integrity \
  --input "$PRIVATE/pass-1.ris" \
  --output-path "$PRIVATE/pass-1-integrity.json"
python3 searches/tools/wos_ris_gate.py integrity \
  --input "$PRIVATE/pass-2.ris" \
  --output-path "$PRIVATE/pass-2-integrity.json"

python3 searches/tools/wos_ris_gate.py sidecar \
  --input "$PRIVATE/pass-1.ris" --rank-start 1 \
  --output-path "$PRIVATE/pass-1-sidecar.json"
python3 searches/tools/wos_ris_gate.py sidecar \
  --input "$PRIVATE/pass-2.ris" --rank-start 1 \
  --output-path "$PRIVATE/pass-2-sidecar.json"

python3 searches/tools/wos_ris_gate.py validate \
  --ris "$PRIVATE/pass-1.ris" \
  --normalized "$PRIVATE/pass-1-normalized.csv" \
  --sidecar "$PRIVATE/pass-1-sidecar.json" \
  --merged "$PRIVATE/pass-1-merged.json" \
  --attestation "$PRIVATE/pass-1-attestation.json" \
  --output-path "$PRIVATE/pass-1-validation.json"

python3 searches/tools/wos_ris_gate.py reconcile \
  --pass-one-ris "$PRIVATE/pass-1.ris" \
  --pass-one-normalized "$PRIVATE/pass-1-normalized.csv" \
  --pass-one-sidecar "$PRIVATE/pass-1-sidecar.json" \
  --pass-one-merged "$PRIVATE/pass-1-merged.json" \
  --pass-one-attestation "$PRIVATE/pass-1-attestation.json" \
  --pass-two-ris "$PRIVATE/pass-2.ris" \
  --pass-two-normalized "$PRIVATE/pass-2-normalized.csv" \
  --pass-two-sidecar "$PRIVATE/pass-2-sidecar.json" \
  --pass-two-merged "$PRIVATE/pass-2-merged.json" \
  --pass-two-attestation "$PRIVATE/pass-2-attestation.json" \
  --output-path "$PRIVATE/two-pass-reconciliation.json"
```

The validation artifact checks strict UTF-8 RIS structure, required native
tags, exact source/rank/total/query-digest provenance in the normalized row,
private sidecar alignment (including an opaque hash of the cited-reference
values), and the one-record canonical merge result. The reconciliation artifact
additionally requires the two native byte hashes and opaque native identifier
orders to agree. Its JSON has hashes, counts, and booleans only.

## Versioned inventory and residual scope

- `searches/tools/wos_ris_gate.py` -- offline private RIS integrity, sidecar,
  validation, and two-pass reconciliation commands.
- `searches/tools/test_wos_ris_gate.py` -- dedicated synthetic privacy,
  no-clobber, malformed-input, and end-to-end regressions.
- `searches/fixtures/wos-ris-gate-synthetic.json` -- structural-only fixture;
  it contains no source output.

Run the regression with:

```sh
python3 searches/tools/test_wos_ris_gate.py
```

Passing this procedure preserves the reproducible one-record export mechanics
only. It does not authorize final discovery, establish a browser-card identity
for bulk work, replace the plan's complete pagination requirements, or close
any other final-adapter gate.
