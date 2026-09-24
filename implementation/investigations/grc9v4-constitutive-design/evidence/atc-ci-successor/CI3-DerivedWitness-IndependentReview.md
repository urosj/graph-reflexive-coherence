The update fixes the defect I reported, but I found one new proof-interface issue that I would correct before declaring CI-3 fully closed.

My current disposition is:

$$
\boxed{\textbf{CI-2: PASS — remains scientifically closed}}
$$

$$
\boxed{\textbf{CI-3 core: PASS}}
$$

$$
\boxed{\textbf{closed-boundary correction: PASS}}
$$

$$
\boxed{\textbf{CI-3 final closure: HOLD narrowly on derived-state witness provenance}}
$$

The hold does **not** require reopening the CI law, root theorem, obstruction, transfer physics, return proof, oracle, or representation campaign.

## 1. The original boundary defect is fixed correctly

The new architecture makes the right conceptual distinction:

$$
\boxed{\text{mathematical predicate truth}\neq\text{outward numerical enclosure}}
$$

`atc_ci_state.py` now retains exact rational preimages and exact \(x,y,W\)-floor/radius predicates for exact states, while derived states retain separately certified operation facts.  

The root-domain checks now consume those predicates rather than asking whether the lower endpoint of an outward interval happens to lie on the correct side of a non-dyadic rational boundary. 

That is exactly the repair I wanted.

I independently reran `check_atc_ci_boundaries.py`. All eight positive boundary cases reproduce exactly:

* \(x=29/10\);
* source \(W=24/25\);
* event \(x=3,y=0\);
* \(x=7/2\);
* \(y=1/50\) with \(W=24/25\);
* reset \(y=-1/50\);
* target \(W=24/25\);
* target \(X=3/2\).

And all 19 negative controls reject, including states only

$$
2^{-300}
$$

outside the exact boundary. The checker explicitly tests those cases rather than using a tolerance. 

The refreshed certificate retains the same successful boundary evidence and those sub-grid negative controls. 

So:

$$
\boxed{\textbf{closed-domain CI-2}\leftrightarrow\textbf{CI-3 exact admission: FIXED}}
$$

## 2. The represented-pairing hardening is also correct

This was my smaller previous concern.

Represented states now have a deliberately weaker rule:

* point-valued numerical inputs only;
* exact binary/dyadic equality of each paired \(C\) and \(W\);
* **no inference of exact charge nine**.



And `advance_raw()` checks that represented pairing **before** it invokes the symmetry-based `paired_enclosures()` operation. 

`represented_step()` repeats the check after publication rounding. 

The boundary test then deliberately patches `paired_enclosures()` to fail if unequal/overlapping representations get far enough to invoke it. Unequal \(C\), unequal \(W\), and merely overlapping non-point boxes are all rejected first. 

That is a strong fix.

The non-charge-nine paired represented control is particularly important: it still runs diagnostically, but its root has no exact domain-witness binding. The refreshed certificate reflects that distinction throughout: exact roots have `domain_witness_binding`, represented roots have it as `null`. 

## 3. The scientific CI-3 payload remains intact

I reran the updated substantive stage campaign.

It reproduces all

$$
\boxed{2153}
$$

independent scalar comparisons exactly, with the original CI-native

$$
\boxed{k=33616}.
$$

The updated root identities differ—as they should—because they now bind predicate provenance. The actual \(J,H,C,W\) enclosures and scientific staging have not changed. The certificate says exactly this, rather than pretending the identities should remain old. 

The refreshed root records now bind both:

$$
\text{numerical state digest}
$$

and

$$
\boxed{\text{domain witness digest}}.
$$

For example the retained source-selected root contains both bindings independently. 

I also reran the transformed graph covariance pressure; the 30 joint \(J/H\) comparisons remain unchanged.

Both certificate self-digests independently reproduce:

* CI-2:
  `a14c2589a23e8e1ecbcc3fd11006a3152317b7ed05343db83661cb9b977303bb`
* CI-3:
  `4fa90d7f48448af20b0182875e0fb7dd3e0cb3669a7a6fc511fa932436d0fc65`

and all newly uploaded correction-file hashes I checked agree with their source bindings.

So I agree with the updated statement that **CI-2 is scientifically closed**. 

---

# 4. New issue: `after_step()` can forge certified theorem facts

This is the remaining problem.

The working note now says:

> Derived states carry only facts proved by their operation. 

That is the correct principle.

But the implementation does not yet enforce it.

The public function

```python
after_step(before, data)
```

accepts:

1. a valid certified `before`;
2. **an arbitrary `a.State` supplied by the caller**.

It then constructs a new `Predicates` object with default

$$
\texttt{charge}=9,\qquad \texttt{paired}=True,
$$

and promotes several theorem-derived facts. 

Nothing proves that `data` is actually the output of the CI continuity + writer operation from `before`.

The comment says:

> “Only called after a domain-admitted CI step and certified log writer.”

but that is currently a convention, not an enforced contract.

### I falsified it directly

I started from a legitimate exact target witness.

Then I constructed arbitrary paired numerical data with total charge

$$
Q=8.4
$$

rather than 9 and called:

```python
forged = predicates.after_step(before, bad_data)
root(forged, profile)
```

Result:

$$
\boxed{\texttt{root()} \text{ admits it}}
$$

with the predicates claiming

$$
Q=9.
$$

I separately supplied

$$
W_e=0.8
$$

on every edge, below

$$
M=\frac{24}{25}=0.96.
$$

`after_step()` sets

$$
\texttt{history\_lower}
=
\max(M,\min W_{\rm numerical})
=
M,
$$

and the resulting forged state is again accepted by `root()`.

So currently one can manufacture:

$$
\boxed{
\text{arbitrary paired numerical state}
\longrightarrow
\text{certified CI theorem witness}
}
$$

provided one already has some admitted `before`.

That is not just hypothetical misuse of interval overlap; it bypasses the new proof layer itself.

## Why the private `State` token does not solve this

The `State` constructor itself is appropriately protected by `_TOKEN`. 

But callers do not need the token.

`after_step()` possesses it internally and will create the certified state on their behalf.

Therefore:

$$
\boxed{\texttt{after\_step} \text{ is presently an unintended proof-authority mint}}
$$

rather than merely a state-conversion helper.

---

# 5. This does not invalidate the retained CI-3 run

This distinction matters.

The actual CI-3 `step()` path is:

$$
\texttt{root(state)}
\rightarrow
\texttt{advance\_raw(...)}
\rightarrow
\texttt{predicates.after\_step(state,data)}
\rightarrow
\texttt{root(following)}.
$$



There, `data` really is the output produced immediately by the certified continuity/writer computation.

So the retained:

* 2153 oracle comparisons;
* boundary results;
* lifecycle sequence;
* represented-error campaign;
* CI-1 preservation;
* actual target roots

remain valid.

This is therefore analogous to a capability leak in a proof API, **not evidence that the certified trajectory itself was wrong**.

That is why I would retain:

$$
\boxed{\text{CI-3 core PASS}}
$$

but not yet upgrade the complete conformance layer to closed.

---

# 6. Recommended correction

I would not try to solve this merely by checking more interval endpoints inside `after_step()`.

Those would be useful consistency checks, but they cannot establish:

> “this data was actually produced by this certified operation.”

### Best structural fix

Make the theorem-bearing successor impossible to construct from arbitrary raw `data`.

For example:

$$
\texttt{advance\_raw}
$$

could return an internal transition witness containing:

$$
\begin{aligned}
&\text{before witness digest},\\
&\text{selected joint-root digest},\\
&h,\\
&\text{profile digest},\\
&\text{result numerical-state digest},\\
&\text{proved operation facts}.
\end{aligned}
$$

Then the predicate layer accepts only that object:

$$
\boxed{
\texttt{certify\_after\_step(before, transition)}
}
$$

rather than arbitrary `data`.

An even simpler architecture would be to let the exact `step()` path construct the certified successor itself and keep any raw predicate-promotion helper private to that path.

The invariant to enforce is:

$$
\boxed{
\text{operation-proved predicates may only originate from an authenticated execution of that operation}.
}
$$

### Defense-in-depth consistency checks

I would additionally have `State.__init__` verify that the numerical enclosure is at least *compatible* with the certified predicates:

$$
9\in\sum_i C_i,
$$

each \(W_e\) enclosure intersects

$$
[\texttt{history\_lower},1],
$$

certified \(x,y\) ranges intersect their numerical enclosures, and the numerical target-radius lower bound does not already exceed its certified upper bound.

These checks are not proofs; they prevent contradictory proof/data pairs from surviving unnoticed.

---

# 7. Add three negative tests

The boundary checker is already the natural place.

I would add at least:

```text
forged_after_step_wrong_charge
forged_after_step_history_below_floor
forged_after_step_unrelated_target_state
```

All should reject **before a certified `State` can be produced**.

That would directly pressure the exact defect rather than relying on source-code structure.

---

## One smaller CI-2 evidence hardening

This is not a blocker, but I noticed that the widened CI-2 transfer domain says the same source-selected share gives lawful transfer, and `atc_ci_state.transfer()` comments that the domain/share lemma proves funding, but the CI-2 rational certificate does not actually retain a funding inequality.

The proof is easy and has a huge margin.

Across

$$
3\le x\le\frac72,\qquad
|y|\le\frac1{50},\qquad
\frac{31}{64}\le s\le\frac{33}{64},
$$

the worst child-funding surplus is

$$
\boxed{\frac{1303}{1600}\approx0.814375>0}.
$$

So I would add something like

$$
\texttt{funding\_lower}=1303/1600
$$

to `domain_bounds()` and explicitly `require(funding_lower > 0)`.

That does not change CI-2's PASS; it just turns an implicit/comment-level transfer fact into retained evidence.

---

# Revised verdict

| Item                                             | Verdict                 |
| ------------------------------------------------ | ----------------------- |
| CI-2 mathematics                                 | **PASS / closed**       |
| Exact \(x,W,y,X\) boundaries                     | **PASS**                |
| \(2^{-300}\)-outside discrimination              | **PASS**                |
| Exact predicate / numerical-box separation       | **PASS**                |
| Represented pairing before symmetry intersection | **PASS**                |
| Rounded non-Q9 state kept diagnostic-only        | **PASS**                |
| Root bound to predicate provenance               | **PASS**                |
| Original J/H/C/W scientific payload              | **PASS**                |
| Independent Decimal oracle                       | **PASS**                |
| Covariance                                       | **PASS**                |
| Lifecycle positive path                          | **PASS**                |
| Finite representation path                       | **PASS**                |
| `after_step` derived-proof provenance            | **FAIL — fix required** |
| CI-2 explicit funding certificate                | **Harden**              |
| **CI-3 closure**                                 | **HOLD narrowly**       |

So the previous boundary HOLD is genuinely resolved.

The only reason I would **not yet mark CI-3 closed** is that the new machinery introduced to solve it currently lets callers manufacture an operation-derived proof witness without proving the operation happened.

Once that constructor is sealed and the three forge controls pass, I do **not** see another scientific CI stage that needs doing. At that point I would expect:

$$
\boxed{\textbf{CI-3 PASS and A\_CI paired research program ready for scoped adjudication}}
$$

without reopening any of CI-1 or CI-2.
