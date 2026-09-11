# Implementation map

The repository currently has explicit contracts for brain/provider boundaries, memory/context, decision proposals, routing, execution policy, Home Base events, capabilities, and device identity.

The first concrete capability adapters are read-only: system diagnostics, scoped workspace file access, and bounded HTTP(S) retrieval.

The next implementation wave should add browser and computer adapters only through those existing contracts. Device orchestration follows after pairing/authentication is defined.
