# AutoClick V6 — Test Tab, i18n & Precision Timer Design

**Date:** 2026-03-30
**Status:** Approved
**Approach:** Single-file (all changes in main.py)

---

## 1. Internationalization (i18n)

### Structure
A `TRANSLATIONS` dictionary at the top of `main.py` with keys for every UI string. A complete string audit of main.py must be performed as the first implementation step, cataloging every hardcoded string including messagebox titles, error messages, status messages, radio button labels, dialog labels, and capture status messages.

```python
TRANSLATIONS = {
    "en": {
        # Window & Tabs
        "window_title": "AutoClick V6 dev by jorgeRjunior",
        "tab_main": "Main Function",
        "tab_custom": "Custom Functions",
        "tab_test": "Test",
        # Main Tab
        "status_waiting": "Waiting to start...",
        "status_running": "Running...",
        "status_stopped": "Stopped.",
        "lbl_input_type": "Input Type",
        "radio_keyboard": "Keyboard",
        "radio_mouse_left": "Mouse 1 (Left)",
        "radio_mouse_right": "Mouse 2 (Right)",
        "radio_mouse_x2": "Mouse 4 (Side Front)",
        "radio_mouse_x1": "Mouse 5 (Side Back)",
        "lbl_key": "Key (when keyboard selected)",
        "lbl_interval_min": "Min Interval (ms)",
        "lbl_interval_max": "Max Interval (ms)",
        "lbl_mode": "Mode",
        "mode_continuous": "Continuous",
        "mode_once": "Once",
        "mode_toggle": "Toggle",
        "btn_start": "Start (F6)",
        "btn_stop": "Stop (F6)",
        "info_text": "...",  # full info block
        # Custom Tab
        "btn_add_function": "Add New Function",
        "btn_save_config": "Save Settings",
        "col_active": "Active?",
        "col_trigger": "Trigger",
        "col_type": "Type",
        "col_action": "Action",
        "col_interval": "Interval (ms)",
        "col_mode": "Mode",
        "col_actions": "Actions",
        "btn_edit": "Edit",
        "btn_delete": "Delete",
        "no_functions_msg": "No custom functions configured...",
        "limit_reached": "Limit Reached",
        "limit_msg": "Maximum of 10 custom functions.",
        "confirm_delete": "Confirm Delete",
        "confirm_delete_msg": "Delete this function?",
        # Dialog
        "dlg_title_new": "New Function",
        "dlg_title_edit": "Edit Function",
        "dlg_trigger_key": "Trigger Key",
        "dlg_action_type": "Action Type",
        "dlg_action_key": "Action Key",
        "dlg_interval_min": "Min Interval (ms)",
        "dlg_interval_max": "Max Interval (ms)",
        "dlg_mode": "Mode",
        "dlg_btn_save": "Save",
        "dlg_btn_cancel": "Cancel",
        "dlg_btn_capture": "Capture",
        "dlg_capturing": "Press a key...",
        # Validation errors
        "err_title": "Error",
        "err_invalid_interval": "Invalid interval values.",
        "err_no_key": "Please enter a key.",
        "err_min_greater_max": "Min interval must be less than max.",
        # Test Tab
        "test_config_title": "Detected Configuration",
        "test_lbl_input": "Input:",
        "test_lbl_key": "Key:",
        "test_lbl_interval": "Interval:",
        "test_lbl_mode": "Mode:",
        "test_btn_start": "Start Test",
        "test_btn_stop": "Stop Test",
        "test_btn_clear": "Clear Results",
        "test_stat_configured": "Configured interval:",
        "test_stat_real_avg": "Real average:",
        "test_stat_min_max": "Min / Max:",
        "test_stat_stddev": "Std deviation:",
        "test_stat_precision": "Precision:",
        "test_stat_total": "Total actions:",
        "test_col_num": "#",
        "test_col_real_time": "Real Time (ms)",
        "test_col_deviation": "Deviation (ms)",
        "test_col_status": "Status",
        "test_suggestion_overhead": "Average system overhead: {overhead}ms. To get exactly {target}ms, set interval to {suggested}ms.",
        "test_suggestion_excellent": "Timing is excellent, no adjustment needed.",
        "test_suggestion_waiting": "At least 20 measurements needed for suggestion...",
        # Splash fallback
        "splash_loading": "Loading AutoClick V6...",
        # Language selector
        "lbl_language": "Language:",
    },
    "pt-br": {
        # ... mirror of all keys above in Portuguese
    }
}
```

### Language Selector
- `ttk.Combobox` in the top-right corner of the window, in a toolbar frame inserted between root and notebook
- This requires adding a `ttk.Frame` as toolbar above the notebook (minor layout restructure)
- Options: "English" / "Português (BR)"
- On change: calls `self.apply_language()` which updates all widgets

### Widget Update Strategy
All translatable widgets must be stored as instance attributes (e.g., `self.lbl_input_type`, `self.btn_start`). The `apply_language()` method iterates over these stored references calling `.configure(text=self.t("key"))` on each.

For the custom tab: `refresh_mappings_display()` already rebuilds dynamic content, so only static elements (title, column headers, buttons) need stored references.

The notebook tab names are updated via `self.notebook.tab(index, text=self.t("key"))`.

### Persistence
- Saves `"language": "en"` or `"language": "pt-br"` in `autoclick_config.json` alongside `custom_mappings`
- Both `load_config()` and `save_config()` must be updated to handle the `"language"` key
- Loaded on startup, defaults to "en"

### Helper Method
- `self.t("key")` returns the translated string for the current language

---

## 2. Precision Timer

### Problem
`time.sleep()` on Windows has ~15.6ms resolution (scheduler tick). For 100ms configured, actual sleep varies between ~75-114ms.

### Solution: Two Layers

**Layer 1 — `timeBeginPeriod(1)`:**
Called via `ctypes` at program startup to force 1ms timer resolution on Windows. Cleanup on shutdown.

```python
import ctypes
import atexit
import sys

if sys.platform == 'win32':
    winmm = ctypes.windll.winmm
    winmm.timeBeginPeriod(1)
    atexit.register(winmm.timeEndPeriod, 1)
```

Additionally, the `mainloop()` call must be wrapped in `try/finally` calling `winmm.timeEndPeriod(1)` as defense-in-depth. On Windows 10 20H1+, the OS auto-cleans per-process timer resolution, so this is a safety net.

**Platform guard:** All `ctypes.windll.winmm` calls must be wrapped in `if sys.platform == 'win32'` checks. On non-Windows platforms, fall back to plain `time.sleep()`.

**Layer 2 — Hybrid spin-wait:**
Replaces `time.sleep(interval)` with `precision_sleep(seconds)`:

```python
def precision_sleep(seconds):
    if seconds <= 0:
        return
    target = time.perf_counter() + seconds
    # For very short intervals (<5ms), use pure spin-wait
    if seconds < 0.005:
        while time.perf_counter() < target:
            pass
        return
    # Sleep most of the time (leave ~2ms margin)
    sleep_time = seconds - 0.002
    if sleep_time > 0:
        time.sleep(sleep_time)
    # Busy-wait the last ~2ms for precision
    while time.perf_counter() < target:
        pass
```

**Dynamic compensation:**
After each action, measure the real time the action took and subtract from next interval:

```python
t_start = time.perf_counter()
# execute action (keyboard.press, mouse.click, etc.)
action_overhead = time.perf_counter() - t_start
next_sleep = interval - action_overhead
precision_sleep(max(0, next_sleep))
```

### CPU Considerations
- The 2ms spin-wait margin is ~2% CPU per thread at 100ms intervals
- For 10 simultaneous mappings at short intervals, CPU load increases proportionally
- The 2ms margin is a reasonable default; for intervals <5ms, pure spin-wait is used since `time.sleep()` would be inaccurate anyway

### Application
Replace all `time.sleep()` calls in action loops (both main tab and custom functions) with `precision_sleep()` + dynamic compensation.

---

## 3. Test Tab

### Location
Third tab in the notebook. Text: "Test" (en) / "Testes" (pt-br).

### Layout (top to bottom)

#### 3.1 Detected Configuration Panel (read-only)
- Displays current config from tab 1: input type, key, interval min/max, mode
- Auto-refreshes when user switches to the test tab via `<<NotebookTabChanged>>` event binding on the notebook widget

#### 3.2 Control Buttons
- `[Start Test]` / `[Stop Test]` — toggle button, text changes on click
- `[Clear Results]` — resets statistics and log

#### 3.3 Real-time Statistics Panel
- **Configured interval:** e.g. "100ms" (or "80-120ms" if range)
- **Real average interval:** e.g. "101.2ms"
- **Real min / max:** e.g. "98ms / 104ms"
- **Standard deviation:** e.g. "±1.8ms"
- **Precision:** e.g. "98.7%"
- **Total actions:** e.g. "347"
- Updates every 250ms during test (faster than 500ms for a precision tool)

**Precision formula:**
```python
target = (interval_min + interval_max) / 2
precision = max(0, 1 - abs(real_avg - target) / target) * 100
```
For range intervals, the target is the midpoint. For the Treeview Status column: any measurement within [interval_min, interval_max] is "OK"; outside range uses ±5%/±10%/>10% thresholds relative to the target.

#### 3.4 Last 100 Measurements Log
- Scrollable `Treeview` showing last 100 measurements (older entries removed when limit exceeded)
- Columns: `#`, `Real Time (ms)`, `Deviation (ms)`, `Status` (OK / High / Low)
- Status coloring via `Treeview.tag_configure()` with foreground text color:
  - `tag_configure("ok", foreground="#28a745")` (green)
  - `tag_configure("warn", foreground="#ffc107")` (yellow/amber)
  - `tag_configure("bad", foreground="#dc3545")` (red)
- Colors applied per-row (Treeview limitation — no per-cell coloring)

#### 3.5 Suggestion Panel (Input Lag)
- Appears after at least 20 measurements
- Calculates: `avg_overhead = real_avg - target`
- Shows: "Average system overhead: +2.3ms. To get exactly 100ms, configure interval to 98ms."
- If precision is already >98%: "Timing is excellent, no adjustment needed."

### Test Operation — Simulated Actions

**Critical design decision:** The test runs a **simulated** timing loop. It does NOT send real keystrokes/clicks to the system.

The test loop:
1. Uses the same `precision_sleep()` function as production
2. Instead of calling `keyboard.send()` / `mouse.click()`, executes a **no-op placeholder** that simulates approximate action overhead (`time.sleep(0.0005)` — ~0.5ms, typical overhead of a keyboard/mouse action)
3. Records `time.perf_counter()` timestamps before and after each iteration
4. Calculates delta between consecutive actions and feeds stats

**Why simulated:** Sending real actions during a test would inject phantom keystrokes/clicks into whatever window the user has open, which is disruptive and useless for timing measurement.

### Mutual Exclusivity with Main Tab
- Starting a test **automatically stops** tab 1 if it is running (calls `self.stop_program()`)
- Starting tab 1 **automatically stops** the test if running
- This avoids hook conflicts since current `stop_program()` calls `keyboard.unhook_all()`

### Hook and Thread Isolation
- The test tab uses its **own** stop event: `self.test_stop_event = Event()`
- The test tab uses its **own** thread: `self.test_thread`
- The test does NOT register any keyboard/mouse hooks (since actions are simulated)
- The test reads config values from tab 1's `StringVar`s directly (`self.input_type`, `self.interval_min`, `self.interval_max`, `self.mode`)
- Completely independent from `self.running`, `self.stop_event`, and `self._active_hook_removers`

---

## Integration Notes

1. **i18n + Test Tab:** All test tab strings are included in the TRANSLATIONS dictionary (see Section 1 keys prefixed with `test_`).
2. **Precision Timer + Test Tab:** The test tab uses `precision_sleep()` to measure production-equivalent timing behavior.
3. **Config changes:** `autoclick_config.json` gains a `"language"` key. Both `load_config()` and `save_config()` are updated.

---

## Non-Goals
- No graphing/charting (text stats only)
- No export of test results
- No additional languages beyond EN and PT-BR
- No changes to project file structure (single-file approach)
