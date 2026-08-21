"""Render a source-aware knowledge graph for the nine CUBICS 2022 awards.

Run from this directory (or from the repository root):
    ../canada_nanosatellites/.venv/bin/python cubics_2022_graph.py

The generated HTML is self-contained. Double-click a node or edge to open its
source; the dossier below the graph provides a compact, source-linked view of
every requested field.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re
import unicodedata
from typing import Iterable

from pyvis.network import Network

from ontology import (
    Alias,
    Carries,
    CollaboratesWith,
    Collaborator,
    CubeSat,
    Edge,
    EvidenceGap,
    Facility,
    GrantRecipient,
    HasObjective,
    Leads,
    Node,
    NotPubliclyDocumented,
    Objective,
    Partner,
    PartnersWith,
    Payload,
    PossiblySameAs,
    RelationRecord,
    RenamedTo,
    UsesFacility,
)


# ---------------------------------------------------------------------------
# Dataset metadata and provenance primitives

DATASET_TITLE = "CUBICS 2022 CubeSat grants"
ASSESSMENT_DATE = "2026-08-15"


@dataclass(frozen=True)
class Source:
    """A directly visitable source used for an assertion in the graph."""

    label: str
    url: str


@dataclass(frozen=True)
class Fact:
    """An evidence-backed project fact or an explicit public-evidence gap."""

    label: str
    detail: str
    sources: tuple[Source, ...]
    gap: bool = False

    @property
    def primary_source(self) -> Source:
        return self.sources[0]


def fact(
    label: str,
    detail: str,
    *sources: Source,
    gap: bool = False,
) -> Fact:
    if not sources:
        raise ValueError(f"Fact {label!r} requires at least one source.")
    return Fact(
        label=label,
        detail=detail,
        sources=tuple(sources),
        gap=gap,
    )


@dataclass(frozen=True)
class Project:
    """One official CUBICS 2022 award and the facts represented in the graph."""

    id: str
    recipient_label: str
    recipient_title: str
    recipient_source: Source
    grant_value: str
    name: str
    title: str
    source: Source
    objectives: tuple[Fact, ...]
    payloads: tuple[Fact, ...]
    status: Fact
    collaborators: tuple[Fact, ...]
    partners: tuple[Fact, ...]
    facilities: tuple[Fact, ...]
    milestone_note: Fact
    aliases: tuple[Fact, ...] = ()
    possible_aliases: tuple[Fact, ...] = ()


CSA_CUBICS = Source(
    "CSA — About CUBICS (modified 2025-04-22)",
    "https://www.asc-csa.gc.ca/eng/satellites/cubics/about.asp",
)
CSA_MARMOT_LAUNCH = Source(
    "CSA — MARMOTSat launch announcement (2026-07-07)",
    "https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-07-07-marmotsat-takes-flight-university-of-victoria-cubesat-launched-into-space.asp",
)
CSA_2023_SELECTION = Source(
    "CSA — 2023 selection announcement (historic names)",
    "https://www.canada.ca/en/space-agency/news/2023/06/another-round-of-canadian-student-teams-selected-to-build-and-launch-their-own-satellites.html",
)
EXOLAUNCH_CUBICS = Source(
    "Exolaunch — CUBICS launch-services agreement (2025-03)",
    "https://www.exolaunch.com/news_124.html",
)
SPACEQ_CUBICS_STATUS = Source(
    "SpaceQ — CUBICS 2022 launch-status table (2026-08-05)",
    "https://spaceq.ca/the-canadian-space-agency-opens-2-4-million-cubics-2026-opportunity-for-university-cubesat-projects/",
)

EXALTA = Source("AlbertaSat — Ex-Alta 3", "https://albertasat.ca/ex-alta-3/")
EXALTA_FACILITIES = Source(
    "AlbertaSat — Facilities", "https://albertasat.ca/facilities/"
)
SC_FREYR = Source(
    "Space Concordia — Spacecraft division / SC-FREYR",
    "https://spaceconcordia.ca/spacecraft",
)
SC_CONCORDIA_NEWS = Source(
    "Concordia — SC-FREYR / AstroYeast partnership (2023-08-02)",
    "https://www.concordia.ca/cunews/main/stories/2023/08/02/canadian-space-agency-awards-350k-to-concordia-team-to-construct-and-launch-its-second-satellite.html",
)
SC_CDR_POST = Source(
    "Space Concordia — SC-FREYR CDR post (2025-05-08)",
    "https://www.instagram.com/p/DJatKABMFpo/",
)
SC_2024_POST = Source(
    "Space Concordia — SC-FREYR payload / collaborator post (2024-09-24)",
    "https://www.instagram.com/p/DAUoUjMutho/",
)
MANTIS = Source(
    "Dalhousie Space Systems Lab — M.A.N.T.I.S. mission",
    "https://dsslabs.ca/?page_id=1313",
)
MANTIS_COMMS = Source(
    "Dalhousie Space Systems Lab — communications / ground station",
    "https://dsslabs.ca/?p=1406",
)
MANTIS_AMATEUR = Source(
    "Dalhousie Space Systems Lab — amateur radio", "https://dsslabs.ca/?p=1364"
)
MANTIS_DAL_NEWS = Source(
    "Dalhousie — MANTIS / MDA sponsorship (2023-09-15)",
    "https://www.dal.ca/news/2023/09/15/dalhousie-satellite-mantis-space.html",
)
MANTIS_IARU = Source(
    "IARU satellite-frequency filing — MANTIS (2026-08-13)",
    "https://iaru.amsat-uk.org/formal_detail.php?serialnum=1115",
)
ARCTICSAT = Source(
    "University of Manitoba StarLabSat — ArcticSat",
    "https://sites.google.com/view/umstarlabsats/arcticsat",
)
ARCTICSAT_AIT = Source(
    "University of Manitoba StarLabSat — AIT facility and GSE",
    "https://sites.google.com/view/umstarlabsats/subsystems/ait/ait-facility-and-gse",
)
ARCTICSAT_GROUND = Source(
    "University of Manitoba StarLabSat — ArcticSat ground station",
    "https://sites.google.com/view/umstarlabsats/arcticsat/subsystems/ground-station",
)
ARCTICSAT_PAPER = Source(
    "Small Satellite Conference 2024 — ArcticSat presentation",
    "https://digitalcommons.usu.edu/cgi/viewcontent.cgi?filename=0&article=5972&context=smallsat&type=additional",
)
ARCTICSAT_STARLAB = Source(
    "University of Manitoba STARLab — current satellite missions",
    "https://umstarlab.ca/index.php/2025/06/08/satellite-missions/",
)
ARCTICSAT_STRUCTURE = Source(
    "University of Manitoba StarLabSat — ArcticSat structure / test work",
    "https://sites.google.com/view/umstarlabsats/arcticsat/subsystems/structure",
)
MSTRI_PRESET = Source("McMaster MSTRI — PRESET", "https://mstri.ca/preset")
MSTRI_CDR = Source(
    "McMaster MSTRI — PRESET critical-design-review recap (2025-07-15)",
    "https://mstri.ca/updates/critical-design-review-recap",
)
MSTRI_TRACKING = Source(
    "McMaster MSTRI — PRESET verification / FlatSat update (2026-07-06)",
    "https://mstri.ca/updates/keepingtabsonthesatellite",
)
PRESET_IARU = Source(
    "IARU satellite-frequency filing — PRESET (updated 2026-02-02)",
    "https://iaru.amsat-uk.org/formal_detail.php?serialnum=1074",
)
PRESET_HASP = Source(
    "McMaster NEUDOSE — PRESET HASP test campaign",
    "https://mcmasterneudose.ca/updates/2025/1/7/hasp-summer-2024",
)
PRESET_GROUND = Source(
    "MSTRI — amateur radio / PRESET ground operations",
    "https://mstri.ca/amateur-radio-overview",
)
MUNSTAR_ARCHIVE = Source(
    "MUNStar-1 project site (archived 2024-05-09)",
    "https://web.archive.org/web/20240509100234/https://munstar-1.com/",
)
MUNSTAR_RADIO_ARCHIVE = Source(
    "MUNStar-1 amateur-radio page (archived 2024-09-14)",
    "https://web.archive.org/web/20240914213504/https://munstar-1.com/radio/",
)
MUNSTAR_CCORE = Source(
    "C-CORE — Killick-2 / MUNStar-1 announcement (2023-06-13)",
    "https://c-core.ca/2023/06/13/c-core-and-mun-engineering-students-to-build-launch-and-operate-second-satellite/",
)
MUNSTAR_SPACEOPS = Source(
    "SpaceOps 2025 paper — MUNStar-1",
    "https://publications.spaceops.org/2025/download_by_id.php?id=0556",
)
MUNSTAR_GOV = Source(
    "Government of Newfoundland and Labrador — MUNStar-1 support",
    "https://www.gov.nl.ca/releases/2024/iet-en/1114n02/",
)
RADSAT_ARCHIVE = Source(
    "SkCubeSat RADSAT-SK2 page (archived 2024-01-10)",
    "https://web.archive.org/web/20240110100951/https://skcubesat.ca/radsat-sk2/",
)
RADSAT_FACILITIES_ARCHIVE = Source(
    "SkCubeSat facilities page (archived 2024-12-09)",
    "https://web.archive.org/web/20241209071424/https://www.skcubesat.ca/facilities",
)
RADSAT_IARU = Source(
    "IARU satellite-frequency filing — RADSAT-SK2",
    "https://iaru.amsat-uk.org/formal_detail.php?serialnum=1061",
)
RADSAT_PCBAWAY = Source(
    "PCBWay — RADSAT-SK2 project description",
    "https://www.pcbway.com/project/sponsor/Radsat_Sk_2_Cubesat_project_13255846.html",
)
RADSAT_USASK = Source(
    "USask — RADSAT-SK2 development update (2024)",
    "https://news.usask.ca/articles/students/2024/new-usask-graduate-set-out-to-do-the-impossible.php",
)
UVIC_CDR = Source(
    "University of Victoria — CUBICS CDR week (2025-06-19)",
    "https://www.uvic.ca/research-innovation/office-vpri/announcements/19june25-cubesat.php",
)
CSA_COHORT_CDR = Source(
    "CSA — CUBICS cohort CDR cycle (2025-07-18)",
    "https://www.linkedin.com/posts/agence-spatiale-canadienne_cubics-activity-7352031994748338176-oykT",
)
WESTERN_ARCHIVE = Source(
    "Western Skylark page (archived 2025-02-20)",
    "https://web.archive.org/web/20250220150409/https://space.uwo.ca/research/Missions%20and%20Instruments/Skylark.html",
)
WESTERN_IARU = Source(
    "IARU satellite-frequency filing — Western Skylark (updated 2026-07-05)",
    "https://iaru.amsat-uk.org/formal_detail.php?serialnum=1108",
)
WESTERN_THESIS = Source(
    "Western thesis — Skylark launch-vibration and thermal modelling (2025)",
    "https://uwo.scholaris.ca/items/e87895f1-0c64-4d76-b796-9032a82349ef",
)
WESTERN_MISSION_CONTROL = Source(
    "Western Space — Mission Control Facility",
    "https://space.uwo.ca/research/mission_control/index.html",
)
MARMOTSAT = Source("MARMOTSat project site", "https://www.marmotsat.ca/")
MARMOT_UVIC = Source(
    "UVic News — MARMOTSat mission and pre-launch integration (2026-07-02)",
    "https://news.uvic.ca/2026/uvic-satellite-to-probe-climate-open-source-radio/",
)
MARMOT_RADIO = Source(
    "UVic Propagation Laboratory — MARMOTSat amateur-radio payload",
    "https://www.propagationlab.ca/satellite/",
)
MARMOT_CDR = Source(
    "MARMOTSat — critical design review update (2025-06-30)",
    "https://www.marmotsat.ca/updates/critical-design-review",
)
MARMOT_TRR = Source(
    "MARMOTSat — test readiness review update (2026-03-03)",
    "https://www.marmotsat.ca/updates/marmotsat-test-readiness-review",
)
MARMOT_VIBRATION = Source(
    "MARMOTSat — CSA Longueuil vibration testing",
    "https://www.marmotsat.ca/updates/flight-spacecraft-vibration-testing",
)
MARMOT_TRIUMF = Source(
    "MARMOTSat — TRIUMF proton-irradiation testing",
    "https://www.marmotsat.ca/updates/proton-irradiation-testing-at-triumf",
)
MARMOT_INTEGRATION = Source(
    "MARMOTSat — CSA cleanroom / Exolaunch deployer integration",
    "https://www.marmotsat.ca/updates/flight-spacecraft-deployer-integration",
)
MARMOT_RENAME = Source(
    "SpaceQ — historic SKYA'ANAsat / MARMOTSat name note",
    "https://spaceq.ca/the-csa-is-looking-for-a-launch-service-provider/",
)


# ---------------------------------------------------------------------------
# The official roster comes from CSA_CUBICS.  Project pages add technical and
# status detail.  Evidence gaps are intentionally represented as facts: absence
# from the reviewed public record is not silently converted into a guess.

PROJECTS = (
    Project(
        id="exalta3",
        recipient_label="University of Alberta\n(AlbertaSat)",
        recipient_title="Official CUBICS grant recipient\nUniversity of Alberta / AlbertaSat\nGrant: CAD 348,700",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 348,700",
        name="Ex-Alta 3",
        title="Experimental Albertan #3\n3U-class CubeSat · 4.613 kg stated\nOfficial CUBICS project: Measuring ice and snow coverage",
        source=EXALTA,
        objectives=(
            fact(
                "Ice, snow and glacier characterization",
                "Use AlbertaSat's open-source student-designed imager to characterize Canadian ice, snow and glacial regions.",
                EXALTA,
            ),
            fact(
                "Ionospheric magnetic-field characterization",
                "Characterize DC and AC magnetic fields at low-Earth-orbit altitudes with a digital fluxgate magnetometer.",
                EXALTA,
            ),
            fact(
                "Student HQP and open-source development",
                "Train students to design, build and operate a satellite while supporting open-source designs.",
                EXALTA,
            ),
            fact(
                "Amateur-radio communications training",
                "Give students end-to-end amateur-radio satellite-communications experience.",
                EXALTA,
            ),
        ),
        payloads=(
            fact(
                "IRIS multispectral imager",
                "In-house 1U payload with VNIR and SWIR optical paths for ice and snow coverage measurements.",
                EXALTA,
            ),
            fact(
                "Digital Fluxgate Magnetometer (DFGM)",
                "University of Alberta Space Physics Lab instrument on a 60 cm deployable boom for ionospheric magnetic-field measurements.",
                EXALTA,
            ),
            fact(
                "Corner-cube retroreflector array",
                "Nadir-face reflector array for laser ranging, complementary magnetic-field context and altitude-decay characterization.",
                EXALTA,
            ),
        ),
        status=fact(
            "Planned — TBA (candidate Q4 2026)",
            "AlbertaSat's page still lists a 2026 Exolaunch/Falcon 9 plan. A later 2026-08-05 launch-status report says Ex-Alta 3 did not make Transporter-17 and is only a candidate for Transporter-18 in Q4 2026; no individual manifest assignment or launch confirmation is public.",
            SPACEQ_CUBICS_STATUS,
            EXALTA,
        ),
        collaborators=(
            fact(
                "University of Alberta Space Physics Lab",
                "Developed the DFGM payload described on the Ex-Alta 3 project page.",
                EXALTA,
            ),
            fact(
                "Northern Alberta Radio Club (NARC)",
                "Partners with AlbertaSat in amateur-radio operator training and the S-band ground-station effort.",
                EXALTA,
                EXALTA_FACILITIES,
            ),
        ),
        partners=(
            fact(
                "Exolaunch — CUBICS launch services",
                "AlbertaSat lists Exolaunch and Falcon 9 in its mission overview. Separately, Exolaunch announced a CSA agreement to facilitate launch of all nine CUBICS CubeSats, including CSA-Quebec integration and EXOpod Nova deployment; neither source confirms Ex-Alta 3's individual flight assignment.",
                EXALTA,
                EXOLAUNCH_CUBICS,
            ),
        ),
        facilities=(
            fact(
                "AlbertaSat Project Room / FlatSat",
                "University of Alberta Faculty of Engineering lab with a FlatSat for interface and electrical/software connection testing before mechanical assembly.",
                EXALTA_FACILITIES,
            ),
            fact(
                "VA6 UAB UHF/VHF ground station",
                "ECERF-roof station with UHF/VHF uplink and downlink capability.",
                EXALTA_FACILITIES,
            ),
            fact(
                "VE6 LRN S-band ground station",
                "NARC-site downlink station intended to continue receiving Ex-Alta 3-generation IRIS image files.",
                EXALTA_FACILITIES,
            ),
            fact(
                "ISO 8 cleanroom",
                "AlbertaSat spacecraft-assembly space with benches, laminar-flow table and TVAC.",
                EXALTA_FACILITIES,
            ),
            fact(
                "Thermal-vacuum chamber and shaker table",
                "TVAC supports approximately −40 to +70 °C and 10e-5 torr; the uniaxial shaker supports component vibration tests such as IRIS.",
                EXALTA_FACILITIES,
            ),
        ),
        milestone_note=fact(
            "CDR participation recorded; no NASA phase named",
            "University of Alberta was among the teams in the June 2025 CDR week. Its public sources also describe planned launch services and integration/test facilities, but none assigns Ex-Alta 3 a NASA lifecycle phase.",
            UVIC_CDR,
            EXALTA,
            EXALTA_FACILITIES,
        ),
    ),
    Project(
        id="sc_freyr",
        recipient_label="Concordia University\n(Space Concordia)",
        recipient_title="Official CUBICS grant recipient\nConcordia University / Space Concordia\nGrant: CAD 350,000",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 350,000",
        name="SC-FREYR",
        title="Space Concordia's second CUBICS CubeSat\nOfficial CUBICS project: AI image processing and CubeSat robustness",
        source=SC_FREYR,
        objectives=(
            fact(
                "On-board AI image processing",
                "Capture RGB Earth images and process them aboard the spacecraft to reduce the need to downlink large raw files.",
                SC_FREYR,
            ),
            fact(
                "Yeast-growth study in space",
                "Study new yeast strains under microgravity and the hazardous space environment to inform possible space-food approaches.",
                SC_FREYR,
            ),
            fact(
                "Student development",
                "Develop student skills and knowledge for the space sector through a technically challenging mission.",
                SC_FREYR,
            ),
        ),
        payloads=(
            fact(
                "RGB imager and on-board AI processing",
                "The public team page confirms RGB Earth imaging and onboard processing; the detailed RGB sensor/AI implementation was not specified there.",
                SC_FREYR,
            ),
            fact(
                "Yeast-growth microfluidics card",
                "Space Concordia’s project page confirms the yeast-growth objective. Concordia’s SC-FREYR announcement identifies AstroYeast Microfarm’s microfluidics framework for nutrient-producing yeast, corroborating the user-supplied microfluidics-card detail.",
                SC_CONCORDIA_NEWS,
                SC_FREYR,
            ),
        ),
        status=fact(
            "Planned — TBA",
            "Space Concordia describes SC-FREYR as actively being designed and developed. Its page calls Nanoracks the launch provider, whereas the CSA/Exolaunch program agreement covers all nine CUBICS CubeSats; SpaceQ’s 2026-08-05 current status table lists SC-FREYR TBA. The supplied expected-2026 Exolaunch note is preserved as a discrepancy, not a confirmed flight.",
            SPACEQ_CUBICS_STATUS,
            SC_FREYR,
            EXOLAUNCH_CUBICS,
        ),
        collaborators=(
            fact(
                "Zetane Systems",
                "A September 2024 Space Concordia post identifies Zetane Systems and AstroYeast as collaborators on SC-FREYR; the current project page also displays Zetane in its collaborators area. Neither source specifies Zetane’s technical role, so no AI/data-processing role is asserted.",
                SC_2024_POST,
                SC_FREYR,
            ),
            fact(
                "AstroYeast Microfarm",
                "Concordia’s SC-FREYR announcement identifies AstroYeast Microfarm’s microfluidics framework for nutrient-producing yeast, corroborating the supplied collaborator note.",
                SC_CONCORDIA_NEWS,
            ),
            fact(
                "Concordia, University of Windsor and Toronto Metropolitan University researchers",
                "Concordia’s SC-FREYR announcement names academic collaborators from these institutions in the project’s research team.",
                SC_CONCORDIA_NEWS,
            ),
        ),
        partners=(
            fact(
                "Nanoracks",
                "Space Concordia's spacecraft page describes Nanoracks as its launch provider. Treat this as a published team-page claim, not a launch confirmation.",
                SC_FREYR,
            ),
            fact(
                "Exolaunch — CUBICS launch services",
                "Exolaunch announced a CSA agreement to facilitate launch of all nine CUBICS CubeSats. This program-level arrangement conflicts with the older Nanoracks statement on the team page and does not itself identify SC-FREYR’s individual flight.",
                EXOLAUNCH_CUBICS,
                SC_FREYR,
            ),
        ),
        facilities=(
            fact(
                "No named project test/operations facility publicly identified",
                "The reviewed public sources do not identify a dedicated SC-FREYR cleanroom, TVAC, vibration facility or operational ground station.",
                SC_FREYR,
                SC_CONCORDIA_NEWS,
                gap=True,
            ),
        ),
        milestone_note=fact(
            "CDR recorded on 2025-05-06; no NASA phase named",
            "Space Concordia reports its CDR to CSA occurred on 2025-05-06 and that it was preparing for TRR. This corrects the user-supplied September 2024 CDR date, which is not corroborated by the reviewed public record; neither cited source assigns SC-FREYR a NASA lifecycle phase.",
            SC_CDR_POST,
            SC_FREYR,
        ),
    ),
    Project(
        id="mantis",
        recipient_label="Dalhousie University\n(DSS Labs)",
        recipient_title="Official CUBICS grant recipient\nDalhousie University / Dalhousie Space Systems Lab\nGrant: CAD 349,740",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 349,740",
        name="M.A.N.T.I.S.",
        title="Multispectral Autonomous Natural Transformation Imaging Satellite\nOfficial award title: STEM engagement through satellite development and observations",
        source=MANTIS,
        objectives=(
            fact(
                "Autonomous environmental Earth observation",
                "Combine multispectral imaging, onboard AI and real-time decision-making to identify significant environmental changes and prioritize valuable downlinks.",
                MANTIS,
            ),
            fact(
                "Climate-related phenomena / harmful algal blooms",
                "The amateur-radio mission page identifies climate-related phenomena, initially harmful algal blooms, as the primary science focus.",
                MANTIS_AMATEUR,
            ),
            fact(
                "Student spacecraft-engineering training",
                "Use an end-to-end student mission to develop systems-engineering and autonomous-spacecraft expertise.",
                MANTIS,
            ),
        ),
        payloads=(
            fact(
                "Multispectral camera and edge-computing AI payload",
                "DSS describes imaging sensors and onboard AI that analyze observations in flight and prioritize downlink data. Dalhousie and the current IARU filing identify a multispectral camera plus edge-computing processors for imagery including harmful/toxic algal-bloom detection; no camera model is published.",
                MANTIS,
                MANTIS_DAL_NEWS,
                MANTIS_IARU,
            ),
        ),
        status=fact(
            "Planned — team target Q3 2027",
            "The IARU filing updated 2026-08-13 says the team is planning a CSA/Exolaunch SpaceX launch to 510 km SSO in Q3 2027. SpaceQ's 2026-08-05 program table still lists the mission TBA; the target is therefore modeled as a plan, not a confirmed manifest.",
            MANTIS_IARU,
            SPACEQ_CUBICS_STATUS,
        ),
        collaborators=(
            fact(
                "Nova Scotia amateur-radio clubs",
                "DSS says it works alongside local amateur-radio clubs for licensing, technical training, mentorship and community engagement.",
                MANTIS_COMMS,
            ),
            fact(
                "Alphonse Penney",
                "DSS credits Penney with amateur-radio guidance and connections with local clubs during the licensing process.",
                MANTIS,
            ),
        ),
        partners=(
            fact(
                "Radio Amateurs of Canada (RAC)",
                "DSS identifies RAC agreements and endorsement activity as part of its amateur-radio commitments.",
                MANTIS_AMATEUR,
                MANTIS,
            ),
            fact(
                "International Amateur Radio Union (IARU)",
                "DSS identifies IARU frequency coordination/licensing as part of the communications path.",
                MANTIS_COMMS,
            ),
            fact(
                "EnduroSat",
                "DSS identifies an EnduroSat UHF Transceiver II as the selected onboard communications unit; this is a component-supplier relation, not evidence of a broader mission partnership.",
                MANTIS_COMMS,
            ),
            fact(
                "MDA",
                "Dalhousie reports MDA provided a three-year sponsorship of tools, equipment and expertise for MANTIS.",
                MANTIS_DAL_NEWS,
            ),
            fact(
                "Exolaunch — planned launch services",
                "The team’s current IARU filing says it is planning a CSA launch via Exolaunch. The broader Exolaunch agreement covers the nine CUBICS CubeSats but does not confirm a specific flight.",
                MANTIS_IARU,
                EXOLAUNCH_CUBICS,
            ),
        ),
        facilities=(
            fact(
                "DSS ground-station setup at Dalhousie",
                "DSS documents a ground-station architecture using an Ettus USRP B210 SDR and associated RF chain; the team describes the antenna as planned atop Dalhousie’s tallest building, so this is a developing operations facility rather than a completed environmental-test facility.",
                MANTIS_COMMS,
                MANTIS_IARU,
            ),
            fact(
                "No named environmental test facility publicly identified",
                "The reviewed mission and communications pages publish FlatSat maturity and ground-station detail but do not name a MANTIS TVAC, cleanroom or vibration facility.",
                MANTIS,
                MANTIS_COMMS,
                gap=True,
            ),
        ),
        milestone_note=fact(
            "Cohort CDR completion recorded; no NASA phase named",
            "CSA reports MANTIS completed the cohort CDR cycle. DSS describes ongoing subsystem/FlatSat development and the current filing plans a Q3 2027 launch, but the reviewed public sources do not assign MANTIS a NASA lifecycle phase.",
            CSA_COHORT_CDR,
            MANTIS,
            MANTIS_IARU,
        ),
    ),
    Project(
        id="arcticsat",
        recipient_label="University of Manitoba\n(StarLabSat)",
        recipient_title="Official CUBICS grant recipient\nUniversity of Manitoba / StarLabSat\nGrant: CAD 349,992",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 349,992",
        name="ArcticSat",
        title="3U CubeSat\nOfficial CUBICS project: Making space accessible for Arctic climate-change research",
        source=ARCTICSAT,
        objectives=(
            fact(
                "Canadian Arctic sea-ice measurement",
                "Scan northern Canada to determine sea-ice coverage, supporting climate-change understanding and timely ice-safety information.",
                ARCTICSAT,
            ),
            fact(
                "Community-accessible Arctic information",
                "Co-develop the mission with the Chesterfield Inlet community and support local Indigenous and Inuit communities with ice-safety information and satellite access.",
                ARCTICSAT,
                ARCTICSAT_GROUND,
            ),
        ),
        payloads=(
            fact(
                "Passive-microwave radiometer / deployable antenna (terminology conflict)",
                "The conference presentation describes an 18.7 GHz passive-microwave radiometer with a deployable cylindrical-reflector antenna that measures Earth-surface brightness temperature for the sea-ice mission. The engineering page calls it a large deployable radiometer antenna, while STARLab uses “radar antenna” shorthand.",
                ARCTICSAT_PAPER,
                ARCTICSAT,
                ARCTICSAT_STARLAB,
            ),
        ),
        status=fact(
            "Planned — TBA",
            "The engineering page lists MCR (2023-10-27), PDR (2024-05-22) and CDR (2025-05-02) under “Future Review Dates,” with TRR/FRR TBD; it is schedule evidence, not proof those reviews passed. SpaceQ's 2026-08-05 status table lists ArcticSat TBA, with no provider, rocket or launch date publicly announced.",
            SPACEQ_CUBICS_STATUS,
            ARCTICSAT,
        ),
        collaborators=(
            fact(
                "Dr. Dustin Isleifson and Dr. Dorthe Dahl-Jensen",
                "University of Manitoba collaborators named on the ArcticSat project page.",
                ARCTICSAT,
            ),
            fact(
                "Dr. John Yackel (University of Calgary)",
                "Named science collaborator on the ArcticSat project page.",
                ARCTICSAT,
            ),
            fact(
                "Chesterfield Inlet, Nunavut community",
                "Named project collaborator; the ground-station requirements emphasize co-development and community satellite control/data access.",
                ARCTICSAT,
                ARCTICSAT_GROUND,
            ),
            fact(
                "SIKU data-sharing network",
                "ArcticSat’s ground-station requirements call for automatic dissemination of payload data to the SIKU network.",
                ARCTICSAT_GROUND,
            ),
        ),
        partners=(
            fact(
                "Magellan Aerospace", 
                "Named returning collaborator; its Winnipeg facility supports ArcticSat/Iris assembly, integration and testing.",
                ARCTICSAT,
                ARCTICSAT_AIT,
            ),
            fact(
                "Interlake School Division",
                "Named returning collaborator from the Iris project.",
                ARCTICSAT,
            ),
            fact(
                "Exolaunch — CUBICS launch services",
                "Exolaunch’s CSA agreement covers the nine CUBICS CubeSats, but it does not establish ArcticSat’s individual flight, vehicle or date.",
                EXOLAUNCH_CUBICS,
            ),
        ),
        facilities=(
            fact(
                "University of Manitoba payload-antenna test work",
                "The current ArcticSat engineering material identifies payload/antenna testing at the University of Manitoba campus. It is test-work evidence, not a claim of a named environmental-qualification chamber.",
                ARCTICSAT_STRUCTURE,
            ),
            fact(
                "Magellan Aerospace ASIF S-band test support",
                "The ArcticSat engineering material identifies S-band testing at Magellan Aerospace’s Advanced Satellite Integration Facility in Winnipeg. The broader StarLabSat AIT page documents ASIF’s cleanroom, vibration and TVAC capabilities, which should not be read as proof every one was used by ArcticSat.",
                ARCTICSAT_STRUCTURE,
                ARCTICSAT_AIT,
            ),
            fact(
                "University of Manitoba / Northern ground-station plan",
                "The ground-station design retains the Iris station, specifies a University of Manitoba station in its flight-model plan and a Northern station/remote-control scripts in Phase C.",
                ARCTICSAT_GROUND,
            ),
        ),
        milestone_note=fact(
            "Review schedule published; no NASA phase named",
            "ArcticSat’s engineering page lists MCR, PDR and CDR as future review dates and TRR/FRR as TBD; it is not proof that those reviews passed. The reviewed sources document test planning and subsystem work but do not assign ArcticSat a NASA lifecycle phase.",
            ARCTICSAT,
            ARCTICSAT_STRUCTURE,
        ),
        possible_aliases=(
            fact(
                "IceCube (original 2023 CSA project label)",
                "CSA’s June 2023 selection announcement calls the University of Manitoba project IceCube, while the current CSA table calls the same grant slot ArcticSat. The reviewed public record does not explicitly state a rename, so this is modeled as a possible historical identity rather than a definitive former name.",
                CSA_2023_SELECTION,
                CSA_CUBICS,
            ),
        ),
    ),
    Project(
        id="preset",
        recipient_label="McMaster University\n(MSTRI / MIST)",
        recipient_title="Official CUBICS grant recipient\nMcMaster University / McMaster Space Technology Research Initiative\nGrant: CAD 350,000",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 350,000",
        name="PRESET",
        title="Pitch REsolving Spectrometry for Electron Transport\n3U CubeSat\nOfficial CUBICS project: spectrometry of charged particles",
        source=MSTRI_PRESET,
        objectives=(
            fact(
                "Electron pitch-angle measurement",
                "Measure high-angular-resolution electron pitch-angle density near the poles in the Van Allen Belts.",
                MSTRI_PRESET,
            ),
            fact(
                "Energetic-electron transport / ozone-depletion research",
                "Improve understanding of electron removal from the Van Allen Belts and the effects of energetic-particle precipitation on polar upper-atmosphere ozone.",
                MSTRI_PRESET,
            ),
        ),
        payloads=(
            fact(
                "Electron Spectrometer Telescope (EST)",
                "1U multi-pin-hole collimator and silicon-strip-detector telescope, stated 200 keV–5 MeV energy range and 6° angular resolution.",
                MSTRI_PRESET,
            ),
            fact(
                "Three-axis magnetometer",
                "0.5U payload with inboard and outboard anisotropic-magnetoresistive sensor heads, used with the electron direction to resolve pitch angle.",
                MSTRI_PRESET,
            ),
        ),
        status=fact(
            "Planned — candidate Q4 2026 / no defined launch",
            "After its May 2025 CDR, MSTRI reported burn-in testing, FlatSat integration and upcoming complete EQM assembly. The IARU filing planned an October 2026 launch but said no launch had been defined; SpaceQ later called PRESET a possible Transporter-18 candidate in Q4 2026. Neither is a confirmed manifest.",
            SPACEQ_CUBICS_STATUS,
            PRESET_IARU,
            MSTRI_TRACKING,
        ),
        collaborators=(
            fact(
                "Canadian Space Agency (CSA)",
                "MSTRI describes PRESET as being developed in collaboration with CSA; CSA is also the CUBICS funder.",
                MSTRI_PRESET,
                CSA_CUBICS,
            ),
        ),
        partners=(
            fact(
                "Exolaunch — CUBICS launch services",
                "Exolaunch’s CSA agreement covers the nine CUBICS CubeSats, but does not confirm PRESET’s individual flight, vehicle or date.",
                EXOLAUNCH_CUBICS,
            ),
        ),
        facilities=(
            fact(
                "MIST FlatSat",
                "Bench-top replica of the satellite electronics used to validate integrated functionality across multiple subsystems in a controlled environment.",
                MSTRI_TRACKING,
            ),
            fact(
                "Engineering Qualification Model (EQM) assembly / burn-in test setup",
                "MSTRI reports a week-long burn-in test of the full software stack on the EQM assembly and plans complete EQM assembly.",
                MSTRI_TRACKING,
            ),
            fact(
                "NASA HASP balloon test campaign / thermal vacuum",
                "MSTRI reports testing PRESET payload, communications and power iterations on NASA’s HASP balloon campaign in 2024, including HASP-provided thermal-vacuum testing.",
                PRESET_HASP,
            ),
            fact(
                "McMaster ground station and Mission Operations Centre",
                "MSTRI identifies its ground station and Mission Operations Centre as being at McMaster University and says it uses SatNOGS for telemetry.",
                PRESET_GROUND,
            ),
        ),
        milestone_note=fact(
            "MCR, PDR, CDR and EQM verification recorded; no NASA phase named",
            "MSTRI records MCR, PDR and CDR, followed by TRR preparation, EQM/FlatSat integration and burn-in verification. These are factual project milestones; the cited sources do not assign PRESET a NASA lifecycle phase.",
            MSTRI_CDR,
            MSTRI_TRACKING,
        ),
    ),
    Project(
        id="munstar1",
        recipient_label="Memorial University of Newfoundland\n(MUNStar-1 team)",
        recipient_title="Official CUBICS grant recipient\nMemorial University of Newfoundland / MUNStar-1 team\nGrant: CAD 350,000",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 350,000",
        name="MUNStar-1",
        title="3U CubeSat\nOfficial CUBICS project: ocean monitoring for climate-change adaptation",
        source=MUNSTAR_ARCHIVE,
        objectives=(
            fact(
                "North Atlantic ocean-state monitoring",
                "Produce delay-Doppler maps to help oceanographers determine sea state in a North Atlantic region of interest.",
                MUNSTAR_ARCHIVE,
            ),
            fact(
                "Student learning, outreach and open ocean-condition data",
                "Support student learning in communications/space systems, outreach and publicly available ocean-condition data alongside the ocean-monitoring mission.",
                MUNSTAR_RADIO_ARCHIVE,
                MUNSTAR_SPACEOPS,
            ),
        ),
        payloads=(
            fact(
                "GNSS Reflectometry payload",
                "The payload uses a deployable nadir patch-antenna array, GNSS analog front end and FPGA digital back end to create delay-Doppler maps for North Atlantic sea-state determination.",
                MUNSTAR_SPACEOPS,
                MUNSTAR_ARCHIVE,
            ),
        ),
        status=fact(
            "Planned — TBA",
            "A September 2025 SpaceOps paper projected June 2026 on Falcon 9 Transporter-17, but that projection is stale: SpaceQ’s 2026-08-05 status report says only MARMOTSat flew on Transporter-17 and lists MUNStar-1 TBA. Falcon 9/Transporter-17 is therefore not modeled as a confirmed launch.",
            SPACEQ_CUBICS_STATUS,
            MUNSTAR_SPACEOPS,
        ),
        collaborators=(
            fact(
                "C-CORE",
                "C-CORE and Memorial are the principal joint effort identified in the MUNStar-1/Killick-2 announcement and SpaceOps paper.",
                MUNSTAR_CCORE,
                MUNSTAR_SPACEOPS,
            ),
            fact(
                "IEEE Student Branch", 
                "MUNStar-1 says Memorial partners with the IEEE Student Branch to offer free amateur-radio training and certification opportunity.",
                MUNSTAR_RADIO_ARCHIVE,
            ),
        ),
        partners=(
            fact(
                "Solace Power",
                "The SpaceOps paper identifies Solace Power as an industry partner.",
                MUNSTAR_SPACEOPS,
            ),
            fact(
                "Government of Newfoundland and Labrador",
                "The provincial government announced CAD 350,000 support for the mission, alongside the CSA grant and C-CORE contribution described in project material.",
                MUNSTAR_GOV,
                MUNSTAR_SPACEOPS,
            ),
            fact(
                "Radio Amateurs of Canada (RAC)",
                "The project promotes RAC course offerings for students seeking Amateur Radio Operator Certificates.",
                MUNSTAR_RADIO_ARCHIVE,
            ),
            fact(
                "Exolaunch — CUBICS launch services",
                "Exolaunch’s CSA agreement covers the nine CUBICS CubeSats, but it does not establish MUNStar-1’s individual flight, vehicle or date.",
                EXOLAUNCH_CUBICS,
            ),
        ),
        facilities=(
            fact(
                "MUN Cleanroom Lab",
                "The SpaceOps paper documents use of Memorial’s Cleanroom Lab for ADCS testing.",
                MUNSTAR_SPACEOPS,
            ),
            fact(
                "C-CORE roof ground station in St. John’s",
                "The SpaceOps paper identifies M2 Yagi ground-station antennas on the C-CORE office roof in St. John’s for mission communications.",
                MUNSTAR_SPACEOPS,
            ),
        ),
        milestone_note=fact(
            "MCR, PDR, CDR and test activity recorded; no NASA phase named",
            "The SpaceOps paper records MCR (2023), PDR (2024), CDR (2025), cleanroom ADCS testing and ground-station assembly. These are factual milestones; the paper does not assign MUNStar-1 a NASA lifecycle phase.",
            MUNSTAR_SPACEOPS,
        ),
        aliases=(
            fact(
                "Killick-2 / MUNStars-1 (former names)",
                "C-CORE says the successor mission was formally known as Killick-2 and renamed MUNStars-1; the current CSA roster uses singular MUNStar-1.",
                MUNSTAR_CCORE,
                CSA_CUBICS,
            ),
        ),
    ),
    Project(
        id="radsat_sk2",
        recipient_label="University of Saskatchewan\n(SkCubeSat)",
        recipient_title="Official CUBICS grant recipient\nUniversity of Saskatchewan / SkCubeSat\nGrant: CAD 350,000",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 350,000",
        name="RADSAT-SK2",
        title="Saskatchewan's second home-grown satellite\nOfficial CUBICS project: radiation-mitigation technology for computer hardware in space",
        source=RADSAT_ARCHIVE,
        objectives=(
            fact(
                "Radiation-mitigating computer hardware in space",
                "The official CSA award title states the mission objective: demonstrate new radiation-mitigating technologies for computer hardware in space.",
                CSA_CUBICS,
            ),
        ),
        payloads=(
            fact(
                "Radiation-effects / mitigation electronics payload",
                "The IARU filing describes the primary payload as studying radiation effects on electronics and mitigations; team material specifies testing analog ICs and commercial microcontrollers.",
                RADSAT_IARU,
                RADSAT_PCBAWAY,
            ),
            fact(
                "Cloud-cover camera and AI algorithm",
                "The IARU filing identifies a small camera as a secondary climate-measurement payload; project material describes a cloud-detection AI algorithm.",
                RADSAT_IARU,
                RADSAT_PCBAWAY,
            ),
        ),
        status=fact(
            "Planned — TBA",
            "The IARU filing planned ISS deployment in Q4 2026, while SpaceQ’s 2026-08-05 CUBICS table lists RADSAT-SK2 TBA. No individual provider, rocket or confirmed launch date is publicly established, so the filing is treated as a plan rather than a manifest.",
            SPACEQ_CUBICS_STATUS,
            RADSAT_IARU,
        ),
        collaborators=(
            fact(
                "University of Regina / University of Regina Space Design Team",
                "The IARU filing names the University of Regina and its Space Design Team alongside the University of Saskatchewan and USask Space Design Team as collaborators.",
                RADSAT_IARU,
            ),
            fact(
                "University of Saskatchewan Space Design Team",
                "Named as the student team collaborator in the IARU filing; USask separately reported that RADSAT-SK2 was being built in 2024.",
                RADSAT_IARU,
                RADSAT_USASK,
            ),
        ),
        partners=(
            fact(
                "Exolaunch — CUBICS launch services",
                "Exolaunch’s CSA agreement covers the nine CUBICS CubeSats, but it does not establish RADSAT-SK2’s individual flight, vehicle or date.",
                EXOLAUNCH_CUBICS,
            ),
        ),
        facilities=(
            fact(
                "Hardy Lab team room and SkCubeSat cleanroom (historic shared facility)",
                "An archived SkCubeSat page says RADSAT-SK and RADSAT-SK2 were built in the University of Saskatchewan Space Design Team room in the College of Engineering's Hardy Lab, with a student-built temperature/humidity-controlled cleanroom. A current SK2-specific AIT/qualification campaign is not documented, so this is modeled as historic shared-facility evidence rather than proof of a completed SK2 test campaign.",
                RADSAT_FACILITIES_ARCHIVE,
            ),
            fact(
                "SkCubeSat ground station (historic shared facility)",
                "The archived facilities page describes the team’s bidirectional ground station for command, telemetry and science data; a current RADSAT-SK2-specific operations facility is not identified in the reviewed record.",
                RADSAT_FACILITIES_ARCHIVE,
            ),
        ),
        milestone_note=fact(
            "Construction and radio coordination recorded; no NASA phase named",
            "Public sources record construction and radio-frequency coordination. They do not assign RADSAT-SK2 a NASA lifecycle phase; claims about the timing of CDR activity are not normalized here because the available sources conflict.",
            RADSAT_IARU,
            RADSAT_USASK,
        ),
    ),
    Project(
        id="western_skylark",
        recipient_label="Western University\n(WEST / Western Space)",
        recipient_title="Official CUBICS grant recipient\nWestern University / Western Engineering Satellite Team\nGrant: CAD 350,000",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 350,000",
        name="The Western Skylark",
        title="3U CubeSat\nNext-generation migratory-wildlife tracking using Motus and ICARUS telemetry systems",
        source=WESTERN_ARCHIVE,
        objectives=(
            fact(
                "Migratory-wildlife tracking",
                "Collect space-based data on migratory songbirds, waterbirds and shorebirds to support migration understanding and conservation.",
                WESTERN_ARCHIVE,
            ),
            fact(
                "Motus data relay demonstration",
                "Demonstrate efficient collection and relay of Motus data using a 3U CubeSat, extending the Motus network.",
                WESTERN_ARCHIVE,
                CSA_CUBICS,
            ),
            fact(
                "Student and amateur-radio engagement",
                "Train students in CubeSat construction/operations and support amateur-radio participation and outreach.",
                WESTERN_ARCHIVE,
            ),
        ),
        payloads=(
            fact(
                "Motus and ICARUS telemetry systems",
                "The official CSA award title identifies Motus and ICARUS as the tracking telemetry systems for the 3U satellite. However, the networks themselves are not stated as partners.",
                CSA_CUBICS,
            ),
            fact(
                "AX.25 telemetry beacon",
                "The archived project page says Skylark will carry an AX.25 beacon receivable by amateur-radio users.",
                WESTERN_ARCHIVE,
            ),
        ),
        status=fact(
            "Planned — team target Q2 2027",
            "The IARU filing updated 2026-07-05 says the team is planning an Exolaunch deployment to an approximately 500–600 km SSO in Q2 2027, with frequency coordination still incomplete. SpaceQ’s 2026-08-05 CUBICS table lists the mission TBA, so this is a plan rather than a confirmed launch/rocket assignment.",
            WESTERN_IARU,
            SPACEQ_CUBICS_STATUS,
        ),
        collaborators=(
            fact(
                "London Amateur Radio Club", 
                "The archived project page directs students seeking amateur-radio training/certification to the London Amateur Radio Club and names it in outreach collaboration.",
                WESTERN_ARCHIVE,
            ),
        ),
        partners=(
            fact(
                "Exolaunch — planned launch services",
                "The IARU filing says the team is planning Exolaunch deployment; the program-wide CSA/Exolaunch agreement does not confirm its individual flight, vehicle or date.",
                WESTERN_IARU,
                EXOLAUNCH_CUBICS,
            ),
        ),
        facilities=(
            fact(
                "Western Mission Control Facility — room 7110",
                "Western Space identifies room 7110 in the Western Interdisciplinary Research Building as a mission-control hub for Skylark. It is operations infrastructure, not proof of environmental qualification testing.",
                WESTERN_MISSION_CONTROL,
            ),
            fact(
                "No named project test/integration facility publicly identified",
                "Western’s public material says Skylark will communicate with a ground station but does not name its location, cleanroom, TVAC or vibration facility. A 2025 thesis documents launch-vibration and orbital-thermal modelling, which is analysis evidence rather than proof of physical environmental qualification.",
                WESTERN_ARCHIVE,
                WESTERN_THESIS,
                gap=True,
            ),
        ),
        milestone_note=fact(
            "Engineering analysis and radio filing recorded; no NASA phase named",
            "Public sources document launch-vibration/orbital-thermal modelling and an in-process radio filing, but do not identify a completed integration, qualification, TRR/FRR or NASA lifecycle phase for Western Skylark.",
            WESTERN_IARU,
            WESTERN_THESIS,
        ),
    ),
    Project(
        id="marmotsat",
        recipient_label="University of Victoria\n(CfAR + UVSD)",
        recipient_title="Official CUBICS grant recipient\nUniversity of Victoria / Centre for Aerospace Research and UVic Satellite Design\nGrant: CAD 349,600",
        recipient_source=CSA_CUBICS,
        grant_value="CAD 349,600",
        name="MARMOTSat",
        title="Mission for Atmospheric Radio Measurements with Open-source Technology Satellite\n3U CubeSat · launched 2026-07-07",
        source=MARMOTSAT,
        objectives=(
            fact(
                "Ionosphere / climate-change research",
                "Support UVic Propagation Laboratory research into the relationship between ionospheric composition/structure and human climate-change-related activity.",
                MARMOTSAT,
                MARMOT_UVIC,
            ),
            fact(
                "Open-source satellite radio demonstration",
                "Fly a radio system intended to be released as open-source spacecraft hardware/software for other teams and amateur-radio users.",
                MARMOT_UVIC,
            ),
            fact(
                "Highly qualified personnel training",
                "Provide undergraduate and graduate students hands-on design, manufacturing, testing and operations experience.",
                MARMOTSAT,
            ),
        ),
        payloads=(
            fact(
                "Modular CubeSat Radio / ionospheric sounding experiments",
                "MARMOTSat’s Propagation Laboratory page describes the Modular CubeSat Radio, VHF digipeater, VHF and 10 m CW telemetry, 10 m DVB-S2 video beacon, and ionospheric citizen-science sounding experiment. The project site and UVic News corroborate the transionospheric-sounding and open-source-radio mission; no separate commercial instrument name is published.",
                MARMOT_RADIO,
                MARMOTSAT,
                MARMOT_UVIC,
            ),
        ),
        status=fact(
            "Launched — in-orbit commissioning",
            "MARMOTSat successfully launched on SpaceX Transporter-17 on 2026-07-07. Its project site says it is undergoing in-orbit commissioning to bring systems online; the 2026-08-05 CUBICS status report identifies it as the only one of the nine to have launched by that point.",
            CSA_MARMOT_LAUNCH,
            MARMOTSAT,
            SPACEQ_CUBICS_STATUS,
        ),
        collaborators=(
            fact(
                "UVic Centre for Aerospace Research (CfAR)",
                "CfAR students and researchers designed and built the spacecraft with UVic Satellite Design.",
                CSA_MARMOT_LAUNCH,
                MARMOTSAT,
            ),
            fact(
                "UVic Satellite Design (UVSD)",
                "UVSD volunteers made major contributions and are named with CfAR as the 57-person design/build team.",
                CSA_MARMOT_LAUNCH,
                MARMOTSAT,
            ),
            fact(
                "UVic Propagation Laboratory",
                "The MARMOTSat mission supports the laboratory's ionosphere/climate research.",
                MARMOTSAT,
            ),
        ),
        partners=(
            fact(
                "CubeSpace",
                "MARMOTSat says its ADCS is provided by CubeSpace; this is a subsystem-provider relation.",
                MARMOTSAT,
            ),
            fact(
                "SpaceX / Transporter-17 rideshare",
                "CSA confirms launch aboard the SpaceX Transporter-17 rideshare mission.",
                CSA_MARMOT_LAUNCH,
            ),
            fact(
                "Exolaunch",
                "MARMOTSat’s pre-launch integration update documents CSA cleanroom integration into an Exolaunch deployer. This is an integration/launch-services relation, distinct from SpaceX as the launch vehicle operator.",
                MARMOT_INTEGRATION,
            ),
        ),
        facilities=(
            fact(
                "CfAR amateur-satellite ground station",
                "The CUBICS CDR-week report says the hands-on operations workshop used CfAR's amateur-satellite ground station, which was to be used for MARMOTSat.",
                UVIC_CDR,
            ),
            fact(
                "TRIUMF Proton Irradiation Facility",
                "MARMOTSat documents a completed proton-irradiation test campaign at TRIUMF’s Proton Irradiation Facility.",
                MARMOT_TRIUMF,
            ),
            fact(
                "CSA Longueuil vibration laboratories",
                "MARMOTSat documents flight-spacecraft vibration testing in CSA Longueuil laboratories for Falcon 9 launch qualification context.",
                MARMOT_VIBRATION,
            ),
            fact(
                "CSA cleanroom / Exolaunch deployer integration",
                "MARMOTSat documents flight-spacecraft integration in a CSA cleanroom into an Exolaunch deployer. This is integration evidence, not a claim that CSA owns the team's test facility.",
                MARMOT_INTEGRATION,
                CSA_MARMOT_LAUNCH,
            ),
        ),
        milestone_note=fact(
            "CDR, TRR, integration, launch and commissioning recorded; no NASA phase named",
            "MARMOTSat documents CDR, a passed TRR, qualification/integration, successful launch and in-orbit commissioning. Those are factual milestones; neither CSA nor UVic labels the mission with a NASA lifecycle phase.",
            MARMOT_CDR,
            MARMOT_TRR,
            CSA_MARMOT_LAUNCH,
            MARMOTSAT,
        ),
        aliases=(
            fact(
                "SKYA'ANA / SKYA'ANAsat (former name)",
                "Historic CUBICS selection material used the SKYA'ANA name. Per the supplied project clarification, it is modeled here as the former name of the current MARMOTSat project, not as a tenth grant recipient; SpaceQ also explicitly describes MARMOTSat as previously named SKYA'ANAsat.",
                MARMOT_RENAME,
                CSA_2023_SELECTION,
                MARMOTSAT,
            ),
        ),
    ),
)


# ---------------------------------------------------------------------------
# Graph construction


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")


def _wrap_label(value: str, width: int = 28, max_lines: int = 4) -> str:
    """Wrap labels without hiding key words in the dense graph view."""

    words = value.replace("\n", " ").split()
    if not words:
        return value
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and len(candidate) > width:
            lines.append(line)
            line = word
            if len(lines) == max_lines - 1:
                break
        else:
            line = candidate
    remainder = " ".join(words[sum(len(item.split()) for item in lines) :])
    if len(lines) < max_lines and remainder:
        if len(remainder) > width and len(lines) == max_lines - 1:
            remainder = remainder[: width - 1].rstrip() + "…"
        lines.append(remainder)
    return "\n".join(lines[:max_lines])


def _sources_text(sources: Iterable[Source]) -> str:
    return "\n".join(f"• {source.label}: {source.url}" for source in sources)


def _fact_title(category: str, item: Fact) -> str:
    heading = f"{category}: {item.label}"
    lines = [heading, "", item.detail]
    if item.gap:
        lines.extend(["", f"Evidence gap assessed on {ASSESSMENT_DATE}; this is not a claim that the capability does not exist."])
    lines.extend(["", "Sources:", _sources_text(item.sources)])
    return "\n".join(lines)


def _project_title(project: Project) -> str:
    return "\n".join(
        [
            project.title,
            "",
            f"Grant recipient: {project.recipient_label.replace(chr(10), ' / ')}",
            f"Grant value: {project.grant_value}",
            "",
            "Flight status:",
            project.status.label,
            project.status.detail,
            "Sources:",
            "\n".join(
                f"• {source.label}: {source.url}"
                for source in project.status.sources
            ),
            "",
            "Public review / lifecycle note:",
            project.milestone_note.label,
            project.milestone_note.detail,
            "Sources:",
            "\n".join(
                f"• {source.label}: {source.url}"
                for source in project.milestone_note.sources
            ),
            "",
            "Primary project source:",
            f"{project.source.label}: {project.source.url}",
            "",
            "Use the dossier below for field-level details and sources.",
        ]
    )


def _fact_node_class(category: str, item: Fact) -> type[Node]:
    if item.gap:
        return EvidenceGap
    return {
        "Objective": Objective,
        "Payload": Payload,
        "Collaborator": Collaborator,
        "Partner": Partner,
        "Test / operations facility": Facility,
        "Former name": Alias,
        "Possible former / related name": Alias,
    }[category]


def _fact_edge_class(category: str, item: Fact) -> type[Edge]:
    if item.gap:
        return NotPubliclyDocumented
    return {
        "Objective": HasObjective,
        "Payload": Carries,
        "Collaborator": CollaboratesWith,
        "Partner": PartnersWith,
        "Test / operations facility": UsesFacility,
        "Former name": RenamedTo,
        "Possible former / related name": PossiblySameAs,
    }[category]


def _make_fact_relation(
    project: Project,
    satellite_id: str,
    category: str,
    index: int,
    item: Fact,
) -> tuple[Node, RelationRecord]:
    node_id = f"{project.id}_{_slug(category)}_{index + 1}"
    node_class = _fact_node_class(category, item)
    edge_class = _fact_edge_class(category, item)
    node = node_class(
        id=node_id,
        label=_wrap_label(item.label),
        title=_fact_title(category, item),
        source_url=item.primary_source.url,
    )
    edge = edge_class(
        id=f"{_slug(category)}_{project.id}_{index + 1}",
        source_url=item.primary_source.url,
        evidence=item.detail,
    )
    # Historical-name relations read naturally in the opposite direction.
    if category in {"Former name", "Possible former / related name"}:
        relation = RelationRecord(source=node_id, target=satellite_id, edge=edge)
    else:
        relation = RelationRecord(source=satellite_id, target=node_id, edge=edge)
    return node, relation


def build_data() -> tuple[list[Node], list[RelationRecord]]:
    # Deliberately keep the nine grants disconnected. A CSA/CUBICS hub made the
    # graph a single dense star and obscured the project-level relationships.
    nodes: list[Node] = []
    relations: list[RelationRecord] = []

    categories = (
        ("Objective", "objectives"),
        ("Payload", "payloads"),
        ("Collaborator", "collaborators"),
        ("Partner", "partners"),
        ("Test / operations facility", "facilities"),
    )

    for project in PROJECTS:
        recipient_id = f"recipient_{project.id}"
        satellite_id = f"satellite_{project.id}"
        recipient = GrantRecipient(
            id=recipient_id,
            label=project.recipient_label,
            title=(
                f"{project.recipient_title}\n\nSource:\n"
                f"{project.recipient_source.label}: {project.recipient_source.url}"
            ),
            source_url=project.recipient_source.url,
        )
        satellite = CubeSat(
            id=satellite_id,
            label=project.name,
            title=_project_title(project),
            source_url=project.source.url,
        )
        nodes.extend((recipient, satellite))
        relations.append(
            RelationRecord(
                source=recipient_id,
                target=satellite_id,
                edge=Leads(
                    id=f"leads_{project.id}",
                    source_url=project.source.url,
                    evidence="The recipient/team project source identifies this CubeSat mission.",
                ),
            )
        )

        for category, field_name in categories:
            for index, item in enumerate(getattr(project, field_name)):
                node, relation = _make_fact_relation(
                    project, satellite_id, category, index, item
                )
                nodes.append(node)
                relations.append(relation)

        for index, item in enumerate(project.aliases):
            node, relation = _make_fact_relation(
                project, satellite_id, "Former name", index, item
            )
            nodes.append(node)
            relations.append(relation)

        for index, item in enumerate(project.possible_aliases):
            node, relation = _make_fact_relation(
                project, satellite_id, "Possible former / related name", index, item
            )
            nodes.append(node)
            relations.append(relation)

    return nodes, relations


NODES, RELATIONS = build_data()
NODES_BY_ID = {node.id: node for node in NODES}


# ---------------------------------------------------------------------------
# Semantic validation


def _node_kind(node: Node) -> str:
    if isinstance(node, GrantRecipient):
        return "recipient"
    if isinstance(node, CubeSat):
        return "cubesat"
    if isinstance(node, Objective):
        return "objective"
    if isinstance(node, Payload):
        return "payload"
    if isinstance(node, Collaborator):
        return "collaborator"
    if isinstance(node, Partner):
        return "partner"
    if isinstance(node, Facility):
        return "facility"
    if isinstance(node, Alias):
        return "alias"
    if isinstance(node, EvidenceGap):
        return "gap"
    raise TypeError(f"Unknown node type: {type(node).__name__}")


def validate_data() -> None:
    if len(NODES_BY_ID) != len(NODES):
        raise ValueError("Duplicate node IDs found.")

    edge_ids = [record.edge.id for record in RELATIONS]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError("Duplicate edge IDs found.")

    connected = {node_id for record in RELATIONS for node_id in (record.source, record.target)}
    orphan_ids = sorted(set(NODES_BY_ID) - connected)
    if orphan_ids:
        raise ValueError(f"Orphan nodes found: {orphan_ids}")

    for relation in RELATIONS:
        if relation.source not in NODES_BY_ID or relation.target not in NODES_BY_ID:
            raise KeyError(f"Unknown endpoint in relation {relation.edge.id}")
        source_kind = _node_kind(NODES_BY_ID[relation.source])
        target_kind = _node_kind(NODES_BY_ID[relation.target])
        edge = relation.edge

        if isinstance(edge, Leads):
            ok = source_kind == "recipient" and target_kind == "cubesat"
        elif isinstance(edge, HasObjective):
            ok = source_kind == "cubesat" and target_kind in {"objective", "gap"}
        elif isinstance(edge, Carries):
            ok = source_kind == "cubesat" and target_kind in {"payload", "gap"}
        elif isinstance(edge, CollaboratesWith):
            ok = source_kind == "cubesat" and target_kind in {"collaborator", "gap"}
        elif isinstance(edge, PartnersWith):
            ok = source_kind == "cubesat" and target_kind in {"partner", "gap"}
        elif isinstance(edge, UsesFacility):
            ok = source_kind == "cubesat" and target_kind in {"facility", "gap"}
        elif isinstance(edge, (RenamedTo, PossiblySameAs)):
            ok = source_kind == "alias" and target_kind == "cubesat"
        elif isinstance(edge, NotPubliclyDocumented):
            ok = source_kind == "cubesat" and target_kind == "gap"
        else:
            raise TypeError(f"Unhandled edge type: {type(edge).__name__}")

        if not ok:
            raise ValueError(
                f"Invalid endpoints for {type(edge).__name__}: "
                f"{relation.source} ({source_kind}) -> {relation.target} ({target_kind})"
            )


validate_data()


# ---------------------------------------------------------------------------
# PyVis rendering and HTML dossier


def _node_hover(node: Node) -> str:
    return f"{node.title}\n\nDouble-click to open source."


def _edge_hover(record: RelationRecord) -> str:
    edge = record.edge
    parts = [edge.label]
    if edge.evidence:
        parts.extend(("", edge.evidence))
    parts.extend(("", f"Source: {edge.source_url}", "", "Double-click to open source."))
    return "\n".join(parts)


def _project_id_for_node(node_id: str) -> str:
    """Return the mini-graph owning a node, for the project focus control."""

    for project in PROJECTS:
        if node_id in {f"recipient_{project.id}", f"satellite_{project.id}"}:
            return project.id
        if node_id.startswith(f"{project.id}_"):
            return project.id
    raise KeyError(f"Node is not associated with a CUBICS project: {node_id}")


def build_network(
    *,
    height: str = "1350px",
    width: str = "100%",
    show_edge_labels: bool = True,
) -> Network:
    net = Network(
        height=height,
        width=width,
        directed=True,
        bgcolor="#07111f",
        font_color="#f8f9fa",
        notebook=False,
        cdn_resources="in_line",
        filter_menu=True,
    )

    for node in NODES:
        net.add_node(
            node.id,
            label=node.label,
            title=_node_hover(node),
            color={"background": node.color, "border": "#e9ecef"},
            shape=node.shape,
            source_url=node.source_url,
            project_id=_project_id_for_node(node.id),
            borderWidth=1.25,
            font={"color": "#f8f9fa", "face": "Arial", "size": 13},
        )

    for record in RELATIONS:
        edge = record.edge
        net.add_edge(
            record.source,
            record.target,
            id=edge.id,
            label=edge.label if show_edge_labels else "",
            title=_edge_hover(record),
            color=edge.color,
            dashes=edge.dashes,
            arrows="to",
            source_url=edge.source_url,
            project_id=_project_id_for_node(record.source),
            font={"color": "#f8f9fa", "size": 10, "strokeWidth": 4, "strokeColor": "#07111f"},
        )

    # A high central gravity (0.16) fights full collision avoidance across the
    # disconnected components and never reaches a stable ForceAtlas2 state.
    net.set_options(
        """
        {
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "multiselect": true
          },
          "layout": {"improvedLayout": true},
          "nodes": {
            "margin": 8,
            "widthConstraint": {"maximum": 175},
            "font": {"size": 13, "face": "Arial", "color": "#f8f9fa"}
          },
          "edges": {
            "smooth": {"enabled": false},
            "arrows": {"to": {"enabled": true, "scaleFactor": 0.6}}
          },
          "physics": {
            "enabled": true,
            "solver": "forceAtlas2Based",
            "stabilization": {"enabled": true, "iterations": 1200, "updateInterval": 40, "fit": true},
            "forceAtlas2Based": {
              "gravitationalConstant": -95,
              "centralGravity": 0.01,
              "springLength": 250,
              "springConstant": 0.01,
              "damping": 0.65,
              "avoidOverlap": 1
            }
          }
        }
        """
    )
    return net


def build_project_selector_html() -> str:
    options = ['<option value="all">All nine projects</option>']
    for project in PROJECTS:
        label = f"{project.name} — {project.recipient_label.replace(chr(10), ' / ')}"
        options.append(
            f'<option value="{escape(project.id, quote=True)}">{escape(label)}</option>'
        )
    return "".join(
        (
            '<section id="project-focus-controls" aria-label="Project graph focus">',
            '<label for="project-focus"><strong>Focus a project</strong></label>',
            '<select id="project-focus">',
            "".join(options),
            "</select>",
            '<span>Choose a recipient to isolate its mini-graph; select all nine for the overview.</span>',
            "</section>",
        )
    )


def _source_links(sources: Iterable[Source]) -> str:
    links = []
    seen: set[str] = set()
    for source in sources:
        if source.url in seen:
            continue
        seen.add(source.url)
        links.append(
            f'<a href="{escape(source.url, quote=True)}" target="_blank" rel="noopener">'
            f"{escape(source.label)}</a>"
        )
    return " · ".join(links)


def _fact_html(item: Fact) -> str:
    marker = ""
    if item.gap:
        marker = ' <span class="badge gap">public-evidence gap</span>'
    return "".join(
        (
            "<details>",
            f"<summary>{escape(item.label)}{marker}</summary>",
            f"<p>{escape(item.detail)}</p>",
            f'<p class="sources"><strong>Sources:</strong> {_source_links(item.sources)}</p>',
            "</details>",
        )
    )


def _facts_html(items: Iterable[Fact]) -> str:
    return "<div class=\"fact-list\">" + "".join(_fact_html(item) for item in items) + "</div>"


def _all_sources() -> list[Source]:
    sources: list[Source] = [CSA_CUBICS]
    for project in PROJECTS:
        sources.extend((project.recipient_source, project.source))
        for item in (
            *project.objectives,
            *project.payloads,
            project.status,
            *project.collaborators,
            *project.partners,
            *project.facilities,
            project.milestone_note,
            *project.aliases,
            *project.possible_aliases,
        ):
            sources.extend(item.sources)
    deduplicated: dict[str, Source] = {}
    for source in sources:
        deduplicated.setdefault(source.url, source)
    return sorted(deduplicated.values(), key=lambda source: source.label.casefold())


def build_dossier_html() -> str:
    rows = []
    for project in PROJECTS:
        rows.append(
            "<tr>"
            f"<th scope=\"row\"><strong>{escape(project.name)}</strong><br>"
            f"<span class=\"muted\">{escape(project.grant_value)}</span><br>"
            f"<a href=\"{escape(project.recipient_source.url, quote=True)}\" target=\"_blank\" rel=\"noopener\">{escape(project.recipient_label.replace(chr(10), ' / '))}</a></th>"
            f"<td>{_facts_html(project.objectives)}</td>"
            f"<td>{_facts_html(project.payloads)}</td>"
            f"<td>{_fact_html(project.status)}</td>"
            f"<td>{_facts_html(project.collaborators)}</td>"
            f"<td>{_facts_html(project.partners)}</td>"
            f"<td>{_facts_html(project.facilities)}</td>"
            "</tr>"
        )

    inventory = "".join(
        f'<li><a href="{escape(source.url, quote=True)}" target="_blank" rel="noopener">{escape(source.label)}</a></li>'
        for source in _all_sources()
    )
    return f"""
    <section id="cubics-dossier" aria-label="CUBICS 2022 project dossiers">
      <h1>{escape(DATASET_TITLE)}</h1>
      <p class="lede">Nine source-aware <strong>recipient → CubeSat mini-graphs</strong>. The CSA/CUBICS hub nodes are intentionally omitted so each grant remains a separate, readable component. The opportunity was posted in September 2022 and the awards were announced in June 2023. Double-click graph items to open their cited source; use the dossier for complete field-level evidence.</p>
      <div class="notes">
        <p><strong>Layout:</strong> each disconnected component contains a grant recipient (box), its CubeSat (triangle), and color-coded fact nodes (dots). A gravity-based ForceAtlas layout with collision avoidance keeps components apart; use <em>Focus a project</em> for an isolated view.</p>
        <p><strong>Status cutoff:</strong> {ASSESSMENT_DATE}. <em>Planned</em> means that the reviewed public material does not document a launch; it is not a claim that a source's schedule is current. <em>Launched</em> requires a launch confirmation.</p>
        <p><strong>Lifecycle evidence:</strong> no inferred NASA phases are shown. Each CubeSat’s hover note contains only the publicly recorded reviews, tests, integration or commissioning milestones, and explicitly says when no NASA phase was published.</p>
        <p><strong>Evidence gaps:</strong> a gray <span class="badge gap">public-evidence gap</span> records what the reviewed public pages did <em>not</em> name as of the cutoff, rather than inventing a payload, partner or test facility.</p>
        <p><strong>Name normalization:</strong> <strong>SKYA'ANA / SKYA'ANAsat</strong> is modeled as the former name of <strong>MARMOTSat</strong>, per the supplied clarification and historic CSA material. <strong>Killick-2 / MUNStars-1</strong> is normalized to current <strong>MUNStar-1</strong>. The historic Manitoba label <strong>IceCube</strong> is linked to ArcticSat as <em>possibly the same project</em>, because the two CSA tables use different names but the reviewed sources do not explicitly document a rename. These do not create extra recipients.</p>
      </div>
      <div class="legend" aria-label="Graph legend">
        <span><i class="swatch recipient"></i> grant recipient (box)</span>
        <span><i class="swatch satellite"></i> CubeSat (triangle)</span>
        <span><i class="swatch objective"></i> objective</span>
        <span><i class="swatch payload"></i> payload</span>
        <span><i class="swatch collaborator"></i> collaborator</span>
        <span><i class="swatch facility"></i> test / operations facility</span>
        <span><i class="swatch gap"></i> evidence gap</span>
      </div>
      <h2>Project dossiers</h2>
      <div class="table-scroll">
        <table>
          <thead><tr>
            <th>Grant recipient / CubeSat</th><th>Objective</th><th>Payload</th><th>Status</th>
            <th>Collaborators</th><th>Partners</th><th>Test / operations facilities</th>
          </tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
      <h2>Source inventory</h2>
      <p class="muted">Archived links are deliberately labeled because their schedules and page content may be stale. The retired/hijacked <code>skcubesat.ca</code> live domain is not used as a current source.</p>
      <ul class="source-inventory">{inventory}</ul>
    </section>
    """


TOOLTIP_CSS = """
<style>
  html, body { background: #07111f !important; color: #eef5ff !important; font-family: Arial, sans-serif; }
  .vis-tooltip { background: #101c2d !important; color: #f8f9fa !important; border: 1px solid #8ea4bf !important; white-space: pre-line !important; max-width: 460px !important; padding: 10px !important; }
  #project-focus-controls { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; max-width: 1800px; margin: 14px auto 8px; padding: 10px 16px; color: #e8eef7; background: #101c2d; border-left: 4px solid #4cc9f0; border-radius: 4px; }
  #project-focus { max-width: min(560px, 100%); padding: 6px 9px; color: #eef5ff; background: #172a42; border: 1px solid #6f8dab; border-radius: 4px; }
  #project-focus-controls span { color: #bdc8d6; font-size: .9rem; }
  #cubics-dossier { max-width: 1800px; margin: 0 auto; padding: 28px 24px 56px; color: #e8eef7; line-height: 1.45; }
  #cubics-dossier h1 { font-size: 1.8rem; margin: 0 0 8px; }
  #cubics-dossier h2 { margin-top: 36px; font-size: 1.35rem; }
  #cubics-dossier a { color: #84d8ff; }
  #cubics-dossier .lede { font-size: 1.05rem; max-width: 1050px; }
  #cubics-dossier .notes { background: #101c2d; border-left: 4px solid #4cc9f0; border-radius: 4px; padding: 8px 18px; margin: 20px 0; }
  #cubics-dossier .notes p { margin: 10px 0; }
  #cubics-dossier .muted { color: #bdc8d6; }
  #cubics-dossier .legend { display: flex; flex-wrap: wrap; gap: 11px 20px; margin: 18px 0 28px; font-size: .92rem; }
  #cubics-dossier .legend span { white-space: nowrap; }
  #cubics-dossier .swatch { display: inline-block; width: 12px; height: 12px; border: 1px solid #e9ecef; border-radius: 50%; vertical-align: -1px; margin-right: 5px; }
  #cubics-dossier .agency { background: #ffd166; } .recipient { background: #f4a261; } .satellite { background: #4cc9f0; }
  #cubics-dossier .objective { background: #90be6d; } .payload { background: #c77dff; } .collaborator { background: #ff9f1c; }
  #cubics-dossier .facility { background: #43aa8b; } .gap { background: #6c757d; }
  #cubics-dossier .table-scroll { overflow-x: auto; border: 1px solid #34495e; border-radius: 6px; }
  #cubics-dossier table { width: 100%; min-width: 2000px; border-collapse: collapse; background: #0b1727; font-size: .88rem; }
  #cubics-dossier th, #cubics-dossier td { padding: 12px; border: 1px solid #34495e; vertical-align: top; text-align: left; }
  #cubics-dossier thead th { position: sticky; top: 0; z-index: 1; background: #172a42; color: #fff; }
  #cubics-dossier tbody > tr:nth-child(even) { background: #0f1c2d; }
  #cubics-dossier th[scope=row] { min-width: 190px; background: #12233a; }
  #cubics-dossier details { margin: 0 0 8px; }
  #cubics-dossier details:last-child { margin-bottom: 0; }
  #cubics-dossier summary { cursor: pointer; color: #fff; font-weight: 600; }
  #cubics-dossier details p { margin: 7px 0; }
  #cubics-dossier .sources { font-size: .78rem; color: #bdc8d6; }
  #cubics-dossier .badge { display: inline-block; padding: 1px 5px; border-radius: 8px; font-size: .7rem; font-weight: 600; vertical-align: 1px; }
  #cubics-dossier .badge.gap { background: #495057; color: #fff; }
  #cubics-dossier .source-inventory { columns: 2 420px; padding-left: 22px; }
  #cubics-dossier .source-inventory li { break-inside: avoid; margin: 5px 0; }
  @media (max-width: 700px) { #project-focus-controls { align-items: flex-start; flex-direction: column; margin: 10px 8px; } #project-focus { max-width: 100%; } #cubics-dossier { padding: 22px 14px 42px; } #cubics-dossier .source-inventory { columns: 1; } }
</style>
"""

PROJECT_FOCUS_SCRIPT = """
<script>
  (function () {
    if (typeof network === "undefined") return;
    var selector = document.getElementById("project-focus");
    if (!selector) return;
    var nodeData = network.body.data.nodes;
    var edgeData = network.body.data.edges;
    function focusProject() {
      var selected = selector.value;
      nodeData.update(nodeData.get().map(function (node) {
        return {id: node.id, hidden: selected !== "all" && node.project_id !== selected};
      }));
      edgeData.update(edgeData.get().map(function (edge) {
        return {id: edge.id, hidden: selected !== "all" && edge.project_id !== selected};
      }));
      var visible = nodeData.get().filter(function (node) { return !node.hidden; }).map(function (node) { return node.id; });
      window.setTimeout(function () {
        network.fit({nodes: visible, animation: {duration: 250, easingFunction: "easeInOutQuad"}});
      }, 0);
    }
    selector.addEventListener("change", focusProject);
  }());
</script>
"""

SOURCE_INTERACTION = """
<script>
  (function () {
    if (typeof network === "undefined") return;
    network.on("doubleClick", function (params) {
      var item = null;
      if (params.nodes && params.nodes.length) item = network.body.data.nodes.get(params.nodes[0]);
      else if (params.edges && params.edges.length) item = network.body.data.edges.get(params.edges[0]);
      if (item && /^https?:\\/\\//.test(item.source_url || "")) {
        window.open(item.source_url, "_blank", "noopener");
      }
    });
  }());
</script>
"""


def render_html(
    output_path: str | Path = "cubics_2022_knowledge_graph.html",
    *,
    show_edge_labels: bool = True,
) -> Path:
    output_path = Path(output_path)
    net = build_network(show_edge_labels=show_edge_labels)
    net.write_html(str(output_path), open_browser=False, notebook=False)

    html = output_path.read_text(encoding="utf-8")
    html = html.replace("</head>", TOOLTIP_CSS + "</head>")
    html = html.replace(
        '<div id="mynetwork" class="card-body"></div>',
        build_project_selector_html() + '<div id="mynetwork" class="card-body"></div>',
    )
    html = html.replace(
        "</body>", build_dossier_html() + PROJECT_FOCUS_SCRIPT + SOURCE_INTERACTION + "</body>"
    )
    output_path.write_text(html, encoding="utf-8")
    return output_path.resolve()


if __name__ == "__main__":
    output = render_html()
    print(f"Wrote {output}")
    print(f"Nodes: {len(NODES)}")
    print(f"Relations: {len(RELATIONS)}")
