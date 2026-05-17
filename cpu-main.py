"""
OS Simulator
main.py — UI, screens, and visualizers
"""

import pygame   # graphics library — handles window, drawing, keyboard, mouse
import sys      # used for sys.exit() to close the app cleanly
from cpu_algorithms import (
    fcfs, sjf, round_robin, get_cpu_stats,  # cpu scheduling functions
    run_memory_algo                          # memory allocation runner
)


# ═══════════════════════════════════════════════════════════════
# CONSTANTS & COLORS
# ═══════════════════════════════════════════════════════════════

W, H = 1400, 900          # window width and height in pixels
BG           = (15, 15, 25)       # dark navy — main background color
PANEL        = (28, 28, 42)       # slightly lighter — used for input boxes and cards
TEXT         = (230, 230, 230)    # near-white — main text color
DIM          = (120, 120, 140)    # gray — used for hints and secondary text
BORDER       = (60, 60, 90)       # dark purple-gray — used for borders and grid lines
ACTIVE_BDR   = (140, 140, 255)    # bright blue — border color when input is focused
INACTIVE_BDR = (60, 60, 90)       # same as BORDER — input box when not focused
BTN_COLOR    = (70, 100, 200)     # blue — normal button color
BTN_HOVER    = (90, 130, 240)     # brighter blue — button color when mouse is over it
BTN_RED      = (140, 50, 50)      # dark red — exit/back buttons
BTN_RED_HOV  = (180, 70, 70)      # brighter red — exit/back button on hover
SEL_COLOR    = (60, 180, 100)     # green — used for successful allocation result
GOLD         = (255, 200, 60)     # yellow — used for winner highlights
ERROR_C      = (220, 80, 80)      # red — used for error messages and failed allocations

# list of 8 distinct colors — one assigned to each process for visual distinction
PROCESS_COLORS = [
    (120, 160, 255), (120, 220, 160), (255, 190, 80),
    (220, 100, 100), (180, 120, 255), (80, 200, 200),
    (255, 140, 60),  (160, 255, 120),
]


# ═══════════════════════════════════════════════════════════════
# SHARED UI HELPERS
# ═══════════════════════════════════════════════════════════════

def draw_btn(screen, font, text, rect, hover=False, red=False):
    # pick color based on whether button is hovered and whether it's a red (danger) button
    color = (BTN_RED_HOV if hover else BTN_RED) if red else (BTN_HOVER if hover else BTN_COLOR)
    pygame.draw.rect(screen, color, rect, border_radius=8)  # draw rounded rectangle
    lbl = font.render(text, True, (255, 255, 255))           # render text as white
    # center the text inside the button
    screen.blit(lbl, (rect.x + (rect.w - lbl.get_width()) // 2,
                      rect.y + (rect.h - lbl.get_height()) // 2))


def draw_input_box(screen, fonts, label, value, rect, active, hint=""):
    fnt_label, fnt_input, fnt_hint = fonts   # unpack the three font sizes
    lbl = fnt_label.render(label, True, TEXT)
    screen.blit(lbl, (rect.x, rect.y - 26))  # draw label 26px above the box
    bdr = ACTIVE_BDR if active else INACTIVE_BDR  # blue border if focused, gray if not
    pygame.draw.rect(screen, PANEL, rect, border_radius=6)   # draw box background
    pygame.draw.rect(screen, bdr, rect, 2, border_radius=6)  # draw box border (2px thick)
    # append "|" cursor to text only when this field is active (focused)
    val = fnt_input.render(value + ("|" if active else ""), True, TEXT)
    # vertically center the text inside the box
    screen.blit(val, (rect.x + 10, rect.y + rect.h // 2 - val.get_height() // 2))
    if hint:
        h = fnt_hint.render(hint, True, DIM)
        screen.blit(h, (rect.x, rect.y + rect.h + 4))  # draw hint 4px below the box


# ═══════════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════════

def run_menu(screen, clock):
    # define fonts at different sizes for title, subtitle, buttons, hints
    font_title = pygame.font.SysFont("Consolas", 36, bold=True)
    font_sub   = pygame.font.SysFont("Consolas", 18)
    font_btn   = pygame.font.SysFont("Consolas", 22, bold=True)
    font_hint  = pygame.font.SysFont("Consolas", 14)

    # define button positions and sizes as Rect(x, y, width, height)
    cpu_btn  = pygame.Rect(W // 2 - 260, 380, 240, 70)  # left of center
    mem_btn  = pygame.Rect(W // 2 + 20,  380, 240, 70)  # right of center
    exit_btn = pygame.Rect(W // 2 - 100, 490, 200, 50)  # centered below

    while True:             # keep looping until user makes a choice
        clock.tick(60)      # limit to 60 frames per second
        mx, my = pygame.mouse.get_pos()  # get current mouse position every frame

        for event in pygame.event.get():   # check all events that happened this frame
            if event.type == pygame.QUIT:  # user clicked the X button
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC key also exits
                    pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:        # user clicked the mouse
                if cpu_btn.collidepoint(mx, my):            # click was inside cpu button
                    return "cpu"                            # return state string to main loop
                if mem_btn.collidepoint(mx, my):
                    return "memory"
                if exit_btn.collidepoint(mx, my):
                    pygame.quit(); sys.exit()

        screen.fill(BG)   # clear screen with background color every frame

        # draw title centered horizontally
        t = font_title.render("OS Simulator", True, (140, 160, 255))
        screen.blit(t, (W // 2 - t.get_width() // 2, 200))
        s = font_sub.render("Select a module to simulate", True, DIM)
        screen.blit(s, (W // 2 - s.get_width() // 2, 260))
        # draw a horizontal divider line
        pygame.draw.line(screen, BORDER, (W // 2 - 300, 310), (W // 2 + 300, 310), 1)

        # draw buttons — pass collidepoint result as hover so button highlights on mouseover
        draw_btn(screen, font_btn, "CPU Scheduling",    cpu_btn,  cpu_btn.collidepoint(mx, my))
        draw_btn(screen, font_btn, "Memory Allocation", mem_btn,  mem_btn.collidepoint(mx, my))
        draw_btn(screen, font_btn, "Exit",              exit_btn, exit_btn.collidepoint(mx, my), red=True)

        hint = font_hint.render("ESC = quit", True, DIM)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 40))

        pygame.display.flip()  # push everything drawn this frame to the actual screen


# ═══════════════════════════════════════════════════════════════
# CPU SCHEDULING — INPUT SCREEN
# ═══════════════════════════════════════════════════════════════

def run_cpu_input(screen, clock):
    font_label = pygame.font.SysFont("Consolas", 17, bold=True)
    font_input = pygame.font.SysFont("Consolas", 17)
    font_hint  = pygame.font.SysFont("Consolas", 13)
    font_error = pygame.font.SysFont("Consolas", 13)
    fonts = (font_label, font_input, font_hint)  # pack into tuple to pass to draw_input_box

    # each field is [label, current_value, hint_text]
    fields = [
        ["Process Names", "", "Space-separated  e.g. P1 P2 P3"],
        ["Arrival Times", "", "Space-separated  e.g. 0 1 2"],
        ["Burst Times",   "", "Space-separated  e.g. 5 3 2"],
        ["Quantum (RR)",  "", "Time quantum for Round Robin (0 = skip RR)"],
    ]
    active    = 0    # index of the currently focused input field
    error_msg = ""   # shown in red if validation fails

    # create input box rects — stacked vertically 110px apart starting at y=130
    rects    = [pygame.Rect(60, 130 + i * 110, 760, 44) for i in range(4)]
    run_btn  = pygame.Rect(W // 2 - 100, 590, 200, 50)
    back_btn = pygame.Rect(40, 20, 120, 40)

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(rects):
                    if r.collidepoint(mx, my):
                        active = i   # clicking a field makes it active
                if run_btn.collidepoint(mx, my):
                    try:
                        names    = fields[0][1].strip().split()                    # split names by space
                        arrivals = list(map(int, fields[1][1].strip().split()))   # convert to int list
                        bursts   = list(map(int, fields[2][1].strip().split()))
                        quantum  = int(fields[3][1].strip())
                        if not (len(names) == len(arrivals) == len(bursts)):      # all lists must match
                            raise ValueError("All three lists must have the same count")
                        if len(names) < 2:
                            raise ValueError("Need at least 2 processes")
                        # build list of process dicts from the three parallel lists
                        processes = [
                            {"name": names[i], "arrival": arrivals[i], "burst": bursts[i]}
                            for i in range(len(names))
                        ]
                        return processes, quantum   # pass to visualizer
                    except ValueError as e:
                        error_msg = f"Error: {e}"  # show error without crashing
                if back_btn.collidepoint(mx, my):
                    return None, None   # signals main loop to go back to menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None
                if event.key == pygame.K_TAB:
                    active = (active + 1) % 4   # TAB moves to next field
                if event.key == pygame.K_BACKSPACE:
                    fields[active][1] = fields[active][1][:-1]  # delete last character
                elif event.key != pygame.K_RETURN:
                    ch = event.unicode
                    # field 0 (names): allow letters, digits, spaces
                    if active == 0 and (ch.isalpha() or ch.isdigit() or ch == " "):
                        fields[active][1] += ch
                    # fields 1,2,3 (numbers): allow digits and spaces only
                    elif active in (1, 2, 3) and (ch.isdigit() or ch == " "):
                        fields[active][1] += ch

        screen.fill(BG)

        t = pygame.font.SysFont("Consolas", 22, bold=True).render(
            "CPU Scheduling — Input", True, (140, 160, 255))
        screen.blit(t, (60, 60))
        draw_btn(screen, font_input, "◄ Back", back_btn, back_btn.collidepoint(mx, my))

        # draw all four input boxes
        for i, (r, (label, value, hint)) in enumerate(zip(rects, fields)):
            draw_input_box(screen, fonts, label, value, r, active == i, hint)

        draw_btn(screen, font_label, "▶  Run Simulation", run_btn, run_btn.collidepoint(mx, my))

        if error_msg:
            err = font_error.render(error_msg, True, ERROR_C)
            screen.blit(err, (60, 560))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════
# CPU SCHEDULING — VISUALIZATION
# ═══════════════════════════════════════════════════════════════

def run_cpu_visualizer(screen, clock, processes, quantum):
    font_large  = pygame.font.SysFont("Consolas", 20, bold=True)
    font_medium = pygame.font.SysFont("Consolas", 16)
    font_small  = pygame.font.SysFont("Consolas", 13)

    # run all three algorithms and store results with their names
    schedules = [
        ("FCFS",        fcfs(processes)),
        ("SJF",         sjf(processes)),
        ("Round Robin", round_robin(processes, quantum)),
    ]

    # assign a unique color to each process by name
    color_map = {p["name"]: PROCESS_COLORS[i % len(PROCESS_COLORS)]
                 for i, p in enumerate(processes)}

    # find the latest end time across all schedules — used to scale the timeline
    max_time = max(
        (s["end"] for _, sched in schedules for s in sched),
        default=1
    )

    CHART_X  = 60    # left edge of chart area
    CHART_W  = W - 120  # total width of chart
    ROW_H    = 50    # height of each algorithm's timeline bar
    ROW_GAP  = 50    # vertical space between algorithm rows
    LABEL_W  = 140   # width reserved for algorithm name on the left
    START_Y  = 110   # y position of first row

    current_time = 0      # how far the animation has progressed (in time units)
    playing      = True   # whether animation is running
    speed        = 2      # time units revealed per second
    timer        = 0      # accumulates time between frames
    back_btn  = pygame.Rect(40, 20, 120, 40)
    again_btn = pygame.Rect(W // 2 - 110, H - 60, 200, 44)

    def time_to_x(t):
        # convert a time unit to an x pixel position on screen
        return CHART_X + LABEL_W + int((t / max_time) * (CHART_W - LABEL_W))

    while True:
        dt = clock.tick(60)   # dt = milliseconds since last frame
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_SPACE:
                    playing = not playing     # toggle pause/resume
                if event.key == pygame.K_r:
                    current_time = 0          # restart animation
                    playing = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(mx, my):
                    return "menu"
                if again_btn.collidepoint(mx, my):
                    return "cpu"

        # advance animation — add dt to timer, reveal one time unit when enough time passed
        if playing and current_time < max_time:
            timer += dt / 1000          # convert ms to seconds
            if timer >= 1 / speed:      # if enough time has passed for one unit
                timer = 0
                current_time = min(current_time + 1, max_time)

        screen.fill(BG)

        t = font_large.render("CPU Scheduling — Timeline Visualization", True, (140, 160, 255))
        screen.blit(t, (W // 2 - t.get_width() // 2, 16))
        hint = font_small.render("SPACE = pause   R = restart   ESC = menu", True, DIM)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, 46))
        draw_btn(screen, font_small, "◄ Menu", back_btn, back_btn.collidepoint(mx, my))

        for ai, (algo_name, schedule) in enumerate(schedules):
            y = START_Y + ai * (ROW_H + ROW_GAP)  # y position of this algorithm's row
            _, avg_w, avg_tat = get_cpu_stats(schedule, processes)  # compute stats

            # draw algorithm name + stats above the row
            label = font_medium.render(
                f"{algo_name}   avg wait: {avg_w}   avg TAT: {avg_tat}",
                True, PROCESS_COLORS[ai]
            )
            screen.blit(label, (CHART_X, y - 22))

            # draw gray background bar for the full timeline
            pygame.draw.rect(screen, PANEL,
                             (CHART_X + LABEL_W, y, CHART_W - LABEL_W, ROW_H),
                             border_radius=4)

            # draw each process block up to current_time
            for s in schedule:
                if s["start"] >= current_time:
                    break   # don't draw blocks that haven't been reached yet
                x1 = time_to_x(s["start"])
                x2 = time_to_x(min(s["end"], current_time))  # clip to current time
                if x2 <= x1:
                    continue
                color = color_map.get(s["name"], (180, 180, 180))
                pygame.draw.rect(screen, color,
                                 (x1, y + 2, x2 - x1, ROW_H - 4), border_radius=3)
                if x2 - x1 > 24:   # only draw name label if block is wide enough
                    lbl = font_small.render(s["name"], True, (20, 20, 30))
                    screen.blit(lbl, (x1 + (x2 - x1 - lbl.get_width()) // 2,
                                      y + (ROW_H - lbl.get_height()) // 2))

            # draw time markers below each row
            for t_mark in range(0, max_time + 1, max(1, max_time // 10)):
                x = time_to_x(t_mark)
                pygame.draw.line(screen, BORDER, (x, y + ROW_H), (x, y + ROW_H + 8))
                lbl = font_small.render(str(t_mark), True, DIM)
                screen.blit(lbl, (x - lbl.get_width() // 2, y + ROW_H + 10))

        # draw process legend below the three rows
        legend_y = START_Y + 3 * (ROW_H + ROW_GAP) + 10
        lx = CHART_X
        for p in processes:
            color = color_map[p["name"]]
            pygame.draw.rect(screen, color, (lx, legend_y, 18, 18), border_radius=3)  # color square
            lbl = font_small.render(
                f"{p['name']} (AT:{p['arrival']} BT:{p['burst']})", True, TEXT)
            screen.blit(lbl, (lx + 24, legend_y))
            lx += lbl.get_width() + 50   # move right for next legend item

        # draw progress bar at the bottom
        bar_y = H - 90
        bar_w = W - 120
        pygame.draw.rect(screen, PANEL, (60, bar_y, bar_w, 8), border_radius=4)   # empty bar
        fill = int(bar_w * current_time / max_time) if max_time > 0 else 0
        pygame.draw.rect(screen, PROCESS_COLORS[0], (60, bar_y, fill, 8), border_radius=4)  # filled portion

        draw_btn(screen, font_medium, "▶  Run Again", again_btn, again_btn.collidepoint(mx, my))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════
# MEMORY ALLOCATION — INPUT SCREEN
# ═══════════════════════════════════════════════════════════════

def run_memory_input(screen, clock):
    font_label = pygame.font.SysFont("Consolas", 17, bold=True)
    font_input = pygame.font.SysFont("Consolas", 17)
    font_hint  = pygame.font.SysFont("Consolas", 13)
    font_error = pygame.font.SysFont("Consolas", 13)
    fonts = (font_label, font_input, font_hint)

    fields = [
        ["Memory Blocks (KB)", "", "Space-separated block sizes  e.g. 100 500 200 300"],
        ["Process Sizes (KB)", "", "Space-separated process sizes  e.g. 212 417 112"],
    ]
    active    = 0
    error_msg = ""

    rects    = [pygame.Rect(60, 160 + i * 120, 760, 44) for i in range(2)]
    run_btn  = pygame.Rect(W // 2 - 100, 460, 200, 50)
    back_btn = pygame.Rect(40, 20, 120, 40)

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(rects):
                    if r.collidepoint(mx, my):
                        active = i
                if run_btn.collidepoint(mx, my):
                    try:
                        blocks    = list(map(int, fields[0][1].strip().split()))  # parse block sizes
                        processes = list(map(int, fields[1][1].strip().split()))  # parse process sizes
                        if len(blocks) < 1 or len(processes) < 1:
                            raise ValueError("Need at least 1 block and 1 process")
                        return blocks, processes
                    except ValueError as e:
                        error_msg = f"Error: {e}"
                if back_btn.collidepoint(mx, my):
                    return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None
                if event.key == pygame.K_TAB:
                    active = (active + 1) % 2
                if event.key == pygame.K_BACKSPACE:
                    fields[active][1] = fields[active][1][:-1]
                elif event.key != pygame.K_RETURN:
                    ch = event.unicode
                    if ch.isdigit() or ch == " ":   # only allow numbers and spaces
                        fields[active][1] += ch

        screen.fill(BG)

        t = pygame.font.SysFont("Consolas", 22, bold=True).render(
            "Memory Allocation — Input", True, (140, 160, 255))
        screen.blit(t, (60, 80))
        draw_btn(screen, font_input, "◄ Back", back_btn, back_btn.collidepoint(mx, my))

        for i, (r, (label, value, hint)) in enumerate(zip(rects, fields)):
            draw_input_box(screen, fonts, label, value, r, active == i, hint)

        draw_btn(screen, font_label, "▶  Run Simulation", run_btn, run_btn.collidepoint(mx, my))

        if error_msg:
            err = font_error.render(error_msg, True, ERROR_C)
            screen.blit(err, (60, 430))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════
# MEMORY ALLOCATION — VISUALIZATION
# ═══════════════════════════════════════════════════════════════

def run_memory_visualizer(screen, clock, original_blocks, process_sizes):
    font_large  = pygame.font.SysFont("Consolas", 20, bold=True)
    font_medium = pygame.font.SysFont("Consolas", 15)
    font_small  = pygame.font.SysFont("Consolas", 13)

    algo_names  = ["First Fit", "Next Fit", "Best Fit", "Worst Fit"]
    algo_colors = [
        (120, 160, 255), (120, 220, 160),
        (255, 190, 80),  (220, 100, 160),
    ]

    # run all four algorithms upfront and store step-by-step results
    results   = {name: run_memory_algo(name, original_blocks, process_sizes)
                 for name in algo_names}
    total_mem = sum(original_blocks)  # total memory size — used to scale block widths

    CHART_X  = 60
    CHART_W  = W - 120
    BAR_H    = 44      # height of each memory bar
    BAR_GAP  = 50      # vertical gap between algorithm bars
    LABEL_W  = 130     # width reserved for algorithm name
    START_Y  = 110

    current_step = 0              # how many allocation steps have been shown
    max_steps    = len(process_sizes)
    playing      = True
    timer        = 0
    speed        = 1.2            # steps per second
    back_btn  = pygame.Rect(40, 20, 120, 40)
    again_btn = pygame.Rect(W // 2 - 110, H - 60, 200, 44)

    while True:
        dt = clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_SPACE:
                    playing = not playing
                if event.key == pygame.K_r:
                    current_step = 0
                    playing = True
                if event.key == pygame.K_RIGHT and not playing:
                    current_step = min(current_step + 1, max_steps)  # manual step forward
                if event.key == pygame.K_LEFT and not playing:
                    current_step = max(current_step - 1, 0)          # manual step backward
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(mx, my):
                    return "menu"
                if again_btn.collidepoint(mx, my):
                    return "memory"

        # advance one step when enough time has passed
        if playing and current_step < max_steps:
            timer += dt / 1000
            if timer >= 1 / speed:
                timer = 0
                current_step += 1

        screen.fill(BG)

        t = font_large.render("Memory Allocation — Block Visualization", True, (140, 160, 255))
        screen.blit(t, (W // 2 - t.get_width() // 2, 16))
        hint = font_small.render("SPACE = pause   R = restart   ◄ ► = step   ESC = menu", True, DIM)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, 46))
        draw_btn(screen, font_small, "◄ Menu", back_btn, back_btn.collidepoint(mx, my))

        for ai, algo_name in enumerate(algo_names):
            steps = results[algo_name]       # get this algorithm's step list
            y     = START_Y + ai * (BAR_H + BAR_GAP)
            color = algo_colors[ai]

            # count how many allocations succeeded and failed so far
            if current_step > 0:
                allocated = sum(1 for s in steps[:current_step] if s["status"] == "Allocated")
                failed    = current_step - allocated
                stat_text = f"  allocated: {allocated}  failed: {failed}"
            else:
                stat_text = ""

            lbl = font_medium.render(f"{algo_name}{stat_text}", True, color)
            screen.blit(lbl, (CHART_X, y - 22))

            # get memory state at current step (or original if no steps yet)
            mem_state = steps[current_step - 1]["memory"] if current_step > 0 else original_blocks.copy()
            cursor    = CHART_X + LABEL_W   # start drawing blocks from here

            for bi, (orig, curr) in enumerate(zip(original_blocks, mem_state)):
                # calculate pixel width of this block proportional to its size
                block_w = int((orig / total_mem) * (CHART_W - LABEL_W))
                used    = orig - curr            # how much of this block is occupied
                used_w  = int((used / orig) * block_w) if orig > 0 else 0
                free_w  = block_w - used_w       # remaining free portion width

                # draw occupied (colored) portion
                if used_w > 0:
                    proc_color = PROCESS_COLORS[bi % len(PROCESS_COLORS)]
                    pygame.draw.rect(screen, proc_color,
                                     (cursor, y, used_w, BAR_H), border_radius=3)
                    if used_w > 30:   # only show label if wide enough
                        ul = font_small.render(f"{used}K", True, (20, 20, 30))
                        screen.blit(ul, (cursor + (used_w - ul.get_width()) // 2,
                                         y + (BAR_H - ul.get_height()) // 2))

                # draw free (dark) portion
                if free_w > 0:
                    pygame.draw.rect(screen, PANEL,
                                     (cursor + used_w, y, free_w, BAR_H), border_radius=3)
                    pygame.draw.rect(screen, BORDER,
                                     (cursor + used_w, y, free_w, BAR_H), 1, border_radius=3)
                    if free_w > 30:
                        fl = font_small.render(f"{curr}K", True, DIM)
                        screen.blit(fl, (cursor + used_w + (free_w - fl.get_width()) // 2,
                                         y + (BAR_H - fl.get_height()) // 2))

                cursor += block_w   # move cursor right for next block

            # show result of latest allocation step below the bar
            if current_step > 0:
                step = steps[current_step - 1]
                rc   = SEL_COLOR if step["status"] == "Allocated" else ERROR_C  # green or red
                rl   = font_small.render(
                    f"Step {current_step}: Process {step['size']}KB → {step['status']}"
                    + (f" in Block {step['block']}" if step["status"] == "Allocated" else ""),
                    True, rc
                )
                screen.blit(rl, (CHART_X + LABEL_W, y + BAR_H + 4))

        # progress bar at the bottom
        bar_y = H - 90
        bar_w = W - 120
        pygame.draw.rect(screen, PANEL, (60, bar_y, bar_w, 8), border_radius=4)
        fill = int(bar_w * current_step / max_steps) if max_steps > 0 else 0
        pygame.draw.rect(screen, algo_colors[0], (60, bar_y, fill, 8), border_radius=4)

        draw_btn(screen, font_medium, "▶  Run Again", again_btn, again_btn.collidepoint(mx, my))

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pygame.init()                                        # initialize all pygame modules
    screen = pygame.display.set_mode((W, H))             # create the window
    pygame.display.set_caption("OS Simulator")           # set window title
    clock = pygame.time.Clock()                          # create clock for frame rate control

    state = "menu"   # start at the main menu

    while True:
        if state == "menu":
            state = run_menu(screen, clock)              # returns "cpu" or "memory"

        elif state == "cpu":
            processes, quantum = run_cpu_input(screen, clock)   # get user input
            if processes is None:
                state = "menu"                          # user pressed back
            else:
                state = run_cpu_visualizer(screen, clock, processes, quantum)  # show visualization

        elif state == "memory":
            blocks, proc_sizes = run_memory_input(screen, clock)
            if blocks is None:
                state = "menu"
            else:
                state = run_memory_visualizer(screen, clock, blocks, proc_sizes)