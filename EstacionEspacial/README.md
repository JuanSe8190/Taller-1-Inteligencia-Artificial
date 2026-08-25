# Taller 1 - Estacion Espacial

## Instalacion

Desde la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
```

## Interfaz recomendada

Para abrir el menu interactivo:

```bash
python menu.py
```

Desde el menu se puede seleccionar el punto del taller, el mapa, el modo de animacion, la velocidad, el zoom y la heuristica cuando aplique.

## Comandos directos

Si la interfaz no funciona en algun equipo, tambien se puede ejecutar el taller desde `main.py`.

Ejemplos:

```bash
python main.py -p DiagnosticProblem -f breadthFirstSearch -l radiationShortcut
python main.py -p ModuleRepairProblem -f uniformCostSearch -l moduleVault
python main.py -p SystemRepairProblem -f aStarSearch -h systemRepairHeuristic -l finalMaintenanceComplex
```

Modos utiles:

```bash
# Modo texto
python main.py -p DiagnosticProblem -f breadthFirstSearch -l radiationShortcut -t

# Sin animacion
python main.py -p DiagnosticProblem -f breadthFirstSearch -l radiationShortcut -q

# Paso a paso en ventana grafica
python main.py -p DiagnosticProblem -f breadthFirstSearch -l radiationShortcut -x -1
```

En modo paso a paso, use las flechas izquierda y derecha para retroceder o avanzar en la animacion.
