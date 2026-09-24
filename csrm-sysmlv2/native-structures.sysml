// CSRM architecture stereotypes as native part types, not source UML classes.
package CSRMNativeStructures {
    part def Spacecraft {
        @CSRMv1Metadata::NativeStructureTypeSource {
            sourceRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1601667501518_959602_14044";
            sourceKind = "CSRM UML Class stereotype";
        }
    }
    part def Satellite :> Spacecraft {
        @CSRMv1Metadata::NativeStructureTypeSource {
            sourceRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1601757120090_718196_15129";
            sourceKind = "CSRM UML Class stereotype";
        }
    }
    part def CubeSat :> Satellite {
        @CSRMv1Metadata::NativeStructureTypeSource {
            sourceRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529602336024_394574_65284";
            sourceKind = "CSRM UML Class stereotype";
        }
    }
}
