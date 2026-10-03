"""Pinned G3 decision and narrow first-leaf entry; not specialization conformance."""
import phase9_implementation_policy as p

RECORD = p.PHASE + 'tranche-7/P9-7.8-G3Acceptance.json'
DIGEST = '5175491685e067a8653f561d497c88f587f90ba2c27926f64d598ce502a57c16'
CHECKPOINT = 'c6925b5f15612204e99bb5140ba9129dd13f12dc'
ENTRY = 'P9-8.1a'
PATHS = ('src/pygrc/models/grc_9_v4_topology.py', 'tests/models/test_grc_9_v4_topology.py')


def accepted(root):
    from profile_g2_registry import checked
    v = p.read(p.safe_path(root, RECORD))
    p.require(v['record_digest'] == p.digest_record(v) == DIGEST
              and v['reviewed_commit'] == CHECKPOINT, 'G3 acceptance identity drift')
    p.git(root, 'merge-base', '--is-ancestor', CHECKPOINT, 'HEAD')
    for ref in (v['review'], v['review_text']):
        data = p.safe_path(root, ref['path']).read_bytes()
        p.require(data == p.git(root, 'show', CHECKPOINT + ':' + ref['path'])
                  and p.sha(data) == ref['sha256'], 'accepted G3 review changed')
    review = p.read(p.safe_path(root, v['review']['path']))
    support = checked(root)['accepted_generic_runtime_support']
    p.require(review['record_digest'] == p.digest_record(review) == v['review']['record_digest']
              and v['accepted_generic_runtime_support'] == review['proposed_consumed_support'] == support
              and v['admitted_specialization_support_sets'] == [support]
              and v['G3_accepted'] is True and v['tranche_7_closed'] is True
              and v['new_runtime_iterations_authorized'] == [ENTRY]
              and v['runtime_paths'] == list(PATHS)
              and v['specialization_runtime_conformance'] is False
              and v['a_expansion_work'] == review['a_expansion_work'], 'G3 accepted scope mismatch')
    return v


def permitted(path, leaf):
    """Call only after accepted(root); neither a label nor a file grants G3."""
    return leaf == ENTRY and path in PATHS


ROW_ENTRY = 'P9-8.1b'
ROW_PREDECESSOR = '75a662916501c59d3d7ff06cee942258ed6d8c4b'
ROW_PREDECESSOR_HASHES = (
    'c085dc3b4a746bf3f0720cb68722fcfa150c4b9a0805392467605b8b597299b9',
    'f9983f0a5de9709a7f25219b51efe3e2c7d72d395aa4b0493562ede3c0d9e11a',
)


def row_bridge_authorization(root):
    """2026-10-02 user request: execute all of .b after committed .a review.

    This is a scoped execution successor, not an amendment to the historical
    G3 decision, acceptance of .b, or permission for another native leaf.
    """
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', ROW_PREDECESSOR, 'HEAD')
    for path, expected in zip(PATHS, ROW_PREDECESSOR_HASHES, strict=True):
        p.require(p.sha(p.git(root, 'show', ROW_PREDECESSOR + ':' + path)) == expected,
                  'row bridge requires the committed chart/graph review subject')
    return ROW_ENTRY


def row_bridge_permitted(path, leaf):
    """Call only after row_bridge_authorization(root)."""
    return leaf == ROW_ENTRY and path in PATHS


TRIGGER_ENTRY = 'P9-8.1c'
TRIGGER_PATHS = ('src/pygrc/models/grc_9_v4_lifecycle.py',
                 'tests/models/test_grc_9_v4_lifecycle.py')
TRIGGER_PREDECESSOR = '7f33a42f8850dbae57b63c8ad09d85bececbaf6e'
TRIGGER_PREDECESSOR_HASHES = (
    '1c3136583ba0148ff708ed980597bf47f3ca5c270f0e6e82fd767a66f2865807',
    '00bd5b342011effc413e8a8a0dea3273ad552e84de1863d19a8fc175d411568e',
)


def trigger_authorization(root):
    """User-requested .c after accepted .b; candidate detection only."""
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', TRIGGER_PREDECESSOR, 'HEAD')
    for path, expected in zip(PATHS, TRIGGER_PREDECESSOR_HASHES, strict=True):
        p.require(p.sha(p.git(root, 'show', TRIGGER_PREDECESSOR + ':' + path)) == expected,
                  'candidate detection requires the accepted row bridge subject')
    return TRIGGER_ENTRY


def trigger_permitted(path, leaf):
    """Call only after trigger_authorization(root); no later lifecycle entry."""
    return leaf == TRIGGER_ENTRY and path in TRIGGER_PATHS


COARSE_ENTRY = 'P9-8.1d'
COARSE_PREDECESSOR = 'e9dfad748b16d9c67b6368f8e3689137944f8f47'
COARSE_PREDECESSOR_HASHES = (
    *TRIGGER_PREDECESSOR_HASHES,
    'a65ea279b644f8592cd763d16e55e931661f7e8100c0e34002a345669589c5c3',
    'f6a991a8e742361df3a02e0a24d7a9827f484c9d97e56c6697bb6ad042c00b7e',
)


def coarse_authorization(root):
    """User-requested .d after accepted .c; column field algebra only."""
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', COARSE_PREDECESSOR, 'HEAD')
    for path, expected in zip((*PATHS, *TRIGGER_PATHS), COARSE_PREDECESSOR_HASHES, strict=True):
        p.require(p.sha(p.git(root, 'show', COARSE_PREDECESSOR + ':' + path)) == expected,
                  'column coarse/Split requires the accepted shared mechanics subject')
    return COARSE_ENTRY


def coarse_permitted(path, leaf):
    """Call only after coarse_authorization(root); reviewed topology owner."""
    return leaf == COARSE_ENTRY and path in PATHS


BACKEND_ENTRY = 'P9-8.1e'
BACKEND_PATHS = (*PATHS, *TRIGGER_PATHS, 'tests/models/test_grc_v4_exact_backend.py')
BACKEND_PREDECESSOR = 'a2d3d36ead9186147fb3434a3300084ce04f7e75'
BACKEND_PREDECESSOR_HASHES = (
    'f73fd466d2ecbf76d62206f779fde6a22634099641e638c592c19810495e5ed5',
    'eeed7dc3c02781a6838b43cdee7e202bf32f21f2b6d01677075021f2b7ea1897',
    'a65ea279b644f8592cd763d16e55e931661f7e8100c0e34002a345669589c5c3',
    'f6a991a8e742361df3a02e0a24d7a9827f484c9d97e56c6697bb6ad042c00b7e',
    '6d253a068fcd37d9eefa44fac77ce34ffd63534c2230a5f39c7d66a767b47457',
)


def backend_authorization(root):
    """User-requested shared exact-backend correction after accepted .d."""
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', BACKEND_PREDECESSOR, 'HEAD')
    for path, expected in zip(BACKEND_PATHS, BACKEND_PREDECESSOR_HASHES, strict=True):
        p.require(p.sha(p.git(root, 'show', BACKEND_PREDECESSOR + ':' + path)) == expected,
                  'backend correction requires the accepted coarse/Split subject')
    return BACKEND_ENTRY


def backend_permitted(path, leaf):
    """Call only after backend_authorization(root); no generic numerical rewrite."""
    return leaf == BACKEND_ENTRY and path in BACKEND_PATHS


ALLOCATOR_ENTRY = 'P9-8.2'
ALLOCATOR_PATHS = ('src/pygrc/models/grc_9_v4_expansion.py',
                   'tests/models/test_grc_9_v4_expansion.py')
ALLOCATOR_PREDECESSOR = '184919b352d96605037fd25cda2e9d38ef66b0f1'
ALLOCATOR_PREDECESSOR_HASHES = {
    'implementation/Phase-9-GRCV4-Handoff.md': '6dac16efecccb57686cd2d9d5727c299c21d7b48082b0a7462ca1f384e006337',
    PATHS[0]: 'f566cfd6c1cd42301d86b825da46ead8ba1d9142fc1d7e357b7d241577656f28',
    PATHS[1]: '4aa9ba5677eb5328a62dee478fdb1ee55ec98a0635d7d99d5a832c5355212c4b',
    TRIGGER_PATHS[0]: 'a79de2f92f85e591980acfb2bcf529d4b8d124a40401e37848333d036fa03527',
    TRIGGER_PATHS[1]: 'f6a991a8e742361df3a02e0a24d7a9827f484c9d97e56c6697bb6ad042c00b7e',
    BACKEND_PATHS[-1]: '0a936127aa5994491ce2cb0c77c51cba303e1d645237011419d08988db28accc',
}


def allocator_authorization(root):
    """2026-10-03 user request: pure allocator after merged parent acceptance."""
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', ALLOCATOR_PREDECESSOR, 'HEAD')
    for path, expected in ALLOCATOR_PREDECESSOR_HASHES.items():
        p.require(p.sha(p.git(root, 'show', ALLOCATOR_PREDECESSOR + ':' + path)) == expected,
                  'allocator requires the accepted shared mechanics parent')
    return ALLOCATOR_ENTRY


def allocator_permitted(path, leaf):
    """Call only after allocator_authorization(root); no lifecycle mutation."""
    return leaf == ALLOCATOR_ENTRY and path in ALLOCATOR_PATHS


COS_ENTRY = 'P9-8.3C-OS'
COS_PATHS = (
    'src/pygrc/models/grc_v4_geometry.py',
    'tests/models/test_grc_v4_geometry.py',
    'src/pygrc/models/grc_9_v4_expansion.py',
    'tests/models/test_grc_9_v4_expansion.py',
    'src/pygrc/models/grc_9_v4_lifecycle.py',
    'tests/models/test_grc_9_v4_lifecycle.py',
)
COS_PREDECESSOR = '79e0e8fca830ea9441e0b9bc7fb98d896f4d0c2c'
COS_PREDECESSOR_HASHES = {
    'implementation/Phase-9-GRCV4-Handoff.md': '808fe2e819dbed2502694de9f520f2030b789411127a742b952ae8f54551dcef',
    'src/pygrc/models/grc_v4_geometry.py': '38964b047669fad08c509ec4f657c6048072e0eae26a8470211564453a387eb0',
    'tests/models/test_grc_v4_geometry.py': '4167e6839e8a555ba278337d9ccefce543661df020adb5ab915d82266b2a492a',
    'src/pygrc/models/grc_9_v4_expansion.py': 'c9edb7b584401b761538d7ad48b257697eabe1d92d16331c98903cf882f60ee3',
    'tests/models/test_grc_9_v4_expansion.py': '0e015347abe22457f0ffd3256ef0cbc60bcb7d13af4c809b39bd417e9064c86d',
    'src/pygrc/models/grc_9_v4_lifecycle.py': 'a79de2f92f85e591980acfb2bcf529d4b8d124a40401e37848333d036fa03527',
    'tests/models/test_grc_9_v4_lifecycle.py': 'f6a991a8e742361df3a02e0a24d7a9827f484c9d97e56c6697bb6ad042c00b7e',
}


def cos_authorization(root):
    """2026-10-03 user request: C_OS integration after accepted allocator merge."""
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', COS_PREDECESSOR, 'HEAD')
    for path, expected in COS_PREDECESSOR_HASHES.items():
        p.require(p.sha(p.git(root, 'show', COS_PREDECESSOR + ':' + path)) == expected,
                  'C_OS integration requires the accepted allocator and numerical subjects')
    return COS_ENTRY


def cos_permitted(path, leaf):
    """Call only after cos_authorization(root); exact C_OS implementation owners."""
    return leaf == COS_ENTRY and path in COS_PATHS


CPC_ENTRY = 'P9-8.3C-PC'
CPC_PATHS = (*ALLOCATOR_PATHS, *TRIGGER_PATHS)
CPC_PREDECESSOR = 'eeb82e983651303f767b8f70853208ce1ee9d82f'
CPC_PREDECESSOR_HASHES = {
    'implementation/Phase-9-GRCV4-Handoff.md': '62d9b9014ebe50a925db9fa31704d45ff27e9e68c96b9e7a03df8be4c6aed1a4',
    ALLOCATOR_PATHS[0]: 'e00ff377f3da9ce5e17be8722e091cd0787bd4a57f6ea9a2950a7e69aa84529b',
    ALLOCATOR_PATHS[1]: '68b3be6347d6dc8eb0c180f55e7cf0c2d49e08b1e9ba81e9fed360a05ab85574',
    TRIGGER_PATHS[0]: 'fd7400c61276ef6f61999a7da9740ca15ed319ea1531b0be6d30da5746fe011f',
    TRIGGER_PATHS[1]: '8573b3531157dabc0e580d1eea26f4a9374d902e765f18452b1caa12edffe6af',
}
CPC_G2 = 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f'


def cpc_authorization(root):
    """User-requested C_PC integration after accepted C_OS; no new G2 claim."""
    decision = accepted(root)
    p.require(CPC_G2 in decision['accepted_generic_runtime_support'],
              'C_PC integration requires its accepted G2 in the G3 consumed set')
    p.git(root, 'merge-base', '--is-ancestor', CPC_PREDECESSOR, 'HEAD')
    for path, expected in CPC_PREDECESSOR_HASHES.items():
        p.require(p.sha(p.git(root, 'show', CPC_PREDECESSOR + ':' + path)) == expected,
                  'C_PC integration requires the accepted C_OS predecessor')
    return CPC_ENTRY


def cpc_permitted(path, leaf):
    """Call only after cpc_authorization(root); carrier event integration only."""
    return leaf == CPC_ENTRY and path in CPC_PATHS


AOS_ENTRY = "P9-8.3A.2"
AOS_PATHS = (
    'src/pygrc/models/grc_9_v4_topology.py',
    'src/pygrc/models/grc_v4_candidate_a.py',
    'src/pygrc/models/grc_v4_realizations.py',
    'src/pygrc/models/grc_v4_step.py',
    'src/pygrc/models/grc_9_v4_expansion.py',
    'src/pygrc/models/grc_9_v4_lifecycle.py',
    'tests/models/test_grc_9_v4_aos.py',
)
AOS_NEW_PATHS = ("tests/models/test_grc_9_v4_aos.py",)
AOS_PREDECESSOR = '0c995f9443d6e659157b51eb324d2d0aac8b65b4'
AOS_PREDECESSOR_HASHES = {
    'implementation/Phase-9-GRCV4-Handoff.md': '87b729076d556065365f8e7ee9a8de9ffde5500b9758d6befdd5741689c4ec5b',
    'implementation/phase-9-grcv4/tranche-8/P9-8.3A.1-AOS-Oracle.json': 'ce7f4ae309d9256d93ce7d96f10073e4380f92b26a9af548df1269f98507a06e',
    'implementation/phase-9-grcv4/tranche-8/P9-8.3A.1-AOS-OracleReview.md': '33457f9ac29f59322aa4d1da4fdba4dac80a9abea8d7d9748281f8bd2002d128',
    'implementation/phase-9-grcv4/verification/verify_p983a_aos_oracle.py': 'a72c76123ccd280f472f5728840e9a19f7bc8316a9f7746cb6380cfe6061eb66',
    'implementation/phase-9-grcv4/verification/test_p983a_aos_oracle.py': 'f04cef6dd849e753f1cdd8c44df710bf135f313ca1a1f9d57c3142dd71b6e06f',
}
AOS_G2 = "grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4"


def aos_authorization(root):
    """Explicit user acceptance of A.1 and request for A.2, no new G2 claim."""
    decision = accepted(root)
    p.require(AOS_G2 in decision['accepted_generic_runtime_support'],
              'A_OS integration requires its exact accepted G2 in G3')
    p.git(root, 'merge-base', '--is-ancestor', AOS_PREDECESSOR, 'HEAD')
    for path, expected in AOS_PREDECESSOR_HASHES.items():
        p.require(p.sha(p.git(root, 'show', AOS_PREDECESSOR + ':' + path)) == expected,
                  'A_OS integration requires the accepted A.1 oracle checkpoint')
        if path != 'implementation/Phase-9-GRCV4-Handoff.md':
            p.require(p.sha(p.safe_path(root, path).read_bytes()) == expected,
                      'A.2 cannot replace accepted oracle expectations')
    return AOS_ENTRY


def aos_permitted(path, leaf):
    """Call after aos_authorization(root); exact fixed-row A_OS bridge owners."""
    return leaf == AOS_ENTRY and path in AOS_PATHS


CCI_ENTRY = 'P9-8.3C-CI'
CCI_PATHS = (
    'src/pygrc/models/grc_9_v4_expansion.py',
    'src/pygrc/models/grc_9_v4_lifecycle.py',
    'tests/models/test_grc_9_v4_cci.py',
)
CCI_NEW_PATHS = ('tests/models/test_grc_9_v4_cci.py',)
CCI_PREDECESSOR = 'ba5cf5c12efc30de7977853876bf801edcbca7d2'
CCI_PREDECESSOR_HASHES = {
    'implementation/Phase-9-GRCV4-Handoff.md': 'e2f4e7204e0afb2cc940452c6c48a85a7a9da894b760efcfc9dd615ebce54efe',
    'src/pygrc/models/grc_9_v4_expansion.py': '5cb2832b05bba367c74e2022630c4d3c06594576c3fa33095909c9c355382ec4',
    'src/pygrc/models/grc_9_v4_lifecycle.py': '59baa8b766f41524c9923e3361dec1f4d3c16423939572d8c4bd3dedaf4840de',
    'implementation/phase-9-grcv4/tranche-8/P9-8.0-CI-ConstructionInputs.json': 'fe0175aec8119ff85efe8685638eeece5b70d2efe705b0a3a475e3ca8bc55f24',
    'implementation/phase-9-grcv4/verification/test_p980_ci_event_companion.py': '0ddd5b79cc2492a1d6635158f81fce308872fa240a6630074676d18d1b983136',
    'implementation/phase-9-grcv4/verification/test_p980_realization_numerical.py': '8fd2e002526854866455f136026c19a0b0656b23d277130206f713ee5f6440f9',
}
CCI_RESEARCH_PATHS = (
    'implementation/phase-9-grcv4/tranche-8/P9-8.0-CI-ConstructionInputs.json',
    'implementation/phase-9-grcv4/verification/test_p980_ci_event_companion.py',
    'implementation/phase-9-grcv4/verification/test_p980_realization_numerical.py',
)
CCI_G2 = 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e'


def cci_authorization(root):
    """User-requested C_CI after accepted A.2; exact existing G2, no promotion."""
    decision = accepted(root)
    p.require(CCI_G2 in decision['accepted_generic_runtime_support'],
              'C_CI requires its exact accepted G2 in G3')
    p.git(root, 'merge-base', '--is-ancestor', CCI_PREDECESSOR, 'HEAD')
    for path, expected in CCI_PREDECESSOR_HASHES.items():
        p.require(p.sha(p.git(root, 'show', CCI_PREDECESSOR + ':' + path)) == expected,
                  'C_CI requires its accepted predecessor and research subjects')
        if path in CCI_RESEARCH_PATHS:
            p.require(p.sha(p.safe_path(root, path).read_bytes()) == expected,
                      'C_CI cannot replace accepted research expectations')
    return CCI_ENTRY


def cci_permitted(path, leaf):
    """Call after cci_authorization(root); event integration owners only."""
    return leaf == CCI_ENTRY and path in CCI_PATHS
