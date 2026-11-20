#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
"$PYTHON" - "$@" <<'PY'
import argparse,json
p=argparse.ArgumentParser()
p.add_argument('check',choices=['google-oauth','github-oauth','stack-browser','mobile-lan'])
p.add_argument('outcome',choices=['pass','fail','blocked'])
a=p.parse_args()
print(json.dumps({'check':a.check,'operator_reported_outcome':a.outcome,
  'classification':'MANUAL OPERATOR REPORT — not independently verified',
  'required_attachment':'Redacted checklist/screenshot; no OTP, code, state, tokens, email or secret'}))
raise SystemExit(0 if a.outcome=='pass' else 1)
PY
