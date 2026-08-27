from typing import Tuple
from collections import deque
 
from algorithms.problems import SystemRepairProblem
from world.game import Directions, Actions

# Valor finito grande que representa "inalcanzable". Se usa en vez de
# float("inf") para que las sumas sigan siendo enteras y para no ensuciar las
# estadisticas que imprime la interfaz.
UNREACHABLE = 10 ** 9

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def _manhattanDistance(a, b):
    """Distancia Manhattan |dx| + |dy| entre dos celdas."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
 
 
def _euclideanDistance(a, b):
    """Distancia euclidiana sqrt(dx^2 + dy^2) entre dos celdas."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
 
 
def _phaseDistance(state, problem, distance):
    """
    Aplica la regla de fase y devuelve la distancia al objetivo obligatorio.
 
    state     : (position, hasKit, pendingSystems)
    problem   : SystemRepairProblem (aporta kitPosition y controlPosition)
    distance  : funcion de distancia a usar (_manhattanDistance o _euclideanDistance)
    """

    position, hasKit, pendingSystems = state
 
    if not hasKit:
        return distance(position, problem.kitPosition)

    if pendingSystems:
        return min(distance(position, system) for system in pendingSystems)
 
    return distance(position, problem.controlPosition)
 
 
def manhattanHeuristic(state, problem):
    """
    Punto 5b. Distancia Manhattan hasta el objetivo obligatorio de la fase.
 
    Admisible: el robot solo se mueve en 4 direcciones y cada paso cuesta 1,
    asi que la distancia Manhattan nunca supera el numero real de pasos hasta
    esa celda; y esa celda es de visita obligatoria antes de terminar la
    mision. Por lo tanto h(n) <= h*(n).
 
    Consistente: dentro de una misma fase, un paso cambia la distancia
    Manhattan en a lo sumo 1, luego h(n) <= 1 + h(n'). En los pasos que cambian
    de fase (entrar a K o reparar un T) el termino que desaparece vale
    exactamente 1, de modo que se obtiene la igualdad y no una violacion.
    """
    return _phaseDistance(state, problem, _manhattanDistance)
 
 
def euclideanHeuristic(state, problem):
    """
    Punto 5c. Igual que la anterior pero con distancia euclidiana.
 
    Tambien es admisible y consistente, por el mismo argumento con la norma
    euclidiana (un paso desplaza exactamente 1 en esa norma).
 
    Es ESTRICTAMENTE MAS DEBIL que Manhattan: como no hay movimiento diagonal,
    siempre se cumple  euclidiana <= Manhattan <= costo real.  Por eso se
    espera que expanda mas nodos que manhattanHeuristic en todos los mapas.
    """
    return _phaseDistance(state, problem, _euclideanDistance)
 

 
def _mapDistances(problem, source):
    """
    Distancias reales (minimo numero de pasos, esquivando muros) desde `source`
    hacia todas las celdas transitables del mapa. Es un BFS estandar.
 
    El resultado se memoiza en problem.heuristicInfo["mapDistances"], porque la
    topologia del mapa no cambia durante la busqueda: basta un BFS por punto de
    interes (K, C y cada T), es decir a lo sumo |T| + 2 recorridos O(celdas).
    """
  
    cache = problem.heuristicInfo.setdefault("mapDistances", {})
    if source in cache:
        return cache[source]
 
    walls = problem.walls
    distances = {source: 0}
    queue = deque([source])
 
    while queue:
        current = queue.popleft()
        currentDistance = distances[current]
 
        for direction in [
            Directions.NORTH,
            Directions.SOUTH,
            Directions.EAST,
            Directions.WEST,
        ]:
            dx, dy = Actions.directionToVector(direction)
            neighbour = (int(current[0] + dx), int(current[1] + dy))

            if walls[neighbour[0]][neighbour[1]]:
                continue
            if neighbour in distances:
                continue
 
            distances[neighbour] = currentDistance + 1
            queue.append(neighbour)
 

    cache[source] = distances
    return distances
 
 
def _mapDistance(problem, poi, cell):
    """
    Distancia real entre un punto de interes `poi` (K, C o un T) y una celda
    cualquiera `cell`. UNREACHABLE si no hay camino.
 
    Importante: el BFS SIEMPRE se lanza desde el punto de interes, nunca desde
    la celda donde esta el robot. Como la distancia es simetrica el resultado
    es el mismo, pero asi el numero de BFS distintos queda acotado por
    |T| + 2 en vez de crecer con el numero de celdas visitadas.
    """
    return _mapDistances(problem, poi).get(cell, UNREACHABLE)
 
 
def _minimumSpanningTree(problem, nodes):
    """
    Peso del arbol de recubrimiento minimo sobre `nodes` (algoritmo de Prim),
    usando distancias reales del mapa como pesos de arista.
 
    `nodes` es una tupla; se usa tal cual como llave de memoizacion, asi que el
    llamador debe pasar siempre el mismo orden para el mismo conjunto.
    """

    cache = problem.heuristicInfo.setdefault("mstCache", {})
    if nodes in cache:
        return cache[nodes]
 
    nodeList = list(nodes)
    size = len(nodeList)

    if size <= 1:
        cache[nodes] = 0
        return 0
 

    distance = [[0] * size for _ in range(size)]
    for i in range(size):
        fromNode = _mapDistances(problem, nodeList[i])
        for j in range(size):
            distance[i][j] = fromNode.get(nodeList[j], UNREACHABLE)
 

    inTree = [False] * size          
    cheapest = [UNREACHABLE] * size  
    cheapest[0] = 0
    total = 0
 
    for _ in range(size):
        chosen = -1
        for candidate in range(size):
            if not inTree[candidate]:
                if chosen == -1 or cheapest[candidate] < cheapest[chosen]:
                    chosen = candidate
 
        inTree[chosen] = True
        total += cheapest[chosen]
 
        for other in range(size):
            if not inTree[other] and distance[chosen][other] < cheapest[other]:
                cheapest[other] = distance[chosen][other]
 
    cache[nodes] = total
    return total
 
 
def systemRepairHeuristic(
    state: Tuple[Tuple, bool, Tuple], problem: SystemRepairProblem
):
    """
    Punto 5d. Heuristica propia para SystemRepairProblem.
 
    Formula
    -------
        h(n) = prefijo + max( entrada + MST(R) ,  max_t [ d(a,t) + d(t,C) ] )
 
    donde
        R        = {T pendientes} U {C}
        prefijo  = d(p, K) si aun no tiene el kit, 0 si ya lo tiene
        a        = K si aun no tiene el kit, la posicion actual si ya lo tiene
        entrada  = min_{x in R} d(a, x)
        d        = distancia REAL sobre el mapa (BFS, esquiva muros)
    """

    position, hasKit, pendingSystems = state
    controlPosition = problem.controlPosition
 
    if hasKit and not pendingSystems and position == controlPosition:
        return 0
 
    if hasKit:
        prefix = 0
        anchor = position
    else:
        prefix = _mapDistance(problem, problem.kitPosition, position)
        anchor = problem.kitPosition

    required = pendingSystems + (controlPosition,)
 
    anchorDistance = {node: _mapDistance(problem, node, anchor) for node in required}

    entryCost = min(anchorDistance.values())
    bound = entryCost + _minimumSpanningTree(problem, required)
 
    for system in pendingSystems:
        candidate = anchorDistance[system] + _mapDistance(
            problem, controlPosition, system
        )
        if candidate > bound:
            bound = candidate
 
    return prefix + bound
 