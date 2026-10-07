# Privacy and Data Boundary

`synthetic_demo` is the mandatory default. The service generates deterministic examples without loading competition records, official outputs, private reports, or frozen model artifacts.

Official private competition records are never published. Official submissions are not API data sources. The public contract contains no official identifiers, row-level allocations, model files, diagnostic reports, request bodies, response bodies, filesystem locations, or artifact hashes.

The share package is allowlisted to documentation, schemas, synthetic examples, OpenAPI, version metadata, and its own manifest. Symlinks, hidden files, path traversal, arbitrary model locations, batch exports, record lookup, and dataset upload are rejected.

`private_local` is local/team-authorized only. It requires configuration plus two environment opt-ins, stays bound to loopback by default, and is not approved for an internet deployment. This contract provides no production authentication claim.

CORS is disabled by default. If a local frontend needs CORS, configure only its known local origin. Wildcard origins are rejected.

Errors are deliberately generic. Service logging includes method, route, status, latency, mode, and request identifier only. It excludes bodies, feature vectors, private identifiers, and filesystem locations.

Normal synthetic validation does not read official identifiers, so its collision-audit status is `NOT_RUN`. An explicit human-local audit may compare identifier sets and emit aggregate counts only; it never prints or saves identifier values. The private command is intentionally excluded from the shareable package.
