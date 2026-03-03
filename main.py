from typing import List
import math
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


app = FastAPI(title="Dynamic Route Optimization System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


# -----------------------------
# Global State
# -----------------------------

current_locations: List[List[float]] = []
current_vehicle_count: int = 1

base_time_matrix: List[List[int]] = []
traffic_multiplier_matrix: List[List[float]] = []


# -----------------------------
# Models
# -----------------------------

class OptimizeRequest(BaseModel):
    locations: List[List[float]]
    vehicle_count: int


class OptimizeResponse(BaseModel):
    routes: List[List[int]]
    total_distance: float
    total_time: float


class AddOrderRequest(BaseModel):
    location: List[float]


# -----------------------------
# Matrix Helpers
# -----------------------------

def build_base_matrix(locations):
    n = len(locations)
    matrix = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            lat1, lng1 = locations[i]
            lat2, lng2 = locations[j]
            dist = math.sqrt((lat1-lat2)**2 + (lng1-lng2)**2)
            matrix[i][j] = int(dist * 1000)

    return matrix


def build_cost_matrix():
    n = len(base_time_matrix)
    cost = [[0]*n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            cost[i][j] = int(base_time_matrix[i][j] * traffic_multiplier_matrix[i][j])

    return cost


# -----------------------------
# VRP Solver
# -----------------------------
def solve_vrp(cost_matrix, vehicle_count):

    n = len(cost_matrix)

    manager = pywrapcp.RoutingIndexManager(n, vehicle_count, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return cost_matrix[from_node][to_node]

    transit_callback = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback)

    # -------------------------------------------------
    # ADD DISTANCE DIMENSION (THIS IS THE FIX)
    # -------------------------------------------------

    routing.AddDimension(
        transit_callback,
        0,          # no slack
        15000,      # max distance per vehicle (TUNE THIS)
        True,       # start cumul to zero
        "Distance"
    )

    distance_dimension = routing.GetDimensionOrDie("Distance")
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_params)

    routes = []
    total_cost = 0

    if solution:
        for v in range(vehicle_count):
            index = routing.Start(v)
            route = []

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(node)
                prev = index
                index = solution.Value(routing.NextVar(index))
                total_cost += routing.GetArcCostForVehicle(prev, index, v)

            route.append(manager.IndexToNode(index))

            if len(route) > 2:
                routes.append(route)

    total_distance = total_cost / 1000.0

    return OptimizeResponse(
        routes=routes,
        total_distance=round(total_distance, 3),
        total_time=round(total_distance, 3),
    )


# -----------------------------
# API Endpoints
# -----------------------------

@app.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest):

    global current_locations
    global current_vehicle_count
    global base_time_matrix
    global traffic_multiplier_matrix

    current_locations = req.locations
    current_vehicle_count = req.vehicle_count

    base_time_matrix = build_base_matrix(current_locations)
    n = len(base_time_matrix)

    traffic_multiplier_matrix = [[1.0]*n for _ in range(n)]

    cost_matrix = build_cost_matrix()
    return solve_vrp(cost_matrix, current_vehicle_count)


@app.post("/simulate-traffic", response_model=OptimizeResponse)
def simulate_traffic():

    if not base_time_matrix:
        raise HTTPException(status_code=400, detail="Run optimize first")

    n = len(traffic_multiplier_matrix)

    # Decay congestion
    for i in range(n):
        for j in range(n):
            traffic_multiplier_matrix[i][j] = max(
                1.0,
                traffic_multiplier_matrix[i][j] - 0.05
            )

    # Hotspot
    hotspot = random.randint(1, n-1)

    for i in range(n):
        if i != hotspot:
            increase = random.uniform(0.4, 0.9)
            traffic_multiplier_matrix[hotspot][i] = min(
                3.0,
                traffic_multiplier_matrix[hotspot][i] + increase
            )
            traffic_multiplier_matrix[i][hotspot] = traffic_multiplier_matrix[hotspot][i]

    cost_matrix = build_cost_matrix()
    return solve_vrp(cost_matrix, current_vehicle_count)


@app.post("/add-order", response_model=OptimizeResponse)
def add_order(req: AddOrderRequest):

    global current_locations
    global base_time_matrix
    global traffic_multiplier_matrix

    if not current_locations:
        raise HTTPException(status_code=400, detail="Run optimize first")

    current_locations.append(req.location)

    base_time_matrix[:] = build_base_matrix(current_locations)
    n = len(base_time_matrix)

    traffic_multiplier_matrix = [[1.0]*n for _ in range(n)]

    cost_matrix = build_cost_matrix()
    return solve_vrp(cost_matrix, current_vehicle_count)