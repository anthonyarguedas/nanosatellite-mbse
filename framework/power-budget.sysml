package PowerBudgetModel {
    private import ScalarValues::*;
    private import ControlFunctions::*;
    private import SequenceFunctions::*;
    doc /* Preliminary steady load demand at component terminals.
     * Mode fractions describe separate sunlight and eclipse populations.
     * They establish no ordering, simultaneous peak or startup assessment.
     * Sources and assumptions belong to each mode draw. Missing values stay unbound.
     */
    enum def ValueBasis { estimated; typical; maximum; measured; }
    attribute def ModeDraw :> EPSModel::ModeLoadProfile {
        attribute display_name : String;
        attribute watts : Real[0..1];
        attribute basis : ValueBasis;
        attribute source_note : String;
        attribute conditions : String;
        attribute :>> load_law = EPSModel::LoadLawKind::constant_power;
        attribute :>> power = watts * 1[SI::W];
        assert constraint nonnegative { watts->forAll { in p : Real; p >= 0 } }
    }
    attribute def SpacecraftMode :> EPSModel::OperatingMode {
        attribute display_name : String;
        attribute :>> kind = EPSModel::ModeKind::custom;
        attribute sunlight_fraction : Real[0..1];
        attribute eclipse_fraction : Real[0..1];
        assert constraint fractionBounds {
            sunlight_fraction->forAll { in f : Real; f >= 0 and f <= 1 } and
            eclipse_fraction->forAll { in f : Real; f >= 0 and f <= 1 }
        }
    }
    requirement def ComponentPowerLimit {
        attribute mode : SpacecraftMode[0..1];
        ref part power_scope[0..*];
        attribute power_limit_W : Real[0..1];
        attribute draw_power_W : Real[0..1];
        attribute power_limit : ISQ::PowerValue[0..1] = power_limit_W * 1[SI::W];
        require constraint drawFits { power_limit_W >= 0 and draw_power_W >= 0 and draw_power_W <= power_limit_W }
    }
    requirement def PowerLimit :> ComponentPowerLimit {
        attribute allocated_power_W : Real[0..1];
        require constraint allocationsFit { allocated_power_W >= 0 and allocated_power_W <= power_limit_W }
    }
    part def ModeContribution {
        ref part physical_load : EPSModel::HardwareComponent;
        attribute mode : SpacecraftMode;
        attribute profile : ModeDraw[0..1];
        attribute quantity : Integer;
        attribute power_W : Real[0..1] = quantity * profile.watts;
        attribute sunlight_power_W : Real[0..1] = power_W * mode.sunlight_fraction;
        attribute eclipse_power_W : Real[0..1] = power_W * mode.eclipse_fraction;
        assert constraint positiveQuantity { quantity > 0 }
    }
    part def IlluminationBudget {
        attribute modes : SpacecraftMode[0..*];
        attribute sunlight_power_W : Real[0..1];
        attribute eclipse_power_W : Real[0..1];
        attribute sunlight_power : ISQ::PowerValue[0..1] = sunlight_power_W * 1[SI::W];
        attribute eclipse_power : ISQ::PowerValue[0..1] = eclipse_power_W * 1[SI::W];
        doc /* Exported usages bind averages to contributing mode draws.
         * The UI checks completeness and fraction sums before exposing a value.
         * LoadEnergy consumes these already weighted averages with duty one.
         * Path efficiency remains in MinimumPanelPower and is applied once.
         */
    }
}
