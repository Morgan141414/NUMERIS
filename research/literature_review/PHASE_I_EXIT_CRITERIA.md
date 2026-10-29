# Phase-I exit criteria: Research Foundation

Status: testable gate, not a declaration that Phase I has passed. The gate is
intended to be evaluated before the mathematical mechanism is presented as a
research contribution.

## Exit decision

Phase I may be marked `PASS` only when every mandatory criterion below is
`PASS`. `PARTIAL`, `BLOCKED`, or `UNRESOLVED` is not a pass. A negative result
is acceptable; an unsupported novelty claim is not.

| ID | Mandatory criterion | Evidence required | Pass condition |
|---|---|---|---|
| P1 | Scope and search protocol | Versioned inclusion/exclusion protocol, query families, search date, and ledger | Protocol exists and every ledger item has a screening decision |
| P2 | Primary-source identity | Direct publisher/proceedings/official links, DOI/title/author check | No unresolved bibliographic contradiction remains in the core ledger |
| P3 | Mechanism extraction | Comparison matrix with controlled object, estimator, adaptation, uncertainty, cost, and limits | Each closest baseline has a filled mechanism card or an explicit `UNKNOWN` |
| P4 | Reproduction plan | `CLOSEST_BASELINE_REPRODUCTION_PLAN.md` and frozen experiment manifest | For adjoint/goal-oriented, likelihood-aware, and DALTON families the plan specifies inputs, metrics, costs, deviations, and stop/fail rules |
| P5 | Local reproducibility status | Run records or explicit blocker records | Every closest baseline is labelled R0--R3, `NOT-REPRODUCED`, or `BLOCKED`, with no ambiguous “implemented” wording |
| P6 | Motivation reproduction | Fixed-grid likelihood-distortion run or a documented source-aligned blocker | The result is recorded as reproduced, not reproduced, or blocked; no inference claim is inferred from citation alone |
| P7 | Frozen NUMERIS question | One target quantity, budget, baseline set, and falsification rule | All are fixed before looking at comparative results |
| P8 | Overlap audit | Line-by-line comparison of the proposed estimator/decision rule with closest baselines | Each component is classified `same`, `known modification`, `unclear`, or `potentially distinct`; `potentially distinct` is not called novel |
| P9 | Claim register | Explicit allowed/prohibited claims in research docs | No document uses “novel”, “first”, “superior”, or “publication-ready” as an established fact |
| P10 | Reproducibility handoff | Exact command/environment/commit instructions for the next phase | A clean checkout can execute the planned smoke test or states the blocker |

## Mandatory failure conditions

Phase I must remain open if any of the following occurs:

- a primary-source DOI, title, or author identity conflicts across project
  documents;
- a nearest comparator is omitted because it is inconvenient to run;
- a local analogue is described as a reproduction without a deviation record;
- the target or budget is changed after seeing results;
- a negative or failed run is removed from the denominator;
- the proposed mechanism has not been compared with adjoint/global,
  functional/goal-oriented, and likelihood-aware alternatives;
- a claimed error estimate has no independent reference-error calibration;
- the review relies on search snippets, blogs, or secondary summaries when a
  primary source is available.

## Required Phase-I handoff package

The handoff to Phase II must contain:

1. the versioned protocol and manifest commit;
2. the bibliography ledger and comparison matrix;
3. the closest-baseline reproduction plan;
4. a completed status table for R0--R3 or explicit blockers;
5. the single selected inference target and budget definition;
6. the claim register and overlap audit;
7. a written decision: `PROCEED`, `REFRAME`, or `STOP/NEGATIVE RESULT`.

`PROCEED` means only that the mathematical investigation is justified as an
open question. It does not mean that novelty, superiority, or publication has
been established.
