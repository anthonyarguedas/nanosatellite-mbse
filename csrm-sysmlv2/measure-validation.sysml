// Each constraint receives targets already filtered by the relation and stereotype.
// The Refined rule inputs are bound by asserted usages in model.sysml.
package CSRMMeasureValidation {
    constraint def 'moeRequirement Refined' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921871_998662_22471";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816651776_286275_2453";
            targetRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_243878_66132";
            relation = "SysML v1 Refine: client to supplier, exact target stereotype";
        }
        in ref matchingRefineTargets [0..*];
        SequenceFunctions::size(matchingRefineTargets) > 0
    }
    constraint def 'mopRequirement Refined' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921871_888241_22472";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816615229_751396_2399";
            targetRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_300770_66133";
            relation = "SysML v1 Refine: client to supplier, exact target stereotype";
        }
        in ref matchingRefineTargets [0..*];
        SequenceFunctions::size(matchingRefineTargets) > 0
    }
    constraint def 'kppRequirement Refined' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921871_612172_22473";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816671041_264736_2480";
            targetRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550607909_173509_14549";
            relation = "SysML v1 Refine: client to supplier, exact target stereotype";
        }
        in ref matchingRefineTargets [0..*];
        SequenceFunctions::size(matchingRefineTargets) > 0
    }
    constraint def 'tpmRequirement Refined' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921871_115072_22474";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816634530_574230_2426";
            targetRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_601405_66134";
            relation = "SysML v1 Refine: client to supplier, exact target stereotype";
        }
        in ref matchingRefineTargets [0..*];
        SequenceFunctions::size(matchingRefineTargets) > 0
    }
    // These inputs are the Satisfy clients selected by each native measure type.
    constraint def 'kppRequirement Satisfy & kpp stereotype' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921872_379595_22475";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816671041_264736_2480";
            targetRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550674761_583894_14584";
            relation = "SysML v1 Satisfy: KPP Property client to kppRequirement supplier";
        }
        in attribute matchingKppSatisfiers : CSRMNativeMeasures::KPP [0..*];
        SequenceFunctions::size(matchingKppSatisfiers) > 0
    }
    constraint def 'moeRequirement Satisfy by MoE Param' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921872_862866_22476";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816651776_286275_2453";
            targetRef = "SysML Profile.mdzip#_12_1_8740266_1172576734625_231808_234";
            relation = "SysML v1 Satisfy: moe Property client to moeRequirement supplier";
        }
        in attribute matchingMoESatisfiers : CSRMNativeMeasures::MoE [0..*];
        SequenceFunctions::size(matchingMoESatisfiers) > 0
    }
    constraint def 'mopRequirement Satisfy by MoP Param' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921872_481818_22477";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816615229_751396_2399";
            targetRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588150_289586_66140";
            relation = "SysML v1 Satisfy: mop Property client to mopRequirement supplier";
        }
        in attribute matchingMoPSatisfiers : CSRMNativeMeasures::MoP [0..*];
        SequenceFunctions::size(matchingMoPSatisfiers) > 0
    }
    constraint def 'tpmRequirement Satisfy by TPM Param1' {
        @CSRMv1Metadata::ValidationRuleSource {
            sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921873_229930_22478";
            scopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816634530_574230_2426";
            targetRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588150_801304_66141";
            relation = "SysML v1 Satisfy: TPM Property client to tpmRequirement supplier";
        }
        in attribute matchingTPMSatisfiers : CSRMNativeMeasures::TPM [0..*];
        SequenceFunctions::size(matchingTPMSatisfiers) > 0
    }
}
