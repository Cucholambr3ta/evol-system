#!/usr/bin/env bats

@test "init idempotent" {
    run bash scripts/evol-init.sh /tmp/test-evol-init --profile=core
    [ "$status" -eq 0 ]

    run bash scripts/evol-init.sh /tmp/test-evol-init --profile=core
    [ "$status" -eq 0 ]
}

@test "gate init" {
    run python3 scripts/evol-gate.py init
    [ "$status" -eq 0 ]
}

@test "state init" {
    run python3 scripts/evol-state.py init
    [ "$status" -eq 0 ]
}