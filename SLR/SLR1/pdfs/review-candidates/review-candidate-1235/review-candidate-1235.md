---
source: null
title: "review-candidate-1235"
page_count: 10
converted_at: "2026-09-06T00:30:49Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# Digital Availability of Product Information for Collaborative Engineering of Spacecraft

</div>

Diana Peters $ ^{1} $ [0000-0002-5855-2989] , Philipp M. Fischer $ ^{2} $ [0000-0003-2918-5195] Philipp M. Schafer $ ^{1} $ [0000-0003-3931-6670] Kobkaew Opasjumruskit $ ^{1} $ [0000-0002-9206-6896] , and Andreas Gerndt $ ^{2} $ [0000-0002-0409-8573]

$ ^{1} $ Software Systems for Digitalization, German Aerospace Center (DLR), Mälzerstraße 3, 07745 Jena, Germany

{diana.peters,p.schaefer,kobkaew.opasjumruskit}@dlr.de $ ^{2} $ Software for Space Systems and Interactive Visualization, German Aerospace Center (DLR), Lilienthalplatz 7, 38108 Braunschweig, Germany {philipp.fischer,andreas.gerndt}@dlr.de

Abstract. In this paper, we introduce a system to collect product information from manufacturers and make it available in tools that are used for concurrent design of spacecraft. The planning of a spacecraft needs experts from different disciplines, like propulsion, power, and thermal. Since these different disciplines rely on each other there is a high need for communication between them, which is often realized by a ModelBased Systems Engineering (MBSE) process and corresponding tools. We show by comparison that the product information provided by manufacturers often does not match the information needed by MBSE tools on a syntactic or semantic level. The information from manufacturers is also currently not available in machine-readable formats. Afterwards, we present a prototype of a system that makes product information from manufacturers directly available in MBSE tools, in a machine-readable way.

Keywords: Model-Based Systems Engineering·Product Information· Spacecraft· Concurrent Engineering.

## 1 Introduction

Complex systems can not be realized by a single person or discipline due to the systems size and heterogeneity. The field of Systems Engineering (SE) aims to find solutions how to realize such systems successfully. One approach emerging in the SE field is Model-Based SE (MBSE), which "can be described as the formalized application of modeling principles, methods, languages, and tools to the entire lifecycle of large, complex, interdisciplinary, sociotechnical systems." [28]. By MBSE tool, we denote any software application that supports the development of a model by participants from different disciplines. The spacecraft components specified in an MBSE tool we denote as Equipment, while spacecraft components built or offered by manufacturers are denoted as products.

<!-- PDF_PAGE: 2 -->

The sources of information that engineers enter in MBSE tools for spacecraft design are PDF data sheets, spreadsheets, and engineers' implicit knowledge. Even if information is stored and transmitted digitally, it is often not machine-readable and especially not automatically available in an MBSE tool. Instead, a human has to take the information from a document to enter it into another system. This manual process is both slow and error-prone. Furthermore, every manufacturer uses a different format and a different vocabulary to represent information. Sometimes, not even PDF data sheets are available—Jahnke and Martelo found, that "From the 34 found suppliers of Cubesat related hardware, 62 % do publish detailed specifications and datasheets on their website." [22], which means that more than one third of the suppliers do not make this information available on their website.

As spacecraft are not anymore always one-of-a-kind products, CubeSats and small series of satellites become more common. According to Lange et al. [23], it becomes also more important to reuse information from former missions. This does not only include the MBSE models themselves, but also for example spacecraft component databases, where engineers could, additionally to the information from manufacturers, also add their own data, e.g. "template components" for different size categories of spacecraft.

Jahnke and Martelo also pointed out that " [...] the task during the CE sessions of the single domain expert is shifted from actual design of the sub-system and estimation of key-parameters towards the selection of the most suiting existing solution from e.g. a database and interface cross-check to other subsystems." [22]. So it becomes more important to find a product that fits certain requirements, including interface compatibility to other products, then to design a product from scratch.

In this paper we point out the problems with the current product information exchange between manufacturer and customer, collect requirements for a system to overcome these problems, and present a prototype system that makes product information available in the in-house MBSE tool of Virtual Satellite.

## 2 Related Work

Several approaches exist to make the whole MBSE process or phases of it possible or easier. This includes software applications, standards, and models of space systems.

The life cycle of a space system, as described by the European Cooperation for Space Standardization (ECSS), the European Space Agency (ESA), and the National Aeronautics and Space Administration (NASA), consists of phases 0 and A through F [2] [25], where in this paper we focus of the early planning phases 0 and A. Virtual Spacecraft Design (VSD) by ESA [9], Virtual Satellite by the German Aerospace Center (DLR) [14], RangeDB by Airbus Defense and Space [8], and Open Concurrent Design Tool (OCDT) [13] as well as CDP4 [1]

<!-- PDF_PAGE: 3 -->

by RHEA Group all aim to support an MBSE process following the suggestions made by ECSS in two Technical Memorandums, ECSS-E-TM-10-23A [12] and ECSS-E-TM-10-25A [10]. These tools have an internal model of the spacecraft and its subsystems. They all require manual input of Equipment data. They all support at least either the import or export of Excel spreadsheets. Though following similar ideas and guidelines, the parameters provided by these tools, and especially the names used for those parameters, vary. Table 1 shows an overview of the mass and structure parameters of most of the mentioned MBSE tools. We selected mass and structure parameters, because those are among the most relevant parameters for the early planning phases.

<table border="1"><tr><td>MBSE Tool</td><td>Virtual Satellite 4</td><td>VSD</td><td>OCDT/CDP4</td></tr><tr><td>Mass Parameters</td><td>massPerUnit(kg)</td><td>Weigth[sic!](gram)</td><td>mass(kg)
mass margin</td></tr><tr><td>Structure Parameters</td><td>radius(m)
shape
sizeX(m)
sizeY(m)
sizeZ(m)</td><td>Height(millimetre)
Length(millimetre)
Width(millimetre)</td><td>diameter(m)
shape
height(m)
length(m)
width(m)</td></tr></table>

<div align="center">

Table 1. Mass and structure parameters of equipment at different MBSE tools (units in braces). The parameter names for Virtual Satellite 4 and VSD were taken from installations of the tools. OCDT and CDP4 directly implement the ParameterType concept from ECSS-E-TM-10-25. At Virtual Satellite, the margin parameters are not defined at Equipment level, but above.

</div>

The aim of standards and formats is to provide a base for interfaces, so systems can exchange information directly, reliably, and without human interaction. For the small field of Spacecraft Onboard Interface Services the Consultative Committee for Space Data Systems (CCSDS) developed a standard for Electronic Data Sheets (EDS) [30]. EDS allow the exchange of information in a machine-readable format; no manual data transformation is necessary. Units, like "gram" or "inch" are defined in the EDS dictionary of terms, as are quantity kinds, like "massQK" or "lengthQK". But there is no definition that connects "gram" with "massQK" or that states that every physical component must have a mass.

ISO 10303 (STEP) [26] is an ISO standard for product manufacturing information, i.e., how a product is supposed to be produced, but it can be used for the whole life cycle of a product. Regarding space engineering, the technical report ECSS-E-TM-10-20A [11] lists what part of the STEP standard should be used for information exchange between which disciplines. This regards mostly computer-aided design (CAD) and physical structure contexts while other parts of the standard, like electronics, are neglected. A rather simple format to store 3D in-

<!-- PDF_PAGE: 4 -->

formation is STL (STereoLithographie, also Standard Triangulation/Tesselation Language) [29], which is supported by most CAD tools and used for additive manufacturing.

The specification of information exchange between manufacturers and MBSE tools does not only include technical protocols but also the information on which data is relevant in which context and what is its semantic meaning. Tailored modeling languages and tools are required to describe the semantic model of a spacecraft. Hennig et al. looked into existing languages and tools that can be used to describe Conceptual Data Models (CDMs). They conclude that none of them are ideal for this task [15]. In the same year, Ait-Ameur et al. introduced a special ontology modeling language (PLIB) for engineering in general [4]. Following their former analysis, Hennig et al. developed a conceptual data modeling language, SCDML [16], and also an ontology to describe space system design data [17]. Hoppe et al. also mentioned the benefits of ontologies and Web Ontology Language (OWL) together with the Eclipse Modeling Framework (EMF) for the MBSE process [19] [18] [21]. On top of that, they built the Semantic Engineering Modeling Framework (SEMF) [20]. MARVL CIP [6] is a platform that aims to support the information exchange between agencies and manufacturers across the whole life cycle of the spacecraft.

All these approaches target at the models in the MBSE process itself and sometimes at the question of how to use the same model across different phases or how to map between models of different phases. They should be taken into account to generate a "product data model" in a way that is compatible to the existing tools. But none of them can be used directly to model product data.

We looked into the previously mentioned EDS [30] and STEP [26] as potential carriers of product data. Both address the exchange of data sheet information, but they either focus on a small topic (EDS) or are used only for a certain area in practice (STEP—for 3D information). So far, no standards or practices exist to cover all relevant information for the data exchange between supplier and customer in the space sector. However, EDS and/or STEP could become a starting point for the development of a data exchange format for product data, especially with the planned new definition of the EDS standard [27].

PDF data sheets are meant to describe a product technically but there is no standard regarding the syntax or semantic of this description. There are several approaches to extract (semantic) information from data sheets, e.g. by [7], [3], [5], and [24], but we do not know of an accessible tool that performs that task reliably.

## 3 Methods

As CubeSats become more common and products for those are already offered in online shops, we compared the information offered by such shops with the information required by the above mentioned MBSE tools. As with the MBSE tools, we focused on parameters for mass and structure. Since the outer dimensions of CubeSats are restricted by the form factor (1U, 2U, ...), we expected

<!-- PDF_PAGE: 5 -->

to find similar presentations of the structure parameters between the different shops. Besides the parameter names we were also interested in the formats the information were offered in.

To use product information directly in MBSE tools, we see the following requirements for an exchange format:

- machine readable - so humans do not have to enter or copy information manually

- uniform / standardized - so no transformations between different formats are necessary

- automatically comparable - so search for a product that fits certain requirements becomes easier

-all values for one product from a single source (optional) - so it is not necessary to request multiple sources for the information about a single product

The results of our search and the comparison with parameters at MBSE tools are discussed in the next section.

## 4 Results

For each of the six CubeSat shops, the formats in which information was presented are summarized in Table 2. We were looking for information in tables (or bullet points in the format <key>:<value>), PDF data sheets, and STEP files. Shop B offered information mostly in free text $ ^{4} $ , little in tables, and PDF or STEP files only upon request. Shop E offered parameters only in free text or in text bullet points like "Mass is ca. XYg"; Shop D offered only very few bullet points in the format <key>:<value> and STEP files only after login. None of the shops offered an API (application programming interface) to read the data—we asked all of them via e-mail. One of the shops is working on an API to request the PDF data sheets, but no machine-readable data.

<table border="1"><tr><td>Shop</td><td>A</td><td>B</td><td>C</td><td>D</td><td>E</td><td>F</td></tr><tr><td>table on website</td><td>X</td><td>(X)</td><td>X</td><td>X</td><td>-</td><td>(X)</td></tr><tr><td>PDF data sheet</td><td>X</td><td>-</td><td>X</td><td>X</td><td>X</td><td>X</td></tr><tr><td>STEP file</td><td>X</td><td>-</td><td>-</td><td>X</td><td>X</td><td>(X)</td></tr></table>

<div align="center">

Table 2. Formats of Information Presentation at CubeSat Shops

</div>

For each shop, we picked the first search result for "solar panel" to compare the parameters presented directly by the shops (not in the data sheets of the manufacturers).

The mass and structure parameters of each shop are compared in Table 3; Shops B, E, and F did not provide any mass or structure related parameters in a table or table-like format.

<!-- PDF_PAGE: 6 -->

<table border="1"><tr><td>Shop</td><td>A</td><td>C</td><td>D</td></tr><tr><td>Mass
Parameters</td><td>Mass</td><td>Very low solar cell mass
Side solar panel weight</td><td>Mass (exact mass
depends on configuration)</td></tr><tr><td>Structure
Parameters</td><td>Nominal thickness
Dimensions(PCB
+Solar Cells)</td><td>Solar cells thickness
PCB Thickness</td><td>Panel Thickness</td></tr></table>

<div align="center">

Table 3. Mass and structure parameters at CubeSat shops. Both parameters in Shop D were followed by lists with the actual values.

</div>

Even though our sample of CubeSat shops is small, it becomes obvious that neither between the different shops nor between the shops and MBSE tools the same parameter names are used. "Mass" and "thickness" are reoccurring names, but the additional texts at the shops (see Table 3) make it clear that the semantics of those names vary (e.g., "thickness" sometimes refers to the cells only, sometimes to cells plus PCB).

## 5 Prototype: Product Information in MBSE Tool

We built a small prototype to make product information available in MBSE tools, including a plugin for the DLR in-house MBSE tool Virtual Satellite. Figure 1 shows an overview of the architecture.

The main component is the Product Data Hub (PDH) that consists of a crawler and a database. The database stores product information independently of manufacturers; this bridges temporary unavailability of single shops and provides a single access point for the MBSE tools. The database is filled by a crawler that request the manufacturers regularly and updates or adds entries. Here, we need only one crawler because all manufacturers provide their data in the same format. To request data from actual manufacturers (given they provide an API) would require different crawlers since currently there is no uniform data exchange format all manufacturers share.

The second component of the prototype is a manually created mockup of manufacturers that provides product information in a machine-readable way via http in a JSON (JavaScript Object Notation, a language-independent data format)) format. The data format is the same for all manufacturers.

The last component of the prototype is a plugin for Virtual Satellite that enables the users to do three different things:

1. Add an Equipment with the values of a product in the PDH

2. Update an Equipment with values from a product in the PDH

3. Save an Equipment as product to the PDH

To add a new Equipment with the values of a product in the PDH, the user browses a product list provided by the plugin and selects one with fitting

<!-- PDF_PAGE: 7 -->


![figure_001.png](figure_001.png)



Software System: one standalone software application

Container: data storage with an interface to store, update, delete, and search data

Person: a human being

<div align="center">

Fig.1. Architecture of Product Data System

</div>

values (see Figure 2). The new Equipment can then be used as any Equipment in Virtual Satellite—changes at the Equipment have no effect on the product from which the Equipment was created.

The update function is rather a search function: The user specifies an Equipment and the plugin looks for products in the PDH that fit this specification within a range of uncertainty for all values. The range of uncertainty can be defined by the user. The user selects one product that fits the pre-specified Equipment and all values from the product are taken over to the Equipment.

The last function is to add an Equipment as product to the PDH. That way the user can for example define templates (e.g. for a "small battery") for which no real product from a manufacturer exists. This function can also be used to add values for products described by PDF data sheets manually.

<!-- PDF_PAGE: 8 -->


![figure_002.png](figure_002.png)



<div align="center">

Fig. 2. Screenshot of Product Selection Dialog in Virtual Satellite

</div>

## 6 Conclusion and Outlook

The comparison of parameters at MBSE tools and CubeSat shops shows that there is neither a set of parameters that is supported by everyone nor a common understanding of the semantics of the provided parameters.

Our prototype shows how product information can be exchanged between manufacturers and MBSE tools in principle. It also shows that for machine readable exchange of product information between manufacturers and MBSE tools a standardized format is needed that includes also a semantic description for each parameter. Our prototype only worked because we had control over all parts—to expand the concept, every party needs a common understanding of the exchanged information. We think that over the next years it should be possible to reach such a common understanding within the space industry, at least for parts of the information to exchange. The attempt at ESA to find a new and broader standard for EDS goes in that direction.

In the future we want to look more into semantic descriptions of space products and also in different phases of the spacecraft life cycle, since so far our focus was on the early planning phase.

<!-- PDF_PAGE: 9 -->

## References

1. Designing the Future of Your Complex Engineering Projects. https:// www.rheagroup.com/cdp, accessed: 2018-05-29

2. Space project management - Project planning and implementation (2009)

3. Agrawal, R., Ho, H., Jacquenet, F., Jacquenet, M.: Mining Information Extraction Rules from Datasheets Without Linguistic Parsing. In: Ali, M., Esposito, F. (eds.) Innovations in Applied Artificial Intelligence. pp. 510-520. Springer Berlin Heidelberg, Berlin, Heidelberg (2005)

4. Ait-Ameur, Y., Baron, M., Bellatreche, L., Jean, S., Sardet, E.: Ontologies in engineering: the OntoDB/OntoQL platform. Soft Computing 21(2), 369-389 (Mar 2015). https://doi.org/10.1007/s00500-015-1633-5

5. Barkschat, K.: Semantic Information Extraction on Domain Specific Data Sheets. In: Presutti, V., d'Amato, C., Gandon, F., d'Aquin, M., Staab, S., Tordai, A. (eds.) The Semantic Web: Trends and Challenges. pp. 864-873. Springer International Publishing, Cham (2014)

6. Bieze, M.: MARVL - Model-based requirements-verification lifecycle. Software Systems Division (TEC-SW) and Data Systems Division (TEC-ED) Final Presentation Day - May 2018

7. Castellanos, M., Chen, Q., Dayal, U., Hsu, M., Lemon, M., Siegel, P., Stinger, J.: Component Advisor: A tool for automatically extracting electronic component data from Web datasheets. on Reuse of Web-based Information p. 31 (1998)

8. Eisenmann, H., Cazenave, C.: Evolving a classic SRDB into an engineering database. In: 6th International Workshop on Systems and Concurrent Engineering for Space Applications (SECESA). pp. 8-10 (2014)

9. Eisenmann, H., Basso, V., Fuchs, J., De Wilde, D.: ESA virtual spacecraft design. In: Proceedings of the 4th International Workshop on System & Concurrent Engineering for Space Applications (SECESA) (2010)

10. ESA-ESTEC: Space engineering - engineering design model data exchange (ecss-e-tm-10-25a). techreport ECSS-E-TM-E-10-25A, ECSS (2010)

11. ESA-ESTEC: Space engineering - product data exchange (ecss-e-tm-10-20a). techreport ECSS-E-TM-E-10-20A, ECSS (2010)

12. ESA-ESTEC: Space engineering - space system data repository (ecss-e-tm-10-23a). techreport ECSS-E-TM-10-23A, ECSS (2011)

13. Ferreira, I., de Koning, H.P., Gerene, S., Pickering, A., Vennekens, J., Beyer, F.: Open Concurrent Design Tool: ESA Community Open Source Ready to Go! 6th International Workshop on System & Concurrent Engineering for Space Applications (SECESA) (Oct 2014)

14. Fischer, P.M., Lüdtke, D., Lange, C., Roshani, F.C., Dannemann, F., Gerndt, A.: Implementing Model-Based System Engineering for the Whole Lifecycle of a Spacecraft. CEAS Space Journal 9(3), 351-365 (Jul 2017). https://doi.org/10.1007/s12567-017-0166-4

15. Hennig, C., Eisenmann, H., Viehl, A., Bringmann, O.: On languages for conceptual data modeling in multi-disciplinary space systems engineering. In: 2015 3rd International Conference on Model-Driven Engineering and Software Development (MODELSWARD). pp. 384-393 (Feb 2015)

16. Hennig, C., Hoppe, T., Eisenmann, H., Viehl, A., Bringmann, O.: SCDML: A language for Conceptual Data Modeling in Model-based Systems Engineering. In: 2016 4th International Conference on Model-Driven Engineering and Software Development (MODELSWARD). pp. 184-192 (Feb 2016)

<!-- PDF_PAGE: 10 -->

17. Hennig, C., Viehl, A., Kämpgen, B., Eisenmann, H.: Ontology-based design of space systems. In: Lecture Notes in Computer Science, pp. 308-324. Springer International Publishing (2016). https://doi.org/10.1007/978-3-319-46547-0_29

18. Hoppe, T., Eisenmann, H., Viehl, A., Bringmann, O.: Digital Space Systems Engineering through Semantic Data Models. In: 2017 IEEE International Conference on Software Architecture (ICSA). IEEE (Apr 2017). https://doi.org/10.1109/icsa.2017.35

19. Hoppe, T., Eisenmann, H., Viehl, A., Bringmann, O.: Guided systems engineering by profiled ontologies. In: 2017 IEEE International Systems Engineering Symposium (ISSE). IEEE (Oct 2017). https://doi.org/10.1109/syseng.2017.8088255

20. Hoppe, T., Eisenmann, H., Viehl, A., Bringmann, O.: SEMF - the semantic engineering modeling framework - bringing semantics into the eclipse modeling framework for space systems engineering. In: Proceedings of the 5th International Conference on Model-Driven Engineering and Software Development. SCITEPRESS - Science and Technology Publications (2017). https://doi.org/10.5220/0006118702930301

21. Hoppe, T., Eisenmann, H., Viehl, A., Bringmann, O.: Shifting from data handling to knowledge engineering in aerospace industry. In: 2017 IEEE International Systems Engineering Symposium (ISSE). IEEE (oct 2017). https://doi.org/10.1109/syseng.2017.8088312

22. Jahnke, S.S., Martelo, A.: Special characteristics of concurrent engineering studies dealing with cubesatmissions and their impact on the CE process. In: 7th International Systems & Concurrent Engineering for Space Applications Conference (SECESA) (2016)

23. Lange, C., Grundmann, J.T., Kretzenbacher, M., Fischer, P.M.: Systematic reuse and platforming: Application examples for enhancing reuse with model-based systems engineering methods in space systems development. Concurrent Engineering 26(1), 77-92 (2018)

24. Murdaca, F., Berquand, A., Kumar, K., Riccardi, A., Soares, T., Gerené, S., Brauer, N.: Knowledge-based information extraction from datasheets of space parts. In: 8th International Systems & Concurrent Engineering for Space Applications Conference (September 2018), https://strathprints.strath.ac.uk/65764/

25. NASA: NASA Systems Engineering Handbook. US National Aeronautics and Space Admin (2008)

26. Pratt, M.J.: Introduction to ISO 10303—the STEP standard for product data exchange. Journal of Computing and Information Science in Engineering 1(1), 102 (2001). https://doi.org/10.1115/1.1354995

27. Prochazka, M.: Electronic Data Sheets at ESA: Current Status and Roadmap. Flight Software Workshop 2017 (Dec 2017)

28. Ramos, A.L., Ferreira, J.V., Barcelo, J.: Model-Based Systems Engineering: An Emerging Approach for Modern Systems. IEEE Transactions on Systems, Man, and Cybernetics, Part C (Applications and Reviews) 42(1), 101-111 (2012). https://doi.org/10.1109/tsmcc.2011.2106495

29. Roscoe, L.E.: StereoLithography Interface Specification. Tech. rep., 3D Systems, Inc. (Oct 1989)

30. (SANA), S.A.N.A.: Spacecraft Onboard Interface Services Electronic Data Sheets and Dictionary of Terms. https://sanaregistry.org/r/sois (May 2017), accessed: 2018-02-19