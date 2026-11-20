# Benchmark fixtures, 2026-10-08

Blind benchmark of Haiku 5.5, Sonnet 5.5 and Opus 5.5 on the offline 2D
pipeline (PROJECT_STATE.md section 15; skill references/model-routing.md).

- T1_r1, T1_r3: Haiku 5.5. T1_r2: Sonnet 5.5. T1_r4: Opus 5.5.
  Each is a new two-storey 4-bed villa designed from the same brief. The judges'
  defects are in research/2026-10-08/benchmark_results.json. The skill's
  test_validate_plan.py (TestBenchmarkGaps) checks that the new checks find them.
- faulted/: the Fairway with 6 injected faults (inject.py made it from
  projects/fairway/villa_design.py). It is the T2 repair task and the
  rules-report test fixture.
- brun.py: the runner the benchmark used (VILLA_OUT kept in the run folder).
- cost.py: list-price cost per agent from workflow transcripts.

These designs are test data, not deliverables. Several are deliberately bad.
