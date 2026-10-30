# Title-rule review — version 1, 30 October 2026

We reviewed **36 possible bug reports**, with 12 from each period. Each period used `random.Random(30412).sample(...)`. The sample includes only reports that pass the label-exclusion rule and already have at least one title match. It does not include reports with no match. It cannot measure missed-report frequency or overall accuracy. We did not change rules after reviewing the sample.

The review uses original titles and up to 2,500 body characters from [saved records](data/classified.jsonl). Linked GitHub issues can change later. The assigned tags below record the rules at review time. Body text helps check context; it does not change title-only results.

## Findings

- Rules find many explicit crash, hang, and API mentions. A match does not confirm a defect, component, or cause. One report can have several tags.
- Two matches use the wrong context. “Crash report” metadata is read as a crash (#43304). “Instead of an error” is read as an emitted error (#46876). Removing code blocks cannot fix these title-context cases.
- Missed contexts include `net.connect()`, `Bun.Terminal`/PTY, JIT, Node streams, wrong or missing results, and “never reaped / never settles”. No tag does not mean no problem.
- Shorter before-merge crash titles often name no component. Later titles can contain more detail. This can change component shares even with unchanged rules. Check unmatched titles and the body text check as well.
- Feature requests can pass the label filter (#32115). We therefore call the input “possible bug reports”.
- Reports opened after the merge can concern old Zig builds (#31400, #36235, #39046). A report date does not prove the implementation.
- “Bundled” can describe runtime distribution rather than a build defect (#24823). Component tags describe context, not cause.

## Sample records

“Supported” means the text supports the assigned tags. “Supported; missed context” means another clear component or problem was missed. No overall accuracy percentage is given. Original issue titles and assigned tag keys are preserved below.

### Before merge

Reports available for sampling: 1315 reports with at least one title match.

| Issue | Assigned components | Assigned symptoms | Review |
| --- | --- | --- | --- |
| [#24724 — Bun crash in WSL2](https://github.com/oven-sh/bun/issues/24724) | — | crash | **Supported.** Crash is explicit; no component can be determined from this sparse title. |
| [#25188 — bun crashed after asking it to follow instructions in a .md file and convert c# code to python](https://github.com/oven-sh/bun/issues/25188) | — | crash | **Supported.** Crash is explicit. The prose describes Claude usage, not a Bun component. |
| [#24823 — Crash from bundled Gemini CLI](https://github.com/oven-sh/bun/issues/24823) | build | crash | **Context only.** Crash is explicit. Bundled Gemini CLI gives build context, but the body reports a runtime crash and does not establish a bundler root cause. |
| [#25079 — panic(main thread): Internal assertion failure](https://github.com/oven-sh/bun/issues/25079) | — | panic, failure | **Supported.** Panic/assertion and generic failure overlap by construction. Body identifies install/lockfile context that the title omits. |
| [#26905 — Segmentation fault at address 0x206C5580080](https://github.com/oven-sh/bun/issues/26905) | — | crash | **Supported.** Fatal signal is explicit. Shell/JSC stack frames in the body do not establish a component from the title. |
| [#27784 — vite dev hangs on port retry with --bun flag and IPv6 localhost ::1](https://github.com/oven-sh/bun/issues/27784) | — | hang | **Supported; missed context.** Hang is explicit. IPv6 localhost/port retry suggests network context but receives no component tag. |
| [#28035 — fetch().body piped through TransformStream does not propagate backpressure](https://github.com/oven-sh/bun/issues/28035) | network | — | **Supported; missed context.** fetch supports network. Missing backpressure is a correctness problem and body describes OOM; neither symptom is captured by the title rules. |
| [#30613 — Bun crashes on non-AVX2 CPUs (all versions after v1.3.8)](https://github.com/oven-sh/bun/issues/30613) | — | crash | **Supported.** Crash is explicit. CPU compatibility context is outside the current component rule set. |
| [#28842 — Segfault in JIT worker thread during DFG LICM phase on macOS aarch64 (Bun v1.3.11)](https://github.com/oven-sh/bun/issues/28842) | — | crash | **Supported; missed context.** Segfault is explicit. JIT worker context is not recognised as native/JSC by the rules. |
| [#30564 — panic: Internal assertion failure — Claude Code standalone on Windows 11 x64 (baseline)](https://github.com/oven-sh/bun/issues/30564) | — | panic, failure | **Supported.** Panic and generic assertion failure are explicit; the title has no safely assignable component. |
| [#25912 — Bun.Terminal PTY allocation fails after extended runtime/sleep on macOS](https://github.com/oven-sh/bun/issues/25912) | — | failure | **Supported; missed context.** Allocation failure is explicit. Bun.Terminal/PTY is process context but is not recognised. |
| [#24679 — segmentation fault when running claude](https://github.com/oven-sh/bun/issues/24679) | — | crash | **Supported.** Fatal signal is explicit; Claude usage does not isolate a Bun component. |

### Canary period: Zig stable and Rust canary

Reports available for sampling: 690 reports with at least one title match.

| Issue | Assigned components | Assigned symptoms | Review |
| --- | --- | --- | --- |
| [#30789 — bun update --latest renders arrows as mojibake in Rust port](https://github.com/oven-sh/bun/issues/30789) | packages | — | **Supported; missed context.** bun update supports package-manager context. Mojibake is wrong output but not recognised as a symptom. |
| [#31580 — tls: sni_cb should return SSL_TLSEXT_ERR_ALERT_FATAL when SNICallback throws or returns non-SecureContext](https://github.com/oven-sh/bun/issues/31580) | network | — | **Supported.** TLS supports network. Body reports incorrect handshake handling; a symptom is not inferred from the title alone. |
| [#30939 — stream/web TransformStream + Node Transform.fromWeb causes internal webstreams_adapters crash (this is not an object)](https://github.com/oven-sh/bun/issues/30939) | — | crash | **Supported; missed context.** Crash is explicit. stream/web and Node stream compatibility are outside the recognised component patterns. |
| [#31400 — node:fs/promises missing mkdtempDisposable export (Bun 1.3.13) — blocks production CLI startup](https://github.com/oven-sh/bun/issues/31400) | filesystem | correctness | **Supported.** node:fs supports filesystem; missing export supports correctness. The report names Zig stable 1.3.13 despite arriving after the rewrite merge. |
| [#32734 — Bun 1.4 regression: bidirectional WebSocket proxy scope hangs after successful messages](https://github.com/oven-sh/bun/issues/32734) | network | hang | **Supported.** WebSocket/proxy and hangs support both tags. A regression claim in a report is not independently verified here. |
| [#34065 — SIGTRAP: C++ exception in __cxa_finalize_ranges at exit after in-process onnxruntime (via @huggingface/transformers) inference — tests pass, teardown panics](https://github.com/oven-sh/bun/issues/34065) | — | panic | **Supported; missed context.** Panics is explicit. SIGTRAP is not in fatal-signal patterns, and in-process native onnxruntime context receives no component tag. |
| [#34415 — Canary 1.4.0 HTTP server emits malformed chunked responses, breaks behind nginx reverse proxy (502)](https://github.com/oven-sh/bun/issues/34415) | network | — | **Supported; missed context.** HTTP/proxy supports network. Malformed responses/breakage is a correctness symptom omitted by the title rules. |
| [#39070 — fs.watch on macOS reports only one file per ~40ms window, so bulk changes are mostly lost](https://github.com/oven-sh/bun/issues/39070) | filesystem | — | **Supported; missed context.** fs.watch supports filesystem. Lost bulk-change events is a correctness symptom omitted by the title rules. |
| [#36235 — bun test --parallel intermittently deadlocks: one worker wedges with all threads in condvar waits (lost wakeup), parent hangs forever](https://github.com/oven-sh/bun/issues/36235) | test | hang | **Supported.** bun test supports test runner; deadlock/hangs supports hang. Body names Zig stable 1.3.14: date groups do not prove the language. |
| [#39046 — Bun.SQL MariaDB hangs after Bun.password or asynchronous node:crypto operation on Windows](https://github.com/oven-sh/bun/issues/39046) | database | hang | **Supported.** SQL/MariaDB supports storage; hangs supports hang. Body names Zig stable 1.3.14. |
| [#32115 — Support bin field in bun info / bun pm view output](https://github.com/oven-sh/bun/issues/32115) | packages | — | **Feature request included.** Package-manager context is supported, but the body uses the feature-request template. The exclusion-label bug definition admits unlabelled feature requests. |
| [#30697 — net.connect() fails with "DEFAULT_IPV6_ADDR is not defined" when using IPv6-mapped IPv4 address](https://github.com/oven-sh/bun/issues/30697) | — | failure | **Supported; missed context.** fails supports generic failure. net.connect() is an obvious network API but is not recognised by current network patterns. |

### After Rust stable, all reported builds

Reports available for sampling: 998 reports with at least one title match.

| Issue | Assigned components | Assigned symptoms | Review |
| --- | --- | --- | --- |
| [#39786 — Bun.plugin() cannot safely instrument JavaScript: onLoad() breaks CommonJS](https://github.com/oven-sh/bun/issues/39786) | modules | failure | **Supported; missed context.** CommonJS supports module context and cannot supports failure. Bun.plugin/onLoad also gives loader/plugin context not separately recognised. |
| [#45365 — macOS: an exited Bun.spawn child is sometimes never reaped inside bun test (zombie, exited never settles)](https://github.com/oven-sh/bun/issues/45365) | test, process | — | **Supported; missed context.** Bun.spawn and bun test support process/test. Never reaped / never settles indicates a failure to finish but misses the hang regex. |
| [#45055 — TLS: certificates under a CA with an iPAddress name constraint fail with UNSUPPORTED_CONSTRAINT_TYPE (Node accepts them)](https://github.com/oven-sh/bun/issues/45055) | network | failure | **Supported.** TLS supports network and fail supports failure; body is a certificate-validation compatibility report. |
| [#40466 — bun install hangs in Resolving dependencies when a transitive peer's manifest is cached from a different registry URL](https://github.com/oven-sh/bun/issues/40466) | packages | hang | **Supported.** bun install and hangs explicitly support package-manager/hang tags. |
| [#39941 — bun test --isolate: synchronous require() of a large ESM graph in a preload pins the file's global — dynamic import() of the same graph doesn't (survives #39818)](https://github.com/oven-sh/bun/issues/39941) | test, modules | — | **Supported; missed context.** bun test / require / ESM support test/module contexts. Pinned global lifetime and retained memory are not captured as symptoms in the title. |
| [#44788 — Map insertion with object-wrapped values is up to 1.6 times slower than Node](https://github.com/oven-sh/bun/issues/44788) | — | performance | **Supported.** slower explicitly supports performance. Underlying benchmark validity is outside a title-tag audit. |
| [#40340 — require(esm): __esModule is not an own enumerable property (Object.keys omits it)](https://github.com/oven-sh/bun/issues/40340) | modules | — | **Supported; missed context.** require/esm supports module context. Omitted enumerable property is wrong output but no symptom rule matches. |
| [#46876 — node:http: destroying a client request mid-body emits 'end' with a partial body instead of an error](https://github.com/oven-sh/bun/issues/46876) | network | failure | **Wrong problem match.** Network is supported. error appears in instead of an error: the defect is missing error propagation and truncated data, not an emitted failure. Current failure regex ignores negation/expected behaviour. |
| [#42783 — process.on("memoryPressure") on Linux emits a false "critical" event after every arm (kernel PSI seeds unprivileged triggers from the wrong aggregator)](https://github.com/oven-sh/bun/issues/42783) | — | correctness | **Supported; missed context.** wrong supports correctness. process.on(memoryPressure) gives event/process context and a memory-related topic, neither recognised by title patterns. |
| [#43304 — Linux: bun:jsc memoryUsage().peak and the crash report peak include the parent's peak RSS](https://github.com/oven-sh/bun/issues/43304) | native | crash | **Wrong problem match.** bun:jsc supports native/JSC context. crash appears only in crash report peak: the body reports incorrect peak-RSS measurement, not a crash. Crash symptom is a match in the wrong context. |
| [#43476 — JavaScriptCore accepts await as an arrow function parameter name in an async function when the parser's function cache holds the arrow function](https://github.com/oven-sh/bun/issues/43476) | native | — | **Supported; missed context.** JavaScriptCore supports native/JSC context. Accepting invalid syntax is a correctness problem not captured by these title patterns. |
| [#44925 — node:http: res.end() after the client disconnects sets _header but leaves headersSent false (regression in 1.4.3, breaks Express res.download() / send)](https://github.com/oven-sh/bun/issues/44925) | network | — | **Supported; missed context.** node:http supports network. Inconsistent headersSent state/breakage is a correctness problem but the title rules assign no symptom. |

## Next check

To make claims about actual defect types, use a separate sample that reviewers have not inspected before. Include reports with no title match. Define review rules, then have reviewers label the report text. Measure correct matches and missed cases for each type. Do not tune the rules and test them on the same examples. Severity, security risk, regression status, and Rust/JSC/FFI causes require more evidence. This review does not infer them.
