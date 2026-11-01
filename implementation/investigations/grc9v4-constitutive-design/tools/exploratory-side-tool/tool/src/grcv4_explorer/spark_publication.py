"""Read-only editorial documents; these are not scientific authority projections."""
from pathlib import Path

from .basin import _bound_file
from .canonical import load_json_object, record_digest
from .spark_earlier_sc3_metadata import need

INV = 'implementation/investigations/grc9v4-constitutive-design/'
VALIDATION = INV + 'evidence/spark-completion/applicability/earlier-closure/EarlierSC3Validation.json'
DOCUMENTS = frozenset(INV + 'drafts/' + name for name in (
    'README.md', '2026-11-GRC-V4.md', 'spark-completion/Proposal.md',
    'spark-completion/Traceability.md',
))


def spark_publication_source(root, side, path):
    """Serve only current adopted editorial documents whose bytes match the recorded check."""
    if path not in DOCUMENTS:
        raise KeyError('not an indexed spark publication document')
    root = Path(root)
    validation = load_json_object(root / VALIDATION)
    need(validation.get('record_digest') == record_digest(validation, 'record_digest'),
         'changed spark publication validation record')
    editorial = validation.get('editorial_consolidation', {})
    need(editorial.get('status') == 'passed_self_contained_proposal_and_full_manuscript_checks'
         and editorial.get('manuscript_succession', {}).get('review_status') == 'accepted',
         'publication review status changed; refresh the reading surface')
    refs = [r for r in editorial.get('documents', []) if r.get('path') == path]
    need(len(refs) == 1, 'missing or repeated publication document binding')
    ref = refs[0]
    return _bound_file(root, path, ref['sha256']).read_bytes(), ref
