// Native owner navigation for the source Duplicate customization.
// The missing vendor Duplicate::ownedElement is an unbound reflective input.
package CSRMDuplicateNavigation {
    metadata def CustomizationSource {
        attribute sourceRef : ScalarValues::String;
        attribute applicationRef : ScalarValues::String;
        attribute sourceHadTarget : ScalarValues::Boolean;
    }
    metadata def ChosenOwnedElementInput {
        attribute sourceClassRef : ScalarValues::String;
        attribute vendorProfile : ScalarValues::String;
        attribute vendorStereotype : ScalarValues::String;
        attribute vendorTag : ScalarValues::String;
        attribute isSourceFeature : ScalarValues::Boolean;
        attribute interpretation : ScalarValues::String;
    }
    metadata def DerivedPropertySource {
        attribute sourceRef : ScalarValues::String;
        attribute applicationRef : ScalarValues::String;
        attribute sourceTypeRef : ScalarValues::String;
        attribute sourceNavigation : ScalarValues::String;
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
    calc def DuplicateOwners {
        @CSRMDuplicateNavigation::DerivedPropertySource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106769_572101_10742";
            applicationRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106769_23436_10743";
            sourceTypeRef = "http://www.omg.org/spec/UML/20131001/UML.xmi#Element";
            sourceNavigation = "Duplicate.ownedElement.owner";
        }
        in ref ownedElements : KerML::Element [0..*] ordered;
        return ref owners : KerML::Element [0..*] ordered;
        ownedElements.owner
    }
    calc def DuplicateOwnerQualifiedNames {
        @CSRMDuplicateNavigation::DerivedPropertySource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836482637_253285_12867";
            applicationRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836482637_469693_12868";
            sourceTypeRef = "http://www.omg.org/spec/UML/20131001/PrimitiveTypes.xmi#String";
            sourceNavigation = "Duplicate.ownedElement.owner.qualifiedName";
        }
        in ref ownedElements : KerML::Element [0..*] ordered;
        return attribute names : ScalarValues::String [0..*] ordered;
        ownedElements.owner.qualifiedName
    }
}
