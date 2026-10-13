"""Read-only Tranche 8 evidence index; never implementation permission or a rerun.

The committed checkpoint pins existing acceptance, not a new acceptance ledger.
Historical mutable handoffs are read from Git; immutable retained evidence must
still match on disk. Missing ignored copies may be restored from lossless archives.
Numerical checkers are exposed only by explicit CLI action.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from copy import deepcopy

from tranche8_validation import ACTIVE, validation_session

LARGER_COS_BOUNDS_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSBoundsInputs.json": "82f32adb6b551aa5a955f631010f9a6937ff757a528a0f4d6b46db8f920a9dda",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSBoundsResults.json": "45ca2fa88ad865612af6a546a2226dec4058c5f8d68b65a7bf51be9cff36f95d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSBoundsPlan.md": "cac8de1f42cdca7c25f4564df825719c0220670aec590c5f2e580e52c29e278f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSBoundsReview.md": "279e986f9631dbf33e6992073da60616a9ed69bf658b84d5353ddfb1d29993f0"
}

LARGER_COS_SOURCES = {
    'implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSInputs.json': '6704e0b7e88dd1882bdaf9c33efa3ae41bb50243dd63dc9d8b2bcb23f7b667ee',
    'implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSResults.json': '371c3c24b2d03ec3d1093e58c7dbac71692d1dffe947756c5a9aa3b9d284b020',
    'implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSPlan.md': '59e97792c3f9258f8009bd33060f25b5ae069e554c5319e892f7eb35ee578899',
    'implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSReview.md': '8846a32f33864afbe718bf293d3323db923fe86c1cd52af80c39250d7103ac1a',
}

CHART_APC_SOURCES = {
    'implementation/phase-9-grcv4/tranche-8/P9-8.4f-APCInputs.json': 'b4d581c9b6bc060d568f9602cc7baa9b4d6654107a503ef18d9e4ed3aa156a72',
    'implementation/phase-9-grcv4/tranche-8/P9-8.4f-APCResults.json': 'e10656da11f663cbf82c6634281c6ebe8a720b57be727e8a4caefd7ce6736083',
    'implementation/phase-9-grcv4/tranche-8/P9-8.4f-APCPlan.md': '7a6f66f79682c895f3a4dd3147f72a4522b765999d2d1b8bd4cf155e1503f0c2',
    'implementation/phase-9-grcv4/tranche-8/P9-8.4f-APCReview.md': 'e75b95cd259551d432e271da3dc84477dab5b60cb2578b7625b872c1914a08fb',
}

CHART_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-ACIInputs.json": "1296e5960804eddf32e0e3c1e2c3048371c2c681f18bdcd57b77fee41f676c85",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-ACIResults.json": "63a9bea44ec97ff48640e11036f17700f2b92589604eab63fe78620b157b1e9a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-ACIPlan.md": "90ad2433ed41ad8542f7f74383eb5bfc0be89e15b1a2bce09a9696fb67ba4e2d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-ACIReview.md": "9a3139bbbf5a0e915e944aef9348aeae6968c19afb8f22623fbb4495e8363847"
}

CHART_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-CCIInputs.json": "dbc19d1486606bb3436d3ca6378907ac91ead58c28e4b4c1c558002e3bad6109",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-CCIResults.json": "5e5afa130d2269be45711797f918d90d9d11517d6179db3b1b63c833b8a8fd31",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-CCIPlan.md": "4f3b3f43340f1d5ee0871ca35fb23930f5bff6c4256876bc9bc6ca56e0a38381",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-CCIReview.md": "e2a9130a81c32f3fe8631c311009d92431cff067fda1003b22b1e7a5b532fbde"
}

CHART_COS_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-COSInputs.json": "ba4f4d3fb036cab5715c54aa4bd08cc00385f50a039a9449eb52847f98838501",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-COSResults.json": "020d614b2f1c6e69b789642be0e865887956a39a378dac084e20d0a1628dd747",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-COSPlan.md": "c7bf3db64b0891fd037794c4b61998584fa380c2019a2910076421effa606771",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4f-COSReview.md": "72111ec5034de16b7d609c72acb6751327e42bac17b26b30b198f0c28205bf34"
}

COVARIANCE_APC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-APCInputs.json": "d7af41e43c3812879c1c76ead68958c26bdf4b39bb6bf78ac1e7fb869d185a3a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-APCResults.json": "983054f5298b83b586b07adc9b527392aa1f90bedaca0c24360cf76b3c367ad9",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-APCPlan.md": "937562002e20260866e10a22fa3ff2638da46b2ac2828eb22571cfdf17478f25",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-APCReview.md": "63b146c2e4aa286e86c0c62a238ec43176a7ff27b8dc5a7b6dc85af7b6b99f3a"
}

COVARIANCE_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-ACIInputs.json": "e266ff8ce7e5dadf60354c47f7dd008188acd6108954132af72851794c335e63",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-ACIResults.json": "70cbc37ee27773ff6545022b5f72f328c663a02868347a2b36fca48332f19292",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-ACIPlan.md": "21f39b20eaaf686361a63f3f4f819a7a8cdfdad9e50d8dcb71cd885b8792a69f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-ACIReview.md": "cdc4ed50e2e5681dff43d66d6adcc5417816bc1297cf328c6b1bba14e325d538",
}

COVARIANCE_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-CCIInputs.json": "093d2ac796cc7b22baf9690b8f3e3422194d575ee7a3eff5eb17b5f5a2154b97",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-CCIResults.json": "ceabcf333bae5dd985deef4fef043fa36a02d1ac54137aff5cca73fc26c52402",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-CCIPlan.md": "5591fcd48a75b724dc91a93dbd6dba40d587327959f9f296554fd6d010232d3d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-CCIReview.md": "c8c5d6b1e975048c4223306c89c5636440ed62266f6657528f37c71d8260b519",
}

COVARIANCE_COS_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-COSInputs.json": "b04c6d3e50540c172f5b35aa869ea801f55f2cf3be367130aff92a6b2006bb2d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-COSResults.json": "5e1642e44b1b93847131c2dd2b564e0641e243bee1f0d6afc313270fa4b21fb8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-COSPlan.md": "380f0e4da8eb65e94fe8dda4dd77004be42c1c13b7327b4e5e916c282366cee0",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4e-COSReview.md": "583b17dcf86d1e2e0d5671016fb8ba1331ce133164ab15b858d0272d5901b30f"
}

ROOT = Path(__file__).resolve().parents[3]
PHASE = "implementation/phase-9-grcv4/"
BASE = PHASE + "tranche-8/"
HERE = PHASE + "verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/"
ASSET = SIDE + "tool/phase9-web/tranche8-evidence.js"
CHECKPOINT = "dbfcd311b8ee67ad9a5d8ea0f38670d88b8d57b1"
DEEP_APC_FULL_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCFullInputs.json": "2044970cc9659caf3b2f52027e8f0e03fa61b7ed98c2fa248e1bca7a139bb6cc",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCFullPlan.md": "b56d1caeab85a0371c774dc5e5b44d7843a78b1416c5fd0ceab677fb56119dd2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCFullResults.json": "ac5749112b6585c26b454ed7f84146f26550a38db52c8b4ab57208ea941dd5ca",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCFullReview.md": "bf10d06cb5ac223269267037c0423d8315a552231ed594cac4098bc2c8010dd6"
}
DEEP_APC_JOINT_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointConstraints.json": "72db98f577f4e49e1e7ba8f6a44e6bcf4e12bee9f8c5d9a4b239ec2afb87f08e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointFeasibility.md": "50e1cbce93a65612d4209a505391d36b07a160276712bf6634b495405f19d493",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointSuccessorInputs.json": "b92a98dc182b9029093b8adf8ea8d77309c705ef6c3c0e911170be5bdd4a9162",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointSuccessorPlan.md": "5bac0d2334ef4e23f82f2fd78187b998f7f61f347fa7b62f73756a695251d6ac",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointSuccessorResults.json": "c3416a413782e812c3b96d48aae93137d9f927d5aafd8e5c620d4c3763ea807c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointWitnessInputs.json": "0b9355ea7d8dcbda94a2a80e708d18894c954f00f86d950f2f4ffd369f3e337d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointWitnessResults.json": "35d6a21c09b206ccf2a5feadd9a991c77dfce9b6dde5dd02e92ef6f0e266427c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCJointWitnessReview.md": "80d91acefca99be2511ffdd2090d6a5d5e413f19b065c382b60068a1ee651d10"
}
DEEP_APC_HISTORY_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCHistoryCompanionInputs.json": "4e0dbdd36444007abdf371fd86560f056e122d319eac5844230d91656fff3754",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCHistoryCompanionPlan.md": "c5e7edfe4eb194caec2932601ebba6754b47df254578646fd12ef304f1442aaf",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCHistoryCompanionPressure.json": "280e7ba8860fa5ba17010701623eed14f26896f27a0d14ce2e7a3dfa643c0dff",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCHistoryCompanionResults.json": "1878085da9623d3e7dab0ef030b51cc73056411e1f58e0f0b8a0a6772316492e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCHistoryCompanionReview.md": "2beb5cd96b11d37d8bbb2f86b58423217b56ece6e9ee71fbbbf03d68a11a761c"
}
DEEP_APC_COMPANION_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCAllocationAcceptance.json": "be371116faef9605e248ebb4c201e7da4fbfefff4c4f88458e62b2bfe65fb990",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCSourceCompanionInputs.json": "da5eba81d29b5aa4798090fcd7e8f59d6522c149a596399296b931346bf6c844",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCSourceCompanionNativeInputs.json": "e28fef81dbb8b959da01ef16322ca9631cc34ee849b342dbe3c19cc3c3bbcb01",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCSourceCompanionNativeResults.json": "de183797241e5826995300f3ee46754c50535df913be5011e4633aa12a94477e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCSourceCompanionPlan.md": "269adc706aebc9fa85f83fef8b7d7e385d3f28f739773eae377818f18971e644",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCSourceCompanionResults.json": "e780807d129fd78647c2b81f0a6dbe6634e332a102fb3f1ef8e323651f83f1a1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCSourceCompanionReview.md": "046e716cbb5aaa9b29c139a225bc0ffe35e08df35c59c95c4ac0bbff108658f0"
}
DEEP_APC_FEASIBILITY_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCAllocationFeasibility.json": "837dcc9f42c679edbb6ccc78c5fc894d3df7c1c5d733f2962dcc127ccd571fca",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCAllocationFeasibility.md": "64ac782f43da980cd5821e1dbf643f4ab9c4e3da6749c97f48fdd09a9d63a6ac"
}
DEEP_APC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCCases.json": "e4cb7e08fbdc4613ca4f0f6b936808804bc4d71b6bc3859074368bb31507fb96",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCResults.json": "2b18893b2f31dbfde9e14ed1cc51a13cf04255b0b1fa9507737a94057663f57b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCPreflightPressure.json": "df0b249f1fcb0b5e38d955ab5f623809ed37d8cf8da1d273b1601c6529ab68fa",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-APCRuntimeReview.md": "564cece4af11bd880fe47a444fa35176c325589c3f3d6fa5c42db226341892f6"
}
DEEP_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-ACICases.json": "00414b326bc9221d38e5e8efc6e138e73b7db23b365fc0f6a4e6256d5044c59c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-ACIResults.json": "691fcf4eb5d30405353594d97a0c7e9c81f35540c105f59e862f66f90d67a0a7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-ACIRuntimeReview.md": "25443d5138d121b94e0cc9b37ddc7870929726d55e38d3dffb0dccf5cdbe5d74"
}
DEEP_ACI_ORACLE_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-ACIOracleInputs.json": "bfe65e401dad40b9e3e6488a706ac8130fafef0ecab0aff32572ab4bf5c2f399",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-ACIOracleResults.json": "5ee490e6e603295235524fc31327ba94b78722bade72be852776d865de4a4bb6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-ACIOracleReview.md": "17bd90f66ccea96e26c0c2d0207f25fa66c6720a56d322b3999d7b178c9022c2"
}
DEEP_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-CCICases.json": "714becd26009a5794e3d610c76959f56402aa0463127ac21281bfdc4e11598fe",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-CCIHardeningCases.json": "e0ac0e8adae13015ef5ccbddc2ea03d3f6a30ae064c6f6f8e15d8caf26e8a0cf",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-CCIHardeningResults.json": "a0b9437a93578491de8e53e3505ef669c87db6f170915960e44f3bed1500688f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-CCIResults.json": "cc39be3684c262ea3ce6210221663ed5ecc5caefc46b1c53449217c0a96e082b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-CCIReview.md": "ef124afe356d847acaddea2254d9e250fa33bca448f76478a5588e19c96c638e"
}
DEEP_COS_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-COSHardeningCases.json": "cdad7743261c594a2e48276ab717cf82acea2d934ac49bd5f73c54fadaceb37e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-COSHardeningResults.json": "e05a9a2697906d827a90d92a7d4831faa5e8c803a8fc3da34c2a39a901cda467",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-COSHardeningReview.md": "84408902b486d2c491e397e60902b1b4a0bb35569e2a716aee766662ccfe28bb",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-COSCases.json": "f2f62f2c5c741a0997f49e0286f1f23b05a796b1f28e9f2cf93ace08649eac50",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-COSResults.json": "8baefd52c9c41847905e49f7299aa57fb42b0f881d9b108817538836a0d60ce1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4d-COSReview.md": "956ad81e2dbb49215d8fd27d198b3571459edc0728692dd1586099120761e128",
}
BOUNDARY_CLOSEOUT_SOURCES = {'implementation/phase-9-grcv4/tranche-8/P9-8.4c-Closeout.json': '052d1a81bfdd3ebe1b763fa87da26805df53a84624e6ffee27fdb30204a4d440', 'implementation/phase-9-grcv4/tranche-8/P9-8.4c-CloseoutReview.md': '206643c340ef1e4303973da67685fa373707b68b2336e39a1d16f01732627ab0'}
# Preregistration pins confer neither numerical evidence nor acceptance.
BOUNDARY_CONTRACT_SOURCES = {
    BASE + "P9-8.4c-BoundaryContract.json": "c7a142d0691cce9a3e7807bc58c1f6d10481772e26103a7210b81a1f69bcf8d9",
    BASE + "P9-8.4c-BoundaryReview.md": "d13fa1298d0d10526bb89fd43499a346da480ec04da11df064e383c5f8750895",
}
BOUNDARY_MECHANICAL_SOURCES = {
    BASE + "P9-8.4c-MechanicalChecks.json": "bfca9935d05b5fb793406765e10e48a1652ec7e203ea40deb93590d0f6cc3c1a",
    BASE + "P9-8.4c-MechanicalReview.md": "df80ed367b159007fc8552f85e5f4fa0276e3e786305077718de6395a310d598",
}
# Boundary execution pins do not confer scoped user acceptance.
BOUNDARY_COS_SOURCES = {
    BASE + "P9-8.4c-COSCases.json": "78d0e3e10e47742114f30e129dc62dce3683cbd1dcde1bae9062c644b293a754",
    BASE + "P9-8.4c-COSResults.json": "5da7e5d80188774a8403e079265c55a27d109fd31ab0136c99dcaa5e7d78b329",
    BASE + "P9-8.4c-COSReview.md": "66ff1d9a0e829cc0fb2349e1bc7e182236cc0e0196db5496af61e4201f067af9"
}

# New A oracle scope remains separate from numerical runtime acceptance.
BOUNDARY_AOS_ORACLE_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSOracleInputs.json": "d6c4c325474d7de8f601fe7a098e90e6027b152826cb9aadda0c9177ee2ed049",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSOracleResults.json": "33b1c41fd3a5764d8317cf2233e19762222e98c5b38301cdd3c91b7a8121b500",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSOracleReview.md": "ac3b85a497a4828eb6c5dbf3ebe4683b833050790952d03b9022fef55c5c1ecf"
}
BOUNDARY_AOS_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSCases.json": "6c3c9e24351fcd7b42c65f0b8e54758a13291bcf94cd5d980921f0a12309879b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSResults.json": "ac2918f910ff07f7f57301d45ce5b043d206bb2436d650adddc93ebeb4832f4c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSRuntimeReview.md": "26849e5d563dcd9f68de0168fab9e1946d38f19f643c6e46aef8d8bdc46aeab9"
}
BOUNDARY_CCI_PREPARATION_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIPreparationInputs.json": "da8f99df3a1ef69317b72161e3e20f35130b62c80bc55a60dcbf0da78d625592",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIPreparationResults.json": "53afccc62c76594a80e5640e40c2abb8289db39ffd756250ca63f2551747d25e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIPreparationReview.md": "4a394abc0e8026a5a5ce739557b3ecc7d053ee0da00d36ca3ef98ec4db00992b"
}

BOUNDARY_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCICases.json": "ba21a1f7e47f4fc8ce79b1fe5ca03b78027195b219997df6853cdfa390e5985e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIResults.json": "f4edf55cee5bb408e29998b5c04416893df0b562653de57a76a9d58b6e350957",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIRuntimeReview.md": "3707b3f42692eb76f31ea86ee573de0b13078fb4f386cb8f1c9ddb829bdd1fa7"
}

BOUNDARY_ACI_ORACLE_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIOracleInputs.json": "6eae65792850f173b7463cf0bc5d96a801c08e8777bda5028d8fd8a413b8809f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIOracleResults.json": "52d43cda43359691f18cbeb1287489a730b6271c2982741a36a5d7f14b62d905",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIOracleReview.md": "ca4f78d414b5f751219b103a34bbbeb5fe716e5e936450d19ee7b3276ed1043c"
}

BOUNDARY_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACICases.json": "d68172e494d2882a678b473894f3823af80edb34c7fbe2deddabaef48f9eec47",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIResults.json": "add9d33980c2e548632da35f121735b8ba1453e27875c8cc59a3a1f2710fffb8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIRuntimeReview.md": "b83315cc8715b8ef8c6fd09bed32e3108abd50f48b4f1c86bbb1b54fea3512af"
}

# C_PC boundary execution and separate scoped acceptance have exact pins.
BOUNDARY_CPC_SOURCES = {
    BASE + "P9-8.4c-CPCCases.json": "efea21c39271508f9b85b5147659613662e11d614fbb2d3dbc571f16e2350616",
    BASE + "P9-8.4c-CPCResults.json": "d281d25dad72d00a3ae1ad4aa40e7489a48ea7065fe6091edcf5ca23505b8f85",
    BASE + "P9-8.4c-CPCRuntimeReview.md": "bdca0a46d77e33189bf7ad1d9f557cea3097cbeee1cd1dc736a77e8bfd6dcbca",
}

# A_PC boundary execution and separate scoped acceptance have exact pins.
BOUNDARY_APC_SOURCES = {
    BASE + "P9-8.4c-APCCases.json": "cf12a1d35d0a8489eb16345f414dc3ef445dfbfcf013828c0c73f18a02eb301c",
    BASE + "P9-8.4c-APCResults.json": "6eb4ded39b423ac35b8ee276eaa2a399b566b2716ce9810ec93f37cc3cd74038",
    BASE + "P9-8.4c-APCRuntimeReview.md": "cefe1d6e94b81c6797e8f5828ff9e6d78c2daa1f1c347a52ecaf5efebabd8c15",
}

# C_CI+PC boundary execution is separate from scoped user acceptance.
BOUNDARY_CCIPC_SOURCES = {
    BASE + "P9-8.4c-CCIPCCases.json": "7641e8bd06a3e617c72a2892f4a9a1eba1c0eda3ba96fd02a1fa2775e13beb74",
    BASE + "P9-8.4c-CCIPCResults.json": "a1963f2b54f66ca49b6ede03add0fe3fda41ad6a1b1b6065cd1437b3fbf8252a",
    BASE + "P9-8.4c-CCIPCRuntimeReview.md": "8e57b3f67cba32062e538d126cc353072d0adf9789f96b7e63bea0182cb2fa4a",
}

# A_RG2b execution and separate scoped acceptance have exact source pins.
BOUNDARY_ARG2B_SOURCES = {
    BASE + "P9-8.4c-ARG2bCases.json": "054fc9a297d4c573dfa84bb0a452c08952a73a9710bebdb245995ce519355aeb",
    BASE + "P9-8.4c-ARG2bResults.json": "cd2ad8d3a5e17fc12f525c54801540864cddf5f6b6110112068282570871dead",
    BASE + "P9-8.4c-ARG2bRuntimeReview.md": "39a7c4f815c1d3fbe44a41b06310983fbb9c1e1185bc74741b30da0daefe20eb",
}

# C_RG2b execution and separate scoped acceptance have exact source pins.
BOUNDARY_CRG2B_SOURCES = {
    BASE + "P9-8.4c-CRG2bCases.json": "23f26abf7ec82008ee5b554dc43a08a994c2be8315965569d81fe670fbf718f9",
    BASE + "P9-8.4c-CRG2bResults.json": "180aee7f94b0a90d8502eaaf1c473e70f5a39637171dc07dd1478dc10cef37af",
    BASE + "P9-8.4c-CRG2bRuntimeReview.md": "fe1a582e1a9025cd7208afb00870d7d47f5970ec09535c532f9a7aeac93a16e7",
}

# A_CI+PC execution and separate scoped acceptance have exact source pins.
BOUNDARY_ACIPC_SOURCES = {
    BASE + "P9-8.4c-ACIPCCases.json": "60508ea1e13b7b924972a01c0ab743670c06380760fea6b2123c00a0aca04db2",
    BASE + "P9-8.4c-ACIPCResults.json": "24210e42fb52a25cf5c6c0e89bf377dbb0911ed9ace14018d1e5fe16348f4ef3",
    BASE + "P9-8.4c-ACIPCRuntimeReview.md": "5a65669e68aca9073f58d6d85103e955e39db0b4b79e39c54ba88818b6fd559d",
}

# A_RG2b execution and separate scoped user acceptance have exact source pins.
ACCEPTED_ARG2B_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bCases.json": "cecede14b568698ea5c2500e07123838ef2e344519e509d5f79abfb7e0f48a08",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bResults.json": "d23a612386ea7d1966b09f159d996b306d240b11cc1f8fb2cc692dce5572564b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bRuntimeReview.md": "9692b616a09a3c764cede9b109d3fbcb6fe849844c383dc97f84a9fe6e89f295",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bNumericalRecheck.json": "871a82f8040d989fbbc6587dc4bf656dae9d3ad136b5addb36b14b1ef7b22dfe"
}
# C_RG2b passing execution remains separate from user acceptance.
ACCEPTED_CRG2B_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bCases.json": "59b97d15e3e29b6dab6e23714c18137d7236a302283be56a78e34226c8bf5fe1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bResults.json": "b0ffbbdcac92732738401306c4d53365c370eaf393e0cbedc9f7369a46e9baea",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bRuntimeReview.md": "40beb6140f4b5581ab6156b5b68a5a4451e2229deead8800fa48b9e84daf86f7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bNumericalRecheck.json": "b823638b97a2cd2e59c2ce63a96b4f20d85b1d56bc6f4a7c6524d8aaa4061e06"
}
# A_CI_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_ACIPC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCCases.json": "a768952d08ec38f9c034f904ec73569de21fc0cb32d755633c8a1860007ade15",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCResults.json": "a1f5da445f6fbce1d17d98a872ab7558477083dea9b288af9a409c540c06f194",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCRuntimeReview.md": "210865b79e318b126f8385078954fae5e3e897abde74c973495f8ef3840f226e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCNumericalRecheck.json": "75cd7300811f5c869fb761afb407f73bba208f3e6492e38609f78549449150cb"
}
# C_CI_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_CCIPC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCCases.json": "0c489a674c35cad9c3f5a64f3fe970414fadf950a7c2aa378ef740f3b3a6978f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCResults.json": "6ae474557161f9d9e6d3c5d350b023f2742eeb1cafa8c24733c39beafe132db2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCRuntimeReview.md": "5d3cd84eb1a6c2b91ab9326818cdd7d372088d160bf87d25131683ab39919e3e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCNumericalRecheck.json": "99e1156bbec61a6a5f311c7912021f88fcb0d2af9f9171bb9781395c7753f52d"
}
# A_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_APC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-APCCases.json": "b0f2b8eb1718c23579f208573eec1e9e463c6b740beeaf68b925ec2728c91163",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-APCResults.json": "cd37259572c53dfec62f9fbf30fe0fb043add1d2d34c1d2f126dfa0deb06b4bc",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-APCRuntimeReview.md": "5e8f762b3a323980eac6255be62030793aa68502a3b5f6a7e1d83296a3238b56"
}
# C_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_CPC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCCases.json": "c23e2a9a2a9d653f433316a57e7b7d3c1c3de557d7d8d507f136d6310ad4271e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCResults.json": "9ca4dae9633e8d91154c8f5f1a9a4454f3dd5a3e83456edb5a27cf5664bc080a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCRuntimeReview.md": "4343ca0bc237f1627c2a8a7a724f04b4174b5bc69fc95c6aab3a3cfa1f0f1d27",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCScientificPressure.json": "59d0ed4fd9351e783e71e0a462ff0f8df669524871ecf4f1f0b88d9f4a7a4a2e"
}
# Exact C_CI execution/review pins. The review records the separate scoped
# user acceptance; raw execution retains its original unaccepted flags.
ACCEPTED_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCICases.json": "473bf8252a1b6e5b02816e261686f53e3c39c927bf957dbae87ef7f705802a85",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIResults.json": "8b6648142a4cf5c863cd4b4ebc6849fcf6b2329401e2ade1bfc2eb2bea2b69a6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCICompletionCases.json": "23d05f40ab6fceba84a5257c0dea7ff03de1ff057946380e5dcbc3e42008876d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCICompletionResults.json": "b7bdb1f848e3b904a6ff9cb99df37882227ea8cc562bbe00a7387a9f2860631f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIRuntimeReview.md": "fbf40e6e109fbbc9c7bad9492807a770a3e2fab7db2d734f3767631517dce679"
}
HANDOFF = "implementation/Phase-9-GRCV4-Handoff.md"
ACCEPTED_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACICases.json": "c3a5dd33e640c2f73dbc97373f27c21b53d98bf967aef524d7a84baaf7e671d8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIResults.json": "01a86bde6105776ecd955e3f3583925c5ec1edbe03a17cb09d9c454e09a43100",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIRuntimeReview.md": "db5e7ef7529bd2412df49f7db6f1b153d1787737f9e19118f54a4ff07cb84003"
}
PLAN = "implementation/Phase-9-GRCV4-ImplementationPlan.md"
FAMILIES = tuple(c + "_" + r for c in ("A", "C") for r in ("OS", "CI", "PC", "CI_PC", "RG2b"))
PROFILE_RECORDS = {
    "A_OS": ("A.2-AOS", "A.1-AOS"),
    "A_CI": ("A.2-ACI", "A.1-ACI"),
    "A_PC": ("A.2-APC", "A.1-APC"),
    "A_CI_PC": ("A.2-ACIPC", "A.1-ACIPC"),
    "A_RG2b": ("A.2-ARG2b", "A.1-ARG2b"),
    "C_CI": ("C-CI", None),
    "C_CI_PC": ("C-CI-PC", None),
    "C_RG2b": ("C-RG2b", None),
}
MECHANICS = (
    ("P9-8.0", "Accepted R1–R10 bounded feasibility, not native execution", "p9-81e-exact-backend-correction-and-p9-80-audit"),
    ("P9-8.1", "Accepted shared mechanics parent", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1a", "Fixed chart and immutable port graph", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1b", "Fixed-row differential and stage-specific weight bridge", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1c", "Fresh mechanical candidate trigger, not a completed spark", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1d", "Column coarse-graining and Split", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1e", "Exact-backend correction", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.2", "Pure allocator: 17 frozen vectors, three transforms; no event commit", "p9-82-pure-expansion-allocator"),
)
CHILDREN = {
    "a": "Coverage and comparison contracts",
    "b": "All-ten frozen expansion counterparts",
    "c": "Capacity and phase boundaries",
    "d": "Deeper recursive runtime expansion",
    "e": "Ordering, relabeling and signed-edge covariance",
    "f": "Chart rotation and reflection/chirality covariance",
    "g": "Larger-graph admission and independent oracles",
    "h": "Larger-graph runtime and covariance",
    "i": "Coverage reconciliation, side-tool catch-up and handoff",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


class Sources:
    def __init__(self, root):
        self.root, self.refs, self.values = Path(root).resolve(), {}, {}
        self.decoded = {}
        git(self.root, "merge-base", "--is-ancestor", CHECKPOINT, "HEAD")

    def current_bytes(self, name):
        snapshot = ACTIVE.get()
        if snapshot is not None:
            require(snapshot.root == self.root, "snapshot root mismatch")
            return snapshot.raw(name)
        return (self.root / name).read_bytes()

    def raw(self, name, *, historical=False):
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "repository-relative source required")
        if name not in self.values:
            path = self.root / name
            require(not path.is_symlink() and path.resolve().is_relative_to(self.root), "unsafe source path")
            boundary_pins = {**BOUNDARY_CLOSEOUT_SOURCES, **BOUNDARY_ARG2B_SOURCES, **BOUNDARY_CRG2B_SOURCES, **BOUNDARY_ACIPC_SOURCES, **BOUNDARY_CONTRACT_SOURCES, **BOUNDARY_MECHANICAL_SOURCES, **BOUNDARY_COS_SOURCES, **BOUNDARY_AOS_ORACLE_SOURCES, **BOUNDARY_AOS_SOURCES, **BOUNDARY_CCI_PREPARATION_SOURCES, **BOUNDARY_CCI_SOURCES, **BOUNDARY_ACI_ORACLE_SOURCES, **BOUNDARY_ACI_SOURCES, **BOUNDARY_CPC_SOURCES, **BOUNDARY_APC_SOURCES, **BOUNDARY_CCIPC_SOURCES}
            boundary_pins.update(DEEP_COS_SOURCES)
            boundary_pins.update(DEEP_CCI_SOURCES)
            boundary_pins.update(DEEP_ACI_ORACLE_SOURCES)
            boundary_pins.update(DEEP_ACI_SOURCES)
            boundary_pins.update(DEEP_APC_SOURCES)
            boundary_pins.update(DEEP_APC_FEASIBILITY_SOURCES)
            boundary_pins.update(DEEP_APC_COMPANION_SOURCES)
            boundary_pins.update(DEEP_APC_HISTORY_SOURCES)
            boundary_pins.update(DEEP_APC_JOINT_SOURCES)
            boundary_pins.update(DEEP_APC_FULL_SOURCES)
            boundary_pins.update(COVARIANCE_COS_SOURCES)
            boundary_pins.update(CHART_COS_SOURCES)
            boundary_pins.update(CHART_CCI_SOURCES)
            boundary_pins.update(CHART_ACI_SOURCES)
            boundary_pins.update(CHART_APC_SOURCES)
            boundary_pins.update(LARGER_COS_SOURCES)
            boundary_pins.update(LARGER_COS_BOUNDS_SOURCES)
            boundary_pins.update(COVARIANCE_CCI_SOURCES)
            boundary_pins.update(COVARIANCE_ACI_SOURCES)
            boundary_pins.update(COVARIANCE_APC_SOURCES)
            if name in boundary_pins:
                require(not historical, "preregistration is not a historical acceptance")
                frozen = self.current_bytes(name)
                require(hashlib.sha256(frozen).hexdigest() == boundary_pins[name], "boundary preregistration/mechanical source drift")
                self.values[name] = frozen
                self.refs[name] = dict(path=name, sha256=boundary_pins[name], revision=None,
                    basis=("pinned_larger_pointwise_bounds_not_native_admission" if name in LARGER_COS_BOUNDS_SOURCES else
                        "pinned_larger_equation_preflight_not_native_admission" if name in LARGER_COS_SOURCES else
                        "pinned_A_PC_history_carrier_chart_covariance_and_scoped_acceptance" if name in CHART_APC_SOURCES else
                        "pinned_A_CI_unsigned_history_joint_root_chart_covariance_and_scoped_acceptance" if name in CHART_ACI_SOURCES else
                        "pinned_C_CI_joint_root_chart_covariance_and_scoped_acceptance" if name in CHART_CCI_SOURCES else
                        "pinned_C_OS_chart_covariance_and_scoped_acceptance" if name in CHART_COS_SOURCES else
                        "pinned_A_PC_carrier_covariance_scoped_acceptance" if name in COVARIANCE_APC_SOURCES else
                        "pinned_A_joint_root_unsigned_history_covariance_scoped_acceptance" if name in COVARIANCE_ACI_SOURCES else
                        "pinned_joint_root_covariance_and_scoped_acceptance" if name in COVARIANCE_CCI_SOURCES else
                        "pinned_covariance_execution_and_scoped_acceptance" if name in COVARIANCE_COS_SOURCES else
                        "pinned_full_coupled_execution_and_scoped_acceptance" if name in DEEP_APC_FULL_SOURCES else
                        "pinned_coupled_witnesses_not_family_acceptance" if name in DEEP_APC_JOINT_SOURCES else
                        "pinned_eligible_source_failed_target_history_companion" if name in DEEP_APC_HISTORY_SOURCES else
                        "pinned_scoped_exclusion_acceptance_and_failed_source_companion" if name in DEEP_APC_COMPANION_SOURCES else
                        "pinned_frozen_source_allocation_exclusion_no_native_credit" if name in DEEP_APC_FEASIBILITY_SOURCES else
                        "pinned_failed_preflight_no_native_credit" if name in DEEP_APC_SOURCES else
                        "pinned_deep_execution_with_scoped_acceptance" if name in DEEP_ACI_SOURCES else
                        "pinned_accepted_independent_oracle_not_runtime_acceptance" if name in DEEP_ACI_ORACLE_SOURCES else
                        "pinned_deep_execution_with_scoped_acceptance" if name in DEEP_CCI_SOURCES else
                        "pinned_deep_execution_with_scoped_acceptance" if name in DEEP_COS_SOURCES else
                        "pinned_boundary_aggregate_closeout" if name in BOUNDARY_CLOSEOUT_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_ARG2B_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_CRG2B_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_ACIPC_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_CCIPC_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_APC_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_CPC_SOURCES else
                        "pinned_accepted_independent_oracle_not_runtime_acceptance" if name in BOUNDARY_ACI_ORACLE_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_ACI_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_CCI_SOURCES else
                        "pinned_target_preparation_not_native_campaign_or_acceptance" if name in BOUNDARY_CCI_PREPARATION_SOURCES else
                        "pinned_accepted_independent_oracle_not_runtime_acceptance" if name in BOUNDARY_AOS_ORACLE_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_AOS_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_COS_SOURCES else
                        "pinned_accepted_mechanical_evidence_not_numerical" if name in BOUNDARY_MECHANICAL_SOURCES else "pinned_preregistration_not_runtime_acceptance"))
                return frozen
            pins = {**ACCEPTED_ARG2B_SOURCES, **ACCEPTED_CCI_SOURCES, **ACCEPTED_ACI_SOURCES, **ACCEPTED_CPC_SOURCES, **ACCEPTED_APC_SOURCES, **ACCEPTED_CCIPC_SOURCES, **ACCEPTED_ACIPC_SOURCES, **ACCEPTED_CRG2B_SOURCES}
            if name in pins:
                require(not historical, "current pinned evidence is not a historical Git snapshot")
                frozen = self.current_bytes(name)
                family = "A_RG2b" if name in ACCEPTED_ARG2B_SOURCES else "C_RG2b" if name in ACCEPTED_CRG2B_SOURCES else "A_CI_PC" if name in ACCEPTED_ACIPC_SOURCES else "C_CI_PC" if name in ACCEPTED_CCIPC_SOURCES else "A_PC" if name in ACCEPTED_APC_SOURCES else "C_PC" if name in ACCEPTED_CPC_SOURCES else "A_CI" if name in ACCEPTED_ACI_SOURCES else "C_CI"
                require(hashlib.sha256(frozen).hexdigest() == pins[name],
                        "accepted " + family + " source drift: " + name)
                self.values[name] = frozen
                self.refs[name] = dict(path=name, sha256=pins[name], revision=None,
                    basis="pinned_execution_with_separate_scoped_user_acceptance")
                return frozen
            frozen = git(self.root, "show", CHECKPOINT + ":" + name)
            require(historical or self.current_bytes(name) == frozen, "Tranche 8 retained source drift: " + name)
            self.values[name] = frozen
            self.refs[name] = dict(path=name, sha256=hashlib.sha256(frozen).hexdigest(),
                                   revision=CHECKPOINT, basis="historical_git" if historical else "current_equals_accepted_checkpoint")
        return self.values[name]

    def read(self, name):
        if name not in self.decoded:
            self.decoded[name] = json.loads(self.raw(name))
        return deepcopy(self.decoded[name])

    def ref(self, name, *, historical=False, anchor=None):
        self.raw(name, historical=historical)
        return {**self.refs[name], **({"anchor": anchor} if anchor else {})}


def build(root=ROOT):
    import phase9_implementation_policy as policy
    policy.restore_packed_evidence(root)
    with validation_session(root=root):
        return _build(root)


def _build(root):
    import phase9_implementation_policy as policy
    sources = Sources(root)
    handoff = sources.ref(HANDOFF, historical=True)
    sources.ref(PLAN, historical=True)
    coverage_path = BASE + "P9-8.4a-Coverage.json"
    coverage = sources.read(coverage_path)
    families = coverage["families"]
    require(set(families) == set(FAMILIES), "all-ten prerequisite population drift")
    mechanics = [dict(work_id=i, status="accepted_bounded", scope=label,
                       acceptance={**handoff, "anchor": anchor}, numerical_conformance_inferred=False)
                 for i, label, anchor in MECHANICS]
    mechanics[0]["acceptance"] = sources.ref(BASE + "P9-8.0-AggregateReview.md")
    profiles = []
    for family in FAMILIES:
        row = families[family]
        evidence = [sources.ref(r["path"]) for r in row["evidence"]]
        review = {**handoff, "anchor": {"C_OS": "p9-83c-os-native-event-integration", "C_PC": "p9-83c-pc-whole-carrier-event-integration"}.get(family)}
        oracle = None
        if family in PROFILE_RECORDS:
            runtime_name, oracle_name = PROFILE_RECORDS[family]
            stem = BASE + "P9-8.3" + runtime_name
            validation = sources.read(stem + "-Validation.json")
            require("acceptance" in validation, "missing recorded runtime decision: " + family)
            evidence.append(sources.ref(stem + "-Validation.json"))
            review = sources.ref(stem + "-RuntimeReview.md")
            if oracle_name:
                oracle_stem = BASE + "P9-8.3" + oracle_name
                oracle = dict(status="accepted_bounded", evidence=sources.ref(oracle_stem + "-Oracle.json"),
                              review=sources.ref(oracle_stem + "-OracleReview.md"))
                if family != "A_OS":
                    oracle["acceptance"] = sources.ref(oracle_stem + "-Acceptance.json")
        profiles.append(dict(family=family, work_id="P9-8.3[" + family + "]",
            status="accepted_bounded", review=review, evidence=evidence,
            independent_A_oracle=oracle, subject_bindings=row["subject_bindings"],
            baseline=sources.ref(row["baseline_data"]["path"]),
            schedule=row["baseline_schedule"], comparison_budget=row["comparison_budget"],
            scope=row["reusable_scope"], prerequisites=row["prerequisites"],
            claim_traces=row["retained_claim_traces"], claim_trace_scope=row["claim_trace_scope"],
            claim_trace_pointer="/families/" + family + "/retained_claim_traces",
            claim_trace_record=sources.ref(coverage_path),
            historical_source_bindings="Original validation source identities remain in the pinned record; later code is not retroactively certified by this view.",
            public_support_added=False))
    closeout_name = BASE + "P9-8.3-CloseoutValidation.json"
    closeout = sources.read(closeout_name)
    large = []
    for family in FAMILIES:
        row = closeout["examples"][family]
        large.append(dict(family=family, configuration=sources.ref(row["path"]),
                          numerical_report=sources.ref(row["numerical_report"]),
                          outcomes=row["outcomes"], runtime_accepted=False,
                          next_owners=["P9-8.4g[" + family + "]", "P9-8.4h[" + family + "]"]))

    cells = {r["id"]: r for r in coverage["coverage_cells"] if r["owner"] == "P9-8.4b" and r["applicable"]}
    require(len(cells) == 322, "8.4b required population drift")
    covered, runs = set(), []
    for family, tag, expected_pass, expected_failure in (("C_OS", "COS", 14, 2), ("C_OS", "COSPhaseOne", 2, 0), ("A_OS", "AOS", 16, 0)):
        input_name, result_name = (BASE + "P9-8.4b-" + tag + n + ".json" for n in ("Cases", "Results"))
        inputs, result = sources.read(input_name), sources.read(result_name)
        require(result["manifest_digest"] == inputs["record_digest"], "runtime manifest link drift")
        require(result["user_accepted"] is False and result["aggregate_closed"] is False, "execution flags rewritten")
        cases = []
        for case in result["cases"]:
            ids = case["coverage_binding"]["cell_ids"]
            require(len(ids) == 2 and all(i in cells and cells[i]["family"] == family for i in ids), "foreign runtime coverage")
            passed = case["outcome"] == "passed_named_case"
            require(not passed or case["event_committed"] is True, "success without event")
            if passed:
                require(not covered.intersection(ids), "duplicate success credit")
                covered.update(ids)
            cases.append(dict(case_id=case["case_id"], cells=ids, case_passed=passed,
                              event_committed=case["event_committed"], outcome=case["outcome"], first_failure=case["first_failure"]))
        require(sum(c["case_passed"] for c in cases) == expected_pass and len(cases) - expected_pass == expected_failure,
                "retained case disposition drift")
        review_name = BASE + ("P9-8.4b-AOSRuntimeReview.md" if family == "A_OS" else "P9-8.4b-RuntimeReview.md")
        require("## Scoped user acceptance" in sources.raw(review_name).decode(), "missing scoped runtime acceptance")
        runs.append(dict(family=family, inputs=sources.ref(input_name), results=sources.ref(result_name),
                         record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
                         passed_cases=expected_pass, incomplete_cases=expected_failure, cases=cases,
                         status="accepted_bounded"))
    pending_cells = set()
    if ACCEPTED_CCI_SOURCES:
        input_name, result_name = (BASE + "P9-8.4b-CCICompletion" + n + ".json" for n in ("Cases", "Results"))
        inputs, result = sources.read(input_name), sources.read(result_name)
        require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True,
                "accepted C_CI execution binding drift")
        require(result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_CI authority widened")
        require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "C_CI case roster drift")
        pending_cases = []
        for case, row in zip(inputs["cases"], result["cases"], strict=True):
            ids = row["coverage_binding"]["cell_ids"]
            require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                    and all(i in cells and cells[i]["family"] == "C_CI" for i in ids), "C_CI foreign coverage")
            passed = row["outcome"] == "passed_named_case"
            require(row["case_passed"] == passed and (not passed or
                    row["event_committed"] is True and row["first_failure"] is None), "C_CI false case success")
            if passed:
                require(not pending_cells.intersection(ids), "duplicate C_CI cell")
                pending_cells.update(ids)
            pending_cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
                event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
        for ref in inputs["source_bindings"]:
            require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                    "accepted C_CI execution source drift: " + ref["path"])
        original_name = BASE + "P9-8.4b-CCIResults.json"
        original = sources.read(original_name)
        sources.ref(BASE + "P9-8.4b-CCICases.json")
        require(result["cases"][:8] == original["cases"][:8]
                and result["shared"] == original["shared"]
                and result["execution_partition"]["predecessor_record_digest"] == original["record_digest"],
                "C_CI retained execution reuse drift")
        failures = [dict(case_id=r["case_id"], event_committed=r["event_committed"],
                         case_passed=r["case_passed"], first_failure=r["first_failure"])
                    for r in original["cases"] if not r["case_passed"]]
        runs.append(dict(family="C_CI", inputs=sources.ref(input_name), results=sources.ref(result_name),
            record_digest=result["record_digest"],
            acceptance=sources.ref(BASE + "P9-8.4b-CCIRuntimeReview.md", anchor="scoped-user-acceptance"),
            review=sources.ref(BASE + "P9-8.4b-CCIRuntimeReview.md"),
            passed_cases=sum(c["case_passed"] for c in pending_cases),
            incomplete_cases=sum(not c["case_passed"] for c in pending_cases),
            cases=pending_cases, status="accepted_bounded",
            execution_partition=result["execution_partition"],
            original_attempt=dict(results=sources.ref(original_name), failures=failures)))
        require(len(pending_cells) == 32 and len(pending_cases) == 16, "accepted C_CI coverage drift")
        covered.update(pending_cells)
        pending_cells.clear()
    if ACCEPTED_ACI_SOURCES:
        input_name, result_name = (BASE + "P9-8.4b-ACI" + n + ".json" for n in ("Cases", "Results"))
        inputs, result = sources.read(input_name), sources.read(result_name)
        require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
                and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_CI execution/scope drift")
        require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_CI case roster drift")
        cases = []
        for case, row in zip(inputs["cases"], result["cases"], strict=True):
            ids = row["coverage_binding"]["cell_ids"]
            require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                    and all(i in cells and cells[i]["family"] == "A_CI" for i in ids), "accepted A_CI foreign coverage")
            passed = row["outcome"] == "passed_named_case"
            require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                    and row["first_failure"] is None), "accepted A_CI false success")
            if passed:
                require(not pending_cells.intersection(ids), "duplicate A_CI cell")
                pending_cells.update(ids)
            cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
                event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
        for ref in inputs["source_bindings"]:
            require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                    "accepted A_CI execution source drift: " + ref["path"])
        review_name = BASE + "P9-8.4b-ACIRuntimeReview.md"
        require("## Scoped user acceptance" in sources.raw(review_name).decode(), "missing scoped A_CI acceptance")
        runs.append(dict(family="A_CI", inputs=sources.ref(input_name), results=sources.ref(result_name),
            record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
            review=sources.ref(review_name),
            passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
            cases=cases, status="accepted_bounded"))
        require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_CI coverage drift")
        covered.update(pending_cells)
        pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-CPC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted C_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "C_PC" for i in ids), "accepted C_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted C_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate C_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted C_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-CPCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "missing scoped C_PC acceptance")
    runs.append(dict(family="C_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        signed_stage_pressure=sources.ref(BASE + "P9-8.4b-CPCScientificPressure.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 34 and len(cases) == 17, "accepted C_PC coverage drift")
    pressure = sources.read(BASE + "P9-8.4b-CPCScientificPressure.json")
    require(pressure["runtime_digest"] == result["record_digest"]
            and pressure["manifest_digest"] == inputs["record_digest"] and len(pressure["reads"]) == 1125
            and pressure["user_accepted"] is False and pressure["native_trajectories_rerun"] is False,
            "C_PC signed stage pressure binding drift")
    for ref in pressure["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "C_PC signed stage pressure source drift: " + ref["path"])
    runs[-1]["pc_claim_restrictions"] = pressure["claim_restrictions"]
    runs[-1]["claim_source"] = sources.ref(
        "implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json")
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-APC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "A_PC" for i in ids), "accepted A_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted A_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate A_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted A_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-APCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "A_PC separate acceptance missing")
    runs.append(dict(family="A_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        stage_evidence=dict(signed_read_certificates=3 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            target_beats=sum(len(r["continuation"]) for r in result["cases"]),
            fresh_final_reads=sum(len(r["final_reads"]) for r in result["cases"]),
            entry_W_Z_effects=sum(len(e) for r in result["cases"] for e in r["entry_effects"].values()),
            minimum_W_Z_effect_margin=min(e["minimum_margin_ratio"] for r in result["cases"] for v in r["entry_effects"].values() for e in v.values()),
            independent_source_chart=inputs["independent_source_chart"],
            resource_recipe=inputs["resource_recipe"]),
        pc_claim_restrictions=inputs["scientific_contracts"]["claim_restrictions"],
        claim_source=sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_PC coverage drift")
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-CCIPC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_CI_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted C_CI_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "C_CI_PC" for i in ids), "accepted C_CI_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted C_CI_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate C_CI_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted C_CI_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-CCIPCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "C_CI_PC separate acceptance missing")
    runs.append(dict(family="C_CI_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        stage_evidence=dict(signed_read_certificates=3 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            target_beats=sum(len(r["continuation"]) for r in result["cases"]),
            fresh_final_reads=sum(len(r["final_reads"]) for r in result["cases"]),
            same_root_writer_effects=sum(len(r["writer_effects"]) for r in result["cases"]),
            final_root_effects=sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            minimum_effect_margin=min(e["minimum_margin_ratio"] for r in result["cases"]
                for e in [*r["writer_effects"].values(), *[e for v in r["final_effects"].values() for e in v.values()]]),
            independent_source_chart=inputs["independent_source_chart"],
            independent_target_charts={c["case_id"]:c["independent_target_chart"] for c in inputs["cases"]}),
        stage_evidence_label="Signed reads, composite roots and carrier effects",
        pc_claim_restrictions=inputs["scientific_contracts"]["claim_restrictions"],
        claim_source=sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted C_CI_PC coverage drift")
    recheck_name = BASE + "P9-8.4b-CCIPCNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "C_CI_PC numerical recheck binding/scope drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "C_CI_PC numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-ACIPC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_CI_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_CI_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "A_CI_PC" for i in ids), "accepted A_CI_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted A_CI_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate A_CI_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted A_CI_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-ACIPCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "A_CI_PC separate acceptance missing")
    runs.append(dict(family="A_CI_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        stage_evidence=dict(signed_read_certificates=3 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            target_beats=sum(len(r["continuation"]) for r in result["cases"]),
            fresh_final_reads=sum(len(r["final_reads"]) for r in result["cases"]),
            entry_W_Z_effects=sum(len(v) for r in result["cases"] for v in r["entry_effects"].values()),
            source_old_Z_effects=sum(len(v) for v in result["shared"]["source_history_effects"].values()),
            final_root_effects=sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            minimum_effect_margin=min(e["minimum_margin_ratio"] for e in
                [*[e for v in result["shared"]["source_history_effects"].values() for e in v.values()],
                 *[e for r in result["cases"] for section in ("entry_effects", "final_effects") for v in r[section].values() for e in v.values()]]),
            independent_source_chart=inputs["independent_source_chart"],
            independent_target_charts={c["case_id"]:c["independent_whole_chart"] for c in inputs["cases"]}),
        stage_evidence_label="Signed joint roots and separate W/Z consumers",
        pc_claim_restrictions=inputs["scientific_contracts"]["claim_restrictions"],
        claim_source=sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_CI_PC coverage drift")
    recheck_name = BASE + "P9-8.4b-ACIPCNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "A_CI_PC numerical recheck binding/scope drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "A_CI_PC numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-CRG2b" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_RG2b execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted C_RG2b roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "C_RG2b" for i in ids), "accepted C_RG2b foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted C_RG2b false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate C_RG2b credit")
            pending_cells.update(ids)
        cases.append({"case_id": row["case_id"], "cells": ids, "case_passed": passed,
            "event_committed": row["event_committed"], "outcome": row["outcome"], "first_failure": row["first_failure"]})
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted C_RG2b execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-CRG2bRuntimeReview.md"
    require(b"## Scoped user acceptance" in sources.raw(review_name), "missing C_RG2b scoped acceptance")
    runs.append({"family": "C_RG2b", "inputs": sources.ref(input_name), "results": sources.ref(result_name),
        "record_digest": result["record_digest"], "acceptance": sources.ref(review_name, anchor="scoped-user-acceptance"),
        "review": sources.ref(review_name),
        "stage_evidence": {"signed_read_certificates": 5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            "inverse_level_residuals": 6*(5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"])),
            "ordinary_bridges": 1 + sum(len(r["continuation"]) for r in result["cases"]),
            "target_beats": sum(len(r["continuation"]) for r in result["cases"]),
            "fresh_final_reads": sum(len(r["final_reads"]) for r in result["cases"]),
            "source_controls": sum(len(v) for v in result["shared"]["source_effects"].values()),
            "entry_controls": sum(len(v) for r in result["cases"] for v in r["entry_effects"].values()),
            "final_controls": sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            "minimum_effect_margin": min(e["minimum_margin_ratio"] for e in
                [*[e for v in result["shared"]["source_effects"].values() for e in v.values()],
                 *[e for r in result["cases"] for section in ("entry_effects", "final_effects") for v in r[section].values() for e in v.values()]]),
            "independent_source_chart": inputs["independent_source_chart"],
            "independent_global_proof": inputs["independent_global_proof"],
            "independent_target_charts": {r["case_id"]:r["executed_case"]["independent_graph_chart"] for r in result["cases"]}},
        "stage_evidence_label": "Signed inverse chains, complete section errors and lagged invariance",
        "rg_claim_restrictions": inputs["scientific_contracts"]["claim_restrictions"],
        "claim_source": sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        "passed_cases": sum(c["case_passed"] for c in cases), "incomplete_cases": sum(not c["case_passed"] for c in cases),
        "cases": cases, "status": "accepted_bounded"})
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted C_RG2b coverage drift")
    recheck_name = BASE + "P9-8.4b-CRG2bNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "C_RG2b numerical recheck binding/scope drift")
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    shared_digest = hashlib.sha256(canonical_json_bytes(result["shared"])).hexdigest()
    require(len(recheck["cases"]) == len(result["cases"])
            and all(check["case_id"] == row["case_id"]
                    and check["case_digest"] == hashlib.sha256(canonical_json_bytes(row)).hexdigest()
                    and check["shared_digest"] == shared_digest
                    and check["successful_history_cells"] == 2
                    and check["interval_equations_recomputed"] is True
                    and check["native_trajectories_rerun"] is False
                    for check, row in zip(recheck["cases"], result["cases"], strict=True)),
            "C_RG2b completed numerical cases drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "C_RG2b numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-ARG2b" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_RG2b execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_RG2b roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "A_RG2b" for i in ids), "accepted A_RG2b foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted A_RG2b false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate A_RG2b credit")
            pending_cells.update(ids)
        cases.append({"case_id": row["case_id"], "cells": ids, "case_passed": passed,
            "event_committed": row["event_committed"], "outcome": row["outcome"], "first_failure": row["first_failure"]})
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted A_RG2b execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-ARG2bRuntimeReview.md"
    require(b"## Scoped user acceptance" in sources.raw(review_name), "missing A_RG2b scoped acceptance")
    runs.append({"family": "A_RG2b", "inputs": sources.ref(input_name), "results": sources.ref(result_name),
        "record_digest": result["record_digest"], "acceptance": sources.ref(review_name, anchor="scoped-user-acceptance"),
        "review": sources.ref(review_name),
        "stage_evidence": {"signed_read_certificates": 5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            "inverse_level_residuals": 4*(5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"])),
            "ordinary_bridges": 1 + sum(len(r["continuation"]) for r in result["cases"]),
            "target_beats": sum(len(r["continuation"]) for r in result["cases"]),
            "fresh_final_reads": sum(len(r["final_reads"]) for r in result["cases"]),
            "writer_controls": sum(len(v) for r in result["cases"] for v in r["writer_effects"].values()),
            "source_controls": sum(len(v) for v in result["shared"]["source_effects"].values()),
            "entry_controls": sum(len(v) for r in result["cases"] for v in r["entry_effects"].values()),
            "final_controls": sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            "minimum_effect_margin": min(e["minimum_margin_ratio"] for e in
                [*[e for v in result["shared"]["source_effects"].values() for e in v.values()],
                 *[e for r in result["cases"] for section in ("entry_effects", "final_effects", "writer_effects") for v in r[section].values() for e in v.values()]]),
            "independent_source_chart": inputs["independent_source_chart"],
            "independent_global_proof": inputs["independent_global_proof"],
            "independent_target_charts": {r["case_id"]:r["executed_case"]["independent_graph_chart"] for r in result["cases"]}},
        "stage_evidence_label": "Signed C/Y chains, W lineage and composed writer controls",
        "rg_claim_restrictions": inputs["scientific_contracts"]["claim_restrictions"],
        "claim_source": sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        "passed_cases": sum(c["case_passed"] for c in cases), "incomplete_cases": sum(not c["case_passed"] for c in cases),
        "cases": cases, "status": "accepted_bounded"})
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_RG2b coverage drift")
    recheck_name = BASE + "P9-8.4b-ARG2bNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "A_RG2b numerical recheck binding/scope drift")
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    shared_digest = hashlib.sha256(canonical_json_bytes(result["shared"])).hexdigest()
    require(len(recheck["cases"]) == len(result["cases"])
            and all(check["case_id"] == row["case_id"]
                    and check["case_digest"] == hashlib.sha256(canonical_json_bytes(row)).hexdigest()
                    and check["shared_digest"] == shared_digest
                    and check["successful_history_cells"] == 2
                    and check["interval_equations_recomputed"] is True
                    and check["native_trajectories_rerun"] is False
                    for check, row in zip(recheck["cases"], result["cases"], strict=True)),
            "A_RG2b completed numerical cases drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "A_RG2b numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    rows = []
    for family in FAMILIES:
        required = sorted(i for i, r in cells.items() if r["family"] == family)
        accepted = sorted(set(required) & covered)
        rows.append(dict(family=family, required_cells=len(required), accepted_cells=len(accepted),
                         executed_pending_cells=len(set(required) & pending_cells),
                         pending_cells=len(required) - len(accepted), required_cell_ids=required,
                         accepted_cell_ids=accepted, status="accepted_bounded" if len(accepted) == len(required)
                         else "executed_pending_review_and_acceptance" if set(required) <= pending_cells else "pending"))
    b_complete = len(covered) == len(cells)
    children = [dict(work_id="P9-8.4" + key, title=title,
                     status="accepted_inventory_not_execution" if key == "a" else
                     ("accepted_bounded" if b_complete else "partial") if key == "b" else "pending",
                     accepted=key == "a" or key == "b" and b_complete) for key, title in CHILDREN.items()]
    # Retain the exact claim/spec/paper associations without promoting their statuses.
    mapping = coverage["scientific_claim_mapping"]
    sources.ref(mapping["paper"]["path"])
    sources.ref(mapping["side_tool_source"])
    for name in ("specs/grc-9-v4-spec.md", "specs/grc-v4-spec.md"):
        sources.ref(name)
    sources.ref(BASE + "P9-8.4a-CoverageReview.md")
    supplements = [sources.ref(BASE + "P9-8.4b-" + name) for name in (
        "AOSOracleInputs.json", "AOSOracleResults.json", "AOSOracleReview.md", "AOSScientificPressure.json")]
    sources.ref(BASE + "P9-8.3-GraphConfigurationGuide.md")
    sources.ref(BASE + "P9-8.3-CatalogValidation.json")
    sources.ref("examples/grcv4/configurations.json")
    # Protect all current transitive inputs of the active 8.4 campaigns without
    # pretending the historical 8.3 validations describe today's source bytes.
    for tag in ("COS", "COSPhaseOne", "AOS"):
        for ref in sources.read(BASE + "P9-8.4b-" + tag + "Cases.json")["source_bindings"]:
            require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                    "8.4 execution source drift: " + ref["path"])
    scope = sorted(policy.runtime_targets(policy.recorded_acceptance(sources.root)), key=lambda r: r["path"])
    work = sources.read(policy.WORK)
    work_paths = {r["path"] for r in work["entries"]}
    ready, owners = policy.leaf_permissions(sources.root)
    import prepare_p984c_boundaries as boundary
    boundary_contract = sources.read(boundary.OUTPUT)
    check_boundary_storage_successor(boundary, boundary_contract, sources.root)
    import test_p984c_mechanics as mechanics_checks
    mechanics_result = sources.read(mechanics_checks.RESULT)
    check_mechanics_storage_successor(mechanics_checks, mechanics_result)
    require("## Scoped user acceptance" in sources.raw(mechanics_checks.REVIEW).decode(), "missing shared mechanics decision")
    require("## Scoped user acceptance" in sources.raw(boundary.REVIEW).decode(), "missing boundary contract decision")
    boundary_view = dict(record=sources.ref(boundary.OUTPUT), review=sources.ref(boundary.REVIEW),
        contract_accepted=True, acceptance_scope="matrix_and_budgets_only_not_numerical_history_cells",
        acceptance=sources.ref(boundary.REVIEW, anchor="scoped-user-acceptance"),
        mechanics=dict(record=sources.ref(mechanics_checks.RESULT), review=sources.ref(mechanics_checks.REVIEW),
            status="accepted_shared_mechanics", acceptance=sources.ref(mechanics_checks.REVIEW, anchor="scoped-user-acceptance"), observations=mechanics_result["observations"],
            test_methods=mechanics_result["tests_passed"], scope=mechanics_result["scope"],
            tests_rerun=False, numerical_history_credit=0, committed_events=0),
        record_digest=boundary_contract["record_digest"], disposition=boundary_contract["disposition"],
        counts=boundary_contract["counts"], layouts=boundary_contract["layouts"],
        families=boundary_contract["families"], schedule=boundary_contract["schedule"],
        retention=boundary_contract["retention"], prerequisites=boundary_contract["prerequisites"],
        native_runtime_executed=False, user_accepted=False)
    import p984c_cos as boundary_cos
    cos_summary = boundary_cos.status(sources.read(boundary_cos.INPUTS), sources.read(boundary_cos.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_cos.REVIEW).decode(), "missing C_OS boundary acceptance")
    require(cos_summary["passed_cases"] == 30 and cos_summary["exact_reuse_cases"] == 2, "incomplete C_OS boundary acceptance")
    cos_summary["accepted_cells"] = 64
    boundary_view["family_results"] = [dict(**cos_summary,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_cos.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_cos.INPUTS), results=sources.ref(boundary_cos.RESULTS),
        review=sources.ref(boundary_cos.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-COSResults.json"),
        comparison_scope="bounded_dense_crosscheck_not_rigorous_full_error_or_effect_separation")]
    import p984c_aos_oracle as boundary_aos
    aos_summary = boundary_aos.validate(sources.read(boundary_aos.INPUTS), sources.read(boundary_aos.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aos.REVIEW).decode(), "missing A_OS boundary oracle acceptance")
    boundary_view["oracle_preparations"] = [dict(**aos_summary, family="A_OS",
        status="accepted_oracle_scope", oracle_scope_accepted=True, native_steps=0,
        acceptance=sources.ref(boundary_aos.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aos.INPUTS), results=sources.ref(boundary_aos.RESULTS),
        review=sources.ref(boundary_aos.REVIEW),
        scope="saved_entry_full_formula_bounds_not_native_admission_or_uniform_trajectory_bound")]
    import p984c_aos_runtime as boundary_aos_runtime
    import p984c_aci_oracle as boundary_aci_oracle
    aci_oracle = boundary_aci_oracle.status(sources.read(boundary_aci_oracle.INPUTS), sources.read(boundary_aci_oracle.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aci_oracle.REVIEW).decode()
        and aci_oracle["passed_cases"] == 30, "missing or incomplete A_CI oracle acceptance")
    boundary_view["oracle_preparations"].append(dict(**aci_oracle,
        oracle_cases_passed=aci_oracle["passed_cases"] + aci_oracle["exact_accepted_target_reuses"],
        oracle_cases_required=aci_oracle["cases_required"], exact_reuse_cases=aci_oracle["exact_accepted_target_reuses"],
        status="accepted_oracle_scope", oracle_scope_accepted=True,
        acceptance=sources.ref(boundary_aci_oracle.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aci_oracle.INPUTS),
        results=sources.ref(boundary_aci_oracle.RESULTS), review=sources.ref(boundary_aci_oracle.REVIEW),
        scope="independent_joint_root_C_W_readback_and_domain_expectations_plus_exact_accepted_D45_targets_not_native_execution"))
    native_aos = boundary_aos_runtime.status(sources.read(boundary_aos_runtime.INPUTS), sources.read(boundary_aos_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aos_runtime.REVIEW).decode(), "missing A_OS boundary native acceptance")
    require(native_aos["successful_history_cells"] == 64, "incomplete A_OS boundary acceptance")
    native_aos["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_aos,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_aos_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aos_runtime.INPUTS), results=sources.ref(boundary_aos_runtime.RESULTS),
        review=sources.ref(boundary_aos_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-AOSResults.json"),
        comparison_scope="actual_saved_entry_full_formula_intervals_and_native_consumer_checks_not_uniform_trajectory_bound"))
    import p984c_cci_preparation as cci_preparation
    cci_ready = cci_preparation.status(sources.read(cci_preparation.INPUTS), sources.read(cci_preparation.RESULTS))
    preparation_status = "prepared_scope_only" if cci_ready["passed_cases"] + cci_ready["exact_reuse_cases"] == cci_ready["cases_required"] else "incomplete_preparation"
    boundary_view["target_preparations"] = [dict(**cci_ready, status=preparation_status,
        inputs=sources.ref(cci_preparation.INPUTS), results=sources.ref(cci_preparation.RESULTS),
        review=sources.ref(cci_preparation.REVIEW),
        scope="entry_joint_root_certificates_and_nominal_predictions_not_native_event_or_continuation")]
    import p984c_cci_runtime as boundary_cci_runtime
    native_cci = boundary_cci_runtime.status(sources.read(boundary_cci_runtime.INPUTS), sources.read(boundary_cci_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_cci_runtime.REVIEW).decode(), "missing C_CI boundary acceptance")
    require(native_cci["successful_history_cells"] == 64, "incomplete C_CI boundary acceptance")
    native_cci["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_cci,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_cci_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_cci_runtime.INPUTS), results=sources.ref(boundary_cci_runtime.RESULTS),
        review=sources.ref(boundary_cci_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-CCICompletionResults.json"),
        comparison_scope="actual_entry_joint_root_full_formula_intervals_and_native_whole_ball_admission_not_uniform_trajectory_bound"))
    import p984c_aci_runtime as boundary_aci_runtime
    native_aci = boundary_aci_runtime.status(sources.read(boundary_aci_runtime.INPUTS), sources.read(boundary_aci_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aci_runtime.REVIEW).decode(), "missing A_CI boundary acceptance")
    require(native_aci["successful_history_cells"] == 64, "incomplete A_CI boundary acceptance")
    native_aci["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_aci,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_aci_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aci_runtime.INPUTS), results=sources.ref(boundary_aci_runtime.RESULTS),
        review=sources.ref(boundary_aci_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-ACIResults.json"),
        comparison_scope="actual_entry_joint_root_readback_W_writer_restart_and_whole_ball_checks_not_uniform_trajectory_bound"))
    import p984c_cpc_runtime as boundary_cpc_runtime
    native_cpc = boundary_cpc_runtime.status(sources.read(boundary_cpc_runtime.INPUTS), sources.read(boundary_cpc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_cpc_runtime.REVIEW).decode()
            and native_cpc["successful_history_cells"] == 64, "C_PC acceptance scope drift")
    native_cpc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_cpc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_cpc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_cpc_runtime.INPUTS), results=sources.ref(boundary_cpc_runtime.RESULTS),
        review=sources.ref(boundary_cpc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-CPCResults.json"),
        comparison_scope="pointwise_full_formula_signed_readback_whole_carrier_reset_and_single_writer_checks_not_uniform_trajectory_bound"))
    import p984c_apc_runtime as boundary_apc_runtime
    native_apc = boundary_apc_runtime.status(sources.read(boundary_apc_runtime.INPUTS), sources.read(boundary_apc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_apc_runtime.REVIEW).decode()
            and native_apc["successful_history_cells"] == 64, "A_PC acceptance scope drift")
    native_apc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_apc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_apc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_apc_runtime.INPUTS), results=sources.ref(boundary_apc_runtime.RESULTS),
        review=sources.ref(boundary_apc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-APCResults.json"),
        comparison_scope="pointwise_fixed_row_signed_readback_exact_W_lineage_and_separate_W_Z_writers_not_uniform_trajectory_bound"))
    import p984c_ccipc_runtime as boundary_ccipc_runtime
    native_ccipc = boundary_ccipc_runtime.status(sources.read(boundary_ccipc_runtime.INPUTS), sources.read(boundary_ccipc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_ccipc_runtime.REVIEW).decode()
            and native_ccipc["successful_history_cells"] == 64, "C_CI_PC acceptance scope drift")
    native_ccipc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_ccipc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_ccipc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_ccipc_runtime.INPUTS), results=sources.ref(boundary_ccipc_runtime.RESULTS),
        review=sources.ref(boundary_ccipc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-CCIPCResults.json"),
        comparison_scope="pointwise_full_joint_root_signed_readback_fixed_old_Z_same_source_writer_and_strict_composite_slack_not_uniform_trajectory_bound"))
    import p984c_acipc_runtime as boundary_acipc_runtime
    native_acipc = boundary_acipc_runtime.status(sources.read(boundary_acipc_runtime.INPUTS), sources.read(boundary_acipc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_acipc_runtime.REVIEW).decode()
            and native_acipc["successful_history_cells"] == 64, "A_CI_PC acceptance scope drift")
    native_acipc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_acipc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_acipc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_acipc_runtime.INPUTS), results=sources.ref(boundary_acipc_runtime.RESULTS),
        review=sources.ref(boundary_acipc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-ACIPCResults.json"),
        comparison_scope="pointwise_full_joint_root_signed_readback_exact_W_lineage_fixed_old_Z_same_source_W_Z_writers_and_strict_composite_slack_not_uniform_trajectory_bound"))
    import p984c_crg2b_runtime as boundary_crg2b_runtime
    native_crg2b = boundary_crg2b_runtime.status(sources.read(boundary_crg2b_runtime.INPUTS), sources.read(boundary_crg2b_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_crg2b_runtime.REVIEW).decode()
            and native_crg2b["successful_history_cells"] == 64, "C_RG2b acceptance scope drift")
    native_crg2b["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_crg2b,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_crg2b_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_crg2b_runtime.INPUTS), results=sources.ref(boundary_crg2b_runtime.RESULTS),
        review=sources.ref(boundary_crg2b_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-CRG2bResults.json"),
        comparison_scope="signed_completion_six_level_inverse_chain_pointwise_section_and_lagged_invariance_checks_not_C1_or_uniform_trajectory_bound"))
    import p984c_arg2b_runtime as boundary_arg2b_runtime
    native_arg2b = boundary_arg2b_runtime.status(sources.read(boundary_arg2b_runtime.INPUTS), sources.read(boundary_arg2b_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_arg2b_runtime.REVIEW).decode()
            and native_arg2b["successful_history_cells"] == 64, "A_RG2b acceptance scope drift")
    native_arg2b["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_arg2b,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_arg2b_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_arg2b_runtime.INPUTS), results=sources.ref(boundary_arg2b_runtime.RESULTS),
        review=sources.ref(boundary_arg2b_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-ARG2bResults.json"),
        comparison_scope="signed_completion_four_level_CY_chain_pointwise_section_lagged_invariance_exact_W_lineage_and_writer_next_read_effects_not_C1_or_uniform_trajectory_bound"))
    import p984c_closeout as boundary_closeout
    reconciliation = boundary_closeout.reconcile(boundary_contract, boundary_view,
        {r["family"]: sources.read(r["inputs"]["path"]) for r in boundary_view["family_results"]})
    require(sources.read(boundary_closeout.RECORD) == reconciliation, "boundary aggregate reconciliation drift")
    boundary_view["closeout"] = dict(reconciliation, record=sources.ref(boundary_closeout.RECORD),
                                     review=sources.ref(boundary_closeout.REVIEW))
    child = next(r for r in children if r["work_id"] == "P9-8.4c")
    child.update(status="accepted_bounded", accepted=True)
    next(r for r in children if r["work_id"] == "P9-8.4f").update(status="partial_execution_accepted", accepted=False)
    deep = deep_view(sources)
    next(r for r in children if r["work_id"] == "P9-8.4d").update(status="partial_execution_accepted", accepted=False)
    next(r for r in children if r["work_id"] == "P9-8.4e").update(status="partial_execution_accepted", accepted=False)
    value = dict(schema="phase9_tranche8_evidence_v1", output_class="retained_implementation_evidence_not_forensic_authority",
        checkpoint=CHECKPOINT, mechanics=mechanics, profiles=profiles,
        runtime_scope_snapshot=scope,
        registered_runtime_paths=sorted(r["path"] for r in scope if r["path"] in work_paths),
        dependency_ready_snapshot=ready,
        permitted_paths_snapshot=sorted(r["path"] for r in scope if
            (r["requires_gate"] == "P9-G1" or r["path"] in work_paths) and set(ready) & owners[r["path"]]),
        runtime_scope_note="Display roster only; current policy must independently authenticate permission, dependency readiness and work bindings.",
        configuration=dict(status="accepted_preparation_not_large_runtime", review=sources.ref(closeout_name),
                           outcome_counts=closeout["outcome_counts"], families=large, catalog_size=42),
        coverage=dict(record=sources.ref(coverage_path), children=children, families=rows, runs=runs,
                      oracle_and_pressure=supplements, boundary_contract=boundary_view, deep_expansion=deep,
                      ordering_covariance=covariance_view(sources),chart_covariance=chart_view(sources),
                      larger_prerequisites=larger_view(sources),
                      required_cells=322, accepted_cells=len(covered), pending_cells=len(cells) - len(covered),
                      executed_pending_cells=len(pending_cells),
                      aggregate_closed=False, other_vector_cells=60, larger_history_cells=20),
        scientific_claim_mapping=mapping,
        verification=dict(level="pinned_sources_and_retained_structure", native_trajectories_rerun=False,
                          interval_equations_recomputed=False, historical_8_3_source_bindings_revalidated_against_current_code=False),
        future=dict(P9_8_5="pending_full_atomicity_campaign", P9_8_6="pending_conformance_review",
                    tranche_9="pending_public_lifecycle_and_compatibility", disabled_cells_pending=40,
                    new_public_support=[], general_ATC_inferred=False, arbitrary_graph_support=False),
        source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]))
    value["view_digest"] = digest(value)
    return value


def check_boundary_storage_successor(boundary, retained, root):
    """Only the accepted 1 MB storage-policy successor differs from 8.4c.

    Reconstruct every scientific/declaration field unchanged. Do not rewrite
    the historical contract or accept an arbitrary edited storage document.
    """
    path='docs/reference/EvidenceStorage.md'
    commit='faccfa0e2887ed411325ab19fd3151c394d0b08a'
    old='3cbc5e3d638a0281df0d94a98e282a9c59d29de8bccef0bf1224ad955d8bb11e'
    new='89e4728977ee45c8ea158179c3a5e7329fa5f45484c5df3e289c2ea3361f4a63'
    git(root,'merge-base','--is-ancestor',commit,'HEAD')
    require(hashlib.sha256(git(root,'show',commit+':'+path)).hexdigest()==new
        and hashlib.sha256((Path(root)/path).read_bytes()).hexdigest()==new,
        'unrecognized storage-policy successor')
    require(hashlib.sha256(git(root,'show',commit+'^:'+path)).hexdigest()==old,
        'storage-policy predecessor mismatch')
    reconstructed=boundary.build(root)
    row=next(r for r in reconstructed['source_bindings'] if r['path']==path)
    require(row['sha256']==new,'storage changed during reconstruction')
    row['sha256']=old
    require(boundary.seal(reconstructed)==retained,'boundary contract differs beyond accepted storage policy')


def check_mechanics_storage_successor(checker, retained):
    """Validate a detached metadata adaptation; original execution stays pinned.

    The preceding boundary check authenticates the exact accepted document
    transition. All runtime-source bindings and scientific fields still pass
    through the unchanged mechanical validator.
    """
    require(retained==checker.contract.seal(retained),'original mechanical digest drift')
    adapted=deepcopy(retained)
    row=next(r for r in adapted['source_bindings'] if r['path']=='docs/reference/EvidenceStorage.md')
    require(row['sha256']=='3cbc5e3d638a0281df0d94a98e282a9c59d29de8bccef0bf1224ad955d8bb11e',
            'unrecognized mechanical storage predecessor')
    row['sha256']='89e4728977ee45c8ea158179c3a5e7329fa5f45484c5df3e289c2ea3361f4a63'
    checker.check(checker.contract.seal(adapted))


def browser_source(value):
    # Smaller indentation preserves every field while keeping this generated
    # executable asset below the raw-file storage threshold; no lossy summary.
    return "// Generated from checked retained Tranche 8 evidence; not new authority.\nexport const TRANCHE8_EVIDENCE = " + json.dumps(value, indent=1, ensure_ascii=False) + ";\n"


def checked(root=ROOT):
    value = build(root)
    require((Path(root) / ASSET).read_text() == browser_source(value), "Tranche 8 browser evidence drift")
    return value


BOUNDARY_RUNTIME = {"C_OS": "p984c_cos", "A_OS": "p984c_aos_runtime",
    "C_CI": "p984c_cci_runtime", "A_CI": "p984c_aci_runtime", "C_PC": "p984c_cpc_runtime", "A_PC": "p984c_apc_runtime", "C_CI_PC": "p984c_ccipc_runtime", "A_CI_PC": "p984c_acipc_runtime", "C_RG2b": "p984c_crg2b_runtime", "A_RG2b": "p984c_arg2b_runtime"}


def deep_family_view(sources, family):
    if family == "A_PC":
        import p984d_apc_runtime as deep
        import p984d_apc_feasibility as feasibility
        import p984d_apc_companion_runtime as companion
        import p984d_apc_history as history
        import p984d_apc_joint_successor as joint
        import p984d_apc_full as full
        c=companion.c
        # Keep the original preflight review in provenance even though the
        # displayed acceptance now belongs to the successful full campaign.
        sources.ref(deep.REVIEW)
        original = deep.status(sources.read(deep.INPUTS), sources.read(deep.RESULTS))
        accepted=sources.read(c.ACCEPTANCE)
        require(accepted==c.acceptance(), "bounded exclusion acceptance drift")
        candidate=c.check(sources.read(c.INPUTS),sources.read(c.RESULTS))
        native=companion.check(sources.read(companion.INPUTS),sources.read(companion.RESULTS))
        hm,hr,hp=(sources.read(p) for p in (history.INPUTS,history.RESULTS,history.PRESSURE))
        hs=history.check(hm,hr);pressure=history.check_pressure(hm,hr,hp)
        earlier=joint.j.check(sources.read(joint.j.INPUTS),sources.read(joint.j.RESULTS))
        jm,jr=(sources.read(p) for p in (joint.INPUTS,joint.RESULTS))
        latest=joint.check(jm,jr)
        full_record = sources.read(full.RESULTS)
        fs=full.status(sources.read(full.INPUTS),full_record)
        acceptance_text = sources.raw(full.REVIEW).decode()
        require("## Scoped user acceptance" in acceptance_text
                and full_record["record_digest"] in acceptance_text,
                "missing or unbound A_PC deep acceptance")
        require(fs["passed_cases"] == 20, "incomplete A_PC deep acceptance")
        fs.update(status="accepted_bounded", accepted_cells=40, passing_pending_cells=0)
        summary=dict(original,**{k:fs[k] for k in ('status','native_cases','passed_cases','attempted_cases',
            'unattempted_cases','committed_events','target_steps','final_reads','passing_pending_cells','accepted_cells','failures')},
            source_steps=0,source_reused=True,successful_history_cells=2*fs['passed_cases'],
            source_companions_tested=3,native_event_attempts=fs['native_cases'],
            count_scope="full_twenty_layout_campaign_including_exact_pilot_reuse_prior_failures_separate")
        return dict(summary, inputs=sources.ref(full.INPUTS), results=sources.ref(full.RESULTS),
            review=sources.ref(full.REVIEW),
            acceptance=sources.ref(full.REVIEW, anchor="scoped-user-acceptance"),
            full_campaign=dict(**fs,inputs=sources.ref(full.INPUTS),results=sources.ref(full.RESULTS),
                plan=sources.ref(full.PLAN),review=sources.ref(full.REVIEW),
                acceptance=sources.ref(full.REVIEW, anchor="scoped-user-acceptance")),
            frozen_source_preflight=original,
            joint_witness=dict(**earlier,inputs=sources.ref(joint.j.INPUTS),results=sources.ref(joint.j.RESULTS),
                constraints=sources.ref(joint.j.DERIVATION),plan=sources.ref(joint.j.PLAN),
                failure_control="same_source_next_current_effect_separation_not_resource_failure"),
            joint_successor=dict(**latest,inputs=sources.ref(joint.INPUTS),results=sources.ref(joint.RESULTS),
                plan=sources.ref(joint.PLAN),review=sources.ref(joint.REVIEW),
                initial_history_mean=jm['initial_history_mean'],shares=jm['derivation']['selection']['shares']),
            history_companion=dict(**hs,pressure=pressure,inputs=sources.ref(history.INPUTS),
                results=sources.ref(history.RESULTS),diagnostic=sources.ref(history.PRESSURE),
                plan=sources.ref(history.PLAN),review=sources.ref(history.REVIEW)),
            source_companion=dict(independent=candidate,native=native,
                inputs=sources.ref(c.INPUTS),results=sources.ref(c.RESULTS),
                native_inputs=sources.ref(companion.INPUTS),native_results=sources.ref(companion.RESULTS),
                plan=sources.ref(c.PLAN),review=sources.ref(c.REVIEW),
                ledger_scope="historical_design_debt_unchanged_runtime_obligation_open"),
            preflight_pressure=dict(**deep.check_pressure(sources.read(deep.INPUTS), sources.read(deep.PRESSURE)),
                evidence=sources.ref(deep.PRESSURE)),
            allocation_feasibility=dict(**feasibility.check(sources.read(feasibility.RESULTS)),
                evidence=sources.ref(feasibility.RESULTS),review=sources.ref(feasibility.REVIEW),
                claim_scope="frozen_source_six_D94_layouts_only_conditional_on_existing_error_budgets",
                acceptance=sources.ref(c.ACCEPTANCE),user_accepted=True),
            comparison_scope="accepted_twenty_declared_coupled_layouts_with_exact_pilot_reuse_not_uniform_domain")
    if family == "A_CI":
        import p984d_aci_runtime as deep
        summary = deep.status(sources.read(deep.INPUTS), sources.read(deep.RESULTS))
        require("## Scoped user acceptance" in sources.raw(deep.REVIEW).decode(), "missing A_CI deep acceptance")
        require(summary["passed_cases"] == 20, "incomplete A_CI deep acceptance")
        summary.update(status="accepted_bounded", accepted_cells=40, passing_pending_cells=0)
        return dict(summary, inputs=sources.ref(deep.INPUTS), results=sources.ref(deep.RESULTS),
            acceptance=sources.ref(deep.REVIEW, anchor="scoped-user-acceptance"), review=sources.ref(deep.REVIEW),
            comparison_scope="A_full_joint_root_pointwise_bounds_actual_history_writer_not_uniform_trajectory_tube")
    if family == "C_CI":
        import p984d_cci as deep
        import p984d_cci_hardening as hardening
        summary = deep.status(sources.read(deep.INPUTS), sources.read(deep.RESULTS))
        require('## Scoped user acceptance' in sources.raw(deep.REVIEW).decode(), 'missing C_CI deep acceptance')
        summary.update(inputs=sources.ref(deep.INPUTS), results=sources.ref(deep.RESULTS),
            review=sources.ref(deep.REVIEW), acceptance=sources.ref(deep.REVIEW, anchor='scoped-user-acceptance'),
            status='accepted_bounded', accepted_cells=40, passing_pending_cells=0,
            comparison_scope="CI_only_tree23_pointwise_full_joint_root_bounds_not_uniform_trajectory_tube")
        supplement = sources.read(hardening.RESULTS)
        exact_transfers = sum(all(v == '0' for v in row['exact_coordinate_transfer_deltas'].values())
            for row in supplement['neighborhood'])
        summary['hardening'] = dict(**hardening.check(sources.read(hardening.INPUTS), supplement),
            exact_charge_preserving_probes=exact_transfers,
            rounded_transfer_controls=len(supplement['neighborhood'])-exact_transfers,
            inputs=sources.ref(hardening.INPUTS), results=sources.ref(hardening.RESULTS), review=sources.ref(deep.REVIEW),
            scope='nine_finite_target_probes_both_roles_two_steps_not_uniform_tube;native_excluded_step_and_late_event_rollback')
        summary['hardening'].update(status='accepted_bounded', acceptance=summary['acceptance'])
        return summary
    require(family == "C_OS", "deep evidence unavailable for this family")
    import p984d_cos as deep
    import p984d_cos_hardening as hardening
    summary = deep.status(sources.read(deep.INPUTS), sources.read(deep.RESULTS))
    require(all("## Scoped user acceptance" in sources.raw(p).decode() for p in (deep.REVIEW, hardening.REVIEW)), "missing C_OS deep acceptance")
    require(summary["passed_cases"] == 20, "incomplete deep acceptance")
    summary.update(inputs=sources.ref(deep.INPUTS), results=sources.ref(deep.RESULTS),
        review=sources.ref(deep.REVIEW), acceptance=sources.ref(deep.REVIEW, anchor="scoped-user-acceptance"),
        status="accepted_bounded", accepted_cells=40, passing_pending_cells=0,
        comparison_scope="bounded_independent_dense_crosscheck_and_captured_consumers_not_rigorous_error_tube")
    summary["hardening"] = dict(**hardening.check(sources.read(hardening.INPUTS),sources.read(hardening.RESULTS)),
        inputs=sources.ref(hardening.INPUTS),results=sources.ref(hardening.RESULTS),review=sources.ref(hardening.REVIEW),
        scope="24_pointwise_exact_real_sign_enclosures_at_represented_prestates_not_uniform_trajectory_tube;finite_neighborhood_not_native_event_admission")
    return summary


def deep_oracle_view(sources):
    import p984d_aci_oracle as oracle
    summary = oracle.status(sources.read(oracle.INPUTS), sources.read(oracle.RESULTS))
    require('## Scoped user acceptance' in sources.raw(oracle.REVIEW).decode(), 'missing deep A_CI oracle acceptance')
    summary.update(status="accepted_oracle_scope")
    return dict(summary, inputs=sources.ref(oracle.INPUTS), results=sources.ref(oracle.RESULTS),
        review=sources.ref(oracle.REVIEW), acceptance=sources.ref(oracle.REVIEW, anchor="scoped-user-acceptance"), oracle_scope_accepted=True,
        comparison_scope="pointwise_A_joint_root_enclosures_not_native_or_uniform_trajectory_tube")


def deep_view(sources):
    families = ("C_OS", "C_CI", "A_CI", "A_PC")
    rows = [deep_family_view(sources, f) for f in families]
    executed = {r["family"] for r in rows if r.get("native_cases", 0) > 0 or r["target_steps"] > 0}
    return dict(checkpoint="8.4d", family_results=rows, aggregate_closed=False,
        oracle_preparations=[deep_oracle_view(sources)],
        first_group=["C_OS", "C_CI", "A_CI", "A_PC"],
        first_group_accepted_cells=sum(r["accepted_cells"] for r in rows),
        first_group_closed=all(r["accepted_cells"] == 40 for r in rows),
        families_not_executed=[f for f in FAMILIES if f not in executed],
        other_family_credit=0, successive_event_credit=0)


def larger_view(sources):
    import p984g_cos as preflight
    import p984g_cos_bounds as bounds
    m,r=sources.read(preflight.INPUTS),sources.read(preflight.RESULTS)
    row=preflight.check(m,r)
    row.update(inputs=sources.ref(preflight.INPUTS),results=sources.ref(preflight.RESULTS),
        plan=sources.ref(preflight.PLAN),review=sources.ref(preflight.REVIEW))
    bm,br=sources.read(bounds.INPUTS),sources.read(bounds.RESULTS)
    successor=bounds.check(bm,br)
    successor.update(inputs=sources.ref(bounds.INPUTS),results=sources.ref(bounds.RESULTS),
        plan=sources.ref(bounds.PLAN),review=sources.ref(bounds.REVIEW),
        pointwise_resource_enclosures=True,uniform_domain=False,
        conditional_staged_outputs=True,production_shortcut_integrated=False,
        points=[dict(graph=c['graph'],role=c['role'],
            exact_real_minimum_lower=c['exact_real']['minimum_lower'],
            staged_minimum_lower=c['staged']['minimum_lower'],
            dense_proposal_sign_separation=c['staged']['minimum_oracle_sign_separation']) for c in br['cases']])
    for summary,review in ((row,preflight.REVIEW),(successor,bounds.REVIEW)):
        require('## Scoped user acceptance' in sources.raw(review).decode(),
            'missing larger C_OS bounded checkpoint acceptance')
        summary.update(user_accepted=True,acceptance_scope='bounded_research_checkpoint_not_native_admission',
            acceptance=sources.ref(review,anchor='scoped-user-acceptance'))
    row['pointwise_bounds']=successor
    row['open_obligations']=['proposed certified shared solver/conditioning and C regularity shortcut; not started; preserve rounding and admission guards',
        'complete native read/residual/charge/final-C admission; then assess 8.4h readiness']
    return dict(family_results=[row],aggregate_closed=False,first_group_closed=False,
        families_without_preflight=[f for f in FAMILIES if f!='C_OS'])


def family_status(root, family, checkpoint="8.4c"):
    """Selected checkpoint/family only; not full-index or boundary validity."""
    import importlib
    import phase9_implementation_policy as policy
    require(checkpoint in ("8.4c", "8.4d", "8.4e", "8.4f", "8.4g"), "unknown family checkpoint")
    if checkpoint == "8.4g":
        require(family=='C_OS','larger prerequisite preflight not available for this family')
        sources=Sources(root)
        return dict(schema="phase9_tranche8_family_status_v1",family=family,checkpoint=checkpoint,
            scope="equation_preflight_not_native_admission",oracle=larger_view(sources)['family_results'][0],
            source_refs=sorted(sources.refs.values(),key=lambda r:r['path']),
            other_families_checked=False,native_trajectories_rerun=False)
    if checkpoint == "8.4f":
        require(family in ("C_OS","C_CI","A_CI","A_PC"), "chart covariance not executed for this family")
        policy.restore_packed_evidence(root)
        with validation_session(({"C_OS":"p984f_cos","C_CI":"p984f_cci","A_CI":"p984f_aci","A_PC":"p984f_apc"}[family],), root=root):
            sources = Sources(root)
            return dict(schema="phase9_tranche8_family_status_v1", family=family, checkpoint=checkpoint,
                scope="selected_family_only_not_execution_permission", native=chart_view(sources,family=family)["family_results"][0],
                source_refs=sorted(sources.refs.values(),key=lambda r:r["path"]),
                other_families_checked=False,native_trajectories_rerun=False)
    if checkpoint == "8.4e":
        require(family in ("C_OS", "C_CI", "A_CI", "A_PC"), "ordering covariance not executed for this family")
        policy.restore_packed_evidence(root)
        module = {"C_OS": "p984e_cos", "C_CI": "p984e_cci", "A_CI": "p984e_aci", "A_PC": "p984e_apc"}[family]
        with validation_session((module,), root=root):
            sources = Sources(root)
            view = covariance_view(sources, family=family)
            return dict(schema="phase9_tranche8_family_status_v1", family=family, checkpoint=checkpoint,
                scope="selected_family_only_not_execution_permission", native=view["family_results"][0],
                source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]),
                other_families_checked=False, native_trajectories_rerun=False)
    if checkpoint == "8.4d":
        require(family in ("C_OS", "C_CI", "A_CI", "A_PC"), "deep evidence unavailable for this family")
        policy.restore_packed_evidence(root)
        if family == "A_CI":
            with validation_session(("p984d_aci_runtime",), root=root):
                sources = Sources(root)
                summary = deep_oracle_view(sources)
                return dict(schema="phase9_tranche8_family_status_v1", family=family, checkpoint=checkpoint,
                    scope="selected_family_only_not_execution_permission", oracle=summary,
                    native=deep_family_view(sources, family),
                    source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]),
                    other_families_checked=False, native_trajectories_rerun=False)
        module = {"C_OS": "p984d_cos", "C_CI": "p984d_cci", "A_PC": "p984d_apc_full"}[family]
        with validation_session((module,), root=root):
            sources = Sources(root)
            summary = deep_family_view(sources, family)
            return dict(schema="phase9_tranche8_family_status_v1", family=family, checkpoint=checkpoint,
                scope="selected_family_only_not_full_index_or_execution_permission", native=summary,
                source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]),
                other_families_checked=False, native_trajectories_rerun=False)
    require(family in BOUNDARY_RUNTIME, "boundary evidence unavailable for this family")
    policy.restore_packed_evidence(root)
    name = BOUNDARY_RUNTIME[family]
    with validation_session((name,), root=root):
        module = importlib.import_module(name)
        sources = Sources(root)
        summary = module.status(sources.read(module.INPUTS), sources.read(module.RESULTS))
        review = sources.raw(module.REVIEW).decode()
        cells = 2 * (summary["passed_cases"] + summary["exact_reuse_cases"])
        require(cells == 64, "incomplete boundary scope")
        require("## Scoped user acceptance" in review, "missing scoped acceptance")
        summary.update(accepted_cells=cells, status="accepted_bounded", passing_pending_cells=0,
            acceptance=sources.ref(module.REVIEW, anchor="scoped-user-acceptance"))
        summary.update(inputs=sources.ref(module.INPUTS), results=sources.ref(module.RESULTS))
        return dict(schema="phase9_tranche8_family_status_v1", family=family, checkpoint="8.4c",
            scope="selected_family_only_not_full_index_or_execution_permission",
            native=summary, source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]),
            other_families_checked=False, native_trajectories_rerun=False)


def chart_view(sources, *, family=None):
    import importlib
    modules={"C_OS":"p984f_cos","C_CI":"p984f_cci","A_CI":"p984f_aci","A_PC":"p984f_apc"}
    rows=[]
    for name,module in modules.items():
        if family is not None and name != family:continue
        chart=importlib.import_module(module)
        summary=chart.check(sources.read(chart.INPUTS),sources.read(chart.RESULTS))
        review=sources.raw(chart.REVIEW).decode();acceptance=None
        if name in ("C_OS","C_CI","A_CI","A_PC"):
            require("## Scoped user acceptance" in review and sources.read(chart.RESULTS)["record_digest"] in review,
                    "missing or unbound chart acceptance")
            summary.update(status="accepted_bounded",accepted_cells=24,passing_pending_cells=0)
            acceptance=sources.ref(chart.REVIEW,anchor="scoped-user-acceptance")
        rows.append(dict(summary,acceptance=acceptance,inputs=sources.ref(chart.INPUTS),
            results=sources.ref(chart.RESULTS),plan=sources.ref(chart.PLAN),review=sources.ref(chart.REVIEW),
            comparison_scope=("pointwise_full_joint_root_certificates_and_chart_covariance_not_uniform_trajectory_enclosure"
                if name in ("C_CI","A_CI") else "pointwise_PC_read_writer_carrier_certificates_and_chart_covariance_not_uniform_trajectory_enclosure" if name=="A_PC" else "exact_frozen_pairs_and_bounded_dense_native_counterparts_not_uniform_error_certificate")))
    first_group_closed = family is None and {r['family'] for r in rows if r['accepted_cells']==24}==set(modules)
    if first_group_closed:
        require('## First-group acceptance' in sources.raw('implementation/phase-9-grcv4/tranche-8/P9-8.4f-APCReview.md').decode(),
                'missing first-group chart acceptance')
    return dict(checkpoint="8.4f",aggregate_closed=False,first_group_closed=first_group_closed,
        first_group_accepted_cells=sum(r['accepted_cells'] for r in rows),family_results=rows,
        families_not_executed=[f for f in FAMILIES if f not in modules])


def covariance_view(sources, *, family=None):
    import importlib
    modules = {"C_OS": "p984e_cos", "C_CI": "p984e_cci", "A_CI": "p984e_aci", "A_PC": "p984e_apc"}
    rows = []
    for name, module in modules.items():
        if family is not None and name != family:
            continue
        covariance = importlib.import_module(module)
        summary = covariance.check(sources.read(covariance.INPUTS), sources.read(covariance.RESULTS))
        review = sources.raw(covariance.REVIEW).decode()
        acceptance = None
        if name in ("C_OS", "C_CI", "A_CI", "A_PC"):
            require("## Scoped user acceptance" in review
                    and sources.read(covariance.RESULTS)["record_digest"] in review,
                    "missing or unbound covariance acceptance")
            summary.update(status="accepted_bounded", accepted_cells=20, passing_pending_cells=0)
            acceptance = sources.ref(covariance.REVIEW, anchor="scoped-user-acceptance")
        rows.append(dict(summary, acceptance=acceptance,
            inputs=sources.ref(covariance.INPUTS), results=sources.ref(covariance.RESULTS),
            plan=sources.ref(covariance.PLAN), review=sources.ref(covariance.REVIEW),
            comparison_scope="two_layouts_five_transforms_two_steps_per_role_not_chart_symmetry_or_uniform_error_bound"))
    return dict(checkpoint="8.4e", family_results=rows, aggregate_closed=False,
                families_not_executed=[f for f in FAMILIES if f not in modules])


def next_work(value):
    c = value["coverage"]
    boundary_summary = " ".join(
        f"8.4c {r['family']}: {r['accepted_cells']}/{r['required_cells']} accepted history cells; {r['passing_pending_cells']} passing cells pending acceptance."
        for r in c["boundary_contract"]["family_results"])
    oracle_summary = " ".join(
        f"{r['family']} boundary oracle: {r['oracle_cases_passed']}/{r['oracle_cases_required']} target expectations available; oracle scope {'accepted' if r['oracle_scope_accepted'] else 'pending review'}, no runtime acceptance follows from the oracle."
        for r in c["boundary_contract"]["oracle_preparations"])
    preparation_summary = " ".join(
        f"{r['family']} target preparation: {r['passed_cases'] + r['exact_reuse_cases']}/{r['cases_required']} cases; native event/continuation evidence and acceptance reported separately."
        for r in c["boundary_contract"]["target_preparations"])
    return (f"Tranche 8: shared 8.1 mechanics and 8.2 allocator accepted; all ten 8.3 bounded profile integrations accepted. "
            f"8.4b has {c['accepted_cells']}/{c['required_cells']} accepted history cells; {c['pending_cells']} remain. "
            f"{c['executed_pending_cells']} additional cells have passing execution evidence awaiting review/acceptance. "
            f"{boundary_summary} {oracle_summary} {preparation_summary} 8.4c is closed at 640/640 accepted history cells. 8.4d C_OS: 40 accepted history cells; C_CI: 40 accepted history cells. A_CI: 40 separately accepted native history cells; A_PC: frozen-source D94 exclusion accepted; resource-only companion passes target preflight but fails the fresh trigger. History-only companion preserves fresh source eligibility but fails D94 target positivity at step one. The full coupled campaign now passes all twenty A_PC cases: forty histories, four hundred native continuation steps and forty final reads; nineteen new cases plus exact pilot reuse. Forty A_PC cells are accepted. The first-group .d checkpoint is closed at 160 accepted cells. Prior failures remain separate. First-group .e C_OS has 20 accepted covariance cells on two layouts and five transforms. C_CI has 20 accepted full-joint-root covariance cells. A_CI has 20 accepted covariance cells with unsigned history/writer and full joint roots. A_PC has 20 accepted covariance cells on D59/D94 using the accepted coupled history/allocation source, with unsigned W and signed carrier transport/archive/reset. First-group .e is accepted at 80/80 history cells; C_OS .f now supplies 24 accepted chart-covariance history cells, separately from four frozen mechanical-plan executions. C_CI .f supplies 24 accepted full-joint-root chart cells, with independent pointwise interval certificates and explicit frozen-plan reuse. A_CI .f supplies 24 accepted unsigned-history/writer/full-joint-root chart cells, with pointwise root/output certificates and explicit frozen-plan reuse. A_PC .f supplies 24 accepted full-chart history/carrier cells on coupled D59/D94 witnesses, with archives, explicit loss, zero target initialization and ZOH/log-W continuation. The first group is accepted at 96/96 cells; .g prerequisites are next. Other .f families remain unexecuted. No uniform neighborhood follows. Six families remain native-unexecuted. 8.4d–i and 8.5/8.6 remain open. Larger-graph preparation is not runtime acceptance; "
            "public lifecycle and forty disabled cells remain Tranche 9 work. No new support or execution permission follows from this view.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "check", "verify-retained"), default="status", nargs="?")
    parser.add_argument("--family", choices=("A_OS", "C_OS", "C_CI", "A_CI", "C_PC", "A_PC", "C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"))
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--checkpoint", choices=("8.4b", "8.4c", "8.4d", "8.4e", "8.4f", "8.4g"), default="8.4b")
    parser.add_argument("--oracle", action="store_true", help="check A_OS or A_CI 8.4c independent oracle scope, not native execution")
    parser.add_argument("--preparation", action="store_true", help="check C_CI 8.4c target preparation, not a native campaign")
    args = parser.parse_args()
    if args.checkpoint == '8.4g':
        require(args.family=='C_OS' and not args.oracle and not args.preparation,'select C_OS prerequisite preflight')
        require(args.action in ('status','verify-retained') and
            (not args.recheck_numerics or args.action=='verify-retained'),'invalid prerequisite mode')
        if args.action=='status':print(json.dumps(family_status(ROOT,args.family,args.checkpoint),indent=2))
        else:
            subprocess.run([sys.executable,str(ROOT/HERE/'tranche8_retained.py'),
                str(ROOT/HERE/'p984g_cos_bounds.py'),'check',*(['--recheck-numerics'] if args.recheck_numerics else [])],cwd=ROOT,check=True)
        return
    if args.checkpoint == "8.4f":
        require(args.family in ("C_OS","C_CI","A_CI","A_PC") and not args.oracle and not args.preparation,
            "select C_OS/C_CI/A_CI/A_PC chart covariance")
        require(args.action in ("status","verify-retained") and
            (not args.recheck_numerics or args.action == "verify-retained"),"invalid chart mode")
        if args.action == "status":
            print(json.dumps(family_status(ROOT,args.family,args.checkpoint),indent=2))
        else:
            subprocess.run([sys.executable,str(ROOT/HERE/"tranche8_retained.py"),
                str(ROOT/HERE/{"C_OS":"p984f_cos.py","C_CI":"p984f_cci.py","A_CI":"p984f_aci.py","A_PC":"p984f_apc.py"}[args.family]),"check",*(["--recheck-numerics"] if args.recheck_numerics else [])],cwd=ROOT,check=True)
        return
    if args.checkpoint == "8.4e":
        require(args.family in ("C_OS", "C_CI", "A_CI", "A_PC") and not args.oracle and not args.preparation,
                "select C_OS/C_CI/A_CI/A_PC ordering covariance, not oracle/preparation")
        require(args.action in ("status", "verify-retained")
                and (not args.recheck_numerics or args.action == "verify-retained"), "invalid covariance mode")
        if args.action == "status":
            print(json.dumps(family_status(ROOT, args.family, args.checkpoint), indent=2))
        else:
            subprocess.run([sys.executable, str(ROOT / HERE / "tranche8_retained.py"),
                str(ROOT / HERE / {"C_OS": "p984e_cos.py", "C_CI": "p984e_cci.py", "A_CI": "p984e_aci.py", "A_PC": "p984e_apc.py"}[args.family]), "check", *(["--recheck-numerics"] if args.recheck_numerics else [])],
                cwd=ROOT, check=True)
        return
    if args.checkpoint == "8.4d":
        if args.family in ("A_CI", "A_PC"):
            require(args.family == "A_CI" or not args.oracle, "A_PC uses its in-case independent preflight")
            require(not args.preparation and args.action in ("status", "verify-retained"),
                "select status or verify-retained; --oracle selects the A_CI independent prerequisite")
            require(not args.recheck_numerics or args.action == "verify-retained", "recheck requires verify-retained")
            if args.action == "status":
                print(json.dumps(family_status(ROOT, args.family, args.checkpoint), indent=2))
            else:
                script = "p984d_aci_oracle.py" if args.oracle else {"A_CI": "p984d_aci_runtime.py", "A_PC": "p984d_apc_runtime.py"}[args.family]
                subprocess.run([sys.executable, str(ROOT / HERE / "tranche8_retained.py"),
                    str(ROOT / HERE / script), "--check-retained",
                    *(["--recheck-numerics"] if args.recheck_numerics else [])], cwd=ROOT, check=True)
                if args.family == "A_PC":
                    subprocess.run([sys.executable, str(ROOT / HERE / "tranche8_retained.py"),
                        str(ROOT / HERE / "p984d_apc_feasibility.py"), "--check",
                        *(["--recheck-numerics"] if args.recheck_numerics else [])], cwd=ROOT, check=True)
                    for companion_script in ("p984d_apc_companion.py", "p984d_apc_companion_runtime.py"):
                        subprocess.run([sys.executable,str(ROOT / HERE / "tranche8_retained.py"),
                            str(ROOT / HERE / companion_script),"--check",
                            *(["--recheck-numerics"] if args.recheck_numerics else [])],cwd=ROOT,check=True)
                    for mode in ("--check", "--check-pressure"):
                        subprocess.run([sys.executable,str(ROOT / HERE / "tranche8_retained.py"),
                            str(ROOT / HERE / "p984d_apc_history.py"),mode,
                            *(["--recheck-numerics"] if args.recheck_numerics else [])],cwd=ROOT,check=True)
                    for script,mode in (("p984d_apc_joint.py","check-derivation"),
                            ("p984d_apc_joint.py","check"),("p984d_apc_joint_successor.py","check"),
                            ("p984d_apc_full.py","check")):
                        subprocess.run([sys.executable,str(ROOT / HERE / "tranche8_retained.py"),
                            str(ROOT / HERE / script),mode,
                            *(["--recheck-numerics"] if args.recheck_numerics else [])],cwd=ROOT,check=True)
            return
        require(args.family in ("C_OS", "C_CI", "A_CI") and not args.oracle and not args.preparation,
            "select completed C_OS or C_CI deep evidence")
        require(not args.recheck_numerics or (args.family == "C_CI" and args.action == "verify-retained"),
            "C_CI numerical recheck requires verify-retained")
        if args.action == "status":
            print(json.dumps(family_status(ROOT, args.family, args.checkpoint), indent=2))
        else:
            require(args.action == "verify-retained", "use verify-retained for the deep checker")
            if args.family == "C_CI":
                subprocess.run([sys.executable, str(ROOT / HERE / "tranche8_retained.py"),
                    str(ROOT / HERE / "p984d_cci.py"), "--check-retained",
                    *(["--recheck-numerics"] if args.recheck_numerics else [])], cwd=ROOT, check=True)
                import p984d_cci_hardening as hardening
                sources = Sources(ROOT)
                for name in (hardening.INPUTS, hardening.RESULTS):
                    sources.raw(name)
                subprocess.run([sys.executable, str(ROOT / hardening.SELF), 'check',
                    *(['--recheck-numerics'] if args.recheck_numerics else [])], cwd=ROOT, check=True)
                return
            subprocess.run([sys.executable, str(ROOT / HERE / "tranche8_retained.py"),
                str(ROOT / HERE / "p984d_cos.py"), "--check"], cwd=ROOT, check=True)
            sources=Sources(ROOT)
            import p984d_cos_hardening as hardening
            for name in (hardening.INPUTS,hardening.RESULTS,hardening.REVIEW):
                sources.raw(name)
            subprocess.run([sys.executable,str(ROOT / hardening.SELF),"check"],cwd=ROOT,check=True)
        return
    if args.action != "verify-retained":
        if args.family:
            require(args.action == "status" and args.checkpoint == "8.4c"
                and not args.recheck_numerics and not args.oracle and not args.preparation,
                "family status requires the 8.4c checkpoint without numerical options")
            print(json.dumps(family_status(ROOT, args.family), indent=2))
            return
        value = checked()
        require(not args.family and not args.recheck_numerics and not args.oracle and not args.preparation and args.checkpoint == "8.4b", "numerical/checker options require verify-retained")
        print(json.dumps(value if args.action == "status" else dict(status="passed", view_digest=value["view_digest"],
              level=value["verification"]["level"], accepted_cells=value["coverage"]["accepted_cells"], native_trajectories_rerun=False), indent=2))
        return
    require(args.family is not None, "select one completed family explicitly")
    if args.checkpoint != "8.4c":
        checked()  # Keep historical .b dispatch unchanged in this bounded refactor.
    require(not args.oracle or (args.family in ("A_OS", "A_CI") and args.checkpoint == "8.4c"), "oracle selection requires A_OS/A_CI boundary checkpoint")
    require(not args.preparation or (args.family == "C_CI" and args.checkpoint == "8.4c"), "preparation selection requires C_CI boundary checkpoint")
    if args.checkpoint == "8.4c":
        require(args.family in BOUNDARY_RUNTIME, "boundary evidence unavailable for this family")
        if args.family in ("C_PC", "A_PC", "C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"):
            commands = [[sys.executable, str(ROOT / HERE / (BOUNDARY_RUNTIME[args.family] + ".py")), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        elif args.family == "A_CI":
            script = "p984c_aci_oracle.py" if args.oracle else "p984c_aci_runtime.py"
            commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        elif args.family == "C_CI":
            script = "p984c_cci_preparation.py" if args.preparation else "p984c_cci_runtime.py"
            commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        elif args.family == "C_OS":
            require(not args.recheck_numerics, "C_OS checker already recomputes dense comparisons")
            commands = [[sys.executable, str(ROOT / HERE / "p984c_cos.py"), "--check"]]
        else:
            script = "p984c_aos_oracle.py" if args.oracle else "p984c_aos_runtime.py"
            commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
    elif args.family == "C_OS":
        require(not args.recheck_numerics, "C_OS retained checker always recomputes its dense comparisons, not native trajectories")
        commands = [[sys.executable, str(ROOT / HERE / "p984b_cos_successor.py"), "--check-retained", *extra] for extra in (["--original"], [])]
    else:
        script = {"C_CI": "p984b_cci_completion.py", "A_CI": "p984b_aci_runtime.py", "A_OS": "p984b_aos_runtime.py",
                  "C_PC": "p984b_cpc_runtime.py", "A_PC": "p984b_apc_runtime.py", "C_CI_PC": "p984b_ccipc_runtime.py", "A_CI_PC": "p984b_acipc_runtime.py", "C_RG2b": "p984b_crg2b_runtime.py", "A_RG2b": "p984b_arg2b_runtime.py"}[args.family]
        commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                     *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        if args.family == "C_PC":
            commands.append([sys.executable, str(ROOT / HERE / "p984b_cpc_pressure.py"), "--check-retained",
                             *(["--recheck-numerics"] if args.recheck_numerics else [])])
    for command in commands:
        if args.checkpoint == "8.4c":
            command.insert(1, str(ROOT / HERE / "tranche8_retained.py"))
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
