# CIP-0/CIP-1 reviews and CIP-2 successor

- [CIP-0 independent scientific PASS](CIP0-IndependentReview.md)
- [CIP-1 independent bounded-chain PASS](CIP1-IndependentReview.md)
- [Additive review disposition and DB-04 ancestry](CIP01-ReviewDisposition.json)
- [CIP-2 contract and scope](../../decisions/ATCCIP2Reference.md)
- [CIP-2 retained execution](ATCCIP2Certificate.json)
- [CIP-2 checker](../../scripts/check_atc_cip_reference.py)
- [CIP-2 independent review and additive disposition](../atc-cip-review/README.md)
- [Current scoped admission](../atc-cip-admission/README.md)

The reviews do not require scientific reruns of CIP-0/CIP-1. Their bytes and
hashes remain unchanged. The DB-04 addition links ROOT-00 to CHAIN-01's
consumer without back-editing history or discharging the debt. Reviewer
extra trajectories/corners are diagnostic reports, not locally reproduced
campaigns. CIP-2 now has independent scientific PASS and local retained-record
integrity PASS. The reviewer did not receive the certificate; no independent
exact-record comparison is claimed. Scoped adjudication/source admission
is now recorded in the separate linked ledger. No native or aggregate ATC
authority is added.

From repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_reference.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_reference.py --check
```

Default executes this bounded suite and prints a new record. `--check` only
validates retained identities. Run CIP-0/CIP-1 `--check` as well when checking
the full predecessor chain. All retained paths are repository-relative.
