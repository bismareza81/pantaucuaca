# Silent Climate — UI/UX Implementation Plan

## 1. Audit Results

### 🔴 Critical Bugs
| # | Issue | Location | Impact |
|---|---|---|---|
| B1 | `anthropic-version` header missing | Oracle API call | 400 error on every Oracle message |
| B2 | Duplicate `tab-list` CSS (lines 119–122 vs 153–155) | CSS block | Second rule silently overrides first |
| B3 | `oracle_input` session state key ≠ widget key (`oracle_input_field`) | Tab 5 | Stale input state after rerun |
| B4 | `Courier Prime` referenced in Plotly legend font but never imported | Charts | Falls back to system font |
| B5 | `.sh-info` border double-declaration (shorthand clobbers left border) | CSS | Left accent border disappears |

### 🟠 Contrast & Readability Failures
| Element | Current Color | On Background | Contrast Ratio | WCAG AA (4.5:1) |
|---|---|---|---|---|
| `--fog-faint` labels | `#5A5450` | `#000000` | ~2.8:1 | ❌ FAIL |
| `sh-card-label` | `#5A5450` | `rgba(0,0,0,0.9)` | ~2.8:1 | ❌ FAIL |
| `sh-header` text | `#9A9288` | `#000000` | ~3.6:1 | ❌ FAIL |
| Forecast date | `#5A5450` | card bg | ~2.8:1 | ❌ FAIL |
| Oracle placeholder | `#3A3A3A` | `#000000` | ~1.6:1 | ❌ FAIL |
| Info box text | `#5A5450` | `rgba(0,0,0,0.86)` | ~2.8:1 | ❌ FAIL |

### 🟡 UX Friction Points
| # | Issue | Impact |
|---|---|---|
| U1 | Block container has no horizontal padding — content bleeds to edge on narrow screens | Layout break |
| U2 | Forecast card fonts (0.55–0.6rem) far below readable minimum (0.75rem) | Unreadable |
| U3 | Tab labels (0.72rem) too small, no padding on mobile | Tap target too small |
| U4 | Oracle chat history has no max-height + scroll — long conversations push input off screen | Major UX |
| U5 | Section headers `margin: 32px 0 18px 0` wastes vertical space at top of each tab | Wasted space |
| U6 | Sidebar controls cramped — no padding between selectbox, slider, button | Crowded |
| U7 | Cards in 4-column grid collapse badly at medium widths | Responsive break |
| U8 | Plotly charts have `margin: l=4, r=4` — axis labels clip on left | Chart clipping |
| U9 | Oracle send button fires on every rerun (no input clear after send) | Duplicate messages |
| U10 | Radio toggle CSS is fragile — relies on `:has()` which has limited browser support | Toggle broken in Firefox |
| U11 | AQI pollutant cards use 6 columns — cramped on laptops, breaks on tablets | Layout break |
| U12 | Footer border uses `#242424` (old var) not `var(--void-border)` | Inconsistency |

---

## 2. Proposed Changes

### Phase A — Bug Fixes (non-negotiable)
- **B1** Add `"anthropic-version": "2023-06-01"` and `"x-api-key": os.environ.get("ANTHROPIC_API_KEY","")` to Oracle headers
- **B2** Remove duplicate `.stTabs [data-baseweb="tab-list"]` block
- **B3** Clear `oracle_input_field` after send via session state workaround
- **B4** Import `Share Tech Mono` for all Plotly legend/axis fonts
- **B5** Fix `.sh-info` — use individual border properties, not shorthand

### Phase B — Contrast Fixes
Raise all failing text to minimum WCAG AA:
- `--fog-faint`: `#5A5450` → `#7A7470` (ratio ~4.6:1)
- `--fog-dim`: `#9A9288` → `#A8A098` (ratio ~5.2:1)
- Forecast date/sublabel: → `#7A7470`
- Oracle placeholder: `#3A3A3A` → `#5A5450`

### Phase C — Layout & Spacing
- **Block container**: add `padding: 0 1.5rem` for breathing room
- **Forecast cards**: min font 0.72rem, increase padding
- **Tab labels**: `font-size: 0.78rem`, `padding: 12px 20px`
- **Oracle chat**: wrap history in `max-height: 420px; overflow-y: auto` container
- **Section headers**: reduce top margin `32px → 22px`
- **Sidebar**: add `gap` between controls via `st.markdown` spacers
- **AQI pollutants**: `st.columns(3, 3)` split instead of 6 flat → better on tablets
- **Plotly margin**: `l=28, r=12` to prevent axis clipping
- **Radio toggle**: replace `:has()` with JS-injected `data-checked` attribute for cross-browser

### Phase D — Visual Polish
- **Cards**: add subtle top gradient line that pulses (CSS animation)
- **Sidebar title**: larger, better line-height
- **Tab active state**: add left border accent in addition to bottom border
- **Oracle messages**: add monospace timestamp to each message
- **Section header `::after`**: extend accent line to 80px
- **Scrollbar**: slightly wider (4px) for discoverability
- **Input focus ring**: consolidate all focus styles globally

---

## 3. Files to Modify
- `app.py` — all changes

## 4. Risk Assessment
- All changes are CSS/layout only except B1 (API header) and B3 (session state)
- No API schema changes
- No data fetcher changes
- Animation canvas untouched

## 5. Estimated Improvement
| Metric | Before | After |
|---|---|---|
| WCAG contrast failures | 6 elements | 0 |
| Critical bugs | 5 | 0 |
| Minimum font size compliance | 60% | 100% |
| Oracle usability | Broken (400 error) | Functional |