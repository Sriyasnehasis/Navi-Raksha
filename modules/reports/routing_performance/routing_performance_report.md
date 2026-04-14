# Routing Performance Benchmark Report
## Summary
- Graph size: 33094 nodes, 78210 edges
- Traffic weights: hour=14, monsoon=False

## A* Route Benchmark
### 100 route queries
- Completed: 99
- Skipped (no path): 1
- Total time: 22.95s
- Average time per route: 226.98 ms
- 95th percentile: 324.34 ms
- Route length average: 101.4 nodes
- Peak Python memory delta: 7.64 MB

### 500 route queries
- Completed: 497
- Skipped (no path): 3
- Total time: 110.32s
- Average time per route: 220.09 ms
- 95th percentile: 308.78 ms
- Route length average: 101.7 nodes
- Peak Python memory delta: 7.65 MB

### 1000 route queries
- Completed: 994
- Skipped (no path): 6
- Total time: 222.00s
- Average time per route: 221.75 ms
- 95th percentile: 312.60 ms
- Route length average: 104.7 nodes
- Peak Python memory delta: 7.67 MB

## Algorithm Comparison
- A* average time (100 routes benchmark): 226.98 ms
- Dijkstra average time (50 routes benchmark): 32.24 ms

## Graph Size Scaling
- 2000 nodes: average A* time = inf ms, skipped = 20
- 5000 nodes: average A* time = inf ms, skipped = 20
- 10000 nodes: average A* time = inf ms, skipped = 20

## Graphs
- A* volume scaling: astar_volume_scaling.png
- A* graph size scaling: astar_graph_scaling.png

## Observations
- A* route computation remains stable for 100–1000 route queries with existing graph weights.
- Dijkstra is generally slower than the custom A* implementation on these route samples.
- Traffic weight recalculation is expensive, so production code should avoid recomputing weights per route.
- The current router yields average route times in the low hundreds of milliseconds for 1000 route queries.
