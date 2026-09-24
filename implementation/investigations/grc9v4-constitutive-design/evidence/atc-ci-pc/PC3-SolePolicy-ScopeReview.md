For the **selected PC-2 law**, no additional contract is needed before PC-3. The tightened law is now complete enough:

$$
c_t=c_s
$$

fixes polarity, and the event is explicitly allowed to land in the signed target carrier ball; PC-3 then has the obligation to prove continuation from that state. The current program already assigns exactly that responsibility to PC-3. 

The **PSD alternative is different**. Because it does not preserve the same \(c_t\) readout, it is no longer simply “the same PC-2 law with the extra property \(Z_t\succeq0\).” It is a genuinely different carrier-continuation law. The existing note already correctly says that PSD preservation would require a separate domain/policy decision and is not the selected event policy. 

So I would use this rule:

$$
\boxed{
\begin{array}{ll}
\text{PSD alternative remains a pressure/control result} &
\Rightarrow \text{its contract can remain unresolved for now},\\[2mm]
\text{PSD alternative may rescue a failed PC-3} &
\Rightarrow \text{its contract must be frozen before PC-3}.
\end{array}}
$$

The second case matters scientifically. If we run PC-3 with the signed isometric lift, discover that its target continuation fails, and **then** define whatever PSD relational invariant happens to make the nonlinear lift succeed, that would be outcome-driven policy selection—the exact thing this investigation has been avoiding.

### What I recommend

I would **not delay PC-3 to fully develop the PSD contract**. Instead, before PC-3, add one explicit scope statement:

> `pc_star_fission_relational_lift_lossless_v1` is the sole PC-3 carrier policy. The PSD-preserving nonlinear construction remains a mathematical pressure control and is not an admissible fallback in PC-3. Failure of the selected signed lift is retained as failure; any PSD-preserving successor requires a separately preregistered cross-topology relational-continuity contract and a new bounded investigation.

That is enough.

It keeps the causal experiment clean:

$$
\text{PC-1 source}
\to
\boxed{L_{\rm rel},\ c_t=c_s}
\to
\text{PC-3 target dynamics}.
$$

No policy switching after seeing the target.

---

### Why the PSD alternative really does need a new contract if revisited

The distinction you recorded is substantive.

For the selected linear map, the target readout was constructed so that

$$
c_t=c_s.
$$

For the PSD construction, using

$$
f=-c\sqrt{\frac{A}{A+D}},
\qquad
g=c\sqrt{\frac{D}{A+D}},
\qquad
h_b=\frac{4c^2}{A+D},
$$

the **same** target incidence readout does not generally return \(c\). The PSD map is injective, so \(c\) remains recoverable, but recovery now depends on retained \(A,D\) as well as the bridge coordinates. 

So its physical claim would have to be something more like

$$
\mathcal C_t(Z_t)=\mathcal C_s(Z_s),
$$

where \(\mathcal C_t\) is a new nonlinear relational observable.

That is not bookkeeping. It answers a different question:

> What exactly counts as “the same persistent relation” when the carrier is required to remain PSD?

We have not derived that law yet.

The fact that the PSD map is invertible proves **information retention**; it does not by itself prove the right notion of **relational continuity**.

That is precisely why it should not silently inherit the \(c_t=c_s\) contract.

---

### The five-dimensional image correction does not create another pre-PC-3 debt

That correction is also important, but I would treat it as a scope clarification rather than another contract.

The target decorated carrier domain has dimension seven, while

$$
L_{\rm rel}(\mathcal Z_s)
$$

is only a five-dimensional embedded event image. The inverse therefore applies only on that image. After one PC writer step, the target carrier can leave it; there is no requirement that ordinary target dynamics preserve the event image. The working note already says the inverse is an event-preimage inverse, not a general time-reversal law. 

So the proper sequence is:

$$
Z_s
\xrightarrow[\text{event}]{L_{\rm rel}}
Z_t^{(0)}
\in\mathcal I_{\rm evt}^{(5)}
\subset
\mathcal Z_t^{(7)},
$$

then

$$
Z_t^{(0)}
\xrightarrow{\text{ordinary PC}}
Z_t^{(1)}
\in\mathcal Z_t^{(7)}.
$$

PC-3 needs to prove continuation in the **seven-dimensional target carrier domain**, starting from the five-dimensional event image. It does not need to prove invariance of the five-dimensional image.

That is actually cleaner.

## So I would proceed

Before PC-3 I would freeze just three things:

1. selected carrier map:

   $$
   L_{\rm rel};
   $$

2. its cross-topology continuity law:

   $$
   \boxed{c_t=c_s};
   $$

3. the falsification discipline:
   **the PSD nonlinear construction cannot be substituted if PC-3 fails.**

Then go directly into PC-3.

The PSD result can remain an important note:

$$
\boxed{\text{PSD preservation is compatible with losslessness, but its relational-continuity law remains undeclared.}}
$$

If the signed lift fails dynamically, that becomes the starting point of a **new PC-2b investigation**, not an adjustment inside PC-3. That preserves the scientific value of either outcome.
