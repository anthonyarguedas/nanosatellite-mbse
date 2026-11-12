0. there is a Mission aka session. at a technical level, a session has some imports, like math for math.pi by default.

1. a Mission has Stakeholders and Third Parties. Stakeholders are specialised into child classes for which the only difference is the name of the child class (RegulatoryAgency, MissionStakeholder, LaunchProvider, Partner). these classes do nothing else.

2. a Mission has Domain Elements, which specialise into Space Segment and Ground Segment. Space Segment has Cumulative Properties, in this case Power, Cost, Mass and Volume. A Cumulative Property is a recommended pattern that sums a property for all children. Space Segment has a set of Modes. Each mode has an allocation of the orbit period. Power can have different values for each Mode. A Mission Domain Element has a property Subsystems. a Space Segment has an init to get itself some predefined Subsystems.

3. A Subsystem has Cumulative Properties. it has the same set of Modes as its parent.

3. a Mission has an Orbit. Orbit has properties Altitude, Beta Angle, and Eccentricity.

4. A Subsystem has a property Components. each Component has properties Cost, Mass, and Volume. It has its own set of Modes mapped to the Modes of its parent with their own period allocations. It has Voltage, Current for the on and off states of its own Modes.

5. There are several specialisations of Components, which are all specific to a certain specialisation of Subsystem. On init, Subsystems will assign themselves some Components.

6. Specialisations of Components assigned to the EPS subsystem specialisation may have several properties. They also have a property COTS. COTS are specialisations of EPS components that do nothing else than fixing their property values. COTS can inherit from more than one EPS component to model integrated solutions. The property values of EPS components can reference the properties of COTS. it is a recommended pattern that property expressions of EPS components use the class of COTS to filter them.

7. there are Requirements. requirements have properties Verification Conditions. Verification Conditions have properties Measure and Target and resolve to a boolean.

8. Properties are Python one-line expressions, including functions from math by default. for more than one line, an expression can call an arbitrary Function imported from a package at the session level. all imports must be in the format import package as pkg, then used as pkg.function(). the Function must have type-annotated and named inputs and outputs. the expression has to explicitly assign one available Property to each input of the Function. expressions can reference the properties of any instance in Mission.

9. an instance whose property is referenced in the Measure of a Requirement is said to be verified by that requirement. if the associated Verification Condition resolves to false, the instance is said to be unverified. properties referenced inside properties also bear the verification condition.
