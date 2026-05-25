# TODO

Future topics to learn:

1. Source data test layer
   - Add an intermediate model for testing flattened source events.
   - Why: current-state `stg_person` can hide older raw data problems.

2. Custom data tests
   - Add tests for rules that generic tests cannot express.
   - Why: duplicate `event_id` with different data needs custom logic.

3. Delete mutations
   - Decide how `mutation = delete` should appear in current state.
   - Why: the raw contract has deletes, but the current model still shows full data.

4. Address feed
   - Add `raw_address` and `stg_address`.
   - Why: this introduces a second event type and person-address relationships.

5. Relationship tests
   - Test links between current addresses and current people.
   - Why: `address.v1` references `person_id`, but events can arrive out of order.

6. Snapshots or history tables
   - Keep historical person states, not only current state.
   - Why: current-state staging is useful, but analytics often need history.

7. dbt docs and lineage
   - Generate docs and inspect the DAG.
   - Why: after multiple models, lineage becomes important.

8. Operational commands
   - Learn normal run, test, full refresh, and selector patterns.
   - Why: incremental models need careful rebuild and test habits.

Later:

- orchestration
- CI/CD
- exposures
- packages
- advanced macros
