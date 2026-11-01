"""Authenticate the earlier C-family research projection without numerical runs."""
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[4]
SIDE=ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool'
sys.path.insert(0,str(SIDE/'tool/src'))
from grcv4_explorer.spark_earlier_c import spark_earlier_c_status


def check():
    view=spark_earlier_c_status(ROOT,SIDE)
    return dict(status='passed_earlier_C_research_source_integrity',projection_digest=view['projection_digest'],
        comparison=view['report']['comparison'],numerical_runs=0,accepted_authority=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',required=True,action='store_true');p.parse_args()
    print(json.dumps(check(),indent=2))
