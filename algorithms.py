
def fifo(num_frames, reference_string):
    frames = [None] * num_frames
    steps = []
    queue = []  # front = oldest page

    for page in reference_string:
        fault = False
        evicted = None

        if page not in frames:
            fault = True
            if None in frames:
                frames[frames.index(None)] = page
            else:
                oldest = queue.pop(0)
                evicted = oldest
                frames[frames.index(oldest)] = page
            queue.append(page)

        steps.append({"page": page, "frames": frames[:], "fault": fault, "evicted": evicted})

    return steps


def lru(num_frames, reference_string):
    frames = [None] * num_frames
    steps = []
    last_used = {}

    for i, page in enumerate(reference_string):
        fault = False
        evicted = None

        if page not in frames:
            fault = True
            if None in frames:
                frames[frames.index(None)] = page
            else:
                lru_page = min(
                    [f for f in frames if f is not None],
                    key=lambda p: last_used.get(p, -1)
                )
                evicted = lru_page
                frames[frames.index(lru_page)] = page

        last_used[page] = i
        steps.append({"page": page, "frames": frames[:], "fault": fault, "evicted": evicted})

    return steps


def optimal(num_frames, reference_string):
    frames = [None] * num_frames
    steps = []

    for i, page in enumerate(reference_string):
        fault = False
        evicted = None

        if page not in frames:
            fault = True
            if None in frames:
                frames[frames.index(None)] = page
            else:
                future = reference_string[i + 1:]
                furthest_page = None
                furthest_distance = -1

                for frame_page in frames:
                    if frame_page not in future:
                        furthest_page = frame_page
                        break
                    distance = future.index(frame_page)
                    if distance > furthest_distance:
                        furthest_distance = distance
                        furthest_page = frame_page

                evicted = furthest_page
                frames[frames.index(furthest_page)] = page

        steps.append({"page": page, "frames": frames[:], "fault": fault, "evicted": evicted})

    return steps


def get_stats(steps):
    total = len(steps)
    faults = sum(1 for s in steps if s["fault"])
    hits = total - faults
    return {
        "total_references": total,
        "page_faults": faults,
        "page_hits": hits,
        "fault_rate": round(faults / total * 100, 1),
        "hit_rate": round(hits / total * 100, 1),
    }
