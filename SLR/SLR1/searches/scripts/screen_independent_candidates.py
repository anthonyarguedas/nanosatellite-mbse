#!/usr/bin/env python3
"""Apply the documented title/abstract screen to the independently frozen candidate set.

This script contains the assessor's record-level title/abstract decisions.  It
never assigns a final Route A/Route B decision: that requires a source-locatable
full-text EPS anchor, model anchor, and bridge under protocol.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "eps-mbse-slr-2026"

# Values: (screening_tier, concise rationale, confidence, retain_as_secondary)
DECISIONS: dict[str, tuple[str, str, str, bool]] = {}

TITLE_DISPLAY_OVERRIDES = {
    "eps-mbse-slr-2026-r0168": "Space Factory 4.0 — New processes for the robotic assembly of modular satellites on an in-orbit platform based on ‘Industrie 4.0’ approach",
}
POPULATION_RE = re.compile(r"\b(?:cube\s*sat(?:s)?|nano[- ]?satellite(?:s)?|nanosat(?:s)?|\d+u\s+(?:cube)?satellite)\b", re.I)
STRUCTURED_MODEL_RE = re.compile(r"\b(?:mbse|sysml|model[- ]based systems? engineering|systems? model(?:ing|ling)?|systems? engineering|digital engineering|digital twin|reference model|requirements?[- ]in[- ]loop|concurrent model)\b", re.I)
EPS_RE = re.compile(r"\b(?:electrical power|electric power|power subsystem|power system|power budget|energy budget|energy model|electrical architecture|pcdu|pmad|battery|solar|power consumption)\b", re.I)


def add(ids: str, tier: str, rationale: str, confidence: str = "moderate", secondary: bool = False) -> None:
    for report_id in ids.split():
        if report_id in DECISIONS:
            raise RuntimeError(f"Duplicate manual screening entry: {report_id}")
        DECISIONS[report_id] = (tier, rationale, confidence, secondary)


# Core = metadata directly signals EPS-primary MBSE or a likely explicit EPS
# model thread.  The labels remain title/abstract retrieval priorities only.
add("eps-mbse-slr-2026-r0045", "core", "Explicit CubeSat/nanosatellite MBSE tool for mass, volume, power, and energy-budget calculation; likely EPS-primary model evidence.", "high")
add("eps-mbse-slr-2026-r0071", "core", "CubeSat systems-engineering simulation metadata explicitly mentions power consumption and was recovered by a direct power-component MBSE query; likely explicit EPS model thread.", "moderate")
add("eps-mbse-slr-2026-r0085", "core", "Explicit CubeSat MBSE/system-model traceability paper named for the power subsystem; direct EPS-primary/explicit-thread candidate.", "high")
add("eps-mbse-slr-2026-r0093", "core", "Nanosatellite electrical architecture is the stated focus and the record was recovered by both EPS-explicit primary queries; likely EPS-primary systems-model study despite sparse Scopus metadata.", "moderate")
add("eps-mbse-slr-2026-r0125", "core", "Direct micro/nanosatellite power-system modelling focus recovered by the functional-EPS MBSE query; likely EPS-primary model study, pending structured-model verification.", "moderate")
add("eps-mbse-slr-2026-r0021", "core", "CubeSat MBSE mission-simulation record recovered by the EPS functional query; available abstract identifies coupled resources and direct power-consumption analysis, making an explicit EPS thread likely.", "moderate")

# Supporting = plausible CubeSat/nanosatellite structured-system MBSE evidence
# for which full text is necessary to test an embedded EPS anchor/model/bridge.
add("eps-mbse-slr-2026-r0134", "supporting", "EPS-relevant CubeSat solar-cell/structural-battery mission record came from both EPS-explicit queries; sparse source metadata cannot establish a structured-model relation.", "low")
add("eps-mbse-slr-2026-r0025", "supporting", "CubeSat mission-development/concurrent-engineering context is plausible; full text must establish the nanosatellite boundary and any embedded EPS model thread.", "moderate")
add("eps-mbse-slr-2026-r0130", "supporting", "Stream-B systems-architecture record may contain a nanosatellite case and structured model; sparse source metadata requires full-text population and EPS-thread testing.", "low")
add("eps-mbse-slr-2026-r0135", "supporting", "3U CubeSat FlatSat development/test context is plausible systems evidence; retrieve to determine whether a structured model includes an EPS thread.", "low")
add("eps-mbse-slr-2026-r0132", "supporting", "Explicit CubeSat model-based systems-engineering structure/configuration-management context; an embedded EPS allocation/interface remains to be tested in full text.", "moderate")
add("eps-mbse-slr-2026-r0042", "supporting", "Student nanosatellite SysML risk-management model is structured-system MBSE; full text must test whether its risks/models include a qualifying EPS thread.", "high")
add("eps-mbse-slr-2026-r0029", "supporting", "Explicit SysML functional-architecture method for CubeSat behaviors; a system-wide model could contain an embedded EPS thread but metadata does not prove it.", "high")
add("eps-mbse-slr-2026-r0030", "supporting", "CubeSat MBSE technical-measurement study has a plausible structured-system-model context; its EPS relevance requires full-text bridge testing.", "moderate")
add("eps-mbse-slr-2026-r0103", "supporting", "CubeSat systems-architecture/test-and-evaluation context is plausible structured systems engineering; retrieve to test an embedded EPS model/V&V thread.", "moderate")
add("eps-mbse-slr-2026-r0137", "supporting", "CubeSat mission study explicitly reports an MBSE activity diagram; communication focus does not rule out an embedded system-level EPS thread at title/abstract stage.", "moderate")
add("eps-mbse-slr-2026-r0129", "supporting", "Systems-engineering satellite budgeting record is a plausible model/architecture candidate from Stream B; population and any EPS rather than data-budget thread need full text.", "low")
add("eps-mbse-slr-2026-r0018", "supporting", "Student-built CubeSat systems-engineering process may use a system model across subsystems; full text is needed to test a separable EPS thread.", "moderate")
add("eps-mbse-slr-2026-r0139", "supporting", "Nanosatellite payload integration uses a named model-based diagnostic system; retain conservatively to test whether the host-system model contains an EPS bridge.", "low")
add("eps-mbse-slr-2026-r0128", "supporting", "CubeSat MBSE/software reliability record is other-subsystem focused but has plausible system-model scope; EPS linkage cannot be ruled out from sparse metadata.", "low")
add("eps-mbse-slr-2026-r0118", "supporting", "CubeSat digital-twin implementation is a plausible structured-system context, but the title does not establish model relationships or EPS content; retain conservatively.", "low")
add("eps-mbse-slr-2026-r0070", "supporting", "Digital-engineering platform explicitly targets CubeSat mission prototyping; retrieve to determine modeled concerns and an EPS thread.", "moderate")
add("eps-mbse-slr-2026-r0005", "supporting", "CubeSat PLM/requirements-in-loop case suggests a structured lifecycle model; full text must establish EPS-specific anchors and relations.", "moderate")
add("eps-mbse-slr-2026-r0083", "supporting", "Small-satellite MBSE conceptual model for intersatellite communication is subsystem-focused but plausibly host-system modeling; test for an embedded EPS thread.", "low")
add("eps-mbse-slr-2026-r0140", "supporting", "Model-based embedded-system method is reported from a CubeSat student project; full text is needed to determine system scope and EPS linkage.", "low")
add("eps-mbse-slr-2026-r0003", "supporting", "MBSE/PLM integration has a plausible CubeSat/nanosatellite design use case under the Stream-B match; source metadata is sparse, so retain for full-text scope testing.", "low")
add("eps-mbse-slr-2026-r0036", "supporting", "CubeSat-class standardized model/template is plausible reusable structured-system evidence; retrieve to test allocation/interface treatment of EPS.", "high")
add("eps-mbse-slr-2026-r0141", "supporting", "CubeSat-swarm ADCS conceptual model is other-subsystem focused but explicitly model-based; retain conservatively for a possible system-level EPS thread.", "low")
add("eps-mbse-slr-2026-r0066", "supporting", "MBSE black-box model for a small-satellite communication system is structured but subsystem-focused; full text must test host-system EPS linkage.", "moderate")
add("eps-mbse-slr-2026-r0015", "supporting", "Model-based spacecraft-architecture design study was returned by the CubeSat/nanosatellite Stream-B query; retrieve to verify population and an EPS-relevant model thread.", "low")
add("eps-mbse-slr-2026-r0123", "supporting", "Agile-MBSE/NewSpace assessment may contain a CubeSat/nanosatellite systems-model case; sparse source metadata prevents a population or EPS-thread conclusion.", "low")
add("eps-mbse-slr-2026-r0116", "supporting", "Student CubeSat mission-proposal record was retrieved by the MBSE Stream-B query; full text is needed to confirm a structured model and EPS thread.", "low")
add("eps-mbse-slr-2026-r0064", "supporting", "Object-oriented functional-modeling study has plausible NewSpace nanosatellite systems scope under the Stream-B match; retrieve to test population and EPS relations.", "low")
add("eps-mbse-slr-2026-r0115", "supporting", "CubeSat mission record was retrieved by the MBSE Stream-B query; retain to determine whether its mission model carries an extractable EPS thread.", "low")
add("eps-mbse-slr-2026-r0120", "supporting", "Concurrent model-based CubeSat mission-design context is plausible structured-system evidence; EPS allocation/interface requires full text.", "moderate")
add("eps-mbse-slr-2026-r0144", "supporting", "CubeSat energy-modelling title is EPS-relevant and came from the functional-EPS query, but does not visibly establish a structured-system-model relation.", "low")
add("eps-mbse-slr-2026-r0145 eps-mbse-slr-2026-r0146 eps-mbse-slr-2026-r0022 eps-mbse-slr-2026-r0102 eps-mbse-slr-2026-r0026 eps-mbse-slr-2026-r0028 eps-mbse-slr-2026-r0035 eps-mbse-slr-2026-r0037", "supporting", "CubeSat System Reference Model/MBSE lineage provides plausible reusable structured-system models; full text must test whether a distinct EPS anchor, model anchor, and bridge are present.", "high")
add("eps-mbse-slr-2026-r0078", "supporting", "Nanosatellite system-modeling architecture for EIRSAT-1 is a plausible whole-system model; full text is needed for an explicit EPS thread.", "high")
add("eps-mbse-slr-2026-r0148", "supporting", "Collaborative modelling/system-thinking work explicitly targets nanosatellite developers; retain to test whether it reports a qualifying system model and EPS thread.", "low")
add("eps-mbse-slr-2026-r0098 eps-mbse-slr-2026-r0104 eps-mbse-slr-2026-r0149", "supporting", "CubeSat digital-engineering/information-exchange context is plausible structured-model and interoperability evidence; EPS-specific anchors/bridges require full text.", "moderate")
add("eps-mbse-slr-2026-r0009", "supporting", "Explicit MBSE framework for academic nanosatellite project management/design; full text must determine an extractable EPS model thread.", "moderate")
add("eps-mbse-slr-2026-r0047", "supporting", "CSRM/SysML metamodel-quality study is structured CubeSat reference-model evidence; full text must test EPS-thread content.", "high")
add("eps-mbse-slr-2026-r0082", "supporting", "27U satellite SysML/model-based space-systems study is a CubeSat-form-factor structured model; camera focus requires full-text EPS-thread testing.", "moderate")
add("eps-mbse-slr-2026-r0153", "supporting", "Nanosatellite MBSE/cybersecurity approach is structured but other-subsystem focused; retain conservatively for possible embedded EPS linkage.", "low")
add("eps-mbse-slr-2026-r0154 eps-mbse-slr-2026-r0155", "supporting", "Student/3U CubeSat development record was retrieved by Stream B; sparse metadata makes structured-model and EPS-thread status a full-text question.", "low")
add("eps-mbse-slr-2026-r0002", "supporting", "Nanospace preliminary-design study explicitly concerns CubeSats; its planning/model context could contain an embedded EPS thread.", "moderate")
add("eps-mbse-slr-2026-r0106", "supporting", "Explicit CubeSat EPS digital twin is central to retrieval, but metadata does not show a structured-system-model linkage; retain with that uncertainty for full text.", "moderate")
add("eps-mbse-slr-2026-r0157", "supporting", "Explicit use of MBSE tools to model CubeSat systems; full text must establish a qualifying EPS thread.", "moderate")
add("eps-mbse-slr-2026-r0158", "supporting", "CubeSat system-modeling/attitude-determination record is subsystem focused but plausibly includes host-system relations; EPS thread needs full text.", "low")
add("eps-mbse-slr-2026-r0126", "supporting", "End-to-end small-satellite concurrent/MBSE design study is plausible population and structured-system evidence; verify CubeSat/nanosatellite separability and EPS thread in full text.", "low")
add("eps-mbse-slr-2026-r0108", "supporting", "Explicit MBSE CubeSat development case study; retrieve to test whether BOREALIS model includes an extractable EPS thread.", "moderate")
add("eps-mbse-slr-2026-r0065", "supporting", "MBSE operational-concept model is structured but communication/multiorbit focused; retain conservatively to test a CubeSat/nanosatellite and EPS thread.", "low")
add("eps-mbse-slr-2026-r0004", "supporting", "Causal MBSE tool study explicitly models CubeSat conceptual-design data; full text must test an EPS-specific relationship.", "moderate")
add("eps-mbse-slr-2026-r0079", "supporting", "Digitally twinned 1U CubeSat is plausible system-model evidence, but metadata does not establish structured model relations or EPS content.", "low")
add("eps-mbse-slr-2026-r0086", "supporting", "MBSE/concurrent-preliminary-design CubeSat Nanospace study is structured-system evidence; retrieve for possible EPS allocation/interface thread.", "high")
add("eps-mbse-slr-2026-r0110", "supporting", "SysML structural-complexity assessment was returned by the CubeSat/nanosatellite Stream-B query; full text must verify population and EPS content.", "low")
add("eps-mbse-slr-2026-r0019", "supporting", "RAX CubeSat MBSE operational-scenarios study explicitly models coupled limited resources; retrieve to test a qualifying EPS relation.", "high")
add("eps-mbse-slr-2026-r0112", "supporting", "Docs-as-code MBSE for a named CubeSat project is plausible structured-system evidence; EPS thread requires full text.", "moderate")
add("eps-mbse-slr-2026-r0159", "supporting", "Model-based requirements/verification connection is structured systems-engineering evidence under a Stream-B population match; EPS target/bridge needs full text.", "low")
add("eps-mbse-slr-2026-r0161", "supporting", "Small-satellite MBSE lessons-learned record may report primary project/model experience; retrieve to verify CubeSat/nanosatellite scope and EPS thread.", "low")
add("eps-mbse-slr-2026-r0162", "supporting", "Explicit MBSE support for nano-satellite development; full text must establish a qualifying EPS model thread.", "moderate")
add("eps-mbse-slr-2026-r0163", "supporting", "Nanosatellite concept design explicitly uses MBSE; retrieve to determine EPS model content and bridge.", "moderate")
add("eps-mbse-slr-2026-r0107", "supporting", "Explicit MBSE data formalization for concurrent preliminary design of CubeSats; a reusable system model may include EPS, requiring full text.", "moderate")
add("eps-mbse-slr-2026-r0081", "supporting", "Integrated MBSE multi-satellite optimization is structured-model evidence under a Stream-B population match; verify target population and EPS thread in full text.", "low")
add("eps-mbse-slr-2026-r0165", "supporting", "CubeSat parametric flight-simulation architecture may be connected to a structured system model; title/metadata cannot distinguish it from standalone simulation.", "low")
add("eps-mbse-slr-2026-r0100", "supporting", "Nanosatellite engineering/lasercom case survived the structured executable-integration refinement; retrieve to test the claimed model link and any EPS thread.", "low")
add("eps-mbse-slr-2026-r0166", "supporting", "Explicit CubeSat MBSE-environment/programmatic-management record; retrieve to test system-model scope and EPS thread.", "moderate")
add("eps-mbse-slr-2026-r0167", "supporting", "Mission-analysis/design/simulation toolkit was recovered by both functional-EPS and Stream-B queries; metadata does not establish a structured-model bridge, so retain conservatively.", "low")
add("eps-mbse-slr-2026-r0011", "supporting", "Rapid model-based interdisciplinary CubeSat mission-design context is plausible whole-system modeling; EPS thread requires full text.", "moderate")
add("eps-mbse-slr-2026-r0034 eps-mbse-slr-2026-r0024", "supporting", "Team Xc concurrent mission-design work explicitly includes CubeSat/NanoSat concepts and system-modeling workflow; full text must establish EPS-specific content.", "moderate")
add("eps-mbse-slr-2026-r0095", "supporting", "CubeSat automated test/V&V record is plausible model-enabled systems evidence; full text must test an explicit EPS target and bridge.", "low")
add("eps-mbse-slr-2026-r0169", "supporting", "Digital-engineering/digital-twin lessons-learned record is a plausible system-model context under the Stream-B match; population, research type, and EPS linkage require full text.", "low")
add("eps-mbse-slr-2026-r0170", "supporting", "CubeSat resilience framework/modeling is plausible structured-system evidence; retrieve to test EPS anchoring and relations.", "low")
add("eps-mbse-slr-2026-r0090", "supporting", "Explicit MBSE early-analysis framework was returned by the CubeSat/nanosatellite Stream-B query; full text must verify population and an EPS thread.", "low")
add("eps-mbse-slr-2026-r0063", "supporting", "Power-subsystem digital-twin/simulation record is EPS-relevant, but its structured-system-model link and nanosatellite applicability are not visible; retain conservatively.", "low")
add("eps-mbse-slr-2026-r0027", "supporting", "CubeSat requirements-engineering model is structured systems evidence; full text must test EPS allocation/traceability.", "moderate")
add("eps-mbse-slr-2026-r0109", "supporting", "MBSE/open-source multi-domain simulation framework was returned by the CubeSat/nanosatellite Stream-B query; retrieve to establish target population and EPS bridge.", "low")
add("eps-mbse-slr-2026-r0007", "supporting", "MBSE-compliant CubeSat reference-model V&V record is structured-model evidence; full text must identify a direct EPS target/model/V&V bridge.", "high")
add("eps-mbse-slr-2026-r0174", "supporting", "Modular satellite-platform design was retrieved by the CubeSat/nanosatellite MBSE stream; full text must verify population, model relations, and EPS thread.", "low")

# Rejected records: a positive title/available abstract gives a clear scope,
# population, publication-type, secondary-study, or non-MBSE reason.  None is
# rejected merely because a sparse Scopus record lacks an EPS word.
add("eps-mbse-slr-2026-r0055", "rejected", "In-orbit 6G laboratory/platform study; no CubeSat/nanosatellite structured-system MBSE or EPS-model focus is visible.", "high")
add("eps-mbse-slr-2026-r0016", "rejected", "Generic satellite AIT-organization readiness/process assessment, not a CubeSat/nanosatellite structured-system model study.", "high")
add("eps-mbse-slr-2026-r0136", "rejected", "Stand-alone nanosatellite thermal/heat-management subsystem concept, without visible structured-system-model linkage.", "high")
add("eps-mbse-slr-2026-r0077", "rejected", "Stand-alone low-power communications receiver design; no structured-system MBSE link.", "high")
add("eps-mbse-slr-2026-r0043", "rejected", "Generic spacecraft verification-planning/Bayesian-network study; available metadata does not establish CubeSat/nanosatellite population.", "high")
add("eps-mbse-slr-2026-r0074", "rejected", "Solar-sail SmallSat feasibility/trajectory study, not a CubeSat/nanosatellite EPS MBSE report.", "high")
add("eps-mbse-slr-2026-r0105", "rejected", "Propulsion thermodynamic analysis, not an orbital CubeSat/nanosatellite structured-system model.", "high")
add("eps-mbse-slr-2026-r0138", "rejected", "Generic university evaluation facility record; no target nanosatellite system-model scope.", "high")
add("eps-mbse-slr-2026-r0050", "rejected", "Construction-equipment MBSE experience report; wrong population.", "high")
add("eps-mbse-slr-2026-r0122", "supporting", "CubeSat fault-detection/autonomous-recovery record was returned by a Stream-B query requiring digital-twin and systems-engineering concepts; sparse metadata warrants full-text testing rather than rejection.", "low")
add("eps-mbse-slr-2026-r0057", "rejected", "Mixed nanosatellite/micro-platform Edge-AI sensing architecture, not a separable CubeSat/nanosatellite MBSE/EPS model study.", "high")
add("eps-mbse-slr-2026-r0127", "rejected", "Sail-driven spacecraft dynamics/control simulation; wrong technical/system scope.", "high")
add("eps-mbse-slr-2026-r0084", "rejected", "Unmanned autonomous-system MBSE tool study; wrong population.", "high")
add("eps-mbse-slr-2026-r0039", "rejected", "Satellite-software/F Prime architecture study lacks a CubeSat/nanosatellite and EPS-model focus.", "moderate")
add("eps-mbse-slr-2026-r0119", "rejected", "Simulation test bench for large satellite constellations; wrong population and standalone simulation focus.", "high")
add("eps-mbse-slr-2026-r0059", "rejected", "SAR imagery analysis/payload study, not MBSE or EPS modeling.", "high")
add("eps-mbse-slr-2026-r0143", "rejected", "Laser-accelerated sailcraft performance analysis; wrong population/system scope.", "high")
add("eps-mbse-slr-2026-r0069", "rejected", "Disaster-observation multiagent/blockchain system study; no structured CubeSat/nanosatellite MBSE focus.", "high")
add("eps-mbse-slr-2026-r0033", "rejected", "Remote-sensing constellation deployment/economic analysis, not structured MBSE or EPS modeling.", "high")
add("eps-mbse-slr-2026-r0147", "rejected", "Concurrent-engineering tutorial; excluded non-primary/tutorial material.", "high")
add("eps-mbse-slr-2026-r0056", "rejected", "Stand-alone CubeSat ADCS development, without visible structured-system-model linkage.", "high")
add("eps-mbse-slr-2026-r0150 eps-mbse-slr-2026-r0012", "rejected", "Satellite-formation/albedo-analysis study; no MBSE or EPS-system-model scope.", "high")
add("eps-mbse-slr-2026-r0151", "rejected", "CubeSat debris-removal mission/application analysis; no visible structured-system model.", "moderate")
add("eps-mbse-slr-2026-r0031", "rejected", "NASA Space Launch System payload-adapter feasibility study; wrong population.", "high")
add("eps-mbse-slr-2026-r0067", "rejected", "UAV-assisted CubeSat communications energy-efficiency optimization, a network-analysis study without structured MBSE linkage.", "high")
add("eps-mbse-slr-2026-r0080", "rejected", "Cooperative CubeSat communications transmission analysis; no structured-system MBSE evidence.", "moderate")
add("eps-mbse-slr-2026-r0152", "rejected", "IoT/NetSat formation-mission implementation, not a structured-system MBSE/EPS report.", "moderate")
add("eps-mbse-slr-2026-r0094", "rejected", "Generic satellite attitude-control model; stand-alone control scope.", "high")
add("eps-mbse-slr-2026-r0156", "rejected", "CubeSat ADCS design/pre-flight test record; other-subsystem technical scope without visible structured-system model.", "high")
add("eps-mbse-slr-2026-r0072", "rejected", "Micro/nano-satellite electronic visualization platform, not an identified structured systems-engineering model.", "moderate")
add("eps-mbse-slr-2026-r0073", "rejected", "Nanosatellite sun-sensor component design/characterization; no MBSE link.", "high")
add("eps-mbse-slr-2026-r0060", "rejected", "CubeSat reaction-wheel control/testbed study; stand-alone control scope.", "high")
add("eps-mbse-slr-2026-r0014", "rejected", "Tethered-subsatellite deployment dynamics identification; non-MBSE technical analysis.", "high")
add("eps-mbse-slr-2026-r0121", "rejected", "Atmospheric optical-lensing science concept, not a structured nanosatellite system model.", "high")
add("eps-mbse-slr-2026-r0096", "rejected", "Nanosatellite antenna vibration/SAR analysis; stand-alone component analysis.", "high")
add("eps-mbse-slr-2026-r0111", "rejected", "Generic micro-satellite design/integration/flight overview; target population and structured MBSE scope are not established.", "moderate")
add("eps-mbse-slr-2026-r0160", "rejected", "CubeSat-kit education activity rather than an eligible orbital primary systems-model report.", "moderate")
add("eps-mbse-slr-2026-r0087", "rejected", "Semi-physical satellite-communications simulation platform; stand-alone simulation/component scope.", "high")
add("eps-mbse-slr-2026-r0061", "rejected", "Haptic teleoperation study; wrong population.", "high")
add("eps-mbse-slr-2026-r0051", "rejected", "CubeSat-swarm GNSS reflectometry/antenna analysis; no MBSE-system-model focus.", "high")
add("eps-mbse-slr-2026-r0041", "rejected", "Lunar Flashlight star-tracker testing; other-subsystem technical study without MBSE scope.", "high")
add("eps-mbse-slr-2026-r0062", "rejected", "Free-floating soft space-robot control study; wrong population.", "high")
add("eps-mbse-slr-2026-r0032", "rejected", "Ionospheric-aerodynamics torque prediction study; stand-alone physical analysis.", "high")
add("eps-mbse-slr-2026-r0164", "rejected", "CubeSat-constellation orbital-formation analysis, without visible structured-system MBSE link.", "moderate")
add("eps-mbse-slr-2026-r0089", "rejected", "Virtual-network-function deployment/networking study, not an orbital nanosatellite systems model.", "high")
add("eps-mbse-slr-2026-r0046", "rejected", "CubeSat swarm navigation flight-results study; no structured-system MBSE or EPS model focus.", "high")
add("eps-mbse-slr-2026-r0040", "rejected", "CubeSat software/autonomy machine-learning experiment; no structured-system MBSE/EPS link.", "high")
add("eps-mbse-slr-2026-r0052", "rejected", "Micro/nano-satellite orbit-attitude control algorithm; stand-alone control scope.", "high")
add("eps-mbse-slr-2026-r0049", "rejected", "FEMTO-satellite PCB design/development; component-level non-MBSE study.", "high")
add("eps-mbse-slr-2026-r0117", "rejected", "Satellite perception-data/payload-system record; no visible CubeSat/nanosatellite MBSE model focus.", "moderate")
add("eps-mbse-slr-2026-r0023", "rejected", "Nanosatellite RTOS/computer performance analysis; stand-alone software-component study.", "high")
add("eps-mbse-slr-2026-r0001", "rejected", "Generic 6G quantum-communication book chapter, not CubeSat/nanosatellite MBSE/EPS evidence.", "high")
add("eps-mbse-slr-2026-r0068", "rejected", "UAV/6G digital-twin networking study with a nano-satellite constellation context; not a nanosatellite EPS MBSE report.", "high")
add("eps-mbse-slr-2026-r0075", "rejected", "CubeSat payload radiation-assurance/fault-model study; no visible structured-system MBSE or EPS thread.", "moderate")
add("eps-mbse-slr-2026-r0038", "rejected", "CubeSat payload reliability/failure-mitigation study; no structured-system MBSE or EPS-model focus.", "high")
add("eps-mbse-slr-2026-r0058", "rejected", "Generic AI/ML aerospace overview, not a CubeSat/nanosatellite systems-model report.", "high")
add("eps-mbse-slr-2026-r0048", "rejected", "Space-communications metasurface technology paper; no CubeSat/nanosatellite MBSE/EPS model.", "high")
add("eps-mbse-slr-2026-r0006", "rejected", "Satellite imagery/GIS application chapter; wrong review scope.", "high")
add("eps-mbse-slr-2026-r0044", "rejected", "Satellite software-security fuzzing study; no structured-system EPS MBSE focus.", "high")
add("eps-mbse-slr-2026-r0101", "rejected", "CubeSat structure-deployment simulation; stand-alone dynamics analysis.", "high")
add("eps-mbse-slr-2026-r0114", "rejected", "Lunar radio-occultation observation simulation; wrong technical scope.", "high")
add("eps-mbse-slr-2026-r0088", "rejected", "Transistor-level radiation-effects simulation; component-level non-MBSE study.", "high")
add("eps-mbse-slr-2026-r0054", "rejected", "Generic technical-device MBSE toolkit with no visible CubeSat/nanosatellite study boundary.", "moderate")
add("eps-mbse-slr-2026-r0124", "rejected", "Sounding-balloon validation platform, not an orbital CubeSat/nanosatellite EPS MBSE report.", "high")
add("eps-mbse-slr-2026-r0168", "rejected", "Generic modular-satellite manufacturing/assembly concept, without established CubeSat/nanosatellite structured-model scope.", "moderate")
add("eps-mbse-slr-2026-r0013", "rejected", "Flexible space-debris attitude-control study; wrong population.", "high")
add("eps-mbse-slr-2026-r0097", "rejected", "Plane-wave-generator excitation-coefficient study; wrong population/system scope.", "high")
add("eps-mbse-slr-2026-r0092", "rejected", "Miniaturized laser-communication-terminal component model; no visible CubeSat/nanosatellite system-model/EPS link.", "moderate")
add("eps-mbse-slr-2026-r0076", "rejected", "Table of contents rather than a primary research report.", "high")
add("eps-mbse-slr-2026-r0113", "supporting", "Sparse Scopus metadata omit the population from the title, but the retained Stream-B query required CubeSat/nanosatellite, digital-twin, and structured-model terms; retrieve to resolve population, model scope, and EPS linkage.", "low")
add("eps-mbse-slr-2026-r0020", "rejected", "CYGNSS microsatellite flight-segment mission paper; no MBSE/EPS-model focus.", "high")
add("eps-mbse-slr-2026-r0171", "rejected", "Ground-segment protocol-services framework, not an orbital nanosatellite EPS system model.", "high")
add("eps-mbse-slr-2026-r0053", "rejected", "CubeSat thermal simulation/control framework; stand-alone subsystem simulation without visible structured-system link.", "high")
add("eps-mbse-slr-2026-r0172", "rejected", "3U CubeSat thermal-system control/model study; stand-alone thermal subsystem scope.", "high")
add("eps-mbse-slr-2026-r0099", "rejected", "NanoSat launch-platform hybrid-rocket motor study; propulsion/launch technical scope.", "high")
add("eps-mbse-slr-2026-r0091", "rejected", "Micro-satellite Earth-sensor component study; no structured-system MBSE/EPS link.", "high")
add("eps-mbse-slr-2026-r0131", "rejected", "CubeSat thermal-model validation; stand-alone thermal simulation/test study.", "high")
add("eps-mbse-slr-2026-r0173", "rejected", "Flexible-space-system motion-control study; wrong population/system scope.", "high")

# Secondary/background records are rejected from primary evidence but retained
# separately for terminology/positioning and later citation chasing.
add("eps-mbse-slr-2026-r0133", "rejected", "Secondary comparative review of CubeSat telemetry architecture; retained only for citation chasing/terminology.", "high", True)
add("eps-mbse-slr-2026-r0008", "rejected", "Secondary antenna-design review; retained only for citation chasing/terminology.", "high", True)
add("eps-mbse-slr-2026-r0142", "rejected", "Secondary comparative study/review of MBSE in space systems; retained only for citation chasing/terminology.", "high", True)
add("eps-mbse-slr-2026-r0010", "rejected", "Historical/background small-satellite chapter; retained only for citation chasing/terminology.", "high", True)
add("eps-mbse-slr-2026-r0017", "rejected", "State-of-the-art information-integration survey; retained only for citation chasing/terminology.", "high", True)


def display_title(candidate: dict[str, Any]) -> str:
    return TITLE_DISPLAY_OVERRIDES.get(candidate["report_id"], candidate.get("title", ""))


def screening_visibility(candidate: dict[str, Any]) -> dict[str, Any]:
    visible_text = " ".join((str(candidate.get("title") or ""), str(candidate.get("abstract") or "")))
    missingness = candidate.get("metadata_missingness") or {}
    return {
        "population_visible_in_saved_title_or_abstract": bool(POPULATION_RE.search(visible_text)),
        "structured_model_visible_in_saved_title_or_abstract": bool(STRUCTURED_MODEL_RE.search(visible_text)),
        "eps_visible_in_saved_title_or_abstract": bool(EPS_RE.search(visible_text)),
        "population_index_match_from_final_query": True,
        "metadata_insufficient": bool(missingness.get("abstract_missing") or missingness.get("abstract_truncated_in_any_source")),
    }


def retrieval_metadata_completeness(candidate: dict[str, Any]) -> dict[str, Any]:
    direct_identifier = bool(candidate.get("doi") or candidate.get("landing_page_urls"))
    source_identifier = bool(candidate.get("source_identifiers") or candidate.get("paperId"))
    if direct_identifier:
        status = "direct_identifier_available"
    elif source_identifier:
        status = "source_id_or_title_lookup_required"
    else:
        status = "title_year_lookup_required"
    missing = [
        name for name, present in [
            ("doi", bool(candidate.get("doi"))),
            ("landing_page_url", bool(candidate.get("landing_page_urls"))),
            ("authors", bool(candidate.get("authors"))),
            ("abstract", bool(candidate.get("abstract"))),
        ] if not present
    ]
    return {
        "status": status,
        "title_present": bool(candidate.get("title")),
        "year_present": candidate.get("year") is not None,
        "doi_present": bool(candidate.get("doi")),
        "landing_page_url_present": bool(candidate.get("landing_page_urls")),
        "source_identifier_present": source_identifier,
        "authors_present": bool(candidate.get("authors")),
        "abstract_present": bool(candidate.get("abstract")),
        "missing_fields": missing,
        "enrichment_status": "pending_before_retrieval" if not direct_identifier else "not_required_for_initial_lookup",
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def esc(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merged-candidates", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--decisions-output", type=Path, required=True)
    parser.add_argument("--screening-output", type=Path, required=True)
    parser.add_argument("--corpus-output", type=Path, required=True)
    parser.add_argument("--secondary-output", type=Path, required=True)
    args = parser.parse_args()

    with args.merged_candidates.open(encoding="utf-8") as fh:
        merged = json.load(fh)
    with args.freeze.open(encoding="utf-8") as fh:
        freeze = json.load(fh)
    candidate_hash = sha256(args.merged_candidates)
    if freeze["candidate_set"]["sha256"] != candidate_hash:
        raise RuntimeError("Merged candidate set changed after independent freeze; stop rather than screen a non-frozen set.")
    candidates = merged.get("results", [])
    candidate_ids = {candidate["report_id"] for candidate in candidates}
    decision_ids = set(DECISIONS)
    if candidate_ids != decision_ids:
        missing = sorted(candidate_ids - decision_ids)
        extraneous = sorted(decision_ids - candidate_ids)
        raise RuntimeError(f"Screening decision coverage mismatch; missing={missing}; extraneous={extraneous}")

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    outcomes: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    secondary: list[dict[str, Any]] = []
    for candidate in candidates:
        tier, rationale, confidence, is_secondary = DECISIONS[candidate["report_id"]]
        visibility = screening_visibility(candidate)
        quality_flags = ["source_title_mojibake_preserved_in_raw_provenance"] if candidate["report_id"] in TITLE_DISPLAY_OVERRIDES else []
        decision = {
            "report_id": candidate["report_id"],
            "display_title": display_title(candidate),
            "screening_tier": tier,
            "screening_rationale": rationale,
            "screening_confidence": confidence,
            "screening_basis": "title/abstract/source metadata only; no retained cache or full text was used",
            "screening_visibility": visibility,
            "metadata_quality_flags": quality_flags,
            "is_secondary_study": is_secondary,
        }
        outcomes.append(decision)
        if tier in {"core", "supporting"}:
            record = deepcopy(candidate)
            record.update({
                "screening_tier": tier,
                "screening_rationale": rationale,
                "screening_confidence": confidence,
                "rationale": rationale,
                "confidence": confidence,
                "normalized_doi": candidate.get("doi"),
                "screening_basis": decision["screening_basis"],
                "screening_visibility": visibility,
                "metadata_quality_flags": quality_flags,
                "display_title": display_title(candidate),
                "retrieval_metadata_completeness": retrieval_metadata_completeness(candidate),
                "status": "pending_full_text_eligibility",
                "full_text_eligibility_decision": None,
                "route_assignment": None,
                "route_assignment_note": "Route A/Route B and EPS anchor/model-anchor/bridge testing are deferred to full-text screening.",
                "merged_candidate_set_sha256": candidate_hash,
                "abstract_missing": candidate.get("metadata_missingness", {}).get("abstract_missing", False),
            })
            kept.append(record)
        elif is_secondary:
            record = deepcopy(candidate)
            record.update({
                "screening_tier": "rejected",
                "screening_rationale": rationale,
                "screening_confidence": confidence,
                "status": "secondary_study_for_citation_chasing_only",
                "not_primary_evidence": True,
            })
            secondary.append(record)

    outcomes.sort(key=lambda item: item["report_id"])
    kept.sort(key=lambda item: item["report_id"])
    secondary.sort(key=lambda item: item["report_id"])
    tier_counts = {tier: sum(outcome["screening_tier"] == tier for outcome in outcomes) for tier in ["core", "supporting", "rejected"]}
    if len(outcomes) != len(candidates) or len(kept) != tier_counts["core"] + tier_counts["supporting"]:
        raise RuntimeError("Screening counts do not reconcile")

    decisions_payload = {
        "review_run_id": RUN_ID,
        "generated_at": now,
        "screened_candidate_set": str(args.merged_candidates),
        "screened_candidate_set_sha256": candidate_hash,
        "screening_protocol": {
            "stage": "title/abstract/source-metadata screening for retrieval priority only",
            "route_assignment": "not performed; Route A/Route B requires full text",
            "sparse_scopus_metadata": "Empty Scopus abstracts/authors were treated as missing metadata, not negative eligibility evidence.",
            "stream_b": "EPS absence from Stream-B metadata was not an exclusion criterion; clear wrong population, secondary/non-primary type, or visible standalone/component/control/simulation scope was required for rejection.",
            "access": "Open-access status was not used as a scientific screening criterion.",
        },
        "counts": {**tier_counts, "kept": len(kept), "secondary_studies": len(secondary), "excluded_total": tier_counts["rejected"]},
        "decisions": outcomes,
    }
    args.decisions_output.parent.mkdir(parents=True, exist_ok=True)
    with args.decisions_output.open("w", encoding="utf-8") as fh:
        json.dump(decisions_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    corpus_payload = {
        "review_run_id": RUN_ID,
        "generated_at": now,
        "source_candidate_set": str(args.merged_candidates),
        "source_candidate_set_sha256": candidate_hash,
        "scope": "Title/abstract-screened retrieval corpus only; no PDF retrieval, full-text eligibility, evidence extraction, or final Route A/B decision has been performed.",
        "screening_summary": {**tier_counts, "kept": len(kept), "status": "pending_full_text_eligibility"},
        "results": kept,
    }
    args.corpus_output.parent.mkdir(parents=True, exist_ok=True)
    with args.corpus_output.open("w", encoding="utf-8") as fh:
        json.dump(corpus_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    secondary_payload = {
        "review_run_id": RUN_ID,
        "generated_at": now,
        "source_candidate_set": str(args.merged_candidates),
        "source_candidate_set_sha256": candidate_hash,
        "scope": "Secondary/background records retained for terminology, positioning, and later protocol-required citation chasing; not primary-evidence corpus records.",
        "count": len(secondary),
        "citation_chasing_status": "deferred until full-text inclusion stage",
        "results": secondary,
    }
    args.secondary_output.parent.mkdir(parents=True, exist_ok=True)
    with args.secondary_output.open("w", encoding="utf-8") as fh:
        json.dump(secondary_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    by_id = {candidate["report_id"]: candidate for candidate in candidates}
    lines = [
        "# Screening Log",
        "",
        f"Review run: `{RUN_ID}`",
        f"Screened source: `searches/merged_candidates.json` (SHA-256 `{candidate_hash}`)",
        f"Candidates after independent merge/dedup: {len(candidates)}",
        f"Kept in retrieval corpus: {len(kept)} ({tier_counts['core']} core; {tier_counts['supporting']} supporting)",
        f"Excluded from primary retrieval corpus: {tier_counts['rejected']} (including {len(secondary)} secondary/background records retained separately in `searches/secondary-studies.json`)",
        "",
        "## Screening rule actually applied",
        "- Title/abstract/source-metadata screening prioritized retrieval only; it did not determine final eligibility or assign Route A/Route B.",
        "- `core` means metadata clearly signals EPS-primary MBSE or a likely explicit EPS model thread. `supporting` means CubeSat/nanosatellite structured-system MBSE is plausible but full text must test an embedded EPS anchor, model anchor, and explicit bridge.",
        "- Empty Scopus abstracts/authors were treated as missing metadata, not as evidence against relevance. Stream-B candidates were not rejected merely because EPS is absent from title/abstract metadata.",
        "- Records were rejected only when title/available abstract clearly showed wrong population/date/type, a secondary/background role, or a standalone component/control/simulation/digital-twin scope without visible structured-system-model linkage. Access/OA was not considered.",
        "- Generic whole-spacecraft MBSE remains only provisional at this stage: a qualifying EPS thread is a full-text test, not inferred from report-level co-occurrence.",
        "",
        "## Core papers",
        "| Decision | Year | Title | Why core | Confidence |",
        "|---|---:|---|---|---|",
    ]
    for outcome in sorted((outcome for outcome in outcomes if outcome["screening_tier"] == "core"), key=lambda item: (by_id[item["report_id"]].get("year") or 0, by_id[item["report_id"]]["title"].lower())):
        candidate = by_id[outcome["report_id"]]
        lines.append(f"| {outcome['report_id']} | {candidate.get('year') or ''} | {esc(outcome['display_title'])} | {esc(outcome['screening_rationale'])} | {outcome['screening_confidence']} |")
    lines += ["", "## Supporting papers", "| Decision | Year | Title | Why supporting | Confidence |", "|---|---:|---|---|---|"]
    for outcome in sorted((outcome for outcome in outcomes if outcome["screening_tier"] == "supporting"), key=lambda item: (by_id[item["report_id"]].get("year") or 0, by_id[item["report_id"]]["title"].lower())):
        candidate = by_id[outcome["report_id"]]
        lines.append(f"| {outcome['report_id']} | {candidate.get('year') or ''} | {esc(outcome['display_title'])} | {esc(outcome['screening_rationale'])} | {outcome['screening_confidence']} |")
    lines += ["", "## Rejected papers", "| Decision | Year | Title | Why rejected | Confidence |", "|---|---:|---|---|---|"]
    for outcome in sorted((outcome for outcome in outcomes if outcome["screening_tier"] == "rejected"), key=lambda item: (by_id[item["report_id"]].get("year") or 0, by_id[item["report_id"]]["title"].lower())):
        candidate = by_id[outcome["report_id"]]
        marker = "secondary; " if outcome["is_secondary_study"] else ""
        lines.append(f"| {outcome['report_id']} | {candidate.get('year') or ''} | {esc(outcome['display_title'])} | {marker}{esc(outcome['screening_rationale'])} | {outcome['screening_confidence']} |")
    lines += [
        "",
        "## Screening confidence and corpus quality reflection",
        "- Confidence is necessarily limited for Scopus-only records because this source returned blank abstracts/authors. Those blanks increased provisional/supporting decisions rather than causing exclusion.",
        "- The kept set deliberately preserves broad Stream-B recall. Full-text assessment must verify target population, scholarly primary-report type, structured system model, and—especially for every retained record—the EPS anchor, model anchor, and explicit bridge.",
        "- Direct EPS/model language is concentrated in the core tier, but core is not final eligibility. Stand-alone digital-twin, simulation, and other-subsystem records retained as supporting have their uncertainty stated and must be tested before evidence extraction.",
        "- Citation chasing is explicitly deferred. Secondary/background records are not in `corpus.json` and can support later terminology/seed work only after the protocol-defined full-text stage.",
        "",
    ]
    args.screening_output.parent.mkdir(parents=True, exist_ok=True)
    args.screening_output.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "status": "success", "candidates": len(candidates), "core": tier_counts["core"],
        "supporting": tier_counts["supporting"], "rejected": tier_counts["rejected"],
        "secondary": len(secondary), "corpus": len(kept),
    }, indent=2))


if __name__ == "__main__":
    main()
