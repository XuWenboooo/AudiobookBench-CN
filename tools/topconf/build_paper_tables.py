"""Build labelled synthetic table metadata only."""
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    p=argparse.ArgumentParser(); p.add_argument('input',type=Path); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); x=json.loads(a.input.read_text())
    if x.get('data_source')!='SYNTHETIC_GOVERNANCE_DRY_RUN': raise SystemExit('FAIL: SYNTHETIC_ONLY input required')
    a.output.write_text(json.dumps({'label':'SYNTHETIC_DEMO_ONLY','table_contract':x.get('table_contract','metadata')},indent=2)+'\n'); print('PASS: SYNTHETIC_DEMO_ONLY')
if __name__=='__main__': main()
