# Reading the version-family infographic

## Reader task

See when reports arrive for stated Zig-line and Rust-line versions. Keep merge, canary availability, and stable rollout separate. Inspect a problem type and a concrete version without treating dates as proof of implementation.

## Design choice

A version-by-week map is the main view. Overlaid version lines would overlap, and stacked families alone would hide concrete versions. A shared count scale makes rows comparable without turning report counts into risk estimates.

The report keeps its established dark/light palette and system typography. The mode is Read, with native controls for exploration. This is an extension of the existing report. It uses the impeccable guidance for clear labels, restrained hierarchy, progressive detail, and accessible controls.

## Reading order

1. A three-period strip explains that Zig stable continued during Rust canary.
2. Version rows are grouped as Zig, Rust, or unclear. Colour shows weekly report counts on one common scale.
3. An aligned npm line gives all-version download context. It is never labelled per-version installations.
4. Family and type selectors reduce the map. The all-version view keeps every row available.
5. Selecting a cell opens one-day counts for that stated version and week. A native selector provides the same route by keyboard.
6. Three-period rate tables show raw counts beside rates. They do not combine canary and after-stable into one headline.

## States and limits

Zero-report cells use the darkest colour. Missing npm observations remain gaps. Partial issue weeks are labelled. Small screens scroll the map horizontally so version labels and cells remain legible. All data remains offline.

Unknown versions, multiple versions, conflicting dates, and old development version strings after merge remain unclear. Row counts include every report. Cell tooltips give dates and exact counts. The first view groups smaller rows but the all-version control exposes them.

The graphic shows a temporal association. It does not estimate a causal Rust effect or bugs per installation. No historical daily denominator exists for each version family.
