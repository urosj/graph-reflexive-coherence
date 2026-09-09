"""Symbolic parent-rule pressure; no human-authority or runtime/G2 evaluation.

Receipt labels are opaque symbols, not content hashes. Commit grouping, typed
roles, hash validation, numerical truth and atomic publication are prerequisites
outside this check. This is not a second current-runtime verification path.
"""

from __future__ import annotations

from copy import deepcopy
import json

POLICY = "grcv4-previous-successful-primary-v1"


def projection(actions):
    """Four-receipt C_OS examples; the validator does not impose that arity."""
    groups = []
    previous = None
    for index, action in enumerate(actions):
        primary = f"{index}:{action}:primary"
        parents = () if previous is None else (previous,)
        groups.append(
            [(primary, parents)]
            + [
                (f"{index}:{action}:{role}", parents)
                for role in ("charge", "candidate-history", "carrier-history")
            ]
        )
        previous = primary
    return groups


def validate_parent_projection(groups):
    """Check ordered, already-typed commit groups, each with primary first."""
    previous = None
    seen = set()
    for group in groups:
        if not group:
            raise ValueError("empty successful commit group")
        expected = () if previous is None else (previous,)
        for receipt_id, parents in group:
            if receipt_id in seen or parents != expected:
                raise ValueError("duplicate receipt or wrong predecessor")
            seen.add(receipt_id)
        previous = group[0][0]


def main():
    positives = {
        "empty_ledger": (),
        "ordinary_root": ("step",),
        "administrative_first": ("reset", "step"),
        "interleaved": ("step", "reset", "rebase", "step"),
        "crossings": ("step", "migration", "step", "event", "step"),
        "zero_duration_commits": ("zero", "zero", "step"),
    }
    for actions in positives.values():
        validate_parent_projection(projection(actions))

    # Copying a prefix does not require fresh globally unique receipt labels.
    prefix = projection(("step", "reset"))
    validate_parent_projection(deepcopy(prefix))
    for tail in ("migration", "event"):
        fork = projection(("step", "reset", tail))
        if fork[:2] != prefix:
            raise AssertionError("fork changed the inherited prefix")
        validate_parent_projection(fork)

    base = projection(("step", "reset", "step"))
    first, previous, current = (group[0][0] for group in base)
    bad_parents = {
        "missing_parent": (),
        "skipped_reset_old_local_convention": (first,),
        "foreign_parent": ("foreign:primary",),
        "forward_parent": (current,),
        "duplicate_parent": (previous, previous),
        "multiple_parents": (first, previous),
        "reordered_multiple_parents": (previous, first),
        "nonprimary_previous_receipt": (base[1][1][0],),
        "intra_commit_auxiliary_parent": (base[2][1][0],),
    }
    mutations = {}
    for name, parents in bad_parents.items():
        altered = deepcopy(base)
        # A forward pointer from the reset goes to the later ordinary commit.
        index = 1 if name == "forward_parent" else 2
        altered[index] = [(rid, parents) for rid, _ in altered[index]]
        if name == "forward_parent":
            # Make this a forward but acyclic graph, distinct from the cycle case.
            altered[2] = [(rid, (first,)) for rid, _ in altered[2]]
        mutations[name] = altered

    altered = deepcopy(base)
    altered[2] = [(rid, (current,)) for rid, _ in altered[2]]
    mutations["self_parent"] = altered
    altered = deepcopy(base)
    altered[1] = [(rid, (current,)) for rid, _ in altered[1]]
    mutations["two_commit_cycle"] = altered
    altered = deepcopy(base)
    altered[2][1] = (altered[2][1][0], (first,))
    mutations["auxiliary_disagrees"] = altered
    altered = deepcopy(base)
    altered[0] = [(rid, ("foreign:root",)) for rid, _ in altered[0]]
    mutations["nonempty_root_parent"] = altered
    altered = deepcopy(base)
    altered[2][1] = altered[2][0]
    mutations["duplicate_receipt_id"] = altered
    mutations["reordered_commit_groups"] = [base[0], base[2], base[1]]
    mutations["empty_group"] = [base[0], []]

    for name, groups in mutations.items():
        try:
            validate_parent_projection(groups)
        except ValueError:
            continue
        raise AssertionError(f"invalid symbolic projection accepted: {name}")

    print(
        json.dumps(
            {
                "proposal_policy": POLICY,
                "symbolic_valid_cases": len(positives) + 3,
                "symbolic_mutations_rejected": sorted(mutations),
                "runtime_executions": 0,
                "hash_or_atomicity_validation": False,
                "authority_acceptance_evaluated": False,
                "G2_accepted": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
