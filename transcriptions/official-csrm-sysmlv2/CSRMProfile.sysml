// Derived from INCOSE SSWG / OMG SDTF CSRM Profile XMI, CC BY 4.0.
// Stereotype labels are metadata definitions. OCL and UML extensions remain in the XMI.
package OfficialCSRMProfile {
    package 'Concerns and Requirements Profile' {
        metadata def 'StakeholderConcern' {
            doc /* Source profile stereotype: StakeholderConcern
            XMI id: _18_5_1_3880181_1505404258412_328388_57518
            «StakeholderConcern» is an interest in a system relevant to one or more of its stakeholders. A stakeholder concern could be manifest in many forms, such as one or more stakeholder needs, goals, expectations, responsibilities, requirements, design constraints, assumptions, dependencies, quality attributes, architecture decisions, risks, or other issues.
            A Stakeholder can have multiple «StakeholderConcern»s, and a single «StakeholderConcern» can be shared by numerous «Stakeholder»s. The «ConcernOf» dependency relates «Stakeholder» to corresponding «StakeholderConcern».
            «StakeholderConcern» are high-level requirements that specific requirements are derived.
            Note that the 'Text' attribute of «AbstractRequirement» is used to document the stakeholder concern. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411622966_356160_14830", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'MissionObjective' {
            doc /* Source profile stereotype: MissionObjective
            XMI id: _18_5_1_3880181_1505404258412_137340_57520
            «MissionObjective» is one of a broad set of goals that must be achieved to successfully satisfy the stated mission need, such as the purpose to be achieved, product to be produced, or a service to be performed.
            «MissionObjective» are derived from «MissionNeed» or «StakeholderConcern». A «MissionObjective» is usually not satisfied directly but one or more «MissionRequirement» are created (derived) to translate to requirements that are then satisfied by a part of the design. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411652098_465286_14842", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'MissionNeed' {
            doc /* Source profile stereotype: MissionNeed
            XMI id: _18_5_1_3880181_1505404258412_224367_57522
            «MissionNeed» is a concise description of a need or service that the system must provide. It should be solution-independent and only describe the problem the system is supposed to solve. The mission need is the main driver of the architecture.
            «MissionNeed» is satisfied by one or more «Mission» or by one or more of its sub-elements. «MissionObjective» are derived from «MissionNeed». «MissionConstraint» can be used as a derived constraint of the «MissionNeed» that limits the scope of the «MissionNeed». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601664902379_314898_13955", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'MissionConstraint' {
            doc /* Source profile stereotype: MissionConstraint
            XMI id: _18_5_1_3880181_1505404258412_91141_57524
            «MissionConstraint» is a limitation placed on cost, schedule, or implementation techniques available to the system designer. It is typically fixed and not subject to trades, e.g., mission budget and schedule.
            «MissionConstraint» can be satisfied by any element that is a subject to the constraint. Alternatively, «PerformanceRequirement» or specialization (like «moeRequirement») can be created and derived from the «MissionConstraint» and then the «PerformanceRequirement» is then satisfied by a corresponding value property. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411657018_939183_14845", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'MissionRequirement' {
            doc /* Source profile stereotype: MissionRequirement
            XMI id: _18_5_1_3880181_1505404258412_728195_57526
            «MissionRequirement» is a statement of facts and assumptions that define expectations on the system's capabilities in terms of mission objectives, environment, constraints, and measures of effectiveness (MoE). «MissionRequirement» are satisfied by «Mission» or one or more of its sub-elements and or derived further into «SpaceSegmentRequirement» and «GroundSegmentRequirement». «MissionRequirement» are derived from «MissionObjective» or directly derived from mission needs/constraints or stakeholder concerns. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411661637_955621_14848", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'CubeSatRequirement' {
            doc /* Source profile stereotype: CubeSatRequirement
            XMI id: _18_5_2_3880181_1529078549705_678163_63477
            «CubeSatRequirement» is a requirement specific to a «CubeSat» needed to design and operate the «CubeSat» or its parts. «CubeSatRequirement» is a kind of Requirement on the CubeSat system satisfied by the «CubeSat» or by one or more of its sub-elements. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601756715971_961984_15091", "general": "_19_0_3_2b0010b_1601756715963_375307_15065"}, "references": []}
        }
        metadata def 'GroundSegmentRequirement' {
            doc /* Source profile stereotype: GroundSegmentRequirement
            XMI id: _18_5_2_3880181_1529078702418_104590_63525
            «GroundSegmentRequirement» is a requirement specific to a «GroundSegment» needed to design and operate the «GroundSegment» or its parts. «GroundSegmentRequirement» is a requirement of satisfied by a «GroundSegment» or by one or more of its sub-elements. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601756598258_393811_15047", "general": "_19_0_3_2b0010b_1601756549762_939405_15008"}, "references": []}
        }
        metadata def 'SubsystemRequirement' {
            doc /* Source profile stereotype: SubsystemRequirement
            XMI id: _18_5_2_3880181_1529078829764_35770_63565
            «SubsystemRequirement» is a requirement specific to a «Subsystem» needed to design and operate a «Subsystem» or its parts. «SubsystemRequirement» is a requirement satisfied by a «Subsystem» or by one or more of its sub-elements. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411807964_523662_14880", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'ComponentRequirement' {
            doc /* Source profile stereotype: ComponentRequirement
            XMI id: _18_5_2_3880181_1529079012472_53655_63605
            «ComponentRequirement» is a requirement specific to a «Component» needed to design and operate the «component» or its parts. «ComponentRequirement» is a requirement Satisfied by a «Component» or by one or more of its sub-elements. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411753427_379145_14872", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'DeployerRequirement' {
            doc /* Source profile stereotype: DeployerRequirement
            XMI id: _18_5_2_3880181_1543956319562_201316_63140
            «DeployerRequirement» is a requirement specific to a «CubeSatDeployer» needed to design and operate the «CubeSatDeployer» or its parts. «DeployerRequirement» is a requirement satisfied by a «CubeSatDeployer» or by one or more of its sub-elements.
            Note that the Deployer in this case is referring to the Deployer mechanism, not an organization. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411247732_922863_14789", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
        }
        metadata def 'SpaceSegmentRequirement' {
            doc /* Source profile stereotype: SpaceSegmentRequirement
            XMI id: _19_0_3_2b0010b_1601663152345_984040_13791
            «SpaceSegmentRequirement» is a requirement specific to a «SpaceSegment» needed to design elements of the «SpaceSegment» and operate the «SpaceSegment» parts. «SpaceSegmentRequirement» is a requirement satisfied by a «SpaceSegment» or one or more composed-elements. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601756582120_374793_15044", "general": "_19_0_3_2b0010b_1601756549762_939405_15008"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601663169284_827465_13821", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1601663169284_630789_13820"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'Group' {
            doc /* Source profile stereotype: Group
            XMI id: _19_0_3_2b0010b_1601670079259_950763_14594
            «Group» is used to organize requirements into nested hierarchies. A «Group» has nested (owns as nested classifiers) requirements that are categorized by the name of the «Group». «Group» owned requirements are not sub-requirements as described by SysML (see 16.3.2.5 Requirement or the SysML specification). A model may have many «Group» elements. For example, as a part of a larger set of requirements, some are contained (owned) in a «Group» named 'Functional Requirements' and another «Group» might be called 'Regulatory', each would own requirements related to those categories. «Group» facilitates a de facto pattern in which hierarchical organization of requirements with some requirements only having a name with the text attribute blank to imply that they are used to categorize requirements. Using requirements in that manner can be confusing as there is no true indicator of the intent. «Group» designates the requirement element as organizational, preventing such confusion. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601670087405_710358_14636", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601670087415_254129_14638", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1601670087415_913395_14637"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'SpacecraftRequirement' {
            doc /* Source profile stereotype: SpacecraftRequirement
            XMI id: _19_0_3_2b0010b_1601747516208_444657_14855
            «SpacecraftRequirement» is a system requirement needed to design and operate a spacecraft and/or its subsystems. «SpacecraftRequirement»is a requirement satisfied by one or more kind of «Spacecraft». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601411628447_227697_14833", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601747516320_359229_14884", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1601747516320_496638_14883"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'SegmentRequirement' {
            doc /* Source profile stereotype: SegmentRequirement
            XMI id: _19_0_3_2b0010b_1601756549762_939405_15008
            «SegmentRequirement» is an abstract requirement that is satisfied by a Segment or its parts. Note that «SegmentRequirement» is a base type for «SpaceSegment» and «GroundSegment» and it is expected to only be used when creating a specific kind of «Segment». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601756566466_297930_15036", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601756566498_726622_15038", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1601756566498_822027_15037"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'SatelliteRequirement' {
            doc /* Source profile stereotype: SatelliteRequirement
            XMI id: _19_0_3_2b0010b_1601756715963_375307_15065
            «SatelliteRequirement» is a requirement of a satellite system needed to design and operate a satellite and/or its subsystems. «SatelliteRequirement» is satisfied by a «Satellite» or one or more of its sub-elements. «SatelliteRequirement» is derived from «SpaceSegmentRequirement» or directly derived from mission needs/objectives/constraints or stakeholder concerns. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601747516217_136130_14881", "general": "_19_0_3_2b0010b_1601747516208_444657_14855"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601756716106_199743_15094", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1601756716106_250615_15093"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
    }
    package 'Technical Measures Profile' {
        metadata def 'moeSpecification' {
            doc /* Source profile stereotype: moeSpecification
            XMI id: _18_5_2_3880181_1510191588135_243878_66132
            The Measure of Effectiveness (MoE) Specification («moeSpecification») specifies attributes of a system that determine how well the system element is satisfying or expected to satisfy technical requirements. «moeSpecification» is a «Block» that specifies a technical measure, constraints, and measurement activities used to provide insight into the progress made in the definition and development of the technical solution, risks, and issues. «moeSpecification» may refine «MissionNeed».
            The «moeSpecification» captures Stakeholder descriptions of operational measures of success that are satisfied by «MoE» properties. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_18_5_2_3880181_1510191588885_719868_66174", "general": "_19_0_3_2b0010b_1614283840256_215949_1862"}, "references": []}
        }
        metadata def 'mopSpecification' {
            doc /* Source profile stereotype: mopSpecification
            XMI id: _18_5_2_3880181_1510191588135_300770_66133
            The Measure of Performance (MoP) Specification «mopSpecification» specifies attributes of a system that determine how well the system element is satisfying or expected to satisfy technical requirements. «mopSpecification» is a «Block» that specifies a technical measure, constraints, and measurement activities used to provide insight into the progress made in the definition and development of the technical solution, risks, and issues.
            The «mopSpecification» captures Stakeholder descriptions of physical or functional attributes relating to system operation that are to be transformed into one or more MoPs.
            «mopSpecification» may refine MoE or KPP Specifications. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_18_5_2_3880181_1510191588885_591236_66176", "general": "_19_0_3_2b0010b_1614283840256_215949_1862"}, "references": []}
        }
        metadata def 'tpmSpecification' {
            doc /* Source profile stereotype: tpmSpecification
            XMI id: _18_5_2_3880181_1510191588135_601405_66134
            The Technical Performance Measure (TPM) Specification specifies attributes of a system that determine how well the system element is satisfying or expected to satisfy technical requirements. «tpmSpecification» is a «Block» that specifies a technical measure, constraints, and measurement activities used to provide insight into the progress made in the definition and development of the technical solution, risks, and issues. «tpmSpecification» refine «tpmRequirement».
            «tpmSpecification» may refine «mopSpecification». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_18_5_2_3880181_1510191588885_143083_66178", "general": "_19_0_3_2b0010b_1614283840256_215949_1862"}, "references": []}
        }
        metadata def 'mop' {
            doc /* Source profile stereotype: mop
            XMI id: _18_5_2_3880181_1510191588150_289586_66140
            The «mop» stereotype represents a performance property of a system (or other element). The «mop» stereotype is applied to a «ValueProperty» element to mark the property as a Measure of performance (MoP). MoP is an engineering performance measure that provides a value necessary for meeting a Measure of Effectiveness (MoE). «mop» satisfy «mopRequirement». */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601668237242_342931_14380", "name": "base_Property", "visibility": "private", "association": "_19_0_3_2b0010b_1601668237242_739491_14379"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Property"}]}
        }
        metadata def 'TPM' {
            doc /* Source profile stereotype: TPM
            XMI id: _18_5_2_3880181_1510191588150_801304_66141
            The «tpm» stereotype represents a performance property of a system (or other element). Technical Performance Measure (TPM) of the attributes of a system element to determine how well the system element is satisfying or expected to satisfy, specified technical requirements. They are based on the driving requirements or technical parameters of high risk or significance - e.g., mass, power, or data rate. Actual versus planned progress of TPMs are tracked so the systems engineer or project manager can assess progress and the risk associated with each TPM. */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601668233871_561008_14353", "name": "base_Property", "visibility": "private", "association": "_19_0_3_2b0010b_1601668233871_180735_14352"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Property"}]}
        }
        metadata def 'kppSpecification' {
            doc /* Source profile stereotype: kppSpecification
            XMI id: _19_0_3_2b0010b_1603550607909_173509_14549
            «kppSpecification» is a «Block» that specifies a technical measure, constraints, and measurement activities used to provide insight into the progress made in the definition and development of the technical solution, risks, and issues. «kppSpecification» is a refinement of a Key Performance Parameter (KPP) requirement of a «Block». KPPs are a critical subset of Technical Measures representing the most critical capabilities and characteristics. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1603550632725_797014_14577", "general": "_19_0_3_2b0010b_1614283840256_215949_1862"}, "references": []}
        }
        metadata def 'KPP' {
            doc /* Source profile stereotype: KPP
            XMI id: _19_0_3_2b0010b_1603550674761_583894_14584
            Key Performance Parameter (KPP) represents a performance property of a of a system (or other element). KPPs are a critical subset of Technical Measures representing the most critical capabilities and characteristics. The «kpp» stereotype is applied to a «ValueProperty» of a «Block». «kpp» Satisfy «kppRequirtement». */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1604693153420_190182_14497", "name": "base_Property", "visibility": "private", "association": "_19_0_3_2b0010b_1604693153420_591986_14496"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Property"}]}
        }
        metadata def 'MeasurementSpecification' {
            doc /* Source profile stereotype: MeasurementSpecification
            XMI id: _19_0_3_2b0010b_1614283840256_215949_1862
            Measurement Specification is a «Block» that specifies a technical measure, constraints, and measurement activities used to provide insight into the progress made in the definition and development of the technical solution, risks, and issues.
            The «MeasurementSpecification» is an abstract stereotype that is the base for defining specific measurement specifications. This is an extension of «Block» to allow the full capability of a «Block» to be used in the specification of a measurement.
            A MeasurementSpecification are intended to be Validated by a ValidationActivity. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1614443737421_665970_3684"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1614283876560_412388_1898", "name": "summary", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-String_PackageableElement"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1614443737456_675565_3686", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1614443737456_501755_3685"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1614452300538_901615_5385", "name": "Id", "visibility": "public", "isID": "true"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/PrimitiveTypes.xmi#String"}]}
        }
        metadata def 'mopRequirement' {
            doc /* Source profile stereotype: mopRequirement
            XMI id: _19_0_3_2b0010b_1615816615229_751396_2399
            A Measure of Performance (MoP) Requirement («mopRequirement») is a requirement specific to a «mop» property that specifies performance criteria for the element. «mopRequirement» is a type of Performance Requirement («performanceRequirement») that is satisfied by a «mop» property of a «Block».
            In a «refine», the «mopSpecification» is the supplier property and the client property is a «mopRequirement». In a «satisfy», the «mopRequirement» is the supplier property and the client property is a «mop». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1615816693519_347266_2508", "general": "_19_0_3_2b0010b_1620748211298_3489_78"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1615816693531_384148_2510", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1615816693531_582660_2509"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'tpmRequirement' {
            doc /* Source profile stereotype: tpmRequirement
            XMI id: _19_0_3_2b0010b_1615816634530_574230_2426
            A Technical Performance Measure (TPM) Requirement («tpmRequirement») is a requirement specific to a «tpm» property that specifies performance criteria for the element. «mopRequirement» is a type of Performance Requirement («performanceRequirement») that is satisfied by a «tpm» property of a «Block».
            In a «refine», the «tpmSpecification» is the supplier property and the client property is a «tpmRequirement». In a «satisfy», the «tpmRequirement» is the supplier property, and the client property is a «tpm». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1615816697034_660622_2516", "general": "_19_0_3_2b0010b_1620748211298_3489_78"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1615816697044_628351_2519", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1615816697044_421650_2518"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'moeRequirement' {
            doc /* Source profile stereotype: moeRequirement
            XMI id: _19_0_3_2b0010b_1615816651776_286275_2453
            A Measure of Performance (MoE) Requirement («moeRequirement») is a requirement specific to a «MoE» property that specifies performance criteria for the element. «moeRequirement» is a type of Performance Requirement («performanceRequirement») that is satisfied by a «MoE» property of a «Block».
            In a «refine», the «moeSpecification» is the supplier property, and the client property is a «moeRequirement». In a «satisfy», the «moeRequirement» is the supplier property, and the client property is a «MoE». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1615816701012_777052_2525", "general": "_19_0_3_2b0010b_1620748211298_3489_78"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1615816701022_338001_2527", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1615816701022_434394_2526"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'kppRequirement' {
            doc /* Source profile stereotype: kppRequirement
            XMI id: _19_0_3_2b0010b_1615816671041_264736_2480
            A Key Performance (KPP) Requirement («kppRequirement») is a requirement specific to a «kpp» property that specifies performance criteria for the property. «kppRequirement» is a type of Performance Requirement («performanceRequirement») that is satisfied by a KPP property of a «Block».
            In a «refine», the «kppSpecification» is the supplier property, and the client property is a «kppRequirement». In a «satisfy», the «kppRequirement» is the supplier property, and the client property is a «kpp». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1615816706254_873694_2533", "general": "_19_0_3_2b0010b_1620748211298_3489_78"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1615816706266_117051_2535", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1615816706266_772968_2534"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
    }
    package 'Architecture Structures Profile' {
        metadata def 'Component' {
            doc /* Source profile stereotype: Component
            XMI id: _18_5_2_3880181_1529417321789_403764_64447
            The «Component» is a type of «Block» that is a part of a subsystem element such as a hardware component, software, or procedures. «Component» satisfies «ComponentRequirement». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_18_5_2_3880181_1529417342367_322598_64476"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
        }
        metadata def 'Segment' {
            doc /* Source profile stereotype: Segment
            XMI id: _18_5_2_3880181_1529602112051_868875_65244
            A «Segment» is one of the parts into which something naturally separates or is divided. The «Segment» is abstract and intended to be implemented as a specific kind of segment like «GroundSegment» and «SpaceSegment». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1617462122983_524717_5367", "general": "_19_0_3_2b0010b_1620750953579_675487_629"}, "references": []}
        }
        metadata def 'CubeSat' {
            doc /* Source profile stereotype: CubeSat
            XMI id: _18_5_2_3880181_1529602336024_394574_65284
            The «CubeSat» is a type of «Satellite». A CubeSat follows the CubeSat form-factor established in 1999 by California Polytechnic State University and Stanford University.
            «CubeSat» is a part of a «SpaceSegment» and satisfies one or more «CubeSatRequirement». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601757120096_310831_15155", "general": "_19_0_3_2b0010b_1601757120090_718196_15129"}, "references": []}
        }
        metadata def 'Facility' {
            doc /* Source profile stereotype: Facility
            XMI id: _19_0_2_3880181_1572290137916_56175_13430
            A «Facility» is a place, amenity, or piece of equipment provided for a particular purpose.
            A «Facility» may be a part of another «Facility». Generally «Facility» is part of a «GroundSegment». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_2_3880181_1572290211167_782339_13458"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_11_5EAPbeta_be00301_1147424179914_458922_958"}]}
        }
        metadata def 'Equipment' {
            doc /* Source profile stereotype: Equipment
            XMI id: _19_0_2_3880181_1572365814841_548942_13459
            «Equipment» is a type of «Block» used to represent tools, machines, or other items required for a particular job or activity. Generally «Equipment» are part of a «Facility». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_2_3880181_1572365871740_389654_13487"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
        }
        metadata def 'Stakeholder' {
            doc /* Source profile stereotype: Stakeholder
            XMI id: _19_0_2_3880181_1574536276030_882809_13389
            A «Stakeholder» is a «Block» representing any entity (individual or organization) that has an interest in the system. Typical stakeholders include users, operators, decision-makers, parties to the agreement, regulatory bodies, developing agencies, support organizations, and society at large. Stakeholders can also represent an entity in opposition or threat to the system.
            Stakeholder is a replacement of the SysML Stakeholder and should be used in its place.
            Note: Because of the incompatibility between the SysML «Stakeholder» and the CSRM «Stakeholder», «ConcernOf» should be used to relate «ViewPoint» to «Stakeholder» property of the «ViewPoint». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_2_3880181_1574536394144_64630_13419"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
        }
        metadata def 'GroundSegment' {
            doc /* Source profile stereotype: GroundSegment
            XMI id: _19_0_3_2b0010b_1601406406213_237688_14631
            The «GroundSegment» is a kind of «Segment» composed of kinds of block like «Facility», «System» and «Equipment» or other «GroundSegment». The composed parts of «GroundSegment» represent systems and facilities like the following:
            • Ground stations, which provide communication interfaces with spacecraft (in the «SpaceSegment»)
            • Mission operations, from which spacecraft are managed, including activities like mission planning and scheduling, command and control of satellites, control of the ground equipment, mission telemetry processing, and mission data processing and distribution
            • Ground networks, which connect the other ground elements to one another
            • Remote terminals, used by support personnel
            • Spacecraft integration and test facilities
            • Launch facilities
            «GroundSegment» is a kind of «Segment» and usually satisfies one or more «GroundSegmentRequirement». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601406418325_549444_14659", "general": "_18_5_2_3880181_1529602112051_868875_65244"}, "references": []}
        }
        metadata def 'SpaceSegment' {
            doc /* Source profile stereotype: SpaceSegment
            XMI id: _19_0_3_2b0010b_1601406435362_893104_14666
            The «SpaceSegment» is a «Segment» that is composed of types of «spacecraft». In addition the «SpaceSegment» may be also be composed of «blocks» representing orbits, the uplink/downlink and the space environment (radiation, atmospheric density, solar wind, etc.). The «SpaceSegment» is controlled by and communicates with the «GroundSegment». The «SpaceSegment» satisfies one or more «SpaceSegment» requirements. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601406449779_316617_14694", "general": "_18_5_2_3880181_1529602112051_868875_65244"}, "references": []}
        }
        metadata def 'Spacecraft' {
            doc /* Source profile stereotype: Spacecraft
            XMI id: _19_0_3_2b0010b_1601667501518_959602_14044
            Spacecraft is a kind of System Block representing a spacecraft system—for example, satellite, rocket, rocket stage, interplanetary vehicle, or space station. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601667561440_93330_14163", "general": "_19_0_3_2b0010b_1620750745531_776560_550"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601667561451_673949_14165", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1601667561451_80591_14164"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'Satellite' {
            doc /* Source profile stereotype: Satellite
            XMI id: _19_0_3_2b0010b_1601757120090_718196_15129
            A «Satellite» is a kind of «Spacecraft» representing an orbital satellite system. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1601667557955_34798_14154", "general": "_19_0_3_2b0010b_1601667501518_959602_14044"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601757120177_56208_15158", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1601757120177_888003_15157"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'CubeSatDeployer' {
            doc /* Source profile stereotype: CubeSatDeployer
            XMI id: _19_0_3_2b0010b_1603313140977_658164_13681
            «CubeSatDeployer» is a type of «System» used to deploy one or more «CubeSat». */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1603313155465_885077_13709", "general": "_19_0_3_2b0010b_1620750745531_776560_550"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1603313155476_629636_13711", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1603313155476_873149_13710"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'Mission' {
            doc /* Source profile stereotype: Mission
            XMI id: _19_0_3_2b0010b_1614443161280_757856_3534
            A «Mission» describes what the system will do and the purpose of doing it. The Mission provides the context for defining measures of effectiveness and for the development of the Concept of Operations.
            A mission is accomplished by operational nodes completing one or more operational activities. An operational node can be an organization, individual(s), or system(s). Operational activities are actions that either transform one or more inputs into outputs or change the state of the system. A system provides capabilities through the execution of operational activities. There may be one or more missions composed of Space and Ground segments. Missions may also be composed of one or more missions (sub-missions). */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1614443189290_788897_3590"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_11_5EAPbeta_be00301_1147424179914_458922_958"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1614443189312_279102_3592", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1614443189312_387071_3591"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'ConcernOf' {
            doc /* Source profile stereotype: ConcernOf
            XMI id: _19_0_3_2b0010b_1619643905008_952641_430
            The «ConcernOf» stereotype is a dependency relationship used to relate an element of the model to a «Stakeholder». The client of the dependency can be any element and the supplier must be a type of «Stakeholder» that has a concern. The documentation of the dependency can be used to document the concern(s) the stakeholder has about the element.
            Another client of «ConcernOf» is the «StakeholderConcern». «StakeholderConcern» is a specialized requirement that can be used to document a stakeholder concern for use in creating derived requirements from the concern. */
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1619650304693_322193_573", "name": "unnamed1"}, "references": [{"{http://www.omg.org/spec/XMI/20131001}idref": "_19_0_3_2b0010b_1619643905008_952641_430"}]}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1619650304693_226783_574"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1619643986654_314797_487", "name": "base_Dependency", "visibility": "private", "association": "_19_0_3_2b0010b_1619643986654_313824_486"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Dependency"}]}
        }
    }
    package 'Validation and Verification Profile' {
        metadata def 'ValidationActivity' {
            doc /* Source profile stereotype: ValidationActivity
            XMI id: _18_5_2_3880181_1554842264428_327055_65039
            The «ValidationActivity» stereotype is applied to a process for validating requirements and technical specifications for correctness, implementability, testability, and that the requirement meets the needs of stakeholders. It often involves acceptance and suitability with customers. The requirements should also be annotated with a «rationale» comment. The activity to validate one or more requirements is often an analysis task performed in concert with the stakeholders to ensure the following:
            1) The set of requirements is correct, complete, and consistent,
            2) A model can be created that satisfies the requirements, and
            3) A real-world solution can be built and tested to prove that it satisfies the requirements.
            The state of the analysis is recorded by the validated property of «Validation».
            The «ValidationActivity» has a metaclass of Behavior, which allows the modeler to choose the appropriate type of modeling element (Activity, Sequence, etc.) to document the process. Note that the documentation of the ValidationActivity can also be used to capture the process. */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_18_5_2_3880181_1554842264459_160737_65066", "name": "A_Plan", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-String_PackageableElement"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_18_5_2_3880181_1554842264459_488518_65067", "name": "B_Procedure", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-String_PackageableElement"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_18_5_2_3880181_1554842264459_180081_65068", "name": "C_Conduct", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-String_PackageableElement"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_18_5_2_3880181_1554842264459_481609_65069", "name": "D_Result", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-String_PackageableElement"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_18_5_2_3880181_1554842264459_920346_65070", "name": "E_Status", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-String_PackageableElement"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1601564508646_297222_15861", "name": "base_Behavior", "visibility": "private", "association": "_19_0_3_2b0010b_1601564508646_563857_15860"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Behavior"}]}
        }
        metadata def 'Validation' {
            doc /* Source profile stereotype: Validation
            XMI id: _19_0_3_2b0010b_1601399071893_366607_14376
            «Validation» is a relationship between a source element («AbstractRequirement» or technical specification) and a client element («ValidationActivity»).
            The element has a boolean property, validated, which is used to document the status of the validation activity. The property has the following meaning:
            undefined(default): The element has not been validated.
            false: The supplier element has been validated and is considered invalid according to the «ValidationActivity».
            true: The supplier element has been validated and is deemed to be valid according to the «ValidationActivity».
            Note that the requirement or technical specification is the driver (supplier) of the relationship. This means that if the supplier element changes, the state of validated property should be changed to unknown until the «ValidationActivity» is performed for the changed element. Changes to a «ValidationActivity» implies the need for re-running the «ValidationActivity» for each supplier but are based on the possibility of invalidating the validation state. */
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1601402798638_381667_14481", "name": "1_supplier_is_requirement"}, "references": []}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1601402798638_118103_14482"}, "references": []}
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1616527116118_344958_1696", "name": "client_is_ValidationActivity"}, "references": [{"{http://www.omg.org/spec/XMI/20131001}idref": "_19_0_3_2b0010b_1601399071893_366607_14376"}]}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1616527116119_654454_1697"}, "references": []}
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1618609553807_259860_13", "name": "1_supplier_is_specification"}, "references": []}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1618609553811_323646_14"}, "references": []}
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1618611410942_448661_612"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Trace"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1616354259602_281192_923", "name": "validated", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-Boolean_PackageableElement"}]}
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1601402741350_57028_14471", "name": "getValidatesSpec"}, "references": []}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1601402741350_176718_14472"}, "references": []}
        }
        metadata def 'VerificationActivity' {
            doc /* Source profile stereotype: VerificationActivity
            XMI id: _19_0_3_2b0010b_1616859963947_857531_2330
            The «VerificationActivity» stereotype is intended to extend SysML to add a verificationMethod (from SysML) such that the Test Case or other behavior method can be annotated with the kind of verification. This improves the original SysML to allow a Requirement to have multiple verification methods by moving the method to the «VerificationActivity» rather than the Requirement.
            «VerificationActivity» has the attribute verificationMethod which is a VerificationMethodKind. Users are encouraged to set the verificationMethod on «VerificationActivity» rather than on the Requirement as this allows a requirement to be verified by many verification method kinds. */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1616859969007_225526_2360", "name": "base_Behavior", "visibility": "private", "association": "_19_0_3_2b0010b_1616859969007_299947_2359"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Behavior"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1616859969009_750613_2365", "name": "base_Operation", "visibility": "private", "association": "_19_0_3_2b0010b_1616859969009_419182_2364"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Operation"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "_19_0_3_2b0010b_1620750669030_739498_482", "id": "_19_0_3_2b0010b_1616859985880_504562_2369", "name": "verificationMethod", "visibility": "public"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1652455604527_860854_40", "name": "verifies", "isDerived": "true"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.AbstractRequirement"}]}
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1649539467119_402174_737", "name": "_getVerifies"}, "references": []}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1649539467120_696582_740"}, "references": []}
        }
        metadata def 'Verification' {
            doc /* Source profile stereotype: Verification
            XMI id: _19_0_3_2b0010b_1617463632588_168719_5413
            «Verification» is a relationship between a type of «AbstractRequirement» (the client of the Abstraction relationship) and a «VerificationActivity» (the supplier of the Abstraction relationship). The relationship is to associate a prescribed Verification Activity that tests for the satisfaction of a requirement.
            The «Verification» stereotype has a boolean property, verified, which is used to document the performance of the «VerificationActivity». The property has the following meaning:
            Unset(default): The supplier element has not been verified by the «VerificationActivity».
            false: The supplier element has failed the «VerificationActivity».
            true: The supplier element has passed the «VerificationActivity».
            A change of the supplier or client elements should be followed by a change to the verified property to unknown. The verification property is also changed whenever the «VerificationActivity» is performed.
            Note: The «Verification» should be used instead of the «verify» of SysML. */
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1617463632590_453459_5415", "name": "1_supplier_is_requirement"}, "references": [{"{http://www.omg.org/spec/XMI/20131001}idref": "_19_0_3_2b0010b_1617463632588_168719_5413"}]}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1617463632593_549219_5421"}, "references": []}
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1617463632591_100985_5416", "name": "client"}, "references": [{"{http://www.omg.org/spec/XMI/20131001}idref": "_19_0_3_2b0010b_1617463632588_168719_5413"}]}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1617463632594_151181_5422"}, "references": []}
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1617566500772_719190_1925"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Verify"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1617463632590_902604_5414", "name": "verified", "visibility": "public"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#_SysML_Libraries_PackageableElement-PrimitiveValueTypes_PackageableElement-Boolean_PackageableElement"}]}
        }
    }
    package 'Comments Profile' {
        metadata def 'Explanation' {
            doc /* Source profile stereotype: Explanation
            XMI id: _19_0_3_2b0010b_1617466891653_608929_7019
            The «Explanation» stereotype is a type of «comment» used to contain explanatory text. This type of comment is used for documenting what model elements are to be created, why they are created or other tutorial information. */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1617574570769_615318_1977", "name": "base_Comment", "visibility": "private", "association": "_19_0_3_2b0010b_1617574570768_148582_1976"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Comment"}]}
        }
        metadata def 'HowTo' {
            doc /* Source profile stereotype: HowTo
            XMI id: _19_0_3_2b0010b_1617466901812_111948_7046
            The «HowTo» stereotype is a type of «comment» used to contain instructions on how to do a modeling tool task. For example, how elements of the model are created. These comments are usually tool-specific instructions. */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1617574625074_87782_1983", "name": "base_Comment", "visibility": "private", "association": "_19_0_3_2b0010b_1617574625074_840557_1982"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Comment"}]}
        }
    }
    package 'SysML Extensions' {
        metadata def 'performanceRequirement' {
            doc /* Source profile stereotype: performanceRequirement
            XMI id: _19_0_3_2b0010b_1620748211298_3489_78
            Requirement that quantitatively measures the extent to which a system, or a system part, satisfies a required capability or condition.
            Note: This stereotype should be used instead of the «performanceRequirement» in the SysML non-normative extension of SysML. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1620751654589_955452_746", "general": "_19_0_3_2b0010b_1620749875083_177494_209"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620748211304_47227_81", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1620748211308_467205_83"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'MoE' {
            doc /* Source profile stereotype: MoE
            XMI id: _19_0_3_2b0010b_1620748288364_156227_107
            Measure of Effectiveness (MoE) represents a performance property of a system (or other element). The «moe» stereotype is applied to a «valueProperty» to mark the property as a MoE. The stereotype indicates an engineering performance measure. A «moe» property represents a parameter whose value is can be used to measure the effectiveness of a «Block». MoE are measures designed to correspond to the accomplishment of mission objectives and the achievement of desired results. MoE quantify the results to be obtained by a system.
            Each «MoE» should satisfy a kind of «moeRequirement».
            Note: This stereotype should be used instead of the «moe» in the SysML non-normative extension of SysML. */
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620748288366_293178_110", "name": "base_Property", "visibility": "private", "association": "_19_0_3_2b0010b_1620748288367_977711_111"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Property"}]}
        }
        metadata def 'ExtRequirement' {
            doc /* Source profile stereotype: ExtRequirement
            XMI id: _19_0_3_2b0010b_1620749875083_177494_209
            A mix-in stereotype that contains generally useful attributes for requirements.
            Note: This stereotype should be used instead of the «extendedRequirement» in the SysML non-normative extension of SysML. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1620749875089_320464_216"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Requirement"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620749875086_287479_212", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1620749875090_3773_217"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620749875087_88981_213", "name": "source", "visibility": "private"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/PrimitiveTypes.xmi#String"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "_19_0_3_2b0010b_1620750669029_844651_481", "id": "_19_0_3_2b0010b_1620749875087_967174_214", "name": "risk", "visibility": "private"}, "references": []}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "_18_5_2_3880181_1554842264428_327055_65039", "id": "_19_0_3_2b0010b_1649536452699_66905_656", "name": "validatedBy", "visibility": "private", "isDerived": "true"}, "references": []}
            // Source-only {"kind": "uml:Constraint", "attributes": {"type": "uml:Constraint", "id": "_19_0_3_2b0010b_1601402741350_57028_14471", "name": "getValidatedBySpec"}, "references": []}
            // Source-only {"kind": "uml:OpaqueExpression", "attributes": {"type": "uml:OpaqueExpression", "id": "_19_0_3_2b0010b_1601402741350_176718_14472"}, "references": []}
        }
        metadata def 'System' {
            doc /* Source profile stereotype: System
            XMI id: _19_0_3_2b0010b_1620750745531_776560_550
            A System is an artificial artifact consisting of blocks that pursue a common goal that cannot be achieved by the system's individual elements. A block can be software, hardware, a person, or an arbitrary unit.
            Note: This stereotype should be used instead of the «System» in the SysML non-normative extension of SysML. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1620750745533_948922_554"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620750745533_162789_553", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1620750745533_856189_555"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'SystemContext' {
            doc /* Source profile stereotype: SystemContext
            XMI id: _19_0_3_2b0010b_1620750953579_675487_629
            A SystemContext element is a virtual container that includes the entire system and its actors.
            Note: This stereotype should be used instead of the system context» in the SysML non-normative extension of SysML. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1620750953582_818032_633"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620750953582_336598_632", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1620750953583_480006_634"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'Subsystem' {
            doc /* Source profile stereotype: Subsystem
            XMI id: _19_0_3_2b0010b_1620751752335_165744_787
            A Subsystem is a - typically large - encapsulated block within a larger system.
            Note: This stereotype should be used instead of the «Subsystem» in the SysML non-normative extension of SysML. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1620751752339_909105_793"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620751752339_120583_792", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1620751752340_959475_794"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
        metadata def 'Domain' {
            doc /* Source profile stereotype: Domain
            XMI id: _19_0_3_2b0010b_1620751752336_574734_789
            A «Domain» block represents an entity, a concept, a location, or a person from the real-world domain. A «Domain» block is part of the system knowledge.
            Note: This stereotype should be used instead of the «Domain» in the SysML non-normative extension of SysML. */
            // Source-only {"kind": "uml:Generalization", "attributes": {"type": "uml:Generalization", "id": "_19_0_3_2b0010b_1620751752343_495971_797"}, "references": [{"href": "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block"}]}
            // Source-only {"kind": "uml:Property", "attributes": {"type": "uml:Property", "id": "_19_0_3_2b0010b_1620751752341_865169_796", "name": "base_Class", "visibility": "private", "association": "_19_0_3_2b0010b_1620751752345_134857_798"}, "references": [{"href": "http://www.omg.org/spec/UML/20131001/UML.xmi#Class"}]}
        }
    }
}
