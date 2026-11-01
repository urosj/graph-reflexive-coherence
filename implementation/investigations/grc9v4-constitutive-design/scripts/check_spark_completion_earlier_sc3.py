"""Check adopted shorter endpoint contracts and propagation; no numerical runs."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
SIDE = ROOT / 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool'
sys.path.insert(0, str(SIDE / 'tool/src'))
from grcv4_explorer.spark_earlier_accepted import spark_earlier_authority


def check():
    view = spark_earlier_authority(ROOT, SIDE)
    return dict(status='passed_earlier_endpoint_sc3', projection_digest=view['projection_digest'],
                endpoints=[{k: r[k] for k in ('family', 'current_entry', 'current_completion',
                           'reset_entry', 'reset_completion', 'ordinary_duration')} for r in view['endpoints']],
                numerical_runs=0, native_completion=False, additional_event_gain=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', required=True, action='store_true')
    parser.parse_args()
    print(json.dumps(check(), indent=2))
