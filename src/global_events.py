from my_utils.signal import Signal


app_exit_requested = Signal()
open_gui_requested = Signal()


# Signals to probably add:
# Monitor state changed
# errors?

# Other potential events:
# Monitor added
# Monitor removed
# Monitor modified
# Monitor executed / new results in


# Signals to WEAK MAYBE CONSIDER adding:
# Monitor due state changed
# Monitor execution failed
