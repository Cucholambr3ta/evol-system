#!/usr/bin/env bats

setup() {
    TEST_DIR=$(mktemp -d)
    export EVOL_DATA_DIR="$TEST_DIR"
    export EVOL_STATE_DB="$TEST_DIR/.evol/state.db"
    export EVOL_HOME="$TEST_DIR/.evol"
}

teardown() {
    if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
    fi
}

@test "init idempotent" {
    run bash "$BATS_TEST_DIRNAME/../scripts/evol-init.sh" "$TEST_DIR/project" --profile=core
    [ "$status" -eq 0 ]

    run bash "$BATS_TEST_DIRNAME/../scripts/evol-init.sh" "$TEST_DIR/project" --profile=core
    [ "$status" -eq 0 ]
}

@test "gate init hermetic" {
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" init
    [ "$status" -eq 0 ]
    [ -f "$TEST_DIR/.evol/.gate-key" ]
    [ -f "$TEST_DIR/.evol/.gate-log.jsonl" ]
}

@test "state init hermetic" {
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-state.py" init
    [ "$status" -eq 0 ]
    [ -f "$EVOL_STATE_DB" ]
}

@test "gate approve hermetic" {
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" init
    [ "$status" -eq 0 ]
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" approve --phase briefing
    [ "$status" -eq 0 ]
    [ -f "$TEST_DIR/.evol/.gate-log.jsonl" ]
}

@test "gate validate hermetic" {
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" init
    [ "$status" -eq 0 ]
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" approve --phase briefing
    [ "$status" -eq 0 ]
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" validate
    [ "$status" -eq 0 ]
}

@test "gate status hermetic" {
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" init
    [ "$status" -eq 0 ]
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" approve --phase briefing
    [ "$status" -eq 0 ]
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-gate.py" status
    [ "$status" -eq 0 ]
}

@test "state record and list hermetic" {
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-state.py" init
    [ "$status" -eq 0 ]
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-state.py" record-instinct --pattern "test-bats --confidence 0.9"
    [ "$status" -eq 0 ]
    run python3 "$BATS_TEST_DIRNAME/../scripts/evol-state.py" list
    [ "$status" -eq 0 ]
}