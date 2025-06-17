#!/bin/bash

DHUB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

dhub-cli() {
    cd $DHUB_ROOT/..
    PYTHONPATH="$DHUB_ROOT/src" python -m dhub.cli "$@"
}
dhub-server() {
    cd $DHUB_ROOT/..
    PYTHONPATH="$DHUB_ROOT/src" python -m dhub.server "$@"
}

export -f dhub-cli
export -f dhub-server

echo "dhub-cli and dhub-server exported..."
