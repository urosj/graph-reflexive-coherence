"""Finite historical G2 epochs; reject drift without running old kernels."""
from pathlib import Path
import unittest
from unittest.mock import patch

import p9_aos_g2_sources as s
import tranche8_source_reuse as bridge


class G2EpochTests(unittest.TestCase):
    def test_all_named_sources_use_exact_committed_epochs(self):
        changes=bridge.record()['changes'];root=bridge.p.ROOT
        self.assertEqual(s.ROSTER_BASE,bridge.record()['base_commit'])
        current={name:s.sha((root/name).read_bytes()) for name in s.EPOCHS.keys() | s.ADDITIONS | s.VALIDATED_ADDITIONS}
        expected={name:s.original(root,revision,name) for name,revision in s.EPOCHS.items()}
        self.assertEqual(s.project(root,current,changes),expected)
        self.assertEqual(s.project(root,expected,changes),expected)
        historical=bridge.retained_bindings(current)
        self.assertEqual(historical,{name:changes[name]['before_sha256'] if name in changes else expected[name]
                                     for name in current if name not in bridge.record()['additions'] and name not in s.ADDITIONS | s.VALIDATED_ADDITIONS})

    def test_live_drift_and_unrelated_binding_reject(self):
        changes=bridge.record()['changes'];root=bridge.p.ROOT
        name='src/pygrc/models/grc_v4_candidate_c.py';target=root/name
        current={name:s.sha(target.read_bytes())};read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'# drift\n' if path==target else read(path)):
            with self.assertRaises(ValueError):s.project(root,current,changes)
        with self.assertRaises(ValueError):s.project(root,{name:'0'*64},changes)
        with self.assertRaises(ValueError):s.project(root,{next(iter(s.ADDITIONS)):'0'*64},changes)
        with self.assertRaises(ValueError):s.project(root,{next(iter(s.VALIDATED_ADDITIONS)):'0'*64},changes)
        self.assertEqual(s.project(root,{'unregistered.py':'0'*64},changes),{'unregistered.py':'0'*64})

    def test_existing_g2_matcher_consumes_bridge_and_keeps_scope(self):
        from g2_source_reuse import matches
        root=bridge.p.ROOT;changes=bridge.record()['changes']
        name='src/pygrc/models/grc_v4_candidate_c.py'
        expected={name:changes[name]['before_sha256']}
        current={name:s.sha((root/name).read_bytes())}
        self.assertTrue(matches(expected,current))
        with self.assertRaises(ValueError):matches({'unknown.py':'old'},{'unknown.py':'new'})
        self.assertEqual(set(s.EPOCHS),{
            *('src/pygrc/models/'+n+'.py' for n in ('grc_v4','grc_v4_candidate_c','grc_v4_ci',
                'grc_v4_geometry','grc_v4_lifecycle','grc_v4_realizations',
                '_grc_v4_matrix','grc_9_v4_lifecycle','grc_v4_exact','grc_v4_linear','grc_v4_numerics')),
            'specs/README.md',
            'src/pygrc/models/__init__.py',
            s.INITIALIZER_READER,
            'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/tranche8.py',
            'implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md',
            'implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md'})
        self.assertEqual(len(s.ADDITIONS),15)
        self.assertEqual(len(s.VALIDATED_ADDITIONS),24)

    def test_initializer_package_keeps_accepted_bytes_and_inputs(self):
        root=bridge.p.ROOT;value=s.initializer_package(root)
        from verify_p972a_initializer_runtime import package
        import json
        self.assertEqual(package(),json.loads(value['specs/grc-v4-a-initializer-release.json'])['release_id'])
        target=root/'src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-schema.json'
        read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda path:read(path)+b' ' if path==target else read(path)):
            with self.assertRaises(ValueError):s.initializer_package(root)

    def test_tranche8_index_keeps_exact_sources_and_rejects_document_drift(self):
        import json
        import tranche8_evidence as index
        root=bridge.p.ROOT
        asset=(root/index.ASSET).read_text()
        value=json.loads(asset.split(' = ',1)[1].rstrip().removesuffix(';'))
        sources=index.Sources(root)
        for ref in value['source_refs']:
            sources.raw(ref['path'],historical=ref['basis']=='historical_git')
            self.assertEqual(sources.refs[ref['path']],ref)
        name='implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md'
        target=root/name;read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda path:read(path)+b'# drift\n' if path==target else read(path)):
            with self.assertRaisesRegex(ValueError,'Tranche 8 retained source drift'):
                index.Sources(root).raw(name)

    def test_boundary_and_mechanics_keep_original_records(self):
        import json
        from copy import deepcopy
        import tranche8_evidence as index
        import prepare_p984c_boundaries as boundary
        import test_p984c_mechanics as mechanics
        root=bridge.p.ROOT
        contract=json.loads((root/boundary.OUTPUT).read_bytes())
        retained=json.loads((root/mechanics.RESULT).read_bytes())
        originals=deepcopy((contract,retained))
        paper='implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md'
        paper_binding=next(r for r in contract['source_bindings'] if r['path']==paper)
        import p984b_runtime as runtime
        with index.historical_index_session(root=root):
            runtime.check_bindings([paper_binding])
            index.check_boundary_storage_successor(boundary,contract,root)
            index.check_mechanics_storage_successor(mechanics,retained)
            altered=deepcopy(contract)
            altered['disposition']='unrelated declaration'
            with self.assertRaisesRegex(ValueError,'boundary contract differs'):
                index.check_boundary_storage_successor(boundary,boundary.seal(altered),root)
        with self.assertRaises(ValueError):
            runtime.check_bindings([paper_binding])
        self.assertEqual((contract,retained),originals)

    def test_committed_projection_avoids_rebuild_but_rechecks_live_sources(self):
        import json
        import tranche8_evidence as index
        root=bridge.p.ROOT
        with patch.object(index,'build',side_effect=AssertionError('unrequested rebuild')):
            value=index.checked(root)
        self.assertFalse(value['verification']['current_runtime_conformance_inferred'])
        raw=(root/index.ASSET).read_text()
        forged=json.loads(raw.split(' = ',1)[1].rstrip().removesuffix(';'))
        forged['verification']['current_runtime_conformance_inferred']=True
        forged['view_digest']=index.digest({k:v for k,v in forged.items() if k!='view_digest'})
        read_text=Path.read_text
        with patch.object(Path,'read_text',lambda path,*a,**k:index.browser_source(forged) if path==root/index.ASSET else read_text(path,*a,**k)):
            with self.assertRaisesRegex(ValueError,'browser evidence drift'):index.checked(root)
        target=root/index.BASE/'P9-8.4a-Coverage.json'
        read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda path:read(path)+b' ' if path==target else read(path)):
            with self.assertRaisesRegex(ValueError,'source drift'):index.checked(root)

    def test_final_review_readers_resolve_only_exact_metadata_epochs(self):
        from p994b_runtime_successor import SOURCES
        from p984i_first_group import authenticate
        root=bridge.p.ROOT
        for name in s.METADATA_SUCCESSORS:
            expected=s.original(root,s.CURRENT,name)
            self.assertEqual(s.sha(authenticate(root,dict(path=name,sha256=expected))),expected)
            if name in SOURCES:
                for old in SOURCES[name]['predecessors']:
                    self.assertEqual(s.sha(authenticate(root,dict(path=name,sha256=old))),old)
            self.assertIsNone(s.metadata_source(root,name,'0'*64))
            read=Path.read_bytes;target=root/name
            with patch.object(Path,'read_bytes',lambda path:read(path)+b' ' if path==target else read(path)):
                self.assertIsNone(s.metadata_source(root,name,expected))
        self.assertIsNone(s.metadata_source(root,'unregistered.py','0'*64))


if __name__=='__main__':unittest.main()
