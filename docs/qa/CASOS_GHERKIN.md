# Casos de Prueba Gherkin

```gherkin
Feature: Bootstrap de Proyectos
  Scenario: Inicializar proyecto válido
    Given manifest valido
    When ejecuto evol-init
    Then proyecto creado correctamente
```