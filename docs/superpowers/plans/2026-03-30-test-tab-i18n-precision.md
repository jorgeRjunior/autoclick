# Test Tab, i18n & Precision Timer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a precision timer, internationalization (EN/PT-BR), and a test tab to AutoClick V6.

**Architecture:** All changes in `main.py` (single-file approach). Three features implemented in dependency order: precision timer first (no UI dependency), then i18n (infrastructure for all text), then test tab (depends on both).

**Tech Stack:** Python, tkinter, ttkbootstrap, ctypes (Windows API), threading

**Spec:** `docs/superpowers/specs/2026-03-30-autoclick-test-tab-i18n-precision-design.md`

**Note:** This is a desktop GUI app with no test framework. Verification is done by running the app and checking behavior. Each task ends with a manual verification step.

---

## Chunk 1: Precision Timer

### Task 1: Add precision_sleep() and timeBeginPeriod

**Files:**
- Modify: `main.py` (top-level imports and new function before class definition)

- [ ] **Step 1: Add ctypes import and timeBeginPeriod call**

After the existing `import time` line (around line 76), add:

```python
import ctypes
import atexit

# High-precision timer for Windows
if sys.platform == 'win32':
    _winmm = ctypes.windll.winmm
    _winmm.timeBeginPeriod(1)
    atexit.register(_winmm.timeEndPeriod, 1)
```

- [ ] **Step 2: Add precision_sleep() function**

Add as a module-level function, after the `close_splash` function and before the `AutoClickerGUI` class:

```python
def precision_sleep(seconds):
    """High-precision sleep using hybrid spin-wait approach."""
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

- [ ] **Step 3: Wrap mainloop in try/finally**

At the bottom of `main.py`, find the `app.root.mainloop()` call and wrap it:

```python
try:
    app.root.mainloop()
finally:
    if sys.platform == 'win32':
        _winmm.timeEndPeriod(1)
```

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add precision_sleep with timeBeginPeriod for accurate timing"
```

### Task 2: Replace time.sleep() with precision_sleep() in all action loops

**Files:**
- Modify: `main.py` (all action loop methods)

- [ ] **Step 1: Find all time.sleep() calls in action loops**

Search for `time.sleep` in the file. Replace each one in action/repeat loops with `precision_sleep()` + dynamic compensation pattern:

```python
# Before each action:
t_start = time.perf_counter()
# ... execute action ...
action_overhead = time.perf_counter() - t_start
interval = random.uniform(float(interval_min), float(interval_max)) / 1000.0
next_sleep = interval - action_overhead
precision_sleep(max(0, next_sleep))
```

Apply this pattern to:
- The main tab's continuous/toggle action loop
- The custom mapping action loops
- Any hold-mode polling loops

- [ ] **Step 2: Verify by running the app**

Run `python main.py`, configure a 100ms fixed interval, start the action, and observe timing behavior is more consistent.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: replace time.sleep with precision_sleep in all action loops"
```

---

## Chunk 2: Internationalization (i18n)

### Task 3: Add TRANSLATIONS dictionary and helper method

**Files:**
- Modify: `main.py` (add TRANSLATIONS dict at top, add self.t() method, add language to config)

- [ ] **Step 1: Add TRANSLATIONS dictionary**

Add after imports, before the `AutoClickerGUI` class. Must contain ALL UI strings in both `"en"` and `"pt-br"`. Perform a full string audit of main.py to capture every hardcoded string. Include keys for:
- Window title, tab names
- All labels, buttons, radio buttons in main tab
- All labels, buttons, column headers in custom tab
- All dialog labels and buttons
- All messagebox titles and messages
- All status messages
- All validation error messages
- Splash screen fallback text
- Test tab strings (for Task 6)
- Language selector label

Add assertion at the end of the dictionary:

```python
assert set(TRANSLATIONS["en"].keys()) == set(TRANSLATIONS["pt-br"].keys()), "Translation keys mismatch!"
```

- [ ] **Step 2: Add self.t() helper and language state to __init__**

In `AutoClickerGUI.__init__`, before `self.load_config()`:

```python
self.current_language = "en"  # will be overwritten by load_config
```

Add method to the class:

```python
def t(self, key):
    """Get translated string for current language."""
    return TRANSLATIONS.get(self.current_language, TRANSLATIONS["en"]).get(key, key)
```

- [ ] **Step 3: Update load_config and save_config for language**

In `load_config()`, after loading custom_mappings:
```python
self.current_language = config.get('language', 'en')
```

In `save_config()`, add language to saved config:
```python
config = {
    'custom_mappings': mappings_to_save,
    'language': self.current_language
}
```

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add i18n translations dictionary and helper method"
```

### Task 4: Add language selector widget

**Files:**
- Modify: `main.py` (`__init__` method, layout restructure)

- [ ] **Step 1: Add toolbar frame above notebook**

In `__init__`, before the notebook creation, add:

```python
# Toolbar frame with language selector
self.toolbar = ttk.Frame(self.root)
self.toolbar.pack(fill='x', padx=10, pady=(10, 0))

ttk.Label(self.toolbar, text=self.t("lbl_language")).pack(side='right', padx=(0, 5))
self.lang_combo = ttk.Combobox(
    self.toolbar,
    values=["English", "Português (BR)"],
    state="readonly",
    width=15
)
self.lang_combo.set("English" if self.current_language == "en" else "Português (BR)")
self.lang_combo.pack(side='right')
self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
```

- [ ] **Step 2: Add on_language_change method**

```python
def on_language_change(self, event=None):
    """Handle language selector change."""
    selected = self.lang_combo.get()
    self.current_language = "en" if selected == "English" else "pt-br"
    self.apply_language()
    self.save_config()
```

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add language selector combobox in toolbar"
```

### Task 5: Replace all hardcoded strings and implement apply_language()

**Files:**
- Modify: `main.py` (all widget creation methods, add apply_language)

- [ ] **Step 1: Store translatable widgets as self.xxx**

In `create_main_tab_widgets()`, change every label/button/radiobutton creation to store as instance attribute and use `self.t()`:

```python
# Before: ttk.Label(main_frame, text="AutoClick V6", ...)
# After:
self.lbl_title = ttk.Label(main_frame, text=self.t("window_title"), ...)
```

Do this for ALL translatable widgets in:
- `create_main_tab_widgets()`
- `create_custom_tab_widgets()` (static elements only — headers, buttons)
- `refresh_mappings_display()` (column headers)
- `open_mapping_dialog()` (dialog labels and buttons)

- [ ] **Step 2: Implement apply_language()**

```python
def apply_language(self):
    """Update all UI text to current language."""
    # Window title
    self.root.title(self.t("window_title"))

    # Notebook tabs
    self.notebook.tab(0, text=self.t("tab_main"))
    self.notebook.tab(1, text=self.t("tab_custom"))
    if hasattr(self, 'test_tab'):
        self.notebook.tab(2, text=self.t("tab_test"))

    # Main tab widgets
    self.lbl_title.configure(text=self.t("window_title"))
    # ... configure all stored widget references ...

    # Refresh custom tab (rebuilds dynamic content with new language)
    self.refresh_mappings_display()
```

- [ ] **Step 3: Verify by running the app**

Run `python main.py`. Switch language from English to Portuguese and back. All UI text should update.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: replace all hardcoded strings with i18n translations"
```

---

## Chunk 3: Test Tab

### Task 6: Create test tab UI layout

**Files:**
- Modify: `main.py` (`__init__` and new `create_test_tab_widgets` method)

- [ ] **Step 1: Add test tab to notebook in __init__**

After the custom tab creation:

```python
# Create test tab
self.test_tab = ttk.Frame(self.notebook)
self.notebook.add(self.test_tab, text=self.t("tab_test"))

# Test tab state
self.test_running = False
self.test_stop_event = Event()
self.test_thread = None
self.test_measurements = []
```

- [ ] **Step 2: Implement create_test_tab_widgets()**

Create the full test tab layout with:
1. **Config panel** — LabelFrame with read-only labels showing tab 1 config
2. **Control buttons** — Start/Stop toggle + Clear
3. **Statistics panel** — LabelFrame with StringVar labels for all stats
4. **Measurements Treeview** — scrollable, 4 columns, tag coloring
5. **Suggestion panel** — LabelFrame with suggestion text

Store all translatable widgets as `self.test_xxx`.

Configure Treeview tags:
```python
self.test_tree.tag_configure("ok", foreground="#28a745")
self.test_tree.tag_configure("warn", foreground="#ffc107")
self.test_tree.tag_configure("bad", foreground="#dc3545")
```

- [ ] **Step 3: Add <<NotebookTabChanged>> binding**

In `__init__`, after notebook setup:

```python
self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
```

```python
def on_tab_changed(self, event=None):
    """Refresh test tab config display when switching to it."""
    current = self.notebook.index(self.notebook.select())
    if current == 2:  # Test tab
        self.refresh_test_config_display()
```

- [ ] **Step 4: Implement refresh_test_config_display()**

```python
def refresh_test_config_display(self):
    """Update the test tab's config panel with current tab 1 settings."""
    input_type = self.input_type.get()
    key = self.key.get()
    imin = self.interval_min.get()
    imax = self.interval_max.get()
    mode = self.mode.get()

    self.test_lbl_input_val.configure(text=input_type)
    self.test_lbl_key_val.configure(text=key if key else "—")
    self.test_lbl_interval_val.configure(
        text=f"{imin}ms" if imin == imax else f"{imin}-{imax}ms"
    )
    self.test_lbl_mode_val.configure(text=self.t(f"mode_{mode}"))
```

- [ ] **Step 5: Commit**

```bash
git add main.py
git commit -m "feat: add test tab UI layout with config display"
```

### Task 7: Implement test execution engine

**Files:**
- Modify: `main.py` (test start/stop/clear methods + test loop thread)

- [ ] **Step 1: Implement start_test()**

```python
def start_test(self):
    """Start the timing test."""
    # Mutual exclusivity: stop main tab if running
    if self.running:
        self.stop_program()

    self.test_running = True
    self.test_stop_event.clear()
    self.test_measurements = []
    self.test_count = 0
    self.test_btn_toggle.configure(text=self.t("test_btn_stop"))

    # Start test loop thread
    self.test_thread = Thread(target=self.test_loop, daemon=True)
    self.test_thread.start()

    # Start UI update timer
    self.update_test_stats()
```

- [ ] **Step 2: Implement test_loop()**

```python
def test_loop(self):
    """Simulated timing loop that measures precision_sleep accuracy."""
    interval_min = float(self.interval_min.get()) / 1000.0
    interval_max = float(self.interval_max.get()) / 1000.0

    prev_time = time.perf_counter()

    while not self.test_stop_event.is_set():
        interval = random.uniform(interval_min, interval_max)

        # Simulate action overhead (~0.5ms)
        t_action_start = time.perf_counter()
        time.sleep(0.0005)
        action_overhead = time.perf_counter() - t_action_start

        # Precision sleep with compensation
        next_sleep = interval - action_overhead
        precision_sleep(max(0, next_sleep))

        # Measure actual time
        now = time.perf_counter()
        actual_ms = (now - prev_time) * 1000.0
        prev_time = now

        self.test_measurements.append(actual_ms)
        self.test_count += 1

        # Keep max 100 measurements
        if len(self.test_measurements) > 100:
            self.test_measurements.pop(0)
```

- [ ] **Step 3: Implement stop_test()**

```python
def stop_test(self):
    """Stop the timing test."""
    self.test_stop_event.set()
    self.test_running = False
    self.test_btn_toggle.configure(text=self.t("test_btn_start"))
```

- [ ] **Step 4: Implement toggle and clear**

```python
def toggle_test(self):
    if self.test_running:
        self.stop_test()
    else:
        self.start_test()

def clear_test(self):
    self.test_measurements = []
    self.test_count = 0
    # Clear treeview
    for item in self.test_tree.get_children():
        self.test_tree.delete(item)
    # Reset stat labels
    self.reset_test_stats()
```

- [ ] **Step 5: Commit**

```bash
git add main.py
git commit -m "feat: implement test execution engine with simulated timing loop"
```

### Task 8: Implement real-time statistics and suggestion

**Files:**
- Modify: `main.py` (update_test_stats method + suggestion logic)

- [ ] **Step 1: Implement update_test_stats()**

```python
def update_test_stats(self):
    """Update test statistics display every 250ms."""
    if not self.test_running:
        return

    measurements = self.test_measurements.copy()

    if len(measurements) > 1:
        target_min = float(self.interval_min.get())
        target_max = float(self.interval_max.get())
        target = (target_min + target_max) / 2.0

        avg = sum(measurements) / len(measurements)
        mn = min(measurements)
        mx = max(measurements)

        # Standard deviation
        variance = sum((x - avg) ** 2 for x in measurements) / len(measurements)
        stddev = variance ** 0.5

        # Precision
        precision = max(0, 1 - abs(avg - target) / target) * 100

        # Update labels
        configured_text = f"{target_min:.0f}ms" if target_min == target_max else f"{target_min:.0f}-{target_max:.0f}ms"
        self.test_stat_configured_val.configure(text=configured_text)
        self.test_stat_avg_val.configure(text=f"{avg:.1f}ms")
        self.test_stat_minmax_val.configure(text=f"{mn:.1f}ms / {mx:.1f}ms")
        self.test_stat_stddev_val.configure(text=f"±{stddev:.1f}ms")
        self.test_stat_precision_val.configure(text=f"{precision:.1f}%")
        self.test_stat_total_val.configure(text=str(self.test_count))

        # Update treeview with latest measurements
        self.update_test_treeview(measurements, target, target_min, target_max)

        # Update suggestion after 20+ measurements
        self.update_test_suggestion(measurements, target)

    # Schedule next update
    if self.test_running:
        self.root.after(250, self.update_test_stats)
```

- [ ] **Step 2: Implement update_test_treeview()**

```python
def update_test_treeview(self, measurements, target, target_min, target_max):
    """Update the measurements treeview."""
    # Clear existing
    for item in self.test_tree.get_children():
        self.test_tree.delete(item)

    # Add last 100 measurements (most recent at top)
    start_idx = max(0, self.test_count - len(measurements))
    for i, ms in enumerate(reversed(measurements)):
        num = self.test_count - i
        deviation = ms - target

        # Determine status
        if target_min <= ms <= target_max:
            status, tag = "OK", "ok"
        elif abs(deviation) / target <= 0.05:
            status, tag = "OK", "ok"
        elif abs(deviation) / target <= 0.10:
            status = "High" if deviation > 0 else "Low"
            tag = "warn"
        else:
            status = "High" if deviation > 0 else "Low"
            tag = "bad"

        self.test_tree.insert("", "end",
            values=(num, f"{ms:.1f}", f"{deviation:+.1f}", status),
            tags=(tag,)
        )
```

- [ ] **Step 3: Implement update_test_suggestion()**

```python
def update_test_suggestion(self, measurements, target):
    """Update the suggestion panel based on measurements."""
    if len(measurements) < 20:
        self.test_suggestion_var.set(self.t("test_suggestion_waiting"))
        return

    avg = sum(measurements) / len(measurements)
    precision = max(0, 1 - abs(avg - target) / target) * 100

    if precision >= 98:
        self.test_suggestion_var.set(self.t("test_suggestion_excellent"))
    else:
        overhead = avg - target
        suggested = target - overhead
        text = self.t("test_suggestion_overhead").format(
            overhead=f"{overhead:+.1f}",
            target=f"{target:.0f}",
            suggested=f"{suggested:.0f}"
        )
        self.test_suggestion_var.set(text)
```

- [ ] **Step 4: Verify by running the app**

Run `python main.py`. Go to Test tab, click Start Test. Verify:
- Stats update in real-time
- Treeview shows colored rows
- Suggestion appears after 20 measurements

- [ ] **Step 5: Commit**

```bash
git add main.py
git commit -m "feat: add real-time statistics, treeview log, and suggestion panel"
```

### Task 9: Add mutual exclusivity and apply_language for test tab

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Add mutual exclusivity to start_program()**

In the existing `start_program()` method, add at the beginning:

```python
# Stop test if running
if self.test_running:
    self.stop_test()
```

- [ ] **Step 2: Update apply_language() to include test tab widgets**

Add test tab widget updates to `apply_language()`:

```python
# Test tab
if hasattr(self, 'test_tab'):
    self.notebook.tab(2, text=self.t("tab_test"))
    self.test_config_frame.configure(text=self.t("test_config_title"))
    self.test_btn_toggle.configure(
        text=self.t("test_btn_stop") if self.test_running else self.t("test_btn_start")
    )
    self.test_btn_clear.configure(text=self.t("test_btn_clear"))
    # ... all test stat labels ...
    self.refresh_test_config_display()
```

- [ ] **Step 3: Final verification**

Run `python main.py`. Test the full flow:
1. Switch language — all tabs update
2. Configure 100ms in tab 1
3. Go to Test tab — config is shown
4. Start test — stats appear, treeview fills
5. Start main tab action — test auto-stops
6. Stop main action, start test again — main tab auto-stops

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add mutual exclusivity and i18n support for test tab"
```
