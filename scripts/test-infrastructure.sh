#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
case "${1:-}" in
  --native) "$PYTHON" scripts/verify_infrastructure.py ;;
  --external) "$PYTHON" scripts/verify_external_integrations.py ;;
  *) printf '%s\n' 'Choose --native (configured disposable local PG/Redis/SMTP lab) or --external (explicit private opt-in staging probes). See docs/RC_VERIFICATION.md'; exit 2 ;;
esac
