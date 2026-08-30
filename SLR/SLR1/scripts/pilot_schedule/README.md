# Pilot schedule query helper

[`queries.py`](queries.py) renders the protocol's nine main partitions and four PSR partitions without changing concept membership. It imports the literal and pair declarations from [AIAA Pilot 003](../aiaa_arc_pilot003/queries.py).

[`build_plan.py`](build_plan.py) creates a no-clobber pilot plan for the shared event runner. Source pilots may use a custom field or cell plan when the full expression exceeds a validated source limit. The saved pilot artifact remains authoritative.
