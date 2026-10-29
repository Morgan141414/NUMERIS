#!/usr/bin/env bash
set -u

# Local Phase-I gate for the closest-baseline reproduction manifest.
# This checker is intentionally conservative: it reports an incomplete gate
# rather than inferring reproduction from citations or ordinary SciPy runs.

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="$ROOT/research/literature_review/BASELINE_REPRODUCTION_MANIFEST_v0.1.md"
LEDGER="$ROOT/research/literature_review/BIBLIOGRAPHY_LEDGER.md"
PLAN="$ROOT/research/literature_review/CLOSEST_BASELINE_REPRODUCTION_PLAN.md"
EXIT_CODE=0

fail() {
  printf 'FAIL: %s\n' "$1"
  EXIT_CODE=1
}

pass() {
  printf 'PASS: %s\n' "$1"
}

if [[ ! -f "$MANIFEST" ]]; then
  fail "manifest is missing: $MANIFEST"
else
  pass "manifest exists"
fi

if [[ ! -f "$LEDGER" ]]; then
  fail "bibliography ledger is missing: $LEDGER"
else
  pass "bibliography ledger exists"
fi

if [[ ! -f "$PLAN" ]]; then
  fail "closest-baseline plan is missing: $PLAN"
else
  pass "closest-baseline plan exists"
fi

if [[ -f "$MANIFEST" ]]; then
  required_statuses=(R0 R1 R2 R3 NOT-REPRODUCED BLOCKED CONCEPTUAL-BASELINE)
  for status in R0 R1 R2 R3 NOT-REPRODUCED BLOCKED CONCEPTUAL-BASELINE; do
    if rg -q --fixed-strings "$status" "$MANIFEST"; then
      pass "status vocabulary contains $status"
    else
      fail "status vocabulary omits $status"
    fi
  done

  required_cards=(ADJ-GLOBAL GO-FUNCTIONAL LIKELIHOOD-DISTORTION DALTON PROB-ODE)
  for card in ADJ-GLOBAL GO-FUNCTIONAL LIKELIHOOD-DISTORTION DALTON PROB-ODE; do
    if rg -q --fixed-strings "| $card |" "$MANIFEST"; then
      pass "baseline card exists: $card"
    else
      fail "baseline card is missing: $card"
    fi
  done

  if rg -n -i '^\| (ADJ-GLOBAL|GO-FUNCTIONAL|LIKELIHOOD-DISTORTION|DALTON|PROB-ODE) \|.*\| *\|$' "$MANIFEST" >/dev/null; then
    fail "one or more baseline cards have an empty current status"
  else
    pass "all baseline cards have a non-empty current status"
  fi

  if rg -n -i '(^|[^n])\b(beaten|superior|novel|first)\b|claims? (an exact )?reproduction|exact reproduction' "$MANIFEST" >/dev/null; then
    fail "manifest contains an unqualified superiority, novelty, or exact-reproduction claim"
  else
    pass "no unqualified superiority, novelty, or exact-reproduction claim detected"
  fi
fi

if [[ -f "$LEDGER" ]]; then
  source_ids=(ADJ-01 ADJ-02 DAL-01 PN-01 PN-02 DIST-01)
  for source_id in ADJ-01 ADJ-02 DAL-01 PN-01 PN-02 DIST-01; do
    if rg -q --fixed-strings "| $source_id |" "$LEDGER"; then
      pass "source ID resolves in ledger: $source_id"
    else
      fail "source ID does not resolve in ledger: $source_id"
    fi
  done
fi

if [[ -f "$PLAN" ]]; then
  plan_terms=(R0 R1 R2 R3 Creswell DALTON CONCEPTUAL-BASELINE)
  for term in R0 R1 R2 R3 Creswell DALTON CONCEPTUAL-BASELINE; do
    if rg -q --fixed-strings "$term" "$PLAN"; then
      pass "plan contains required control: $term"
    else
      fail "plan omits required control: $term"
    fi
  done
fi

printf '\nPhase-I baseline reproduction gate: '
if [[ "$EXIT_CODE" -eq 0 ]]; then
  printf 'PASS (manifest structurally complete; scientific reproduction still requires evidence)\n'
else
  printf 'BLOCKED/PARTIAL (see failures above; no reproduction claim is permitted)\n'
fi

exit "$EXIT_CODE"
