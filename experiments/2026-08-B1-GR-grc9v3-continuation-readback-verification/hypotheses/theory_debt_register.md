# Theory Debt Register View

Source: controlling specification, Section 9.1.

Debt remains explicit rather than being repaired by implementation labels.
GRV0 serializes every `D-*` row with its consequence and decision route. Later
gates may resolve, preserve, or reopen a row only through the declared route.
