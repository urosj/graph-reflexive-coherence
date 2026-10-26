"""Read-only Tranche 8 evidence index; never implementation permission or a rerun.

The committed checkpoint pins existing acceptance, not a new acceptance ledger.
Historical mutable handoffs are read from Git; immutable retained evidence must
still match on disk. Missing ignored copies may be restored from lossless archives.
Numerical checkers are exposed only by explicit CLI action.
"""

import argparse
import hashlib
import json
import lzma
from pathlib import Path
import subprocess
import sys
from copy import deepcopy
from contextlib import contextmanager
from unittest.mock import patch

from tranche8_validation import ACTIVE, validation_session, LOCK
from p984h_pre_solve_reuse_sources import historical_view, historical_binding

# Display references only. Execution manifests authenticate all underlying
# code/fixture hashes; closeout authenticates its checker sources separately.
LARGER_RUNTIME_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-1.json.xz": "a763c9d77fb7e645cd9f1b0a71ddac3f4f00291440071154760fb9aaa9404e2a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-10.json.xz": "b4d5690b747ba23e12fc6b8fce23fadd939667f49ea79b5ab54dd051a4cd488c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-2.json.xz": "ed3c805506a0309fd10dcdacec183aa475bcca603d89d82637197dbc63a2510b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-3.json.xz": "1a320c7c265850b40fbd9aefd35abf8f7dfa77621eabd4450d6999d8216ed47d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-4.json.xz": "455a8f3590969eeec1077df4362618c7b3bccb01e0aab25939ddcd4a4ef43cbe",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-5.json.xz": "8170766a83f62fd84cda5fe4b6ee1df283b367113f6642373f10287b03d1b69b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-6.json.xz": "4358df33cfefc752cbc705bbc58b6b247dc27e84db366db170cd57f57dd3331e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-7.json.xz": "f5a865063d28a7bf5c2d20d8f59d7f6b1840477279dba74b433b352a13b65abb",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-8.json.xz": "f0dd9da2812476a8b2529c144a947c603bb1fb5611c1c4f0f4b10a91bb462d58",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-9.json.xz": "6b226adae8b5a76fc735721f585130522043f3c32163403f18f285c7e7b4d5fd",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-current-final.json.xz": "0406700b2861056cc59d02307cc20c4f9e1cba972e4a94e57eb066acaeb19b2d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-event.json.xz": "5381f789f81a445b51919231637270f8aaa896cc287c463625d300c9907ff858",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-1.json.xz": "1ad3e1c2261f08ca11a1e11a55fc41d5c393376ec463751adca1e638824e6978",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-10.json.xz": "123bc6119340a55aa7dc8898b06ba65b5ca64059715ff69fc58ef49fd77a93af",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-2.json.xz": "ee4799d8e32ec3f7c8ef3b8659d68fb755413087c466c122d78bb1eec1b1b84a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-3.json.xz": "40b1f442c5b3e8c8ea6528cf1a760752be6db2d31f3854b9082b997d230ee687",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-4.json.xz": "7050fa5a02025d4f169723ad8d411a873d626096bd04bf6ad7cc34e1ca6b2d31",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-5.json.xz": "16e1c2c0804f8863dfd18ad50247976723b08b033fcfb645c25c8cdf3d653906",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-6.json.xz": "e4ead9d9813ddce64c11059ed5a7bcad3a26ec101928f84503931bda0dd3bbd0",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-7.json.xz": "c99127842fd42d4f01768085921f2527899fe07131a097a7c194d0f99d7ad105",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-8.json.xz": "413352fe266d99f7a14c940263db57244fd2032cbe2ee3029c1678a9a8de848b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-9.json.xz": "a44b3de2a441c812886c9316a45dfa1bb2cd2b321e0026b905af21fa288a5740",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-reset-final.json.xz": "22f3a6cc6ac096e92ba592875ac1799a2a48471cb871b8eefc5702373b1ea11a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACI-source.json.xz": "7975acfe75f44b3ceab8db01c110cee7204ae821c35f4562d1e15e403734f41b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICampaignInputs.json": "6b54eb6dc816031f29d6209fa8a4509911186da5502a69b290aba22536bc841a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICampaignPlan.md": "8099d08f77445268cdd229727845044e789e7beef4069608d3232e81591d1ad8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACIChargeInputs.json": "4556fd2a89bb0dd218b1170b95ca0ad45e536e1d0cc983e0e0bdcca215a6512b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICloseout.json": "e82f44ccb055b9df10f754b7abe6d22944e375397b006797413f23771efc6221",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-combined-current.json.xz": "af0f05525ec0a73e7a6b3e0c4aca178414b5f45a0d84efbb36124c8c4ad8640c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-combined-event.json.xz": "0bd7d85c09c1241f540f2a326f78b037e119c9115d5fedf9cf1a848462e6b9cd",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-combined-reset.json.xz": "3ca6d0dbd50922cfef51ec2decb99c1c72248ae0e3c1c1700fa3cf0676aa3f1f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-edge_order-current.json.xz": "9a3a2c2b244bebdbe13c5360c8a32ea1831881952a544063e54baf2921f2c0e6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-edge_order-event.json.xz": "67894578c1562addd00dbf44ec97a0b925638dfeb55d8c3438dc21118d74bd8b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-edge_order-reset.json.xz": "0031896cb65597c794e0c772a1e3843522424fce087fb02f2d38f712f2ab59c5",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-node_order-current.json.xz": "db67297b9888d4395700fc775e8b0dc70901a07b8dabd4376427c00274772a76",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-node_order-event.json.xz": "2f1a97f549abfde3ee3c59392c270a4a9c1bd62407924b8032f07fefcfc3050d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-node_order-reset.json.xz": "c632fcb1fd7848138d9cc9b9f7a329df02f82bb029023c0a64636cfdfecb1cb8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-reflect-current.json.xz": "a7a2b0084d8b445c5ac53ebbd3ec9fc0929248880c2c51a3d57aab8b52c8c942",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-reflect-event.json.xz": "d65096a78f9236d437a7ff6bcf063d440ab90604a20c52126dce92820c55ed19",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-reflect-reset.json.xz": "b0bad6fabf96b94d5c806c23ff0dda3a6da6228a9786b3a9d0d7fd6a329628e1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-relabel-current.json.xz": "a7e81c50565786f2b75ab0444cb4a7d2ef17843e9c069f9501fefa51ae789a56",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-relabel-event.json.xz": "a7236601f4ea05c097c37082e181361c13e817251fcbdd518b806fbb315be724",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-relabel-reset.json.xz": "b6880903c87792720154e83e6d1dac8e706419512e15679dfd225886163d2f20",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-rotate-current.json.xz": "ddaa8be439c5452bfeaf770ea92f618616e0a20f8b0e83aa5aafbd452944cb59",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-rotate-event.json.xz": "8c4044179484272baff2ead4f6c35905caafc3272718e5d280b01f5e511624f1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-rotate-reset.json.xz": "419388420cf024f5df89c036a6177c2e77855a5567567c6c02804141a611762a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-rotate_twice-current.json.xz": "60bd51696c111f4d8e699689ef1bd928d8c7fead3298193dc1b90f382217af77",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-rotate_twice-event.json.xz": "dde58132535e9e59920811ec7244aeec5a7fda798a70191f83021ddce41c38c4",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-rotate_twice-reset.json.xz": "c751e9692761060be706c74deeea38d6b7f1f82bdabab5a737115950e5740c54",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-signed-current.json.xz": "82dd38975f57b6233447a511421e045f8ad7a53b1ec31ff63eaa315572683143",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-signed-event.json.xz": "d020dacdc914950e03c85a7afefb051b0fef08ddc00cecb15181a372763af676",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariance-signed-reset.json.xz": "aad33f4870aa9b075a0543b978cbbcd0ec57205daa891e9269ae52c9e1f06d19",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovarianceInputs.json": "65854dd7e0036a37efb2025846645a8a1791aecd593f670f393b8d1f41379a21",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACICovariancePlan.md": "7216104f4e726d4c772d6699313305b45d91655a58c8a6df10b74f3b374c91f5",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACIResetChargeInputs.json": "7c8e7153cf63646b782835e9f5c902e97e1d048c86988214d7349ed245f5877e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACIReview.md": "ff2a05fa90a79209e90e1073d857f1b7bc3204fbe5292b0b37afdf15c9c504ff",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-ACISourceInputs.json": "57773a2d0ed4a2693f076373f1cb17a811087c21f165be3893e2f1dec87dd1d9"
}

LARGER_RUNTIME_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCI-event.json.xz": "e04f8f9a514f2d9cc320a692965f48e7e67e66fd7cc71c03c129b752374b6862",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCI-source.json.xz": "3a5933d68415fdecfe3fa1ecbc78d87a046dd13e5384e71f60ee80d5ef1ccbca",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-1.json.xz": "a6d2ef8a150e29c47c7b68ed34582364587339215791b1d4215ed3542b1fb85f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-10.json.xz": "a600a4ae474c4de61f745cee58a4156c317aa29ead4f375724652c55ca041965",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-2.json.xz": "d789828b0e1e22690575dab11b2f29cc69d891df1326978749e0f218b7efa242",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-3.json.xz": "6ac3361ee061916205eb84697968c04c7ebecdd740d107b385e3a1f8839ce755",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-4.json.xz": "5ccbe535c4706f976b71a677c1df8ac1203920ebc314d2f81656837e791376eb",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-5.json.xz": "a851af437765ca820f5fd5a37d67430e7fdb7e8c896ea2fb274355be1cbdf875",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-6.json.xz": "89c47dc7cb63347548d74097a4f2a81d7c4e19cc1b6d84dd1499d1d8c4d94594",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-7.json.xz": "ee09c32f51b6248a5b9178a1bfb198e330754d1f3791ee7515605cbbb0cdbe04",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-8.json.xz": "10dde41ca816309690d51217a1cca7a9f98b4c57a786657ae8e66d418d508442",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-9.json.xz": "72a67e7413d0cd4cc1eed8d8330cf70e171f835b9b4abda4ed9170107a8ce00e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-current-final.json.xz": "c31e6dbaf83db2c203a947f55fc547c6a0763d78fd7f4b9460b3149929556eb5",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-1.json.xz": "558e6ee621d6f5f94b3435982ac2b24275588871f347f34e6aa627b06812f972",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-10.json.xz": "0afe0b01b5fd3165466305f096ff30e2512de9d7a336334d9a972638e18d8043",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-2.json.xz": "865f5b712a3066e6d7227cbaa87cd7767a1268412c8669f58606c86a8b60c029",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-3.json.xz": "4c8db957fd35794f7678b98c1782553eda421cb847d569ee579045f905df4fc4",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-4.json.xz": "f550b709fc8c3fd4d337a4a1cb20fb3de16db52f2ba3313d42c5a151199c4610",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-5.json.xz": "7e4598aafa46063d65868dc94ec6508559ca2fae12a760b1c9b171bd1e60140f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-6.json.xz": "9ff8aba570b5777c059a1e0aa2f59fcb44d1d56c9186431ae934cbfb25a536f2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-7.json.xz": "dc20cd132f05e125c489c691e7473ec92f56db155019807f8bd7c239e58e3280",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-8.json.xz": "6c144ed91ae43c92be259cfa4c2e9ba70678f1cb455ce9ebb8a00f38623d1a8f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-9.json.xz": "ca08f4bb1b2633213bb4a3f82d673c817e7b5671a362a506583852cfe509ac73",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuation-reset-final.json.xz": "e2dc1d8a58c8090215a43628836ce233b0974becab64471afdc30fd7aaed60ca",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuationInputs.json": "5ac821188e30ea1df1d231b1290a6fc79b5dabf1bd540bcf5bb235cb7b48111e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuationPlan.md": "15b53dbf671d6ecb365aaddcec224bce2074bac013fe3cd40c1012f2b871fc27",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIContinuationReview.md": "3866c5a63ec5814120ac968a7a0fb997fa9b70ac5fbddb7b52fbac4fdb6e45d7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-combined-current.json.xz": "ad411331219293c970427eec4bc53154e0e0a229c71468b4407fc533c5a2578c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-combined-event.json.xz": "7411e84cd862d19efbdd99d25a72e72ef6c764495bea9d311bf9046f8932fba5",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-combined-reset.json.xz": "531f390e05eb5bc3bd746ea20d2e5add04cca453c794aa478f60346c1000dc1a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-edge_order-current.json.xz": "78780d9c2358a5ae1cab2f4f647a48159141643cbf3094ec5dc96ce0209c3453",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-edge_order-event.json.xz": "be9cd76efaf1bcb18087ffbcfe91e02c563720407c4674842d97af8316dc7b98",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-edge_order-reset.json.xz": "d067de33b13920faedaacbaae2116e632b019ac9c7480566f85cfae4e41f8707",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-node_order-current.json.xz": "7bff21586ba7647cea292985f91af8c403862b868af0239e461c1014cf8de417",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-node_order-event.json.xz": "554b754a4267fbd42059e172b3e657d48fa3368a77432de7e96a749ae6fdfbb5",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-node_order-reset.json.xz": "3199c0502f05a1b3cac1c4507101f78acbfb8f7c0217849980ec61cb6cabfbf0",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-reflect-current.json.xz": "910f46dfcefeb4677a7c93c4aed5dac3aef5e79b1eca66c856b0897b1da0f807",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-reflect-event.json.xz": "d8e7c31ef1a0fdb92ed558e79bfcc74e6675e8ee9e1bb46d077b595fc3007182",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-reflect-reset.json.xz": "88b0b7650a69c8a5aaaae5f8326f7d517f0322e1a7f37a7ec3bda6180b4cfbc4",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-relabel-current.json.xz": "85c95a907ae7b3e360e164cbe83f14f16bd3503aec25f82ebc6a3244a5a80352",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-relabel-event.json.xz": "645267d9581fe81983e8acc8c12feb6257572349ca8570f97a1de10f1e49abba",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-relabel-reset.json.xz": "28814a4fcef9bab2ce4d51446a33d569e9498d625cd97cc1abbf55d36422e05b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-rotate-current.json.xz": "910969ef7a747354a9b95263a83ec842c19c6113006121f86807b75bd5c35c2d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-rotate-event.json.xz": "8629423df0207cf6b578867d9955068edceb96411c462e5483b9a59296dcf807",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-rotate-reset.json.xz": "19b7ead0fb75ecdc9745e25083b9c51220f4972d3f5089b40f8e444386e757e2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-rotate_twice-current.json.xz": "db86a068016e2b37e913321d410b3fc44ba6751b6c3f23a78f32c1b7d7269a04",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-rotate_twice-event.json.xz": "816da02f2c541aeef4b24134e8f670fe55fd7e0acdad9b0744070781f4f16654",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-rotate_twice-reset.json.xz": "6080eded0b985cf5a841140a0eae196c1982946713e1ff39feda2c1f92450dbc",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-signed-current.json.xz": "73be84611fdec290cdcdbcc7adaa935764b3dad12d83574d8fb39ac7334a5b71",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-signed-event.json.xz": "7647ac98648c084e7e1c146fa7e416a700ce1dc75ad290a57712a5b3ce9d9679",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariance-signed-reset.json.xz": "f8a19fc2afd3d0b878ca7292f737f032019dceb4bfd52c91239359de0aa019fe",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovarianceInputs.json": "a4c4a3729719506f721c084398f969851407aac1c157f172f60e27a0baf82b56",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovariancePlan.md": "245347c9df2f7f35c8596811ea1fbcbde69a41bceec427e5759e2977dd348168",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCICovarianceReview.md": "ba6388b315500f93045459a4d5c75ca14fcb63f9cc6722b9f7bee3cfbd67581c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIInputs.json": "67a1e101626b240e6022d09e3bcab5e572235ff182118849712f6edf0a71e761",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIPlan.md": "dd5c0e09b3145550169599dd0675f157706f6ab64f5c78c744b2b243bcea61b6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-CCIReview.md": "dabc87f9698319bc698fe1c9c0363e82ff18431bedf88ba7051e5dc4feacb3aa",
    "implementation/phase-9-grcv4/verification/p984h_cci.py": "76ed26a106bc249009920693a7f050cc350af900315026d3ddbc3c09b9d40953",
    "implementation/phase-9-grcv4/verification/p984h_cci_continuation.py": "4121f3a2c93e781b8f9db76831adcb8a5d57c47425e04af613766ab43067089b",
    "implementation/phase-9-grcv4/verification/p984h_cci_covariance.py": "444721c3031b5439ac7bc3fbcf7e4fc3e29913c6322749b95578bf21bbcc9101",
    "implementation/phase-9-grcv4/verification/test_p984h_cci.py": "04ffab057f54cd869b6653278c41035cd3cc4083d246de0bc7277012e17ba4bf",
    "implementation/phase-9-grcv4/verification/test_p984h_cci_continuation.py": "b16aa635573400e1c9d1114e4e59b6ebfb9421a76f8b0d62a204d926c0d23c0d",
    "implementation/phase-9-grcv4/verification/test_p984h_cci_covariance.py": "6752364a085589b92662116fa1cad7dfa9395c94952a28e61e17d765e6352a5e",
    "implementation/phase-9-grcv4/verification/test_p984h_cci_surfaces.py": "99c4c97275be5df10ea68dd0679a986148185190946ab6ea5766ee5b52032c04"
}

LARGER_RUNTIME_COS_COVARIANCE_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-edge_order-event.json.xz": "3729e0f6073ad5d4d4a343fcd67bd7deae525eab26aeb5e0526cf4da14286e84",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-edge_order-ContinuationInputs.json": "4d4f237b17b8a32c7843af0c42ec83c0e0dc1a2216b033744938166ef37fc6a1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-edge_order-current-successor.json.xz": "6be62d7eefda01394ea181dfd4e29403524865e9b001a2fb64f74b08fc5192c2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-edge_order-reset-successor.json.xz": "f3b7f8f3dd635d115bed58f1f4a8c5796cb3d3b306472091c9832e9e8a74961d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-node_order-event.json.xz": "26011e3cf8f28d0aefd433e12a0144c39f57dbd1c40615c5be31874103440d73",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-node_order-ContinuationInputs.json": "ca85039fea88f6232a52de632ae7f1905207cc1efc4ffdb5563914fcaa0e1f75",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-node_order-current-successor.json.xz": "4350b0bc929ecb8e68db45c50d199f4d2ba57ec7d2939b06f7d1e0709598bf3e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-node_order-reset-successor.json.xz": "9ca45d9103f12776e29392b14371efcdc1e8d057bfb6d937c285a6d8d1fcd7d1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-relabel-event.json.xz": "58207a61f725707b83a36ded308b166884cd805b95a2feaae867dd0d24bafa57",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-relabel-ContinuationInputs.json": "eee2509dc16a3c8f22203dd014a0f81694ea7b591eb8a1e939a1f5b2e7addc47",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-relabel-current-successor.json.xz": "4ac5d04ae6fb0ee6d6d55abe7e79da7889f5ac59c494ef1d8634ad0eda09bdaa",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-relabel-reset-successor.json.xz": "0deab4cabaeffbfe31ded746c0fc9b3c8b676091a4595492ed8c6fb10cd00ecc",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-signed-event.json.xz": "4579cee45554bf5a9f97b265c83ebc8abecec581e0dd84e339af5756d818ad3b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-signed-ContinuationInputs.json": "a8696c22a1aea8897fe3cdd0c37f45afa5e823b8082d4be9892c2f5a3b62c1ad",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-signed-current-successor.json.xz": "56c74991c7b190e917980f2df8440e6b06f3481cb3a822cff238b0a5db2bd1dd",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-signed-reset-successor.json.xz": "21ff43129a9b40c1220ff2a73c5f102c91d350e44703497f2b045b3d5dbce71b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate-event.json.xz": "12d9cffe125b2532b7fc6ad9b27e67182127275d6ae3955bca9eafbd45aa95b0",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate-ContinuationInputs.json": "3f2562ead769108f5c1c8d3500061da3fc0b8ff301c4af832581c62d2428ace6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate-current-successor.json.xz": "196a49c429037b066d50d7e0a3edced982c9c58d7b211a8b859b98fd54fc39c7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate-reset-successor.json.xz": "37a219e1c15824fca9424b97b807ac047feb24744d25ceb3e01173b0ec2476b6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate_twice-event.json.xz": "8ccc6e340f0078b699d2aac0b54eab80e5b6dd0928413fcaaeba23c532a64d19",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate_twice-ContinuationInputs.json": "3b802898d3c987f005b980d55dc56c0207121f357078f9fa19f1c26829a9cd90",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate_twice-current-successor.json.xz": "8331cac20db0a01151f6a021bcd9d037a86a648199a4461e43724bb7520476f1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-rotate_twice-reset-successor.json.xz": "9c2bc3b8b499ff02e2db34d95a539ac0726f9e0e115cdefce5ee6f8e964d5839",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-reflect-current-successor.json.xz": "4792e92f7ccb9cd1994127a72623d5a10cdc064842974da53f4e1f48b14abefd",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-reflect-reset-successor.json.xz": "1b31491c03e463edc575d90d7e98652d58c9e74008eb6564e24dce42239e3ebb",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-reflect-event.json.xz": "2ba51ec443e2e5f3ded0cbd1dff41cb414c091c04a162539e9eeab84bd834321",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-reflect-ContinuationInputs.json": "929d43b262f7b9e62bdc2a224629b15cafb5cc968ced3aaa14b77393f3cc3b18",
    "implementation/phase-9-grcv4/verification/p984h_cos_covariance_transforms.py": "ae8f39749909882a88768212573124a4e1a336263c6c92fcf824ba526b3d67fe",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_covariance_transforms.py": "7ca4a8284ccbdf32bf97f8ab87f59f9e8ce67ccf233a5fec1165b69dc4e4162a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-all-mechanical.json.xz": "62e22a250b03f7ade5af2e93abd23674824c793422ba71c0061cf7d0d74712d6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-combined-current-successor.json.xz": "94a429add199d14401966de1eb115b05f5a99c3f3f72cd06cf285fb4601ff7f7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-combined-event.json.xz": "d1de55f32e6e2af2d1bfb02e74b2139174db703569315fca4fe831f77b2edf0b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariance-combined-reset-successor.json.xz": "2bc11fd11e9fe8c5bbe082e04a78236f75412ca0f2afa58313d52866aafdf179",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovarianceContinuationInputs.json": "243b2996248fb5c1a395745fad1687cafc78c550e6212c1eb306f7675a595f4a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovarianceInputs.json": "fadf62b844b82dc5657902a381f5ffb2a29fe244c33fec6027e23d4981c58d10",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovariancePlan.md": "a5d7e6f0e3b6c80e8ffce4d1204f07c36de9fbdcc0bfbb930a0221a3499eb4af",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSCovarianceReview.md": "25d51f7b315ca194b617267ba4412d4a54e7e4fc1e07b5f34eacdb4932ec5c40",
    "implementation/phase-9-grcv4/verification/p984h_cos_covariance.py": "c04ae175b9c324b769202ad7d429d597ecd841d224dafad5e24da2ef6c1f10ad",
    "implementation/phase-9-grcv4/verification/p984h_cos_covariance_continuation.py": "083636c82d1e771faa567d8ee69dc9b71936f3b744349ef1b5abdfd38d134dc6",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_covariance.py": "0da1636c98248ecaf2434610727892b3f3d399806ac60b2b93077e85f9316f9f",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_covariance_continuation.py": "9a8baf0d54cf2b4e4c7f9b81ce3b238a41124ae7f8be04aaec065c68115c8b78"
}

LARGER_RUNTIME_COS_CONTINUATION_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984h_cos_continuation.py": "c4fa19e52783a43f29edbed3f5ff93aadcd960281c821e676f160467306a224d",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_continuation.py": "a892c5d5c0547c132ed3cc411625dc82d93d93788d9eadb5bfe531e7103e2f79",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuationInputs.json": "8d2b2d6869321ff462f2aca6038d281d6383b432767de019ae84290df0a1d3f6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuationPlan.md": "9e15dba4b57932b11d4179d1ff48547e4a203d52aa1def1d8bf9dd888450f557",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuationReview.md": "cea40c0ca021736f4f25293564043befd8a03cf565acd9ed7f4b6a09b74213f3",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-1.json.xz": "aac8fe517fa1a3269c8df26cc6cf1b2a62808f2f475a04a37ea900351e11aceb",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-2.json.xz": "771c42177f13647073841afeb8fb4144d7e00754e80c5918b48fb4d58829f89c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-3.json.xz": "a76ad1768ccf29cc2adde2971c5448d7015f3ce6aceb52a1236fbf63fa34889c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-4.json.xz": "4d0f878348da8fbdfcd793c2bb408a2c71ad58e699e9f9093e34d2561b13b605",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-5.json.xz": "6c2ee0d975923d1314c58f92ef26c6937706b7ca5dc9e69e131c25cf7607ff79",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-6.json.xz": "3ef55463df87731b625d002e32f08097ba5194b152f76ec6a998dc21e5262f1a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-7.json.xz": "a6fe2c28be6298d14a5106934ae9aa2f308bf5e00521a5819c5d0663104f3411",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-8.json.xz": "40bf97dd42153cd5dec133484f0d4f46c83f637b3ef17febdab7686542840b61",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-9.json.xz": "78900df8eac2baf3a9ce9086beb56e31be660aebecf8c6997fd0c358a0238c97",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-10.json.xz": "2967e331fe0c4c5804acbff33bcf13a978c1bbfc1f429cb9b6751f7c4f75236a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-current-final.json.xz": "b0014e538954eef38e50b8eb661d74240d26c7c4c9c9d774368bb420eb492c02",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-1.json.xz": "1f36b82bfb14831ba0f10d7298a2a1b64b6624cf69e0934c64736dce1203917f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-2.json.xz": "c5b1f35ca6bbcb6d18e0b958158a3949a27d5b4b234d9cd202dcf2df6f682774",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-3.json.xz": "d0f80f4577791b7cae05d7a47fcb1d0b9b1d6d715929ab8f9e422515e9d7376a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-4.json.xz": "da5d1b60a1a274402ad12fb10a30a2fb60ecc2dd348f917a94c95a0e1c321e3e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-5.json.xz": "0ecbb3636489a3972d7a35f7a1bd6856eac7a6bc38598def2c6de6e1615815fc",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-6.json.xz": "710626878a41f713b1a4aca4c2b9462af706dbc3d24202ba1ccc44fc9c1fc80b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-7.json.xz": "5471ef3e75d7d0f1cb74d09e66634552d1ffa6039c112442d8de18966da5a43d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-8.json.xz": "e9e46645d25462e34e6341bd20ad6ca55c1834bbfe782335e47ec878392d16be",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-9.json.xz": "4fa124edd53b2308461e30c28aff93d8f3de975f2e03f71ba34f6738b8776181",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-10.json.xz": "a7f72f095cedfae2a58be6df5d427b2809f1c9e4c46f5c6df0d50b63352ada21",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSContinuation-reset-final.json.xz": "45ddc6c65905cebfc814027a5a045298212a700a5d42149c5fe14912a4b27b29"
}

LARGER_RUNTIME_COS_EVENT_SUCCESSOR_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984h_cos_event_successor.py": "a894879e6cbafeb8ca6be3aa141e5cf8844b230aaa8e935e8b1e679f8e84baf3",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_event_successor.py": "ac17afba53573f7e3b7317a76712973f1ac27f3d5fdc94c57c15e80043002210",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSEventSuccessor.md": "e180bb0927d0944d640884d7fba93fe56feab4764bc066e3327650b63d42c7a8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSEventSuccessorInputs.json": "760c8a5321b31e4dd74a54ff407b36d1cdfcde43219b8797f456be4a2bee60fd",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSEventSuccessor.json.xz": "ad5eae5df68cf2e5a877a4f5f3aced0681349d9d5c4d0f10b9d70a16d23c0273",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSEventSuccessorReview.md": "e126010e0f4ebcba2f5c46fbeed223f00735c393c259e3192b4d5f81ee4fd6b9"
}

LARGER_RUNTIME_COS_NATIVE_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984h_cos_native.py": "c9a6c8aceeda4b2c4d62f7cf187a3654cbffdc84c10f57bf69167f59fd895a8b",
    "implementation/phase-9-grcv4/verification/p984h_cos_native_compact.py": "366330ba65f441a61bd835458fac687d774b38533acd2a136d4b2f34ab224375",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_native.py": "44dca9feac554172b2668daca14a7cc3e01118d1d9dc1d45ff825e725be9f083",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_native_pressure.py": "cee8919de0e9fba56409f3c240d7cea7c545125bc7c708f4a2aac3de316b09a6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSNativePlan.md": "45af24edf3590cb4aaafb0c91f0c6cc6ab884f4cdca84ea79c290ce58d5f08d3",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSNativeReview.md": "3997226270bf34d2b403f80ec9585212ce276e59b42964e0993034d6586216af",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSNativeInputs.json": "e7b7412c8365b6d191e0e2824dd48bbd040a775d1f4017d873c824d263b5e28e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSNative-prefix.json.xz": "f94d4c22e33d84ec4a2a4cc8906d2a2e6be9fd4fdc355015fef9b526da776366"
}
LARGER_RUNTIME_COS_PERFORMANCE_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984h_cos_read_profile.py": "b0d238d812d00f255171547cd3891b3b9991d0319ff08fbef0927b46d8297ada",
    "implementation/phase-9-grcv4/verification/p984h_cos_solve_reuse.py": "02d3910ad64c14ff11f9457aa753451dd7222395bd4900533baada728901add0",
    "implementation/phase-9-grcv4/verification/p984h_pre_solve_reuse_sources.py": "6d6835ef34194ff2701bdefa4b3617ad05f9a32b5a0316a46106457f8995caba",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSReadProfile.json.xz": "1f156e0908aece3ada4270c0d6318cb32c2f6239252909402a82859d1c955261",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSSolveReuse.json.xz": "560defe685be0f4355e4cfe0e2941be2ba933d712c24977b5a623dbf0cf4292b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSPerformance.md": "281961bee7dfc198a501d2e746d02d091121c7f64548375db6b40acdb73c5dec",
    "implementation/phase-9-grcv4/verification/p984h_cos_scalar_reuse.py": "42e993702cf13c792468b53e159309d0a0faeab0e05bce5347cd725c8d8923a6",
    "implementation/phase-9-grcv4/verification/p984h_cos_kernel_profile.py": "132a61b568e420b93a199b941a941adb340e913475bfd0f5dcff9786bf008ff3",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSScalarReuse.json.xz": "00b0245298e332860b54d209689cdc17e9cb882cfc587b80136bced51e39cbd2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSKernelProfile.json.xz": "e4eee02846b1aa87f00f68badc213363d9bcde2b7a4dfbdb2cde83c796268733",
    "implementation/phase-9-grcv4/verification/p984h_cos_dyadic_rounding.py": "94d73bf79c8426f512c6b7e2b9316cec7bbe7e8afc3c5c4fec96cca31e93fe20",
    "implementation/phase-9-grcv4/verification/p984h_cos_dyadic_step.py": "c9f5b75b722707b95d4b4d0316c2825eb89912bd5b6c6d0f9f7c92fafd96b660",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_dyadic.py": "01edde6d23ab1c59811fe9a6e61678f6ea26766feba6f31cad63b6af05edec78",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSDyadicRounding.json.xz": "83680a3cca4c636c0716ebc4a354052d916dc5a4b9384ae79ecd523463294668",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSDyadicStep.json.xz": "0655afbe1bbccdd43c6f26cfaa9523dcc480a57cb59014e8f6ca67fd5e29dbfc",
    "implementation/phase-9-grcv4/tranche-8/kernel-predecessors/grc_v4_certification-scalar-reuse.py.xz": "6dc00b344ddbbfd15bf404b1597de8797d418770d3acaef22b3dd509fef52905",
    "implementation/phase-9-grcv4/tranche-8/kernel-predecessors/grc-v4-numerical-policy-scalar-reuse.md.xz": "718b3ee30829f56dbb3d00c5c97887b64095071c1eb4186989982c1c6a388618"
}

LARGER_RUNTIME_COS_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984h_cos.py": "38d509e3ef87170ef9260b6932e6353b344490fd43d8577e53081d10045b7d08",
    "implementation/phase-9-grcv4/verification/test_p984h_cos.py": "fe0a15f17e511c3bb1316fe32cbcaf69d14b98229e374d1d635d1972c89e3f70",
    "implementation/phase-9-grcv4/verification/test_p984h_cos_surfaces.py": "7f273c40c26ec9bf81deeb363ff2e5cd42cde69d0aad64282dc4889fa7da1bf0",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSPlan.md": "0f807d49d1a1f9efe9e90bacb4dfd2cb8f16a88f912e1032453dd0bb048f17cc",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSReview.md": "933e912a261bab94c7886f3b9f07961494e15c1a6b3839470900bbeb03ab52c0",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSInputs.json": "5a4376f25b34ed58d12345eca716009bcc5e7942e8fb4ce6a4df99a8797f5108",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4h-COSOracle.json.xz": "73e5149c32fa417f5ea141ed354ffef84cc99f58225b67fcfded9786f426b7b4"
}

LARGER_APC_NATIVE_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_apc_native.py": "1e594aad85c58eea2776d1a610c57e667648c2e6c7e98ef590191eab614be8e8",
    "implementation/phase-9-grcv4/verification/test_p984g_apc_native.py": "e92a93ef37835a1b46e05bed49ccbe0a662e847cc15feb768680701ee5377d7f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNativePlan.md": "1248649340a5a6b49242ee7e78ab9c9579830acdfba8814bf7f88f0ca3dc8149",
    "implementation/phase-9-grcv4/verification/p984g_apc_native_targets.py": "af4b79061ebda0945a804c961db1ef0cb29a2add99c20a1c36a1d98625d608a2",
    "implementation/phase-9-grcv4/verification/test_p984g_apc_native_targets.py": "d1768d798e87bdef4ad8428afe1f1127eea35ee7ca56eac0dbe9e66a046e1e5b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNativeTargetPlan.md": "5e6ddb88b6046d2c71cfdb27f28c9741ffacc5bf645492e41b291dfdb6d3e084",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNative.md": "6c5071b280fcb75d80ee38991a9cea09f22625b043d2141b6dffaf38d558cba7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNativeResults.json": "5bc33747e81512b977debc30967e8c04b06c704782923058e31d0095299b4bf6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNative/source-current.json.xz": "769fd740ef872ef1cc8409f8e9129b093fc6a34dd7090e8e8e091e323dcf6342",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNative/source-reset.json.xz": "d12038b61518dca02aecf2f6874fc774fa4f088c8080fd7ca17af648123dac1d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNativeTargets/target-current.json.xz": "d98c4175a2ff6ed0a68a8a8feee1358c47ea17c75ed182ff13f361a75206e78f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNativeTargets/target-reset.json.xz": "02992d6603b625fd443f15c0d85ea23d88ca8dfc97aced52d4eb5813e4d9c62d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNative/target-current.json.xz": "4524aea2afd0a5d53ca4c17f6cbcb509a4374e8c7519cf182ee7a2549aa899ab",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCNative/target-reset.json.xz": "11542b0e9b2c9944119a0721234e36c4d20f8d9bbe0139a0717f8e4612d40e4e"
}

LARGER_APC_HARDENING_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_apc_hardening.py": "d3444dab55701e0df2c4565882e3b7d9a4190ab9824249dbbecfc55b182e5027",
    "implementation/phase-9-grcv4/verification/test_p984g_apc_hardening.py": "a6295342ea1606228c4b28b3a4c0a953d2c92095c4d1c038725f3c0a18a27d27",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCHardeningPlan.md": "4c0e22841be8833913a1f8a5a9edf71ee60ebe209cd6c8ed0542abbe0a75a148",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCHardening.md": "1e40a1f375fd039b18db6ebba66b1d66a2868870d84935f248dc99d40bc1d93f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCHardeningResults.json.xz": "4eb77d6c65a30f95d53313d9ba05272438dcb2aba995804bdc3c723d47fa2bc7"
}

LARGER_APC_STAGED_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_apc_staged.py": "06371f464dfd0bcf22087bf8e6c14d9c593a1f690116a402e94ed9acb364c182",
    "implementation/phase-9-grcv4/verification/test_p984g_apc_staged.py": "0b681cadaa59f07869ac4502613e202675ffe1b24608b29ea0e73c383e58ab94",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCStagedPlan.md": "1e15755ebedad8976aa6af8eefb95967af7f132634bb81f8964244c4958e6df9",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCStaged.md": "5299a933ee87e18027d6ff221cd3a6abe023ab5b3681bfa9b6c67966c3e9c3d8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCStagedResults.json.xz": "17d33daf98c19fa4f1e67b4e89f9a097c516016fdf624c34c0cc747787f65da3"
}

LARGER_APC_FEASIBILITY_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_apc_feasibility.py": "b39607a5680cdbbfdfdb8ab5442a3256d64b82b45a93acb54ea02368205df68e",
    "implementation/phase-9-grcv4/verification/test_p984g_apc_feasibility.py": "ae7f8ccde167cc81ca8bb61d4f7dd9b1b59b5b294cf57472ae0f1056bfc8b3a3",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCFeasibilityPlan.md": "db84eff81835994671d218db784f55ea4c4fe628edfd790b3965af4ce021b702",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCFeasibility.md": "b84079f6722251bba76eb2fb139122417b702d7de1ac7b156176f9b144cfbb80",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCFeasibilityResults.json.xz": "ce0d8df18806e5d3930c6412cd853291adde26a9a97de0034d215c34aa7eb3b7"
}

LARGER_APC_RESEARCH_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_apc_investigation.py": "b2e54c9b8093a9126470b0fae5ebd71280c65a57a514330e57000825c469e1d1",
    "implementation/phase-9-grcv4/verification/test_p984g_apc_investigation.py": "4eed2e789cd6e7ffdde117c176fbb651f916ad77660f88d2695cd30d0fa5c839",
    "implementation/phase-9-grcv4/verification/test_p984g_apc_surfaces.py": "a87fffd4d34f6b8a2f2afe305df20159820283a8b510b6b44c6711e1cf974efd",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCInvestigation.md": "9d865d5491ef35a0b460a7037f0f7701ea0c70a87a42fbc4a5166983f723d0ba",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCInvestigationPlan.md": "c6e65f569ad9b3d83b91b8c140a96c73430be92fc32b2c5ceb4cb2edbc9301b4",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-APCInvestigationResults.json": "5c1201b1135920cea1a5b0bce7dfdc46032cfafcaaa522f45527b9d70a0799c3"
}

LARGER_ACI_SUCCESSOR_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_pre_aci_residual_sources.py": "71323c0db80f24375d87f8e26822cef3aedbf5502e10b4c4ab804be05ba399bb",
    "implementation/phase-9-grcv4/verification/p984g_aci_native_successor.py": "50b9eec43ea97b10bf3de16a060924a883f3797e534dd65e0d4c60279b21c8b0",
    "implementation/phase-9-grcv4/verification/p984g_aci_native_successor_check.py": "078a34de1ac47e1eafbec070c5925cb45553a2987d2a913f0ba74cdbfbe75a8a",
    "implementation/phase-9-grcv4/verification/test_p984g_aci_native_successor.py": "9e6197ec37c5d6e589c22fcbcf17f73627c24a454ae64293dbe905c00fe888f7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeSuccessorPlan.md": "9c6ad8120ea8835e50c5a03a56fa62e6fb5b06fa6ab5e2f7ecdcf549a8b45506",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeSuccessor.md": "5971110714a0c5f830a450f7d2897032842ff70d07681c28951204a5773c7940",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeSuccessorResults.json": "dac0903519e9b842ce16f37e94cbff3d09f38ab4dd8fe8ae9880851e39e06b12",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeSuccessor/source-current.json.xz": "9039dd93d7f70bc79317f4d5c7ca129ed2f31332a52db7794c5391007a343626",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeSuccessor/source-reset.json.xz": "bd2db8d8c4922827730ca50f40dbd08cce0af2ab2b7986e65e6bd8b329b0cb95",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeSuccessor/target-current.json.xz": "e99728d142b6e5cc3be0488068e7ddf4877dd4d7775b40da48e21d2566259bf2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeSuccessor/target-reset.json.xz": "515c4ac0ea8ee92a80050df12fb04b07e96f2c0a034818326c59fdd855425348",
    "tests/models/test_grc_v4_ci_residual_policy.py": "c2bdde04913e6ec39b60f18f6cf90e3c24f0866021bc68ab8902420c8298e968"
}

LARGER_ACI_NATIVE_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_aci_native.py": "dcb67b4e3477e89f76ac9c0342150422ed47a547e6c8790e0bf94aa762065106",
    "implementation/phase-9-grcv4/verification/p984g_aci_native_check.py": "d5173b435cfb8f2f29fe73d00e8687ce496209c6b5fe1936c286a704f925c4a3",
    "implementation/phase-9-grcv4/verification/test_p984g_aci_native.py": "66426a6864d282fbf35ad81b04582e9d8eac7f826f21d00c0d313fa90bb51d15",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativePlan.md": "7ba5b2dddf358507e9d3259b46a35fdff845e99621fb902e585182febd625e2d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINativeResults.json": "4bd971114c0f3d9b21130f14b33c9bf8296d3fe95bd128fd2daa4d7a3d8115b8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINative.md": "af69c628a18043426938dbf7bed2c220ce8cc2998668014b53f17c7774056a47",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACINative/source-current.json.xz": "0ca3b8741aad62b527ff785dd855c1a3a1c10e2adfe3bef967c0bc4e77371794"
}

LARGER_ACI_STAGED_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_aci_staged.py": "9deb9304333f49e13a04b363d0c24443044b4df8521f908f6abc579e7823a9b4",
    "implementation/phase-9-grcv4/verification/test_p984g_aci_staged.py": "19746d14e28641e917269538e6fe90bff5ac5ad80a0fce7f335c793a478365b2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIStagedPlan.md": "2cb3b2c606103b567650eb388debfbcd745df774c2154107eb63ddadf45e9291",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIStaged.md": "491192f320c14f7e50dcf504f7ea30fa95632c7755b81c6067b9b118946d187e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIStagedResults.json.xz": "b3ce5cd335921033cb5fadad3c2724930923abb54215e7e977c525d18be3011a"
}

LARGER_ACI_FEASIBILITY_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_aci_feasibility.py": "28bfe6a9543bb67e13b5aef534577dac178e976548f2d22b15c7db00ebf29549",
    "implementation/phase-9-grcv4/verification/test_p984g_aci_feasibility.py": "d0441b3c9e60f18ed4d030a6754ad50ca0f9665e9b69d47c6f09c6a985eb50f8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIFeasibilityPlan.md": "485cacdb747816468c2c55a2dd4a6881856d0c56260660da99713422ddd7f253",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIFeasibility.md": "9fad6e8b370c5baba01323852d78fc6acb2b71efdeaade28c95df5723ff02f85",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIFeasibilityResults.json": "5892c2c5a9cf2f15b9ffe4a22d6fbe7fd080544f2b174aae93a1be3e340d8e4f"
}

LARGER_ACI_RESEARCH_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_aci_investigation.py": "31b5c76b3d0b9199f25d8ce927ae455618a1baf12ccab0f70bbd8bff518a0993",
    "implementation/phase-9-grcv4/verification/test_p984g_aci_investigation.py": "ec6a1c2d6b8537a1bc9e8170bc39a1a2fdebabb0507ece0da0b2ec18df7db81d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIInvestigation.md": "5fc3f8aea6b60f9e3057238efdb2e8a000f2668807b19d6c30900349a3d57581",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-ACIInvestigationResults.json": "4a8bc6f7c3619e7b36177c622b0e76ba4c942c632df0f6575c293b1787b90b79",
    "implementation/phase-9-grcv4/verification/test_p984g_aci_surfaces.py": "e9b298cbaa998574d339e89e843c9145c229647099fbe4e8759adba8814fc269"
}

LARGER_CCI_NATIVE_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_cci_closure.py": "e3e20404a3beb4e3234e9449f50818d3cd224d6a39a8b71f53c3e61912e781eb",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIClosurePlan.md": "f0a6ee755e24fd010f5e8fe78309b89e5f4eeb0bed485449f4b8cbe9fe44b503",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIClosureResults.json": "afa3842bde3bafbd2e4eb67a90522b40a86434644f6fd6e8bff6326d6be51f2e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIClosure.md": "70b1a26d75c3122cda4a0f3d3810828f4b14b7f917d18b41073f5705465f5861",
    "implementation/phase-9-grcv4/verification/p984g_cci_closure_check.py": "2d36804228de800f528eb1104c355aac02a842c1b3771fc5e13528c216bfef3b",
    "implementation/phase-9-grcv4/verification/test_p984g_cci_closure.py": "1ac96c47174fcb30725ed0aa3852e2c9c2af0471867d7a1f63f4bf55a44cd957",
    "implementation/phase-9-grcv4/verification/p984g_pre_ci_interval_sources.py": "7d8faca54f58405265b3f1ef82703742410ffa8f0f256f6deef5b94e329f7995",
    "implementation/phase-9-grcv4/verification/p984g_cci_native.py": "67752c22f3f878a2e6fd88819620a4b519258948ebe6af07a19e30a6513a3fa1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCINativePlan.md": "1af932ec4b7a184329b7447415516ef8826fdb9a19405397b13f4e509b65c0d6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCINativeProbe.json": "2bbdb7835ebc650d7a78b70720dcfe060de58d9d31255524de0765621afb278b",
    "implementation/phase-9-grcv4/verification/p984g_cci_native_admission.py": "7b07a97ce529da8226121a4707697892c6f66b0704c63f82ba0bbb60a346ba31",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCINativeCertificate.json": "4766136e554c4aa340fee0bb2bac27b2f93fb695db0298b188ee3fad55d1848c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIClosure/source-current.json.xz": "9868cb981bf35675fb20687183795702e34d88237a579a15246030bd9afffc34",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIClosure/source-reset.json.xz": "723e825d5c9940364e4c5f721cc3861b151b291bbb1cb1925f286df8067f355d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIClosure/target-current.json.xz": "905efd6a9972e24d0e60bbd9c84c1bbe7f1e74efcebab90fddc4e1396ff43196",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIClosure/target-reset.json.xz": "61928f0e01f9b4faa3a7e8af5523f7e18b44eea4890743bf7301ab063146fe5a"
}

LARGER_CCI_FEASIBILITY_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_cci_feasibility.py": "5194f1b61e892667fde22ff9984844da3384dd016327da300072ff5c0baeebbc",
    "implementation/phase-9-grcv4/verification/test_p984g_cci_feasibility.py": "ae79fb01b87f095e279f3b6c75081c9e78e209795cc94edd97773d3d78eb3ae5",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIFeasibilityPlan.md": "8bb8a75b389f795a075d07369dd43f7d235f0ede98e0b46c1cbf4411dfd8aeb7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIFeasibility.md": "4dd14f5d26bbc32c0818ac0c92e6e111090edf383bd70710bce5f3237c61ae31",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIFeasibilityResults.json": "aed82b3aa38ddc67297d3d1b2f747810b26c82df6ccf839845f5379b9f136773"
}

LARGER_CCI_STAGED_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_cci_staged.py": "579268ad06f6fadea0f041c076a1494c15c64a89e2c8c12c09db1c4ac24aea6d",
    "implementation/phase-9-grcv4/verification/test_p984g_cci_staged.py": "ebb20fc152a192e7e7687bbe7503ae14cd9676337c10b62ed6d8bf542b56141d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIStagedPlan.md": "8f87961a84596b34fc51a72c857ff8febbadfd1b2095de2c271523fcbaa92753",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIStagedReview.md": "b0a94e381d662daf9f8d3d4cb8cc442912e247117b4f7137ee8dc0e7b1c50294",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIStagedResults.json": "1c1b37ab39de41cd12a7f1fc434fb45de8739abdc7d90401afc307fddb72ea78",
    "implementation/phase-9-grcv4/verification/p984g_cci_continuation.py": "2cfc74d2502befcc21e4248195b956deacef1f75822ee605e007c7366e70878b",
    "implementation/phase-9-grcv4/verification/test_p984g_cci_continuation.py": "73d99fe16fcf3bfc715b4f8a22836c762164ed0f4f39281894da54ad9ec11ddb",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIContinuationBounds.json": "01df5c1efaf668bb534231095345bc711e6bc549e5ea3b883739e73fc375bf02",
    "implementation/phase-9-grcv4/verification/test_p984g_cci_staged_controls.py": "cea0bf999c3fd47ee42f50805ca91c59f37c479e7d5e8117822181980ad83810",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIStaged/source-current.json": "3534811a7422164b4bfa44f772ab57437e66c149d9fd995b88bcff0affaae685",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIStaged/source-reset.json": "dcb2cc399f74f7141928982dc70392899bc29565ae356215b1cc96fd4ad59c28",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIStaged/target-current.json": "7bf3d5d05a0d7c9dead11eee3c6b87588bd2c031b36edfe83f40db63f164319e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIStaged/target-reset.json": "d36b3c6dc7bb78a2819a40829a60654715a37825ed06b7857d6d216283c390b4"
}

LARGER_CCI_RESEARCH_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_cci_investigation.py": "b7ab1106122b5cd6463edce6e66740c73976cc2e06116c3555896b7cf1a013c8",
    "implementation/phase-9-grcv4/verification/test_p984g_cci_investigation.py": "7d3d0769d0d9bc33cd3382e225a9a3fdbc2c1ae022696aa60f22a0994de02825",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIInvestigationPlan.md": "dd4937bf06c2547b298fb2de7e5b57ad776691a2a1441e03683c729a4bf51320",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIInvestigation.md": "b2991fb5512b7c9db2e26eab230d69f0c9991c33436b834a8eb8a1670581265e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-CCIInvestigationResults.json": "4cddc0df1b18132df92c181f93a508be9f0dd148b0b97c73cf373ef519e018f0"
}

# Populated with the exact completed successor records, never live discovery.
LARGER_COS_NATIVE_SOURCES = {
    "implementation/phase-9-grcv4/verification/p984g_cos_native.py": "f45248934786ea7c0a8d1d068e0d7377df2ac142810f52a7eb1a886b7c0e5e5d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNativePlan.md": "b4171105c4dc24afe42c67a4caaaeeb4f451928aa45eaa09af4ce41374b2fe4e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNativeReview.md": "944882be5959c41ca022125e2f7232ca28ffc06372648ec87f4d3fb1b9d18e32",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNativeInputs.json": "1ace3520005e441e8972ec4f7100ebab3683d662c0343b5e155167c7c9a71d02",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNativeResults.json": "68d61125cd69db6a2a2a8766fa015f221db8f8e92ac92b077663fbca0fad55ff",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNative/source-current.json": "b87740777122259ec3e9c05d08e066e521cd7c22b2f71ce73b5ecbf4028f91af",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNative/source-reset.json": "a79cf7134db57de9b9784f11d2bd61f6c37952840e15119edb1ff1c7544f8f8e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNative/target-current.json": "94961fbff7c660e095befd13da742364aaef078ccd6cc9a4fbe6b58813bc8929",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4g-COSNative/target-reset.json": "08619442900f2427a1bfe54e457f7df7a62c6d46c3ffb3417ab0b0ac2a8af3a3"
}


@contextmanager
def historical_larger_sources():
    """Retain old scientific checks against their exact pre-integration sources.

    Only src/ bindings resolve from the named Git subject. Checkers, equations,
    tests and original result digests remain unchanged; no current runtime credit
    follows from this historical source adapter.
    """
    import p984g_cos as preflight
    import p984g_cos_bounds as bounds
    revision = '5b9836358af2873e524e6ceae7256639e8a6bbce'
    def bound_builder(original):
        def build():
            value = original()
            for row in value['source_bindings']:
                if row['path'].startswith('src/'):
                    row['sha256'] = hashlib.sha256(git(ROOT, 'show', revision+':'+row['path'])).hexdigest()
            return preflight.seal(value)
        return build
    with LOCK, patch.object(preflight, 'make_manifest', bound_builder(preflight.make_manifest)), \
            patch.object(bounds, 'make_manifest', bound_builder(bounds.make_manifest)):
        yield

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
            boundary_pins.update(LARGER_COS_NATIVE_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_COS_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_CCI_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_ACI_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_COS_NATIVE_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_COS_PERFORMANCE_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_COS_EVENT_SUCCESSOR_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_COS_CONTINUATION_SOURCES)
            boundary_pins.update(LARGER_RUNTIME_COS_COVARIANCE_SOURCES)
            boundary_pins.update(LARGER_CCI_RESEARCH_SOURCES)
            boundary_pins.update(LARGER_CCI_STAGED_SOURCES)
            boundary_pins.update(LARGER_CCI_FEASIBILITY_SOURCES)
            boundary_pins.update(LARGER_CCI_NATIVE_SOURCES)
            boundary_pins.update(LARGER_ACI_RESEARCH_SOURCES)
            boundary_pins.update(LARGER_ACI_FEASIBILITY_SOURCES)
            boundary_pins.update(LARGER_ACI_STAGED_SOURCES)
            boundary_pins.update(LARGER_ACI_NATIVE_SOURCES)
            boundary_pins.update(LARGER_ACI_SUCCESSOR_SOURCES)
            boundary_pins.update(LARGER_APC_RESEARCH_SOURCES)
            boundary_pins.update(LARGER_APC_FEASIBILITY_SOURCES)
            boundary_pins.update(LARGER_APC_STAGED_SOURCES)
            boundary_pins.update(LARGER_APC_HARDENING_SOURCES)
            boundary_pins.update(LARGER_APC_NATIVE_SOURCES)
            boundary_pins.update(COVARIANCE_CCI_SOURCES)
            boundary_pins.update(COVARIANCE_ACI_SOURCES)
            boundary_pins.update(COVARIANCE_APC_SOURCES)
            if name in boundary_pins:
                require(not historical, "preregistration is not a historical acceptance")
                frozen = self.current_bytes(name)
                require(hashlib.sha256(frozen).hexdigest() == boundary_pins[name], "boundary preregistration/mechanical source drift")
                self.values[name] = frozen
                self.refs[name] = dict(path=name, sha256=boundary_pins[name], revision=None,
                    basis=("pinned_A_CI_8_4h_not_acceptance" if name in LARGER_RUNTIME_ACI_SOURCES else
                        "pinned_C_CI_large_event_integration_not_acceptance" if name in LARGER_RUNTIME_CCI_SOURCES else
                        "pinned_partial_larger_covariance_not_acceptance" if name in LARGER_RUNTIME_COS_COVARIANCE_SOURCES else
                        "pinned_detached_continuation_not_covariance_or_acceptance" if name in LARGER_RUNTIME_COS_CONTINUATION_SOURCES else
                        "pinned_event_successor_not_target_horizon_or_acceptance" if name in LARGER_RUNTIME_COS_EVENT_SUCCESSOR_SOURCES else
                        "pinned_read_performance_not_event_or_acceptance" if name in LARGER_RUNTIME_COS_PERFORMANCE_SOURCES else
                        "pinned_native_segments_separate_success_and_timeout" if name in LARGER_RUNTIME_COS_NATIVE_SOURCES else
                        "pinned_A_PC_whole_chart_research_not_native" if name in LARGER_APC_RESEARCH_SOURCES else
                        "pinned_A_CI_accepted_corrected_native_prerequisites" if name in LARGER_ACI_SUCCESSOR_SOURCES else
                        "pinned_A_CI_native_attempt_not_closure" if name in LARGER_ACI_NATIVE_SOURCES else
                        "pinned_A_CI_staged_joint_oracle_not_native" if name in LARGER_ACI_STAGED_SOURCES else
                        "pinned_A_CI_interval_input_feasibility_not_native" if name in LARGER_ACI_FEASIBILITY_SOURCES else
                        "pinned_A_CI_exact_real_investigation_not_native" if name in LARGER_ACI_RESEARCH_SOURCES else
                        "pinned_C_CI_native_prerequisites_scoped_acceptance" if name in LARGER_CCI_NATIVE_SOURCES else
                        "pinned_C_CI_source_allocation_feasibility_not_native_admission" if name in LARGER_CCI_FEASIBILITY_SOURCES else
                        "pinned_C_CI_staged_joint_bridge_not_native_stopping" if name in LARGER_CCI_STAGED_SOURCES else
                        "pinned_C_CI_exact_real_investigation_not_native" if name in LARGER_CCI_RESEARCH_SOURCES else
                        "pinned_C_OS_native_prerequisites_scoped_acceptance" if name in LARGER_COS_NATIVE_SOURCES else
                        "pinned_larger_pointwise_bounds_not_native_admission" if name in LARGER_COS_BOUNDS_SOURCES else
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
    next(r for r in children if r["work_id"] == "P9-8.4h").update(status="native_prefix_event_timeout_performance_first", accepted=False)
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
                      larger_runtime=[larger_cos_runtime_view(sources), *([larger_cci_runtime_view(sources)] if LARGER_RUNTIME_CCI_SOURCES else []),
                                      *([larger_aci_runtime_view(sources)] if LARGER_RUNTIME_ACI_SOURCES else [])],
                      required_cells=322, accepted_cells=len(covered), pending_cells=len(cells) - len(covered),
                      executed_pending_cells=len(pending_cells),
                      aggregate_closed=False, other_vector_cells=60, larger_history_cells=20),
        scientific_claim_mapping=mapping,
        verification=dict(level="pinned_sources_and_retained_structure", native_trajectories_rerun=False,
                          pre_solve_reuse_numerical_sources='718f95be_not_current_execution',
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
    transition. Runtime bindings resolve from the exact pre-integration Git
    tree, not the newer numerical-policy implementation. Scientific fields
    still pass through the unchanged validator; no current-runtime credit.
    """
    require(retained==checker.contract.seal(retained),'original mechanical digest drift')
    adapted=deepcopy(retained)
    row=next(r for r in adapted['source_bindings'] if r['path']=='docs/reference/EvidenceStorage.md')
    require(row['sha256']=='3cbc5e3d638a0281df0d94a98e282a9c59d29de8bccef0bf1224ad955d8bb11e',
            'unrecognized mechanical storage predecessor')
    row['sha256']='89e4728977ee45c8ea158179c3a5e7329fa5f45484c5df3e289c2ea3361f4a63'
    revision='5b9836358af2873e524e6ceae7256639e8a6bbce'
    git(ROOT,'merge-base','--is-ancestor',revision,'HEAD')
    historical_paths=git(ROOT,'ls-tree','-r','--name-only',revision,'src/pygrc/models').decode().splitlines()
    historical_paths={p for p in historical_paths if Path(p).name.startswith(('grc_v4','grc_9_v4')) and p.endswith('.py')}
    historical_rows=[dict(path=p,sha256=hashlib.sha256(git(ROOT,'show',revision+':'+p)).hexdigest())
                     for p in sorted(historical_paths)]
    require([r for r in adapted['source_bindings'] if r['path'].startswith('src/')]==historical_rows,
            'historical mechanical runtime bindings drift')
    current_nonruntime=[r for r in checker.bindings() if not r['path'].startswith('src/')]
    expected=sorted(current_nonruntime+historical_rows,key=lambda r:r['path'])
    with LOCK, patch.object(checker,'bindings',return_value=expected):
        checker.check(checker.contract.seal(adapted))


def browser_source(value):
    # Compact whitespace preserves every field while keeping this generated
    # executable asset below the raw-file storage threshold; no lossy summary.
    return "// Generated from checked retained Tranche 8 evidence; not new authority.\nexport const TRANCHE8_EVIDENCE = " + json.dumps(value, separators=(',', ':'), ensure_ascii=False) + ";\n"


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


@historical_view
def larger_apc_investigation(sources):
    """Authenticate pinned A_PC research; do not rerun even scalar equations."""
    import p984g_apc_investigation as research
    for path in LARGER_APC_RESEARCH_SOURCES:sources.raw(path)
    result=sources.read(research.RESULTS)
    require(result==research.seal(result) and result['source_bindings']==research.bindings(), 'A_PC research identity/source drift')
    require(result['schema']=='p984g-apc-investigation-v1' and result['family']=='A_PC'
        and result['scope']=='exact_real_whole_chart_and_diagonal_prestate_not_native_or_staged'
        and result['native_steps']==result['native_events']==0 and not result['ready_for_8_4h']
        and not result['user_accepted'] and not result['aggregate_closed'],'A_PC research scope')
    require([(c['graph'],c['role']) for c in result['cases']]==list(research.rows.shared.CASES),'A_PC case roster')
    cases=[dict(graph=c['graph'],role=c['role'],vertices=c['vertices'],edges=c['edges'],
        resource_sign=c['resource_sign'],minimum_resource_lower_display=float(research.q(c['first_resource_minimum_lower'])),
        source_envelope_upper_display=float(research.q(c['whole_chart']['source_upper'])),
        carrier_radius=float(research.q(c['whole_chart']['carrier_radius'])),
        carrier_next_norm_upper_display=float(research.q(c['carrier_next_norm_upper'])),
        carrier_next_in_ball=c['carrier_next_in_ball'],
        negative_vertices=[r['vertex'] for r in c['negative_vertices']],
        history_writer_certified=c['history_writer'] is not None,
        leading_empty_node_constraints=len(c['leading_empty_node_constraints'])) for c in result['cases']]
    import p984g_apc_feasibility as feasible
    for path in LARGER_APC_FEASIBILITY_SOURCES:sources.raw(path)
    f=feasible.check_retained(json.loads(lzma.decompress(sources.raw(feasible.RESULTS))))
    bounds=[dict(role=c['role'],
        initial_target_minimum_lower_display=float(research.q(c['initial_target']['minimum_resource_lower'])),
        source_postbeat_minimum_lower_display=float(research.q(c['source_postbeat']['minimum_resource_lower'])),
        source_signed_hessian_upper_display=float(research.q(c['source_trigger']['minimum_signed_hessian_upper'])),
        postbeat_transfer_target_minimum_lower_display=float(research.q(c['postbeat_transfer_target']['minimum_resource_lower'])),
        postbeat_role_use=c['postbeat_role_use']) for c in f['cases']]
    companion=dict(shares=f['selection']['shares'],source_deficit=f['companion']['source_deficit'],
        compensation_node=f['companion']['compensation_node'],compensation_distance=f['companion']['compensation_distance'],
        cases=bounds,event_pair=f['event_pair'],original_reset_exclusion_preserved=True,
        scope=f['scope'],native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        interval_research_recomputed=False,poststate_read_executed=False,
        open_obligations=f['open_obligations'],results=sources.ref(feasible.RESULTS),
        plan=sources.ref(feasible.PLAN),review=sources.ref(feasible.NOTE))
    import p984g_apc_staged as staged
    for path in LARGER_APC_STAGED_SOURCES:sources.raw(path)
    sv=staged.check_retained(json.loads(lzma.decompress(sources.raw(staged.RESULTS))))
    scases=[]
    for c in sv['cases']:
        r=c['result']
        scases.append(dict(graph=c['graph'],role=c['role'],minimum_resource=r['minimum_resource'],
            final_current_error_upper_display=float(research.q(r['final']['errors']['current'])),
            nonzero_offdiagonal_carrier_entries=r['nonzero_offdiagonal_carrier_entries'],
            stale_Z_final_current_changed_coordinates=r['stale_Z_final_current_changed_coordinates'],
            exact_stored_charge_drift=r['exact_stored_charge_drift'],
            final_read_executed=r['final_read_executed'],
            effects={stage:{key:dict(separated_coordinates=e['separated_coordinates'],maximum_lower_display=float(research.q(e['maximum_lower'])))
                for key,e in r[stage]['effects'].items()} for stage in ('initial','final')}))
    staged_view=dict(cases=scases,precision_bits=sv['precision_bits'],native_steps=0,native_events=0,
        ready_for_8_4h=False,user_accepted=False,interval_research_recomputed=False,
        scope=sv['scope'],open_obligations=sv['open_obligations'],results=sources.ref(staged.RESULTS),
        plan=sources.ref(staged.PLAN),review=sources.ref(staged.NOTE))
    import p984g_apc_hardening as hardening
    for path in LARGER_APC_HARDENING_SOURCES:sources.raw(path)
    hv=hardening.check_retained(json.loads(lzma.decompress(sources.raw(hardening.RESULTS))))
    hardened=dict(scale=hv['selection']['scale'],unconstrained_scale=hv['selection']['unconstrained_scale'],
        original_pressure=hv['original_pressure'],unconstrained_exclusion=hv['unconstrained_exclusion'],
        cases=[dict(graph=c['graph'],role=c['role'],minimum_resource=c['result']['minimum_resource'],
            separated_coordinates=c['carrier_separation']['separated_coordinates'],
            changed_current_coordinates=c['carrier_separation']['changed_current_coordinates'],
            effect_lower_display=float(research.q(c['carrier_separation']['effect_lower'])),
            combined_error_upper_display=float(research.q(c['carrier_separation']['two_read_error_upper'])),
            exact_stored_charge_drift=c['result']['exact_stored_charge_drift']) for c in hv['cases']],
        scope=hv['scope'],native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        numerical_recomputed=False,results=sources.ref(hardening.RESULTS),plan=sources.ref(hardening.PLAN),review=sources.ref(hardening.NOTE))
    import p984g_apc_native_targets as native
    for path in LARGER_APC_NATIVE_SOURCES:sources.raw(path)
    nv=sources.read(native.RESULTS)
    require(nv==native.seal(nv) and nv['source_bindings']==native.bindings() and
        nv['hardening_digest']==hv['record_digest'] and nv['schema']=='p984g-apc-native-summary-v1','A_PC native binding')
    require([(c['graph'],c['role']) for c in nv['cases']]==list(native.CASES),'A_PC native roster')
    for c in nv['cases']:
        if c['outcome']=='not_run':continue
        require(c['path']==native.case_path(c['graph'],c['role']),'A_PC native path')
        raw=sources.raw(c['path']);record=json.loads(lzma.decompress(raw))
        runtime_bindings=native.base.bindings() if c['graph']=='source' else native.bindings()
        require(hashlib.sha256(raw).hexdigest()==c['sha256'] and record==native.seal(record)
            and record['record_digest']==c['record_digest'] and record['source_bindings']==runtime_bindings, 'A_PC native retained identity')
    require(len(nv['historical_target_attempts'])==2,'A_PC historical attempts')
    for c in nv['historical_target_attempts']:
        raw=sources.raw(c['path']);record=json.loads(lzma.decompress(raw))
        require(c['path']==native.base.case_path(c['graph'],c['role']) and c['outcome']=='incomplete' and c['native_steps']==0
            and hashlib.sha256(raw).hexdigest()==c['sha256'] and record==native.seal(record)
            and record['record_digest']==c['record_digest'] and record['source_bindings']==native.base.bindings(),'A_PC historical failure binding')
    require(nv['native_steps']==sum(c['native_steps'] for c in nv['cases']) and
        nv['native_reads']==sum(c['native_reads'] for c in nv['cases']) and
        nv['native_prerequisites_complete']==all(c['outcome']=='completed' for c in nv['cases']) and
        nv['native_events']==nv['committed_steps']==0 and not nv['ready_for_8_4h'] and not nv['user_accepted'],'A_PC native scope')
    acceptance=sources.raw(native.NOTE).decode()
    require('## Scoped user acceptance' in acceptance and nv['record_digest'] in acceptance,
        'missing or unbound A_PC native prerequisite acceptance')
    native_view=dict(nv,results=sources.ref(native.RESULTS),plan=sources.ref(native.PLAN),review=sources.ref(native.NOTE),
        user_accepted=True,ready_for_8_4h=True,status='accepted_A_PC_prerequisites',
        original_execution_flags_unchanged=True,
        acceptance=sources.ref(native.NOTE,anchor='scoped-user-acceptance'))
    native_view.pop('source_bindings')
    return dict(family='A_PC',scope=result['scope'],pc_whole_chart=True,cases=cases,feasibility=companion,pc_staged=staged_view,pc_hardening=hardened,pc_native=native_view,
        native_roots=0,native_steps=nv['native_steps'],native_events=0,ready_for_8_4h=True,user_accepted=True,
        aggregate_closed=False,scalar_certificates_recomputed=False,native_trajectories_rerun=False,
        approximate_display_numbers=True,open_obligations=result['open_obligations'],
        results=sources.ref(research.RESULTS),plan=sources.ref(research.PLAN),review=sources.ref(research.NOTE))


@historical_view
def larger_aci_successor(sources):
    """Authenticate the compact result, not rerun roots or the full checker."""
    import p984g_aci_native_successor_check as check
    for path in LARGER_ACI_SUCCESSOR_SOURCES:sources.raw(path)
    value=sources.read(check.RESULTS)
    require(value==check.prior.seal(value) and value['family']=='A_CI' and
        value['schema']=='p984g-aci-corrected-native-summary-v1','corrected native summary identity')
    require(all(hashlib.sha256(sources.raw(p)).hexdigest()==h for p,h in value['source_bindings'].items()),
        'corrected native summary sources')
    require([(r['graph'],r['role']) for r in value['cases']]==list(check.run.base.CASES), 'corrected case roster')
    require(value['native_steps']==4 and value['native_roots']==12 and value['native_prerequisites_complete']
        and not value['known_implementation_holds'] and value['native_events']==value['committed_steps']==0
        and not value['ready_for_8_4h'] and not value['user_accepted'],'corrected native scope')
    bindings=check.run.bindings();cases=[]
    for row in value['cases']:
        require(row['path']==check.run.case_path(row['graph'],row['role']),'corrected native path')
        raw=sources.raw(row['path']);record=json.loads(lzma.decompress(raw))
        require(hashlib.sha256(raw).hexdigest()==row['sha256'] and record==check.prior.seal(record)
            and record['record_digest']==row['record_digest'] and record['source_bindings']==bindings,
            'corrected native execution binding')
        require(record['outcome']==row['outcome']=='completed' and not record['timed_out']
            and record['exit_code']==0 and record['error'] is None and row['root_evaluations']==[2,2,2],
            'corrected native completion')
        cases.append(dict(row,evidence=sources.ref(row['path'])))
    review=check.run.BASE+'P9-8.4g-ACINativeSuccessor.md'
    acceptance=sources.raw(review).decode()
    require('## Scoped user acceptance' in acceptance and value['record_digest'] in acceptance,
        'missing or unbound A_CI native prerequisite acceptance')
    return dict(value,cases=cases,full_retained_checker_rerun=False,
        user_accepted=True,ready_for_8_4h=True,status='accepted_A_CI_prerequisites',
        original_execution_flags_unchanged=True,
        acceptance=sources.ref(review,anchor='scoped-user-acceptance'),
        results=sources.ref(check.RESULTS),plan=sources.ref(check.run.PLAN),
        review=sources.ref(review))


@historical_view
def larger_aci_investigation(sources):
    import p984g_aci_investigation as research
    for name in LARGER_ACI_RESEARCH_SOURCES:
        sources.raw(name)
    result=research.check(sources.read(research.RESULTS))
    import p984g_aci_feasibility as feasible
    for name in LARGER_ACI_FEASIBILITY_SOURCES:
        sources.raw(name)
    f=feasible.check_retained(sources.read(feasible.RESULTS))
    import p984g_aci_staged as staged
    for name in LARGER_ACI_STAGED_SOURCES:
        sources.raw(name)
    import p984g_pre_aci_residual_sources as residual_history
    s=residual_history.check_staged(json.loads(lzma.decompress(sources.raw(staged.RESULTS))))
    import p984g_aci_native_check as native
    for name in LARGER_ACI_NATIVE_SOURCES:
        sources.raw(name)
    attempt=sources.read(native.RESULTS)
    require(attempt==native.seal(attempt) and attempt['family']=='A_CI' and
        attempt['source_bindings']=={native.SELF:hashlib.sha256((sources.root/native.SELF).read_bytes()).hexdigest()},
        'A_CI native summary binding')
    require(attempt['native_steps']==attempt['native_roots']==attempt['native_events']==0 and
        not attempt['ready_for_8_4h'] and not attempt['user_accepted'] and not attempt['native_prerequisites_complete']
        and attempt['known_implementation_holds']==native.KNOWN_HOLDS,'A_CI native hold promotion')
    require([(r['graph'],r['role'],r['outcome']) for r in attempt['cases']]==
        [('source','current','incomplete'),('source','reset','not_run'),('target','current','not_run'),('target','reset','not_run')],
        'A_CI attempted case scope')
    first=attempt['cases'][0];raw=sources.raw(first['path'])
    record=json.loads(lzma.decompress(raw))
    with residual_history.native_sources(native.run):
        old_native_bindings=native.run.bindings()
    require(hashlib.sha256(raw).hexdigest()==first['sha256'] and record==native.seal(record)
        and record['record_digest']==first['record_digest'] and record['source_bindings']==old_native_bindings
        and record['timed_out'] and record['outcome']=='incomplete','A_CI native attempt identity')
    native_view=dict(attempt,results=sources.ref(native.RESULTS),review=sources.ref(native.run.BASE+'P9-8.4g-ACINative.md'),
        plan=sources.ref(native.run.PLAN),attempt=sources.ref(first['path']),
        root_work_attempted=True,full_retained_checker_rerun=False,
        small_native_control='three_node_whole_step_writer_and_final_root_pass',
        enclosure_pressure='expected_failure_not_conformance_pass')
    staged_view=dict(scope=s['scope'],precision_bits=s['precision_bits'],linear_solve=s['linear_solve'],
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        interval_research_recomputed=False,approximate_display_numbers=True,
        cases=[dict(graph=c['graph'],role=c['role'],
            selected_joint_point_digest=c['result']['selected_joint_point_digest'],
            two_consecutive_independent_residual_passes=c['result']['two_consecutive_independent_residual_passes'],
            native_stopping_outcome_verified=False,
            confirming_joint_residual_upper_display=float(research.q(c['result']['stages'][1]['analytic_joint_residual_upper'])),
            feedback_coordinates_above_selected_error=c['result']['feedback_coordinates_above_selected_error'],
            generated_changed_diagonals=c['result']['generated_changed_diagonals'],
            generated_nonzero_offdiagonals=c['result']['generated_nonzero_offdiagonals'],
            exact_root_minimum_resource_lower_display=float(research.q(c['result']['exact_root_minimum_resource_lower']))) for c in s['cases']],
        open_obligations=s['open_obligations'],results=sources.ref(staged.RESULTS),
        plan=sources.ref(staged.PLAN),review=sources.ref(staged.NOTE))
    companion=dict(scope=f['scope'],shares=f['companion']['shares'],source_deficit=f['companion']['source_deficit'],
        source_compensation_node=f['companion']['source_compensation_node'],event_pair=f['event_pair'],
        allocation_only_diagnostic_kind='uncertified_exact_strict_margin',
        history_policy_unchanged=True,original_reset_exclusion_preserved=True,
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        interval_research_recomputed=False,approximate_display_numbers=True,
        cases=[dict(role=c['role'],
            initial_target_minimum_lower_display=float(research.q(c['initial_target']['minimum_resource_lower'])),
            fresh_transfer_target_minimum_lower_display=float(research.q(c['postbeat_transfer_target']['minimum_resource_lower'])),
            source_postbeat_gradient_norm_upper_display=float(research.q(c['source_trigger']['gradient_norm_upper'])),
            source_postbeat_signed_hessian_upper_display=float(research.q(c['source_trigger']['minimum_signed_hessian_upper']))) for c in f['cases']],
        open_obligations=f['open_obligations'],results=sources.ref(feasible.RESULTS),
        plan=sources.ref(feasible.PLAN),review=sources.ref(feasible.NOTE))
    # Exact rational endpoints remain in the linked evidence, not duplicated
    # into an executable browser asset. Display conversions grant no authority.
    cases=[dict(graph=c['graph'],role=c['role'],vertices=c['vertices'],edges=c['edges'],
        exact_real_unique_joint_root=c['exact_real_unique_joint_root'],
        exact_real_first_step_resources_nonnegative=c['exact_real_first_step_resources_nonnegative'],
        bounds_display={k:float(research.q(v)) for k,v in c['bounds'].items()},
        negative_vertices=[v['vertex'] for v in c['certified_negative_vertices']],
        unresolved_resource_vertices=c['unresolved_resource_vertices']) for c in result['cases']]
    return dict(family='A_CI',scope=result['scope'],cases=cases,feasibility=companion,staged_oracle=staged_view,native_attempt=native_view,
        native_successor=larger_aci_successor(sources),
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        aggregate_closed=False,approximate_display_numbers=True,scalar_certificates_recomputed=True,
        native_trajectories_rerun=False,open_obligations=result['open_obligations'],
        authority=result['authority'],results=sources.ref(research.RESULTS),
        plan=sources.ref(research.NOTE),review=sources.ref(research.NOTE))


@historical_view
def larger_cci_investigation(sources):
    from p984g_pre_ci_interval_sources import historical_sources
    with historical_sources():
        return _larger_cci_investigation(sources)


def _larger_cci_investigation(sources):
    import p984g_cci_investigation as research
    for name in LARGER_CCI_RESEARCH_SOURCES:
        sources.raw(name)
    result=research.check(sources.read(research.RESULTS))
    import p984g_cci_staged as staged
    import p984g_cci_continuation as continuation
    for name in LARGER_CCI_STAGED_SOURCES:
        sources.raw(name)
    assessed=continuation.check()  # includes the staged retained check once
    checked=staged.read(staged.RESULTS)
    import p984g_cci_feasibility as feasible
    for name in LARGER_CCI_FEASIBILITY_SOURCES:
        sources.raw(name)
    f=feasible.check_retained(sources.read(feasible.RESULTS))
    feasibility=dict(scope=f['scope'],shares=f['companion']['shares'],source_deficit=f['companion']['source_deficit'],
        source_compensation_node=f['companion']['source_compensation_node'],event_pair=f['event_pair'],
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        interval_solves_rerun=False,approximate_display_numbers=True,
        allocation_only_staged_trigger_failed_roles=[r['role'] for r in f['allocation_only_diagnostic']['cases']],
        cases=[dict(role=r['role'],
            initial_target_minimum_lower_display=float(staged.q(r['initial_transfer']['minimum_lower'])),
            fresh_transfer_target_minimum_lower_display=float(staged.q(r['fresh_postbeat_transfer']['minimum_lower'])),
            source_postbeat_gradient_norm_upper_display=float(staged.q(r['source_postbeat_trigger']['gradient_norm_upper'])),
            source_postbeat_signed_hessian_upper_display=float(staged.q(r['source_postbeat_trigger']['minimum_signed_hessian_upper'])),
            rounded_exact_postbeat_control_passed=r['rounded_exact_postbeat_control']['strict_hessian_condition']) for r in f['cases']],
        results=sources.ref(feasible.RESULTS),plan=sources.ref(feasible.PLAN),review=sources.ref(feasible.REVIEW))
    # Compact display only: exact endpoints remain in the authenticated records.
    cases=[dict(graph=c['graph'],role=c['role'],
        analytic_joint_residual_display=float(staged.q(c['analytic_joint_residual_upper'])),
        joint_root_error_display=float(staged.q(c['joint_root_bridge']['joint_error_upper'])),
        exact_feedback_lower_display=float(staged.q(c['exact_feedback_current_max_lower'])),
        exact_feedback_upper_display=float(staged.q(c['exact_feedback_current_max_upper'])),
        independent_analytic_residual_pass=c['independent_analytic_residual_pass'],
        counterfactual_changed_current_coordinates=c['counterfactual_changed_current_coordinates'],
        generated_changed_diagonals=c['generated_changed_diagonals'],
        generated_nonzero_offdiagonals=c['generated_nonzero_offdiagonals'],
        minimum_continuity_proposal=c['minimum_continuity_proposal'],
        evidence=sources.ref(c['path'])) for c in checked['cases']]
    bridge=dict(scope=checked['scope'],cases=cases,approximate_display_numbers=True,
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,
        user_accepted=False,native_stopping_outcome_verified=False,
        interval_solves_rerun=False,results=sources.ref(staged.RESULTS),
        plan=sources.ref(staged.PLAN),review=sources.ref(staged.REVIEW),
        continuation=dict(scope=assessed['scope'],results=sources.ref(continuation.RESULTS),
            excluded_target_roles=sum(c['graph']=='target' and bool(c['certified_negative_vertices']) for c in assessed['cases']),
            cases=[dict(graph=c['graph'],role=c['role'],
                minimum_lower_display=float(staged.q(c['exact_root_resource_minimum_lower'])),
                minimum_upper_display=float(staged.q(c['exact_root_resource_minimum_upper'])),
                negative_vertices=[dict(index=v['index'],node=v['node'],
                    every_positive_dt=v['excluded_for_every_positive_dt_at_this_state']) for v in c['certified_negative_vertices']]) for c in assessed['cases']]),
        open_obligations=['source/allocation companion has bounded exact-real feasibility; native admission remains unproved',
            'native whole-domain certificate and analytic residual/stopping comparison',
            'both-role computed roots, charge and final-C admission',
            'preserve feedback-versus-rounding limits; no tolerance change or extra iteration implied'])
    import p984g_cci_closure_check as closure
    for name in LARGER_CCI_NATIVE_SOURCES:
        sources.raw(name)
    from p984g_pre_aci_residual_sources import native_sources,REVISION
    with native_sources(closure.run):
        native=closure.check()
    require(native==sources.read(closure.run.RESULTS),'C_CI native summary drift')
    acceptance=sources.raw(closure.run.REVIEW).decode()
    require('## Scoped user acceptance' in acceptance and native['record_digest'] in acceptance,
            'missing or unbound C_CI native prerequisite acceptance')
    native_view=dict(scope=native['scope'],native_steps=native['native_steps'],native_roots=native['native_roots'],
        native_events=0,committed_steps=0,native_prerequisites_complete=True,user_accepted=True,
        ready_for_8_4h=True,numerical_trajectories_rerun=False,status='accepted_C_CI_prerequisites',
        acceptance=sources.ref(closure.run.REVIEW,anchor='scoped-user-acceptance'),
        cases=[dict(graph=c['graph'],role=c['role'],seconds=c['seconds'],minimum_resource=c['minimum_resource'],
            root_evaluations=c['root_evaluations'],independent_joint_residual_upper=c['independent_joint_residual_upper'],
            exact_resource_sum_delta=c['exact_resource_sum_delta'],evidence=sources.ref(c['path'])) for c in native['cases']],
        results=sources.ref(closure.run.RESULTS),plan=sources.ref(closure.run.PLAN),review=sources.ref(closure.run.REVIEW),
        historical_source_revision='e1d61021',native_runtime_source_revision=REVISION,
        corrected_runtime_reexecuted=False,original_research_flags_unchanged=True)
    return dict(result, staged_bridge=bridge, feasibility=feasibility, native_prerequisites=native_view,
        results=sources.ref(research.RESULTS), plan=sources.ref(research.PLAN),
        review=sources.ref(research.REVIEW), scalar_certificates_recomputed=True,
        native_trajectories_rerun=False)


@historical_view
def larger_view(sources, *, include_investigations=True):
    import p984g_cos as preflight
    import p984g_cos_bounds as bounds
    m,r=sources.read(preflight.INPUTS),sources.read(preflight.RESULTS)
    with historical_larger_sources():
        row=preflight.check(m,r)
    row.update(inputs=sources.ref(preflight.INPUTS),results=sources.ref(preflight.RESULTS),
        plan=sources.ref(preflight.PLAN),review=sources.ref(preflight.REVIEW))
    bm,br=sources.read(bounds.INPUTS),sources.read(bounds.RESULTS)
    with historical_larger_sources():
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
    import p984g_cos_native as native
    # Authenticate output bytes before trusting their internal summaries.
    for name in LARGER_COS_NATIVE_SOURCES:
        sources.raw(name)
    from p984g_pre_ci_interval_sources import historical_sources
    with historical_sources():
        checked = native.check(sources.read(native.INPUTS), sources.read(native.RESULTS))
    row['native_prerequisites'] = dict(checked, inputs=sources.ref(native.INPUTS),
        results=sources.ref(native.RESULTS), plan=sources.ref(native.PLAN), review=sources.ref(native.REVIEW),
        production_shortcut_integrated=True, native_trajectories_rerun=False,
        historical_source_revision='e1d61021',current_tree_execution=False)
    require('## Scoped user acceptance' in sources.raw(native.REVIEW).decode(),
            'missing C_OS native prerequisite acceptance')
    row['native_prerequisites'].update(status='accepted_C_OS_prerequisites',
        user_accepted=True, ready_for_8_4h=True,
        acceptance_scope='four_fixed_C_OS_numerical_prerequisites_not_lifecycle_campaign',
        acceptance=sources.ref(native.REVIEW,anchor='scoped-user-acceptance'))
    row['open_obligations']=['8.4h actual expansion/lifecycle and continuation campaign; not executed here']
    return dict(family_results=[row],investigations=([larger_cci_investigation(sources),larger_aci_investigation(sources),larger_apc_investigation(sources)] if include_investigations else []),
        aggregate_closed=False,first_group_closed=False,
        families_without_preflight=[f for f in FAMILIES if f not in
            (('C_OS','C_CI','A_CI','A_PC') if include_investigations else ('C_OS',))])


def larger_cos_native_view(sources):
    """Exact pinned completed segments; status never reruns native admission."""
    import p984h_cos_native as run
    for name in LARGER_RUNTIME_COS_NATIVE_SOURCES:
        sources.raw(name)
    m=sources.read(run.INPUTS)
    require(m==run.seal(m), 'native manifest identity')
    for name,sha in m['source_bindings'].items():
        require(historical_binding(name,sha,sources.current_bytes(name)),'native source drift: '+name)
    rows={}; failures=[]
    oracle=json.loads(lzma.decompress(sources.raw(run.oracle.RESULTS)))
    for segment in run.CAPS:
        name=run.path(segment)
        if name not in LARGER_RUNTIME_COS_NATIVE_SOURCES:
            continue
        record=json.loads(lzma.decompress(sources.raw(name)))
        require(record==run.seal(record) and record['manifest_digest']==m['record_digest']
                and record['segment']==segment, 'native segment identity')
        require(not record['user_accepted'] and not record['aggregate_closed']
                and not record['covariance_executed'], 'native scope widened')
        if 'execution_driver' in record:
            driver=record['execution_driver']
            require(driver['path'] in LARGER_RUNTIME_COS_NATIVE_SOURCES
                    and driver['sha256']==hashlib.sha256(sources.raw(driver['path'])).hexdigest()
                    and driver['serialization']=='compact_json_xz','native execution driver drift')
        if record['outcome']!='completed':
            require(segment=='event' and record['outcome']=='failed'
                    and record['failure']['type']=='TimeoutError', 'unknown native failure')
            failures.append(dict(segment=segment,outcome=record['outcome'],error=record['failure'],
                seconds=record['elapsed_seconds'],event_committed=False,result=sources.ref(name)))
        else:rows[segment]=record
    require('prefix' in rows, 'native prefix missing')
    require(rows['prefix']['execution']['native_steps']==2, 'native source-step count')
    if 'event' in rows:
        require(rows['event']['execution']['predecessor_digest']==rows['prefix']['record_digest'], 'native event predecessor')
        require(rows['event']['execution']['event_id']==oracle['event_id'], 'native/oracle event identity')
    for role in ('current','reset'):
        if role in rows:
            require('event' in rows and rows[role]['execution']['predecessor_digest']==rows['event']['record_digest'], 'native role predecessor')
            actual=rows[role]['execution']['steps']
            expected=next(c for c in oracle['cases'] if c['role']==role)['steps'][0]
            require(len(actual)==1 and actual[0]['corrector']['current']==expected['current']
                    and actual[0]['after_C']==expected['after_C'],'native first-step oracle mismatch')
    return dict(status='historical_native_prefix_complete',
        source_steps=rows['prefix']['execution']['native_steps'],
        native_events=rows.get('event',{}).get('execution',{}).get('native_events',0),
        target_steps_by_role={r:rows.get(r,{}).get('execution',{}).get('native_steps',0) for r in ('current','reset')},
        required_target_steps_per_role=m['planned_total_steps_per_role'],
        first_step_minima={role:rows[role]['execution']['steps'][0]['minimum_resource']
                           for role in ('current','reset') if role in rows},
        remaining_covariance=True,detached_continuation=True,ten_step_campaign_complete=False,
        native_numerics_rerun=False,user_accepted=False,failures=failures,
        timeout_note='Original attempt exceeded 1200 s during target readmission; artifact removed at user request. No success credit.',
        historical_source_revision='718f95be',current_tree_execution=False,
        inputs=sources.ref(run.INPUTS),plan=sources.ref(run.PLAN),
        segments=[dict(segment=s,result=sources.ref(run.path(s)),seconds=v['elapsed_seconds']) for s,v in rows.items()])


def larger_cos_performance_view(sources):
    import p984h_cos_solve_reuse as run
    for name in LARGER_RUNTIME_COS_PERFORMANCE_SOURCES:sources.raw(name)
    baseline=json.loads(lzma.decompress(sources.raw(run.probe.OUTPUT)))
    value=json.loads(lzma.decompress(sources.raw(run.OUTPUT)))
    require(baseline==run.run.seal(baseline) and value==run.run.seal(value), 'performance record identity')
    for name,sha in baseline['source_bindings'].items():
        require(historical_binding(name,sha,sources.current_bytes(name)), 'profile source drift: '+name)
    for name,sha in value['source_bindings'].items():
        require(historical_binding(name,sha,sources.current_bytes(name)), 'solve reuse source drift: '+name)
    require(value['baseline_record_digest']==baseline['record_digest']
            and value['input_digest']==baseline['input_digest'], 'performance predecessor/input drift')
    require(value['native_events']==value['native_steps']==0, 'performance false execution credit')
    require([r['name'] for r in value['records']]==['cold','warm'], 'performance read roster')
    expected=run.run.digest({k:baseline[k] for k in run.FIELDS})
    require(all(r['baseline_parity'] and r['scientific_view_digest']==expected for r in value['records']),
            'performance full-point parity')
    import p984h_cos_scalar_reuse as scalar
    optimized=json.loads(lzma.decompress(sources.raw(scalar.OUTPUT)))
    require(optimized==run.run.seal(optimized), 'scalar reuse record identity')
    for name,sha in optimized['source_bindings'].items():
        require(historical_binding(name,sha,sources.current_bytes(name)), 'scalar kernel source drift: '+name)
    require(optimized['baseline_record_digest']==baseline['record_digest']
            and optimized['input_digest']==baseline['input_digest']
            and optimized['scientific_view_digest']==expected and optimized['baseline_parity']
            and optimized['native_steps']==optimized['native_events']==0, 'scalar kernel parity/scope drift')
    import p984h_cos_dyadic_rounding as dyadic
    current=json.loads(lzma.decompress(sources.raw(dyadic.OUTPUT)))
    require(current==run.run.seal(current), 'dyadic read record identity')
    for name,sha in current['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha, 'dyadic source drift: '+name)
    require(current['baseline_record_digest']==baseline['record_digest']
            and current['input_digest']==baseline['input_digest']
            and current['scientific_view_digest']==expected and current['baseline_parity']
            and current['native_steps']==current['native_events']==0, 'dyadic parity/scope drift')
    import p984h_cos_dyadic_step as step_probe
    step=json.loads(lzma.decompress(sources.raw(step_probe.OUTPUT)))
    prefix=json.loads(lzma.decompress(sources.raw(run.run.path('prefix'))))
    require(step==run.run.seal(step) and step['prefix_record_digest']==prefix['record_digest']
            and baseline['prefix_digest']==prefix['record_digest'], 'changing step predecessor drift')
    for name,sha in step['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha, 'changing step source drift: '+name)
    prior_step=prefix['execution']['steps'][1]
    require(step['whole_step_parity'] and step['scientific_view_digest']==run.run.digest(
        {k:v for k,v in prior_step.items() if k not in ('seconds','dense_errors','trigger')})
        and step['native_steps']==1 and step['native_events']==step['new_campaign_steps']==0,
        'changing step parity/scope drift')
    return dict(baseline_seconds=baseline['elapsed_seconds'],cold_seconds=value['records'][0]['elapsed_seconds'],
        warm_seconds=value['records'][1]['elapsed_seconds'],full_read_parity=True,
        scalar_kernel_cold_seconds=optimized['elapsed_seconds'],scalar_kernel_result=sources.ref(scalar.OUTPUT),
        dyadic_cold_seconds=current['elapsed_seconds'],dyadic_result=sources.ref(dyadic.OUTPUT),
        repeated_source_step_seconds=step['elapsed_seconds'],repeated_source_step_full_parity=True,
        repeated_source_step_result=sources.ref(step_probe.OUTPUT),
        current_tree_read_only=True,event_execution=False,numerics_rerun=False,
        results=sources.ref(run.OUTPUT),baseline=sources.ref(run.probe.OUTPUT),
        review=sources.ref(BASE+'P9-8.4h-COSPerformance.md'))


def larger_cos_event_successor_view(sources):
    """Pinned execution projection; offline checker owns full reconstruction."""
    import p984h_cos_event_successor as run
    for name in LARGER_RUNTIME_COS_EVENT_SUCCESSOR_SOURCES:sources.raw(name)
    m=sources.read(run.INPUTS)
    r=json.loads(lzma.decompress(sources.raw(run.RESULTS)))
    require(m==run.seal(m) and r==run.seal(r) and r['manifest_digest']==m['record_digest'],
            'event successor identity')
    for name,sha in m['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha,
                'event successor source drift: '+name)
    prefix=json.loads(lzma.decompress(sources.raw(run.native.path('prefix'))))
    require(m['prefix_record_digest']==prefix['record_digest'], 'event successor predecessor')
    if 'retention_revision' in r:
        require(r['retention_revision']['execution_payload_digest']==run.digest(r['execution'])
                and r['retention_revision']['numerical_rerun'] is False, 'retention execution drift')
    require(r['schema']=='p984h-cos-event-successor-v1'
            and r['outcome'] in ('completed','failed') and r['cap_seconds']==m['cap_seconds']==1200
            and r['native_steps']==0 and not r['user_accepted'] and not r['aggregate_closed']
            and not r['covariance_executed'] and m['scientific_inputs_unchanged'], 'event successor scope')
    completed=r['outcome']=='completed'
    if completed:
        e=r['execution']
        require(r['native_events']==e['native_events']==1 and e['native_steps']==0
                and e['predecessor_digest']==prefix['record_digest'] and e['event_id']==m['event_id']
                and r['elapsed_seconds']<=1200 and r['publication_observation']=='committed_and_checked'
                and len(e['admissions'])==4 and e['rollback_exact']
                and all(a['split_admitted'] and a['old_publication_live'] for a in e['admissions'])
                and not e['ten_step_campaign_complete'], 'event successor execution scope')
    else:
        require(r['native_events']==0 and 'execution' not in r and 'failure' in r
                and r['publication_observation']=='unknown_on_failure', 'failed successor false credit')
    return dict(outcome=r['outcome'],seconds=r['elapsed_seconds'],cap_seconds=1200,
        native_events=r['native_events'],native_steps=0,both_role_admission_checked=completed,
        publication_observation=r['publication_observation'],failure=r.get('failure'),
        failed_attempt_artifact_retained=False,scientific_inputs_unchanged=True,
        target_steps_by_role=dict(current=0,reset=0),user_accepted=False,
        native_numerics_rerun=False,full_reconstruction_rerun=False,
        inputs=sources.ref(run.INPUTS),results=sources.ref(run.RESULTS),plan=sources.ref(run.PLAN),
        review=sources.ref(BASE+'P9-8.4h-COSEventSuccessorReview.md'))


def larger_cos_continuation_view(sources):
    """Authenticate pinned per-role chains without replaying native reads."""
    import p984h_cos_continuation as run
    for name in LARGER_RUNTIME_COS_CONTINUATION_SOURCES:sources.raw(name)
    m=sources.read(run.INPUTS)
    require(m==run.seal(m),'continuation manifest seal')
    for name,sha in m['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha,'continuation source drift: '+name)
    event=json.loads(lzma.decompress(sources.raw(run.event.RESULTS)))
    require(event['record_digest']==m['event_record_digest'] and event['outcome']=='completed','continuation event linkage')
    seed=event['execution']['checkpoint']['state']['inputs'];roles={}
    for role in run.ROLES:
        previous=m['event_record_digest'];post=None;records=[];minima=[];durations=[];charges=[];final=False
        for step in (*range(1,11),'final'):
            name=run.path(role,step)
            if name not in LARGER_RUNTIME_COS_CONTINUATION_SOURCES:continue
            r=json.loads(lzma.decompress(sources.raw(name)))
            require(r==run.seal(r) and r['manifest_digest']==m['record_digest']
                    and r['event_record_digest']==m['event_record_digest'] and r['predecessor_digest']==previous
                    and r['role']==role and r['step']==step and r['outcome']=='completed'
                    and 0<=r['elapsed_seconds']<=m['seconds_per_step_or_final_read']
                    and not r['user_accepted'] and not r['aggregate_closed'] and not r['covariance_executed']
                    and r['native_events']==0 and r['detached_continuation'],'continuation record linkage/scope')
            if step=='final':
                require(len(records)==10 and r['native_steps']==0 and r['final_reads']==1
                        and r['input_digest']==run.digest(post) and r['split_admitted'],'final read linkage')
                final=True
            else:
                require(step==len(records)+1 and r['native_steps']==1 and r['final_reads']==0,'continuation sequence')
                row=r['observation'];next_inputs=r['next_inputs']
                require(row['before_C']==(post['current']['C'] if post else seed[role]['C'])
                        and (post is None or row['before_digest']==run.digest(post))
                        and row['after_digest']==run.digest(next_inputs) and row['after_C']==next_inputs['current']['C']
                        and next_inputs['reset']==seed['reset'] and next_inputs['reference']==seed['reference']
                        and next_inputs['H1_form']==seed['H1_form']
                        and row['minimum_resource']==min(row['after_C'])>0 and row['split_admitted']
                        and row['after_index']==seed['step_index']+step,'continuation state/scope')
                if step==1:
                    oracle=json.loads(lzma.decompress(sources.raw(run.native.oracle.RESULTS)))
                    expected=next(c for c in oracle['cases'] if c['role']==role)['steps'][0]
                    require(row['corrector']['current']==expected['current'] and row['after_C']==expected['after_C'],'first step oracle')
                post=next_inputs;records.append(step);minima.append(row['minimum_resource']);charges.append(row['charge'])
            previous=r['record_digest'];durations.append(r['elapsed_seconds'])
        roles[role]=dict(native_steps=len(records),final_reads=int(final),minimum_resources=minima,
            charge_observations=charges,segment_seconds=durations,
            results=[sources.ref(run.path(role,s)) for s in records]+([sources.ref(run.path(role,'final'))] if final else []))
    return dict(roles=roles,target_steps=sum(r['native_steps'] for r in roles.values()),
        final_reads=sum(r['final_reads'] for r in roles.values()),
        baseline_complete=all(r['native_steps']==10 and r['final_reads']==1 for r in roles.values()),
        detached_continuation=True,first_steps_match_certified_oracle=all(r['native_steps']>=1 for r in roles.values()),
        native_numerics_rerun=False,uniform_trajectory_enclosure=False,covariance_executed=False,user_accepted=False,
        inputs=sources.ref(run.INPUTS),plan=sources.ref(run.PLAN),review=sources.ref(BASE+'P9-8.4h-COSContinuationReview.md'))


def larger_cos_covariance_view(sources):
    """Pinned partial coverage, not a native/allocator/full-chain rerun."""
    import p984h_cos_covariance as run
    import p984h_cos_covariance_continuation as successor
    import p984h_cos_covariance_transforms as individual
    for name in LARGER_RUNTIME_COS_COVARIANCE_SOURCES:sources.raw(name)
    m=sources.read(run.INPUTS)
    require(m==run.seal(m),'covariance manifest seal')
    for name,sha in m['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha,'covariance source drift: '+name)
    successor_manifest=sources.read(successor.INPUTS)
    require(successor_manifest==run.seal(successor_manifest) and successor_manifest['parent_manifest_digest']==m['record_digest'],
        'covariance comparison successor identity')
    for name,sha in successor_manifest['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha,'covariance successor source drift: '+name)
    individual_manifests={}
    for kind in individual.KINDS:
        name=individual.inputs(kind)
        if name not in LARGER_RUNTIME_COS_COVARIANCE_SOURCES:continue
        declaration=sources.read(name)
        require(declaration==run.seal(declaration) and declaration['parent_manifest_digest']==m['record_digest']
            and declaration['selected_transform']==kind and declaration['numerical_law_changed'] is False
            and declaration['parent_event_reexecuted'] is False,'individual covariance manifest identity/scope')
        for source,sha in declaration['source_bindings'].items():
            require(hashlib.sha256(sources.current_bytes(source)).hexdigest()==sha,'individual covariance source drift: '+source)
        event=json.loads(lzma.decompress(sources.raw(run.path(kind,'event'))))
        require(declaration['event_record_digest']==event['record_digest'],'individual covariance event binding')
        individual_manifests[kind]=declaration
    rows=[];mechanical=[];events=steps=0
    for kind,segment in [('all','mechanical')]+[(k,s) for k in run.KINDS for s in ('event',*run.ROLES)]:
        if segment in run.ROLES:
            name=successor.path(segment) if kind=='combined' else individual.path(kind,segment)
        else:name=run.path(kind,segment)
        if name not in LARGER_RUNTIME_COS_COVARIANCE_SOURCES:continue
        r=json.loads(lzma.decompress(sources.raw(name)))
        expected_manifest=(successor_manifest if kind=='combined' else individual_manifests[kind]) if segment in run.ROLES else m
        require(r==run.seal(r) and r['manifest_digest']==expected_manifest['record_digest'] and r['kind']==kind
            and r['segment']==segment and r['outcome']=='completed' and not r['user_accepted']
            and not r['aggregate_closed'],'covariance record identity/scope')
        e=r['execution']
        if segment=='mechanical':
            require([v['kind'] for v in e]==list(run.KINDS) and all(v['exact_graph_and_both_role_transfer']
                and v['native_events']==v['native_steps']==0 for v in e),'mechanical covariance scope')
            mechanical=list(run.KINDS);continue
        require(e['native_events']==int(segment=='event') and e['native_steps']==int(segment!='event'),'covariance counts')
        require(0<=r['elapsed_seconds']<=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds'],'covariance cap')
        if segment=='event':
            require(len(e['admissions'])==4 and all(v['split_admitted'] and v['old_publication_live'] for v in e['admissions'])
                and e['rollback_exact'],'covariance admission/rollback')
        else:
            ev=json.loads(lzma.decompress(sources.raw(run.path(kind,'event'))))
            require(e['event_record_digest']==ev['record_digest'] and e['role']==segment
                and e['observation']['split_admitted'] and e['observation']['minimum_resource']>0
                and e['detached_continuation'],'covariance continuation link')
        rows.append(dict(kind=kind,segment=segment,seconds=r['elapsed_seconds'],
            covariance_errors=e['covariance_errors'],results=sources.ref(name)))
        events+=e['native_events'];steps+=e['native_steps']
    completed=[kind for kind in run.KINDS if {r['segment'] for r in rows if r['kind']==kind}=={'event',*run.ROLES}]
    pending=[kind for kind in run.KINDS if kind not in completed]
    return dict(mechanical_transforms=mechanical,required_transforms=list(run.KINDS),segments=rows,
        completed_numerical_transforms=completed,pending_numerical_transforms=pending,
        native_events=events,target_steps=steps,transformed_horizon=1,source_prefix_rerun=False,
        covariance_complete=not pending and mechanical==list(run.KINDS),user_accepted=False,native_numerics_rerun=False,
        inputs=sources.ref(run.INPUTS),plan=sources.ref(run.PLAN),
        review=sources.ref(BASE+'P9-8.4h-COSCovarianceReview.md'))


def larger_cos_runtime_view(sources):
    """Pinned oracle projection; no solves, materialization or native execution."""
    import p984h_cos as run
    for name in LARGER_RUNTIME_COS_SOURCES:sources.raw(name)
    m=sources.read(run.INPUTS)
    r=json.loads(lzma.decompress(sources.raw(run.RESULTS)))
    require(m==run.seal(m) and r==run.seal(r) and r['inputs_digest']==m['record_digest'],'larger runtime oracle identity')
    for name,sha in m['source_bindings'].items():
        require(historical_binding(name,sha,sources.current_bytes(name)),'larger runtime source drift: '+name)
    require([c['role'] for c in r['cases']]==list(run.ROLES) and all(len(c['steps'])==1 for c in r['cases']),
        'larger runtime oracle coverage')
    require(not m['original_postbeat_trigger']['eligible'] and r['trigger']['eligible'],'larger runtime trigger distinction')
    require(r['native_events']==r['native_steps']==0 and not r['user_accepted'] and not r['aggregate_closed'],'larger runtime false credit')
    result=dict(family='C_OS',checkpoint='8.4h',status='two_beat_oracle_complete_native_pending',
        original_trigger=m['original_postbeat_trigger'],source_beats_before_request=m['source_beats_before_request'],
        initial_conditions_unchanged=m['initial_conditions_unchanged'],fresh_trigger=r['trigger'],
        oracle_steps=2,source_oracle_steps=1,exact_reused_reset_cases=1,dense_screen_steps=2*run.STEPS,
        native_events=0,native_steps=0,
        user_accepted=False,aggregate_closed=False,numerical_trajectories_rerun=False,
        covariance_executed=False,uniform_trajectory_enclosure=False,
        role_minima={c['role']:min(s['minimum_resource'] for s in c['steps']) for c in r['cases']},
        inputs=sources.ref(run.INPUTS),results=sources.ref(run.RESULTS),plan=sources.ref(run.PLAN),review=sources.ref(run.REVIEW))
    if LARGER_RUNTIME_COS_NATIVE_SOURCES:
        native=larger_cos_native_view(sources)
        result.update(status=native['status'],native=native,native_events=native['native_events'],
            native_steps=native['source_steps']+sum(native['target_steps_by_role'].values()))
    if LARGER_RUNTIME_COS_PERFORMANCE_SOURCES:
        result['performance']=larger_cos_performance_view(sources)
    if LARGER_RUNTIME_COS_EVENT_SUCCESSOR_SOURCES:
        successor=larger_cos_event_successor_view(sources)
        result.update(event_successor=successor,native_events=successor['native_events'],
            status=('native_event_successor_complete_target_continuation_pending'
                if successor['outcome']=='completed' else 'native_event_successor_failed'))
    if LARGER_RUNTIME_COS_CONTINUATION_SOURCES:
        continuation=larger_cos_continuation_view(sources)
        result.update(continuation=continuation,native_steps=result['native']['source_steps']+continuation['target_steps'],
            status='native_baseline_complete_covariance_pending' if continuation['baseline_complete'] else 'native_target_continuation_partial')
    if LARGER_RUNTIME_COS_COVARIANCE_SOURCES:
        covariance=larger_cos_covariance_view(sources)
        result.update(covariance=covariance,covariance_executed=covariance['native_events']>0,
            native_events=result['native_events']+covariance['native_events'],
            native_steps=result['native_steps']+covariance['target_steps'],
            status=('native_baseline_and_covariance_complete_pending_acceptance'
                if result['continuation']['baseline_complete'] and covariance['covariance_complete']
                else 'native_baseline_complete_covariance_partial'))
        acceptance=sources.raw(BASE+'P9-8.4h-COSCovarianceReview.md').decode()
        require('## Scoped user acceptance' in acceptance and '2026-10-21' in acceptance,
            'missing scoped C_OS 8.4h acceptance')
        require(result['continuation']['baseline_complete'] and covariance['covariance_complete'],
            'accepted C_OS 8.4h coverage incomplete')
        result.update(status='native_baseline_and_covariance_accepted',user_accepted=True,
            accepted_on='2026-10-21',acceptance_scope='C_OS P9-8.4h bounded baseline and eight covariance counterparts',
            acceptance=covariance['review'],original_execution_flags_unchanged=True)
    return result


def larger_cci_covariance_view(sources, baseline_digest):
    """Pinned eight-by-three roster; never reconstruct or solve a counterpart."""
    import p984h_cci_covariance as cov
    if cov.INPUTS not in LARGER_RUNTIME_CCI_SOURCES:return None
    m=sources.read(cov.INPUTS)
    require(m==cov.seal(m) and m['baseline_event_digest']==baseline_digest
        and [d['kind'] for d in m['transforms']]==list(cov.KINDS),'C_CI covariance manifest/roster')
    for name,sha in m['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha,'C_CI covariance source drift: '+name)
    cases=[];events=0;steps=0
    def maximum(value):
        if isinstance(value,dict):return max((maximum(v) for v in value.values()),default=0.)
        return float(value)
    for kind in cov.KINDS:
        event_record=None;segments=[]
        for segment in ('event',*cov.ROLES):
            name=cov.path(kind,segment)
            if name not in LARGER_RUNTIME_CCI_SOURCES:continue
            r=json.loads(lzma.decompress(sources.raw(name)))
            require(r==cov.seal(r) and r['schema']=='p984h-cci-covariance-results-v1'
                and r['manifest_digest']==m['record_digest'] and r['kind']==kind and r['segment']==segment
                and r['outcome']=='completed' and not r['user_accepted'] and not r['aggregate_closed'],
                'C_CI covariance segment identity/scope')
            require(0<=r['elapsed_seconds']<=m['event_cap_seconds' if segment=='event' else 'step_cap_seconds'],
                'C_CI covariance cap')
            e=r['execution']
            if segment=='event':
                require(e['native_events']==1 and e['native_steps']==0 and len(e['admissions'])==2
                    and e['rollback_exact'],'C_CI covariance event coverage')
                event_record=r;events+=1
            else:
                require(event_record is not None and e['event_record_digest']==event_record['record_digest']
                    and e['role']==segment and e['native_events']==0 and e['native_steps']==1
                    and e['detached_continuation'] and cov.q(e['resource_bounds']['minimum_exact_root_lower'])>0,
                    'C_CI covariance step predecessor/coverage')
                steps+=1
            segments.append(dict(segment=segment,seconds=r['elapsed_seconds'],
                maximum_covariance_error=maximum(r['covariance_errors']),result=sources.ref(name)))
        cases.append(dict(kind=kind,complete=[r['segment'] for r in segments]==['event',*cov.ROLES],segments=segments))
    return dict(required_transforms=list(cov.KINDS),cases=cases,native_events=events,target_steps=steps,
        covariance_complete=all(c['complete'] for c in cases),transformed_horizon=1,
        source_prefix_rerun=False,full_joint_roots=True,user_accepted=False,aggregate_closed=False,
        inputs=sources.ref(cov.INPUTS),plan=sources.ref(cov.PLAN),review=sources.ref(cov.REVIEW))


def larger_cci_runtime_view(sources):
    """C_CI segment status: pinned retained data only, no root or trajectory."""
    import p984h_cci as run
    for name in LARGER_RUNTIME_CCI_SOURCES:sources.raw(name)
    m=sources.read(run.INPUTS)
    require(m==run.seal(m) and m['family']=='C_CI','C_CI manifest')
    for name,sha in m['source_bindings'].items():
        require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha,'C_CI execution source drift: '+name)
    records={}
    for segment in run.CAPS:
        name=run.path(segment)
        if name not in LARGER_RUNTIME_CCI_SOURCES:continue
        r=json.loads(lzma.decompress(sources.raw(name)))
        require(r==run.seal(r) and r['manifest_digest']==m['record_digest'] and r['segment']==segment
            and r['outcome']=='completed' and not r['user_accepted'] and not r['aggregate_closed'],
            'C_CI retained segment identity/scope')
        require(r['seconds']<=m['caps'][segment],'C_CI segment cap')
        records[segment]=r
    require('source' in records,'C_CI source not executed')
    prefix=records['source']['execution']
    require(prefix['accepted_source_full_parity'] and prefix['native_steps']==1 and prefix['native_events']==0
        and prefix['fresh']['trigger']['eligible'],'C_CI source scope/trigger')
    if 'event' in records:
        e=records['event']['execution']
        require(e['predecessor_digest']==records['source']['record_digest'] and e['native_events']==1
            and e['native_steps']==0 and e['target']==prefix['fresh']['target']
            and len(e['admissions'])==2,'C_CI event predecessor/target')
    continuation=None
    import p984h_cci_continuation as cont
    if cont.INPUTS in LARGER_RUNTIME_CCI_SOURCES:
        cm=sources.read(cont.INPUTS)
        require(cm==run.seal(cm) and 'event' in records
            and cm['event_record_digest']==records['event']['record_digest'],'C_CI continuation predecessor')
        for name,sha in cm['source_bindings'].items():
            require(hashlib.sha256(sources.current_bytes(name)).hexdigest()==sha,'C_CI continuation source drift: '+name)
        roles={}
        for role in cont.ROLES:
            predecessor=cm['event_record_digest'];rows=[];final_reads=0;refs=[]
            gap=False
            for step in (*range(1,11),'final'):
                name=cont.path(role,step)
                if name not in LARGER_RUNTIME_CCI_SOURCES:
                    gap=True;continue
                require(not gap,'C_CI continuation gap')
                r=json.loads(lzma.decompress(sources.raw(name)))
                require(r==run.seal(r) and r['schema']=='p984h-cci-continuation-segment-v1'
                    and r['manifest_digest']==cm['record_digest'] and r['role']==role and r['step']==step
                    and r['predecessor_digest']==predecessor and r['event_record_digest']==cm['event_record_digest'],
                    'C_CI continuation linkage')
                require(r['outcome']=='completed' and 0<=r['elapsed_seconds']<=cont.CAP
                    and r['native_events']==0 and not r['user_accepted'] and not r['aggregate_closed']
                    and not r['covariance_executed'] and r['detached_continuation'],'C_CI continuation scope')
                require(r['native_steps']==int(step!='final') and r['final_reads']==int(step=='final'),
                    'C_CI continuation credit')
                predecessor=r['record_digest'];refs.append(sources.ref(name))
                if step=='final':final_reads=1
                else:
                    bounds=r['resource_bounds']
                    require(cont.q(bounds['minimum_exact_root_lower'])>0 and bounds['minimum_represented_resource']>0
                        and not bounds['uniform_trajectory_enclosure'],'C_CI continuation positivity scope')
                    rows.append(dict(step=step,seconds=r['elapsed_seconds'],
                        minimum_resource=bounds['minimum_represented_resource'],
                        exact_root_lower_approx=float(cont.q(bounds['minimum_exact_root_lower'])),
                        maximum_root_resource_radius_approx=float(cont.q(bounds['maximum_root_resource_radius'])),
                        exact_resource_sum_delta=r['exact_resource_sum_delta']))
            roles[role]=dict(native_steps=len(rows),final_reads=final_reads,steps=rows,results=refs)
        continuation=dict(roles=roles,target_steps=sum(r['native_steps'] for r in roles.values()),
            final_reads=sum(r['final_reads'] for r in roles.values()),
            baseline_complete=all(r['native_steps']==10 and r['final_reads']==1 for r in roles.values()),
            local_joint_root_resource_enclosures=True,uniform_trajectory_enclosure=False,
            inputs=sources.ref(cont.INPUTS),plan=sources.ref(cont.PLAN),
            review=sources.ref(cont.BASE+'P9-8.4h-CCIContinuationReview.md'))
    covariance=larger_cci_covariance_view(sources,records['event']['record_digest']) if 'event' in records else None
    result = dict(family='C_CI',checkpoint='8.4h',
        status=('baseline_and_covariance_complete_pending_acceptance'
                if continuation and continuation['baseline_complete'] and covariance and covariance['covariance_complete'] else
                'baseline_complete_covariance_pending' if continuation and continuation['baseline_complete'] else
                'native_event_complete_continuation_pending' if 'event' in records else 'native_source_complete_event_pending'),
        native_steps=1,native_events=int('event' in records),
        target_steps=continuation['target_steps'] if continuation else 0,
        final_reads=continuation['final_reads'] if continuation else 0,continuation=continuation,
        source_full_joint_parity=True,fresh_trigger=prefix['fresh']['trigger'],
        native_numerics_rerun=False,covariance_executed=bool(covariance and covariance['native_events']),
        covariance=covariance,user_accepted=False,aggregate_closed=False,
        total_native_events=int('event' in records)+(covariance['native_events'] if covariance else 0),
        total_target_steps=(continuation['target_steps'] if continuation else 0)+(covariance['target_steps'] if covariance else 0),
        uniform_trajectory_enclosure=False,
        segments=[dict(segment=k,seconds=v['seconds'],result=sources.ref(run.path(k))) for k,v in records.items()],
        inputs=sources.ref(run.INPUTS),plan=sources.ref(run.PLAN))
    if continuation and continuation['baseline_complete'] and covariance and covariance['covariance_complete']:
        acceptance=sources.raw(BASE+'P9-8.4h-CCICovarianceReview.md').decode()
        require('## Scoped user acceptance' in acceptance and '2026-10-21' in acceptance,
            'missing scoped C_CI 8.4h acceptance')
        result.update(status='baseline_and_covariance_accepted',user_accepted=True,
            accepted_on='2026-10-21',acceptance_scope='C_CI P9-8.4h bounded baseline and eight covariance counterparts',
            acceptance=covariance['review'],original_execution_flags_unchanged=True)
    return result


def larger_aci_runtime_view(sources):
    from p984h_aci_status import view
    result=view(sources,LARGER_RUNTIME_ACI_SOURCES)
    if result['continuation']['baseline_complete'] and result['covariance'] and result['covariance']['covariance_complete'] and result['retained_checkpoint_review']:
        acceptance=sources.raw(BASE+'P9-8.4h-ACIReview.md').decode()
        require('## Scoped user acceptance' in acceptance and '**2026-10-26**' in acceptance,
            'missing scoped A_CI 8.4h acceptance')
        result.update(status='baseline_and_covariance_accepted',user_accepted=True,
            accepted_on='2026-10-26',acceptance_scope='A_CI P9-8.4h bounded baseline and eight covariance counterparts',
            acceptance=result['review'],original_execution_flags_unchanged=True)
    return result


def family_status(root, family, checkpoint="8.4c"):
    """Selected checkpoint/family only; not full-index or boundary validity."""
    import importlib
    import phase9_implementation_policy as policy
    require(checkpoint in ("8.4c", "8.4d", "8.4e", "8.4f", "8.4g", "8.4h"), "unknown family checkpoint")
    if checkpoint == '8.4h':
        require(family in ('C_OS','C_CI','A_CI'),'8.4h family not yet executed or declared')
        sources=Sources(root)
        return dict(schema='phase9_tranche8_family_status_v1',family=family,checkpoint=checkpoint,
            runtime={'C_OS':larger_cos_runtime_view,'C_CI':larger_cci_runtime_view,'A_CI':larger_aci_runtime_view}[family](sources),source_refs=sorted(sources.refs.values(),key=lambda r:r['path']),
            other_families_checked=False,native_trajectories_rerun=False)
    if checkpoint == "8.4g":
        if family=='A_PC':
            sources=Sources(root)
            return dict(schema='phase9_tranche8_family_status_v1',family=family,checkpoint=checkpoint,
                scope='whole_carrier_chart_and_first_step_research_not_native_or_acceptance',
                investigation=larger_apc_investigation(sources),
                source_refs=sorted(sources.refs.values(),key=lambda r:r['path']),
                other_families_checked=False,native_trajectories_rerun=False)
        if family=='A_CI':
            sources=Sources(root)
            return dict(schema='phase9_tranche8_family_status_v1',family=family,checkpoint=checkpoint,
                scope='exact_real_research_not_native_or_acceptance',
                investigation=larger_aci_investigation(sources),
                source_refs=sorted(sources.refs.values(),key=lambda r:r['path']),
                other_families_checked=False,native_trajectories_rerun=False)
        if family=='C_CI':
            sources=Sources(root)
            return dict(schema='phase9_tranche8_family_status_v1',family=family,checkpoint=checkpoint,
                scope='historical_research_plus_native_prerequisites_not_lifecycle_campaign',
                investigation=larger_cci_investigation(sources),
                source_refs=sorted(sources.refs.values(),key=lambda r:r['path']),
                other_families_checked=False,native_trajectories_rerun=False)
        require(family=='C_OS','larger prerequisite preflight not available for this family')
        sources=Sources(root)
        return dict(schema="phase9_tranche8_family_status_v1",family=family,checkpoint=checkpoint,
            scope="historical_bounds_plus_native_prerequisites_not_lifecycle_campaign",oracle=larger_view(sources,include_investigations=False)['family_results'][0],
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
            f"{boundary_summary} {oracle_summary} {preparation_summary} 8.4c is closed at 640/640 accepted history cells. 8.4d C_OS: 40 accepted history cells; C_CI: 40 accepted history cells. A_CI: 40 separately accepted native history cells; A_PC: frozen-source D94 exclusion accepted; resource-only companion passes target preflight but fails the fresh trigger. History-only companion preserves fresh source eligibility but fails D94 target positivity at step one. The full coupled campaign now passes all twenty A_PC cases: forty histories, four hundred native continuation steps and forty final reads; nineteen new cases plus exact pilot reuse. Forty A_PC cells are accepted. The first-group .d checkpoint is closed at 160 accepted cells. Prior failures remain separate. First-group .e C_OS has 20 accepted covariance cells on two layouts and five transforms. C_CI has 20 accepted full-joint-root covariance cells. A_CI has 20 accepted covariance cells with unsigned history/writer and full joint roots. A_PC has 20 accepted covariance cells on D59/D94 using the accepted coupled history/allocation source, with unsigned W and signed carrier transport/archive/reset. First-group .e is accepted at 80/80 history cells; C_OS .f now supplies 24 accepted chart-covariance history cells, separately from four frozen mechanical-plan executions. C_CI .f supplies 24 accepted full-joint-root chart cells, with independent pointwise interval certificates and explicit frozen-plan reuse. A_CI .f supplies 24 accepted unsigned-history/writer/full-joint-root chart cells, with pointwise root/output certificates and explicit frozen-plan reuse. A_PC .f supplies 24 accepted full-chart history/carrier cells on coupled D59/D94 witnesses, with archives, explicit loss, zero target initialization and ZOH/log-W continuation. The first group is accepted at 96/96 cells; .g prerequisites remain family-scoped; C_OS .h has two passing native source steps and one separately bound successful event in 871.507 s under the unchanged 1200 s cap. The original timeout is summarized only; its failed artifact was removed. Native target continuation now completes ten steps per role and two fresh final reads. The bounded baseline and all eight larger covariance counterparts are accepted for C_OS on 2026-10-21; other families and aggregate 8.4h remain open, with no uniform trajectory enclosure. Other .f families remain unexecuted. No uniform neighborhood follows. Six families remain native-unexecuted. 8.4d–i and 8.5/8.6 remain open. Larger-graph preparation is not runtime acceptance; "
            "public lifecycle and forty disabled cells remain Tranche 9 work. No new support or execution permission follows from this view.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "check", "verify-retained"), default="status", nargs="?")
    parser.add_argument("--family", choices=("A_OS", "C_OS", "C_CI", "A_CI", "C_PC", "A_PC", "C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"))
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--checkpoint", choices=("8.4b", "8.4c", "8.4d", "8.4e", "8.4f", "8.4g", "8.4h"), default="8.4b")
    parser.add_argument("--oracle", action="store_true", help="check A_OS or A_CI 8.4c independent oracle scope, not native execution")
    parser.add_argument("--preparation", action="store_true", help="check C_CI 8.4c target preparation, not a native campaign")
    args = parser.parse_args()
    if args.checkpoint == '8.4h':
        require(args.family in ('C_OS','C_CI','A_CI') and args.action=='status' and not args.recheck_numerics
            and not args.oracle and not args.preparation,'select C_OS/C_CI/A_CI 8.4h read-only status; explicit numerical execution uses its family runner')
        print(json.dumps(family_status(ROOT,args.family,args.checkpoint),indent=2));return
    if args.checkpoint == '8.4g':
        if args.family in ('C_CI','A_CI'):
            require(args.action in ('status','verify-retained') and not args.recheck_numerics
                and not args.oracle and not args.preparation,'select C_CI/A_CI read-only scalar investigation')
            print(json.dumps(family_status(ROOT,args.family,args.checkpoint),indent=2))
            return
        require(args.family=='C_OS' and not args.oracle and not args.preparation,'select C_OS prerequisite preflight')
        require(args.action in ('status','verify-retained') and
            (not args.recheck_numerics or args.action=='verify-retained'),'invalid prerequisite mode')
        if args.action=='status':print(json.dumps(family_status(ROOT,args.family,args.checkpoint),indent=2))
        else:
            # Optional interval recomputation remains a historical research check;
            # ordinary verification checks the native successor without reruns.
            script = 'p984g_cos_bounds.py' if args.recheck_numerics else 'p984g_cos_native.py'
            subprocess.run([sys.executable,str(ROOT/HERE/'tranche8_retained.py'),
                str(ROOT/HERE/script),'check',*(['--recheck-numerics'] if args.recheck_numerics else [])],cwd=ROOT,check=True)
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
