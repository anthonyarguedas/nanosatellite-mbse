---
source: null
title: "review-candidate-0176"
page_count: 26
converted_at: "2026-09-05T21:20:45Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# RETRIEVAL AUGMENTED (KNOWLEDGE GRAPH), AND LARGE LANGUAGE MODEL-DRIVEN DESIGN STRUCTURE MATRIX (DSM) GENERATION OF CYBER-PHYSICAL SYSTEMS

</div>

PREPRINT, COMPILED FEBRUARY 20, 2026

Hasan Sinan Bank $ \textcircled{G} $ $ ^{1*} $ and Daniel R. Herber, PhD $ \textcircled{G} $ $ ^{1*} $

$ ^{1} $ Department of Systems Engineering, Colorado State University, Fort Collins, CO 80523, USA

## ABSTRACT

We explore the potential of Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and Graph-based RAG (GraphRAG) for generating Design Structure Matrices (DSMs). We test these methods on two distinct use cases—a power screwdriver and a CubeSat with known architectural references—evaluating their performance on two key tasks: determining relationships between predefined components, and the more complex challenge of identifying components and their subsequent relationships. We measure the performance by assessing each element of the DSM and overall architecture. Despite design and computational challenges, we identify opportunities for automated DSM generation, with all code publicly available for reproducibility and further feedback from the domain experts.

Keywords retrieval augmented knowledge graph · natural language processing · architecture synthesis · design structure matrix

We explore the potential of Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and Graph-based RAG (GraphRAG) for generating Design Structure Matrices (DSMs). We test these methods on two distinct use cases—a power screwdriver and a CubeSat with known architectural references evaluating their performance on two key tasks: determining relationships between predefined components, and the more complex challenge of identifying components and their subsequent relationships. We measure the performance by assessing each element of the DSM and overall architecture. Despite design and computational challenges, we identify opportunities for automated DSM generation, with all code publicly available for reproducibility and further feedback from the domain experts.

Keywords: retrieval augmented knowledge graph, natural language processing, architecture synthesis, design structure matrix

Abbreviations: DSM—Design Structure Matrix; LLM—Large Language Model; AI—Artificial Intelligence; CAD—Computer Aided Design; CPS—Cyber-Physical System; NLP—Natural Language Processing; RAG—Retrieval Augmented Generation; MBSE—Model-Based Systems Engineering; PLM—Product Lifecycle Management

## 1 INTRODUCTION

Since the Industrial Revolution, humanity has increasingly created sophisticated technological tools that shape our world, inspired by natural patterns and scientific advancements. As technology has evolved, the growing complexity of these developments has necessitated more advanced approaches to engineering and design [1]. This complexity prompted the establishment of formalized education programs, with the University of Michigan awarding the first MSc [2] in 1859 and Yale University granting the first PhD [3] in 1861, while concurrently spurring the development of foundational conceptual frameworks. For decades, engineering and scientific disciplines have driven the pursuit of understanding technologies and their interrelated parts.

In response to these needs, significant frameworks emerged, including von Bertalanffy's introduction of general system theory [4] in the 1930s, and Bell Laboratories coining the term "systems engineering" in the 1940s [5, 6]. As these foundational concepts evolved to address increasingly integrated technologies, they have become particularly relevant for today's complex systems. Building on this historical foundation, modern architectural representation methods for cyber-physical systems (CPS) require clear definitions of systems, complexity, and architecture to address today's design challenges.

To effectively examine modern architectural representation methods, particularly in the context of CPS, we need to clarify the definitions for the core concepts of systems engineering, such as systems, complexity, and architecture. The term "system" has over 180 definitions, applied in various contexts, and the notion of "complexity" is similarly multifaceted [9]. Our goal in providing these definitions is to establish clarity regarding our perspective, avoiding the ambiguity often associated with phrases such as "I can't define it for you, but I know it when I see it." [10] A complex system has many elements or entities that are highly interrelated, interconnected, or interwoven [11]. This complexity is driven into systems by demanding more in terms of function, performance, robustness, and flexibility, as well as through the increasing need for systems to work together and interconnect. Such characteristics create challenges not only in development but also in comprehension and management.

Similar to "system" and "complexity," architecture has numerous definitions. Its origins span various industries, but in the context of systems, it is best described as "an abstract description of the entities of a system and the relationship between those entities" [12] or as defined in ISO/IEC 42010, "fundamental concepts or properties of a system in its environment embodied in its elements, relationships, and in the principles of its design and evolution." Every system has an architecture that may arise through deliberate de novo design, evolution from previous designs with legacy constraints, adherence to regulations and

<!-- PDF_PAGE: 2 -->


![figure_001.png](figure_001.png)



<div align="center">

Figure 1: Architectural Representations of Sample Systems a) Steam Engine [7] b) F1Tenth Autonomous Car [8]

</div>

standards, accretion of smaller systems, or dialogue between stakeholders and architects. Architecture strongly influences system behavior, determining both its basic functions and other properties such as durability, maintainability, and flexibility collectively called the "ilities."[13]

When we examine the literature, the formation of architectural representation mostly deals with qualitative and hard-to-measure aspects such as function, allocation, structure, and physical elements. Within the context of architecting or the definition of system architecture, the architect finds a design to solve the problem from requirements to physical aspects while overlaying these in slightly different perspectives. Maier[14] characterizes architecting methodologies as both art and science - where science is embodied in normative and rational methods, while art manifests in participative and heuristic approaches, particularly when dealing with "immeasurables" and complex system conceptualization. Buede[15] further emphasizes this duality, demonstrating how system architectures comprise functional (what the system must do), physical (resource partitioning), and allocated (mapping functions to resources) architectures that, while distinct, must be "developed in parallel but with close interaction" to ensure meaningful integration.

These architectural challenges have become particularly evident in CPS, which represent one of the most complex integration challenges in modern engineering. As defined by NSF[16], the defining characteristic of CPS is the "seamless integration of computation algorithms and physical hardware," while NIST[17] elaborates that "Cyber-Physical Systems (CPS) are smart systems that include co-engineered interacting networks of physical and computational components." VDI[18] (Verein Deutscher Ingenieure) describes CPS as an evolution beyond traditional mechatronic systems by incorporating internet connectivity and adaptive properties - they are defined as "interconnected mechatronic systems that are additionally connected to the Internet of Things and Services and adapt their properties during operation. This enables them to communicate with each other and use Internet services." This connectivity between physical processes and digital networks creates diverse applications with high economic potential and innovative strength.

The evolution of systems from mechanical to cyber-physical has introduced new challenges in architectural representation and analysis, as illustrated in Fig. 1. Using the steam engine[7] and F1Tenth Autonomous Car[8] as representative examples, we can see how system architectures have evolved from purely mechanical representations to complex cyber-physical integrations As these systems integrate computational elements, networking capabilities, and adaptive behaviors, we must examine how traditional and emerging methods address their architectural representation.

The challenges of representing and analyzing such CPS architectures motivate our exploration of new approaches for automated architectural generation. The following sections examine key architectural representation methods and automation techniques, starting from graph-based approaches while examining its matrix-based derivatives such as Design Structure Matrix (DSM), and expanding to language-based methods. This background establishes the foundation for our proposed methodology that combines baseline models and augmented techniques to generate DSMs that capture the complexity of modern CPS.

## 2 LITERATURE REVIEW

## 2.1 The Architectural Representation

Modern CPS present significant challenges in architectural representation and analysis, particularly in generating effective architectural models during the design phase because of their inherent complexities. Researchers have approached this challenge from various angles, with most studies focusing on analyzing existing architectural structures. Among these contributions, Raz[19] introduced a notable framework for architecture design space characterization that integrates decision alternatives across functional, physical, and allocational spaces. Their work demonstrated that the traditional dichotomous treatment of system architecture and design trade-off analysis is insufficient for complex systems with interacting and interwoven functions and elements. However, their approach, while providing a substantial framework for representing and analyzing architectural design space, focuses primarily on characterizing and evaluating architectural alternatives rather than their initial formation.

To address these architectural representation challenges, researchers have developed numerous methodologies for modern complex systems. Early efforts focused on creating integrated model environments, while later work explored specialized analysis techniques. For example, the Total System Model (TSM) concept introduced by Bajaj[20] provides a graph-based digital blueprint that federates information from engineering models across multiple repositories. Schummer[21] focused on developing a schema and MBSE modeling approach for using graph databases to analyze system architectures. However, these approaches face practical implementation challenges, particularly when integrating existing engineering tools and processes. As Chadzynski[22] demonstrated, effective automation requires not

<!-- PDF_PAGE: 3 -->

only modeling capabilities but also seamless integration with Product Lifecycle Management (PLM) systems where critical implementation details reside.

While the above approaches focus on model-based representations, another significant contribution to architectural analysis comes from matrix-based methods. The DSM, introduced by Steward in the 1960s, is a compact, matrix-based representation of a system that is particularly valuable for analyzing and managing complex interdependencies [23]. While structurally similar to an adjacency matrix from graph theory, a DSM's primary application is in architectural analysis, such as identifying modules through clustering or managing process flows by reordering elements (e.g., to minimize feedback loops). However, these approaches face significant practical limitations. For example, as highlighted by Eppinger [24], multiple real-world cases demonstrate the labor-intensive nature of DSM creation: the development process of Pratt & Whitney's jet engine required four months of doctoral student work to extract the necessary DSM interactions. Creating a DSM with 84 components for Xerox's iGen3 Digital Printing System architecture required 140 person-hours. Even more notably, at NASA, a master's student spent five months researching seven robotic spacecraft missions to generate the Technology Risk DSM for Mars Pathfinder Technology Readiness Assessment. These cases underscore a persistent challenge: while DSM generation is important for understanding the system architecture, the process remains labor-intensive and time-consuming.

Additional challenges exist with domain-specific language methods, such as SysML, where users must understand specific structures in a generic manner while deriving their own extensions for specific uses[25]. This requirement for significant expert input makes scalability and the general use of these approaches persistently challenging. While some research studies claim to automate trade studies by combining PLM and SysML models, they often fail to address the fundamental challenge identified by Chadzynski[22]: the need to semantically connect elements across different modeling domains while maintaining traceability throughout the Requirements-Functional-Logical-Physical (RFLP) core.

All of these examples highlight two critical gaps: 1) irrespective of the state of the CPS (e.g., physically existing or fresh in the initial design phase), extensive time and human expertise are required for the generation of systems architecture; and 2) integration challenges between system models, implementation data, and existing PLM workflows such as computer-aided design, engineering, and manufacturing. The labor-intensive nature of these processes is demonstrated in industry practice, where generating architectural representations can take months of expert work while maintaining semantic connections and traceability across different modeling domains, data structures, and modalities remains a persistent challenge.

All of these gaps suggest the need for a generalizable and automated approach to generating architectural representations that can reduce manual effort while maintaining accuracy and semantic compatibility with existing practices. The emergence of advanced language models and multi-modal capabilities offers promising new directions for addressing these challenges, particularly when combined with proven approaches for integrating PLM systems and maintaining traceability across the development life-cycle.

These gaps in current architectural representation methods have led researchers to investigate automated approaches to address the challenges of manual effort, scalability, and integration. These automation efforts have primarily followed two directions: graph-based methods that leverage mathematical foundations for structural representation and analysis and language-based methods that harness semantic understanding for architectural generation. Each approach offers distinct advantages while addressing different aspects of the identified challenges. The following sections examine these approaches in detail, beginning with graph-based methods that have historically provided a foundation for system representation.

## 2.2 Automated Architecture Generation

## 2.2.1 Graph-based Methods

Graph theory provides a rigorous mathematical foundation for representing and analyzing relationships between components in a system. Through its fundamental concepts of vertices (nodes) and edges (connections), it enables engineers and scientists to model complex systems from physical structures to information networks, excelling in representing both qualitative relationships (e.g., functional dependencies, spatial arrangements) and quantitative metrics (e.g., flow rates, connection strengths). The flexibility of its components allows for the depiction of diverse properties and relationships, while the graph framework provides a holistic overview. Moreover, its mathematical rigor and structural adaptability facilitate seamless translation into formats such as matrices for computational purposes, preserving inherent modularity and adaptation, solidifying its role as a foundational apparatus across domains.

Building on this foundation, graph-theoretic approaches provide a systematic way to generate and analyze system architectures. While research studies have investigated methods ranging from transforming generated shapes into simulation models[26] to intricate relationship mapping through generative algorithms[27] and Boolean satisfiability problems[28], the difficulties are especially pronounced in CPS. In these domains, component relationships must satisfy multiple constraints simultaneously, extending beyond simple feasibility constraints[29] to include uniqueness requirements[30] and the need to accommodate various models and design variables in the optimization process[31]. These multi-domain relationships and constraints can make traditional graph representations difficult to interpret and analyze without a layout algorithm (e.g., ForceAtlas2 [32], YifanHu [33], etc.) or software tool (e.g., Gephi [34]), especially during initial architectural formation, as the visual complexity and the interactions increase with the number of components or geometrical elements (e.g., vertex, edges, faces, etc.) of each part.

An alternative to these complex node-link visualizations is to use a matrix representation, such as the previously introduced DSM. The DSM excels at representing structural relationships and enabling quantitative analysis by maintaining clarity through its predefined and structured tabular format. This approach inherently avoids the visual clutter of node-link diagrams in large-scale systems, without requiring a layout algorithm or tool. However, despite these advantages in representing architectures, capturing the initial semantic information and domain expertise required to create the DSM remains a significant challenge. DSMs face inherent constraints in the initial formation

<!-- PDF_PAGE: 4 -->

of the architecture for capturing semantic complexity and contextual information—all essential elements for comprehensive architectural understanding. For example, Petnga's work[35] demonstrates the analytical power of graph-based approaches once implemented, and it also reveals key challenges in the initial capture and encoding of semantic information. His framework requires significant manual effort to extract and transform SysML model data into labeled property graphs, with users needing expertise across multiple domains, including systems modeling, graph databases (e.g., Neo4j), and specialized query languages (e.g., Cypher). Peterson[36] similarly acknowledges these expertise barriers, noting that while SysML offers robust modeling capabilities, its limited accessibility hampers wider comprehension of the systems-of-interest. These challenges in capturing and encoding semantic information point to a fundamental limitation in graph-based or DSM approaches to initial architectural generation. As systems grow in complexity, incorporating language-based methods into the architectural generation process may provide the semantic richness needed to complement the structural precision of DSM or graph-based methods.

## 2.2.2 Language-Based Methods

Chomsky's transformational grammar[37] laid the groundwork for understanding how language structure might relate to system architecture. By hypothesizing that all human languages share an underlying structure consisting of three fundamental components—a noun as the instrument of action, a verb describing the action, and a noun as the object of the action—Chomsky had already established a parallel to what we would recognize as key elements of system architecture: form, process, and operand[11]. This foundational insight about structural parallels between language and systems has evolved significantly over time. For example, more recent work by Akay and Kim[38] builds on this foundation using advanced language models to demonstrate how design knowledge embedded in textual documentation can be systematically extracted and structured through their "Design Reading" system. Their research shows that when functional requirements (FRs) and design parameters (DPs) are expressed in natural language documentation, they can be automatically identified and hierarchically organized through a recursive decomposition process using question-answering techniques. For instance, they demonstrated how BERT[39], finetuned on question-answering tasks, can extract the highest-level FRs and corresponding DPs, then recursively decompose them into structured hierarchies. This systematic approach to processing design documentation extends Ulrich's framework of product architecture[40] as a scheme mapping function to physical components. From Chomsky's initial insights about language structure to Akay and Kim's demonstration that language models can automatically extract and structure design knowledge from text, we see an evolution in understanding how language, having evolved to describe parts and their relationships, serves as more than a descriptive tool—it potentially encodes the architectural relationships that define system structure. The semantic domain of language has proven to be a faithful mirror of the functional domain of design, allowing modern language processing systems to automatically discern and represent system architectures while preserving their essential relationships and hierarchies. In many cases, natural language processing (NLP), especially LLMs, is utilized to translate existing textual information about an engineering system to a target format such as Enhanced Function-Means (E F-M) Modeling[41] as an extended derivative of axiomatic design[42] or Unified Modeling Language (UML) diagrams[43] as the basis of system modeling language (SysML v1), and Function Behavior Structure (FBS) of systems[44], to name a few.

In a similar sense, recent efforts have been to integrate NLP methods into model-based systems engineering workflows, i.e., SysML-based approaches. By analyzing textual descriptions of systems, NLP methods can help automate certain aspects of the model-based systems engineering process, reducing the manual workload and helping to scale architecture generation. For example, Zhong[45] investigated automatically generating SysML v1 models, focusing particularly on structure and requirement diagrams through natural language processing. While their approach achieved automation in diagram generation, the preparation steps require significant manual work due to their reliance on traditional NLP approaches. Additionally, current research demonstrates a significant increase in the utilization of large language models, mostly to interpret one form of information to another. Furthermore, DeHart[46] explores leveraging Large Language Models (LLMs) for direct interaction with SysML v2, demonstrating how LLMs can serve as an efficient interface for model manipulation and reduce the complexity typically associated with API interactions. While their work shows promising results regarding efficiency and workflow integration, it lacks specific metrics for analyzing LLM output quality and does not address critical challenges such as hallucination prevention and validation methodology for ensuring model accuracy—key considerations for implementing LLMs in technical domains. VanGundy et al. demonstrated the effectiveness of combining LLMs with graph databases for requirement discovery and traceability, showing improved accuracy through validated database queries compared to LLM approaches[47].

These approaches focus on translating textual information into various modeling formats such as graphs, UML diagrams, and SysML models, another important line of research has explored automated generation of architectural representations through matrix-based approaches. One of the first studies to automatically generate DSMs from design matrices was Dong and Whitney's work in 2001, which converted requirement-parameter relationships into component dependencies. However, their approach was limited to square matrices with an equal number of requirements and parameters. Wilschut[48] demonstrated Multi-Domain Matrix (MDM) generation from structured textual specifications in 2018, though their method required manual conversion of natural language documentation into their prescribed grammatical format. Koh[49] recently explored automated DSM generation using LLMs to reduce the traditional time-intensive process of manual DSM creation, though the approach relies on predefined questions, off-the-shelf LLMs, and lacks shared source code or query history.

The evidence demonstrates the potential of natural language processing approaches to translate one form of information to another and create architectural representations while reducing the manual labor necessary to know the domain-specific languages. The question remains: what approaches can best ensure reliability and semantic consistency in these translations while minimizing manual intervention in the process, particularly regarding validating LLM outputs and preventing hallucinations?

<!-- PDF_PAGE: 5 -->

As we explore the challenges and possibilities of automating architectural generation, we must recognize that no single approach can solve every aspect of system complexity. While valuable, many existing methods struggle to scale effectively as system complexity increases. Our goal in the following sections is not to present a final solution to all the challenges in system architecture generation but rather to offer an approach that can help streamline certain aspects of architectural formation and analysis.

Given the complexity of such modern systems, it is natural to approach their representation from an architectural perspective, aiming to understand and resolve system issues through this lens. However, the key question is how to implement this solution effectively. In the remainder of this paper, we present language and augmented language models with their derivatives for doing so. We will highlight existing methodologies and our approach, comparing them programmatically with the available ones, while providing source code and log files of the experiments[50].

## 3 METHOD

In the following sections, we examine various language model variants (LLM, Augmented Language Model-ALM) that enhance this process, their implementation specifics, and their contributions to addressing CPS architectural challenges, as shown in Fig. 2.

## 3.1 Large Language Models-LLMs

As highlighted in the literature, LLMs have demonstrated significant capabilities in processing and understanding natural language text, with emerging abilities to extract semantic relationships from unstructured content. The key aspect that makes LLMs particularly interesting for systems engineering is their ability to process unstructured data (e.g., technical documents) and extract meaningful relationships, potentially requiring relatively less amount of pre-defined templates or structured formats.

Many of these models are autoregressive, trained on extensive text corpora (e.g., FineWeb[53]) to predict the conditional probability of token sequences. To achieve this, they utilize Transformer architectures with self-attention mechanisms[54] to effectively capture long-range dependencies in text. Well-known foundational models, such as DeepSeek[55, 56], ChatGPT[57], Llama[58], and Claude[59], leverage these architectures with vast datasets and scaling techniques[60]. This enables them to perform a wide array of language-based downstream tasks, such as translation, summarization, and reasoning, by generalizing patterns learned during pretraining to novel inputs[61]. However, the underlying statistical nature of these models introduces innate limitations for systems engineering applications. As Buchmann et al. succinctly state, "LLMs are statistical, as opposed to conceptual models."[62] This core characteristic leads to two critical issues: hallucination and semantic drift. While LLMs can generate fluent and plausible-looking output, their probabilistic foundation means they may invent relationships or components that do not exist or fail to capture critical, deterministic technical dependencies accurately.

When applied to systems engineering tasks, the transformer processes engineering-relevant data (e.g., technical documents, graphs, geometrical information, etc.) through tokenization,


![figure_002.png](figure_002.png)



<div align="center">

Figure 2: Overview of a) Baseline LLM b) Baseline LLM with RAG[51] c) LLM with KG and RAG[52]

</div>

converting text into numerical representations that maintain contextual relationships. The attention mechanism enables the model to assign varying levels of importance to different parts of the input, thereby facilitating the identification of crucial technical relationships and dependencies. The model generates output through decoding that converts these numerical representations back into human-readable text while maintaining learned semantics and relationships, as shown in Fig. 2.a.

## 3.2 Augmented Language Models-ALMs

ALMs represent an evolution in language model application that addresses one of the fundamental challenges in architectural generation: ensuring the accuracy and reliability of the generated content[63]. Extensive research has been conducted on identifying hallucinations in outputs generated by LLMs[64], a concern that has grown increasingly significant in technical fields employing LLMs for systems architecture generation.

These issues in LLMs stem from multiple factors, including temporal limitations of training data, incorrect knowledge activation, and imperfect data distribution in the input space[65, 66]. These challenges are particularly acute in technical domains (e.g., engineering system design) where precision is paramount,

<!-- PDF_PAGE: 6 -->


![figure_003.png](figure_003.png)



<div align="center">

Figure 3: An Overview of Step 1 of the proposed approach

</div>

as inaccurate generation can propagate through subsequent errors in system design decisions.

Retrieval-Augmented Generation (RAG) has emerged to overcome these limitations by incorporating external knowledge sources into the generation process. This approach enhances input queries with retrieved documents from specific corpora, leveraging information retrieval mechanisms to supply relevant knowledge to generative LLMs[51, 67]. RAG systems have progressed from specialized retrieval models to more integrated approaches that directly augment standard language models [68, 69].

Experimental evaluations have demonstrated RAG's empirical success across various application domains[70, 71]. This approach has particular significance for architectural generation, where grounding in verified technical documentation and established system knowledge is crucial. The process encompasses both retrievals of relevant architectural documentation and validation of relationships through external knowledge bases[72], as shown in Fig. 2.b.

While traditional RAG approaches rely on direct text chunk retrieval and embedding-based similarity search, graph-based RAG architectures introduce a fundamentally different approach to knowledge organization and retrieval. The key innovation lies in converting source documents into a structured entity knowledge graph, where nodes represent key concepts and edges capture their relationships. This structural representation enables two critical capabilities: (1) the capture of complex relationships between concepts that may be distributed across different text chunks and (2) the ability to leverage graph modularity for efficient information organization.

A distinctive feature of graph-based RAG implementation is its hierarchical processing pipeline. Initially, the system processes source documents to extract entities and relationships using LLM-driven extraction techniques [73]. These elements are then organized into a weighted graph structure where edge weights represent the strength of relationships between entities. The graph is subsequently partitioned into communities using algorithms (e.g., Leiden [74]) to identify closely related concept clusters. This community structure enables a novel "map-reduce" approach to query processing: relevant communities are first identified, parallel summaries are generated for each community, and these summaries are then synthesized into a final response [75].

Where traditional RAG might struggle due to its limited context windows and local relevance matching, graph-based implementations use community structure to maintain a broader context

while reducing computational overhead. Practical implementations in both Neo4J[76] and NebulaGraph[77] environments have demonstrated the scalability of this approach, particularly for queries requiring integration of distributed knowledge.

To realize all highlighted points in Fig. 2 as aligned with the details above while generating the target system's DSM, we employ a three-step procedure:

Step 1 - Preparation of the References and Design Configuration: To utilize downstream LLM tasks (e.g., RAG and graph processes), we need appropriate technical context from known references. In this step, we semi-automate a procedure to extract information from well-known academic search engines (e.g., Google Scholar, Semantic Scholar, Web of Science, Scopus) and crowdsourced project repositories (e.g., Instructables, Hackaday) for the system-of-interest. Scientific literature with high citation counts typically contains accurate expert-level information, representing R1-type knowledge that we can use for the target system-of-interest, while books commonly used in classroom instruction or industrial standards for the system-of-interest provide examples of R2-type (formal or normative) knowledge. By "formal," we mean information typically used to teach students at various levels (e.g., from high school to graduate). Here, we utilize crowdsourced project repositories created mainly by enthusiasts, hobbyists, and makers—many of whom are experts in their fields. However, since these web pages generally aim to be used by entry-level users, their content is primarily suited for non-expert or novice users for the target system-of-interest, hence their classification as R3-type(informal).

This methodological approach demonstrates that the choice of academic search engines and crowdsourced project repositories implicitly and not strictly pre-filters the types of references to be used before the document classification step. After collecting the documents, we proceed with the prompt-engineered classify_docs.py script to classify the downloaded documents for the specific use case. Similar to Ma[78], for enhanced results, we used prompt engineering while highlighting the expertise of the LLM model in our classification queries. Once classified, the documents are formatted as [Year Author] RType-Title.pdf. We then use generate_json.py to create the required configuration files for Step 2 - Process while combining the documents in the same category into a single document and listing them in the reference files parameter of the configuration file. We illustrate this workflow in Fig. 4, including a snippet of the template JSON file. Unlike Yan[79], where an LLM-judge verifies retrieved information during the retrieval process due to the use of the Internet as a reference, our approach pre-specifies and

<!-- PDF_PAGE: 7 -->


![figure_004.png](figure_004.png)



<div align="center">

R: RAG; G: GraphRAG; Mx: Main Code Cell; EC1-iMPLR: Experiment Cell to Post-Process

</div>

<div align="center">

Figure 4: An Overview of Step 2 with associated repository[50] steps

</div>

classifies the documents that will be used in downstream LLM tasks before the fact.

Step 2 - xLM Preparation and Process: Subject to the selected method, we utilized the provided workflows in Fig. 3 (a-LLM, bRAG, and c-GraphRAG) in this step. For RAG and GraphRAG, we first convert the documents to text and clean them by using DocumentLabeler[80]. Then, we created chunks of the texts to be ingested by the target models (e.g., RAG and GraphRAG), while baseline LLM models utilized the existing knowledge of the model (without any documents or fine-tuning). To have a viable comparison between the RAG and GraphRAG, we kept the chunk size and overlap equal for each case. Moreover, in GraphRAG, we autotuned the graph extraction prompts using the framework's built-in capabilities [81] and indexed the target documents before sending our prompts.

Irrespective of the method, we asked the same prompts as shown in Appendix A. While addressing the questions, we ensured that three aspects were covered in our queries: output format specification (e.g., the size of the DSM matrix and its structure), clear and concise instructions (without overlooking the specifics of the systems of interest and domain), and a first-shot example (e.g., an example reflecting uncertainties and another one to reflect the expected output format). The structure of the prompts varies based on the use case, method, and evaluation, as detailed in the supplemental information via configuration files.

The experiments with the ground truth consist of two scenarios (i- with initial subcomponents and ii-without any initial subcomponents). For (i), where we provide the model with the list subcomponents (e.g., for a power screwdriver: ["Bit", "Transmission", "Motor", "Battery Holder", "Electrical System", "Housing", "External"]) and expect the model to determine the existing relationships (e.g., sub-system's spatial proximity, etc.) between those subcomponents, whereas in (ii), we did not provide the list of subcomponents and allowed the model to identify the subcomponents. To do so, in (ii), we utilized an initial prompt for identification of the components, an updated prompt, and a validator prompt, as their details are provided in Appendix A. Once the model inferred the system's subcomponents by using the initial prompt, the updated prompt extracts the relationships between components, and the validator prompts checks the identified subcomponents. After the identification and validation process, the model determines the existing target relationships (e.g., proximity for power screwdriver and wholepart for CubeSat) between those parts. We provide the necessary

details—such as which models and type of compute were used and why—in the Results and Discussion section while sharing our configuration files and process logs in the paper's repository.

Subject to the model, method, and case being run, we analyzed and visualized the results to assess the effectiveness of the models in Step 3.

Step 3 - Analysis and Visualization of the Results: It is imperative to understand the performance of the methods for the specific use cases that we have. In (i), where we provide the model with the list of subcomponents, we analyzed the determination of the existing target relationships in a cell-by-cell manner by using the traditional metrics such as accuracy, precision, recall, and F1-Score. These metrics are calculated using true positives (TP), true negatives (TN), false positives (FP), and false negatives (FN) as follows:

$$
\mathrm {A c c u r a c y} = \frac {\mathrm {T P} + \mathrm {T N}}{\mathrm {T P} + \mathrm {T N} + \mathrm {F P} + \mathrm {F N}}
$$

$$
\mathrm {P r e c i s i o n} = \frac {\mathrm {T P}}{\mathrm {T P} + \mathrm {F P}}
$$

$$
\mathrm {R e c a l l} = \frac {\mathrm {T P}}{\mathrm {T P} + \mathrm {F N}}
$$

$$
\mathrm {F 1 - S c o r e} = \frac {2 \times \mathrm {P r e c i s i o n} \times \mathrm {R e c a l l}}{\mathrm {P r e c i s i o n} + \mathrm {R e c a l l}}
$$

In (ii), we did not provide the list of subcomponents and allowed the model to identify the subcomponents and their target relationships, we incorporated a cosine-similarity based LLM filtration followed by traditional metrics as in (i) on a cell-by-cell basis. Moreover, due to the graph structure of DSMs, we utilized graph-based metrics to evaluate the effect of the subcomponents' alignment globally, compared to the original ground truth. We visualized all these metrics in a bar graph to clearly understand the impact of the method on the (i-determination of the existing target relationships) or (ii-identification of the subcomponents and determination of the existing target relationships) in Figs. 7 and Fig. 8, while including their standard deviations. The graph-based metrics we employed include the edit distance $ ( d_{L1} ) $ and spectral distance $ ( d_{spec} ) $ between design structure matrices A (ground truth) and B (generated) (where $ a_{ij} $ and $ b_{ij} $ are individual

<!-- PDF_PAGE: 8 -->


![figure_005.png](figure_005.png)



<div align="center">

Figure 5: An Overview of Step 3 - Analysis and Visualization

</div>

elements of these matrices and A and B are n x n matrices):

$$
d _ {L 1} (A, B) = \sum_ {i = 1} ^ {n} \sum_ {j = 1} ^ {n} \left| a _ {i j} - b _ {i j} \right|
$$

$$
d _ {s p e c} (A, B) = \sqrt {\sum_ {i = 1} ^ {n} \left(\lambda_ {i} (A) - \lambda_ {i} (B)\right) ^ {2}}
$$

where $ \lambda_{i} ( A ) $ and $ \lambda_{i} ( B ) $ are the eigenvalues of matrices A and B as shown in Fig. 6.

## 4 USE-CASE STUDIES

We demonstrate the effectiveness of our approach through two distinct use cases and examine systems with established architectural structures from literature. There are many documented use cases across diverse domains, including microelectromechanical systems (MEMS) [38], aerospace control systems[82], as well as automotive powertrains and manufacturing systems[83], among many others. For our validation, we specifically focus on architectural structures from CubeSAT systems[84] and a power tool example from Tilstra's product architecture analysis with High-Definition Design Structure Matrix (HDDSM) [85]. These well-documented examples serve as ground truth for comparing and validating our results. While previous studies have investigated LLM effectiveness for various downstream tasks either with ground truth[86] or without it[87], our work uses standard evaluation metrics to provide a comprehensive benchmark for local and global relationships of the DSM structures.

Our investigation of architectural generation for CPS would demonstrate appropriate cases since most complex CPS are iteratively designed from their existing structures rather than being designed from scratch[88,89]. Our approach enables us to dissect existing designs and provide an initial architecture that would lead to future structural modifications—and potentially assist in preventing obsolescence[90] or any other potential technical debts[91] of systems engineering efforts during the design process of CPS. While the solution provides a starting point for architectural development, the generated architectures serve as initial proposals that require expert validation, verification, and further refinement by system architects.

In the following sections, we detail our use cases and testing methodology. To ensure reproducibility, unlike many research studies, we provide our source code[50] with multiple test cases rather than claiming effectiveness based on a single use case with an insufficient number of experiments that supports the methodology.

## 4.1 Architectural Structure of Existing Systems

The presented research examines two distinct systems that provide validation cases for our proposed methodology due to their well-documented component interactions and already-established system architectures.

Power Screwdriver: The Black & Decker power screwdriver represents a consumer product with a documented architecture [92]. It consists of 42 components organized into six main subsystems (bit, transmission, motor, electrical system, battery holder, and housing). Tilstra [85] utilized this product to demonstrate the HDDSM approach, providing detailed documentation of physical connections and functional interactions (including spatial proximity, energy transfer, material flow, and information exchange) which serve as ground truth for our proximity relationship analysis.

CubeSat: CubeSats are standardized nanosatellites based on a 10 $ \times $ 10 $ \times $ 10cm form factor (1U), often scaled up (2U, 3U, etc.), serving diverse missions [93, 94]. However, CubeSats face significant challenges, with failure rates of 35% in academic missions and 25% in industrial applications, often attributed to issues originating in the conceptual design phase [95]. To address these challenges, researchers have applied Model-Based Systems Engineering (MBSE) methodologies for formalized architectural documentation [96, 97]. Friedenthal [84] provided a SysML guide for small satellite architecture, which we use as a basis. CubeSats typically employ a modular architecture with standardized subsystems (structures/thermal, power, attitude control, communications, command/data handling, payload). This standardized structure with documented interfaces [98, 99], especially the whole-part relationships between subsystems, makes CubeSats valuable for validating our architecture generation methods.

Both use cases provide valuable ground-truth architectural structures that can be used to validate generated DSMs based on the extracted information. Tilstra's power screwdriver example offers detailed component-level interactions in a consumer product context, while Friedenthal's spacecraft example demonstrates a more abstract example of a system-of-systems architectural structure in a space application context (e.g., CubeSat).

## 5 RESULTS AND DISCUSSION

Irrespective of the presented methods (LLM, RAG, or GraphRAG), the process of generating DSMs through language models involves two fundamental tasks: component identification and the determination of the existing relationship between pairs. Initially, the models must identify the relevant system components using the provided prompts and subject to the method the documentation that the use-case entails. Then, they must determine the target relationships to populate the DSM struc-

<!-- PDF_PAGE: 9 -->


![figure_006.png](figure_006.png)



<div align="center">

Figure 6: Sample DSM Architecture for a) power screwdriver[85] and b) CubeSat[84]

</div>

ture. At the implementation level, each of our tested methods processes these tasks differently. Basic LLMs depend exclusively on their pre-trained knowledge to identify components and classify their target relationships, while RAG utilizes chunks of relevant documents, and GraphRAG further structures this process by forming a knowledge graph from these document chunks.

The computational demands and model capabilities for these tasks vary significantly. GraphRAG, being the most complex approach, places the highest demands on model performance and computational resources, particularly during the knowledge graph construction (e.g., indexing phase). Therefore, we used GraphRAG performance as our initial constraint for the selection of the models as detailed in Appendix A.2, our reasoning is that the models capable of handling GraphRAG's demands would also perform adequately in simpler baseline LLM and RAG implementations. This approach allowed us to systematically evaluate different hardware configurations (from local GPU setups to cloud infrastructure) and model architectures (from open-source to proprietary) to identify the most suitable combinations for DSM generation.

To thoroughly evaluate these approaches, we conducted our experiments in two phases. First, we analyzed how each method performed in component identification, and then, the identification of the components and existing relationships separately. While doing so, we examined their end-to-end performance in generating complete DSMs. This systematic evaluation allows us to understand not just the final DSM accuracy but also where and why each approach succeeds or fails in the generation process while considering the practical constraints of computational resources and model selection (as presented in Appendix A).

## 5.1 Evaluations of LLM, RAG, and GraphRAG for DSM Generation

In our experiments, we evaluated three distinct methodologies (LLM, RAG, GraphRAG) in parallel to the presented use cases (Power screwdriver and CubeSat). The presented use cases have established ground-truth architectural structures: a Black & Decker power screwdriver's proximity (spatial relationship of the parts) architecture out of nine relationships[85], and a CubeSat nanosatellite system from a sample spacecraft's systems architecture[84]. Our goal is to evaluate the performance of the models for (i) determining the existence of target relationships between the provided systems and in (ii) identifying the components, followed by determining the relationships of identified components. For calculating the cell-level evaluation metrics

discussed in Section 3 (Equations 1-4), model outputs corresponding to the "unsure" state ("2") were excluded to evaluate performance based only on confident predictions of existence ("1") or non-existence ("0"). Furthermore, to enhance the reliability of the results, we conducted each experiment five times and used the global and local evaluation metrics with their standard deviations in the following sections.

For the experiments described below, each API request is treated as an independent operation with no shared memory across calls. Therefore, in the context of chain-of-thought processes implemented as model-to-model validation via a validator in ii—it is necessary to explicitly provide both the query and its corresponding response if any further processing or validation is required (as detailed in Appendix A).

i- Determination of the Existing Relationships of the Pairs: In this evaluation, we provided a list of components and explicitly indicated the types of relationships we aimed to recognize. For the power screwdriver scenario, the targeted relationships were primarily spatial, underscoring the system's physical structure. In contrast, for the CubeSat, the analysis concentrated on delineating system-level whole-part relationships. During experiments, we observed significant performance degradation when details, such as the relationship type or the specific object of interest (e.g., power screwdriver or CubeSat), were omitted. This sensitivity underscores the importance of precise prompt design, as discussed by [100]. Therefore, detailed prompts used in this study are provided in Appendix A as supplementary material.

To assess relationship classification performance, we evaluated five models selected via the method detailed in Appendix A.2. Model sizes ranged from approximately 1.77T parameters (OpenAI gpt-4-turbo-preview) down to 14.8B parameters (deepseekr1:14b). In baseline LLM experiments for spatial reasoning of the power screwdriver, mixtral:8x22b achieved the best overall performance (and best LLM performance), with an F1-Score of 0.849 $ \pm $ 0.074, precision of 0.826 $ \pm $ 0.024, and accuracy of 0.796 $ \pm $ 0.082, despite being smaller than both GPT-4 variants ( $ \approx $ 1.77T parameters). Additionally, deepseek-r1:14b exhibited competitive accuracy （ $ 0.771\pm0.008 $ ）as second-best overall performance, surpassing larger models such as llama3.3:70b. These results suggest that architectural design choices and training methods may influence performance more significantly than model size alone. The high accuracy and precision observed with mixtral:8x22b and deepseek-r1:14b indicate their effectiveness in minimizing false positives—a critical factor for reliable DSM generation.

For the CubeSat scenario, characterized by abstract, high-level whole-part relationships, llama3.3:70b outperformed other models in baseline LLM, achieving accuracy of 0.889 $ \pm $ 0.000, precision of 0.909 $ \pm $ 0.000, recall of 0.909 $ \pm $ 0.000, and an F1-score of 0.909 $ \pm $ 0.000. The superior performance of llama3.3:70b likely stems from its capability to effectively handle higher abstraction levels, suitable for system-level analyses compared to the spatial proximity emphasis in the power screwdriver scenario, though a more detailed architectural or training data analysis would be needed to confirm these potential model specializations.

We further investigated RAG methods by systematically combining all reference sets (R1, R2, R3) to determine whether external knowledge retrieval improved relationship classification. Contrary to initial expectations, simply aggregating all references

<!-- PDF_PAGE: 10 -->


![figure_007.png](figure_007.png)



<div align="center">

Figure 7: Best two predictions of the models and methods for (i) of power screwdriver and CubeSat. (Please see Table 2 and Table 3 in Appendix.)

</div>

did not consistently enhance performance. For CubeSat, performance varied according to model size and architecture. Some configurations performed best with a single reference, while others benefited from multiple references. Notably, certain large-scale models exhibited diminished or plateaued performance when all three references (R1-R2-R3) were combined, highlighting a non-monotonic relationship between retrieved context volume and classification accuracy. Similar behavior was observed for the power screwdriver scenario. Adding more references did not reliably improve performance, indicating greater model sensitivity to specific reference configurations, resulting in significant performance variability. These findings align with the understanding that retrieval-augmented pipelines require careful tuning to avoid introducing irrelevant or conflicting information and pinpointing the exact textual elements within specific references that cause performance shifts (e.g., performance enhancements or bias) would require further detailed investigation beyond the scope of this work. Interestingly, smaller architectures sometimes benefited more from RAG than larger models, a phenomenon also observed in baseline experiments.

This highlights that while the R1/R2/R3 classification showed some correlation with outcome quality, simply aggregating references based on these broad categories does not guarantee optimal performance. The specific combination of documents containing the necessary component and interaction details proved more critical. Future work could investigate more granular content-based relevance scoring for reference selection, potentially moving beyond these high-level source classifications to better predict utility for specific DSM generation tasks. We additionally evaluated GraphRAG, integrating structured graph representations with retrieval-augmented generation. This approach utilized knowledge graphs created from different reference combinations (R1-R2 and R2-R3). GraphRAG showed notable performance gains in specific configurations. For the power screwdriver case, GraphRAG R2-R3 achieved strong performance throughout the models, significantly outperforming some of the baseline LLMs and standard RAG approaches. Similarly, for the CubeSat scenario, GraphRAG provided benefits with gpt-4-turbo-preview and GraphRAG R2-R3.

Additionally, structural similarity metrics (edit and spectral distances) revealed interesting patterns across all methods and models. For the CubeSat scenario, llama3.3:70B with baseline LLM achieved the best structural alignment (edit distance: $ 4. 0 \pm0. 0 $

spectral distance: 0.769 $ \pm $ 0.0), while mixtral:8x22b with baseline LLM showed competitive results for power screwdriver (edit distance: 16.0 $ \pm $ 0.0, spectral distance: 0.781 $ \pm $ 0.157). Various RAG implementations with specific reference combinations also demonstrated good structural correspondence depending on the model used. GPT4-Turbo-Preview with GraphRAG R2-R3 showed strong alignment for power screwdriver (edit distance: 17.361 $ \pm $ 2.038, spectral distance: 0.768 $ \pm $ 0.014). These varied results across different approaches suggest that structural alignment depends significantly on the combination of model architecture, retrieval method, and reference material selection rather than being exclusive to any single approach.

## All these findings are detailed in Fig. 7 and Appendix A.

ii- Identification or the Parts and Determination of the Existing Relationships of the Pairs: In this evaluation, models first predict the component list before determining relationship existence Our analysis considers both raw predictions and aligned results after filtering with LLMs(achieved via cosine similarity between component name embeddings; further details are provided in the code repository [50]). We employ the same evaluation metrics as in i.

Across 500 experiments (as #ofModels $ \times $ #ofRepetitions $ \times $ #ofDocumentCombinations $ \times $ #ofUseCases; where $ 5 \times 5 \times 1 \times 2 $ in LLM; where $ 5 \times 5 \times 7 \times 2 $ in RAG; and where $ 5 \times 5 \times 2 \times 2 $ in GraphRAG) both for power screwdriver and CubeSat in (ii), gpt-4-turbo-preview has consistent performance in the power screwdriver case, and it has the best scores in 5 of those experiments. For our (i) (only identification of existing relationships) and ii (identification of components and their existing relationships) studies, the results differ significantly, the experiments of (ii) have relatively lower top accuracy scores compared to the top accuracy scores of i. The alignment process (filter with LLMs) in (ii) improves the overall accuracies compared to the raw accuracy scores of the model responses, as we presented in Fig. 8 for both power screwdriver and CubeSat use-cases for best two predictions of the complete set of experiments.

Overall, in (ii), baseline RAG's predictions have higher accuracies compared to baseline LLMs, especially for R1-R2, R2-R3, and R1-R2-R3 as references. However, in several experiments, the reason for higher accuracy is the result of the deduction of unmatched parts during the matching and alignment. Hence, one should check both the spectrum distance (to understand how close the system is to the ground truth one) and the DSM

<!-- PDF_PAGE: 11 -->


![figure_008.png](figure_008.png)



<div align="center">

Figure 8: Best two aligned predictions of the models and methods for (ii) of power screwdriver and CubeSat. (Please see Table 4, 5, 6, and 7 for the detailed results and Figs. 9 and 10 for the details of raw and aligned DSMs in Appendix.)

</div>

prediction of the model (to see the reduction in the number of components after the alignment step) while checking the DSM matrix to see the real changes (removal of the parts during the alignment).

The validator generally confirmed the predictions of most models without requiring corrections. However, in experiments involving the deepseek-r1:14b model, which occasionally showed confusion in its reasoning for task (ii), the validator did provide corrections, effectively guiding the model's reasoning process. This would suggest the validator's utility might be model-specific, being more beneficial for models prone to reasoning inconsistencies.

By looking at the performance of baseline RAG, we decide to evaluate only R1-R2 and R2-R3 combinations for baseline GraphRAG.

## 6 CONCLUSION AND FUTURE WORK

In this paper, we investigated the capabilities of LLMs with their RAG, and GraphRAG derivatives in generating DSMs with two distinct use cases: power screwdriver and CubeSat with well-known architectural references, while evaluating two architectural generation tasks: (i) determining relationships between predefined components and (ii) identifying components and their relationships. We assessed performance using both local metrics for cell-level evaluation and global metrics to capture overall architecture. Despite design and computational challenges, we identify opportunities for automated DSM generation, with all code publicly available for reproducibility, enabling domain experts and interested parties to validate results, provide feedback, and contribute domain-specific improvements.

Our experiments demonstrated that model architecture often proves more critical than parameter count for relationship classification tasks. For instance, for the power screwdriver's spatial reasoning, mixtral:8x22b achieved the highest performance, despite being smaller than gpt-4 variants. For CubeSat's wholepart relationships, llama3.3:70B showed best performance. RAG improved performance in specific configurations, but combining all references did not consistently yield improvements, suggesting that careful reference selection is essential. The bestperforming models showed strong structural similarity to ground truth, with the llama3.3:70b model for the CubeSat case and mixtral:8x22b for the power screwdriver case each achieving notable edit distance and spectral distance metrics that confirmed their effectiveness. While these results suggest architectural

choices may outweigh parameter count in some scenarios, further studies across more diverse tasks and models are needed to fully substantiate this trend.

Irrespective of the method, all approaches require consideration of prompt design, as query formulation significantly affects outcomes. This dependency on query design presents considerations for broader application across diverse system types. The methodology was tested on two distinct cases (power screwdriver focusing on spatial proximity, CubeSat focusing on whole-part relationships), providing valuable insights but also highlighting the need for future validation. Extending this work to a broader range of CPS architectures, varying documentation quality, and diverse relationship types (e.g., functional, logical flows) would be crucial to assess the generalizability of these automated DSM generation techniques. The effectiveness of RAG approaches depends on reference document selection and classification, which involves a balance between automation and domain expertise. Computational requirements vary across approaches, with cloud-based models offering faster processing but at a considerably higher cost, while local implementations require substantial hardware resources. The preparation of the experimental setup benefits from domain knowledge to ensure appropriate system representation.

Several research directions could enhance automated DSM generation. Addressing prompt dependency is imperative for broader application, with potential approaches including compiler-like frameworks such as DSpy[100] that can automate the creation of self-improving pipelines for language model calls. Incorporating reasoning models shows promise for competitive architectural results even with smaller models, potentially providing cost-effective alternatives to larger proprietary options. Furthermore, exploring a wider array of LLM architectures, potentially including models fine-tuned specifically for engineering tasks or complex reasoning, could yield deeper insights into the factors driving performance variations beyond just parameter count or reference data. For better integration with detailed design processes, improved connections with Product Lifecycle Management interfaces are needed, particularly focusing on physical viewpoints (e.g., geometric data representations and material aspects). Finally, while LLMs, ALMs, and their derivatives demonstrate understanding and reasoning abilities, they face challenges in real-world task execution. To overcome these limitations, structured agentic frameworks offer significant potential for enhanced performance (e.g., error correction, etc.). Agentic approaches with reasoning and programmatic xLM mechanisms might generate more accurate system archi-

<!-- PDF_PAGE: 12 -->

tectures with multi-level granularity, which we leave for future study.

The authors gratefully acknowledge Dr. Steve Simske and Dr. Emily King for their insightful feedback.

## ACKNOWLEDGEMENTS

## REFERENCES

[1] INCOSE. INCOSE systems engineering handbook. John Wiley & Sons, 2023.

[2] Howard Henry Peckham. The making of the University of Michigan, 1817-1992. University of Michigan Press, 1994.

[3] Roger L Geiger. To advance knowledge: The growth of American research universities, 1900-1940. Routledge, 2017.

[4] Ludwig Von Bertalanffy. The history and status of general systems theory. Academy of management journal, 15(4): 407-426, 1972.

[5] Eric C Honour. A historical perspective on systems engineering. Systems Engineering, 21(3):148-151, 2018.

[6] Niamat Ullah Ibne Hossain, Raed M Jaradat, Michael A Hamilton, Charles B Keating, and Simon R Goerger. A historical perspective on development of systems engineering discipline: a review and analysis. Journal of Systems Science and Systems Engineering, 29:1-35, 2020.

[7] Marco Di Maio, Tim Weilkiens, Omar Hussein, Mostafa Aboushama, Irfan Javid, Sophian Beyerlein, and Michael Grötsch. Evaluating MBSE methodologies using the FEMMP framework. In 2021 IEEE International Symposium on Systems Engineering (ISSE), pages 1-8. IEEE, 2021.

[8] Oliver Von Heissen, Fabian Hanke, Isaac Mpidi Bita, Aschot Hovemann, Roman Dumitrescu, et al. Toward Intelligent Generation of System Architectures. DS 130: Proceedings of NordDesign 2024, Reykjavik, Iceland, 12th-14th August 2024, pages 504-513, 2024.

[9] Dov Dori and Hillary Sillitto. What is a system? An ontological framework. Systems Engineering, 20(3):207- 219, 2017.

[10] Peter A Corning. Complexity is just a word! Technological Forecasting and Social Change, 59(2):197-200, 1998.

[11] Edward Crawley, Bruce Cameron, and Daniel Selva. System architecture: strategy and product development for complex systems. Prentice Hall Press, 2015.

[12] Daniel Whitney, Edward Crawley, Olivier de Weck, Steven Eppinger, Christopher Magee, Joel Moses, Warren Seering, Joel Schindall, and David Wallace. The influence of architecture in engineering systems. Engineering Systems Monograph, MIT Engineering Systems Division, March, 2004.

[13] Olivier L De Weck, Daniel Roos, and Christopher L Magee. Engineering systems: Meeting human needs in a complex technological world. Mit Press, 2011.

[14] Mark W Maier. The art of systems architecting. CRC press, 2009.

[15] Dennis M Buede and William D Miller. The engineering design of systems: models and methods. John Wiley & Sons, 2024.

[16] National Science Foundation. NSF 24-581: CyberPhysical Systems (CPS). Report NSF 24-581, National Science Foundation, Alexandria, VA, June 2024. Published June 4, 2024.

[17] Edward R. Griffor, Christopher Greer, David A. Wollman, and Martin J. Burns. Framework for Cyber-Physical Systems: Volume 1, Overview. NIST Special Publication 1500-201, National Institute of Standards and Technology, June 2017.

[18] Iris Graessler and Julian Hentze. The new V-Model of VDI 2206 and its validation. at-Automatisierungstechnik, 68(5):312-324, 2020.

[19] Ali K Raz, C Robert Kenley, and Daniel A DeLaurentis. System architecting and design space characterization. Systems Engineering, 21(3):227-242, 2018.

[20] Manas Bajaj, Jonathan Backhaus, Tim Walden, Manoj Waikar, Dirk Zwemer, Chris Schreiber, Ghassan Issa, Intercax, and Lockheed Martin. Graph-based digital blueprint for model based engineering of complex systems. In INCOSE International Symposium, volume 27, pages 151-169. Wiley Online Library, 2017.

[21] Florian Schummer and Maximilian Hyba. An Approach for System Analysis with MBSE and Graph Data Engineering. arXiv preprint arXiv:2201.06363, 2022.

[22] Pawel Z Chadzynski, Barclay Brown, and Patrick Willemsen. Enhancing automated trade studies using MBSE, SysML and PLM. In INCOSE International Symposium, volume 28, pages 1626-1635. Wiley Online Library, 2018.

[23] Donald V Steward. The design structure system: A method for managing the design of complex systems. IEEE transactions on Engineering Management, (3):71- 74, 1981.

[24] Steven D Eppinger and Tyson R Browning. Design structure matrix methods and applications. MIT press, 2012.

[25] Tauany LS Santos and Michel S Soares. A survey on what users think about sysml. Systems Engineering, 26 (4):379-392, 2023.

[26] Amir Hooshmand, Matthew I Campbell, and Kristina Shea. Steps in transforming shapes generated with generative design into simulation models. In International Design Engineering Technical Conferences and Computers and Information in Engineering Conference, volume 45028, pages 883-892. American Society of Mechanical Engineers, 2012.

[27] Ashish Khetan, Danny J Lohan, and James T Allison. Managing variable-dimension structural optimization problems using generative algorithms. Structural and Multidisciplinary Optimization, 52:695-715, 2015.

<!-- PDF_PAGE: 13 -->

[28] Clemens Münzer, Bergen Helms, and Kristina Shea. Automatically transforming object-oriented graph-based representations into Boolean satisfiability problems for computational design synthesis. Journal of Mechanical Design, 135(10):101001, 2013.

[29] David F Wyatt, David C Wynn, and P John Clarkson. A scheme for numerical representation of graph structures in engineering design. Journal of Mechanical Design, 136(1):011010, 2014.

[30] Linda C Schmidt, Harshawardhan Shetty, and Scott C Chase. A graph grammar approach for structure synthesis of mechanisms. In International Design Engineering Technical Conferences and Computers and Information in Engineering Conference, volume 80333, page V003T03A034. American Society of Mechanical Engineers, 1998.

[32] Mathieu Jacomy, Tommaso Venturini, Sebastien Heymann, and Mathieu Bastian. ForceAtlas2, a continuous graph layout algorithm for handy network visualization designed for the Gephi software. PloS one, 9(6):e98679, 2014.

[31] Anand P Deshmukh, Daniel R Herber, and James T Allison. Bridging the gap between open-loop and closed-loop control in co-design: A framework for complete optimal plant and control architecture design. In 2015 American Control Conference (ACC), pages 4916-4922. IEEE, 2015.

[33] Yifan Hu. Efficient, high-quality force-directed graph drawing. Mathematica journal, 10(1):37-71, 2005.

[34] Mathieu Bastian, Sebastien Heymann, and Mathieu Jacomy. Gephi: An Open Source Software for Exploring and Manipulating Networks. In International AAAI Conference on Weblogs and Social Media, 2009.

[35] Leonard Petnga. Graph-based Assessment and Analysis of System Architecture Models. In INCOSE International Symposium, volume 29, pages 922-936. Wiley Online Library, 2019.

[36] Troy Peterson. Understanding Systems through Graph Theory and Dynamic Visualization. In Proceedings of the 2014 Ground Vehicle Systems Engineering and Technology Symposium (GVSETS), Novi, MI, USA, pages 4-6, 2015.

[37] Noam Chomsky. Syntactic structures. Mansfield Centre, CT: Martino Publishing, 2015.

[38] Haluk Akay and Sang-Gook Kim. Reading functional requirements using machine learning-based language processing. CIRP Annals, 70(1):139-142, 2021.

[39] Jacob Devlin. Bert: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805, 2018.

[40] Karl Ulrich. The role of product architecture in the manufacturing firm. Research policy, 24(3):419-440, 1995.

[41] Massimo Panarotto, Timos Kipouros, Arindam Brahma, Ola Isaksson, Oskar Strandh Tholin, John Clarkson, et al. Using DSMs in functionally driven explorative design experiments-an automation approach. In DS 121: Proceedings of the 24th International DSM Conference

(DSM 2022), Eindhoven, The Netherlands, October, 11- 13, 2022, pages 68-77, 2022.

[42] Nam P Suh. The principles of design. (No Title), 1990.

[43] Alejandro Pradas Gomez, Petter Krus, Massimo Panarotto, and Ola Isaksson. Large language models in complex system design. Proceedings of the Design Society, 4:2197-2206, 2024.

[44] Boheng Wang, Haoyu Zuo, Zebin Cai, Yuan Yin, Peter Childs, Lingyun Sun, and Liuqing Chen. A Task-Decomposed AI-Aided Approach for Generative Conceptual Design. In International Design Engineering Technical Conferences and Computers and Information in Engineering Conference, volume 87349, page V006T06A009. American Society of Mechanical Engineers, 2023.

[45] Shaohong Zhong, Andrea Scarinci, and Alice Cicirello Natural language processing for systems engineering: automatic generation of systems modelling language diagrams. Knowledge-Based Systems, 259:110071, 2023.

[46] John K DeHart. Leveraging Large Language Models for Direct Interaction with SysML v2. In INCOSE International Symposium, volume 34, pages 2168-2185. Wiley Online Library, 2024.

[47] Braxton VanGundy, Nipa Phojanamongkolkij, Barclay Brown, Ramana Polavarapu, and Joshua Bonner. Requirement Discovery Using Embedded Knowledge Graph with ChatGPT. In INCOSE International Symposium, volume 34, pages 2011-2027. Wiley Online Library, 2024.

[48] T Wilschut, LFP Etman, JE Rooda, and JA Vogel. Generation of a function-component-parameter multi-domain matrix from structured textual function specifications. Research in Engineering Design, 29:531-546, 2018.

[49] Edwin CY Koh. Auto-DSM: Using a Large Language Model to generate a Design Structure Matrix. Natural Language Processing Journal, 9:100103, 2024.

[50] H.S. Bank. xLM-DSM: Accompanying Code to the Publication: Retrieved Augmented Knowledge Graph and Large Language Model-Driven Design Structure Matrix (DSM) Generation of Cyber-Physical Systems. https://github.com/bankh/xLM_DSM, 2024. GitHub repository.

[51] Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Kuttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, et al. Retrieval-augmented generation for knowledge-intensive nlp tasks. Advances in neural information processing systems, 33:9459-9474, 2020.

[52] Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, and Jonathan Larson. From local to global: A graph rag approach to query-focused summarization. arXiv preprint arXiv:2404.16130, 2024.

[53] HuggingFace. Fine Web: The Data Set for Training State of-the-Art LLMs. https://huggingface.co/datasets/HuggingFaceH4/fine-web, 2023. URL https://doi.org/10.52202/079017-0970. Accessed April 2025.

<!-- PDF_PAGE: 14 -->

[54] A Vaswani. Attention is all you need. Advances in Neural Information Processing Systems, 2017.

[55] Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, et al. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. arXiv preprint arXiv:2501.12948, 2025.

[56] Aixin Liu, Bei Feng, Bing Xue, Bingxuan Wang, Bochao Wu, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, et al. Deepseek-v3 technical report. arXiv preprint arXiv:2412.19437, 2024.

[57] Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.

[58] Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, et al. The Ilama 3 herd of models. arXiv preprint arXiv:2407.21783, 2024.

[59] AI Anthropic. The claude 3 model family: Opus, sonnet, haiku. Claude-3 Model Card, 1, 2024.

[60] Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec Radford, Jeffrey Wu, and Dario Amodei. Scaling laws for neural language models. arXiv preprint arXiv:2001.08361, 2020.

[61] Tom B Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. arXiv preprint arXiv:2005.14165, 2020.

[62] Robert Buchmann, Johann Eder, Hans-Georg Fill, Ulrich Frank, Dimitris Karagiannis, Emanuele Laurenzi, John Mylopoulos, Dimitris Plexousakis, and Maribel Yasmina Santos. Large language models: Expectations for semantics-driven systems engineering. Data & Knowledge Engineering, 2024.

[63] Konstantinos Andriopoulos and Johan Pouwelse. Augmenting LLMs with Knowledge: A survey on hallucination prevention. arXiv preprint arXiv:2309.16459, 2023.

[64] Ziwei Ji, Nayeon Lee, Rita Frieske, Tiezheng Yu, Dan Su, Yan Xu, Etsuko Ishii, Ye Jin Bang, Andrea Madotto, and Pascale Fung. Survey of hallucination in natural language generation. ACM computing surveys, 55(12):1-38, 2023.

[65] Nikhil Kandpal, Haikang Deng, Adam Roberts, Eric Wallace, and Colin Raffel. Large language models struggle to learn long-tail knowledge. In International Conference on Machine Learning, pages 15696-15707. PMLR, 2023.

[66] Alex Mallen, Akari Asai, Victor Zhong, Rajarshi Das, Daniel Khashabi, and Hannaneh Hajishirzi. When not to trust language models: Investigating effectiveness of parametric and non-parametric memories. arXiv preprint arXiv:2212.10511, 2022.

[67] Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Mingwei Chang. Retrieval augmented language

model pre-training. In International conference on machine learning, pages 3929-3938. PMLR, 2020.

[68] Urvashi Khandelwal, Omer Levy, Dan Jurafsky, Luke Zettlemoyer, and Mike Lewis. Generalization through memorization: Nearest neighbor language models. arXiv preprint arXiv:1911.00172, 2019.

[69] Sebastian Borgeaud, Arthur Mensch, Jordan Hoffmann, Trevor Cai, Eliza Rutherford, Katie Millican, George Bm Van Den Driessche, Jean-Baptiste Lespiau, Bogdan Damoc, Aidan Clark, et al. Improving language models by retrieving from trillions of tokens. In International conference on machine learning, pages 2206-2240. PMLR, 2022.

[70] Omar Khattab, Keshav Santhanam, Xiang Lisa Li, David Hall, Percy Liang, Christopher Potts, and Matei Zaharia Demonstrate-search-predict: Composing retrieval and language models for knowledge-intensive nlp. arXiv preprint arXiv:2212.14024, 2022.

[71] Ori Ram, Yoav Levine, Itay Dalmedigos, Dor Muhlgay, Amnon Shashua, Kevin Leyton-Brown, and Yoav Shoham. In-context retrieval-augmented language models. Transactions of the Association for Computational Linguistics, 11:1316-1331, 2023.

[72] Sewon Min, Kalpesh Krishna, Xinxi Lyu, Mike Lewis, Wen-tau Yih, Pang Wei Koh, Mohit Iyyer, Luke Zettlemoyer, and Hannaneh Hajishirzi. Factscore: Fine-grained atomic evaluation of factual precision in long form text generation. arXiv preprint arXiv:2305.14251, 2023.

[73] Yuzhe Zhang, Yipeng Zhang, Yidong Gan, Lina Yao, and Chen Wang. Causal graph discovery with retrieval-augmented generation based large language models. arXiv preprint arXiv:2402.15301, 2024.

[74] Vincent A Traag, Ludo Waltman, and Nees Jan Van Eck. From Louvain to Leiden: guaranteeing well-connected communities. Scientific reports, 9(1):1-12, 2019.

[75] Jinheon Baek, Alham Fikri Aji, and Amir Saffari. Knowledge-augmented language model prompting for zero-shot knowledge graph question answering. arXiv preprint arXiv:2306.04136, 2023.

[76] Neo4j. Using a Knowledge Graph to implement a RAG application, 2023. URL https://neo4j.com/blog/developer/knowledge-graph-rag-application/. Accessed: 2025-04-01.

[77] NebulaGraph. NebulaGraph Launches Industry-First Graph RAG: Retrieval-Augmented Generation with LLM Based on Knowledge Graphs, 2023. URL https://www.nebula-graph.io/posts/graph-RAG. Accessed: 2025-04-01.

[78] Kevin Ma, Daniele Grandi, Christopher McComb, and Kosa Goucher-Lambert. Exploring the capabilities of large language models for generating diverse design solutions. arXiv preprint arXiv:2405.02345, 2024.

[79] Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, and Zhen-Hua Ling. Corrective retrieval augmented generation. 2024.

[80] Hasan Sinan Bank and Daniel R Herber. CatalogBank: A Structured and Interoperable Catalog Dataset with a Semi-Automatic Annotation Tool (DocumentLabeler) for

<!-- PDF_PAGE: 15 -->

Engineering System Design. In Proceedings of the ACM Symposium on Document Engineering 2024, pages 1-9, 2024.

[81] Alonso Guevara Fernandez, Katy Smith, Joshua Bradley, Darren Edge, Ha Trinh, Sarah Smith, Ben Cutler, Steven Truitt, and Jonathan Larson. GraphRAG Auto-Tuning Provides Rapid Adaptation to New Domains. https://www.microsoft.com/en-us/research/blog/graphrag-auto-tuning-provides-rapid-adaptation-to-new-domains/, September 2024. Microsoft Research Blog.

[82] Ru Wang, ZhuQin Wei, Haokun Li, Zuoxu Wang, Yu Huang, and Guoxin Wang. Intelligent design exploration method for complex engineered system architecture generation. Journal of Engineering Design, pages 1-39, 2024.

[83] Avner Engel and Yoram Reich. Advancing architecture options theory: six industrial case studies. Systems Engineering, 18(4):396-414, 2015.

[84] Sanford Friedenthal and Christopher Oster. Architecting spacecraft with sysml: A model-based systems engineering approach. CreateSpace Independent Publishing Platform, 2017.

[85] Andrew Harold Tilstra, Carolyn Conner Seepersad, and Kristin L Wood. A high-definition design structure matrix (HDDSM) for the quantitative assessment of product architecture. Journal of Engineering Design, 23(10-11): 767-789, 2012.

[86] Anna C Doris, Daniele Grandi, Ryan Tomich, Md Ferdous Alam, Hyunmin Cheong, and Faez Ahmed. DesignQA: A Multimodal Benchmark for Evaluating Large Language Models' Understanding of Engineering Documentation. arXiv preprint arXiv:2404.07917, 2024.

[87] Wanyu Xu, Maulik Chhabilkumar Kotecha, and Daniel A McAdams. How good is ChatGPT? An exploratory study on ChatGPT's performance in engineering design tasks and subjective decision-making. Proceedings of the Design Society, 4:2307-2316, 2024.

[88] Eun Suk Suh, Michael R Furst, Kenneth J Mihalyov, and Olivier de Weck. Technology infusion for complex systems: A framework and case study. Systems Engineering, 13(2):186-203, 2010.

[89] Zachary Dennis and Thomas Holzer. Machine learning approaches for improving integration of advanced sensors on legacy aircraft. Systems Engineering, 26(6):800-813, 2023.

[90] Baris Egemen Ozkan and Serol Bulkan. Multi-objective approach to forecast design refresh time due to COTS obsolescence. Systems Engineering, 25(3):224-241, 2022.

[91] Howard Kleinwaks, Ann Batchelor, and Thomas H Bradley. Technical debt in systems engineering—A systematic literature review. Systems Engineering, 26(5): 675-687, 2023.

[92] Andrew Harold Tilstra. Representing product architecture and analyzing evolvable design characteristics. 2010.

[93] Christopher A Kitts and Robert J Twiggs. Initial developments in the Stanford SQUIRT program. In Platforms and Systems, volume 2317, pages 178-185. SPIE, 1995.

[94] Dana Clarke, Michael Hicks, Alissa Fitzgerald, Jason Suchman, Robert Twiggs, J Randolf, and Thomas Kenny. Picosat Free Flying Magnetometer Experiment. 1996.

[95] Carlo Girardello, Martin Tajmar, and Carsten Scharlemann. GREATCUBE+: conceptual design tool for CubeSat's design. CEAS Space Journal, 16(3):375-392, 2024.

[96] Louise Anderson, Bjorn Cole, Rose Yntema, Manas Bajaj, Sara Spangelo, David Kaslow, Christopher Lowe, Eric Sudano, Mary Boghosian, Robin Reil, et al. Enterprise modeling for CubeSats. In 2014 IEEE Aerospace Conference, pages 1-16. IEEE, 2014.

[97] L Greg Magone and Steven Simske. A Scalable System Architecture for CubeSat Test & Evaluation for Enhanced Mission Success. In AIAA SCITECH 2025 Forum, page 1026, 2025.

[98] Cal Poly. CDS REV14_1. Technical document, California Polytechnic State University, 02 2022. Accessed: 2025-03-23.

[99] Chin Jamie, Coelho Roland, Foley Justin, and Johnstone Alicia. Basic concepts and processes for first-time CubeSat developers. CubeSat101, CaliforDesign of a CubeSat Testbednia, 2017.

[100] Omar Khattab, Arnav Singhvi, Paridhi Maheshwari, Zhiyuan Zhang, Keshav Santhanam, Sri Vardhamanan, Saiful Haq, Ashutosh Sharma, Thomas T Joshi, Hanna Moazam, et al. Dspy: Compiling declarative language model calls into self-improving pipelines. arXiv preprint arXiv:2310.03714, 2023.

[101] Charles Dickens and Richard Kelly. A Christmas Carol. Broadview literary texts. Broadview Press, Peterborough, Ont, 2003 - 2003. ISBN 1551114763.

<!-- PDF_PAGE: 16 -->

## A APPENDIX A

Below are the LLM prompts as used in 'Step2a_DSL_LLM_RAG.ipynb' The reader can find the output from these prompts in the same IPython Notebook and provided log files (inside '/logs' folder). The structure of the prompts as single sentence per line is purposefully written as presented here and in the code repository. However, due to the limited space on the paper, we cannot reflect that verbatim and present it in the associated prompt boxes below.

Moreover, we present the details of the model selection procedure as well as additional details of the experiments and their complete results as part of the corresponding tables.

## A.1

Power Screwdriver Example Prompt for i:

"" Please identify system-level proximity relationships (in contact) between the components of Power Screwdriver, as listed below, and represent them in a Design Structure Matrix (DSM) format. The relationships should be articulated in plain English, capturing the essence of their interactions. Here is the list of subsystems/components to analyze: ["Bit", "Transmission", "Motor", "Electrical System", "Battery Holder", "Housing", "External Environment"] The DSM should clearly indicate the interactions between these components as 1 exist and 0 does not exist, considering both the presence and nature of these connections. Present the output in a square matrix format (number of rows and columns MUST be the same as the number of components = 7 for this example), with rows and columns labeled accordingly. Diagonal elements should be 1 in DSM matrix since each component interacts with itself. If you don't know the answer, just write 2 for the specific cell that you are unsure of. A worst case scenario of the **as a list of lists** shown below (diagonal elements are 1 and rest are 2). Don't make up an answer. final response = [ [1, 2, 2, 2, 2, 2, 2], [2, 1, 2, 2, 2, 2, 2], [2, 2, 1, 2, 2, 2, 2], [2, 2, 2, 1, 2, 2, 2], [2, 2, 2, 2, 1, 2, 2], [2, 2, 2, 2, 2, 1, 2], [2, 2, 2, 2, 2, 1] ] IMPORTANT: Your response must **ONLY** contain a valid **as a list of lists** in the following example format 7x7 matrix. The below list of lists is just an example format of your response. **Replace** the values with your **actual analysis** while providing your response with parameter of "final response". final response = [ [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 1] ] IMPORTANT: THE FORMAT OF THE OUTPUT MUST BE AS LIST OF LISTS ONLY SIMILAR TO THE ONE ABOVE (NO LATEX, CODE, OR OTHER ENCODINGS). """

"" Please identify system-level proximity relationships between the components of power screwdriver, and represent them in a Design Structure Matrix (DSM) format.

The relationships should be articulated in plain English, capturing the essence of their interactions.

The DSM should clearly indicate the interactions between these components as 1 exist and 0 does not exist, considering both the presence and nature of these connections.

Present the output in a square matrix format (number of rows and columns MUST be the same as the number of identified components), with rows and columns labeled accordingly.

Diagonal elements should be 1 in DSM matrix since each component interacts with itself.

If you don't know the answer, just write 2 for the specific cell that you are unsure of. A worst case scenario of the **as a list of lists** shown below (diagonal elements are 1 and rest are 2).

Don’t make up an answer.

This is an example of the output format for 7 components (as 7x7 matrix)-based on our system-of-interest the size of the matrix can change.

"final_response": [ [1, 2, 2, 2, 2, 2], [2, 1, 2, 2, 2, 2], [2, 2, 1, 2, 2, 2], [2, 2, 2, 1, 2, 2], [2, 2, 2, 1, 2, 2], [2, 2, 2, 2, 1, 2], [2, 2, 2, 2, 2, 1]]

IMPORTANT: Your response must **ONLY** contain a valid **as a list of lists** as JSON in the following example format 7x7 matrix.

The below list of lists is just an example format of your response. **Replace** the values with your **actual analysis** while providing your response with parameter of "final response".

This is an example of the output format for 7 components (as 7x7 matrix)-based on our system-of-interest the size of the matrix can change.

IMPORTANT: Your response MUST be a valid JSON object in the following format:

"final_response": [[1,0,0,0,0,0],

[0,1,0,0,0,0,0], ...] """

## CubeSat Example Prompt 1 for i:

_prompt = f"" Please identify system-level config.relationship_type relationships between the components of config.concept_name, as listed below, and represent them in a Design Structure Matrix (DSM) format. The relationships should be articulated in plain English, capturing the essence of their interactions. Here is the list of subsystems/components to analyze: config.predicted_components The DSM should clearly indicate the interactions between these components as 1 exist and 0 does not exist, considering both the presence and nature of these connections. Present the output in a square matrix format (number of rows and columns MUST be the same as the number of components =

<!-- PDF_PAGE: 17 -->

len(config.predicted_components) for this example), with rows and columns labeled accordingly. Diagonal elements should be 1 in DSM matrix since each component interacts with itself. If you don't know the answer, just write 2 for the specific cell that you are unsure of. A worst case scenario of the **as a list of lists** shown below (diagonal elements are 1 and unsure ones are 2). Don't make up an answer. final response = [[1, 2, 2, 2, 2, 2, 2],[2, 1, 2, 2, 2, 2, 2],[2, 2, 1, 2, 2, 2, 2],[2, 2, 2, 1, 2, 2, 2],[2, 2, 2, 1, 2, 2],[2, 2, 2, 2, 2, 1]] for 7 components final response = [[1, 2, 2],[2, 1, 2],[2, 2, 1]] for 3 components IMPORTANT: Your response must **ONLY** contain a valid **as a list of lists** in the following example format 7x7 matrix. The below list of lists is just an example format of a response. **Replace** the values with your actual analysis** while providing your response with parameter of "final response". final response = [[1, 0, 0, 0, 0, 0],[0, 1, 0, 0, 0, 0],[0, 0, 1, 0, 0, 0, 0],[0, 0, 0, 1, 0, 0, 0],[0, 0, 0, 0, 1, 0, 0],[0, 0, 0, 0, 0, 1]] for 7 components final response = [[1, 0, 0],[0, 1, 0],[0, 0, 1]] for 3 components IMPORTANT: THE FORMAT OF THE OUTPUT MUST BE AS LIST OF LISTS ONLY SIMILAR TO THE ONE ABOVE (NO LATEX, CODE, OR OTHER ENCODINGS). ""

Above, 'config.predicted_components' is not empty, unlike in the (ii) provided below. This way, we were able to generalize and parameterize for both cases. In (ii), the identification prompt determines the predicted components, and hence, it is utilized accordingly in the following steps. Identification prompt ii:

prompt = f"" Please identify the major components of self.config.concept_name in the self.config.application_domain based on self.config.relationship_type relationships. The number of components must be len(self.original_components) and must be a list of strings. Please do not identify similar components that will work together under subsystem level since our interest is to identify the major components that form the core architecture of the system. Here is an example of the components for made-up system: final response = [ "component 1", "component 2", "component 3", "component 4", "component 5" ] IMPORTANT: THE FORMAT OF THE OUTPUT MUST BE AS A LIST OF STRINGS ONLY SIMILAR TO THE ONE ABOVE (NO LATEX, NO CODE, NO DESCRIPTION, OR OTHER ENCODINGS). ""

CubeSat Example Update Prompt 1 for ii:

_prompt = f"" Please identify system-level config.relationship_type relationships between the components of config.concept_name, as listed

below, and represent them in a Design Structure Matrix (DSM) format.

The relationships should be articulated in plain English, capturing the essence of their interactions.

Here is the list of subsystems/components to analyze: config.predicted_components

The DSM should clearly indicate the interactions between these components as 1 exist and 0 does not exist, considering both the presence and nature of these connections.

Present the output in a square matrix format (number of rows and columns MUST be the same as the number of components = len(config.predicted_components) for this example), with rows and columns labeled accordingly.

Diagonal elements should be 1 in DSM matrix since each component interacts with itself.

If you don't know the answer, just write 2 for the specific cell that you are unsure of. A worst case scenario of the **as a list of lists** shown below (diagonal elements are 1 and unsure ones are 2). Don't make up an answer.

final response = [[1, 2, 2, 2, 2, 2], [2, 1, 2, 2, 2, 2], [2, 2, 1, 2, 2, 2], [2, 2, 2, 1, 2, 2], [2, 2, 2, 2, 1, 2], [2, 2, 2, 2, 2, 1]] for 7 components

final response = [[1, 2, 2], [2, 1, 2], [2, 2, 1]] for 3 components

IMPORTANT: Your response must **ONLY** contain a valid **as a list of lists** in the following example format 7x7 matrix (NO LATEX, NO CODE, NO DESCRIPTION, OR OTHER ENCODINGS, JUST THE LIST OF LISTS).

The below list of lists is just examples format of a response. **Replace** the values with your **actual analysis** while providing your response with parameter of "final response".

final response = [[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]] for 7 components

final response = [[1, 0, 0], [0, 1, 0], [0, 0, 1]] for 3 components

IMPORTANT: THE FORMAT OF THE OUTPUT MUST BE AS LIST OF LISTS ONLY SIMILAR TO THE ONE ABOVE (NO LATEX, NO CODE, NO DESCRIPTION, OR OTHER ENCODINGS, JUST THE LIST OF LISTS). """

## Validator prompt:

validation_prompt = f"" You are a validator. Review this response based on the requirements of the original prompt: Original prompt: original_prompt Response: raw_response Requirements: 1- Response must follow the format in the original prompt. 2- Response must have the same number of components as the original prompt. Answer only with "Valid" or "Invalid". ""

## A.2 Selection of the Models and Compute for the Experiments

For initial benchmarking, we tested relatively small and open source models (e.g., mistral:latest-4k, llama3.2:1b/3b) on an entry-level gaming laptop (Gigabyte G6) equipped with an Intel

<!-- PDF_PAGE: 18 -->

<div align="center">

Table 1: Model and Experimental Details (as more details provided in GitHub Repository)

</div>

<table border="1"><tr><td>Model</td><td>Embedding</td><td>Compute</td><td>CodeBase</td><td>Cost|Duration</td><td>Input</td><td>Quality(# of Nodes)</td></tr><tr><td>gpt4tp-OAI</td><td>TE3s-OAI</td><td>OAI Infra</td><td>MS-GraphRAG</td><td>4.87 USD</td><td>CC-Dickens</td><td>High(208nodes)</td></tr><tr><td>gpt4o-OAI</td><td>TE3s-OAI</td><td>OAI Infra</td><td>MS-GraphRAG</td><td>1.18 USD</td><td>CC-Dickens</td><td>High(267nodes)</td></tr><tr><td>mistral</td><td>TE3s-OAI</td><td>HP Victus</td><td>MS-GraphRAG</td><td>33 mins 2secs</td><td>CC-Dickens</td><td>Low(460nodes)</td></tr><tr><td>deepseek-llm</td><td>TE3s-OAI</td><td>HP Victus</td><td>MS-GraphRAG</td><td>1hr 30mins</td><td>CC-Dickens</td><td>Low(17nodes)</td></tr><tr><td>llama3.2:3b</td><td>TE3s-OAI</td><td>HP Victus</td><td>MS-GraphRAG</td><td>24mins 6secs</td><td>CC-Dickens</td><td>Low(59nodes)</td></tr><tr><td>mixtral-8x22b</td><td>NET-Ollama</td><td>Tensorcraft</td><td>MS-GraphRAG</td><td>4hrs 11mins</td><td>CC-Dickens</td><td>High(587nodes)</td></tr><tr><td>llama3.3:70b</td><td>NET-Ollama</td><td>Tensorcraft</td><td>MS-GraphRAG</td><td>2hrs 48mins</td><td>CC-Dickens</td><td>High(600nodes)</td></tr><tr><td>ds-r1:14b</td><td>TE3s-OAI</td><td>Tensorcraft</td><td>MS-GraphRAG</td><td>1hr 18mins</td><td>CC-Dickens</td><td>High(499nodes)</td></tr><tr><td colspan="7">TE3:Text-embedding-small,NET:Nomic-Embed-Text,OAI:OpenAI,CC:Christmas Carol[101],MS:Microsoft,DS:DeepSeek</td></tr></table>

i7-13620HX CPU, 64GB RAM, and a power-limited NVIDIA GeForce RTX 4060 mobile GPU (8GB vRAM) and more moderate (HP Victus) with an Intel i7-13700HX, 64GB RAM, and a NVidia GeForce RTX 4060 mobile GPU (8GB vRAM). While this setup allowed for rapid iteration, it became clear that the limited vRAM and smaller context windows of the models that can fit into this vRAM were insufficient, especially during GraphRAG indexing.

For more demanding open-source models (e.g., mixtral:8x22B, llama3.3:70b, etc.), we leveraged our custom multi-GPU workstation (Craftnetics TensorCraft-Red) featuring an AMD EPYC CPU, 504GB RAM, and six AMD RDNA3 GPUs with a combined 144GB vRAM. This setup enabled better performance when handling larger architectural graphs and multi-level retrieval processes. However, compared to proprietary models with cloud-infrastructure, the processing time remained a concern, particularly in GraphRAG implementations requiring graph indexing and retrieval augmentation.

For proprietary models, we relied on OpenAI's cloud infrastructure through API access. The lack of transparency in hardware specifications was offset by significantly faster inference times and a more optimized tokenization process, particularly for RAG and GraphRAG tasks. Despite a non-negligible cost per request, OpenAI models consistently provided high-quality node extractions during the indexing step of the GraphRAG in a short notice.

During preliminary tests, we also evaluated embedding models to balance local and cloud-based computations. Specifically, we utilized OpenAI's text-embedding-3-small (te3s) against Nomic's nomic-embed-text (net) for vector storage and retrieval using ChromaDB. The combination of local LLMs with cloudbased embeddings helped offload GPU workload while improving retrieval consistency for resource-constrained hardware. Furthermore, the per-token costs (0.02 cents per million tokens for 'text-embedding-3-small' ) would be a limit for larger datasets.

To benchmark indexing and clustering performance, we tested a baseline dataset consisting of Charles Dickens's A Christmas Carol[101]. This text provides a controlled environment to compare model performance, retrieval efficiency, and indexing overhead. From these trials, we determined that smaller models lacked the necessary performance for GraphRAG-based knowledge graph extraction. This led us to exclude them from further analysis for the whole set of experiments with other methods. Instead, we focused on a refined selection of models that performed best in these tests, including mixtral-8x22b, llama 3.3:70b, deepseek-r1:14b, gpt-4-o, and gpt-4-turbo-preview, for the remainder of the study.

Additionally, we identified scalability constraints in deepseekr1:32b, which, despite its promising architecture, suffered from long response times and server errors (500 timeout issues) in GraphRAG indexing tasks locally. As a result, we excluded deepseek-r1:32b from further experiments, prioritizing models that maintained a balance between performance and usability Our thinking by selecting 14b over 32b is having a comparison between a relatively larger model without reasoning and showing the performance of a smaller model that can run on relatively resource-constrained hardware with reasoning.

## A.3 Some Remarks for the Experiments

Here, during our experiments—especially for local LLMs, one needs to pay close attention to the context window size and embedding length of the model that is used. The default context window in Ollama is purposefully small (2048) and needs to be changed, as we detailed in our repository. Otherwise, the results of the GraphRAG will be quite poor for the open-source models, and in some cases, a lot of errors occur. In addition to this, to have a proper entity detection from the text, the user has to pay attention to some of the parameters, especially 'Number_of_gleanings' and 'chunk_size'. A small 'chunk_size' will identify the entities poorly since the LLM will only process within the provided 'chunk_size' and irrespective of the chunk size, as the number of gleanings (passes) increases the number of identified entities [52].

In the light of these foregoing points, we conduct the benchmark for the some variation of RAG experiments with appropriate setting of the parameters (Chunk_size=1200; Overlap=100; Number_of_gleanings=1 for GraphRAG in 'settings.yaml' and num_ctx=maximum embedding size for the corresponding Ollama models). Because of the required time and cost for the indexing step, we limited the GraphRAG experiments with the best case of the RAG. Hence, we utilized R1-R2 and R2-R3 cases for GraphRAG in our evaluations.

For the baseline LLM approach, we evaluated both proprietary and open-source models. The proprietary models included gpt 4-turbo-preview and gpt-4-o, while the open-source models encompass llama3.3:70B, mixtral:8x22B, and deepSeek-R1:14B. In the following tables, we provide complementary information to Fig. 7 and Fig 8, where we present the best result out of other possible combinations of the references for i and ii tasks.

<!-- PDF_PAGE: 19 -->

<div align="center">

PREPRINT - RETRIEVAL AUGMENTED (KG), AND LLM-DRIVEN DSM GENERATION OF CPS

</div>

<table border="1"><tr><td>Graph RAG R2-R3</td><td>Graph RAG R1-R2</td><td>RAG R1-R2-R3</td><td>RAG R2-R3</td><td>RAG R1-R2</td><td>RAG R3</td><td>RAG R2</td><td>RAG R1</td><td>LLM</td><td></td></tr><tr><td>0.9522±0.0239
0.7091±0.0223
0.8124±0.0120
0.8000±0.0111
7.2000±0.4000
1.7361±0.2308</td><td>0.8774±0.0230
0.7182±0.0530
0.7891±0.0376
0.7667±0.0377
8.4000±1.3565
1.6225±0.3639</td><td>0.7857±0.000
1.0000±0.000
0.8800±0.0000
0.8333±0.0000
6.0000±0.000
1.0981±0.000</td><td>0.7857±0.000
1.0000±0.000
0.8800±0.0000
0.8333±0.0000
6.0000±0.000
1.0981±0.000</td><td>0.7857±0.000
1.0000±0.000
0.8800±0.0000
0.8333±0.0000
6.0000±0.000
1.0981±0.000</td><td>0.7857±0.000
1.0000±0.000
0.8800±0.0000
0.8333±0.0000
6.0000±0.000
1.0981±0.000</td><td>0.7857±0.000
1.0000±0.000
0.8800±0.0000
0.8333±0.0000
6.0000±0.000
1.0981±0.000</td><td>0.8212±0.0269
0.9545±0.000
0.8826±0.0152
0.8444±0.0222
5.6000±0.8000
1.1076±0.1257</td><td>1.77T/128k/128k</td></tr><tr><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>0.6111±0.000
1.0000±0.000
0.7586±0.0000
0.6111±0.0000
20.0000±4.8990
3.6344±0.6970</td><td>1.77T/128k/128k</td></tr><tr><td>0.7462±0.077
0.9364±0.0364
0.8303±0.0193
0.7667±0.0222
8.4000±0.8000
0.9989±0.0229</td><td>0.7500±0.000
0.9545±0.000
0.8400±0.0000
0.7778±0.0000
8.0000±0.000
0.9875±0.0000</td><td>0.7538±0.0077
0.9455±0.0182
0.8387±0.0027
0.7778±0.0000
8.0000±0.000
0.9420±0.0909</td><td>0.7692±0.0385
0.9636±0.0182
0.8553±0.0307
0.8000±0.0444
7.2000±1.600
0.9556±0.0669</td><td>0.7500±0.000
0.9545±0.000
0.8400±0.022
0.7778±0.000
8.0000±0.000
0.9875±0.0000</td><td>0.7294±0.0412
0.9636±0.0182
0.8291±0.0217
0.7556±0.0444
8.0000±1.6000
1.1956±0.4163</td><td>0.7167±0.0583
0.9818±0.0364
0.8258±0.0219
0.7444±0.0444
9.2000±1.6000
1.5149±0.4598</td><td>0.7692±0.0000
0.9091±0.0000
0.8333±0.0000
0.7778±0.0000
8.0000±0.000
2.0927±0.1290</td><td>140.6B/65k/6k</td></tr><tr><td>0.7143±0.000
0.9091±0.000
0.8000±0.000
0.7222±0.000
10.000±0.000
0.9875±0.0000</td><td>0.7143±0.000
0.9091±0.000
0.8000±0.000
0.7222±0.000
10.000±0.000
0.9875±0.0000</td><td>0.9091±0.0000
0.9091±0.0000
0.8696±0.0000
0.8889±0.0000
4.000±0.000
0.7688±0.0000</td><td>0.9091±0.0000
0.9091±0.0000
0.8696±0.0000
0.8889±0.0000
4.000±0.000
0.7688±0.0000</td><td>0.9091±0.0000
0.9091±0.0000
0.8696±0.0000
0.8889±0.0000
4.000±0.000
0.7688±0.0000</td><td>0.9091±0.0000
0.9091±0.0000
0.8696±0.0000
0.8889±0.0000
4.000±0.000
0.7688±0.0000</td><td>0.9091±0.0000
0.9091±0.0000
0.8696±0.0000
0.8889±0.0000
4.000±0.000
0.7688±0.0000</td><td>70.6B/131k/8k</td></tr><tr><td>0.9515±0.0243
0.7000±0.0223
0.8062±0.0141
0.7944±0.0136
7.4000±0.4899
1.7986±0.2164</td><td>0.7333±0.000
1.0000±0.0000
0.8462±0.0000
0.7778±0.0000
8.0000±0.000
1.5634±0.0000</td><td>0.6551±0.0162
1.000±0.000
0.7915±0.0116
0.6778±0.0222
11.6000±0.8000
2.0073±0.0418</td><td>0.6308±0.0394
1.0000±0.0000
0.7729±0.0286
0.6389±0.0556
41.8000±16.4000
6.9151±2.5972</td><td>0.6471±0.0000
1.000±0.0000
0.7857±0.0000
0.6667±0.0000
12.000±0.0000
2.0282±0.0000</td><td>0.6510±0.0078
0.9818±0.0364
0.7824±0.0066
0.6667±0.0000
12.000±0.0000
2.0282±0.0000</td><td>0.7612±0.0916
0.8909±0.0739
0.8129±0.0326
0.7444±0.0733
15.20±14.4416
2.2995±2.7703</td><td>0.7754±0.0422
0.9364±0.0364
0.8481±0.0387
0.7944±0.544
7.4000±1.9596
0.8496±0.0697</td><td>0.7233±0.0017
0.9273±0.0545
0.8120±0.0230
0.7389±0.0222
9.4000±0.8000
1.1013±0.0920</td></tr></table>

Table 2: Performance metrics of Cubesat for i across methods and models. Each cell has from left to right (Precision, Recall, F1-Score, Accuracy, Edit Distance, and Spectral Distance). Values in each cell are the average of five experiments. The total of $ 5 0 \times5=2 5 0 $ experiments.

<!-- PDF_PAGE: 20 -->

<div align="center">

PREPRINT - RETRIEVAL AUGMENTED (KG), AND LLM-DRIVEN DSM GENERATION OF CPS

</div>

<table border="1"><tr><td>Graph RAG R2-R3</td><td>Graph RAG R1-R2</td><td>RAG R1-R2-R3</td><td>RAG R2-R3</td><td>RAG R1-R2</td><td>RAG R3</td><td>RAG R2</td><td>RAG R1</td><td>LLM</td><td></td></tr><tr><td>0.8537±0.0402
0.6970±0.000
0.7670±0.000
0.7143±0.0258
14.000±1.2649
1.0194±0.1150</td><td>0.7419±0.0764
0.7091±0.1504
0.7206±0.1098
0.6408±0.1275
17.600±6.2482
1.0876±0.2668</td><td>0.7277±0.0489
0.7697±0.0594
0.7469±0.0457
0.6490±0.0663
17.2000±3.2496
1.1314±0.5593</td><td>0.7624±0.0251
0.6970±0.0000
0.7280±0.0114
0.6490±0.02000
17.2000±0.9798
0.9683±0.0408</td><td>0.7265±0.0497
0.7212±0.0297
0.7218±0.0165
0.6245±0.0400
18.4000±1.9596
1.0816±0.5881</td><td>0.7279±0.0388
0.7333±0.0297
0.7291±0.0107
0.6327±0.0258
18.0000±1.2649
0.9718±0.2526</td><td>0.7900±0.0061
0.6848±0.0242
0.7335±0.0163
16.4000±0.8000
0.9554±0.0741</td><td>0.7758±0.0218
0.7091±0.0242
0.7404±0.0124
0.6653±0.0163
16.4000±0.8000
0.8585±0.1645</td><td>0.6082±0.0457
0.7333±0.0485
0.7159±0.0171
0.7673±0.0835
19.2000±1.6000
0.8185±0.2308</td><td>1.77T/128k/128k</td></tr><tr><td>na
na
na
na
na
na</td><td>na
na
na
na
na
na</td><td>na
na
na
na
na
na</td><td>na
na
na
na
na
na</td><td>na
na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>0.8117±0.0258
0.6242±0.0707
0.7034±0.0481
0.6490±0.0416
17.2000±2.0396
1.2926±0.3513</td><td>1.77T/128k/128k</td></tr><tr><td>0.8532±0.0258
0.6970±0.0000
0.7670±0.0162
0.7143±0.0258
14.000±1.2649
1.0194±0.1150</td><td>0.7521±0.0094
0.8788±0.0606
0.8092±0.0185
0.7224±0.0163
13.600±0.800
2.0466±0.2143</td><td>0.7218±0.0404
0.7091±0.0242
0.7139±0.0097
0.6163±0.0327
18.8000±1.6000
1.0125±0.1774</td><td>0.7980±0.0575
0.6121±0.0121
0.6924±0.0288
0.6327±0.0408
18.0000±2.000
2.1441±0.2258</td><td>0.7419±0.0000
0.6970±0.0000
0.7188±0.0000
0.6327±0.0000
18.0000±4.0000
0.9238±0.0000</td><td>0.7108±0.0623
0.6606±0.0727
0.6847±0.0681
0.5918±0.0816
20.0000±4.0000
0.8909±0.0658</td><td>0.6848±0.0147
0.6606±0.0485
0.6721±0.0316
0.5673±0.0327
21.2000±1.6000
1.1346±0.0810</td><td>0.7980±0.0575
0.6121±0.0121
0.6924±0.0288
0.6327±0.0408
18.0000±2.0000
2.1551±0.2038</td><td>0.8258±0.0240
0.8788±0.1212
0.8486±0.0743
0.7959±0.0816
10.0000±4.000
0.9162±0.1020</td><td>140.6B/65k/6k</td></tr><tr><td>0.8519±0.000
0.6970±0.000
0.7667±0.000
0.7143±0.000
14.000±0.000
1.0334±0.000</td><td>0.8519±0.000
0.6970±0.000
0.7667±0.000
0.7143±0.000
14.000±0.000
1.0334±0.000</td><td>0.7108±0.0142
0.5636±0.0242
0.6281±0.0105
0.5510±0.0000
22.000±0.000
1.1997±0.3541</td><td>0.6970±0.0000
0.6970±0.0000
0.6970±0.0000
0.5918±0.0000
22.000±0.000
1.3170±0.0000</td><td>0.7037±0.0000
0.5758±0.0000
0.6333±0.0000
0.5510±0.0000
22.000±0.000
1.1997±0.3541</td><td>0.7108±0.0142
0.5636±0.0242
0.6281±0.0105
0.5510±0.0000
22.000±0.000
1.1997±0.3541</td><td>0.6774±0.0000
0.6364±0.0000
0.6562±0.0000
0.5510±0.0000
22.000±0.000
1.1751±0.0000</td><td>0.6970±0.0000
0.6970±0.0000
0.6970±0.0000
0.5918±0.0000
22.000±0.000
1.9079±0.0000</td><td>70.6B/131k/8k</td></tr><tr><td>na
na
na
na
na</td><td>0.8400±0.000
0.6364±0.000
0.7241±0.000
0.6735±0.000
16.000±0.000
1.7049±0.000</td><td>0.7990±0.0698
0.7758±0.1236
0.7756±0.0212
0.7020±0.0163
24.400±20.3037
2.7900±3.3631</td><td>0.7552±0.0717
0.8545±0.1291
0.7900±0.0260
0.6980±0.0300
34.4000±25.0088
4.3374±4.2319</td><td>0.6974±0.0479
0.9394±0.1212
0.7923±0.0252
0.6735±0.0000
55.2000±19.6000
7.8540±3.3218</td><td>0.7251±0.0681
0.8364±0.1265
0.7659±0.0332
0.6735±0.0000
55.2000±19.3763
3.1958±3.2034</td><td>0.7263±0.0652
0.9030±0.1248
0.7950±0.0270
0.6898±0.0327
26.4000±19.3763
3.1958±3.2034</td><td>0.7901±0.0626
0.7273±0.1472
0.7448±0.0522
0.6735±0.0447
24.6000±19.7221
3.0330±3.2685</td><td>0.7849±0.0900
0.7879±0.1897
0.7673±0.0835
0.6939±0.0774
24.800±20.4490
3.1968±3.1978</td><td>14.8B/131k/5k</td></tr></table>

Table 3: Performance metrics of power screwdriver for i across methods and models. Each cell has from left to right (Precision, Recall, F1-Score, Accuracy, Edit Distance, and Spectral Distance). Values in each cell are the average of five experiments. The total of $ 5 0 \times5=2 5 0 $ experiments.

<!-- PDF_PAGE: 21 -->

<div align="center">

PREPRINT - RETRIEVAL AUGMENTED (KG), AND LLM-DRIVEN DSM GENERATION OF CPS

</div>

<table border="1"><tr><td>Graph RAG R2-R3</td><td>Graph RAG R1-R2</td><td>RAG R1-R2-R3</td><td>RAG R2-R3</td><td>RAG R1-R2</td><td>RAG R3</td><td>RAG R2</td><td>RAG R1</td><td>LLM</td><td></td></tr><tr><td>0.650±0.050
0.950±0.100
0.731±0.034
0.611±0.070
14.000±2.530
2.429±0.992</td><td>0.578±0.000
0.900±0.0000
0.698±0.000
0.572±0.000
15.400±0.800
2.359±1.034</td><td>0.448±0.000
0.650±0.000
0.531±0.000
0.361±0.000
23.000±0.000
1.489±0.000</td><td>0.579±0.999
0.550±0.0000
0.564±0.000
0.528±0.000
17.000±0.000
1.799±0.000</td><td>0.556±0.000
1.000±0.000
0.714±0.000
0.556±0.000
16.000±0.000
3.199±0.000</td><td>0.520±0.000
0.650±0.000
0.578±0.000
0.472±0.000
19.0000±0.000
1.225±0.000</td><td>0.550±0.000
0.550±0.000
0.550±0.000
18.000±0.000
1.799±0.000</td><td>0.571±0.000
0.600±0.000
0.585±0.000
0.528±0.000
17.000±0.000
2.179±0.000</td><td>0.600±0.000
0.900±0.000
0.720±0.000
0.611±0.000
14.000±0.000
2.027±0.000</td><td>1.77T/128k/128k</td></tr><tr><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>0.8117±0.0258
0.6242±0.0707
0.7034±0.0481
0.6490±0.0416
17.2000±2.0396
1.2926±0.3513</td><td>gpt4o</td><td>1.77T/128k/128k</td></tr><tr><td>0.562±0.000
0.900±0.0000
0.692±0.000
0.556±0.000
16.0000±0.000
2.188±0.000</td><td>0.562±0.000
0.900±0.0000
0.692±0.000
0.556±0.000
16.000±0.000
2.188±0.000</td><td>0.625±0.000
1.000±0.000
0.769±0.000
0.667±0.000
12.000±0.000
2.188±0.000</td><td>0.625±0.000
1.000±0.000
0.769±0.000
0.667±0.000
12.0000±0.000
2.188±0.000</td><td>0.588±0.000
1.000±0.000
0.769±0.000
0.667±0.000
14.0000±0.000
2.188±0.000</td><td>0.625±0.000
0.500±0.000
0.769±0.000
0.667±0.000
20.000±0.0000
2.188±0.000</td><td>0.625±0.000
1.000±0.000
0.769±0.000
0.667±0.000
12.0000±0.000
2.188±0.000</td><td>0.588±0.000
1.000±0.000
0.741±0.000
0.611±0.000
14.000±0.000
2.188±0.000</td><td>140.6B/65k/6k</td></tr><tr><td>0.615±0.0000
0.800±0.0000
0.696±0.0000
0.611±0.0000
14.0000±0.0000
1.367±0.0000</td><td>0.615±0.0000
0.800±0.0000
0.696±0.0000
0.611±0.0000
14.0000±0.0000
1.367±0.0000</td><td>0.600±0.000
0.600±0.000
0.556±0.0000
16.000±0.000
1.275±0.000</td><td>0.545±0.0000
0.600±0.0000
0.571±0.0000
0.500±0.0000
18.0000±0.0000
0.936±0.0000</td><td>0.778±0.0000
0.700±0.0000
0.737±0.0000
0.722±0.0000
16.000±0.0000
1.560±0.0000</td><td>0.562±0.0000
0.900±0.0000
0.632±0.0000
0.556±0.0000
16.000±0.0000
2.188±0.0000</td><td>0.545±0.0000
0.600±0.0000
0.571±0.0000
0.500±0.0000
18.0000±0.0000
0.936±0.0000</td><td>0.778±0.0000
0.700±0.0000
0.737±0.0000
0.722±0.0000
10.000±0.0000
1.560±0.0000</td><td>70.6B/131k/8k</td></tr><tr><td>0.581±0.068
0.870±0.214
0.693±0.124
0.587±0.110
15.800±4.665
2.127±0.506</td><td>0.581±0.068
0.870±0.214
0.693±0.124
0.587±0.110
15.800±4.665
2.127±0.506</td><td>0.556±0.000
1.000±0.000
0.714±0.000
0.556±0.000
16.000±0.000
3.199±0.000</td><td>0.588±0.000
1.000±0.000
0.714±0.000
0.556±0.000
14.000±0.000
2.460±0.000</td><td>0.556±0.000
1.000±0.000
0.714±0.000
0.556±0.000
16.000±0.000
3.199±0.000</td><td>0.556±0.000
1.000±0.000
0.714±0.000
0.556±0.000
16.000±0.000
3.199±0.000</td><td>0.588±0.000
1.000±0.000
0.714±0.000
0.556±0.000
14.000±0.000
3.199±0.000</td><td>0.556±0.000
1.000±0.000
0.714±0.000
0.556±0.000
16.000±0.000
3.199±0.000</td><td>14.8B/131k/5k</td></tr></table>

Table 4: Performance metrics of CubeSat for ii-raw across methods and models. Each cell has from left to right (Precision, Recall, F1-Score, Accuracy, Edit Distance, and Spectral Distance). Values in each cell are the average of five experiments. The total of $ 5 0 \times5=2 5 0 $ experiments.

<!-- PDF_PAGE: 22 -->

<div align="center">

PREPRINT - RETRIEVAL AUGMENTED (KG), AND LLM-DRIVEN DSM GENERATION OF CPS

</div>

<table border="1"><tr><td>Graph RAG R2-R3</td><td>Graph RAG R1-R2</td><td>RAG R1-R2-R3</td><td>RAG R2-R3</td><td>RAG R1-R2</td><td>RAG R3</td><td>RAG R2</td><td>RAG R1</td><td>LLM</td><td></td></tr><tr><td>0.658±0.000
0.940±0.000
0.768±0.000
0.650±0.000
5.600±0.000
1.690±0.432</td><td>0.500±0.000
0.500±0.000
1.000±0.000
0.667±0.000
2.000±0.000
1.414±0.000</td><td>1.000±0.000
0.714±0.000
0.833±0.000
0.778±0.000
2.000±0.000
2.000±0.000</td><td>0.500±0.000
1.000±0.000
0.667±0.000
0.500±0.000
2.000±0.000
1.414±0.000</td><td>0.556±0.000
1.000±0.000
0.714±0.000
0.556±0.000
16.000±0.000
3.199±0.000</td><td>1.000±0.000
0.714±0.000
0.833±0.000
0.778±0.000
2.000±0.000</td><td>0.650±0.000
0.650±0.000
0.611±0.000
14.000±0.000
2.000±0.000</td><td>0.833±0.000
0.714±0.000
0.769±0.000
0.667±0.000
3.000±0.000
1.799±0.000</td><td>0.429±0.000
1.000±0.000
0.600±0.000
0.500±0.000
8.000±0.000
1.937±0.000</td><td>0.600±0.000
0.900±0.000
0.720±0.000
0.611±0.000
14.000±0.000
1.626±0.000</td><td>1.77T/128k/128k</td></tr><tr><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>0.8117±0.0258
0.6242±0.0707
0.7034±0.0481
0.6490±0.0416
17.2000±2.0396
1.2926±0.3513</td><td>0.6242±0.0707
0.7034±0.0481
0.6490±0.0416
17.2000±2.0396
1.2926±0.3513</td><td>1.77T/128k/128k</td></tr><tr><td>0.625±0.000
1.000±0.0000
0.769±0.000
0.625±0.000
6.000±0.000
2.036±0.000</td><td>0.500±0.000
0.800±0.000
0.615±0.000
0.444±0.000
2.188±0.000</td><td>0.778±0.000
1.000±0.000
0.875±0.000
0.778±0.000
2.000±0.000
1.231±0.000</td><td>0.714±0.000
0.833±0.000
0.769±0.000
0.625±0.000
6.000±0.000
0.506±0.000</td><td>0.714±0.000
1.000±0.000
0.833±0.000
0.769±0.000
0.625±0.000
4.000±0.000
1.310±0.000</td><td>0.714±0.000
0.833±0.000
0.769±0.000
0.625±0.000
6.000±0.000
0.506±0.000</td><td>na
na
na
na


Table 5: Performance metrics of CubeSat for ii-aligned across methods and models. Each cell has from left to right (Precision, Recall, F1-Score, Accuracy, Edit Distance, and Spectral Distance). Values in each cell are the average of five experiments. The total of $ 5 0 \times5=2 5 0 $ experiments.

<!-- PDF_PAGE: 23 -->

<div align="center">

PREPRINT - RETRIEVAL AUGMENTED (KG), AND LLM-DRIVEN DSM GENERATION OF CPS

</div>

<table border="1"><tr><td>Graph RAG R2-R3</td><td>Graph RAG R1-R2</td><td>RAG R1-R2-R3</td><td>RAG R2-R3</td><td>RAG R1-R2</td><td>RAG R3</td><td>RAG R2</td><td>RAG R1</td><td>LLM</td><td></td></tr><tr><td>0.630±0.0000
0.500±0.0000
0.557±0.0000
0.449±0.0000
27.000±0.0000
1.478±0.0000</td><td>0.788±0.0000
0.765±0.0000
0.776±0.0000
0.694±0.0000
15.0000±0.0000
1.156±0.0000</td><td>0.829±0.0000
0.853±0.0000
0.841±0.0000
0.776±0.0000
11.0000±0.0000
1.004±0.0000</td><td>0.774±0.0000
0.706±0.0000
0.738±0.0000
0.653±0.0000
17.0000±0.0000
1.004±0.0000</td><td>0.848±0.0000
0.824±0.0000
0.836±0.0000
0.776±0.0000
11.0000±0.0000
1.363±0.0000</td><td>0.727±0.0000
0.706±0.0000
0.716±0.0000
0.612±0.0000
19.0000±0.0000
1.026±0.0000</td><td>0.829±0.0000
0.853±0.0000
0.730±0.0000
0.653±0.0000
17.0000±0.0000
1.004±0.0000</td><td>0.829±0.0000
0.853±0.0000
0.841±0.0000
0.776±0.0000
11.0000±0.0000
1.004±0.0000</td><td>1.77T/128k/128k</td><td></td></tr><tr><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>0.8117±0.0258
0.6242±0.0707
0.7034±0.0481
0.6490±0.0416
17.2000±2.0396
1.2926±0.3513</td><td>1.77T/128k/128k</td><td></td></tr><tr><td>0.667±0.0000
0.529±0.0000
0.590±0.0000
0.490±0.0000
25.0000±0.0000
0.985±0.0000</td><td>0.661±0.011
0.518±0.024
0.581±0.019
0.482±0.016
25.400±0.8000
1.065±0.159</td><td>0.783±0.0000
0.529±0.0000
0.632±0.0000
0.571±0.0000
21.0000±0.0000
1.720±0.0000</td><td>0.704±0.0000
0.559±0.0000
0.623±0.0000
0.571±0.0000
21.0000±0.0000
1.720±0.0000</td><td>0.722±0.0000
0.382±0.0000
0.500±0.0000
0.469±0.0000
26.0000±0.0000
2.585±0.0000</td><td>0.762±0.0000
0.471±0.0000
0.582±0.0000
0.531±0.0000
23.0000±0.0000
2.084±0.0000</td><td>0.762±0.0000
0.471±0.0000
0.582±0.0000
0.531±0.0000
23.0000±0.0000
1.945±0.0000</td><td>0.621±0.0000
0.529±0.0000
0.571±0.0000
0.449±0.0000
27.0000±0.0000
1.219±0.0000</td><td>140.6B/65k/6k</td><td></td></tr><tr><td>0.710±0.0000
0.647±0.0000
0.677±0.0000
0.571±0.0000
21.0000±0.0000
0.887±0.0000</td><td>0.710±0.0000
0.647±0.0000
0.677±0.0000
0.571±0.0000
21.000±0.0000
0.955±0.0000</td><td>0.710±0.0000
0.647±0.0000
0.677±0.0000
0.571±0.0000
21.000±0.0000
0.955±0.0000</td><td>0.826±0.0000
0.559±0.0000
0.667±0.0000
0.612±0.0000
19.0000±0.0000
1.381±0.0000</td><td>0.710±0.0000
0.647±0.0000
0.677±0.0000
0.571±0.0000
21.000±0.0000
0.995±0.0000</td><td>0.694±0.0000
1.0000±0.0000
0.819±0.0000
0.694±0.0000
15.000±0.0000
0.955±0.0000</td><td>0.826±0.0000
1.0000±0.0000
0.819±0.0000
0.694±0.0000
15.000±0.0000
0.955±0.0000</td><td>0.710±0.0000
0.647±0.0000
0.677±0.0000
0.571±0.0000
21.000±0.0000
1.194±0.0000</td><td>70.6B/131k/8k</td><td></td></tr><tr><td>na
na
na
na</td><td>0.746±0.010
0.547±0.0820
0.627±0.058
0.555±0.0033
21.8000±1.6000
1.664±0.371</td><td>0.694±0.0000
1.0000±0.0000
0.819±0.0000
0.694±0.0000
15.000±0.0000
3.0000±0.0000</td><td>0.694±0.0000
1.0000±0.0000
0.819±0.0000
0.694±0.0000
15.0000±0.0000
3.0000±0.0000</td><td>0.694±0.0000
1.0000±0.0000
0.819±0.0000
0.694±0.0000
15.0000±0.0000
3.0000±0.0000</td><td>0.778±0.0000
1.0000±0.0000
0.618±0.0000
0.689±0.0000
0.612±0.0000
19.000±0.0000
1.252±0.0000</td><td>0.778±0.0000
1.0000±0.0000
0.618±0.0000
0.689±0.0000
0.612±0.0000
19.000±0.0000
1.252±0.0000</td><td>0.698±0.0000
1.0000±0.0000
0.819±0.0000
0.694±0.0000
15.000±0.0000
1.252±0.0000</td><td>0.762±0.0000
0.471±0.0000
0.582±0.0000
0.653±0.0000
17.000±0.0000
2.108±0.0000</td><td>14.8B/131k/5k</td><td></td></tr></table>

Table 6: Performance metrics of power screwdriver for ii-raw across methods and models. Each cell has from left to right (Precision, Recall, F1-Score, Accuracy, Edit Distance, and Spectral Distance). Values in each cell are the average of five experiments. The total of $ 5 0 \times5=2 5 0 $ experiments.

<!-- PDF_PAGE: 24 -->

<div align="center">

PREPRINT - RETRIEVAL AUGMENTED (KG), AND LLM-DRIVEN DSM GENERATION OF CPS

</div>

<table border="1"><tr><td>Graph RAG R2-R3</td><td>Graph RAG R1-R2</td><td>RAG R1-R2-R3</td><td>RAG R2-R3</td><td>RAG R1-R2</td><td>RAG R3</td><td>RAG R2</td><td>RAG R1</td><td>LLM</td><td></td></tr><tr><td>0.556±0.000
1.000±0.000
0.714±0.000
0.556±0.000
4.000±0.000
2.449±0.000</td><td>0.788±0.000
0.765±0.000
0.776±0.000
0.694±0.000
15.0000±0.0000
1.156±0.0000</td><td>0.846±0.000
0.917±0.000
0.880±0.000
0.833±0.000
6.000±0.000
1.247±0.000</td><td>0.750±0.000
0.750±0.000
0.750±0.000
0.667±0.000
12.000±0.000
1.676±0.000</td><td>0.833±0.000
0.833±0.000
0.833±0.000
0.778±0.000
8.0000±0.000
0.998±0.000</td><td>0.792±0.000
0.792±0.000
0.792±0.000
0.722±0.000
10.000±0.000
0.498±0.000</td><td>0.846±0.000
0.917±0.000
0.880±0.000
0.833±0.000
6.000±0.000
1.247±0.000</td><td>0.727±0.000
0.667±0.000
0.696±0.000
0.611±0.000
14.000±0.000
1.483±0.000</td><td>0.846±0.000
0.917±0.000
0.880±0.000
0.833±0.000
6.0000±0.0000
1.247±0.000</td><td>1.77T/128k/128k</td></tr><tr><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na
na</td><td>na
na
na
na</td><td>gpt4-turbo-preview</td><td>gpt4-turbo-preview</td></tr><tr><td>0.800±0.000
0.667±0.000
0.727±0.000
0.625±0.000
6.0000±0.000
0.598±0.000</td><td>0.807±0.013
0.700±0.067
0.748±0.042
0.650±0.050
5.600±0.800
0.478±0.239</td><td>0.800±0.000
0.800±0.000
0.800±0.000
0.760±0.000
6.000±0.000
0.935±0.000</td><td>0.692±0.000
0.600±0.000
0.643±0.000
0.600±0.000
10.0000±0.000
0.456±0.000</td><td>0.583±0.000
0.467±0.000
0.519±0.000
0.480±0.000
13.0000±0.000
0.697±0.000</td><td>0.875±0.000
0.636±0.000
0.737±0.000
0.688±0.000
5.0000±0.000
na</td><td>0.700±0.000
0.636±0.000
0.667±0.000
0.562±0.000
7.000±0.000
0.449±0.000</td><td>0.762±0.000
0.889±0.000
0.821±0.000
0.720±0.000
7.0000±0.000
1.313±0.000</td><td>0.842±0.000
0.889±0.000
0.865±0.000
0.800±0.000
5.000±0.000
0.981±0.000</td><td>140.6B/65k/6k</td></tr><tr><td>0.864±0.000
0.792±0.000
0.826±0.000
0.778±0.000
8.0000±0.0000
0.800±0.0000</td><td>0.864±0.000
0.792±0.000
0.826±0.000
0.778±0.0000
8.0000±0.0000
0.800±0.0000</td><td>0.792±0.000
0.792±0.000
0.792±0.000
0.722±0.0000
10.000±0.000
0.998±0.000</td><td>0.773±0.000
0.708±0.000
0.739±0.000
0.667±0.000
12.0000±0.0000
0.800±0.0000</td><td>0.792±0.000
0.792±0.000
0.792±0.000
0.722±0.0000
10.000±0.000
0.998±0.000</td><td>0.792±0.000
0.792±0.000
0.792±0.000
0.722±0.0000
10.000±0.000
0.998±0.000</td><td>0.773±0.000
0.708±0.000
0.739±0.000
0.667±0.000
12.0000±0.000
0.800±0.0000</td><td>0.750±0.000
1.0000±0.000
0.857±0.000
0.750±0.000
4.0000±0.000
1.625±0.0000</td><td>70.6B/131k/8k</td></tr><tr><td>na
na
na
na</td><td>0.760±0.120
0.582±0.109
0.640±0.053
0.562±0.0000
7.0000±0.0000
0.832±0.584</td><td>0.667±0.000
1.000±0.000
0.800±0.000
0.667±0.000
12.000±0.000
2.738±0.000</td><td>0.667±0.000
1.000±0.000
0.800±0.000
0.667±0.000
12.000±0.000
2.738±0.000</td><td>0.640±0.000
1.000±0.000
0.780±0.000
0.640±0.000
9.000±0.000
2.420±0.000</td><td>0.800±0.000
0.750±0.000
0.774±0.000
0.720±0.000
7.000±0.000
0.525±0.000</td><td>0.800±0.000
0.750±0.000
0.774±0.000
0.720±0.000
7.000±0.000
0.525±0.000</td><td>0.750±0.000
1.0000±0.000
0.857±0.000
0.750±0.000
4.000±0.000
1.6075±0.000</td><td>0.900±0.000
0.750±0.000
0.818±0.000
0.778±0.000
8.0000±0.000
1.078±0.000</td><td>14.8B/131k/5k</td></tr><tr><td>na
na
na
na</td><td>0.582±0.109
0.640±0.053
0.562±0.0000
7.0000±0.0000
0.832±0.584</td><td>1.000±0.000
0.800±0.000
0.667±0.000
12.000±0.000
2.738±0.000</td><td>1.000±0.000
0.800±0.000
0.667±0.000
12.000±0.000
2.738±0.000</td><td>1.000±0.000
0.780±0.000
0.640±0.000
9.000±0.000
2.420±0.000</td><td>0.750±0.000
0.774±0.000
0.720±0.000
7.000±0.000
0.525±0.000</td><td>0.750±0.000
0.754±0.000
0.905±0.000
0.840±0.000
4.000±0.000
0.636±0.000</td><td>0.864±0.000
0.950±0.000
0.905±0.000
0.840±0.000
4.000±0.000
1.230±0.000</td><td>0.722±0.0000
0.542±0.0000
0.619±0.0000
0.556±0.0000
16.0000±0.0000
1.230±0.000</td><td>14.8B/131k/5k</td></tr></table>

Table 7: Performance metrics of power screwdriver for ii-aligned across methods and models. Each cell has from left to right (Precision, Recall, F1-Score, Accuracy, Edit Distance, and Spectral Distance). Values in each cell are the average of five experiments. The total of $ 5 0 \times5=2 5 0 $ experiments.

<!-- PDF_PAGE: 25 -->

<div align="center">

Figure 9: Best two aligned predictions of the models and methods for (ii)-DSM of power screwdriver Matrix Comparisons: Raw (Avg) vs Aligned (Avg) - powerscrewdriver / LLM / gpt-4-turbo-preview

</div>


![figure_009.png](figure_009.png)




![figure_010.png](figure_010.png)




![figure_011.png](figure_011.png)




![figure_012.png](figure_012.png)



Matrix Comparisons: Raw (Avg) vs Aligned (Avg) - powerscrewdriver / LLM_RAG / mixtral / R1


![figure_013.png](figure_013.png)



<div align="center">

Predicted Matrix (Raw LLM Average)

</div>


![figure_014.png](figure_014.png)




![figure_015.png](figure_015.png)




![figure_016.png](figure_016.png)



<!-- PDF_PAGE: 26 -->

<div align="center">

Figure 10: Best two aligned predictions of the models and methods for (ii)-DSM of CubeSat Matrix Comparisons: Raw (Avg) vs Aligned (Avg) - CubeSat / LLM_RAG / Ilama3.3 / R1_R2

</div>


![figure_017.png](figure_017.png)



<div align="center">

Ground Truth Matrix (Aligned)

</div>


![figure_018.png](figure_018.png)




![figure_019.png](figure_019.png)




![figure_020.png](figure_020.png)



Matrix Comparisons: Raw (Avg) vs Aligned (Avg) - CubeSat / LLM_RAG / mixtral / R2

<div align="center">

Ground Truth Matrix (Raw)

</div>


![figure_021.png](figure_021.png)



<div align="center">

Ground Truth Matrix (Aligned)

</div>


![figure_022.png](figure_022.png)




![figure_023.png](figure_023.png)




![figure_024.png](figure_024.png)

