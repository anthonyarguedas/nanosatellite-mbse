---
source_url: https://cdn.standards.iteh.ai/samples/60496/10d91b71b4ef4c49acd1b065b3bcecb0/ISO-17770-2017.pdf
canonical_url: https://www.iso.org/standard/60496.html
title: Space systems — Cube satellites (CubeSats)
edition: First edition, 2017-06. Confirmed 2024. Published and current at retrieval, stage 90.92 to be revised.
revision: First edition, 2017-06. Confirmed 2024. Published and current at retrieval, stage 90.92 to be revised.
availability: preview
status_label: PREVIEW ONLY
document_type: standard preview
page_count: 9
source_sha256: 03813e98d74fc1decb517f6ce22bba14f28ffdde2394384c3048290c5a2c2d33
source: https://cdn.standards.iteh.ai/samples/60496/10d91b71b4ef4c49acd1b065b3bcecb0/ISO-17770-2017.pdf
converted_at: '2026-10-09T01:16:54.699066+00:00'
method: Z.ai GLM-OCR using the supplied pdf_to_markdown.py, standalone-page OCR in private 20-page chunks, then ordered reassembly
  with local crops; a private wrapper retains verified blank pages rejected by the service; supplemental direct source-render
  crops are retained where recorded
source_note: PREVIEW ONLY. All nine physical pages of the archived preview are converted. This is not the complete ISO 17770:2017
  standard.
limitations:
- Machine OCR is not lossless. Characters, clause numbering, reading order, tables, equations and diagram details may contain
  recognition or layout errors; consult the source PDF for authoritative use.
- OCR-generated headings, HTML tables and equations are retained without editorial reconstruction. Page-spanning content remains
  page-local fragments.
- Detected logos, page headers and footers are omitted by the supplied converter. Content images are kept as local crops,
  with chunk prefixes to prevent filename collisions.
- Validation establishes source integrity, physical-page coverage and image availability, not complete semantic equivalence,
  standard adoption or compliance.
verified_blank_pages_retained: []
supplemental_source_crops: []
---

> PREVIEW ONLY. All nine physical pages of the archived preview are converted. This is not the complete ISO 17770:2017 standard.

<!-- PDF_PAGE: 1 -->

INTERNATIONAL STANDARD

ISO 17770

First edition

2017-06

<div align="center">

# Space systems — Cube satellites (CubeSats)

</div>

Systèmes spatiaux — Satellites cubiques (CubeSats)

iTeh STANDARD PREVIEW (standards.iteh.ai)

ISO 17770:2017 https://standards.iteh.ai/catalog/standards/sist/e2a7d1f6-f563-413e-a6f9- 4701f0f23928/iso-17770-2017





<!-- PDF_PAGE: 2 -->

ISO 17770:2017(E)

<div align="center">

# iTeh STANDARD PREVIEW (standards.iteh.ai)

</div>

ISO 17770:2017 https://standards.iteh.ai/catalog/standards/sist/e2a7d1f6-f563-413e-a6f9- 4701f0f23928/iso-17770-2017


![figure_001.png](iso-17770-2017-preview_images/p0001_figure_001.png)



## COPYRIGHT PROTECTED DOCUMENT

$ \textcircled{c} $ ISO 2017, Published in Switzerland

All rights reserved. Unless otherwise specified, no part of this publication may be reproduced or utilized otherwise in any form or by any means, electronic or mechanical, including photocopying, or posting on the internet or an intranet, without prior written permission. Permission can be requested from either ISO at the address below or ISO's member body in the country of the requester.

ISO copyright office

Ch. de Blandonnet 8 • CP 401

CH-1214 Vernier, Geneva, Switzerland

Tel. +41 22 749 01 11

Fax +41 22 749 09 47

copyright@iso.org

www.iso.org

<!-- PDF_PAGE: 3 -->

## Contents

Foreword iv

Introduction v

1 Scope 1

2 Normative references 1

3 Terms and definitions 1

4 Abbreviated terms 2

5 CubeSat requirements 2

5.1 General requirements 2

5.2 CubeSat mechanical requirements: External dimensions 3

5.3 CubeSat mechanical requirements: Mass 5

5.4 CubeSat mechanical requirements: Materials 5

5.5 Electrical requirements 6

5.6 Operational requirements 6

6 Interface to the launch vehicle: The CubeSat Deployer 7

6.1 Enclosure 7

6.2 Interface 7

6.3 Mass 7

6.4 Modularity 7

6.5 Parts attachment 7

6.6 Release from the Deployer 7

7 CubeSat and Deployer assurance/quality verification 7

7.1 General 7

7.2 Random vibration 8

7.3 Thermal/Vacuum bakeout 8

7.4 Shock 8

7.5 Visual inspection 8

Bibliography 9

<!-- PDF_PAGE: 4 -->

## Foreword

ISO (the International Organization for Standardization) is a worldwide federation of national standards bodies (ISO member bodies). The work of preparing International Standards is normally carried out through ISO technical committees. Each member body interested in a subject for which a technical committee has been established has the right to be represented on that committee. International organizations, governmental and non-governmental, in liaison with ISO, also take part in the work. ISO collaborates closely with the International Electrotechnical Commission (IEC) on all matters of electrotechnical standardization.

The procedures used to develop this document and those intended for its further maintenance are described in the ISO/IEC Directives, Part 1. In particular the different approval criteria needed for the different types of ISO documents should be noted. This document was drafted in accordance with the editorial rules of the ISO/IEC Directives, Part 2 (see www.iso.org/directives).

Attention is drawn to the possibility that some of the elements of this document may be the subject of patent rights. ISO shall not be held responsible for identifying any or all such patent rights. Details of any patent rights identified during the development of the document will be in the Introduction and/or on the ISO list of patent declarations received (see www.iso.org/patents).

Any trade name used in this document is information given for the convenience of users and does not constitute an endorsement.

For an explanation on the voluntary nature of standards, the meaning of ISO specific terms and expressions related to conformity assessment, as well as information about ISO's adherence to the World Trade Organization (WTO) principles in the Technical Barriers to Trade (TBT) see the following URL: www.iso.org/iso/foreword.html.

This document was prepared by Technical Committee ISO/TC 20, Aircraft and space vehicles Subcommittee SC 14, Space systems and operations.

<!-- PDF_PAGE: 5 -->

## Introduction

Recent years have seen an increase in the number of student satellites developed at universities around the world. To date, most university satellites require several years to develop and significant financial resources, making them prohibitive for small programs. New technological developments in small low-power electronics make smaller, lower-cost satellites feasible.

The CubeSat program has developed a picosatellite standard that significantly reduces the cost and development time of picosatellites with a specific form factor. In addition, CubeSats can serve as platforms for in-space experimentation, as well as a means of space-qualifying future small-satellite hardware.

The CubeSat Standard is an evolution of the picosatellites developed for Stanford's OPAL mission. CubeSats are constrained to a 100 mm cube (not including deployment interface rails) with a mass of one kilogram or less. Led by Stanford University's Space Systems Development Lab (SSDL), the CubeSat project is developed jointly by universities and industry worldwide. Within this international community CubeSat developments at the California Polytechnic State University (CalPoly) have been twofold: first, develop the standardized launcher-interface/deployer mechanism for CubeSats, and second, demonstrate the feasibility of developing a working CubeSat using low-cost, commercial off-the-shelf components. The project involves a multidisciplinary team of software, aerospace, manufacturing, electrical, and mechanical engineering undergraduate students.

In recent years, more sophisticated capabilities have been demonstrated in CubeSats by major space corporations and major space customers. CubeSat concepts for inclusion in Mars exploration are in development. Entire companies have been established to solely support the global CubeSat marketplace.

(standards.iteh.ai)

ISO 17770:2017 https://standards.iteh.ai/catalog/standards/sist/e2a7d1f6-f563-413e-a6f9- 4701f0f23928/iso-17770-2017

<!-- PDF_PAGE: 6 -->

<div align="center">

# iTeh STANDARD PREVIEW (standards.iteh.ai)

</div>

ISO 17770:2017 https://standards.iteh.ai/catalog/standards/sist/e2a7d1f6-f563-413e-a6f9- 4701f0f23928/iso-17770-2017

<!-- PDF_PAGE: 7 -->

## Space systems — Cube satellites (CubeSats)

## 1 Scope

This document addresses CubeSats, CubeSat Deployer and related verification of assurance/quality terms and metrics.

This document defines a unique class of picosatellite, the CubeSat. CubeSats are ideal as space development projects for universities around the world. In addition to their significant role in educating space scientists and engineers, CubeSats provide a low-cost platform for testing and space qualification of the next generation of small payloads in space. A key component of the project is the development of a standard CubeSat Deployer.

This Deployer is capable of releasing a number of CubeSats as secondary payloads on a wide range of launchers. The standard Deployer requires all CubeSats to conform to common physical requirements, and share a standard Deployer interface. CubeSat development time and cost can be significantly reduced by the development of standards that are shared by a large number of spacecraft.

Normative control of the CubeSat design, qualification and acceptance testing is generally applied from other small satellite specific standards with the exception of CubeSat/Deployer launch environment test.

## iTeh STANDARD PREVIEW

## 2 Normative references

## (standards.iteh.ai)

The following documents are referred to in the text in such a way that some or all of their content constitutes requirements of this document. For dated references, only the edition cited applies. For undated references, the latest edition of the referenced document (including any amendments) applies.

ISO 14620-1, Space systems — Safety requirements — Part 1: System safety

ISO 24113, Space systems — Space debris mitigation requirements

## 3 Terms and definitions

## 3.1

## CubeSat

picosatellite measuring 100 mm cubic and weighing 1,33 kg or less

Note 1 to entry: Variations on the basic form factor are also considered CubeSats.

## 3.2

## deployer

encloses CubeSats within a confined volume with a lid at one side that closes the ejection port during the launch phase

Note 1 to entry: It is capable of carrying one or multiple standard CubeSats and serves as the interface between the CubeSats and launch vehicle.

## 3.3

## P-POD

## Poly Picosatellite Orbital Deployer

example of a CubeSat Deployer

Note 1 to entry: In recognition of the original design by the California Polytechnic State University - Cal Poly.

Note 2 to entry: The P-POD is Cal Poly's standardized CubeSat deployment system. It is capable of carrying three standard CubeSats.

<!-- PDF_PAGE: 8 -->

## 3.4

single CubeSat

single 100 mm CubeSat

Note 1 to entry: Singe CubeSat is also described as "1U".

## 3.5

triple CubeSat

common three CubeSat configuration, where it is three CubeSats long connected along the longitudinal axis

Note 1 to entry: Triple CubeSat is also described as "3U".

## 4 Abbreviated terms

CVCM Collected Volatile Condensable Mass

FCC Federal Communication Commission

IARU International Amateur Radio Union

LV Launch Vehicle

P/N Part Number

P-POD Poly Picosatellite Orbital Deployer iTeh STANDARD PREVIEW

RBF Remove Before Flight （standards.iteh.ai）

RF Radio Frequency

ISO 17770:2017

STD Standard https://standards.iteh.ai/catalog/standards/sist/e2a7d1f6-f563-413e-a6f9- 4701f9f23028/ico_17770_2017

STD Standard

4701f0f23928/iso-17770-2017

TML Total Mass Loss

U Used with a number [e.g. 1U (see 3.4), 3U (see 3.5)] to denote CubeSat units

## 5 CubeSat requirements

## 5.1 General requirements

5. 1.1 All parts shall remain attached to the CubeSat during the launch phase, ejection, and operation to ensure safety (see ISO 14620-1). No additional space debris shall be created (see ISO 24113).

5. 1.2 Pyrotechnics shall not be permitted.

5. 1.3 Propulsion systems shall have at least three inhibits to activation.

5. 1.4 Total stored chemical energy shall not exceed 100 Watt-hours.

5. 1.5 CubeSat materials shall satisfy the following out-gassing criterion to prevent contamination of other spacecraft during integration, testing and launch.

NOTE A list of NASA approved out-gassing materials can be found at http://outgassing.nasa.gov.

5. 1.5.1 Total Mass Loss (TML) shall be <1,0 %.

<!-- PDF_PAGE: 9 -->

5. 1.5.2 Collected Volatile Condensable Material (CVCM) shall be <0,1 %.

5. 1.6 The CubeSat shall be designed to accommodate ascent venting per ventable volume/area <50 800 mm (Note: derived from 2000 inches).

## 5.2 CubeSat mechanical requirements: External dimensions

5. 2.1 The CubeSat shall use the coordinate system as defined in Figure 1 for single CubeSat, and Figure 2 for triple CubeSat.

5. 2.2 The Z-face of the CubeSat will be inserted first into the Deployer.

5. 2.3 The single CubeSat configuration and physical dimensions shall be per Figure 1, the triple CubeSat per Figure 2.

5. 2.4 The CubeSat shall be 100,0 mm $ \pm $ 0,1 mm wide (X and Y dimensions per Figure 1).

5. 2.5 A single CubeSat shall be 113,5 mm $ \pm $ 0,1 mm tall (Z dimension per Figure 1).

5. 2.5.1 A triple CubeSat shall be 340,5 mm $ \pm $ 0,3 mm tall (Z dimension per Figure 2).

5. 2.6 All components shall not exceed 6,5 mm normal to the surface of the 100,0 mm cube.

5. 2.7 Exterior CubeSat components shall not contact the interior surface of the Deployer other than the designated CubeSat rails.

ISO 17770:2017

5. 2.8 Deployable items shall be constrained by the CubeSat. The Deployer rails and walls shall not be used to constrain deployable items. 4701f0f23928/iso-17770-2017

5. 2.9 The rails shall have a minimum width of 8,5 mm.

5. 2.10 The rails shall have a surface roughness less than 1,6 $ \mu\mathrm{m} $ .
