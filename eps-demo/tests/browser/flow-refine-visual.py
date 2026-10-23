"""Matched overview, battery, and deep interactive branch captures."""
exec((ROOT/'flow-only.py').read_text().split('\nprobe.wait_js("document.querySelectorAll')[0])
probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
click_task('battery');probe.snapshot('battery-after')
click_task('scenarios');loads=child('scenarios','loads');load=child(loads,'load');windows=child(load,'windows');child(windows,'window');probe.snapshot('deep-window-after')
probe.screenshots=False
