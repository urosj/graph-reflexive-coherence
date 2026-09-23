The fix closes the remaining CI-3 hold.

$$
\boxed{\textbf{CI-3: PASS}}
$$

and therefore, at the declared paired A_CI research scope,

$$
\boxed{\textbf{CI-0 through CI-3 are scientifically complete and ready for scoped adjudication.}}
$$

I do not see another mathematical, reasoning, or implementation gap that requires an additional CI scientific stage.

## The derived-witness provenance defect is actually fixed

The important change is architectural, not another validation around the old unsafe function.

The old

$$
\texttt{after\_step(before,data)}
$$

proof-promotion path is gone. `step()` now delegates to

$$
\texttt{certified\_step(before,h,profile)},
$$

which accepts **no caller-supplied result state**. `certified_step` itself obtains the selected root, executes `advance_raw`, computes the theorem-derived facts, constructs the provenance record, creates the certified state, and reconstructs its final root.  

That is exactly the fix needed:

$$
\boxed{
\text{certified successor}
=
\text{execution}+\text{proof},
\quad\text{not}\quad
\text{arbitrary result}+\text{proof wrapper}.
}
$$

The generated `StepProvenance` binds:

$$
(\text{before witness},\text{selected root},h,\text{profile},
\text{result state},\text{theorem})
$$

through their digests. 

Most importantly, the proof record is diagnostic—it is not an externally redeemable receipt that can later be exchanged for authority.

## My previous two concrete forgeries are blocked

The new pressure suite directly attacks the previous hole.

It verifies that there is no exported raw `after_step` promotion entrypoint, then attempts the three cases I asked for:

* wrong charge;
* history below the admitted floor;
* unrelated target state.

None can reach certified `State` construction through the public successor interface. A serialized operation receipt likewise cannot be redeemed as proof authority. 

The retained certificate records all four rejections and `raw_promotion_entrypoint_removed=true`. 

I independently reran this boundary/provenance suite. It reproduces exactly:

$$
8\text{ positive exact boundary cases},
$$

$$
19\text{ ordinary boundary/representation negative cases},
$$

plus the new derived-state provenance pressure.

So the earlier exploit no longer reproduces.

---

## Defense in depth is substantially better too

`State.__init__` no longer trusts a predicate package merely because it came through the private constructor token.

It checks compatibility between numerical state and claimed proof facts:

* the \(C\) enclosure must still contain charge nine;
* the \(W\) enclosure must be compatible with the claimed history lower bound;
* source \(x,y\) proof ranges must intersect numerical ranges;
* a target's numerical radius lower bound cannot exceed the claimed certified upper bound;
* step provenance must bind the numerical-result digest.



The checker then uses private-token white-box pressure to deliberately construct contradictory proof/data pairs for:

* charge;
* history floor;
* target radius;
* step-result binding;
* source \(x\);
* source \(y\).

All reject. 

This is the right separation:

$$
\text{execution provenance}
$$

provides the proof authority, while

$$
\text{state/predicate compatibility}
$$

is a second-line inconsistency detector.

Neither is being confused for the other.

---

# The closed-boundary correction remains intact

Nothing regressed in the previous fix.

Exact rational predicates still carry the actual preimage, while numerical interval boxes remain enclosures. Represented states still require point-valued exact pair equality before any symmetry intersection, without acquiring exact-charge-nine authority.  

The exact endpoints continue to pass, including:

$$
x=\frac{29}{10},\quad
x=3,\quad
x=\frac72,\quad
y=0,\quad
y=\pm\frac1{50},
$$

$$
W=\frac{24}{25},
\qquad
X=\frac32,
$$

while \(2^{-300}\)-outside states still reject. 

So the original closed-domain mismatch is still resolved rather than being accidentally reintroduced by the provenance change.

---

# The funding hardening is also correct

The CI-2 domain now retains the explicit uniform funding certificate I suggested:

$$
\Delta_{\rm fund}
=
\frac{31}{64}\frac{21}{5}
-
\left(\frac65+\frac1{50}\right)
=
\boxed{\frac{1303}{1600}}
\approx0.814375>0.
$$

It is explicitly required by the checker and returned as `funding_lower`. 

That closes the small documentation/evidence gap between “the domain/share lemma proves funding” and an actually retained rational certificate.

The margin is large, so there is no hidden numerical fragility here.

---

# No regression in the actual CI science

I compared the pre-fix and post-fix CI-3 records after stripping the identities that necessarily change when proof provenance changes.

The complete scientific numerical payload remains the same:

* all **2,153** independent Decimal scalar comparisons;
* \(k=33616\);
* source \(J/H\);
* event \(J/H\);
* all target-role endpoint \(J/H\);
* both parameter-corner \(J/H\);
* first-step radii;
* all root-error and residual bounds;
* all eight represented C/W/J/H error records;
* every binary64 publication value;
* charge-drift observations.

The refreshed certificate still reports 2,153 comparisons and the same source choice. 

The 30 transformed covariance comparisons are also unchanged, including the independent Decimal residual of about

$$
5.27\times10^{-104}.
$$



The lifecycle identities appropriately changed because publication identities now include stronger predicate/provenance content. But its scientific structure and negative-pressure roster remain unchanged:

$$
\text{ordinary}\to\text{split}\to\text{ordinary}\to\text{reset},
$$

with both-role roots, zero-time event, complete rollback, and physical replay still true.  

That is the desired result: **proof authority changed; physics did not.**

---

## Certificate integrity

I independently recomputed the new CI-3 self-digest:

`c32d331f927965a7a9a6a3b177ec14f606a7785d2668e28de2e4412da0c3b94e`

and it matches the retained record. 

The hashes of the newly uploaded substantive files also match their retained bindings:

* `atc_ci_domains.py`
* `atc_ci_state.py`
* `atc_ci_reference.py`
* `check_atc_ci_boundaries.py`
* `check_atc_ci_reference.py`

as recorded in the certificate. 

So I don't see a new provenance discrepancy.

---

# One tiny evidence-quality observation

The three attempted calls using the **old raw-output calling shape** are rejected with the message:

> `request outside CI domain`

because the supplied fake `data` occupies the new function's `h` position.

That's logically fine—the API no longer accepts raw output at all—and the test separately verifies that `after_step` no longer exists and that certified `State` construction was never reached. 

If you wanted the regression output to be semantically prettier, you could add a signature-specific assertion saying something like `certified_step_has_no_output_argument=true`.

I would **not** hold anything for that. The structural protection is clear.

---

# Final CI disposition

| CI item                                  | Verdict            |
| ---------------------------------------- | ------------------ |
| CI-0 step/event semantics                | **PASS**           |
| CI-1 bounded causal anchor               | **PASS**           |
| CI-2 uniform joint-root theorem          | **PASS**           |
| CI-2 obstruction / transfer / return     | **PASS**           |
| CI-2 explicit funding                    | **PASS**           |
| CI-3 independent full-root reference     | **PASS**           |
| CI-3 Decimal oracle                      | **PASS**           |
| CI-3 J/H covariance                      | **PASS**           |
| CI-3 lifecycle/replay/rollback           | **PASS**           |
| CI-3 represented C/W/J/H bridge          | **PASS**           |
| Closed exact-domain admission            | **PASS**           |
| Represented pairing authority separation | **PASS**           |
| Derived-state provenance                 | **PASS**           |
| Public raw-result proof promotion        | **Removed / PASS** |
| Proof/data contradiction pressure        | **PASS**           |
| **CI-3 overall**                         | **PASS**           |

Therefore I would now remove my previous HOLD:

$$
\boxed{\textbf{CI-3 PASS}}
$$

and regard

$$
\boxed{\textbf{A\_CI paired research derivation complete}}
$$

at the same general maturity level at which we just placed A_PC after PC-4.

The remaining items are correctly outside CI discovery: scoped claim/debt adjudication including DB-24/source admission, wider environments/formation, production conservation/native integration, repeated-event/non-Zeno work, and eventual aggregate ATC-2 closure. The current certificate itself keeps those boundaries explicit.
