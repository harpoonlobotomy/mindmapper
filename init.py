"""mindmapper runner"""


def run():
    from mm_GUI import start_window
    while True:
        outcome = start_window()
        if outcome:
            print(f"Outcome from make_window: {outcome}")
        break

run()


