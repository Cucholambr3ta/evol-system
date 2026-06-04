#!/usr/bin/env bats
SCRIPT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)/scripts/evol-gitflow.sh"

setup() {
  TEST_REPO="$(mktemp -d)"
  cd "$TEST_REPO"
  git init -q
  git config user.email "test@evol.test"
  git config user.name "Test"
  git checkout -b main -q
  git commit --allow-empty -m "init" -q
}

teardown() { rm -rf "$TEST_REPO"; }

@test "setup dev: crea branch develop" {
  run bash "$SCRIPT" setup --mode=dev
  [ "$status" -eq 0 ]
  git rev-parse --verify develop
}

@test "setup collab: guarda modo collab" {
  run bash "$SCRIPT" setup --mode=collab
  [ "$status" -eq 0 ]
  [ "$(cat .evol/gitflow.mode)" = "collab" ]
}

@test "setup: modo invalido falla" {
  run bash "$SCRIPT" setup --mode=invalid
  [ "$status" -ne 0 ]
}

@test "setup: añade patrones Evol-DD al .gitignore" {
  run bash "$SCRIPT" setup --mode=dev
  [ "$status" -eq 0 ]
  grep -q "acuerdos/" .gitignore
  grep -q "memoria.md" .gitignore
  grep -q ".evol/" .gitignore
}

@test "setup: no duplica patrones en .gitignore" {
  bash "$SCRIPT" setup --mode=dev
  bash "$SCRIPT" setup --mode=dev
  count=$(grep -c "^acuerdos/$" .gitignore || true)
  [ "$count" -eq 1 ]
}

@test "sprint-start: crea branch feature/sprint-01-titulo" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=1 --title=auth
  [ "$status" -eq 0 ]
  git rev-parse --verify "feature/sprint-01-auth"
}

@test "sprint-start: sin --sprint falla" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --title=auth
  [ "$status" -ne 0 ]
}

@test "sprint-start: sin --title falla" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=1
  [ "$status" -ne 0 ]
}

@test "sprint-start: type=fix crea branch fix/sprint-01-titulo" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=1 --title=hotfix --type=fix
  [ "$status" -eq 0 ]
  git rev-parse --verify "fix/sprint-01-hotfix"
}

@test "sprint-start: normaliza numero de sprint a 2 digitos" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=3 --title=dashboard
  [ "$status" -eq 0 ]
  git rev-parse --verify "feature/sprint-03-dashboard"
}

@test "pre-push: EVOL_SKIP_PREPUSH=1 pasa sin checks" {
  bash "$SCRIPT" setup --mode=dev
  run env EVOL_SKIP_PREPUSH=1 bash "$SCRIPT" pre-push
  [ "$status" -eq 0 ]
}

@test "pre-push: bloquea si artefacto Evol-DD staged" {
  bash "$SCRIPT" setup --mode=dev
  mkdir -p acuerdos
  echo "test" > acuerdos/idea.md
  git add -f acuerdos/idea.md
  run bash "$SCRIPT" pre-push
  [ "$status" -ne 0 ]
  [[ "$output" == *"Artefactos Evol-DD"* ]]
}

@test "pre-push: pasa si staging limpio" {
  bash "$SCRIPT" setup --mode=dev
  echo "src code" > main.py
  git add main.py
  run env EVOL_SKIP_GITLEAKS=1 bash "$SCRIPT" pre-push
  [ "$status" -eq 0 ]
}

@test "status: muestra modo y branch" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" status
  [ "$status" -eq 0 ]
  [[ "$output" == *"dev"* ]]
}

@test "sprint-start sin repo git falla con mensaje claro" {
  tmp=$(mktemp -d)
  cd "$tmp"
  run bash "$SCRIPT" sprint-start --sprint=1 --title=test
  [ "$status" -ne 0 ]
  [[ "$output" == *"No es un repositorio git"* ]]
  rm -rf "$tmp"
}
