// Source-scoped direct ConcernOf navigation. No 2025 ConcernOf links exist.
package CSRMRelationshipNavigation {
    metadata def CustomizationSource {
        attribute sourceRef : ScalarValues::String;
        attribute applicationRef : ScalarValues::String;
        attribute sourceTargetRef : ScalarValues::String;
        attribute convertedOwnedProperties : ScalarValues::Integer;
    }
    metadata def SourceRelationshipInput {
        attribute sourceRef : ScalarValues::String;
        attribute sourceCustomizationRef : ScalarValues::String;
        attribute sourceTargetStereotypeRef : ScalarValues::String;
        attribute relationKind : ScalarValues::String;
        attribute direction : ScalarValues::String;
        attribute sourceLinkCount : ScalarValues::Integer;
        attribute isSourceFeature : ScalarValues::Boolean;
        attribute bindingContract : ScalarValues::String;
    }
    metadata def DerivedPropertySource {
        attribute sourceRef : ScalarValues::String;
        attribute applicationRef : ScalarValues::String;
        attribute sourceTypeRef : ScalarValues::String;
        attribute sourceRelationRef : ScalarValues::String;
        attribute sourceDirection : ScalarValues::String;
    }
    metadata def PropertyGroupSource {
        attribute sourceRef : ScalarValues::String;
        attribute applicationRef : ScalarValues::String;
        attribute qualifierRef : ScalarValues::String;
        attribute qualifierName : ScalarValues::String;
        attribute showGroupInDependencyMatrix : ScalarValues::Boolean;
        attribute showGroupInElementSpecification : ScalarValues::Boolean;
        attribute showGroupInGoTo : ScalarValues::Boolean;
        attribute showGroupInQuickProperties : ScalarValues::Boolean;
        attribute showGroupInRelationMap : ScalarValues::Boolean;
        attribute useAsNode : ScalarValues::Boolean;
    }
    calc def ConcernOfSuppliers {
        @CSRMRelationshipNavigation::DerivedPropertySource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1619729706298_14887_42454";
            applicationRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1619729706298_444769_42455";
            sourceTypeRef = "http://www.omg.org/spec/UML/20131001/UML.xmi#Element";
            sourceRelationRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1619643905008_952641_430";
            sourceDirection = "DIRECT";
        }
        in ref directConcernOfLinks : KerML::Dependency [0..*];
        return ref stakeholders : KerML::Element [0..*];
        directConcernOfLinks.supplier
    }
}
