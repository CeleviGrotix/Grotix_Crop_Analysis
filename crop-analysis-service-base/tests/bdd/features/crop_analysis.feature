Feature: Clasificación del estado fenológico mediante Inteligencia Artificial
  Como usuario de Grotix
  Quiero que el sistema identifique automáticamente la etapa de crecimiento de mi planta
  Para conocer su progreso biológico sin necesidad de ser un experto en botánica

  # US24 - Escenario 1
  Scenario: Categorización exitosa de estados de crecimiento
    Given la Inteligencia Artificial ha recibido una imagen pre-procesada
    When se ejecute el algoritmo de inferencia
    Then el sistema debe clasificar la planta en una de las categorías definidas con base en el dataset de entrenamiento

  # US24 - Escenario 2
  Scenario: Umbral de confianza de la inferencia
    Given el modelo genera un resultado de clasificación
    When el nivel de confianza sea inferior al 75%
    Then el sistema debe marcar el estado como "Indeterminado"

  # US24 - Escenario 3
  Scenario: Actualización automática del perfil del cultivo
    Given el modelo ha identificado un cambio de etapa
    When se valide el resultado
    Then el sistema debe actualizar automáticamente el estado actual en la base de datos