---
source: null
title: "citation-candidate-0815"
page_count: 14
converted_at: "2026-09-08T15:00:55Z"
---

<!-- PDF_PAGE: 1 -->





WILEY

<div align="center">

# Driving digital engineering integration and interoperability through semantic integration of models with ontologies

</div>

Daniel Dunbar $ ^{1} $ Thomas Hagedorn $ ^{1} $ Mark Blackburn $ ^{1} $ John Dzielski $ ^{1} $ Steven Hespelt $ ^{1} $ Benjamin Kruse $ ^{2} $ Dinesh Verma $ ^{1} $ Zhongyuan Yu $ ^{1} $

$ ^{1} $Systems Engineering Research Center (SERC), Stevens Institute of Technology, Hoboken, New Jersey, USA

$ ^{2} $ e:fs TechHub GmbH from Gaimersheim, Germany

## Correspondence

Correspondence Daniel Dunbar, Systems Engineering Research Center (SERC), Stevens Institute of Technology, Hoboken, NJ, USA. Email: ddunbar1@stevens.edu

Funding information Systems Engineering Research Center (SERC), Grant/Award Numbers: HQ003413D0004, W15QKN18D0040; University Affiliated Research Center (UARC); Stevens Institute of Technology

## Abstract

Engineered solutions are becoming more complex and multi-disciplinary in nature. This evolution requires new techniques to enhance design and analysis tasks that incorporate data integration and interoperability across various engineering tool suites spanning multiple domains at different abstraction levels. Semantic web technologies (SWT) offer data integration and interoperability benefits as well as other opportunities to enhance reasoning across knowledge represented in multiple disparate models. This paper introduces the digital engineering framework for integration and interoperability (DEFII) for incorporating SWT into engineering design and analysis tasks. The framework includes three notional interfaces for interacting with ontology-aligned data. It also introduces a novel model interface specification diagram (MISD) that provides a tool-agnostic model representation enabled by SWT that exposes data stored for use by external users through standards-based interfaces. Use of the framework results in a tool-agnostic authoritative source of truth spanning the entire project, system, or mission.

## KEYWORDS

digital engineering, SEE24 model-based systems engineering (MBSE), SEE26 modeling and simulation, SEE29 other systems engineering enablers, semantic web and ontologies

## 1 INTRODUCTION

Increasing complexity in the design and development of modern cyber-physical systems requires a high level of collaboration across disciplines. To maintain high standards of quality and reasonable time frames, computer assisted collaboration is increasingly necessary. Data integration that enables cross-domain reasoning and collaboration at the model level is key to enabling and enhancing computer assisted engineering and design across multiple abstraction levels, domains, and disciplines.

Digital engineering (DE) is an umbrella domain that seeks to integrate the model based systems engineering (MBSE) and domain specific model based engineering (MBE) domains. Defense Acquisition University defines DE as "an integrated digital approach that uses authoritative sources of systems" data and models as a continuum across disciplines to support lifecycle activities from concept through disposal." In order to do this, it relies heavily on the concepts of authoritative source of truth (AST) and digital thread (DT). The AST serves as a central data registry where all tools associated with the project must go to access system data. Thus, multiple tools can access

<!-- PDF_PAGE: 2 -->

the same datapoint and have certainty that they are working from the same reference baseline. Researchers have used various structures to form the AST, including system models, $ ^{2} $ databases, $ ^{3} $ and various graph data structures. $ ^{4-7} $ The DT digitally connects different models used in system design and analysis across domain and software boundaries. $ ^{8} $ This requires a robust data integration plan to enable the needed model level connections.

Integration of various models is traditionally done through tool-to-tool integration. Custom interfaces designed to connect tool A to tool B have been used for years to accommodate data integration needs in cross domain analysis. However, tool-to-tool integration is brittle in nature, $ ^{4} $ and the number of tool-to-tool integrations needed to fully connect the design and analysis system grows exponentially as tools are added. $ ^{9} $ In other words, tool-to-tool integration is prone to error, difficult to maintain, and hard to scale.

A database approach, which allows for a central hub of data, that is, accessed by multiple tools, is a better fit as a DE AST. Particularly, a graph data structure that captures system specific data and connects it to domain knowledge presents an interesting foundation for a potential solution. Graph data structures capture relationships between nodes and can take advantage of both relational and graph based algorithms. $ ^{10} $

Computer based ontologies and associated technologies collectively known as semantic web technologies (SWT) provide a technological base to build out a graph data structure as an AST in the DE context. SWT comprises a suite of technologies to tag graph data with semantically meaningful labels, to store and retrieve that data, and to automatically reason upon it based upon the logical framework underpinning the tags. Ontologies provide the markup schema used to tag the graph and a logical formalization in the form of a taxonomy of terms, relations, and machine-readable logical expressions using them. Data repositories called triplestores provide storage and endpoints for semantic queries, which are used to retrieve and interact with graph data. Automated reasoners afford the ability to deduce new relations within tagged data based upon logical inferencing, and to enhance query results with that inferred information.

While graph data structures have been used in DE and systems engineering domains with positive results, $ ^{4-7} $ to date there is not a robust framework for guiding engineers to integrate SWT into a DE environment.

This paper presents the digital engineering framework for integration and interoperability (DEFII), an ontology-based framework for solving integration and interoperability concerns inherent to the DE domain space. It uses a graph data structure as the DE AST and establishes three notional interfaces to allow interaction with the ontology aligned data: the Direct Interface, the Mapping Interface, and the Specified Model Interface. Additionally, the paper introduces a novel model interface specification diagram (MISD) to specify ontologically relevant interfaces without deep understanding of the underlying ontologies.

A successful framework for integrating SWT into DE must move beyond theory and enable practice that realizes these benefits. For a framework to reach that threshold, this paper holds that it must:

## Significance and Practitioner Points

This paper develops the use of ontologies and semantic web technologies for Digital Engineering by introducing the digital engineering framework for integration and interoperability (DEFII). The DEFII framework establishes three notional interfaces for populating, interacting with, and enhancing ontology-aligned data. It provides the ability to establish tool-agnostic interfaces for data contained in a system design with the novel model interface specification diagram (MISD). The MISD uses the SysML language as a descriptive model of the analysis system and co-mingles this with the system model, giving modelers the ability to specify interfaces used for analysis in a context dependent manner. This allows for models to be defined to include data from disparate sources within the system and exposed in a way that gives external tools, from industry established design and analysis software to in-house visualization tools, access to an established, authoritative source of truth. This approach to interoperability allows practitioners to continue using tools that suit their needs and preferences while taking advantage of enhanced interoperability between disciplines and creating a knowledge base that can be expanded in the future to allow for further integration of artificial and augmented intelligence applications.

1. Provide clear avenues for mapping data from engineering design and analysis models to an ontology-aligned data store.

2. Allow access to contained data in a flexible, tool-agnostic manner.

3. Allow for the transformation and enhancement of data using various semantic technologies.

These three success criteria address current data integration needs in DE and prepare for future capability by taking advantage of an ontology-based AST that provides a holistic view of the systems under design. This paper shows the DEFII framework satisfies all three criteria.

Section 2 looks at related work and identifies a gap identified in existing literature the DEFII framework fills. Section 3 details the DEFII framework and related interface types. Section 4 introduces a case study from the Information Technology (IT) cyber security domain that uses DEFII to produce results that can be analyzed. It then instantiates the notional interfaces to address the specific use case and describes the results of usage of the DEFII framework. Section 5 analyzes the results to validate DEFII against the success criteria defined above, discusses limitations of the research and opportunities to extend the research, and interprets the results for the larger DE context. Section 6 provides a conclusion to the paper.

<!-- PDF_PAGE: 3 -->

## 2 | RELATED WORK

Ontologies have long been proposed as a medium for knowledge representation in engineering. Theoretical benefits include the potential for reuse, automated inferencing, and knowledge sharing. $ ^{11-13} $ These theoretical benefits have led to research on how to build solutions that make use of SWT to enhance engineering efforts. A first step in this research is the use of SWT directly.

A significant body of past research has focused on demonstrating engineering capabilities that are enabled by SWT. Most prior work focuses narrowly on either pure ontology definition for the engineering domain or the capabilities afforded by ontology aligned data. Coelho et al. use direct invocation of the SWT stack in their proposal of the "Data-Ontology-Rule footing" as a mechanism for building ontology integration into the design and analysis workflow. Mechanisms for pulling system data into ontologies beyond direct manipulation of the ontological data using semantic tools are not discussed. $ ^{14} $ Eddy et al. describe a framework for design alternative development based on the use of modular ontologies of the engineering design domain and various reasoning capabilities. $ ^{15} $ Similarly, Hagedorn et al. use SWT to enable design and ideation in the Additive Manufacturing domain $ ^{16} $ based upon semantic querying and rule-based inferences. Daun et al. use ontologies to describe contexts in concurrent engineering. $ ^{17} $ While these works demonstrate possible benefits of SWT in engineering context, they lack defined techniques for populating ontology-aligned data instances and interacting with engineering models or tools. Thus the benefits demonstrated in these and similar works remain largely hypothetical. $ ^{6} $

Several works have attempted to bridge this gap between tools and SWT using a process of data mapping. Termed "data ingestion" by commercial tools, $ ^{18} $ mapping is a process by which data from outside the SWT stack is parsed into SWT formats and aligned to ontology-tagged graph patterns. El Kadiri and Kiritsis discuss mapping for ontology use in the Product Lifecycle Management (PLM) domain. $ ^{19} $ Several other publications discuss mapping both specifically and generically in reference to systems engineering domain. $ ^{10,18,20-23} $ Mapping tool and model information to ontology-aligned data allows the use of SWT in more realistic engineering workflows using real or realistic data. Examples of this include NASA's Jet Propulsion Laboratory (JPL) use of Computer Aided Engineering for Spacecraft Architectures Tool Suite (CAESAR) to establish logical consistency and build reports using custom queries. $ ^{24} $ Lu et al.'s use of custom querying, $ ^{21} $ DL reasoning by Petnga et al., $ ^{23} $ and data exploration by Hagedorn et al. $ ^{18} $

Multiple frameworks have been introduced that make use of direct mappings from tools to enable SWT applications in engineering contexts. JPL introduced CEASAR as a type of framework to aid in MBSE analyses. CAESAR uses the Ontological Modeling Language (OML) to capture models in a controlled vocabulary and a number of tool adapters to incorporate different external design and analysis tools into the ontology-based approach. $ ^{24} $ Moser has proposed the Engineering Knowledge Base (EKB) as a framework for integrating SWT in multidisciplinary engineering environments. $ ^{9} $ This framework focuses on the use of custom tool mappings to interface with the underlying graph data structure. $ ^{9,25} $ Moser contrasts this approach with a common repository approach. In a common repository approach, schema must be predetermined and are tool specific, which makes them more fragile and harder to maintain. In the EKB approach, tool data are mapped to common engineering concepts, which enables a more robust representation of the data and semi-automatic transformation of data from one tool to another. $ ^{9} $ Both the CAESAR and EKB frameworks use an ontology-based AST and enable aspects of the DT. Mapping is often used alongside descriptive models such as those defined using the Systems Modeling Language (SysML). JPL, $ ^{5,26} $ Bone et al., $ ^{7} $ and Blackburn et al. $ ^{27} $ all populate SWT tools with ontologically aligned information using SysML that use stereotypes to inject ontological tags. In all these cases, stereotypes serve to guide a tool-specific mapping process.

Across all of these efforts, mapping provides a mechanism for connecting engineering tools with ontology-aligned data and the broader SWT stack. However, it does so through a rigid, often tool-specific, connection point. As a result, it may be difficult or labor intensive to add new tools to a workflow. It also limits accessibility of the data to those with knowledge of how to use SWT tools. Broader access, through a more flexible input and output mechanism would enable more design and analysis functionality. SysML v2 begins to provide more flexible access to system data through the use of a standards based Application Programming Interface (API). $ ^{28,29} $ However, SysML v2 uses this flexible input/output mechanism to access the system model, not an ontology-aligned representation of the information stored in the system model.

DTs require the interaction of multiple tools external to an AST. Flexibility in how tools can interact with data in the AST enables more opportunity for this interaction and increases the usability of a DE solution. While the SWT stack and mapping provide capability for a DT and are being used in current engineering research, there is space for additional types of interfaces to enable more diverse access to the AST.

## 3 METHODS

The DEFII framework (Figure 1) assigns the role of the AST to ontologies and data aligned to those ontologies. This forms the foundation of the framework. It then uses automated reasoning capabilities of SWT to enrich the ontology-aligned data through the use of rules and relationships defined in the ontologies. Finally, it provides clear categories of interfaces that users can use to access, modify, and populate the AST.

## 3.1 Ontology aligned data

Ontology-aligned data is the foundation of the framework. It enables the use of a graph data structure to act as the AST. Using a triplestore as a graph repository, the ontological knowledge base uses controlled vocabulary defined by ontology class data to characterize system data as instances of assigned classes. Representation of system data as ontology-aligned data in a graph data structure has following four primary benefits:

<!-- PDF_PAGE: 4 -->


![figure_001.png](figure_001.png)



<div align="center">

FIGURE 1 The DEFII framework for use of SWT in DE contexts.

</div>

## 1. Interoperability

Gruber argues for the use of ontologies for both reusability and interoperability between domains. $ ^{11,12} $ The framework specifies the use of a top-level ontology and shared development principles to drive co-development terminology across disparate knowledge domains. A top-level ontology provides a high-level philosophical basis and development guidance, that is, shared by all aligned ontologies within an ecosystem. Subsequent, domain specific ontologies simply extend this high-level understanding to ever more specific knowledge domains.

## 2. Tool agnostic

Because ontologies model domains of knowledge, rather than specific tools or datasets, data aligned to ontologies is tool agnostic. The use of a standards-based open formats, such as the Resource Description Framework (RDF) syntax and the Web Ontology Language (OWL) enhances this tool agnostic representation of system data. This makes the data portable and offers greater flexibility and freedom with tool access to the data.

## 3. Domain agnostic

Not only does the graph data structure promote tool agnostic access to data, it also promotes a domain agnostic approach. As noted by Mordecai et al., $ ^{10} $ the use of graph data structures extracts the system representation from the MBSE toolset and presents it in more general terms. As DE serves as an umbrella domain to connect many different domains, $ ^{30} $ representation of data in a way that separates it from any specific domain, including the systems engineering domain, offers more equitable access to it.

## 4. Access to SWT stack

The SWT stack offers many functions based on the formal nature of ontology-aligned data and the triple format of the stored data. Access

to powerful querying, reasoning, and validation is enabled by the foundational decision of the framework to use ontology-aligned data and will be detailed in subsequent sections of the paper.

## 3.2 Reasoning layer

The reasoning layer uses some of the automated reasoning capabilities included in the SWT stack. Since ontologies make use of axioms and relationships to characterize classes within them, these axioms can be used to further enrich the data beyond what has been explicitly defined. For example, if a child's mother and the mother's mother are defined explicitly in a graph repository and definitions and relations are encoded in the ontology (i.e., a grandmother is a role filled by a parent's mother for that parent's child), then the relationship between the child and the grandmother can be made through automated reasoning, bypassing the need to explicitly declare all knowledge in the graph repository. In characterizing engineering knowledge applied to a system, the ability to infer knowledge based on a heterogenous data store opens the possibility of discovering insights to how design elements originating in separate tools relate to each other. This capability uses mathematical logic, specifically description logics (DL), to enable DL reasoners as part of the SWT stack to automatically enrich the data without any extra involvement by external users.

## 3.3 Notional interfaces

The characterization of the system data in the AST is established, updated, viewed, and analyzed through interfaces to external sources. DEFII specifies three types of notional interfaces: the Direct Interface, the Mapping Interface, and the Specified Model Interface. The Specified Model Interface is further refined by the introduction of the Model Interface Specification Diagram (MISD). With these three types of interfaces and the MISD, the framework provides a structured approach to access and analyze ontology-aligned data.

The Direct Interface enables the use of the SWT stack directly on stored data. Data stored as ontology-aligned data enables the use of SWT tools to extract specific knowledge, apply constraint checking, and more using a growing set of tools in the SWT suite. This interface acknowledges this reality and codifies it within the framework's view of interfaces. While implementation of subsequent interface types will inevitably use SWT tools to enable them, this interface type is distinguished by its direct invocation of those tools.

The Mapping Interface transforms model data into ontology-aligned data by accessing data stored in a model or tool and mapping it to ontological classes in the controlled vocabulary. Beginning with external model data and establishing a connection to an ontology limits this interface type to a tool or model specific implementation per instance of the interface connected. Primarily, this interface addresses MBSE models and maps system models to ontology-aligned data. System models are broad in scope and capture design criteria for multiple domains. Thus, tagging data with relevant ontological terms and mapping that data to an ontology-aligned graph provides flexibility for the system model to be built to describe the relevant domains instead of

<!-- PDF_PAGE: 5 -->


![figure_002.png](figure_002.png)



<div align="center">

FIGURE 2 Mapping to an AST reduces interface development work.

</div>

fitting it into predetermined structure. It also means that the interface is domain agnostic: the ontological tags are simply changed or expanded to handle new domains.

This interface is the most restrictive interface as it is responsible for accessing data stored in other tools, making most instances tool-specific implementations. However, this form of interface still provides reductions in development efforts and maintains the benefits of ontologies over the use of direct tool-to-tool data integrations (Figure 2). The use of a mapping to an AST provides a limiting principle on the development efforts related to interfaces. Instead of a growing stable of tool-to-tool integrations, which will multiply with each tool added, an AST limits development to a single new interface per tool added to the workflow. In addition, if the AST uses a triplestore and ontology-aligned data, these add functionality to the AST by giving access to the reasoning capacities of the SWT and the other two types of notional interfaces.

The Specified Model interface characterizes models of interest within the broader system model. A model of interest is defined here as an aggregation of parameters present in the system model, that is, needed for external tools and application purposes. In contrast with the Mapping Interface, the Specified Model Interface begins with ontology-aligned data and exposes this data towards tool interfaces. This reverse of direction enables the interface to be tool agnostic. Even if an instantiation of the Specified Model Interface is designed with a particular tool in mind, the direction of the interface creation enables other tools to access the same information via the same interface. This interface primarily addresses MBE models and exposes data in a structured way to be analyzed, visualized, etc.

## 3.4 Model interface specification diagram

The MISD is a reusable, graphical specification for the Specified Model Interface. The MISD makes use of SysML parametric diagrams to describe a model of interest and define connections to parameters established elsewhere in the system model (Figure 3). The MISD acts as a graphical specification of data that will be provided to a given tool when requested. This extends Cilli's concept of an Assessment Flow Diagram. $ ^{31} $


![figure_003.png](figure_003.png)



<div align="center">

FIGURE 4 BDD showing cyber system architecture hierarchy.

</div>

Once mapped into the ontological layer, this specification can be concretized in a variety of formats, such as the Comma Separated Value (CSV) format. The MISD allows users unfamiliar with semantic technologies or the underlying ontologies used by the framework to request and update ontology-aligned data captured by the system model. It provides the means for tool-agnostic Specified Model Interfaces to be created and accessed by broader user group and toolset.

## 4 RESULTS

Results are produced using a case study from the Information Technology (IT) domain. $ ^{18,27} $ Below is an introduction of the case study followed by an instantiation of the DEFII framework for use in the case study.

## 4.1 Framework case study

While the DEFII framework is domain agnostic, the following IT case study provides a simple use case, that is, intuitive to understand as a test of the framework and a demonstration of its functionality. The case study examines a simple cyber system that has various cyber elements such as a laptop and software. The system is represented by a SysML Block Definition Diagram (Figure 4), where the blocks are tagged with stereotypes (e.g., <<CyberSystem>>) that align with the ontology classes, for which the model data is to be mapped into a triplestore repository.

<!-- PDF_PAGE: 6 -->

<div align="center">

TABLE 1 List of CVSS related value properties assigned to each block.

</div>

<table border="1"><tr><td>ac(attack complexity)</td><td>av(attack vector)</td></tr><tr><td>a(Availability)</td><td>vs(CVSS Vector)</td></tr><tr><td>score(CVSS Overall Score)</td><td>i(Integrity)</td></tr><tr><td>s(Scope)</td><td>c(Confidentiality)</td></tr><tr><td>pr(Privileges Required)</td><td>ui(User Interaction)</td></tr></table>


![figure_004.png](figure_004.png)



<div align="center">

FIGURE 5 DEFII framework applied to cyber case study.

</div>

The use case involving this case study is the identification of a seeded cyber vulnerability in the Internet Explorer web browser (contrived for demonstration) and the generation of a system wide Common Vulnerability Scoring System (CVSS) $ ^{32} $ score. This requires the use of both an MBSE model (system model in SysML) and an MBE model (MATLAB analysis model). In addition, a visualization of the results is included to demonstrate that a single tool-agnostic interface can service multiple tools. The DEFII Framework is displayed in the context of the case study (Figure 5).

To account for the cyber vulnerability portion of the use case, each cyber element also includes the value properties listed in Table 1 related to a CVSS score. These attributes are used to apply a CVSS score to a specific cyber vulnerability. For example, the "Scope" value can be "Unchanged" or "Changed," and the CVSS scoring process would take that value into account when calculating the overall CVSS score. These attributes are left off Figure 4 for readability.

Reflecting the collaborative and reusable nature of ontologies, the case study is based on existing, publicly available ontologies. The Basic Formal Ontology (BFO) $ ^{33} $ was used as a top-level ontology. BFO provides a small core of rigorously vetted terms, philosophical principles, and strict development guidelines which may be used to develop domain ontologies. This work also used the common core ontologies (CCO), $ ^{34} $ which extend BFO to cover common things found in many domains such as information. A Cybersecurity Ontology extending the CCO lexicon was used to describe the Cyber domain. This ecosystem


![figure_005.png](figure_005.png)



<div align="center">

FIGURE 6 Partial ontology shown in Protégé.

</div>

was then extended to describe the CVSS scoring system, as well as to introduce configuration management type notions such as version and patch numbers that are used to identify the vulnerability seeded into the case study. This represents a best practice that impacts usability of ontologies and ontology-aligned data: where possible, existing ontologies ought to be used and expanded only when required of the particular use case.B This limits the amount of work an individual team or use case will need to perform, and if the ontologies are built according to a consistent methodology (such as using BFO), previous efforts can be reused. This reusability and extensibility of ontologies enables organizations to slowly build up their collection of ontologies as business cases evolve. A portion of the ontology in the Protégé software is shown in Figure 6.

Elements in the Block Definition Diagram (BDD) (Figure 4) are stereotyped with ontological classes according to the ontologies being used in the DEFII framework. For example, the Laptop block has the <<LaptopComputer>> stereotype. These custom stereotypes are used to map tagged system model elements to ontology-aligned data.

The cyber system is instantiated within the system model. This allows the stakeholder to observe a specific instance of a system definition and for observation of both structure (an instantiation captures structure inherited from the definition) and specific values (e.g., Internet Explorer Version 1 and Version 2). A partial instantiation table is shown in Table 2.

Several tools are used to instantiate the DEFII framework for the case study. Ontotext's GraphDB triplestore $ ^{35} $ is used as the graph repository. Dassault Systemes' SysML Authoring tool suite, including CATIA Teamwork Cloud (TWC), $ ^{36} $ that is, used to create SysML models and provides remote, API-based access to the SysML elements. Protégé $ ^{37} $ is used for editing ontologies. Python is used for interacting with the various tools and instantiating the interfaces. The

<!-- PDF_PAGE: 7 -->

<div align="center">

TABLE 2 Partial instance table of instantiated model.

</div>

<table border="1"><tr><td>Name</td><td>ac:attack complexity</td><td>a:availability</td><td>av:attack vector</td></tr><tr><td>centOS</td><td>High</td><td>Low</td><td>Physical</td></tr><tr><td>Cyber system</td><td>High</td><td>Low</td><td>Physical</td></tr><tr><td>Ethernet cord</td><td>High</td><td>Low</td><td>Physical</td></tr><tr><td>Internet explorer</td><td>Low</td><td>Low</td><td>Network</td></tr></table>


![figure_006.png](figure_006.png)



<div align="center">

FIGURE 7 Digital thread across different interfaces.

</div>

OWLREADY2 $ ^{38} $ Python library is used for programmatic manipulation of graph data aligned to ontologies.

## 4.2 Framework implementation

To produce results, a DT is established (Figure 7) that uses all the interfaces to realize the defined use case. The first step is a mapping of the SysML system model from a tool specific implementation to an ontology aligned, tool-agnostic representation stored in a triplestore. Second, the Direct Interface is used to directly query the graph repository, via a SPARQL query, to discover a specific vulnerability. After the vulnerability is discovered, the third step is a MATLAB analysis program pulling data specified by an MISD from the triplestore via a REST API GET call. Fourth, after the analysis is complete, the triplestore is updated with new values produced by the analysis. Fifth, the same REST API endpoint that was used by the MATLAB analysis program is reused by a web application dashboard to display the results of the analysis. In this dataflow, all major elements of the framework are instantiated, and the reusability of the notional Specified Model Interface is highlighted.

A functional analysis of the three success criteria identified in the introduction must be performed to determine in the DEFII framework fulfills its purpose.

## 4.2.1 Mapping interface instantiation

The use of a SysML System Model requires a mapping interface. Specifically, it requires a tool specific interface for TWC, which is the repository for the SysML data. The mapping makes use of a combination of SysML language elements, like the custom stereotype, and TWC

"Step 1": "Execute SPARQL Query for stereotyped elements; store results for class and name",

"Step 2": "Loop through the results evaluating for 'name' variable existence in defined ontologies",

"Step 3": "Where 'name' exists as a class in the ontology, perform the following three tasks",

"Step 3a": "Create a triple in form ([class]_entity, rdf:type, [name])",

"Step 3b": "Create a triple in the form ([class]_spec, rdf:type: DirectiveInformationContentEntity)",

"Step 3c": "Create a triple in the form ([subject from Step 3b], Comm:prescribes, [subject from Step 3a])",

"Step 4": "Put newly created triples into the graph database",

"Step 5": "Add a link between relevant elements in mapped repository and original data repository"

<div align="center">

FIGURE 8 Pseudocode describing the implementation of a mapping rule.

</div>

specific features, like the Application Programming Interface (API) to TWC data that results in a JSON representation of the data that can be analyzed and mapped to ontology-aligned data. Mapping begins by transforming this API data to a representation in triples. SPARQL, a query language for semantic languages, can then be used to extract data relevant to the ontologies. Below is an example of a mapping rule executed in the mapping process. The example is presented in pseudocode (Figure 8) followed by a general explanation.

First a SPARQL query is run (Figure 9). This simple SPARQL query extracts classes from the triplestore that have been stereotyped by various names. The results are then checked against known classes in the ontologies. If the variable "?name" is the name of an ontological class, then the variable "?class" is mapped to the ontology aligned data. An entity and spec are created and related to each other to adhere to the way that the CCO describes information. Finally, a link back to the original, unmapped graph representation of the tool data is

<!-- PDF_PAGE: 8 -->


![figure_007.png](figure_007.png)



<div align="center">

FIGURE 9 A SPARQL query to discover stereotyped classes.

</div>

created to enable pushing updates back to the mapped tool. If the variable "?name" does not correspond to an ontological class, the result is discarded, and the mapping program moves to the next result.

This example mapping rule is implemented as part of a collection of mapping rules stored in a JavaScript Object Notation (JSON) file. These rules address aspects of the SysML model representation as presented by the TWC tool and include other facets of the language such as instances and enumerations. Together, these rules provide a process for transferring a SysML model representation to a tool-agnostic, ontology-aligned graph data structure. In the IT use case, a value with the <<VersionNumber>> stereotype applied to it would match the ?name variable in the SPARQL query, and variable would align with an ontology entity with the same name. Thus, a mapping of the SysML model's Version value on the Internet Explorer block to an instance of the "VersionNumber" ontology class is performed. While this specific result relates to the cyber case study described in the Section 3, the mapping rules discussed are more general and can be applied to any SysML model stored in a TWC instance. Thus, the mapping interface is tool-specific, but it is domain-agnostic and can be used across many different models and domains.

## 4.2.2 Direct interface

Accessing the triplestore via the Direct Interface allows for use of the SWT stack. Step 2 in the DT (Figure 7) uses a SPARQL query to directly query the triplestore in search of a specific vulnerability. Seen in Figure 10, SPARQL is selective enough to isolate a specific vulnerability tied to a particular version and patch number of the Internet Explorer web browser (a contrived vulnerability created for demonstration purposes). In this example, the user interface provided by GraphDB is used to execute the SPARQL queries.

The bottom half of Figure 9 shows a graph representation of the ontology-aligned data. As can be seen, "browser" is an instantiation of the "InternetExplorerWebBrowser." It is designated by "ver" and "patch," which are instantiations of "VersionNumber" and "PatchNumber," respectively and are show to have specific values of type "xsd:integer." The SPARQL query can look at the graph data and extract specific results that match this specific pattern. In this case, the graph is stored in GraphDB, but it can be exported in many different formats, included RDF and JavaScript Object Notation—Linked Data (JSON-LD).


![figure_008.png](figure_008.png)



<div align="center">

FIGURE 10 Top: SPARQL query; bottom: graph view.

</div>

## 4.2.3 Specified model interface with MISD

Steps 3 through 5 of the DT (Figure 7) requires the use of the Specified Model Interface. In order to instantiate the interface, an MISD is created to define the CVSS model for a system level vulnerability score (Figure 11). The MISD connects parameters from a variety of levels of the architecture to a single analysis model. It also shows multiple like parameters coming into the same port. The multiple levels of hierarchy show the flexibility of the interface specification-as long as the parameter is specified within the system model, it can be attached to a specified interface. Multiple parameters sharing a single port in the analysis model are collected into an array that can be analyzed as a block of data.

This interface definition is mapped to ontology-aligned data via the same mapping process described above and delineated by the <<Model >> stereotype.

Once the interface definition has been mapped to ontology-aligned data, the instantiated data associated with the definition can be transformed to a variety of different formats including JSON, which is a popular format for exchanging data. This data can then be exposed via a REpresentational State Transfer (REST) API. REST APIs allow stateless interaction with web services via HTTP requests. The DEFII REST API allows the Python implementation of the specified model interface to be exercised remotely via POST, GET, and PUT requests to instantiate, retrieve, and modify data in the triplestore (Figure 12).

<!-- PDF_PAGE: 9 -->


![figure_009.png](figure_009.png)



<div align="center">

FIGURE 11 CVSS Model Interface Specification Diagram (MISD).

</div>

<!-- PDF_PAGE: 10 -->


![figure_010.png](figure_010.png)



<div align="center">

FIGURE 12 Partial results of GET request of MISD in JSON.

</div>


![figure_011.png](figure_011.png)



<div align="center">

FIGURE 13 Dashboard showing CVSS analysis results.

</div>

For the CVSS model defined, a simple MATLAB analysis model was deployed to determine a system wide CVSS score along with a text-based vector for characterizing the CVSS score. Using MATLAB's webread and webwrite functions to access the REST API endpoint, data specified by the MISD is read into the analysis program, transformed by the analysis, and written back to the triplestore. In this process, the data are kept in a semantically aware position all data using the Specified Model Interface is specified and modified in terms of its place in the ontology-aligned data.

The results can be visualized using the same REST API endpoint accessed by the MATLAB analysis program. Since the interface is toolagnostic and specified for a defined model, a simple dashboard was created to pull the results data from the same interface. Figure 13 shows a resulting CVSS score and vector after the MATLAB analysis model has been run.

## 4.2.4 Additional SWT transformation

Additional SWT Transformation is seen in the use of automated reasoning supported by the tripl estore used. In the case study, Ontotext's GraphDB triplestore was used. The chosen reasoning profile for this paper was RDFS-Plus, which includes sub-classes and property inferences plus transitivity. This profile was chosen because it allows for relatively fast query answering, and this application does not require more sophisticated OWL semantics. Figure 14 shows that 36,674 of the total statements in the mapped repository were inferred compared to the 19,720 statements that were explicitly provided (an expansion


![figure_012.png](figure_012.png)



<div align="center">

FIGURE 14 GraphDB display of explicit and inferred statements.

</div>

ratio of 2.86). This result demonstrates that additional information was inferable through automated reasoning on the ontology definitions and provided instance data.

## 5 DISCUSSION AND FUTURE WORK

## 5.1 Analysis of results

The paper introduction identifies three functional attributes of a framework defined as success criteria for its operation in the DE context:

1. Provide clear avenues for mapping data from engineering design and analysis models to an ontology-aligned data store.

2. Allow access to contained data in a flexible, tool-agnostic manner.

3. Allow for the transformation and enhancement of data using various semantic technologies.

All three criteria are met by the DEFII framework presented in the paper.

Success Criteria 1 is fulfilled by the mapping interface. It provides clear guidance for what function the interface performs for the framework, and an example of its usage mapping a SysML model from an authoring tool to ontology-aligned data provides results that demonstrate the interface and give details to aid in reproduction of the interface.

Success Criteria 2 is fulfilled by the Specified Model Interface and the associated MISD. Use of the MISD allowed creation of a REST API endpoint that exposed ontology-aligned data to external tools. The results show the tool-agnostic nature of the data by accessing the same interface with two different tools, MATLAB and a web application dashboard. The MISD can also be created by system modelers that are unfamiliar with the underlying ontologies used by the DEFII framework. This enhances the functionality of the framework by expanding its usability beyond those adept in semantic technologies.

Success Criteria 3 is fulfilled by both the Direct Interface and the reasoning layer of the DEFII framework. The results show a SPARQL query accessing the ontology-aligned data to identify a vulnerability embedded in the data. The reasoning layer is demonstrated through the additional inferred statements based on the reasoning profile setup in the triplestore.

<!-- PDF_PAGE: 11 -->

These criteria and the framework approach increase usability of ontology-aligned data in a DE context in a few ways. Because the mapping mechanism is rooted in the SysML model (Criteria 1), a limited set of existing team members can participate in the mapping using a modeling language in which they are proficient. Likewise, because the MISD construct enables the exposure of ontology-aligned data in a way that does not require deep knowledge of ontologies and SWT by the whole team (Criteria 2), the number of teams that can implement the framework and take advantage of the graph representation of the data increases. While Criteria 3 specifically denotes the need to be able to use SWT to further enhance data, this criterion represents future capabilities beyond the need for an AST and the ability to implement a DT. Thus, this capability can be seen by users as upside when time and resources allow.

The DEFII framework's use of the MISD and Specified Model Interface also promote tool interoperability. Tool interoperability denotes the ability to use multiple tools to perform similar functionality on a single model. In the cyber case study, the CVSS analysis was performed by a MATLAB program. However, a program written in Java, Python, or a myriad of other tools and programming languages that can call REST services could perform the same analysis using the same interface. Further, another Specified Model Interface could be instantiated to provide the model specified by the MISD in a format other than the REST API endpoint. For example, it may be more beneficial to create and ingest CSV files for a particular model. As many different tools can read CSV files, the potential for creating tool-interoperable data increases. The more complicated the analysis, the harder tool interoperability may become on the tool side, but the DEFII framework establishes a standard way of specifying and exposing data in a tool agnostic format that promotes tool interoperability.

## 5.2 Limitations and future research opportunities

The MISD presented in the cyber case study includes many similar elements manually connected to a cyber analysis model. While the diversity of elements and parameters (multiple levels of hierarchy, single, and multiple inputs to various ports) demonstrates key features of the MISD and thus is useful for presenting the overall notional interface, the actual analysis being performed could be characterized as a pattern to greatly simplify the specific instantiation of the interface. A roll-up pattern like the one presented (also consider weight $ ^{18} $ and cost) is recursive in nature, where like elements at one level of architecture are "rolled up" to their parent element, which then serves as an element of analysis for the next level of architecture. Future research needs to determine how to account for these types of analysis in the interface specification.

The Specified Model Interface is the preferred interface in the presented framework for most uses in a DE environment. It enables tool-agnostic implementation of a DT across multiple toolsets and consolidates interface development in a way that preserves the semantic underpinnings of the approach. It can be extended to provide tool specific data through the use of middleware that transforms the tool-

agnostic representation of an interface (i.e., JSON from a REST API endpoint) to a tool specific format of an external tool that does not have web services capability. This implementation could have two benefits: developers do not need to understand SWT to create the middleware whereas they would need that background information to create a custom mapping interface, and (2) the interface could still be used by other tools. For example, an analysis program may make use of middleware to transform standard JSON to a tool specific XML representation, but a dashboard could access that same interface to do reporting and visualization of the data the analysis program is using/producing. If this is consistently used in practice, the Mapping Interface may be limited to the unique semantic mapping needs of a system model.

The Direct Interface enables a wide range of applications and further exploration of the SWT stack. Results in this paper show a simple SPARQL query to demonstrate access to the SWT, but more complex applications of the SWT could provide deeper functionality to the notional interface. For example, the use of the W3C recommended Shapes Constraint Language (SHACL) $ ^{39} $ could allow for certain verification and validation tasks to occur on the semantic representation of the system model, such as checks for well-formedness and consistency.

While this paper only integrates a single analysis model and visualization tool, most cyber physical systems would need multiple simulation-based analyses. Therefore, multiple MISDs would be linked together into a broader Assessment Flow Diagram $ ^{31} $ where various discipline specific simulation models (Computational Fluid Dynamics, Finite Element Analysis, Computer Aided Design, etc.) have one or more shared, interrelated parameters. Co-mingling the model of analysis with the system or mission model allows designers to relate the metadata and results from various analysis models to the system or mission level performance measures.

## 5.3 Framework impact on digital engineering domain

Ultimately, the DEFII framework guides engineering organizations in transforming domain specific models into a knowledge representation that both provides needs for existing workflows (integrating with domain models) and establishes the foundation for additional applications depending on an integrated view of the system as a whole (digital assistants, reasoning, constraint checking, etc.). This forward-looking component of the DEFII framework adds value to its use in the present day as it solves an existing problem (robust data integration across multiple models) with a solution that presents opportunity beyond the current need.

Augmented Intelligence applications such as Digital Assistants can be a force multiplier in a context where solutions are becoming increasingly complex and quicker turnaround times are expected. A robust, machine readable knowledge representation of the system under design, along with the relevant domains, is needed to inform an augmented intelligence agent, and semantic technologies are a viable candidate for this representation. $ ^{18,40} $ Existing research into the use of Machine Learning algorithms applied to ontological data could also be

<!-- PDF_PAGE: 12 -->

leveraged to provide added value. $ ^{41} $ The DEFII framework gives structure for using SWT in the DE context and opens these opportunities in the future.

## 6 CONCLUSION

The DEFII framework addresses integration and interoperability challenges in the Digital Engineering context through the use of ontologyaligned data, that is, exposed through to external toolsets through three types of interfaces: the Mapping Interface, the specified Model Interface, and the Direct Interface. It introduces the Model Interface Specification diagram as a mechanism for defining interfaces in SysML that align with ontologically relevant data without the need for the interface designer to be an expert in ontologies or semantic technologies. The systems of analysis are defined in a MBSE tool and language, that is, natural to systems engineers, that is, ultimately mapped to an underlying ontology-based repository. This allows for the implementation of a Digital Thread that permits external tools to interact with a common Authoritative Source of Truth in a flexible, tool-agnostic manner. By taking advantage of the formal nature of ontologies and the various technologies that have been developed to enhance and use ontologies, the framework both provides for the integration and interoperability needs of model-based design and analysis today, and sets a foundation for further innovation in the future.

## ACKNOWLEDGEMENTS

This research was sponsored by the Systems Engineering Research Center (SERC), a University Affiliated Research Center (UARC) housed at Stevens Institute of Technology.

## DATA AVAILABILITY STATEMENT

None

## ORCID

Daniel Dunbar https://orcid.org/0000-0001-9647-8073

John Dzielski https://orcid.org/0000-0002-7931-076X

## REFERENCES

1. Defense Acquisition University Glossary. Accessed May 15, 2022. https://www.dau.edu/glossary/Pages/Glossary.aspx#!both|D|27345

2. Rogers EB, Mitchell SW. MBSE delivers significant return on investment in evolutionary development of complex SoS. Syst Eng. 2021;24(6):385-408. doi:10.1002/sys.21592

3. Kruse B, Blackburn M. Collaborating with OpenMBEE as an authoritative source of truth environment. Procedia Comput Sci. 2019;153:277- 284. doi:10.1016/j.procs.2019.05.080

4. Bone MA, Blackburn MR, Rhodes DH, Cohen DN, Guerrero JA. Transforming systems engineering through digital engineering. J Def Model Simul Appl Methodol Technol. 2019;16(4):339-355. doi:10.1177/ 1548512917751873

5. Wagner DA, Bennett MB, Karban R, Rouquette N, Jenkins S, Ingham M. An ontology for state analysis: formalizing the mapping to SysML. 2012 IEEE Aerospace Conference, Big Sky, MT, USA; 2012: 1-16. doi:10. 1109/AERO.2012.6187335

6. Hagedorn TJ, Smith B, Krishnamurty S, Grosse I. Interoperability of disparate engineering domain ontologies using basic formal ontology. J Eng Des. 2019;30(10-12):625-654. doi:10.1080/09544828.2019.1630805

7. Bone M, Blackburn M, Kruse B, Dzielski J, Hagedorn T, Grosse I. Toward an interoperability and integration framework to enable digital thread. Systems. 2018;6(4):46. doi:10.3390/systems6040046

8. Roper W. There is No Spoon: The New Digital Acquisition Reality. United States Air Force; 2020. https://software.af.mil/wp-content/uploads/2020/10/There-Is-No-Spoon-Digital-Acquisition-7-Oct-2020-digital-version.pdf

9. Moser T. The engineering knowledge base approach. In: Biffl S, Sabou M, eds. Semantic Web Technologies for Intelligent Engineering Applications. Springer International Publishing; 2016:85-103. doi:10.1007/978-3-319-41490-4 4

10. Mordecai Y, Fairbanks JP, Crawley EF. Category-theoretic formulation of the model-based systems architecting cognitive-computational cycle. Appl Sci. 2021;11(4):1945. doi:10.3390/app11041945

11. Gruber TR. The role of common ontology in achieving sharable, reusable knowledge bases. Kr. 1991;91:601-602.

12. Gruber TR. A translation approach to portable ontology specifications. Knowl Acquis. 1993;5(2):199-220. doi:10.1006/knac.1993.1008

13. Gruber TR. Toward principles for the design of ontologies used for knowledge sharing? Int J Hum-Comput Stud. 1995;43(5-6):907-928.

14. Coelho M, Austin MA, Blackburn MR. The data-ontology-rule footing: a building block for knowledge-based development and event-driven execution of multi-domain systems. In: Adams S, Beling PA, Lambert JH, Scherer WT, Fleming CH, eds. Systems Engineering in Context. Springer International Publishing; 2019:255-266. doi:10.1007/978-3-030-00114-8_21

15. Eddy D, Krishnamurty S, Grosse I, Wileden J. Support of product innovation with a modular framework for knowledge management: a case study. ASME 2011 International Design Engineering Technical Conferences and Computers and Information in Engineering Conference. Volume 2: 31 $ ^{st} $ Computers and Information in Engineering Conference, Parts A and B. 2011:1223-1235. https://scholar.google.com/scholar?hl=en&as_sdt=0%2C25&q=Support+of+Product+Innovation+With+a+ Modular+Framework+for+Knowledge+Management%3A+A+Case+ Study&btnG=#d=gs_cit&t=1677517318757&u=%2Fscholar%3Fq% 3Dinfo%3Ay9javeLtbIIJ%3Ascholar.google.com%2F%26output% 3Dcite%26scirp%3D0%26hl%3Den

16. Hagedorn TJ, Krishnamurty S, Grosse IR. A knowledge-based method for innovative design for additive manufacturing supported by modular ontologies. J Comput Inf Sci Eng. 2018;18(2):021009. doi:10.1115/ 1.4039455

17. Daun M, Brings J, Weyer T, Tenbergen B. Fostering concurrent engineering of cyber-physical systems a proposal for an ontological context framework. 2016 3rd International Workshop on Emerging Ideas and Trends in Engineering of Cyber-Physical Systems (EITEC). IEEE; 2016:5-10. doi:10.1109/EITEC.2016.7503689

18. Hagedorn T, Bone M, Kruse B, Grosse I, Blackburn M. Knowledge representation with ontologies and semantic web technologies to promote augmented and artificial intelligence in systems engineering. Insight. 2020;23(1):15-20. doi:10.1002/inst.12279

19. El Kadiri S, Kiritsis D. Ontologies in the context of product lifecycle management: state of the art literature review. Int J Prod Res. 2015;53(18):5657-5668. doi:10.1080/00207543.2015.1052155

20. Hoppe T, Eisenmann H, Viehl A, Bringmann O. Digital space systems engineering through semantic data models. 2017 IEEE International Conference on Software Architecture (ICSA), Gothenburg, Sweden. 2017:93-96. doi:10.1109/ICSA.2017.35

21. Lu J, Ma J, Zheng X, Wang G, Li H, Kiritsis D. Design ontology supporting model-based systems engineering formalisms. IEEE Syst J. 2021:1-12. doi:10.1109/JSYST.2021.3106195. Published online.

<!-- PDF_PAGE: 13 -->

22. Madni AM, Sievers M. Model-based systems engineering: motivation, current status, and research opportunities. Syst Eng. 2018;21(3):172- 190. doi:10.1002/sys.21438

23. Petnga L, Austin M, Blackburn M. Semantically-enabled model-based systems. Insight. 2017;20(3):29-38. doi:10.1002/inst.12161

24. Wagner D, Kim-Castet SY, Jimenez A, Elaasar M, Rouquette N, Jenkins S. CAESAR model-based approach to harness design. 2020 IEEE Aerospace Conference; 2020:1-13. doi:10.1109/AERO47225. 2020.9172630

25. Kovalenko O, Euzenat J. Semantic matching of engineering sata Structures. In: Bifl S, Sabou M, eds. Semantic Web Technologies for Intelligent Engineering Applications. Springer International Publishing; 2016:137-157. doi:10.1007/978-3-319-41490-4_6

26. Jenkins JS, Rouquette NF. Semantically-Rigorous Systems Engineering Modeling Using SysML and OWL; 2012: 8. Published online.

27. Blackburn MR, Bone MA, Dzielski J, et al. Transforming Systems Engineering through Model-Centric Engineering, Final Technical Report SERC-2020-TR-009, WRT-1008 (NAVAIR); 2020.

28. Bajaj M, Friedenthal S, Seidewitz E. Systems modeling language (SysML v2) support for Digital Engineering. Insight. 2022;25(1):19-24. doi:10.1002/inst.12367

29. Friedenthal S, Seidewitz E. A preview of the next generation system modeling language (SysML v2). Syst Eng Newsl Proj Perform Int PPI. 2020; SyEN 95:18.

30. Zimmerman P, Gilbert T, Salvatore F. Digital engineering transformation across the Department of Defense. J Def Model Simul Appl Methodol Technol. 2019;16(4):325-338. doi:10.1177/1548512917747050

31. Cilli MV. Improving Defense Acquisition Outcomes Using an Integrated Systems Engineering Decision Management (ISEDM) Approach. PhD Thesis; 2015. http://ezproxy.stevens.edu/login?url=https://www.proquest.com/dissertations-theses/improving-defense-acquisition-outcomes-using/docview/ 1776469856/se-2?accountid=14052

32. NVD - Vulnerability Metrics. Accessed May 28, 2021. https://nvd.nist.gov/vuln-metrics/cvss

33. Arp R, Smith B, Spear AD. Building Ontologies with Basic Formal Ontology. Mit Press; 2015.

34. CUBRC, Inc. An Overview of the Common Core Ontologies; 2020. Accessed March 20, 2021. https://github.com/ CommonCoreOntology/CommonCoreOntologies/blob/master/ documentation/An%20Overview%20of%20the%20Common% 20Core%20Ontologies%201.3.docx

35. GraphDBTM. Ontotext. Accessed March 20, 2021. https://www. ontotext.com/products/graphdb/

36. Teamwork Cloud - CATIA - Dassault Systèmes $ ^{\circ} $ . Accessed May 15, 2022. https://www.3ds.com/products-services/catia/products/nomagic/teamwork-cloud/

37. Musen MA. The protégé project: a look back and a look forward. AI Matters. 2015;1(4):4-12. doi:10.1145/2757001.2757003

38. Lamy JB. Owlready: ontology-oriented programming in Python with automatic classification and high level constructs for biomedical ontologies. Artif Intell Med. 2017;80:11-28. doi:10.1016/j.artmed.2017.07.002

39. Shapes Constraint Language (SHACL). Accessed May 15, 2022. https:// www.w3.org/TR/shacl/

40. Rouse WB. AI as systems engineering augmented intelligence for systems engineers. Insight. 2020;23(1):52-54. doi:10.1002/inst.12286

41. Austin M, Delgoshaei P, Coelho M, Heidarinejad M. Architecting smart city digital twins: combined semantic model and machine learning approach. J Manag Eng. 2020;36(4):04020026. doi:10.1061/(ASCE) ME.1943-5479.0000774

How to cite this article: Dunbar D, Hagedorn T, Blackburn M, et al. Driving digital engineering integration and interoperability through semantic integration of models with ontologies. Systems Engineering. 2023;26:365-378. https://doi.org/10.1002/sys.21662

## AUTHOR BIOGRAPHIES


![figure_013.png](figure_013.png)



Daniel Dunbar is a PhD Candidate in Systems Engineering at Stevens Institute of Technology. His research interests include Digital Engineering and formal knowledge representation as means to enable better multidisciplinary collaboration. He currently works as a Research Assistant for the Systems Engineering Research Center (SERC) under Dr Mark Blackburn's leadership. Before joining Stevens, he worked in the telecommunications domain designing and implementing two-way radio systems.


![figure_014.png](figure_014.png)



Thomas Hagedorn is a Research Scientist at Stevens Institute of Technology since 2022 investigating the use of ontologies and ontology-backed frameworks in engineering design and systems engineering. He holds a PhD in Mechanical Engineering from the University of Massachusetts at Amherst (Amherst, MA), and a BS in Biomedical Engineering from Boston University (Boston, MA).


![figure_015.png](figure_015.png)



Mark Blackburn, PhD is a Senior Research Scientist with Stevens Institute of Technology since 2011 and principal at KnowledgeBytes. Dr Blackburn has been the Principal Investigator (PI) on 17 System Engineering Research Center (SERC) research tasks for both US Navy NAVAIR,

US Army ARDEC, and US Space Force on Digital Engineering Transformation Research Tasks. He has also been PI on a FAA NextGen and National Institute of Standards and Technology projects and has received research funding from the National Science Foundation. He develops and teaches a course on Systems Engineering for Cyber Physical Systems. He is a member of the SERC Research Council, OpenMBEE Leadership Team, and INCOSE Pattern Working Group focused on the Semantic Technologies for Systems Engineering initiative. Prior to joining Stevens, Dr Blackburn worked in industry for more than 25 years. He has been the Principal Investigator to the National Institute of Standards and Technology on projects dating back to 2000 involving model-based tools and

<!-- PDF_PAGE: 14 -->

methods for verification and validation of security-related products and applications. Dr Blackburn holds a PhD from George Mason University, a MS in Mathematics (emphasis in C.S.) from Florida Atlantic University, and a BS in Mathematics (C.S. option) from Arizona State University.


![figure_016.png](figure_016.png)



John Dzielski earned a BS in mechanical engineering from Carnegie-Mellon University in 1982, and MS and PhD degrees in mechanical engineering from the Massachusetts Institute of Technology in 1984

and 1988, respectively. He has more than 30 years of experience relating to the design, integration, and at-sea testing of unmanned undersea vehicle systems supporting various US Navy missions. He has been involved in research and development of supercavitating vehicle technology since 1995. He is applying his experience in simulation-based analysis, synthesis, and validation processes to the development of formal model-based system engineering methods and processes using SysML integrated with modern analysis and design optimization tools. These methods rely heavily on semantic-web technologies and are being developed for and delivered to several different government sectors. He may be the expert on American football dynamics and aerodynamics.


![figure_017.png](figure_017.png)



Steven Hespelt studied Computer Science, Mathematics at the University of Rochester. Since 1985, Steve's worked in both commercial and academic research positions in software developer, team lead, and IT support roles.


![figure_018.png](figure_018.png)



Benjamin Kruse acquired his diploma in mechanical engineering in the field of aerospace at the Technical University Munich in Munich (2012, Germany) where he also started his doctorate before finishing his Dr.sc. at ETH Zurich in Zurich (2017, Switzerland). There he investigated formal and reuse-based support for multidisciplinary concept design using the model-based systems engineering language SysML. Afterwards, he became a Research Assistant Professor at Stevens Institute of Technology in Hoboken, NJ (2017, USA), working on the model-based systems engineering side of the systems engineering transformation through modelcentric engineering as part of implementing the Department of Defense's digital engineering strategy. This work was continued as an ISE Post-Doctoral Associate for the Virginia Polytechnic Institute and State University in Blacksburg, VA (2021, USA) before switching to the e:fs TechHub GmbH in Gaimersheim (2022, Germany) in order to work as a developer for model-based systems engineering in the Volkswagen Group.


![figure_019.png](figure_019.png)



Dinesh Verma received the PhD (1994) and the MS (1991) in Industrial and Systems Engineering from Virginia Tech. He served as the Founding Dean of the School of Systems and Enterprises at Stevens Institute of Technology from 2007 through 2016. He currently serves as the Executive Director of the Systems

Engineering Research Center (SERC), a US Department of Defense sponsored University Affiliated Research Center (UARC) focused on systems engineering research; along with the Acquisition Innovation Research Center (AIRC). Prior to this role, he served as Technical Director at Lockheed Martin Undersea Systems, in Manassas, Virginia, in the area of adapted systems and supportability engineering. Before joining Lockheed Martin, Verma worked as a Research Scientist at Virginia Tech and managed the University's Systems Engineering Design Laboratory. He served as an Invited Lecturer from 1995 through 2000 at the University of Exeter, United Kingdom. In addition to his publications, Verma has received three patents in the areas of life-cycle costing and fuzzy logic techniques for evaluating design concepts. Dr. Verma has authored over 150 technical papers, book reviews, technical monographs, and co-authored three textbooks: Maintainability: A Key to Effective Serviceability and Maintenance Management (Wiley, 1995), Economic Decision Analysis (Prentice Hall, 1998), Space Systems Engineering (McGraw Hill, 2009). He was recognized with an Honorary Doctorate Degree (Honoris Causa) in Technology and Design from Linnaeus University (Sweden) in January 2007; and with an Honorary Master of Engineering Degree (Honoris Causa) from Stevens Institute of Technology in September 2008.


![figure_020.png](figure_020.png)



Zhongyuan Yu is a Teaching Associate Professor and Software Engineering Program Director in the School of Systems and Enterprises at Stevens Institute of Technology and a member of Center for Complex Systems and Enterprises. Dr Yu builds smart and interactive data-driven

decision support systems. Dr Yu has 15 years of extensive software prototype developing expertise and her research crosses multiple disciplines including applied statistics, optimization, data visualization, simulation, natural language processing, network analysis, and socio-economics. Dr Yu has presented her research findings in national and international conferences such as INFORMS, Academy Health, CESUN and JSM, and delivered hundreds of presentations to executives and senior managers in public sectors and private industry, including Northwell Health, Emory Healthcare, North Shore-LIJ Health System, CareFirst BlueCross BlueShield, UnitedHealth, Bell Labs, MITRE and others. Dr Zhongyuan Yu holds a PhD in System Engineering from Stevens Institute of Technology, MS in Operations Research, and MS in Industrial Engineering from Georgia Institute of Technology.