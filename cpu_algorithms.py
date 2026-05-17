"""
OS Simulator
algorithms.py — CPU Scheduling + Memory Allocation logic
"""

import copy
from collections import deque


# ═══════════════════════════════════════════════════════════════
# CPU SCHEDULING
# ═══════════════════════════════════════════════════════════════

def fcfs(processes):
    result = []
    time = 0
    plist = sorted(processes, key=lambda x: x["arrival"])
    for p in plist:
        start = max(time, p["arrival"])
        end = start + p["burst"]
        result.append({"name": p["name"], "start": start, "end": end})
        time = end
    return result


def sjf(processes):
    result = []
    plist = sorted(copy.deepcopy(processes), key=lambda x: x["arrival"])
    ready = []
    time = 0
    while plist or ready:
        while plist and plist[0]["arrival"] <= time:
            ready.append(plist.pop(0))
        if ready:
            ready.sort(key=lambda x: x["burst"])
            p = ready.pop(0)
            start = time
            end = start + p["burst"]
            result.append({"name": p["name"], "start": start, "end": end})
            time = end
        else:
            time += 1
    return result


def round_robin(processes, quantum):
    if quantum == 0:
        return []
    result = []
    plist = sorted(copy.deepcopy(processes), key=lambda x: x["arrival"])
    for p in plist:
        p["remaining"] = p["burst"]
    queue = deque()
    time = 0
    i = 0
    while queue or i < len(plist):
        while i < len(plist) and plist[i]["arrival"] <= time:
            queue.append(plist[i])
            i += 1
        if queue:
            p = queue.popleft()
            start = time
            run = min(quantum, p["remaining"])
            time += run
            p["remaining"] -= run
            result.append({"name": p["name"], "start": start, "end": time})
            while i < len(plist) and plist[i]["arrival"] <= time:
                queue.append(plist[i])
                i += 1
            if p["remaining"] > 0:
                queue.append(p)
        else:
            time += 1
    return result


def get_cpu_stats(schedule, processes):
    stats = []
    for p in processes:
        slices = [s for s in schedule if s["name"] == p["name"]]
        if not slices:
            continue
        finish = slices[-1]["end"]
        turnaround = finish - p["arrival"]
        waiting = turnaround - p["burst"]
        stats.append({
            "name": p["name"],
            "finish": finish,
            "turnaround": turnaround,
            "waiting": waiting
        })
    avg_wait = round(sum(s["waiting"] for s in stats) / len(stats), 1) if stats else 0
    avg_tat  = round(sum(s["turnaround"] for s in stats) / len(stats), 1) if stats else 0
    return stats, avg_wait, avg_tat


# ═══════════════════════════════════════════════════════════════
# MEMORY ALLOCATION
# ═══════════════════════════════════════════════════════════════

def first_fit(blocks, size):
    for i in range(len(blocks)):
        if blocks[i] >= size:
            blocks[i] -= size
            return i, blocks
    return -1, blocks


def next_fit(blocks, size, pointer):
    n = len(blocks)
    for i in range(n):
        idx = (pointer + i) % n
        if blocks[idx] >= size:
            blocks[idx] -= size
            return idx, blocks, (idx + 1) % n
    return -1, blocks, pointer


def best_fit(blocks, size):
    best = -1
    for i in range(len(blocks)):
        if blocks[i] >= size:
            if best == -1 or blocks[i] < blocks[best]:
                best = i
    if best != -1:
        blocks[best] -= size
    return best, blocks


def worst_fit(blocks, size):
    worst = -1
    for i in range(len(blocks)):
        if blocks[i] >= size:
            if worst == -1 or blocks[i] > blocks[worst]:
                worst = i
    if worst != -1:
        blocks[worst] -= size
    return worst, blocks


def run_memory_algo(algo_name, original_blocks, process_sizes):
    """
    Run a memory allocation algorithm and return step-by-step results.
    Each step: { size, block, status, memory }
    """
    blocks = original_blocks.copy()
    steps = []
    pointer = 0

    for size in process_sizes:
        if algo_name == "First Fit":
            idx, blocks = first_fit(blocks, size)
        elif algo_name == "Next Fit":
            idx, blocks, pointer = next_fit(blocks, size, pointer)
        elif algo_name == "Best Fit":
            idx, blocks = best_fit(blocks, size)
        elif algo_name == "Worst Fit":
            idx, blocks = worst_fit(blocks, size)
        else:
            idx = -1

        steps.append({
            "size":   size,
            "block":  idx,
            "status": "Allocated" if idx != -1 else "Failed",
            "memory": blocks.copy()
        })

    return steps

