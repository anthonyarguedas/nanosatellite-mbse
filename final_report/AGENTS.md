All final report figures go in `fig`.

The final report is the sole source of truth.
It must not be necessary to read any other file to fully understand the proposed framework and its OOSEM design process.

The final report only describes the framework that will be built.
The framework code itself will live elsewhere.
The final report will be the only input used to develop the framework.

Abbreviations go in `final_report/glosario.tex`.
Concise theoretical concepts (mostly related to systems engineering, nanosatellites, EPS, and OOSEM) go in `final_report/teoria.tex`.

The final report will not invent terminology.
It will use systems engineering concepts from OOSEM, and other technical concepts from the cited literature.
The report will avoid software engineering-specific terminology unless necessary to describe the framework, as its audience has more of a systems/electrical/space engineering background.

The final report will never mention specific local files or artifacts, since the final audience will only have access to its compiled PDF.
Supplementary information, if relevant, can be supplied in appendices.

`final_report/main.tex` lists all sections of the final report.
The full report, excluding cover, indexes, formalities, and appendices, must not be over 70 pages.
Appendices can only include minimal prose, thus they are mostly tables and figures.
The report is very long, so under no circumstances can it all be written in a single try.
Do not edit parts of the report that you were not asked to edit.

Never write "X is pending" or "revise X if Y" in the audience-facing prose.
These are report writing tasks, and no such conditionals or loose ends can remain in the final report unless they are legitimate gaps of the entire report, and in that case they'd go in the dedicated future work section.
Write what you currently know as it will be written in the final report, and disclose what's pending in LaTeX comments.
Delete any stale LaTeX comments.
Visible prose overrides the hidden comments.

The entire report must be written in good prose.
Nobody, not even the stakeholders, will read the report if the prose is bad, even if the framework is useful or interesting.
Some people will still not read the prose even if it's good, so the diagrams must be good as well.
Using Syside SysML v2 renders is a bad idea. They contain little information, are hard to read, and are honestly ugly. SysML v1-inspired or purely illustrative diagrams should be used instead.
Maintain a consistent visual language: monochrome, serif, academic figures.

## Figure visual language

- Use monochrome vector diagrams, Times New Roman text, white backgrounds, thin black outlines and square corners. Reserve light gray for external participants.
- Keep black-box views opaque. Show logical parts inside the framework only in architecture views, with external participants outside.
- Give each interface one rectangular boundary port. Put its IF identifier on the rectangle and pass all its exchange routes through it.
- Distinguish information exchanges with solid, dotted and dash-dot lines. Reserve dashed lines for control.
- Use one large foreground arrowhead at each receiving end. Intermediate ports carry continuous routes without extra heads.
- Label exchanges alongside their routes. Put legends, explanations and authority notes in captions. Keep figures free of footers.
