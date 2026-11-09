from pathlib import Path
import json
import subprocess
import time
from redteam.harness import ROOT, AUDIT, dump

failures = []
for name in json.loads((AUDIT / 'cases.json').read_text()):
    status = AUDIT / name / 'status.json'
    if status.exists():
        print(f'Already completed: {name}', flush=True)
        continue
    print(f'Starting {name}', flush=True)
    started = time.monotonic()
    with (AUDIT / name / 'run.log').open('w') as handle:
        result = subprocess.run(['bash', f'redteam/{name}/run.sh'], cwd=ROOT,
                                stdout=handle, stderr=subprocess.STDOUT)
    if result.returncode:
        failures.append(name)
    print(f'Finished {name}: exit={result.returncode}, seconds={time.monotonic()-started:.1f}', flush=True)
dump(AUDIT / 'batch_status.json', {'failed_case_runners': failures})
