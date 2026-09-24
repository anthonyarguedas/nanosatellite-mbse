// Native value types for the four source performance property stereotypes.
package CSRMNativeMeasures {
    attribute def KPP {
        doc /*Key Performance Parameter (KPP) represents a performance property of a of a system (or other element). KPPs are a critical subset of Technical Measures representing the most critical capabilities and characteristics. The «kpp» stereotype is applied to a «ValueProperty» of a «Block». «kpp» Satisfy «kppRequirtement».*/
        @CSRMv1Metadata::NativePropertyTypeSource {
            sourceRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550674761_583894_14584";
            sourceKind = "SysML v1 performance Property stereotype";
        }
    }
    attribute def MoE {
        doc /*A measure of effectiveness (moe) represents a parameter whose value is critical for achieving the desired mission cost effectiveness.*/
        @CSRMv1Metadata::NativePropertyTypeSource {
            sourceRef = "SysML Profile.mdzip#_12_1_8740266_1172576734625_231808_234";
            sourceKind = "SysML v1 performance Property stereotype";
        }
    }
    attribute def MoP {
        doc /*The «mop» stereotype represents a performance property of a system (or other element). The «mop» stereotype is applied to a «ValueProperty» element to mark the property as a Measure of performance (MoP). MoP is an engineering performance measure that provides a value necessary for meeting a Measure of Effectiveness (MoE). «mop» satisfy «mopRequirement». */
        @CSRMv1Metadata::NativePropertyTypeSource {
            sourceRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588150_289586_66140";
            sourceKind = "SysML v1 performance Property stereotype";
        }
    }
    attribute def TPM {
        doc /*The «tpm» stereotype represents a performance property of a system (or other element). Technical Performance Measure (TPM) of the attributes of a system element to determine how well the system element is satisfying or expected to satisfy, specified technical requirements. They are based on the driving requirements or technical parameters of high risk or significance - e.g., mass, power, or data rate. Actual versus planned progress of TPMs are tracked so the systems engineer or project manager can assess progress and the risk associated with each TPM.*/
        @CSRMv1Metadata::NativePropertyTypeSource {
            sourceRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588150_801304_66141";
            sourceKind = "SysML v1 performance Property stereotype";
        }
    }
}
