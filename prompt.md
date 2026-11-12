0. there is a Mission aka session. at a technical level, a session has some imports, like math for math.pi

1. a Mission has Stakeholders and Third Parties. Stakeholders are specialised into child classes for which the only difference is the name of the child class (RegulatoryAgency, MissionStakeholder, LaunchProvider, Partner). these classes do nothing else.

2. a Mission has Domain Elements, which specialise into Space Segment and Ground Segment. Space Segment has Cumulative Properties, in this case Power, Cost, Mass and Volume. Space Segment has a set of Modes. Power can have different values for each Mode depending on . A Mission Domain Element has a property Subsystems.

3. A Subsystem has Cumulative Properties. it has the same set of Modes as its parent.

3. a Mission has an Orbit.

4. A Subsystem has a property Components. each Component has properties Cost, Mass, and Volume. It has its own set of Modes mapped to the Modes of its parent. It has Voltage, Current depending on its own Modes.

1. there are Requirements. requirements can reference Parameters, which have Units and reference Expressions that apply in States. Expressions are Python code. Expressions can reference other Parameters, even from other Requirements.

2. there are Verification Means. A verification means  
