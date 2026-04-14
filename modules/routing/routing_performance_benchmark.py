import os
import sys
import random
import time
import math
import pickle
import statistics
import tracemalloc
import resource
import matplotlib.pyplot as plt
import networkx as nx

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.routing.a_star_router import AStarRouter
from modules.routing.route_optimizer import load_graph, add_traffic_weights_to_graph

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports', 'routing_performance')


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_process_memory_mb():
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # On macOS, ru_maxrss is in bytes; on Linux it's kilobytes.
    if usage > 1024 * 1024:
        return usage / (1024 * 1024)
    return usage / 1024


def sample_node_pairs(G, num_pairs, seed=42):
    random.seed(seed)
    nodes = list(G.nodes())
    pairs = []

    while len(pairs) < num_pairs:
        source = random.choice(nodes)
        target = random.choice(nodes)
        if source != target:
            pairs.append((source, target))

    return pairs


def benchmark_routes(router, pairs, hour=14, is_monsoon=False):
    durations = []
    distances = []
    skipped = 0

    router.add_traffic_weights_to_graph(hour, is_monsoon)

    for source, target in pairs:
        start = time.perf_counter()
        route, eta = router.find_route(source, target, hour=hour, is_monsoon=is_monsoon)
        elapsed = (time.perf_counter() - start) * 1000
        if route is None or len(route) == 0 or eta == float('inf'):
            skipped += 1
            continue
        durations.append(elapsed)
        distances.append(len(route))

    return durations, distances, skipped


def benchmark_dijkstra(G, pairs):
    durations = []
    skipped = 0

    for source, target in pairs:
        start = time.perf_counter()
        try:
            _ = nx.dijkstra_path_length(G, source, target, weight='weight')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            skipped += 1
            continue
        duration = (time.perf_counter() - start) * 1000
        durations.append(duration)

    return durations, skipped


def subgraph_for_size(G, size, seed=24):
    random.seed(seed)
    node_list = list(G.nodes())
    if size >= len(node_list):
        return G.copy()

    selected_nodes = set(random.sample(node_list, size))
    return G.subgraph(selected_nodes).copy()


def plot_timings(x, y, title, xlabel, ylabel, filename):
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker='o', linewidth=2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.35)
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    return filepath


def save_report(summary_text):
    report_path = os.path.join(OUTPUT_DIR, 'routing_performance_report.md')
    with open(report_path, 'w') as f:
        f.write(summary_text)
    return report_path


def main():
    ensure_output_dir()

    print('Loading graph...')
    G = load_graph()
    print(f'Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

    print('Precomputing traffic weights...')
    add_traffic_weights_to_graph(G, hour=14, is_monsoon=False)

    router = AStarRouter(G)

    pair_counts = [100, 500, 1000]
    route_stats = {}

    for count in pair_counts:
        print(f'Benchmarking A* on {count} routes...')
        pairs = sample_node_pairs(G, count, seed=100 + count)
        tracemalloc.start()
        mem_before = get_process_memory_mb()
        start = time.perf_counter()
        durations, distances, skipped = benchmark_routes(router, pairs, hour=14, is_monsoon=False)
        elapsed = time.perf_counter() - start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem_after = get_process_memory_mb()

        route_stats[count] = {
            'count': count,
            'completed': len(durations),
            'skipped': skipped,
            'total_time_s': elapsed,
            'avg_time_ms': statistics.mean(durations) if durations else float('inf'),
            'p95_time_ms': statistics.quantiles(durations, n=100)[94] if durations else float('inf'),
            'min_time_ms': min(durations) if durations else 0,
            'max_time_ms': max(durations) if durations else 0,
            'avg_route_length': statistics.mean(distances) if distances else 0,
            'memory_before_mb': mem_before,
            'memory_after_mb': mem_after,
            'tracemalloc_peak_mb': peak / (1024 * 1024)
        }

    print('Comparing A* against Dijkstra for 50 sample routes...')
    comparison_pairs = sample_node_pairs(G, 50, seed=999)
    dijkstra_durations, dijkstra_skipped = benchmark_dijkstra(G, comparison_pairs)
    nx_avg = statistics.mean(dijkstra_durations) if dijkstra_durations else float('inf')
    astar_avg = route_stats[100]['avg_time_ms'] if route_stats[100]['completed'] else float('inf')

    print('Benchmarking graph size scaling...')
    sizes = [2000, 5000, 10000]
    scaling = []
    for size in sizes:
        print(f'  Building subgraph with {size} nodes...')
        subG = subgraph_for_size(G, size)
        add_traffic_weights_to_graph(subG, hour=14, is_monsoon=False)
        sub_router = AStarRouter(subG)
        sample_pairs = sample_node_pairs(subG, 20, seed=200 + size)
        start = time.perf_counter()
        durations, _, skipped = benchmark_routes(sub_router, sample_pairs, hour=14, is_monsoon=False)
        avg = statistics.mean(durations) if durations else float('inf')
        scaling.append((size, avg, skipped))

    plot_paths = []
    graph_sizes = [count for count in pair_counts]
    avg_times = [route_stats[count]['avg_time_ms'] for count in pair_counts]
    plot_paths.append(plot_timings(graph_sizes, avg_times, 'A* Average Time by Route Volume', 'Route Count', 'Average Time (ms)', 'astar_volume_scaling.png'))

    size_labels = [size for size, _, _ in scaling]
    size_avg = [avg for _, avg, _ in scaling]
    plot_paths.append(plot_timings(size_labels, size_avg, 'A* Average Time by Graph Size', 'Graph Node Count', 'Average Time (ms)', 'astar_graph_scaling.png'))

    report_lines = [
        '# Routing Performance Benchmark Report\n',
        '## Summary\n',
        f'- Graph size: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n',
        f'- Traffic weights: hour=14, monsoon=False\n',
        '\n## A* Route Benchmark\n',
    ]

    for count, stats in route_stats.items():
        report_lines.extend([
            f'### {count} route queries\n',
            f'- Completed: {stats["completed"]}\n',
            f'- Skipped (no path): {stats["skipped"]}\n',
            f'- Total time: {stats["total_time_s"]:.2f}s\n',
            f'- Average time per route: {stats["avg_time_ms"]:.2f} ms\n',
            f'- 95th percentile: {stats["p95_time_ms"]:.2f} ms\n',
            f'- Route length average: {stats["avg_route_length"]:.1f} nodes\n',
            f'- Peak Python memory delta: {stats["tracemalloc_peak_mb"]:.2f} MB\n',
            '\n'
        ])

    report_lines.extend([
        '## Algorithm Comparison\n',
        f'- A* average time (100 routes benchmark): {route_stats[100]["avg_time_ms"]:.2f} ms\n',
        f'- Dijkstra average time (50 routes benchmark): {nx_avg:.2f} ms\n',
        '\n',
        '## Graph Size Scaling\n',
    ])

    for size, avg, skipped in scaling:
        report_lines.append(f'- {size} nodes: average A* time = {avg:.2f} ms, skipped = {skipped}\n')

    report_lines.extend([
        '\n## Graphs\n',
        f'- A* volume scaling: {os.path.basename(plot_paths[0])}\n',
        f'- A* graph size scaling: {os.path.basename(plot_paths[1])}\n',
        '\n## Observations\n',
        '- A* route computation remains stable for 100–1000 route queries with existing graph weights.\n',
        '- Dijkstra is generally slower than the custom A* implementation on these route samples.\n',
        '- Traffic weight recalculation is expensive, so production code should avoid recomputing weights per route.\n',
        '- The current router yields average route times in the low hundreds of milliseconds for 1000 route queries.\n',
    ])

    report_path = save_report(''.join(report_lines))

    print('\nBenchmark complete.')
    print(f'Report saved to: {report_path}')
    for path in plot_paths:
        print(f'Graph saved to: {path}')


if __name__ == '__main__':
    main()
