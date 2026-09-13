# Negative and Non-reportable Result Register

This register separates scientific negatives, design gates, valid
non-reportability, and engineering failures. A non-reportable metric is not
silently converted into a negative scientific finding.

| Evidence | Category | Adjudicated status | Bounded meaning | Prohibited upgrade |
| --- | --- | --- | --- | --- |
| `E-W5-EXP3` | `NEGATIVE_SCIENTIFIC_RESULT` | `NO_GO` | The tested small-head generator-diverse representation design did not improve mean/worst OOD or controlled-splice recovery. | Generator-diverse representation learning is impossible. |
| `E-W5-EXP4` | `NEGATIVE_SCIENTIFIC_RESULT` | `NO_GO` | The tested frozen Chinese HuBERT replacement did not improve under the unchanged Exp2 temporal contract. | SSL representations cannot solve the task. |
| `E-W5-EXP5` | `NEGATIVE_SCIENTIFIC_RESULT` | `NO_GO` | The tested ECAPA-based temporal encoder did not improve over the frozen Exp2 baseline. | Temporal modeling does not work. |
| `E-W4-ADAPTIVE-REDTEAM` | `NOT_REPORTABLE` | `PRIMARY_H4 = NOT_REPORTABLE` | Held-out execution completed with 10/12 winners and 2/12 terminal no-parent cases; the frozen 12/12 gate was not met. | A negative H4 claim, case deletion, replacement, fallback parent, or counterfactual H4. |

`ENGINEERING_FAILURE` is not assigned to the Week4 terminal outcome: the
protocol and evidence chain were completed with integrity PASS. Historical
engineering invalidations remain in their original Week4 records and are not
reclassified as scientific outcomes.
