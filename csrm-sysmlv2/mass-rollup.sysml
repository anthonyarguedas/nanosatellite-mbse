// Reimplemented SysML v1 mass rollup. No source unit or quantity kind is declared.
// subMass is abstract. Nine CubeSat subsystem and 30 eligible component parts subset it.
package CSRMMassRollUp {
    calc def MassTotal {
        @CSRMv1Metadata::MassRollUpSource {
            sourceRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312270_321176_13835";
            sourceKind = "SysML v1 ConstraintBlock total: total = parent + sum(child)";
        }
        in attribute parent : ScalarValues::Real;
        in attribute child : ScalarValues::Real [0..*];
        return attribute total : ScalarValues::Real;
        parent + RealFunctions::sum(child)
    }
    part def MassRollUpPattern {
        @CSRMv1Metadata::MassRollUpSource {
            sourceRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312269_537593_13833";
            sourceKind = "SysML v1 Block and rollup pattern";
        }
        abstract part subMass : MassRollUpPattern [0..*] {
            @CSRMv1Metadata::MassRollUpSource {
                sourceRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                sourceKind = "composite derived union";
            }
        }
        attribute mass : ScalarValues::Real default = 0.0 {
            @CSRMv1Metadata::MassRollUpSource {
                sourceRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_396376_13891";
                sourceKind = "SysML v1 Real ValueProperty with default 0.0";
            }
        }
        derived attribute totalMass : ScalarValues::Real = MassTotal(mass, subMass.totalMass) {
            @CSRMv1Metadata::MassRollUpSource {
                sourceRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_412848_13892";
                sourceKind = "SysML v1 derived Real ValueProperty";
            }
        }
    }
}
