package CatalogModel {
    private import ScalarValues::*;
    private import ControlFunctions::*;
    private import SequenceFunctions::*;
    doc /* Generic normalized catalog interchange. Record fields follow the frozen TSV
     * headers. Optional cells are absent values, never zero. IDs are case sensitive.
     * self is the implicit product root. Other element IDs are product scoped.
     * Catalog records are observations under stated conditions. They are separate
     * from design selections and operating points. Typical values are not bounds.
     * Absolute maxima are stress ratings, not recommended operating limits.
     * Importers validate finite decimals, UTC timestamps, hashes, lowercase codes,
     * dictionary membership, unit conversion, composite keys and parent acyclicity.
     * Source locators contain structured locations, not interpretation prose.
     * Product levels distinguish controller ICs from complete modules. Nested
     * ratings apply to their named elements. Pin coverage may be partial.
     * Resource formats identify actual artifacts. PDF circuits are not editable
     * native schematics. Library IDs require checked library membership.
     */
    enum def UnitCode :> String {
        enum dimensionless = "1";
        enum volt = "V";
        enum ampere = "A";
        enum watt = "W";
        enum watt_per_square_metre = "W/m2";
        enum watt_hour = "Wh";
        enum ampere_hour = "Ah";
        enum second = "s";
        enum kelvin = "K";
        enum hertz = "Hz";
        enum metre = "m";
        enum square_metre = "m2";
        enum kilogram = "kg";
        enum ohm = "ohm";
        enum farad = "F";
        enum henry = "H";
        enum kelvin_per_watt = "K/W";
        enum volt_per_kelvin = "V/K";
        enum ampere_per_kelvin = "A/K";
        enum per_kelvin = "1/K";
        enum volt_per_ampere = "V/A";
        enum per_second = "s^-1";
        enum bit = "bit";
        enum byte = "byte";
        enum joule = "J";
        enum ampere_per_square_metre = "A/m2";
        enum kilogram_per_square_metre = "kg/m2";
        enum per_square_metre = "m^-2";
        enum per_square_metre_second = "m^-2/s";
        enum metre_per_second = "m/s";
    }
    enum def DefinitionKind { parameter; feature; curve_axis; condition_parameter; }
    enum def ScalarKind :> String { enum real_number = "Real"; enum integer_number = "Integer"; enum string_value = "String"; enum boolean_value = "Boolean"; }
    attribute def DefinitionRecord {
        attribute definition_kind : DefinitionKind;
        attribute name : String;
        attribute sysml_owner : String;
        attribute scalar_type : ScalarKind;
        attribute canonical_unit : UnitCode[0..1];
    }
    enum def ProductLevel { cell; discrete; integrated_circuit; module; assembly; board; }
    enum def ProductType :> String {
        enum SolarArray = "EPSModel::SolarArray";
        enum Battery = "EPSModel::Battery";
        enum DCDCConverter = "EPSModel::DCDCConverter";
        enum BatteryCharger = "EPSModel::BatteryCharger";
        enum LoadSwitch = "EPSModel::LoadSwitch";
        enum BatteryProtector = "EPSModel::BatteryProtector";
        enum IdealDiode = "EPSModel::IdealDiode";
        enum Processor = "EPSModel::Processor";
        enum NonvolatileMemory = "EPSModel::NonvolatileMemory";
        enum RealTimeClock = "EPSModel::RealTimeClock";
        enum CurrentSensor = "EPSModel::CurrentSensor";
        enum TemperatureSensor = "EPSModel::TemperatureSensor";
        enum Heater = "EPSModel::Heater";
        enum IntegratedEPS = "EPSModel::IntegratedEPS";
    }
    enum def ValueKind { minimum; typical; maximum; nominal; absolute_maximum; fixed; 'derived';
        minimum_exclusive; maximum_exclusive; }
    doc /* Minimum and maximum condition bounds include their endpoints.
     * minimum_exclusive and maximum_exclusive retain strict inequalities.
     * Fixed values are stated test settings, not zero-tolerance product claims.
     */
    enum def ElementKind { rail; channel; solar_input; battery_interface; data_interface; thermal_interface; supply_pin_group; }
    enum def DocumentKind { datasheet; product_page; reference_design; cad_library; application_note; simulation_model; }
    enum def ResourceKind { reference_schematic; native_schematic; symbol; footprint; spice_model; ibis_model; pinout; reference_design; application_note; }
    enum def ResourceFormat { pdf; kicad_sch; kicad_sym; kicad_mod; lib; sub; asc; asy; zip; html; step; altium; orcad; }
    enum def PinKind { power_input; power_output; ground; analog_input; analog_output; digital_input; digital_output; bidirectional; passive; no_connect; }
    enum def PinDirection :> String { enum input = "in"; enum output = "out"; enum input_output = "inout"; enum no_direction = "none"; }
    enum def PointKind { tabulated; digitized; 'derived'; }
    attribute def ProductRecord {
        attribute product_id : String;
        attribute sysml_type : ProductType;
        attribute manufacturer : String;
        attribute part_number : String;
        attribute product_level : ProductLevel;
        attribute product_url : String[0..1];
        attribute datasheet_url : String[0..1];
    }
    attribute def ParameterRecord {
        attribute product_id : String;
        attribute element_id : String;
        attribute parameter_name : String;
        attribute value : Real;
        attribute value_kind : ValueKind;
        attribute unit : UnitCode;
        attribute condition_id : String[0..1];
        attribute source_id : String;
        attribute source_locator : String;
    }
    attribute def IntegerParameter :> ParameterRecord { attribute :>> value : Integer; }
    attribute def ConditionParameterRecord {
        attribute condition_id : String;
        attribute parameter_name : String;
        attribute value : Real;
        attribute value_kind : ValueKind;
        attribute unit : UnitCode;
        attribute source_id : String;
        attribute source_locator : String;
        doc /* Supplemental condition-parameters.tsv uses exactly these seven
         * columns. This is condition evidence without product or element keys.
         * Minimum/maximum observations preserve ranges. They do not authorize a
         * guessed midpoint. Exclusive bound kinds preserve strict endpoints.
         * Supply headroom means input/supply voltage minus output voltage.
         * A fixed zero headroom encodes equal input and output test voltages.
         * Decimal parsing and finite values are importer checks.
         */
    }
    attribute def IntegerConditionParameter :> ConditionParameterRecord {
        attribute :>> value : Integer;
    }
    attribute def FeatureEvidence {
        attribute product_id : String;
        attribute element_id : String;
        attribute feature_name : String;
        attribute source_id : String;
        attribute source_locator : String;
    }
    attribute def FeatureRecord :> FeatureEvidence {
        attribute value : String;
    }
    attribute def BooleanFeature :> FeatureEvidence {
        attribute value : Boolean;
    }
    doc /* FeatureRecord.value is the lexical TSV cell. BooleanFeature is its
     * decoded Boolean counterpart on owner types. String features retain exact
     * package/interface codes. Unknown features remain absent, not false.
     */
    doc /* Condition numeric fields use the units in their headers.
     * state_of_charge is a fraction. c_rate is the conventional hourly C-rate
     * multiplier. Missing conditions remain unspecified and are not universal.
     */
    attribute def ConditionRecord {
        attribute adc_conversion_time_code : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "adc_conversion_time_code"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute adc_resolution_bits : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "adc_resolution_bits"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute airflow_speed : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "airflow_speed"; :>> unit = CatalogModel::UnitCode::metre_per_second; }
        attribute ambient_temperature : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "ambient_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute auxiliary_clock_frequency : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "auxiliary_clock_frequency"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute backup_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "backup_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute bus_adc_full_scale_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "bus_adc_full_scale_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute bus_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "bus_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute bus_voltage_range_code : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "bus_voltage_range_code"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute calibration_interval : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "calibration_interval"; :>> unit = CatalogModel::UnitCode::second; }
        attribute clock_frequency : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "clock_frequency"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute common_mode_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "common_mode_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute conversion_averages : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "conversion_averages"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute conversion_cycle_frequency : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "conversion_cycle_frequency"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute conversion_period_code : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "conversion_period_code"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute conversion_time : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "conversion_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute crystal_load_capacitance : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "crystal_load_capacitance"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute differential_input_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "differential_input_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute enable_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "enable_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute enable_voltage_ratio : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "enable_voltage_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute final_temperature : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "final_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute fram_cache_hit_fraction : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "fram_cache_hit_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute gain_ratio : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "gain_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute initial_temperature : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "initial_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute initialization_pulse_duration : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "initialization_pulse_duration"; :>> unit = CatalogModel::UnitCode::second; }
        attribute input_logic_voltage_high_ratio : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "input_logic_voltage_high_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute input_logic_voltage_low_ratio : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "input_logic_voltage_low_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute inter_byte_time : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "inter_byte_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute irradiation_particle_energy : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "irradiation_particle_energy"; :>> unit = CatalogModel::UnitCode::joule; }
        attribute load_capacitance : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "load_capacitance"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute memory_wait_state_count : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "memory_wait_state_count"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute output_clock_frequency : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "output_clock_frequency"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute output_current : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "output_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute output_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "output_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute output_voltage_supply_headroom : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "output_voltage_supply_headroom"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute particle_fluence : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "particle_fluence"; :>> unit = CatalogModel::UnitCode::per_square_metre; }
        attribute particle_fluence_rate : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "particle_fluence_rate"; :>> unit = CatalogModel::UnitCode::per_square_metre_second; }
        attribute pga_attenuation_divisor : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "pga_attenuation_divisor"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute pull_up_resistance : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "pull_up_resistance"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute reference_voltage_ratio : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "reference_voltage_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute response_completion_fraction : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "response_completion_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute rtc_clock_frequency : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "rtc_clock_frequency"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute sense_current : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "sense_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute settling_fraction : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "settling_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute shunt_adc_range_code : CatalogModel::IntegerConditionParameter[0..*] :> qualifier_observations { :>> parameter_name = "shunt_adc_range_code"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute sun_distance : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "sun_distance"; :>> unit = CatalogModel::UnitCode::metre; }
        attribute supply_voltage : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "supply_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute temperature_error_magnitude : CatalogModel::ConditionParameterRecord[0..*] :> qualifier_observations { :>> parameter_name = "temperature_error_magnitude"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute qualifier_observations : ConditionParameterRecord[0..*];
        attribute condition_id : String;
        attribute temperature_K : Real[0..1];
        attribute input_voltage_V : Real[0..1];
        attribute output_voltage_V : Real[0..1];
        attribute output_current_A : Real[0..1];
        attribute irradiance_W_m2 : Real[0..1];
        attribute state_of_charge : Real[0..1];
        attribute c_rate : Real[0..1];
        attribute test_frequency_Hz : Real[0..1];
        attribute pulse_duration_s : Real[0..1];
        attribute charge_voltage_V : Real[0..1];
        attribute discharge_cutoff_voltage_V : Real[0..1];
        attribute operating_mode : String[0..1];
        doc /* Original conditions.tsv columns keep their original unit meanings.
         * Additional named qualifiers subset sourced qualifier_observations.
         * operating_mode remains a label. Numeric model inputs require numeric
         * columns or sourced qualifier records, never interpretation of that code.
         * Dimensionless register/selector codes need their documented decoding
         * before becoming engineering quantities. Bounds preserve endpoints.
         * Endpoint inclusion follows the source relation, not an assumed equality.
         * Observed irradiation energy, fluence and flux characterize a source test.
         * They specify no mission lifetime, radiation environment or qualification.
         */
    }
    attribute def CurveRecord {
        attribute product_id : String;
        attribute element_id : String;
        attribute curve_id : String;
        attribute independent_parameter : String;
        attribute independent_value : Real;
        attribute independent_unit : UnitCode;
        attribute dependent_parameter : String;
        attribute dependent_value : Real;
        attribute dependent_unit : UnitCode;
        attribute condition_id : String[0..1];
        attribute source_id : String;
        attribute source_locator : String;
        attribute point_kind : PointKind;
    }
    attribute def SourceRecord {
        attribute source_id : String;
        attribute url : String;
        attribute document_kind : DocumentKind;
        attribute revision : String[0..1];
        attribute sha256 : String[0..1];
        attribute retrieved_utc : String;
    }
    attribute def ResourceRecord {
        attribute product_id : String;
        attribute resource_kind : ResourceKind;
        attribute url : String;
        attribute format : ResourceFormat;
        attribute library_id : String[0..1];
        attribute source_id : String;
        attribute source_locator : String[0..1];
    }
    attribute def ElementRecord {
        attribute product_id : String;
        attribute element_id : String;
        attribute parent_element_id : String;
        attribute element_kind : ElementKind;
    }
    attribute def PinRecord {
        attribute product_id : String;
        attribute element_id : String;
        attribute pin_number : String;
        attribute pin_name : String;
        attribute pin_kind : PinKind;
        attribute direction : PinDirection;
        attribute source_id : String;
        attribute source_locator : String[0..1];
    }
    part def Catalog {
        attribute definitions : DefinitionRecord[0..*];
        attribute products : ProductRecord[0..*];
        attribute parameters : ParameterRecord[0..*];
        attribute features : FeatureRecord[0..*];
        attribute conditions : ConditionRecord[0..*];
        attribute condition_parameters : ConditionParameterRecord[0..*];
        attribute curves : CurveRecord[0..*];
        attribute sources : SourceRecord[0..*];
        attribute resources : ResourceRecord[0..*];
        attribute elements : ElementRecord[0..*];
        attribute pins : PinRecord[0..*];
        assert constraint uniqueProducts {
            products->forAll { in a : ProductRecord; products->forAll { in b : ProductRecord;
                a == b or a.product_id != b.product_id } }
        }
        assert constraint uniqueSources {
            sources->forAll { in a : SourceRecord; sources->forAll { in b : SourceRecord;
                a == b or a.source_id != b.source_id } }
        }
        assert constraint uniqueConditions {
            conditions->forAll { in a : ConditionRecord; conditions->forAll { in b : ConditionRecord;
                a == b or a.condition_id != b.condition_id } }
        }
        assert constraint uniqueElements {
            elements->forAll { in a : ElementRecord; elements->forAll { in b : ElementRecord;
                a == b or a.product_id != b.product_id or a.element_id != b.element_id } }
        }
        assert constraint parameterKeys {
            parameters->forAll { in r : ParameterRecord;
                products->exists { in p : ProductRecord; p.product_id == r.product_id } and
                sources->exists { in s : SourceRecord; s.source_id == r.source_id } and
                r.condition_id->forAll { in c : String; conditions->exists { in v : ConditionRecord; v.condition_id == c } } and
                (r.element_id == "self" or elements->exists { in e : ElementRecord;
                    e.product_id == r.product_id and e.element_id == r.element_id }) }
        }
        assert constraint conditionParameterKeys {
            condition_parameters->forAll { in r : ConditionParameterRecord;
                conditions->exists { in c : ConditionRecord; c.condition_id == r.condition_id } and
                sources->exists { in s : SourceRecord; s.source_id == r.source_id } }
        }
        assert constraint conditionParameterInterpretation {
            condition_parameters->forAll { in r : ConditionParameterRecord;
                definitions->exists { in d : DefinitionRecord;
                    d.definition_kind == DefinitionKind::condition_parameter and
                    d.sysml_owner == "CatalogModel::ConditionRecord" and d.name == r.parameter_name and
                    d.canonical_unit == r.unit and
                    (d.scalar_type == ScalarKind::real_number or
                     (d.scalar_type == ScalarKind::integer_number and r.value istype Integer)) } }
        }
        assert constraint conditionQualifierScope {
            conditions->forAll { in c : ConditionRecord;
                c.qualifier_observations->forAll { in r : ConditionParameterRecord;
                    r.condition_id == c.condition_id and
                    condition_parameters->exists { in declared : ConditionParameterRecord; declared == r } } }
        }
        assert constraint featureKeys {
            features->forAll { in r : FeatureRecord;
                products->exists { in p : ProductRecord; p.product_id == r.product_id } and
                sources->exists { in s : SourceRecord; s.source_id == r.source_id } and
                (r.element_id == "self" or elements->exists { in e : ElementRecord;
                    e.product_id == r.product_id and e.element_id == r.element_id }) }
        }
        assert constraint curveKeys {
            curves->forAll { in r : CurveRecord;
                products->exists { in p : ProductRecord; p.product_id == r.product_id } and
                sources->exists { in s : SourceRecord; s.source_id == r.source_id } and
                r.condition_id->forAll { in c : String; conditions->exists { in v : ConditionRecord; v.condition_id == c } } and
                (r.element_id == "self" or elements->exists { in e : ElementRecord;
                    e.product_id == r.product_id and e.element_id == r.element_id }) }
        }
        assert constraint curveAxisInterpretation {
            curves->forAll { in r : CurveRecord;
                definitions->exists { in d : DefinitionRecord;
                    d.definition_kind == DefinitionKind::curve_axis and
                    d.sysml_owner == "EPSModel::CurvePoint" and d.name == r.independent_parameter and
                    d.canonical_unit == r.independent_unit and
                    (d.scalar_type == ScalarKind::real_number or
                     (d.scalar_type == ScalarKind::integer_number and r.independent_value istype Integer)) } and
                definitions->exists { in d : DefinitionRecord;
                    d.definition_kind == DefinitionKind::curve_axis and
                    d.sysml_owner == "EPSModel::CurvePoint" and d.name == r.dependent_parameter and
                    d.canonical_unit == r.dependent_unit and
                    (d.scalar_type == ScalarKind::real_number or
                     (d.scalar_type == ScalarKind::integer_number and r.dependent_value istype Integer)) } }
        }
        assert constraint resourceKeys {
            resources->forAll { in r : ResourceRecord;
                products->exists { in p : ProductRecord; p.product_id == r.product_id } and
                sources->exists { in s : SourceRecord; s.source_id == r.source_id } }
        }
        assert constraint elementKeys {
            elements->forAll { in r : ElementRecord;
                r.element_id != "self" and r.parent_element_id != r.element_id and
                products->exists { in p : ProductRecord; p.product_id == r.product_id } and
                (r.parent_element_id == "self" or elements->exists { in e : ElementRecord;
                    e.product_id == r.product_id and e.element_id == r.parent_element_id }) }
        }
        assert constraint pinKeys {
            pins->forAll { in r : PinRecord;
                products->exists { in p : ProductRecord; p.product_id == r.product_id } and
                sources->exists { in s : SourceRecord; s.source_id == r.source_id } and
                (r.element_id == "self" or elements->exists { in e : ElementRecord;
                    e.product_id == r.product_id and e.element_id == r.element_id }) }
        }
    }
}
