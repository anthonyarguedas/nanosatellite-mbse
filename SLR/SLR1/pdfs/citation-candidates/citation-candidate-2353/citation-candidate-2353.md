---
source: null
title: "citation-candidate-2353"
page_count: 8
converted_at: "2026-09-08T16:14:35Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# ACADEMIA Letters

</div>

Designing and Developing OPCloud, an OPM-based Collaborative Software Environment, in a Mixed Academic and Industrial Setting: An Experience Report

Hanan Kohen Dov Dori

## Abstract

OPCloud is a Web-based collaborative software environment for model-based systems engineering (MBSE) used for creating conceptual models in Object-Process Methodology, OPM, ISO 19450:2005. As we have been designing and developing OPCloud, we faced several challenges, mostly stemming from the unique development environment. OPCloud is a high-end, Cloud-based tool. Software of this kind is developed by commercial companies, be they large established ones or small startups. In contrast, OPCloud is developed in an academic environment at a technological university. As such, it involves a variety of people contributing to its development, each having a different objective, capabilities, and commitment level. In this report, we describe our experiences of a three-year project of OPCloud software design and development. To this end, we have adopted an agile development methodology, involving regular weekly meetings of all the development stakeholders and monthly product deployment to be delivered to the commercial company customer. We describe how we engaged the diverse population of developers, including faculty, post-doctoral fellows, academic researchers, graduate and undergraduate students, and dedicated developers, in the software development process.

Index Terms— Object-Process Methodology, OPM; model-based systems engineering (MBSE); OPCloud

<!-- PDF_PAGE: 2 -->

## I. Introduction

Model based systems engineering (MBSE) has evolved out of the recognition that conceptual models should be central in engineered systems' lifecycles. Conceptual modeling, used to understand, design, and manage engineering systems should precede mathematical and physical modeling.

In December 2015, the International Organization for Standardization (ISO) adopted Object- Process Methodology, OPM, as an MBSE language in ISO 19450:2015 Automation systems and integration — Object-Process Methodology [1]. In recent years, and especially since the adoption of OPM by ISO, OPM is rapidly gaining acceptance in the industry, and interest in learning and applying OPM as the MBSE language and methodology of choice has been increasing steadily.

In this report, we want to present the process of designing and developing OPCloud, an OPM modeling tool, in a mixed academic and industrial setting.

## II. OPCloud - Objectives, features and highlights

OPCloud is a cloud-based application that utilizes the Web as a framework for creating OPM models according to OPM ISO 19450:2015 [2]. At its core, OPCloud is optimized for the construction of correct OPM models in a friendly, supportive way. It is designed to produce correct-by-construction models by enabling, for example, drawing only legal links between two entities which the modeler is about to connect. OPCloud enables creating and editing of an OPM model.

Main features of OPCloud includes backward compatibility - the ability to import OPCAT files, a previous OPM modeling software [3] automatic generation of OPL - Object-Process Language, model sharing with transferrable editing rights, commenting, exporting the model, full control over styling, and a modern graphical user interface.

A major power of a cloud-based application is its ability to perform calculations and connect to IoT devices [4], opening the door for real-time collaborative modeling and model control - a new key OPCloud feature. Not only does collaboration enable a group of modelers to jointly construct a system model; it is also a great facilitator of knowledge sharing and integration.

<!-- PDF_PAGE: 3 -->

## III. The academic-industrial mixed project setting

Companies are interested in new products which would bring them financial benefits and help society. Industrial projects and industrial project management have a vast of literature on project management methodologies [5], [6], [7]. Academic projects' have different nature and funding from industrial projects. One of these differences is that academic projects have higher variances, while literature and methodologies are far more sporadic [8], [9]. This is mainly because of the academic freedom and the higher-risk nature of academic projects. Given this state of affairs, in order to achieve the best results for the OPCloud project, which will reflect both the needs of the industrial commercial partner and the expected academic results, we had to mix project management techniques from both the academic and industrial worlds. Techniques we used include setting up an agile, Scrum-like software development methodology, and working closely with the industrial partner and project funder to set up acceptance criteria and timetables for deliverables.

## IV. The unique OPCloud agile software development environment

Software projects often meet many challenges such as shifting schedules, scope creep, inflexible budgets, and unrealistic customer expectations. These challenges typically result from a lack of process awareness and support on the part of development and management divisions [10].

Scrum focuses on project management in situations where planning ahead is difficult, with mechanisms for "empirical process control", in which feedback loops constitute the core element [11], [12].

In our OPCloud project, we have defined the project manager as the Scrum master. The Principal Investigator - head academic researcher and the head of the industrial partner were the product owners. The development team comprised a balanced blend of Ph.D. researchers, paid developers, graduate (Ph.D. and M.Sc.) students, and teams of undergraduate students. Following a rather thorough benchmark, we selected Zoho projects $ [13]^{1} $ as the managing program to keep track of the iterations, milestones, tasks, and bugs, GIT for version control [14] and Jenkins [15], [16] for CI/CD.

<!-- PDF_PAGE: 4 -->

## V. The diverse developers, their goals, qualifications, and commitments

The mix of talents in the OPCloud development team can be a source of problems due to conflicting interests, but this diverse population can also create a fertile ground for the creation of a vibrant, synergistic community of people with complementary interests. Indeed, since members of our team included faculty, associate researchers with an industrial background, second and third-degree students, and hired software developers, some full-time and others part-time student developers. Another component of the development personnel has been undergraduate students who took the course "Full Stack Web Development". The various team members brought their diverse experience into the community, which ranged from very young and inexperienced, through medium-level experience of graduate students, some of whom work in high-tech industries, while carrying out their research, all the way to a highly experienced, software and systems engineers.

This human resource diversity was accounted for when planning our timeline, features, and deliverables within this agile OPCloud software development process. At the same time, we had to account for the priorities set up by the paying customer requirements and sort them so they could be merged optimally with the potential of our team.

For instance, a prime concern of the customer included problems related to user management, authorization and authentication, management of groups, and applying differential access control. To handle these issues, we divided them into a series of development tasks that fit into a student course team project. These "mini-projects" were developed in a similar environment of a startup company, integrated after code review into the main trunk of the project in GIT [17]. $ ^{2} $

Major aspects of integrating systems engineering and software engineering are open research topics that have scientific or engineering value beyond OPM or OPCloud. Topics of this generic nature are designated as Ph.D. or Master's research topics, with their testbed being an elegant implementation in OPCloud. This way, we achieve the dual purpose of providing on the one hand the research student with a solid development platform to build upon, and on the other hand, the product of the implementation remains part and parcel of OPCloud, enriching it with state-of-the-art features.

One prominent example of this kind of research topic is the Ph.D. research aimed at fusing systems engineering and software engineering by enhancing conceptual modeling with computational capabilities and direct execution of models, extending the OPM ISO 19450:2005 standard [18]. Another example is research related to Design Structure Matrix (DSM) [19] or

<!-- PDF_PAGE: 5 -->

Insights of OPM Models by using a graph-theoretic querying approach [20].

The connectivity of OPCloud has two aspects: connectivity with other MBSE tools commonly used by system architects and engineers, and the reusability of OPM models by other standard popular modeling systems. OSLC (Workgroup 2010) has been adopted to answer the first connectivity concern, which builds on the RDF [21] graph representation based on an OWL ontology [22] of OPM. The second aspect is based on the availability of an RDF representation of an entire model through an extension of the OSLC capability, the OWL ontology of the OPM language [23], and the use of semantic mediation [24]. Semantic mediation can translate ontologies of different standard modeling languages, such as SysML [25] or Modelica [26], by applying transformational rules based on the OWL semantics and producing RDF representations of SysML or Modelica models, respectively.

## VI. The Full Stack Web Development course

A rather unique element of the OPCloud project was to involve graduate and undergraduate students as participants in OPCloud development. To this end, we initiated and launched a graduate-undergraduate level course, titled Full Stack Web Development, at the Faculty of Industrial Engineering and Management, Technion, Israel Institute of Technology. The course is taught in a Project-Based Learning (PBL) approach, combined with teamwork [14], [27]. In order to have the students both participate in the development and receive the benefits of PBL, we asked them to develop several key OPCloud features. For example, one team of students was behind the implementation of the collaborative feature of OPCloud, while another team developed a feature of comparing and finding the differences between two OPM models.

## VII. Summary and lessons for the future

OPCloud [www.opcloud.tech] has been developed in a unique academic environment that includes elements from industry, such as adopting the Scrum agile software development method, working with a very large customer who poses real-life requirements, the need to develop robust, industrial-strength Cloud-based software. Hence, even though formally the environment is part of academia, it has a strong flavor of a startup company. The diverse composition of the developing team is another special element of this environment. Unlike a startup, the team includes members who are students at all levels, researchers, and professional developers, some of whom started as employed students and went on to become full-time employees. Yet another non-common factor is the involvement of undergraduate student teams,

<!-- PDF_PAGE: 6 -->

who change each semester, yet contribute important modules to OPCloud while gaining real-life experience in a startup-like environment.

## References

[1] "ISO/PAS 19450 Automation systems and integration - Object-Process Methodology," 2015.

[2] D. Dori et al., "OPCloud: An OPM Integrated Conceptual-Executable Modeling Environment for Industry 4.0," in Systems Engineering in the Fourth Industrial Revolution: Big Data, Novel Technologies, and Modern Systems Engineering, A. Z. Ron S. Kenett Robert S. Swarz, Ed. John Wiley & Sons, 2019, pp. 243-271.

[3] D. Dori, C. Linchevski, and R. Manor, "OPCAT-a software environment for object-process methodology based conceptual modeling of complex systems," Proc 1st Int Conf Model Manag. Eng. Process., pp. 147-151, 2010.

[4] H. Kohen and D. Dori, "Incorporating Hardware-in-the-Loop Simulation into Object- Process Methodology," in 2020 IEEE International Systems Conference (SysCon), 2020, pp. 1-8, doi: 10.1109/SysCon47679.2020.9275904.

[5] H. Kerzner and H. R. Kerzner, Project management: a systems approach to planning, scheduling, and controlling. John Wiley & Sons, 2017.

[6] J. R. Turner, Handbook of project-based management, vol. 92. McGraw-hill New York, NY, 2014.

[7] S. Tonchia, Tonchia, and Mahagaonkar, Industrial project management. Springer, 2018.

[8] V. Morandi, "The management of industry-university joint research projects: How do partners coordinate and control R&D activities?," J. Technol. Transf., vol. 38, no. 2, pp. 69-92, 2013, doi: 10.1007/s10961-011-9228-5.

[9] P. Notargiacomo Mustaro and R. Rossi, "Project Management Principles Applied in Academic Research Projects," Issues Informing Sci. Inf. Technol., vol. 10, pp. 325-340, 2013, doi: 10.28945/1814.

[10] E. Flarup, "Best practices in software localization," in Internationalization & Unicode Conference (IUC32), San Jose, California, 2007.

<!-- PDF_PAGE: 7 -->

[11] K. Schwaber, "SCRUM Development Process," in Business Object Design and Implementation, London: Springer London, 1997, pp. 117-134.

[12] K. Schwaber and M. Beedle, Agile software development with Scrum. 2002.

[13] N. B. Milman, "Communication, collaboration, and project management tools for producing and managing group projects at a distance," Distance Learn., vol. 8, no. 4, p. 85, 2011.

[14] B. F. Jones, C. M. Rasmussen, and M. C. Moffitt, Real-life problem solving: A collaborative approach to interdisciplinary learning. 2004.

[15] C. Singh, N. S. Gaba, M. Kaur, and B. Kaur, "Comparison of Different CI/CD Tools Integrated with Cloud Platform," in 2019 9th International Conference on Cloud Computing, Data Science & Engineering (Confluence), 2019, pp. 7-12, doi: 10.1109/CONFLUENCE.2019.8776985.

[16] N. Pathania, Learning Continuous Integration with Jenkins Second Edition A beginner's guide to implementing Continuous Integration and Continuous Delivery using Jenkins 2 Nikhil Pathania BIRMINGHAM-MUMBAI. 2017.

[17] L. Dabbish, C. Stuart, J. Tsay, and J. Herbsleb, "Social coding in GitHub: transparency and collaboration in an open software repository," in Proceedings of the ACM 2012 conference on computer supported cooperative work, 2012, pp. 1277-1286.

[18] N. Levi-Soskin, R. Shaoul, H. Kohen, A. Jbara, and D. Dori, "Model-Based Diagnosis with FTTell: Assessing the Potential for Pediatric Failure to Thrive (FTT) During the Perinatal Stage," in EuroSymposium on Systems Analysis and Design, 2019, pp. 37-47.

[19] G. Sobol and D. Dori, "Improving OPM Conceptual Models by Incorporating Design Structure Matrix," in ISSE 2020 - 6th IEEE International Symposium on Systems Engineering, Proceedings, 2020, doi: 10.1109/ISSE49799.2020.9272243.

[20] D. Medvedev, U. Shani, and D. Dori, "Gaining Insights into Conceptual Models: A Graph-Theoretic Querying Approach," Appl. Sci., vol. 11, no. 2, 2021.

[21] O. Lassila and R. R. Swick, "Resource description framework (RDF) model and syntax specification," 1999.

[22] D. L. McGuinness, F. Van Harmelen, and others, "OWL web ontology language overview," W3C Recomm., vol. 10, no. 10, p. 2004, 2004.

<!-- PDF_PAGE: 8 -->

[23] S. Jacobs, N. Wengrowicz, and D. Dori, "Exporting Object-Process Methodology System Models to the Semantic Web," in Systems, Man and Cybernetics (SMC), 2014 IEEE International Conference on, 2014, pp. 1014-1019.

[24] U. Shani, S. Jacobs, N. Wengrowicz, and D. Dori, "Engaging ontologies to break MBSE tools boundaries through semantic mediation," in 2016 Conference on Systems Engineering Research, 2016.

[25] S. Friedenthal, A. Moore, and R. Steiner, A practical guide to SysML: the systems modeling language. Morgan Kaufmann, 2014.

[26] P. Fritzson, Principles of object-oriented modeling and simulation with Modelica 2.1. John Wiley & Sons, 2010.

[27] Y. J. Dori and A. Silva, "Assessing international product design and development graduate courses: The MIT-Portugal program," Adv. Eng. Educ., vol. 2, no. 2, pp. 1-30, 2010.