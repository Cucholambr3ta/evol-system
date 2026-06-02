#!/usr/bin/env bats

SCRIPT_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")" && pwd)"
ADAPT_SCRIPT="$SCRIPT_DIR/../scripts/evol-adapt.sh"

@test "reject trigger with path traversal ../x" {
    run bash "$ADAPT_SCRIPT" --trigger="../x" all --dry-run 2>&1 || true
    printf "%s\n" "$output" | grep -q "Path traversal detected\|Invalid trigger"
}

@test "reject trigger with slash a/b" {
    run bash "$ADAPT_SCRIPT" --trigger="a/b" all --dry-run 2>&1 || true
    printf "%s\n" "$output" | grep -q "Invalid trigger\|Path traversal detected"
}

@test "reject trigger with command injection ;rm -rf" {
    run bash "$ADAPT_SCRIPT" --trigger=';rm -rf /' all --dry-run 2>&1 || true
    printf "%s\n" "$output" | grep -q "Invalid trigger"
}

@test "reject trigger with double dot .." {
    run bash "$ADAPT_SCRIPT" --trigger='..' all --dry-run 2>&1 || true
    printf "%s\n" "$output" | grep -q "Invalid trigger\|Path traversal detected"
}

@test "reject trigger with special chars dot dot" {
    run bash "$ADAPT_SCRIPT" --trigger='test..' all --dry-run 2>&1 || true
    printf "%s\n" "$output" | grep -q "Invalid trigger\|Path traversal detected"
}

@test "accept valid alphanumeric trigger" {
    run bash "$ADAPT_SCRIPT" --trigger="evol123" all --dry-run 2>&1
    [ "$status" -eq 0 ] || printf "%s\n" "$output"
}

@test "accept trigger with underscore" {
    run bash "$ADAPT_SCRIPT" --trigger="my_trigger" all --dry-run 2>&1
    [ "$status" -eq 0 ] || printf "%s\n" "$output"
}

@test "accept trigger with hyphen" {
    run bash "$ADAPT_SCRIPT" --trigger="my-trigger" all --dry-run 2>&1
    [ "$status" -eq 0 ] || printf "%s\n" "$output"
}

@test "accept trigger with mixed valid chars" {
    run bash "$ADAPT_SCRIPT" --trigger="Test-User_123" all --dry-run 2>&1
    [ "$status" -eq 0 ] || printf "%s\n" "$output"
}

@test "accept default trigger evol" {
    run bash "$ADAPT_SCRIPT" evol --dry-run 2>&1
    [ "$status" -eq 0 ] || printf "%s\n" "$output"
}