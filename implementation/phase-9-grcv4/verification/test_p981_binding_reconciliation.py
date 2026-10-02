"""Current-boundary pressure for exact post-G3 maintenance reconciliation.

Mutations are in-memory views consumed by the real checker. No live repository
file or historical acceptance is changed by a pressure case.
"""

import unittest
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import phase9_implementation_policy as p


@contextmanager
def candidate(*, records=None, contents=None, additions=()):
    records, contents = records or {}, contents or {}
    original_read, original_bytes, original_git = p.read, Path.read_bytes, p.git

    def read(path):
        name = str(path.relative_to(p.ROOT))
        return deepcopy(records[name]) if name in records else original_read(path)

    def read_bytes(path):
        try:
            name = str(path.relative_to(p.ROOT))
        except ValueError:
            return original_bytes(path)
        return contents[name] if name in contents else original_bytes(path)

    def git(root, *args):
        result = original_git(root, *args)
        if args == ("ls-files", "--cached", "--others", "-z"):
            result += b"".join(name.encode() + b"\0" for name in additions)
        return result

    with (
        patch.object(p, "read", side_effect=read),
        patch.object(Path, "read_bytes", read_bytes),
        patch.object(p, "git", side_effect=git),
    ):
        yield


def updated(record, edit):
    value = deepcopy(record)
    edit(value)
    value["record_digest"] = p.digest_record(value)
    return value


class BindingReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = p.read(p.ROOT / p.POLICY)
        cls.work = p.read(p.ROOT / p.WORK)
        cls.record = p.binding_reconciliation(p.ROOT)

    def test_current_boundary_and_exact_committed_roster(self):
        boundary, tree = p.current_boundary(p.ROOT)
        self.assertEqual(boundary, self.policy)
        self.assertEqual(tree["registered_runtime_files"], len(self.work["entries"]))
        self.assertEqual(len(p.RECONCILED_CONTEXT_PATHS), 392)
        self.assertEqual(len(p.RECONCILED_RUNTIME), 13)
        self.assertFalse(p.RECONCILED_CONTEXT_PATHS & set(p.RECONCILED_RUNTIME))
        for field, old_manifest, rows_field in (
            ("maintenance", p.POLICY, "artifact_bindings"),
            ("work", p.WORK, "entries"),
        ):
            import json

            old = json.loads(
                p.git(
                    p.ROOT,
                    "show",
                    self.record["previous_boundary_commit"] + ":" + old_manifest,
                )
            )
            hashes = {row["path"]: row["sha256"] for row in old[rows_field]}
            for row in self.record["stale_bindings"][field]:
                self.assertEqual(row["previous_sha256"], hashes[row["path"]])
                self.assertEqual(
                    row["subject_sha256"],
                    p.sha(
                        p.git(
                            p.ROOT,
                            "show",
                            self.record["subject_commit"] + ":" + row["path"],
                        )
                    ),
                )

    def test_rehashed_reconciliation_cannot_change_scope_or_subject(self):
        edits = (
            lambda v: v.update(subject_commit="HEAD"),
            lambda v: v["context_bindings"].pop(),
            lambda v: v["context_bindings"].append(v["context_bindings"][0]),
            lambda v: v["runtime_additions"][0].update(iteration_id="P9-8.1b"),
            lambda v: v["runtime_additions"][0].update(
                path="src/pygrc/models/grc_9_v4_row.py"
            ),
            lambda v: v.update(claim_ceiling="all specialization support accepted"),
        )
        for edit in edits:
            with (
                self.subTest(edit=edit),
                candidate(records={p.RECONCILIATION: updated(self.record, edit)}),
                self.assertRaisesRegex(ValueError, "untrusted binding reconciliation"),
            ):
                p.current_boundary(p.ROOT)

    def test_rehashed_maintenance_cannot_rewrite_retained_context(self):
        names = (
            p.INV + "GRC9V4ConstitutiveDesignDecisionLedger.md",
            p.PHASE + "tranche-8/P9-8.0-AggregateReview.md",
        )
        for name in names:
            content = (p.ROOT / name).read_bytes() + b"\nchanged verdict\n"
            policy = updated(
                self.policy,
                lambda v, name=name, content=content: next(
                    row for row in v["artifact_bindings"] if row["path"] == name
                ).update(sha256=p.sha(content)),
            )
            with (
                self.subTest(path=name),
                candidate(records={p.POLICY: policy}, contents={name: content}),
                self.assertRaisesRegex(
                    ValueError, "retained reconciliation context changed"
                ),
            ):
                p.current_boundary(p.ROOT)

    def test_rehashed_roster_cannot_drop_a_protected_context_path(self):
        name = next(iter(p.RECONCILED_CONTEXT_PATHS))
        policy = updated(
            self.policy,
            lambda v: v.update(
                artifact_bindings=[
                    row for row in v["artifact_bindings"] if row["path"] != name
                ]
            ),
        )
        with (
            candidate(records={p.POLICY: policy}),
            self.assertRaisesRegex(
                ValueError, "implementation maintenance roster drift"
            ),
        ):
            p.current_boundary(p.ROOT)

    def test_helper_content_still_needs_a_current_work_binding(self):
        name = "src/pygrc/models/grc_v4_numerics.py"
        with (
            candidate(contents={name: (p.ROOT / name).read_bytes() + b"\n# changed\n"}),
            self.assertRaisesRegex(ValueError, "work content binding mismatch"),
        ):
            p.current_boundary(p.ROOT)

    def test_helper_cannot_borrow_another_owner_or_specialization_leaf(self):
        name = "src/pygrc/models/grc_v4_numerics.py"
        for leaf, reason in (
            ("P9-2.1", "different owning leaf"),
            ("P9-8.1a", "exact leaf/path entry"),
            ("P9-8.1b", "exact leaf/path entry"),
        ):
            work = updated(
                self.work,
                lambda v, leaf=leaf: next(
                    row for row in v["entries"] if row["path"] == name
                ).update(iteration_id=leaf),
            )
            with (
                self.subTest(leaf=leaf),
                candidate(records={p.WORK: work}),
                self.assertRaisesRegex(ValueError, reason),
            ):
                p.current_boundary(p.ROOT)

    def test_rehashed_work_cannot_promote_support(self):
        for field in (
            "accepted_generic_runtime_support",
            "admitted_specialization_support_sets",
        ):
            work = updated(self.work, lambda v, field=field: v[field].clear())
            with (
                self.subTest(field=field),
                candidate(records={p.WORK: work}),
                self.assertRaisesRegex(ValueError, "beyond accepted G2"),
            ):
                p.current_boundary(p.ROOT)

    def test_exact_optional_flint_extra_and_legacy_dependencies(self):
        before = p.git(p.ROOT, "show", p.BASELINE + ":pyproject.toml")
        after = (p.ROOT / "pyproject.toml").read_bytes()
        p.integration("pyproject.toml", before, after)
        for replacement in (
            b"python-flint==0.9.1",
            b"python-flint>=0.9.0",
            b"numpy==0.9.0",
        ):
            with (
                self.subTest(replacement=replacement),
                self.assertRaisesRegex(
                    ValueError, "unreviewed V4 exact-backend dependency"
                ),
            ):
                p.integration(
                    "pyproject.toml",
                    before,
                    after.replace(b"python-flint==0.9.0", replacement),
                )
        with self.assertRaisesRegex(ValueError, "non-additive dependency integration"):
            p.integration(
                "pyproject.toml",
                before,
                after + b'\n[unreviewed]\ndependency = "python-flint"\n',
            )

    def test_unlisted_runtime_and_research_additions_still_reject(self):
        for name in (
            "src/pygrc/models/grc_9_v4_unreviewed.py",
            p.INV + "research/unreviewed.py",
            p.PHASE + "tranche-8/unreviewed.json",
        ):
            with (
                self.subTest(path=name),
                candidate(additions=(name,)),
                self.assertRaisesRegex(
                    ValueError, "unauthorized source/test/planning addition"
                ),
            ):
                p.current_boundary(p.ROOT)

    def test_legacy_source_remains_frozen(self):
        name = "src/pygrc/models/grc_v3.py"
        with (
            candidate(contents={name: (p.ROOT / name).read_bytes() + b"\n# changed\n"}),
            self.assertRaisesRegex(ValueError, "frozen bytes changed"),
        ):
            p.current_boundary(p.ROOT)

    def test_published_run_cannot_be_rehashed_as_new_work(self):
        name = next(
            row["path"]
            for row in self.work["entries"]
            if row["path"].endswith("/run.json")
        )
        content = (p.ROOT / name).read_bytes() + b"\n"
        work = updated(
            self.work,
            lambda v: next(row for row in v["entries"] if row["path"] == name).update(
                sha256=p.sha(content)
            ),
        )
        with (
            candidate(records={p.WORK: work}, contents={name: content}),
            self.assertRaisesRegex(ValueError, "published run evidence is immutable"),
        ):
            p.current_boundary(p.ROOT)


if __name__ == "__main__":
    unittest.main()
