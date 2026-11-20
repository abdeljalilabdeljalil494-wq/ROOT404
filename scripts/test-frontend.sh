#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
cd frontend
npm run lint
npm test
npm run build
npm run test:e2e
npm audit --audit-level=moderate
