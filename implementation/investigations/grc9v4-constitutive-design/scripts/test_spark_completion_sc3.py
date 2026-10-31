"""Bounded SC-3 design and surface pressure. No native trajectory campaign."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
import jsonschema
from unittest.mock import patch

import check_spark_completion_sc3 as check
from grcv4_explorer import spark_completion as sc
from grcv4_explorer import basin
from grcv4_explorer.canonical import digest, record_digest
from grcv4_explorer.errors import SourceAdmissionError
from grcv4_explorer.tooling import managed_node, tool_environment

ROOT, SIDE = check.ROOT, check.SIDE
TOOL = SIDE / "tool"
sys.path.insert(0,str(ROOT / check.INV / "research"))
from spark_completion_schema import validate_structure


def example():
    """Synthetic envelope for schema pressure ONLY, never scientific evidence."""
    bound = lambda name: dict(path="implementation/"+name+".json",sha256="0"*64)
    node = lambda name: dict(kind="str",value=name)
    basin = lambda name: dict(anchor=node(name),members=[node(name),node(name+"2")])
    policy = dict(schema_version="grc9v4-child-completion-policy-v2",
        policy_id="grc9v4-certified-geometric-child-basins-v1",landscape_sign=-1,
        epsilon_gradient="1/100",epsilon_Hessian="1/10",minimum_resource="1/10",contrast="1/10",
        minimum_beats=2,minimum_elapsed="64",step_duration="32",
        trap_policy_id="full_physical_map_strict_contraction_v1",numerical_policy_id="explicit_test_policy_v1")
    proof = dict(certificate=bound("trap"),equation_binding=bound("equation"),state_channels=["C"],
        constraints=bound("charge"),domain=bound("domain"),center=bound("center"),norm_id="declared_norm",
        q="9/10",image_margin="1/1000",numerical_policy_id=policy["numerical_policy_id"],
        full_step_error="1/10000",full_step_certificate=bound("full-step"),
        constraint_certificate=bound("constraint"),diagnostic_certificate=bound("diagnostic"))
    observations=[dict(role="current",receipt=bound("receipt"+str(i)),step_index=i,time=str(i*32),duration="32",
        state=bound("state"+str(i)),read=bound("read"+str(i)),operands=bound("operands"+str(i)),
        diagnostic_certificate=bound("diagnostic"+str(i)),descendants=[basin("a"),basin("p")]) for i in (1,2)]
    return policy,dict(schema_version="grc9v4-child-completion-evidence-v2",policy_digest=digest(policy),
        event_lineage_id="actual_event_occurrence",decision="completed",source_capture=bound("source"),
        event_receipt=bound("event"),parent=basin("p"),expanded_vertex=node("v"),target_profile_id="target",
        target_graph_id="graph",lineage=bound("lineage"),proof=proof,observations=observations,
        local_gain=1,new_child_anchors=[node("a")])


class SC3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = sc.load_predecessor(ROOT,SIDE)
        cls.current = sc.load_spark_completion_forensic_context(ROOT,SIDE)
        cls.view = sc.spark_completion_authority(ROOT,SIDE)

    def test_graph_preservation_claim_classes_and_debt_routing(self):
        for key,value in self.old.nodes.items():
            self.assertEqual(self.current.nodes[key],value)
        edges={r["edge_id"]:r for r in self.current.propagation_edges}
        for old in self.old.propagation_edges:
            self.assertEqual(edges[old["edge_id"]],old)
        self.assertEqual(len(self.current.nodes)-len(self.old.nodes),25)
        for trace in self.view["debts"]:
            self.assertIn("bounded",trace["rows"][0]["payload"]["status"])
            self.assertTrue(any(r["classification"]=="forward_verification_routing"
                and r["payload"]["status"]=="pending_forward" for r in trace["rows"]))
        by_id={r["query"]["contract_id"]:r["rows"][0]["payload"] for r in self.view["contracts"]}
        self.assertEqual(by_id["SC-EC-FULL-STATE-RETURN"]["support_disposition"],
                         ["accepted_bounded_conditional_science"])
        self.assertEqual(by_id["SC-EC-QUARTIC-SITE"]["support_disposition"],
                         ["accepted_bounded_scientific_design"])
        self.assertEqual(check.check()["claims"],7)

    def test_rehashed_authority_and_source_drift_rejected(self):
        original=sc.load_json_object
        for defect in ("definition","native","claim_class","debt","admission","propagation"):
            def altered(path):
                v=deepcopy(original(path))
                if path==ROOT/sc.SOURCE:
                    if defect=="definition":v["contracts"][0]["normative_equation_or_contract"]="strongest route only"
                    if defect=="native":v["scope"]["native_completed_spark_support"]=True
                    if defect=="claim_class":v["claims"][2]["claim_class"]="normative"
                    if defect=="debt":v["debts"][0]["remaining_work"]=[]
                if path.name==sc.ADMISSION and defect=="admission":v["graph_digest"]="0"*64
                if path==ROOT/sc.MANIFEST and defect=="propagation":v["contract_ids"].pop()
                if "record_digest" in v:v["record_digest"]=record_digest(v,"record_digest")
                return v
            with self.subTest(defect=defect),patch.object(sc,"load_json_object",altered):
                with self.assertRaises(SourceAdmissionError):sc.spark_completion_authority(ROOT,SIDE)
        sha=basin.file_sha256
        with patch.object(basin,"file_sha256",lambda p: "0"*64 if p==ROOT/"specs/grc-9-v4-spark-completion.md" else sha(p)):
            with self.assertRaises(SourceAdmissionError):sc.spark_completion_authority(ROOT,SIDE)
        with self.assertRaises(KeyError):sc.spark_completion_source(ROOT,SIDE,"../outside")

    def test_schema_and_semantic_boundaries(self):
        p,v=example()
        self.assertEqual(validate_structure(v,policy=p),"structure_only_not_scientific_or_native_admission")
        site=dict(schema_version="grcv4-homogeneous-quartic-site-v1",evaluator_id="homogeneous_quartic_site_v1",
            c0="2",a="1",mu="1",units_id="resource_potential_site_units_v1")
        validate_structure(site)
        for edit in ({"mu":"0"},{"a":"2"},{"c0":"4/2"},{"mu":"NaN"},{"node_wells":{}},{"c0":2.0}):
            with self.subTest(edit=edit),self.assertRaises((ValueError,jsonschema.ValidationError)):validate_structure({**site,**edit})
        mutations=[lambda x:x["proof"].update(q="1"),lambda x:x["proof"].update(full_step_error="1/1000"),
            lambda x:x["proof"].pop("constraint_certificate"),lambda x:x["proof"].update(state_channels=[]),
            lambda x:x.update(local_gain=2),lambda x:x["observations"][1].update(role="reset"),
            lambda x:x["observations"][1].update(step_index=1),
            lambda x:x["observations"][1].update(receipt=x["observations"][0]["receipt"]),
            lambda x:x["observations"].pop(),lambda x:x["parent"]["anchor"].update(kind="int",value=True),
            lambda x:x["parent"]["members"].append(x["parent"]["members"][0]),
            lambda x:x["source_capture"].update(path="implementation/../private.json"),
            lambda x:x.update(schema_version="grc9v4-child-completion-evidence-v1"),
            lambda x:x.update(fallback="accept_sample"),lambda x:x["proof"].update(q="9/10",numerical_policy_id="different")]
        for i,edit in enumerate(mutations):
            bad=deepcopy(v);edit(bad)
            with self.subTest(mutation=i),self.assertRaises((ValueError,jsonschema.ValidationError)):validate_structure(bad,policy=p)
        pending={k:v[k] for k in ("schema_version","policy_digest","event_lineage_id")}
        pending.update(decision="unresolved",reason="full-map numerical certificate absent")
        validate_structure(pending)
        with self.assertRaises((ValueError,jsonschema.ValidationError)):validate_structure({**pending,"local_gain":1})

    def test_http_notebook_and_fail_closed(self):
        book=json.loads((TOOL/"notebooks/phase9_verification.ipynb").read_bytes())
        cell=next(c for c in book["cells"] if c.get("id")=="spark-completion-authority")
        ns={"repo_root":ROOT};code=compile("".join(cell["source"]),"spark-cell","exec")
        exec(code,ns);self.assertEqual(ns["phase9_spark_completion"],self.view)
        with patch.object(sc,"spark_completion_authority",side_effect=SourceAdmissionError("held")):
            with self.assertRaises(SourceAdmissionError):exec(code,ns)
        self.assertIsNone(ns["phase9_spark_completion"])
        spec=importlib.util.spec_from_file_location("sc3_server",TOOL/"scripts/serve_phase9.py")
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        h=server.Handler.__new__(server.Handler);codes=[]
        h.send_response=codes.append;h.send_header=lambda *a:None;h.end_headers=lambda:None
        h.path="/api/spark-completion";h.wfile=BytesIO();h.do_GET()
        self.assertEqual(codes[-1],200);self.assertEqual(json.loads(h.wfile.getvalue()),self.view)
        h.wfile=BytesIO()
        with patch.object(server,"spark_completion_authority",side_effect=SourceAdmissionError("held")):h.do_GET()
        self.assertEqual(codes[-1],503);self.assertEqual(set(json.loads(h.wfile.getvalue())),{"error"})
        h.path="/api/spark-completion/source?path=specs%2Fgrc-9-v4-spark-completion.md"
        h.wfile=BytesIO();h.do_GET();self.assertEqual(codes[-1],200)
        self.assertEqual(h.wfile.getvalue(),(ROOT/"specs/grc-9-v4-spark-completion.md").read_bytes())

    def test_browser_and_stale_output(self):
        js=r'''
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalBasin} from './basin.js';
import {checkedSparkCompletion,sparkCompletionLoader} from './spark-completion.js';
const value=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedSparkCompletion(value),value);
for(const edit of [v=>v.scope.native_completed_spark_support=true,v=>v.scope.scientific_family='all',
 v=>v.scope.G4_accepted=true,v=>v.debts.pop(),v=>v.contracts.pop()]) {
 const bad=structuredClone(value);edit(bad);delete bad.projection_digest;
 bad.projection_digest=createHash('sha256').update(canonicalBasin(bad)).digest('hex');
 await assert.rejects(checkedSparkCompletion(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=sparkCompletionLoader(output,status,async()=>({ok,json:async()=>value}),tag=>({tag,append(){}}));
await load();assert.ok(output.children.length>10);assert.match(status.textContent,/Native work follows separately/);
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="spark-completion-refresh"/);
console.log('SC3_BROWSER_PASS');
'''
        r=subprocess.run([str(managed_node()),"--input-type=module","-e",js],cwd=TOOL/"phase9-web",
            input=json.dumps(self.view),text=True,capture_output=True,timeout=30,env=tool_environment())
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),"SC3_BROWSER_PASS")


if __name__ == "__main__":
    unittest.main()
