0. A Mission is a session representing one configuration. Alternatives use separate sessions. Session imports include `import math as math` by default.

1. A Mission has Stakeholders and Third Parties. Stakeholder subclasses (RegulatoryAgency, MissionStakeholder, LaunchProvider and Partner) differ only by class name.

2. A Mission has Domain Elements specialised into Space Segment and Ground Segment. Domain Elements have Subsystems. A newly added Space Segment creates predefined Subsystems. Space Segment has Cumulative Properties for Power, Cost, Mass and Volume. Each class defines its aggregation scope and counts each included physical instance once. Aggregation is a recommended pattern. Space Segment has Spacecraft Modes with orbit period allocations. Power can vary by Spacecraft Mode. CubeSat Bus has a Units Property. When first added, it creates bus mass and volume Requirements whose Targets are Units times explicit per-U limits.

3. A Subsystem has Cumulative Properties and shares its parent's Spacecraft Modes. Spacecraft Modes, Component Modes, Component States and time allocations are distinct classes. Their detailed timing and mapping rules remain to be specified.

4. A Mission has an Orbit with Altitude, Beta Angle and Eccentricity. Illumination support for Eccentricity is deferred.

5. A Subsystem has Components. Each Component has Cost, Mass and Volume. Its Component Modes map to its parent's Spacecraft Modes through separate allocations. Voltage and Current are defined for the on and off Component States of each Component Mode.

6. Component specialisations belong to specific Subsystem specialisations. A newly added Subsystem creates predefined Components. Default creation runs once per instance. Restoration preserves saved objects and deliberate deletions.

7. EPS Component specialisations have a COTS property. COTS specialise EPS Components by fixing their property values. COTS can inherit from several EPS Component classes to represent integrated solutions. EPS Component properties can reference COTS properties. Filtering COTS by class is a recommended expression pattern.

8. Requirements have Verification Conditions. Each condition has Measure, Target and a Python one-line expression returning a boolean. Evaluation status is separate from the boolean result. Requirements also have a plain text Rationale and a Statement template. Statements can display owned Measures and Targets. Statement content is independent of Verification Conditions.

9. A Property holds a Python one-line expression and a Unit annotation. The Unit class provides descriptive annotations only. Expressions can reference any instance's Properties in the Mission and use math functions. Longer calculations can call arbitrary imported Functions. Session imports use `import package as pkg`, with calls as `pkg.function(...)`. Custom Functions have named, annotated inputs with no optional inputs or defaults. They return a NamedTuple with annotated fields. Each call explicitly binds every input to a Property. Calls execute independently without caching or execution protection. Hidden Function dependencies are an accepted gap.

10. An instance whose Property is referenced in a Requirement's Measure is verified by that Requirement. A false Verification Condition makes the instance unverified. Properties referenced transitively inherit that condition. Each propagated failure exposes its originating Requirement, condition and dependency path.
