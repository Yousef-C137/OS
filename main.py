from visualizer import run_visualizer, run_input_screen

if __name__ == "__main__":
    while True:
        reference_string, num_frames, speed = run_input_screen()
        run_again = run_visualizer(num_frames, reference_string, speed)
        if run_again is not True:
            break