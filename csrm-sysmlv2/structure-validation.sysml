// The 2025 source has no SpaceSegment applications. The user authorized a scope expansion.
package CSRMStructureValidation {
    constraint def 'Space Segment Compostion' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921881_949808_22493";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1601406435362_893104_14666";
            targetRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1601667501518_959602_14044";
            relation = "Chosen: at least one direct composite spacecraft part, not the original decomposition predicate";
        }
        in ref part directSpacecraftParts : CSRMNativeStructures::Spacecraft [0..*];
        SequenceFunctions::size(directSpacecraftParts) > 0
    }
}
