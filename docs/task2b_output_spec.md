# Phase 24 Task 2B output and policy specification

## Scope

Phase 24 exports the frozen Phase 22 allocation into the organizer-supplied
`submission_task2b.csv` template and generates the required short
prioritization policy. It does not run the optimizer or change any frozen
decision. Real-data execution is human-local; repository tests are synthetic.

## Preconditions

Every local command fails closed unless:

- the Phase 22 manifest state is `FROZEN` and its allocation/trip-summary
  hashes match;
- Phase 23 records both the own-validator and organizer-checker statuses as
  `PASS`; and
- the Phase 23 evidence refers to the same frozen allocation.

The immutable Phase 23 evidence may be supplied directly or resolved from the
latest valid timestamped `checker_runs/*/checker_evidence.json` record.

## Official-template export

The official template controls the exact columns, identity values, and row
order:

`scenario, order_ref, outlet_id, decision, vehicle_id, trip_id`

The exporter resolves `submission_task2b.csv` through the dataset manifest,
joins by the unique nonblank `order_ref`, verifies scenario and outlet identity
against both the frozen allocation and canonical S1 source, and fills only the
three answer columns. Repeated `outlet_id` values are valid.

The final CSV is written without an index to a temporary file, read back,
fully revalidated, and atomically moved to `outputs/submission_task2b.csv`.
Existing output is not overwritten unless `--force` is explicit and the prior
private export manifest names the same frozen allocation hash.

Private export evidence is stored under
`reports/private/phase24_task2b_output/`; it contains hashes, aggregate counts,
and PASS statuses only.

## Policy evidence and writer

The policy writer deterministically combines approved static prose with
aggregate metrics derived locally from the canonical scenario, frozen
allocation, frozen trip summary, compatibility recomputation, and Phase 23
PASS evidence. Its provenance map binds every inserted scenario number to an
evidence key and source artifact. No order, outlet, vehicle, or trip membership
lists are written to policy evidence.

The policy separates official hard feasibility from the WayLoom lexicographic
engineering policy. It states the official trip-time formula, excludes return
travel, explains the 270-minute Fresh and 480-minute Style+Tech limits, uses a
conservative definition of unavoidable deferral, and reports operational
impact without inventing monetary cost.

The preferred engineering target is at most 550 words; more than 650 words is
a validation failure. These thresholds operationalize the booklet's
"approximately one page or less" requirement and are not organizer rules.

## Local execution order

Run the export, then the policy builder, then the final Phase 24 validator.
The final validator does not rerun the optimizer or organizer checker. It
rechecks frozen hashes, Phase 23 PASS evidence, template identity, placeholder
removal, allocation/candidate parity, output SHA256, policy provenance, length,
and absence of private row identifiers.
