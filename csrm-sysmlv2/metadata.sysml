// Records source identities without asserting SysML v2 quantity or unit semantics.
package CSRMv1Metadata {
    metadata def ExternalProjectSource {
        attribute sourceRef : ScalarValues::String;
        attribute projectId : ScalarValues::String;
        attribute evidence : ScalarValues::String;
    }

    metadata def ConvertedClassSource {
        attribute sourceRef : ScalarValues::String;
        attribute stereotypeRef : ScalarValues::String;
        attribute sourceSummary : ScalarValues::String;
        attribute sourceId : ScalarValues::String;
    }

    metadata def ConvertedPartSource {
        attribute sourceRef : ScalarValues::String;
        attribute associationRef : ScalarValues::String;
        attribute sourceTypeRef : ScalarValues::String;
        attribute sourceMultiplicity : ScalarValues::String;
    }

    metadata def ExpandedValidationScope {
        attribute sourceRef : ScalarValues::String;
        attribute originalScopeRef : ScalarValues::String;
        attribute appliedClassRef : ScalarValues::String;
        attribute decision : ScalarValues::String;
    }

    metadata def NativePropertyTypeSource {
        attribute sourceRef : ScalarValues::String;
        attribute sourceKind : ScalarValues::String;
    }

    metadata def NativeStructureTypeSource {
        attribute sourceRef : ScalarValues::String;
        attribute sourceKind : ScalarValues::String;
    }

    metadata def MassRollUpSource {
        attribute sourceRef : ScalarValues::String;
        attribute sourceKind : ScalarValues::String;
    }

    metadata def ChosenRollUpSubsetting {
        attribute sourceRef : ScalarValues::String;
        attribute chosenTargetRef : ScalarValues::String;
        attribute isSourceSubsetting : ScalarValues::Boolean;
    }

    metadata def ExcludedRollUpContributor {
        attribute sourceRef : ScalarValues::String;
        attribute sourceTypeRef : ScalarValues::String;
        attribute reason : ScalarValues::String;
    }

    metadata def ChosenOrbitReference {
        attribute sourceRef : ScalarValues::String;
        attribute chosenTypeRef : ScalarValues::String;
        attribute sourceHadType : ScalarValues::Boolean;
        attribute sourceMultiplicity : ScalarValues::String;
    }

    metadata def ChosenOrbitBinding {
        attribute sourceRef : ScalarValues::String;
        attribute chosenTargetRef : ScalarValues::String;
        attribute sourceHadBinding : ScalarValues::Boolean;
        attribute interpretation : ScalarValues::String;
    }

    metadata def UntypedValuePropertySource {
        attribute sourceRef : ScalarValues::String;
        attribute sourceKind : ScalarValues::String;
        attribute sourceHadType : ScalarValues::Boolean;
        attribute sourceMultiplicity : ScalarValues::String;
        attribute sourceAggregation : ScalarValues::String;
        attribute quantityKindRef : ScalarValues::String;
        attribute unitRef : ScalarValues::String;
    }

    metadata def ReifiedRefineTargets {
        attribute sourceRefineIds : ScalarValues::String;
        attribute targetSourceRef : ScalarValues::String;
    }

    metadata def CorrectedRefineSource {
        attribute sourceRef : ScalarValues::String;
        attribute originalClientRef : ScalarValues::String;
        attribute originalSupplierRef : ScalarValues::String;
        attribute isRefine : ScalarValues::Boolean;
    }

    metadata def ValidationRuleSource {
        attribute sourceRef : ScalarValues::String;
        attribute scopeRef : ScalarValues::String;
        attribute targetRef : ScalarValues::String;
        attribute relation : ScalarValues::String;
    }

    metadata def ValueTypeSource {
        attribute sourceRef : ScalarValues::String;
        attribute quantityKindRef : ScalarValues::String;
        attribute quantityKindName : ScalarValues::String;
        attribute unitRef : ScalarValues::String;
        attribute unitName : ScalarValues::String;
    }
}
