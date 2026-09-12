"""Read-only joint package integrity, not event or coordinate runtime evidence."""

import build_p972b_event_release as r
from pygrc.models.grc_v4_event_codec import EVENT_RELEASE_ID, load_event_schemas


def check(root=None):
    if root is not None and root.resolve() != r.b.ROOT.resolve():
        raise ValueError("joint package checker loaded from a different repository subject")
    for name, expected in r.build().items():
        if (r.b.ROOT / name).read_bytes() != expected:
            raise ValueError("joint event package drift: " + name)
    load_event_schemas()
    return dict(release_id=EVENT_RELEASE_ID, contract_package_verified=True,
                runtime_evidence_evaluated=False, new_G2_support=[], G3_accepted=False)


if __name__ == "__main__":
    print(check())
