package EPSModel {
    private import ScalarValues::*;
    private import ControlFunctions::*;
    private import SequenceFunctions::*;
    doc /* Generic EPS and load interfaces for model in the loop verification.
     * No mission, product selection, eclipse fraction or depth of discharge law
     * is supplied. Mechanical, EMC and radiation qualification are outside scope.
     * Optional repeated catalog attributes preserve min/typ/max and conditions.
     * Their exact leaf names are dictionary keys. Each leaf fixes its TSV unit.
     * The scalar representation is a serialization contract, not a proof of
     * dimensional correctness. Importers convert and check units before binding
     * choices to the explicit ISQ quantities in operating point checks.
     * Ah converts to 3600 coulombs and Wh to 3600 joules. AC impedance never
     * supplies DC battery sag resistance. Curves require their stated conditions.
     * Comparator pin references need the documented divider before becoming bus
     * thresholds. Current programming ranges are trip settings, not continuous
     * current ratings. Thermistor ratios/targets depend on the stated NTC circuit.
     * Example external MOSFET identities carry no intrinsic controller rating.
     * operating_temperature_basis retains ambient, case or junction scope.
     * Efficiency losses and already complete supply currents are counted once.
     */
    part def PowerConsumer {
        attribute power_consumption_W : Real[0..1];
        attribute power_consumption : ISQ::PowerValue[0..1] = power_consumption_W * 1[SI::W];
        doc /* Active mode consumption for the installed usage. Per-unit demand
         * remains in the load profiles. Mission usages bind this projection to
         * their draw parameter, which includes installed quantity and accounting.
         * An unbound projection retains unknown consumption.
         */
    }
    part def HardwareComponent :> PowerConsumer {
        attribute interface_smbus : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "interface_smbus"; }
        attribute diameter : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "diameter"; :>> unit = CatalogModel::UnitCode::metre; }
        attribute solar_absorptance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "solar_absorptance"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute thermal_emittance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "thermal_emittance"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute physical_resource_id : String[0..1];
        attribute catalog_product_id : String[0..1];
        attribute catalog_element_id : String[0..1];
        attribute parameter_observations : CatalogModel::ParameterRecord[0..*];
        attribute feature_observations : CatalogModel::FeatureEvidence[0..*];
        attribute design_choices : DesignParameterChoice[0..*];
        attribute model_availability : ModelAvailability[0..*];
        assert constraint observationProductScope {
            catalog_product_id->forAll { in product : String;
                parameter_observations->forAll { in observation : CatalogModel::ParameterRecord;
                    observation.product_id == product } and
                feature_observations->forAll { in observation : CatalogModel::FeatureEvidence;
                    observation.product_id == product } }
        }
        assert constraint observationElementScope {
            catalog_element_id->forAll { in element : String;
                parameter_observations->forAll { in observation : CatalogModel::ParameterRecord;
                    observation.element_id == element } and
                feature_observations->forAll { in observation : CatalogModel::FeatureEvidence;
                    observation.element_id == element } }
        }
        doc /* Exact dictionary leaves subset the evidence collections. When a
         * catalog product/element is bound, every observation belongs to it.
         * Bind the root as self. Generic unselected component types remain open.
         */
        attribute mass : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "mass";
            :>> unit = CatalogModel::UnitCode::kilogram;
        }
        attribute length : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "length";
            :>> unit = CatalogModel::UnitCode::metre;
        }
        attribute width : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "width";
            :>> unit = CatalogModel::UnitCode::metre;
        }
        attribute height : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "height";
            :>> unit = CatalogModel::UnitCode::metre;
        }
        attribute operating_temperature_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "operating_temperature_min";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute operating_temperature_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "operating_temperature_max";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute storage_temperature_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "storage_temperature_min";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute storage_temperature_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "storage_temperature_max";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute maximum_junction_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "maximum_junction_temperature";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute thermal_resistance_junction_ambient : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "thermal_resistance_junction_ambient";
            :>> unit = CatalogModel::UnitCode::kelvin_per_watt;
        }
        attribute thermal_resistance_junction_case : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "thermal_resistance_junction_case";
            :>> unit = CatalogModel::UnitCode::kelvin_per_watt;
        }
        attribute supply_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "supply_voltage_min";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute supply_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "supply_voltage_max";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute supply_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "supply_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute standby_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "standby_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute shutdown_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "shutdown_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute quiescent_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "quiescent_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute interface_frequency_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "interface_frequency_max";
            :>> unit = CatalogModel::UnitCode::hertz;
        }
        attribute technology : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "technology"; }
        attribute package_id : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "package_id"; }
        attribute interface_i2c : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "interface_i2c"; }
        attribute interface_spi : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "interface_spi"; }
        attribute interface_uart : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "interface_uart"; }
        attribute interface_can : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "interface_can"; }
        attribute interface_analog : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "interface_analog"; }
        attribute external_passives_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_passives_required"; }
        attribute external_mosfet_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_mosfet_required"; }
        attribute pin_map_complete : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "pin_map_complete"; }
    }
    part def ElectricalElement :> HardwareComponent {
        attribute above_mppt_range_behavior : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "above_mppt_range_behavior"; }
        attribute battery_balancing : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "battery_balancing"; }
        attribute battery_heater_included : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "battery_heater_included"; }
        attribute battery_protection_responsibility : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "battery_protection_responsibility"; }
        attribute battery_required_for_generation : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "battery_required_for_generation"; }
        attribute channel_count_scope : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "channel_count_scope"; }
        attribute configurable_input_current : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "configurable_input_current"; }
        attribute configurable_retry : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "configurable_retry"; }
        attribute configuration_id : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "configuration_id"; }
        attribute control_protocol : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "control_protocol"; }
        attribute disable_dependency : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "disable_dependency"; }
        attribute efficiency_data_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "efficiency_data_kind"; }
        attribute efficiency_loss_scope : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "efficiency_loss_scope"; }
        attribute factory_configurable_voltage : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "factory_configurable_voltage"; }
        attribute inhibit_interface : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "inhibit_interface"; }
        attribute interface_spi_option : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "interface_spi_option"; }
        attribute mppt_algorithm : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "mppt_algorithm"; }
        attribute mppt_autonomous : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "mppt_autonomous"; }
        attribute mppt_controller : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "mppt_controller"; }
        attribute mppt_independent_of_mcu : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "mppt_independent_of_mcu"; }
        attribute mppt_operating_modes : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "mppt_operating_modes"; }
        attribute output_control : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "output_control"; }
        attribute output_source_options : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "output_source_options"; }
        attribute output_voltage_choices : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "output_voltage_choices"; }
        attribute overcurrent_event_logging : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "overcurrent_event_logging"; }
        attribute overcurrent_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "overcurrent_protection"; }
        attribute overcurrent_response : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "overcurrent_response"; }
        attribute overvoltage_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "overvoltage_protection"; }
        attribute power_control_independent_of_mcu : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "power_control_independent_of_mcu"; }
        attribute power_stage_topology : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "power_stage_topology"; }
        attribute protection_controller : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "protection_controller"; }
        attribute recommended_current_bound_exclusive : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "recommended_current_bound_exclusive"; }
        attribute shared_current_budget_group : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "shared_current_budget_group"; }
        attribute soft_start : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "soft_start"; }
        attribute solar_voltage_constraint : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "solar_voltage_constraint"; }
        attribute supported_battery_chemistry : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "supported_battery_chemistry"; }
        attribute temperature_rating_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "temperature_rating_basis"; }
        attribute thermal_protection_action : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "thermal_protection_action"; }
        attribute undervoltage_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "undervoltage_protection"; }
        attribute voltage_regulation : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "voltage_regulation"; }
        attribute watchdog_action : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "watchdog_action"; }
        attribute watchdog_disable_supported : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "watchdog_disable_supported"; }
        attribute battery_capacity : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "battery_capacity"; :>> unit = CatalogModel::UnitCode::ampere_hour; }
        attribute battery_energy : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "battery_energy"; :>> unit = CatalogModel::UnitCode::watt_hour; }
        attribute cell_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "cell_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute cell_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "cell_voltage_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charge_undervoltage_recovery : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_undervoltage_recovery"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charge_undervoltage_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_undervoltage_threshold"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charge_voltage_setpoint : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_voltage_setpoint"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute discharge_current_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_current_max"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute fallback_input_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "fallback_input_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute hardware_current_limit : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "hardware_current_limit"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute heater_power_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "heater_power_max"; :>> unit = CatalogModel::UnitCode::watt; }
        attribute maximum_input_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "maximum_input_power"; :>> unit = CatalogModel::UnitCode::watt; }
        attribute mppt_search_start_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "mppt_search_start_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute mppt_update_frequency : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "mppt_update_frequency"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute overvoltage_recovery_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "overvoltage_recovery_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute protection_latch_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "protection_latch_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute recommended_current_upper_bound : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "recommended_current_upper_bound"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute reset_pulse_duration_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reset_pulse_duration_max"; :>> unit = CatalogModel::UnitCode::second; }
        attribute reset_pulse_duration_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reset_pulse_duration_min"; :>> unit = CatalogModel::UnitCode::second; }
        attribute standby_current_per_cell : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "standby_current_per_cell"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute telemetry_update_frequency : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "telemetry_update_frequency"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute thermal_recovery_hysteresis : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "thermal_recovery_hysteresis"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute trickle_charge_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "trickle_charge_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute undervoltage_recovery_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "undervoltage_recovery_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute watchdog_timeout_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "watchdog_timeout_max"; :>> unit = CatalogModel::UnitCode::second; }
        attribute load_profiles : ModeLoadProfile[0..*];
        attribute accounting : AccountingEntry[0..1];
        ref part runtime : ElectricalRuntime[0..1];
        attribute efficiency : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "efficiency";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute series_cell_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "series_cell_count";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute parallel_string_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "parallel_string_count";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute nominal_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "nominal_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute charge_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute charge_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute charge_current_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_current_max";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute input_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "input_voltage_min";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute input_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "input_voltage_max";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute output_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "output_voltage_min";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute output_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "output_voltage_max";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute fixed_output_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "fixed_output_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute maximum_output_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "maximum_output_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute maximum_output_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "maximum_output_power";
            :>> unit = CatalogModel::UnitCode::watt;
        }
        attribute maximum_input_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "maximum_input_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute startup_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "startup_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute current_limit : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "current_limit";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute overvoltage_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "overvoltage_threshold";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute operating_temperature_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "operating_temperature_basis"; }
        attribute undervoltage_release : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "undervoltage_release";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute undervoltage_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "undervoltage_threshold";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute undervoltage_hysteresis : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "undervoltage_hysteresis";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute reverse_current_blocking : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "reverse_current_blocking"; }
        attribute autonomous_overcurrent_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_overcurrent_protection"; }
        attribute autonomous_overvoltage_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_overvoltage_protection"; }
        attribute autonomous_undervoltage_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_undervoltage_protection"; }
        attribute autonomous_thermal_shutdown : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_thermal_shutdown"; }
        attribute enable_input : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "enable_input"; }
        attribute active_low_enable : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "active_low_enable"; }
    }
    part def SolarArray :> ElectricalElement {
        attribute cell_polarity : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "cell_polarity"; }
        attribute external_bypass_diode_compatible : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_bypass_diode_compatible"; }
        attribute geometry_configurable : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "geometry_configurable"; }
        attribute iv_curve_current_sign_convention : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "iv_curve_current_sign_convention"; }
        attribute areal_mass : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "areal_mass"; :>> unit = CatalogModel::UnitCode::kilogram_per_square_metre; }
        attribute current_at_maximum_power_remaining_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_at_maximum_power_remaining_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute current_at_maximum_power_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_at_maximum_power_temperature_coefficient"; :>> unit = CatalogModel::UnitCode::ampere_per_kelvin; }
        attribute current_density_at_maximum_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_density_at_maximum_power"; :>> unit = CatalogModel::UnitCode::ampere_per_square_metre; }
        attribute maximum_power_density : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "maximum_power_density"; :>> unit = CatalogModel::UnitCode::watt_per_square_metre; }
        attribute open_circuit_voltage_remaining_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "open_circuit_voltage_remaining_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute open_circuit_voltage_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "open_circuit_voltage_temperature_coefficient"; :>> unit = CatalogModel::UnitCode::volt_per_kelvin; }
        attribute relative_current_at_maximum_power_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "relative_current_at_maximum_power_temperature_coefficient"; :>> unit = CatalogModel::UnitCode::per_kelvin; }
        attribute relative_short_circuit_current_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "relative_short_circuit_current_temperature_coefficient"; :>> unit = CatalogModel::UnitCode::per_kelvin; }
        attribute short_circuit_current_density : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_current_density"; :>> unit = CatalogModel::UnitCode::ampere_per_square_metre; }
        attribute short_circuit_current_remaining_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_current_remaining_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute short_circuit_current_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_current_temperature_coefficient"; :>> unit = CatalogModel::UnitCode::ampere_per_kelvin; }
        attribute temperature_coefficient_temperature_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "temperature_coefficient_temperature_max"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute temperature_coefficient_temperature_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "temperature_coefficient_temperature_min"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute voltage_at_maximum_power_remaining_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "voltage_at_maximum_power_remaining_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute voltage_at_maximum_power_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "voltage_at_maximum_power_temperature_coefficient"; :>> unit = CatalogModel::UnitCode::volt_per_kelvin; }
        attribute curve_points : CurvePoint[0..*];
        attribute active_area : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "active_area";
            :>> unit = CatalogModel::UnitCode::square_metre;
        }
        attribute maximum_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "maximum_power";
            :>> unit = CatalogModel::UnitCode::watt;
        }
        attribute voltage_at_maximum_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "voltage_at_maximum_power";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute current_at_maximum_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "current_at_maximum_power";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute open_circuit_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "open_circuit_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute short_circuit_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "short_circuit_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute voltage_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "voltage_temperature_coefficient";
            :>> unit = CatalogModel::UnitCode::volt_per_kelvin;
        }
        attribute current_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "current_temperature_coefficient";
            :>> unit = CatalogModel::UnitCode::ampere_per_kelvin;
        }
        attribute power_temperature_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "power_temperature_coefficient";
            :>> unit = CatalogModel::UnitCode::per_kelvin;
        }
        attribute reference_irradiance : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "reference_irradiance";
            :>> unit = CatalogModel::UnitCode::watt_per_square_metre;
        }
        attribute end_of_life_power_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "end_of_life_power_fraction";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute bypass_diode : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "bypass_diode"; }
        attribute deployable : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "deployable"; }
    }
    part def Battery :> ElectricalElement {
        attribute cutoff_implementation : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "cutoff_implementation"; }
        attribute external_protection_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_protection_required"; }
        attribute heater_control_automatic_available : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "heater_control_automatic_available"; }
        attribute heater_control_default : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "heater_control_default"; }
        attribute heater_included : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "heater_included"; }
        attribute characterization_charge_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "characterization_charge_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute characterization_charge_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "characterization_charge_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute characterization_post_discharge_rest_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "characterization_post_discharge_rest_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute charge_temperature_cutoff : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_temperature_cutoff"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute charge_termination_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_termination_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute dcir_baseline_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "dcir_baseline_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute dcir_baseline_duration : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "dcir_baseline_duration"; :>> unit = CatalogModel::UnitCode::second; }
        attribute discharge_temperature_cutoff : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_temperature_cutoff"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute heater_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "heater_power"; :>> unit = CatalogModel::UnitCode::watt; }
        attribute heater_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "heater_resistance"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute self_discharge_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "self_discharge_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        ref part battery_runtime : BatteryRuntime[0..1];
        attribute curve_points : CurvePoint[0..*];
        attribute rated_capacity : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "rated_capacity";
            :>> unit = CatalogModel::UnitCode::ampere_hour;
        }
        attribute rated_energy : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "rated_energy";
            :>> unit = CatalogModel::UnitCode::watt_hour;
        }
        attribute discharge_current_continuous : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "discharge_current_continuous";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute discharge_current_pulse : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "discharge_current_pulse";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute discharge_cutoff_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "discharge_cutoff_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute dc_internal_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "dc_internal_resistance";
            :>> unit = CatalogModel::UnitCode::ohm;
        }
        attribute ac_impedance : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "ac_impedance";
            :>> unit = CatalogModel::UnitCode::ohm;
        }
        attribute charge_temperature_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_temperature_min";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute charge_temperature_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_temperature_max";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute discharge_temperature_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "discharge_temperature_min";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute discharge_temperature_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "discharge_temperature_max";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute cycle_life : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "cycle_life";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute cycle_life_retained_capacity : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "cycle_life_retained_capacity";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute chemistry : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "chemistry"; }
        attribute balancing_included : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "balancing_included"; }
        attribute protection_included : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "protection_included"; }
    }
    part def RegulatorConverter :> ElectricalElement {
        attribute charge_current_programming : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "charge_current_programming"; }
        attribute charge_temperature_inhibit_responsibility : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "charge_temperature_inhibit_responsibility"; }
        attribute charge_termination_configurable : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "charge_termination_configurable"; }
        attribute control_interface : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "control_interface"; }
        attribute current_limit_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "current_limit_basis"; }
        attribute forced_pwm_selectable : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "forced_pwm_selectable"; }
        attribute light_load_mode : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "light_load_mode"; }
        attribute mppt_enable_responsibility : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "mppt_enable_responsibility"; }
        attribute mppt_enabled_at_reset : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "mppt_enabled_at_reset"; }
        attribute optional_external_mosfet_roles : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "optional_external_mosfet_roles"; }
        attribute output_capability_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "output_capability_basis"; }
        attribute output_voltage_programming : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "output_voltage_programming"; }
        attribute short_circuit_response : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "short_circuit_response"; }
        attribute simulation_model_encrypted : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "simulation_model_encrypted"; }
        attribute solar_control_method : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "solar_control_method"; }
        attribute supported_chemistry : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "supported_chemistry"; }
        attribute switching_control : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "switching_control"; }
        attribute temperature_monitor_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "temperature_monitor_kind"; }
        attribute charge_current_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_current_min"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute charge_current_programming_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_current_programming_coefficient"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charge_current_programming_gain : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_current_programming_gain"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute charge_current_programming_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_current_programming_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charge_current_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_current_sense_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charge_current_step : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_current_step"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute charge_enable_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_enable_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute charge_inhibit_cold_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_inhibit_cold_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute charge_inhibit_hot_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_inhibit_hot_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute charge_safety_timeout : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_safety_timeout"; :>> unit = CatalogModel::UnitCode::second; }
        attribute charge_sense_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_sense_resistance"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute charge_termination_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_termination_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute charge_voltage_accuracy : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_voltage_accuracy"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute charge_voltage_step : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_voltage_step"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute current_limit_valley : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_limit_valley"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute effective_output_capacitance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "effective_output_capacitance"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute enable_threshold_falling : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "enable_threshold_falling"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute enable_threshold_rising : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "enable_threshold_rising"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute feedback_voltage_reference : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "feedback_voltage_reference"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute input_current_programming_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "input_current_programming_coefficient"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute input_voltage_regulation_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "input_voltage_regulation_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute input_voltage_regulation_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "input_voltage_regulation_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute input_voltage_regulation_reference : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "input_voltage_regulation_reference"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute input_voltage_regulation_setpoint : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "input_voltage_regulation_setpoint"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute mppt_sample_interval : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "mppt_sample_interval"; :>> unit = CatalogModel::UnitCode::second; }
        attribute mppt_sample_settling_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "mppt_sample_settling_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute precharge_current_floor : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_current_floor"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute precharge_current_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_current_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute precharge_current_programming_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_current_programming_coefficient"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute precharge_current_programming_gain : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_current_programming_gain"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute precharge_current_programming_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_current_programming_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute precharge_current_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_current_sense_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute precharge_current_step : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_current_step"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute precharge_feedback_voltage_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_feedback_voltage_threshold"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute precharge_safety_timeout : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_safety_timeout"; :>> unit = CatalogModel::UnitCode::second; }
        attribute precharge_to_fast_voltage_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_to_fast_voltage_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute precharge_voltage_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "precharge_voltage_threshold"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute recharge_feedback_voltage_hysteresis : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "recharge_feedback_voltage_hysteresis"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute short_circuit_current_limit : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_current_limit"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute soft_start_charge_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "soft_start_charge_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute soft_start_current_ramp_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "soft_start_current_ramp_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute soft_start_voltage_reference : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "soft_start_voltage_reference"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute startup_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "startup_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute startup_input_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "startup_input_voltage_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute termination_current_floor : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "termination_current_floor"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute termination_current_fraction : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "termination_current_fraction"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute termination_current_programming_coefficient : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "termination_current_programming_coefficient"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute termination_current_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "termination_current_sense_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute termination_current_step : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "termination_current_step"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute switching_frequency : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "switching_frequency";
            :>> unit = CatalogModel::UnitCode::hertz;
        }
        attribute output_voltage_accuracy : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "output_voltage_accuracy";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute output_ripple : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "output_ripple";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute dropout_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "dropout_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute mppt_voltage_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "mppt_voltage_ratio";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute mppt_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "mppt_voltage_min";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute mppt_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "mppt_voltage_max";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute cell_count_min : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "cell_count_min";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute cell_count_max : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "cell_count_max";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute charge_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_voltage_min";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute charge_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_voltage_max";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute termination_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "termination_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute precharge_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "precharge_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute recharge_hysteresis : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "recharge_hysteresis";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute regulation_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "regulation_kind"; }
        attribute power_conditioning : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "power_conditioning"; }
        attribute autonomous_mppt : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_mppt"; }
        attribute input_voltage_regulation : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "input_voltage_regulation"; }
        attribute charge_cc_cv : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "charge_cc_cv"; }
        attribute charge_temperature_inhibit : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "charge_temperature_inhibit"; }
        attribute configurable_output_voltage : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "configurable_output_voltage"; }
        attribute configurable_charge_current : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "configurable_charge_current"; }
    }
    part def DCDCConverter :> RegulatorConverter {
    }
    part def BatteryCharger :> RegulatorConverter {
    }
    part def PowerCircuitSwitch :> ElectricalElement {
        doc /* Charge pump turn-off voltage is the VCAP minus ANODE comparator
         * threshold. It is distinct from the GATE minus ANODE drive voltage.
         */
        attribute charge_pump_turn_off_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "charge_pump_turn_off_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute autonomous_cell_balancing : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_cell_balancing"; }
        attribute autonomous_charge_overcurrent_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_charge_overcurrent_protection"; }
        attribute autonomous_discharge_overcurrent_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_discharge_overcurrent_protection"; }
        attribute autonomous_temperature_protection : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "autonomous_temperature_protection"; }
        attribute charge_overcurrent_recovery_policy : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "charge_overcurrent_recovery_policy"; }
        attribute control_input_bias : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "control_input_bias"; }
        attribute control_input_semantics : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "control_input_semantics"; }
        attribute current_limit_programming_model : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "current_limit_programming_model"; }
        attribute current_path_direction : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "current_path_direction"; }
        attribute current_rating_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "current_rating_basis"; }
        attribute current_sense_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "current_sense_basis"; }
        attribute current_sense_polarity : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "current_sense_polarity"; }
        attribute external_mosfet_for_reverse_blocking_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_mosfet_for_reverse_blocking_required"; }
        attribute external_mosfet_location : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "external_mosfet_location"; }
        attribute external_mosfet_topology : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "external_mosfet_topology"; }
        attribute external_mosfet_type : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "external_mosfet_type"; }
        attribute external_thermistor_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_thermistor_required"; }
        attribute external_thermistor_type : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "external_thermistor_type"; }
        attribute inrush_control_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "inrush_control_kind"; }
        attribute lifecycle_status : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "lifecycle_status"; }
        attribute mcu_off_configuration : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "mcu_off_configuration"; }
        attribute on_resistance_scope : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "on_resistance_scope"; }
        attribute overcurrent_action : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "overcurrent_action"; }
        attribute overcurrent_delay_programming : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "overcurrent_delay_programming"; }
        attribute overcurrent_recovery_policy : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "overcurrent_recovery_policy"; }
        attribute overvoltage_action : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "overvoltage_action"; }
        attribute overvoltage_recovery_policy : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "overvoltage_recovery_policy"; }
        attribute protection_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "protection_kind"; }
        attribute protection_requires_mcu : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "protection_requires_mcu"; }
        attribute reference_external_mosfet_part_number : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "reference_external_mosfet_part_number"; }
        attribute retry_policy : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "retry_policy"; }
        attribute reverse_blocking_configuration : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "reverse_blocking_configuration"; }
        attribute reverse_blocking_disabled_in_devsleep : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "reverse_blocking_disabled_in_devsleep"; }
        attribute shutdown_blocks_forward_current : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "shutdown_blocks_forward_current"; }
        attribute startup_policy : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "startup_policy"; }
        attribute supply_current_accounting : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "supply_current_accounting"; }
        attribute supports_back_to_back_mosfets : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "supports_back_to_back_mosfets"; }
        attribute threshold_configuration : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "threshold_configuration"; }
        attribute undervoltage_action : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "undervoltage_action"; }
        attribute undervoltage_recovery_policy : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "undervoltage_recovery_policy"; }
        attribute voltage_threshold_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "voltage_threshold_basis"; }
        attribute zero_voltage_charging : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "zero_voltage_charging"; }
        attribute charge_overcurrent_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_overcurrent_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute charge_overcurrent_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_overcurrent_sense_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charge_overtemperature_release_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_overtemperature_release_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute charge_overtemperature_target_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_overtemperature_target_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute charge_overtemperature_threshold_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_overtemperature_threshold_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute charge_pump_capacitance_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_pump_capacitance_min"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute charge_undertemperature_release_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_undertemperature_release_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute charge_undertemperature_target_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_undertemperature_target_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute charge_undertemperature_threshold_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charge_undertemperature_threshold_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute charger_overvoltage_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charger_overvoltage_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute charger_overvoltage_release : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charger_overvoltage_release"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute charger_overvoltage_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "charger_overvoltage_threshold"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute current_fault_recovery_holdoff : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_fault_recovery_holdoff"; :>> unit = CatalogModel::UnitCode::second; }
        attribute current_limit_programming_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_limit_programming_resistance"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute current_limit_programming_resistance_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_limit_programming_resistance_max"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute current_limit_programming_resistance_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_limit_programming_resistance_min"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute current_limit_thermal_shutdown_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_limit_thermal_shutdown_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute current_limit_timeout : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_limit_timeout"; :>> unit = CatalogModel::UnitCode::second; }
        attribute discharge_overtemperature_release_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_overtemperature_release_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute discharge_overtemperature_target_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_overtemperature_target_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute discharge_overtemperature_threshold_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_overtemperature_threshold_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute discharge_undertemperature_release_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_undertemperature_release_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute discharge_undertemperature_target_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_undertemperature_target_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute discharge_undertemperature_threshold_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "discharge_undertemperature_threshold_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute enable_falling_threshold_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "enable_falling_threshold_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute enable_high_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "enable_high_voltage_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute enable_low_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "enable_low_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute enable_rising_threshold_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "enable_rising_threshold_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute enable_threshold_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "enable_threshold_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute external_mosfet_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "external_mosfet_count"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute external_mosfet_count_min : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "external_mosfet_count_min"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute external_mosfet_vgs_rating_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "external_mosfet_vgs_rating_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute fault_recovery_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "fault_recovery_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute fault_timer_discharge_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "fault_timer_discharge_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute fault_timer_voltage_excursion : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "fault_timer_voltage_excursion"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute forward_recovery_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "forward_recovery_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute gate_drive_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "gate_drive_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute gate_driver_gain : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "gate_driver_gain"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute gate_driver_off_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "gate_driver_off_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute gate_pull_down_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "gate_pull_down_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute gate_pull_up_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "gate_pull_up_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute normal_input_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "normal_input_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute open_wire_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "open_wire_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute open_wire_hysteresis : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "open_wire_hysteresis"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute open_wire_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "open_wire_threshold"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute output_clamp_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "output_clamp_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute output_ramp_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "output_ramp_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute output_rise_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "output_rise_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute ov_comparator_falling_reference_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "ov_comparator_falling_reference_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute ov_comparator_hysteresis_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "ov_comparator_hysteresis_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute ov_comparator_rising_reference_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "ov_comparator_rising_reference_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute override_disable_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "override_disable_voltage_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute override_enable_low_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "override_enable_low_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute overvoltage_hysteresis : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "overvoltage_hysteresis"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute overvoltage_recovery_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "overvoltage_recovery_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute overvoltage_recovery_holdoff : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "overvoltage_recovery_holdoff"; :>> unit = CatalogModel::UnitCode::second; }
        attribute programmable_current_limit_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "programmable_current_limit_max"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute programmable_current_limit_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "programmable_current_limit_min"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute programmable_overvoltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "programmable_overvoltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute retry_count_min : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "retry_count_min"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute retry_programming_reference_capacitance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "retry_programming_reference_capacitance"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute retry_programming_reference_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "retry_programming_reference_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute retry_timer_bias_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "retry_timer_bias_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute retry_timer_capacitance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "retry_timer_capacitance"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute retry_timer_cycle_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "retry_timer_cycle_count"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute retry_timer_hysteresis_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "retry_timer_hysteresis_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute retry_timer_parasitic_capacitance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "retry_timer_parasitic_capacitance"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute reverse_blocking_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reverse_blocking_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute reverse_blocking_hysteresis_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reverse_blocking_hysteresis_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute reverse_blocking_release_output_above_input_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reverse_blocking_release_output_above_input_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute reverse_blocking_release_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reverse_blocking_release_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute reverse_blocking_trip_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reverse_blocking_trip_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute reverse_current_activation_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reverse_current_activation_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute reverse_overcurrent_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "reverse_overcurrent_sense_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute secondary_overcurrent_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "secondary_overcurrent_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute secondary_overcurrent_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "secondary_overcurrent_sense_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute sense_resistance_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "sense_resistance_min"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute short_circuit_current_limit_offset : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_current_limit_offset"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute short_circuit_current_limit_ratio : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_current_limit_ratio"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute short_circuit_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute short_circuit_detection_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_detection_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute short_circuit_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "short_circuit_sense_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute slew_control_capacitance_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "slew_control_capacitance_max"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute slew_control_capacitance_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "slew_control_capacitance_min"; :>> unit = CatalogModel::UnitCode::farad; }
        attribute slew_control_charging_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "slew_control_charging_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute slew_control_voltage_gain : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "slew_control_voltage_gain"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute soft_start_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "soft_start_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute supported_series_cell_count_max : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "supported_series_cell_count_max"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute supported_series_cell_count_min : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "supported_series_cell_count_min"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute switchover_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "switchover_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute temperature_fault_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "temperature_fault_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute thermal_shutdown_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "thermal_shutdown_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute thermal_shutdown_hysteresis : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "thermal_shutdown_hysteresis"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute thermal_shutdown_release_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "thermal_shutdown_release_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute thermal_shutdown_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "thermal_shutdown_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute undervoltage_recovery_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "undervoltage_recovery_delay"; :>> unit = CatalogModel::UnitCode::second; }
        attribute uv_comparator_falling_reference_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "uv_comparator_falling_reference_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute uv_comparator_hysteresis_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "uv_comparator_hysteresis_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute uv_comparator_rising_reference_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "uv_comparator_rising_reference_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        ref part switch_runtime : SwitchControlCheck[0..1];
        attribute on_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "on_resistance";
            :>> unit = CatalogModel::UnitCode::ohm;
        }
        attribute sense_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "sense_resistance";
            :>> unit = CatalogModel::UnitCode::ohm;
        }
        attribute overcurrent_threshold : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "overcurrent_threshold";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute overcurrent_sense_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "overcurrent_sense_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute overcurrent_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "overcurrent_delay";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute overvoltage_release : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "overvoltage_release";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute overvoltage_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "overvoltage_delay";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute undervoltage_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "undervoltage_delay";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute retry_delay : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "retry_delay";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute turn_on_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "turn_on_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute turn_off_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "turn_off_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute reverse_blocking_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "reverse_blocking_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute forward_regulation_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "forward_regulation_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute auto_retry : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "auto_retry"; }
        attribute latching_fault : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "latching_fault"; }
        attribute default_enabled : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "default_enabled"; }
        attribute configurable_thresholds : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "configurable_thresholds"; }
    }
    part def LoadSwitch :> PowerCircuitSwitch {
    }
    part def BatteryProtector :> PowerCircuitSwitch {
    }
    part def IdealDiode :> PowerCircuitSwitch {
    }
    part def ProcessorMemory :> ElectricalElement {
        attribute clock_frequency_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "clock_frequency_max";
            :>> unit = CatalogModel::UnitCode::hertz;
        }
        attribute program_memory_bytes : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "program_memory_bytes";
            :>> unit = CatalogModel::UnitCode::byte;
        }
        attribute ram_bytes : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "ram_bytes";
            :>> unit = CatalogModel::UnitCode::byte;
        }
    }
    part def Processor :> ProcessorMemory {
        attribute program_memory_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "program_memory_kind"; }
        attribute flash_memory_bytes : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "flash_memory_bytes"; :>> unit = CatalogModel::UnitCode::byte; }
        attribute information_memory_bytes : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "information_memory_bytes"; :>> unit = CatalogModel::UnitCode::byte; }
        attribute cpu_architecture : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "cpu_architecture"; }
    }
    part def NonvolatileMemory :> ProcessorMemory {
        attribute endurance_scope : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "endurance_scope"; }
        attribute erase_required_before_program : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "erase_required_before_program"; }
        attribute read_access_time_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "read_access_time_basis"; }
        attribute unlimited_write_endurance : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "unlimited_write_endurance"; }
        attribute write_busy_cycle_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "write_busy_cycle_required"; }
        attribute active_read_write_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "active_read_write_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute erase_chip_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "erase_chip_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute erase_sector_bytes : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "erase_sector_bytes"; :>> unit = CatalogModel::UnitCode::byte; }
        attribute erase_sector_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "erase_sector_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute write_page_bytes : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "write_page_bytes"; :>> unit = CatalogModel::UnitCode::byte; }
        attribute capacity_bits : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "capacity_bits";
            :>> unit = CatalogModel::UnitCode::bit;
        }
        attribute read_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "read_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute write_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "write_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute write_cycle_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "write_cycle_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute read_access_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "read_access_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute write_endurance : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "write_endurance";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute data_retention_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "data_retention_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute memory_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "memory_kind"; }
    }
    part def RealTimeClock :> ElectricalElement {
        attribute accuracy_basis : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "accuracy_basis"; }
        attribute backup_interface_available : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "backup_interface_available"; }
        attribute backup_requires_main_supply_pulse : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "backup_requires_main_supply_pulse"; }
        attribute backup_retains_ram : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "backup_retains_ram"; }
        attribute backup_retains_time : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "backup_retains_time"; }
        attribute backup_voltage_max_tracks_supply : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "backup_voltage_max_tracks_supply"; }
        attribute battery_trickle_charger : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "battery_trickle_charger"; }
        attribute clock_source_kind : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "clock_source_kind"; }
        attribute accuracy_temperature_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "accuracy_temperature_max"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute accuracy_temperature_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "accuracy_temperature_min"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute backup_initialization_pulse_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "backup_initialization_pulse_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute backup_switchover_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "backup_switchover_voltage_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute retained_ram_bytes : CatalogModel::IntegerParameter[0..*] :> parameter_observations { :>> parameter_name = "retained_ram_bytes"; :>> unit = CatalogModel::UnitCode::byte; }
        attribute timekeeping_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "timekeeping_current"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute uncorrected_crystal_relative_frequency_error : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "uncorrected_crystal_relative_frequency_error"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        ref part retained_clock : ClockStep[0..1];
        attribute backup_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "backup_voltage_min";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute backup_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "backup_voltage_max";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute backup_current : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "backup_current";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute oscillator_frequency : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "oscillator_frequency";
            :>> unit = CatalogModel::UnitCode::hertz;
        }
        attribute relative_frequency_error : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "relative_frequency_error";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute oscillator_startup_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "oscillator_startup_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute external_crystal_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_crystal_required"; }
        attribute integrated_oscillator : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "integrated_oscillator"; }
        attribute temperature_compensated : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "temperature_compensated"; }
        attribute battery_backup : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "battery_backup"; }
    }
    part def Sensor :> ElectricalElement {
        attribute alert_behavior : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "alert_behavior"; }
        attribute alert_output : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "alert_output"; }
        attribute analog_bandwidth : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "analog_bandwidth"; :>> unit = CatalogModel::UnitCode::hertz; }
        attribute relative_sample_rate_error : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "relative_sample_rate_error"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute response_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "response_time"; :>> unit = CatalogModel::UnitCode::second; }
        attribute conversion_time : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "conversion_time";
            :>> unit = CatalogModel::UnitCode::second;
        }
        attribute sample_rate : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "sample_rate";
            :>> unit = CatalogModel::UnitCode::hertz;
        }
        attribute resolution_bits : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "resolution_bits";
            :>> unit = CatalogModel::UnitCode::bit;
        }
        attribute digital_output : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "digital_output"; }
    }
    part def CurrentSensor :> Sensor {
        attribute calibration_formula : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "calibration_formula"; }
        attribute current_scale_programmable : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "current_scale_programmable"; }
        attribute external_shunt_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_shunt_required"; }
        attribute integrated_shunt : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "integrated_shunt"; }
        attribute output_reference_mode : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "output_reference_mode"; }
        attribute bus_voltage_resolution : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "bus_voltage_resolution"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute calibration_range_multiplier : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "calibration_range_multiplier"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute common_mode_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "common_mode_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute common_mode_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "common_mode_voltage_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute current_calibration_constant_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_calibration_constant_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute current_measurement_error : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_measurement_error"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute current_offset : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_offset"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute current_resolution : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "current_resolution"; :>> unit = CatalogModel::UnitCode::ampere; }
        attribute external_shunt_resistance_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "external_shunt_resistance_max"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute input_offset_drift : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "input_offset_drift"; :>> unit = CatalogModel::UnitCode::volt_per_kelvin; }
        attribute relative_gain_drift : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "relative_gain_drift"; :>> unit = CatalogModel::UnitCode::per_kelvin; }
        attribute series_path_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "series_path_resistance"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute shunt_resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "shunt_resistance"; :>> unit = CatalogModel::UnitCode::ohm; }
        attribute shunt_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "shunt_voltage_max"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute shunt_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "shunt_voltage_min"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute shunt_voltage_resolution : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "shunt_voltage_resolution"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute voltage_gain : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "voltage_gain"; :>> unit = CatalogModel::UnitCode::dimensionless; }
        attribute current_range_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "current_range_min";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute current_range_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "current_range_max";
            :>> unit = CatalogModel::UnitCode::ampere;
        }
        attribute bus_voltage_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "bus_voltage_min";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute bus_voltage_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "bus_voltage_max";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute shunt_voltage_range : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "shunt_voltage_range";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute input_offset_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "input_offset_voltage";
            :>> unit = CatalogModel::UnitCode::volt;
        }
        attribute gain_error : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "gain_error";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute current_sensitivity : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "current_sensitivity";
            :>> unit = CatalogModel::UnitCode::volt_per_ampere;
        }
        attribute bidirectional_measurement : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "bidirectional_measurement"; }
    }
    part def TemperatureSensor :> Sensor {
        attribute negative_output_bias_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "negative_output_bias_required"; }
        attribute temperature_transfer_model : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "temperature_transfer_model"; }
        attribute output_reference_temperature : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "output_reference_temperature"; :>> unit = CatalogModel::UnitCode::kelvin; }
        attribute output_reference_voltage : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "output_reference_voltage"; :>> unit = CatalogModel::UnitCode::volt; }
        attribute temperature_sensitivity : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "temperature_sensitivity"; :>> unit = CatalogModel::UnitCode::volt_per_kelvin; }
        attribute thermal_time_constant : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "thermal_time_constant"; :>> unit = CatalogModel::UnitCode::second; }
        attribute temperature_range_min : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "temperature_range_min";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute temperature_range_max : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "temperature_range_max";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute temperature_accuracy : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "temperature_accuracy";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
        attribute temperature_resolution : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "temperature_resolution";
            :>> unit = CatalogModel::UnitCode::kelvin;
        }
    }
    part def Heater :> ElectricalElement {
        attribute external_temperature_control_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "external_temperature_control_required"; }
        attribute heat_sink_required : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "heat_sink_required"; }
        attribute pressure_sensitive_adhesive : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "pressure_sensitive_adhesive"; }
        attribute lead_exit_height : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "lead_exit_height"; :>> unit = CatalogModel::UnitCode::metre; }
        attribute lead_length : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "lead_length"; :>> unit = CatalogModel::UnitCode::metre; }
        attribute minimum_bending_radius : CatalogModel::ParameterRecord[0..*] :> parameter_observations { :>> parameter_name = "minimum_bending_radius"; :>> unit = CatalogModel::UnitCode::metre; }
        attribute resistance : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "resistance";
            :>> unit = CatalogModel::UnitCode::ohm;
        }
        attribute rated_power : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "rated_power";
            :>> unit = CatalogModel::UnitCode::watt;
        }
    }
    part def IntegratedEPS :> ElectricalElement {
        part elements : ElectricalElement[0..*];
        doc /* Internal roles refer to declared product elements. A complete board
         * consumption is counted once. Rail maxima are not a board total.
         */
        attribute channel_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "channel_count";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute solar_input_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "solar_input_count";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute regulated_rail_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "regulated_rail_count";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute unregulated_rail_count : CatalogModel::IntegerParameter[0..*] :> parameter_observations {
            :>> parameter_name = "unregulated_rail_count";
            :>> unit = CatalogModel::UnitCode::dimensionless;
        }
        attribute own_power_consumption : CatalogModel::ParameterRecord[0..*] :> parameter_observations {
            :>> parameter_name = "own_power_consumption";
            :>> unit = CatalogModel::UnitCode::watt;
        }
        attribute bus_regulation : CatalogModel::FeatureRecord[0..*] :> feature_observations { :>> feature_name = "bus_regulation"; }
        attribute controller_programmable : CatalogModel::BooleanFeature[0..*] :> feature_observations { :>> feature_name = "controller_programmable"; }
    }
    part def Subsystem :> PowerConsumer {
        attribute subsystem_id : String[0..1];
        attribute aggregate_profiles : AggregateLoadProfile[0..*];
        attribute accounting_plan : AccountingPlan[0..1];
    }
    part def Load :> ElectricalElement;
    part def DeploymentActuator :> Load {
        attribute deployment_limits : DeploymentLimits[0..1];
        ref part deployment_check : DeploymentActuationCheck[0..1];
    }
    part def Software :> PowerConsumer {
        attribute activity_profiles : SoftwareActivity[0..*];
        doc /* Software allocates execution to an existing physical processor.
         * Activity is counted through that processor's selected load profile.
         * Only characterized incremental demand may be added separately.
         */
    }
    attribute def CurvePoint :> CatalogModel::CurveRecord {
        attribute response_fraction : Real[0..1]; // 1
        attribute clock_frequency : Real[0..1]; // Hz
        attribute current_density : Real[0..1]; // A/m2
        attribute current_limit_maximum : Real[0..1]; // A
        attribute current_limit_minimum : Real[0..1]; // A
        attribute current_limit_programming_resistance : Real[0..1]; // ohm
        attribute current_limit_typical : Real[0..1]; // A
        attribute dc_internal_resistance : Real[0..1]; // ohm
        attribute overcurrent_delay : Real[0..1]; // s
        attribute overcurrent_delay_programming_resistance : Real[0..1]; // ohm
        attribute retry_delay : Real[0..1]; // s
        attribute retry_timer_capacitance : Real[0..1]; // F
        attribute secondary_overcurrent_delay : Real[0..1]; // s
        doc /* Axis leaves retain dictionary identity and canonical units.
         * Populate only the matching independent/dependent axes. Importers check
         * axis name, unit and value agreement with the normalized CurveRecord.
         * Loaded discharge voltage and open circuit voltage are distinct models.
         * Axis leaves are scalar projections of the sourced CurveRecord, not
         * additional independent observations. Catalog.curveAxisInterpretation
         * checks each normalized axis name, scalar type and canonical unit.
         * Importers keep projections aligned and preserve the source sign convention.
         * Each point retains its own condition. Interpolation across different
         * wait states, modes or other conditions needs a declared supporting model.
         */
        attribute voltage : Real[0..1]; // V
        attribute current : Real[0..1]; // A
        attribute power : Real[0..1]; // W
        attribute efficiency : Real[0..1]; // 1
        attribute discharged_capacity : Real[0..1]; // Ah
        attribute state_of_charge : Real[0..1]; // 1
        attribute time : Real[0..1]; // s
        attribute temperature : Real[0..1]; // K
        attribute cycle_count : Integer[0..1]; // 1
        attribute retained_capacity : Real[0..1]; // 1
    }
    attribute def DesignParameterChoice {
        attribute parameter_name : String;
        attribute chosen_value : Real;
        attribute unit : CatalogModel::UnitCode;
        attribute observation : CatalogModel::ParameterRecord[0..*];
        attribute assumption_id : String[0..1];
        doc /* A deliberate design choice, never an implicit catalog default.
         * Observation bindings and assumptions remain separately identifiable.
         */
    }
    enum def ModelKind { solar_iv; solar_temperature; battery_ocv_soc; battery_dc_sag;
        battery_capacity; converter_efficiency; converter_transient; protection;
        thermal; sensor_transfer; clock_error; load_transient; }
    enum def ModelStatus { unavailable; catalog_points; characterized; reduced_order; assumed; }
    attribute def ModelAvailability {
        attribute model_kind : ModelKind;
        attribute status : ModelStatus;
        attribute source_id : String[0..*];
        attribute curve_id : String[0..*];
        attribute condition_id : String[0..*];
        attribute assumption_id : String[0..1];
    }
    enum def ModeKind { off; standby; nominal; safe; acquisition; processing;
        receiving; transmitting; maneuvering; deployment; heating; charging; custom; }
    attribute def OperatingMode {
        attribute mode_id : String;
        attribute kind : ModeKind;
    }
    enum def LoadLawKind { constant_power; constant_current; resistive; characterized_curve; }
    attribute def DutyCycle {
        attribute fraction : Real;
        attribute period : ISQ::DurationValue[0..1];
        attribute on_duration : ISQ::DurationValue[0..1];
        attribute phase : ISQ::DurationValue[0..1];
        doc /* Fraction is in [0,1]. Periodic profiles require a positive period.
         * When both are specified, on_duration equals fraction times period.
         * Averages support energy estimates. Pulses and schedules govern peaks.
         */
    }
    enum def PulseShape { rectangular; piecewise_linear; characterized_curve; }
    attribute def StartupPulse {
        attribute pulse_id : String;
        attribute shape : PulseShape;
        attribute delay : ISQ::DurationValue;
        attribute duration : ISQ::DurationValue;
        attribute additional_current : ISQ::ElectricCurrentValue[0..1];
        attribute additional_power : ISQ::PowerValue[0..1];
        attribute curve_id : String[0..1];
        doc /* Pulse is incremental above the selected steady profile. Specify one
         * demand representation or a characterized waveform, not two sums.
         */
    }
    attribute def ModeLoadProfile {
        attribute profile_id : String;
        attribute mode_id : String;
        attribute load_law : LoadLawKind;
        attribute power : ISQ::PowerValue[0..1];
        attribute current : ISQ::ElectricCurrentValue[0..1];
        attribute resistance : ISQ::ResistanceValue[0..1];
        attribute curve_id : String[0..1];
        attribute voltage_min : ISQ::ElectricPotentialValue[0..1];
        attribute voltage_max : ISQ::ElectricPotentialValue[0..1];
        attribute duty : DutyCycle[0..1];
        attribute startup : StartupPulse[0..*];
        attribute default_enabled : Boolean[0..1];
        attribute essential : Boolean[0..1];
        attribute shedding_allowed : Boolean[0..1];
        attribute shed_priority : Integer[0..1];
        doc /* Profile values describe design demand at the load terminals.
         * Lower priority numbers shed first. Essential loads require an explicit
         * emergency authorization for shedding. Missing behavior stays unknown.
         */
    }
    attribute def SoftwareActivity {
        attribute mode_id : String;
        attribute processor_resource_id : String;
        attribute utilization_fraction : Real[0..1];
        attribute memory_bytes : Integer[0..1];
        attribute deadline : ISQ::DurationValue[0..1];
        attribute incremental_profile_id : String[0..1];
    }
    enum def AccountingScope { physical_leaf; full_aggregate; overhead_only;
        included_in_parent; reference_only; characterized_increment; }
    attribute def AccountingEntry {
        attribute entry_id : String;
        attribute physical_resource_id : String;
        attribute scope : AccountingScope;
        attribute contributes : Boolean;
        attribute covered_resource_ids : String[1..*];
        attribute parent_entry_id : String[0..1];
        attribute profile_id : String[0..1];
        doc /* A contributing full aggregate covers all its included resources.
         * Covered sets of contributing entries must be disjoint. Overhead covers
         * only its own loss/idle domain. Shared execution references contribute
         * no second full processor draw. Increments use distinct characterized
         * resource IDs and exclude the baseline already covered by the processor.
         */
    }
    attribute def AccountingPlan {
        attribute entries : AccountingEntry[0..*];
    }
    attribute def AggregateLoadProfile {
        attribute mode_id : String;
        attribute profile : ModeLoadProfile;
        attribute covered_resource_ids : String[1..*];
        attribute scope : AccountingScope;
    }
    part def AccountingCheck {
        attribute plan : AccountingPlan;
        assert constraint uniqueEntries {
            plan.entries->forAll { in a : AccountingEntry; plan.entries->forAll { in b : AccountingEntry;
                a == b or a.entry_id != b.entry_id } }
        }
        assert constraint noDoubleCounting {
            plan.entries->forAll { in a : AccountingEntry; plan.entries->forAll { in b : AccountingEntry;
                a.entry_id == b.entry_id or not (a.contributes and b.contributes) or
                not (a.covered_resource_ids->exists { in x : String;
                    b.covered_resource_ids->exists { in y : String; x == y } }) } }
        }
        assert constraint referenceRoles {
            plan.entries->forAll { in a : AccountingEntry;
                (a.scope != AccountingScope::reference_only and
                 a.scope != AccountingScope::included_in_parent) or not a.contributes }
        }
        assert constraint ownResourceCovered {
            plan.entries->forAll { in a : AccountingEntry;
                not a.contributes or a.covered_resource_ids->exists { in x : String;
                    x == a.physical_resource_id } }
        }
        assert constraint atomicCoverage {
            plan.entries->forAll { in a : AccountingEntry;
                a.scope != AccountingScope::physical_leaf or size(a.covered_resource_ids) == 1 }
        }
    }
    enum def TriggerKind { absolute_time; periodic_time; mode_entry; command;
        eclipse_entry; eclipse_exit; separation; deployment_complete; low_soc;
        voltage_threshold; temperature_threshold; protection_trip; rtc_alarm; }
    attribute def EventTrigger {
        attribute trigger_id : String;
        attribute kind : TriggerKind;
        attribute resource_id : String[0..1];
        attribute mode_id : String[0..1];
        attribute command_id : String[0..1];
        attribute time : ISQ::DurationValue[0..1];
        attribute period : ISQ::DurationValue[0..1];
        attribute threshold_value : Real[0..1];
        attribute threshold_unit : CatalogModel::UnitCode[0..1];
    }
    attribute def ModeScheduleEntry {
        attribute entry_id : String;
        attribute mode_id : String;
        attribute resource_id : String[0..1];
        attribute start_time : ISQ::DurationValue[0..1];
        attribute duration : ISQ::DurationValue[0..1];
        attribute trigger_id : String[0..1];
        attribute precedence : Integer;
        doc /* Resolve overlapping entries for each resource by explicit precedence.
         * Equal precedence conflicts are invalid. Events use virtual clock time.
         */
    }
    attribute def ModeSchedule {
        attribute modes : OperatingMode[0..*];
        attribute entries : ModeScheduleEntry[0..*] ordered;
        attribute triggers : EventTrigger[0..*];
    }
    part def ScheduleCheck {
        attribute schedule : ModeSchedule;
        assert constraint modeKeys {
            schedule.entries->forAll { in e : ModeScheduleEntry;
                schedule.modes->exists { in m : OperatingMode; m.mode_id == e.mode_id } and
                e.trigger_id->forAll { in t : String;
                    schedule.triggers->exists { in g : EventTrigger; g.trigger_id == t } } }
        }
        assert constraint activation {
            schedule.entries->forAll { in e : ModeScheduleEntry;
                size(e.start_time) + size(e.trigger_id) == 1 and
                e.duration->forAll { in d : ISQ::DurationValue; d > 0[SI::s] } }
        }
        assert constraint triggerPeriods {
            schedule.triggers->forAll { in g : EventTrigger;
                (g.kind != TriggerKind::periodic_time or size(g.period) == 1) and
                g.period->forAll { in p : ISQ::DurationValue; p > 0[SI::s] } and
                (g.kind != TriggerKind::absolute_time or size(g.time) == 1) and
                size(g.threshold_value) == size(g.threshold_unit) }
        }
    }
    part def LoadProfileCheck {
        attribute profile : ModeLoadProfile;
        assert constraint lawInputs {
            if profile.load_law == LoadLawKind::constant_power ? size(profile.power) == 1
            else if profile.load_law == LoadLawKind::constant_current ? size(profile.current) == 1
            else if profile.load_law == LoadLawKind::resistive ? size(profile.resistance) == 1
            else size(profile.curve_id) == 1
        }
        assert constraint resistanceDomain {
            profile.resistance->forAll { in r : ISQ::ResistanceValue; r > 0[SI::ohm] }
        }
        assert constraint voltageOrder {
            profile.voltage_min->forAll { in lo : ISQ::ElectricPotentialValue;
                profile.voltage_max->forAll { in hi : ISQ::ElectricPotentialValue; lo <= hi } }
        }
        assert constraint startupInputs {
            profile.startup->forAll { in pulse : StartupPulse;
                pulse.duration > 0[SI::s] and pulse.delay >= 0[SI::s] and
                size(pulse.additional_current) + size(pulse.additional_power) + size(pulse.curve_id) == 1 and
                (pulse.shape != PulseShape::characterized_curve or size(pulse.curve_id) == 1) }
        }
    }
    part def DutyCycleCheck {
        attribute duty : DutyCycle;
        assert constraint fractionBound { duty.fraction >= 0 and duty.fraction <= 1 }
        assert constraint periodBound { duty.period->forAll { in p : ISQ::DurationValue; p > 0[SI::s] } }
        assert constraint durationConsistency {
            duty.on_duration->forAll { in d : ISQ::DurationValue; duty.period->forAll { in p : ISQ::DurationValue;
                d == duty.fraction * p } }
        }
    }
    part def ElectricalRuntime {
        attribute time : ISQ::DurationValue;
        attribute voltage : ISQ::ElectricPotentialValue;
        attribute current : ISQ::ElectricCurrentValue;
        attribute power : ISQ::PowerValue;
        attribute temperature : ISQ::ThermodynamicTemperatureValue;
        attribute enabled : Boolean;
        assert constraint terminalPower { power == voltage * current }
    }
    part def LoadOperatingPoint {
        attribute law : LoadLawKind;
        attribute enabled : Boolean;
        attribute voltage : ISQ::ElectricPotentialValue;
        attribute current : ISQ::ElectricCurrentValue;
        attribute power : ISQ::PowerValue;
        attribute selected_power : ISQ::PowerValue;
        attribute selected_current : ISQ::ElectricCurrentValue;
        attribute selected_resistance : ISQ::ResistanceValue;
        attribute startup_current : ISQ::ElectricCurrentValue;
        attribute voltage_min : ISQ::ElectricPotentialValue;
        attribute voltage_max : ISQ::ElectricPotentialValue;
        assert constraint terminalPower { power == voltage * current }
        assert constraint nonnegativeDemand {
            current >= 0[SI::A] and startup_current >= 0[SI::A]
        }
        assert constraint loadLaw {
            if not enabled ? current == 0[SI::A]
            else if law == LoadLawKind::constant_power ?
                voltage > 0[SI::V] and power == selected_power + voltage * startup_current
            else if law == LoadLawKind::constant_current ?
                current == selected_current + startup_current
            else if law == LoadLawKind::resistive ?
                selected_resistance > 0[SI::ohm] and
                current == voltage / selected_resistance + startup_current
            else true
        }
        constraint voltageTolerance {
            not enabled or (voltage >= voltage_min and voltage <= voltage_max)
        }
        doc /* The runner binds the active law and incremental pulse at each time.
         * Enabled means electrically supplied. A supplied standby or software
         * shutdown mode retains its characterized nonzero load profile. An open
         * supply path has zero modeled load current. Switch leakage and retained
         * domains are separate accounting entries.
         * Unused selected quantities are unbound inputs, not assumed zeros.
         * A curve law needs a separately supplied interpolation model. Brownout
         * response is a model input. Constant power is undefined at zero voltage.
         */
    }
    part def SheddingCheck {
        attribute essential : Boolean;
        attribute shedding_allowed : Boolean;
        attribute emergency_authorized : Boolean;
        attribute shed_command : Boolean;
        attribute enabled_before : Boolean;
        attribute enabled_after : Boolean;
        assert constraint validShedding {
            enabled_after == (enabled_before and not
                (shed_command and shedding_allowed and (not essential or emergency_authorized)))
        }
    }
    part def EnergyBalanceStep {
        attribute step : ISQ::DurationValue;
        attribute battery_terminal_voltage : ISQ::ElectricPotentialValue;
        attribute charge_current : ISQ::ElectricCurrentValue;
        attribute discharge_current : ISQ::ElectricCurrentValue;
        attribute generation_power : ISQ::PowerValue;
        attribute battery_discharge_power : ISQ::PowerValue;
        attribute battery_charge_power : ISQ::PowerValue;
        attribute delivered_load_power : ISQ::PowerValue;
        attribute converter_loss : ISQ::PowerValue;
        attribute distribution_loss : ISQ::PowerValue;
        attribute curtailed_power : ISQ::PowerValue;
        attribute charge_storage_power : ISQ::PowerValue;
        attribute discharge_internal_power : ISQ::PowerValue;
        attribute self_discharge_power : ISQ::PowerValue;
        attribute stored_energy_before : ISQ::EnergyValue;
        attribute stored_energy_after : ISQ::EnergyValue;
        assert constraint positiveStep { step > 0[SI::s] }
        assert constraint nonnegativeFlows {
            generation_power >= 0[SI::W] and battery_discharge_power >= 0[SI::W] and
            battery_charge_power >= 0[SI::W] and delivered_load_power >= 0[SI::W] and
            converter_loss >= 0[SI::W] and distribution_loss >= 0[SI::W] and
            curtailed_power >= 0[SI::W] and charge_storage_power >= 0[SI::W] and
            discharge_internal_power >= 0[SI::W] and self_discharge_power >= 0[SI::W] and
            stored_energy_before >= 0[SI::J] and stored_energy_after >= 0[SI::J]
        }
        assert constraint singleBatteryBoundary {
            battery_terminal_voltage >= 0[SI::V] and
            charge_current >= 0[SI::A] and discharge_current >= 0[SI::A] and
            (charge_current == 0[SI::A] or discharge_current == 0[SI::A]) and
            battery_charge_power == battery_terminal_voltage * charge_current and
            battery_discharge_power == battery_terminal_voltage * discharge_current and
            (charge_current != 0[SI::A] or charge_storage_power == 0[SI::W]) and
            (discharge_current != 0[SI::A] or discharge_internal_power == 0[SI::W])
        }
        assert constraint busBalance {
            generation_power + battery_discharge_power == delivered_load_power +
                battery_charge_power + converter_loss + distribution_loss + curtailed_power
        }
        assert constraint storageBalance {
            stored_energy_after - stored_energy_before ==
                (charge_storage_power - discharge_internal_power - self_discharge_power) * step
        }
        assert constraint batteryLosses {
            battery_charge_power >= charge_storage_power and
            discharge_internal_power >= battery_discharge_power
        }
        doc /* One battery boundary uses the net terminal current. Charge and
         * discharge are its nonnegative, mutually exclusive directions. Bind
         * the same currents to BatterySOCStep. Hold terminal voltage/current
         * over each integration interval and split intervals at sign changes.
         * Independent battery boundaries require separate step records.
         * Stored energy is in joules. Charge based SOC is a separate balance.
         * Delivered demand includes retained domains and heaters exactly once.
         * Storage-side flows include battery losses. Bus-side flows do not.
         */
    }
    part def BatteryRuntime {
        attribute time : ISQ::DurationValue;
        attribute state_of_charge : Real;
        attribute cell_temperature : ISQ::ThermodynamicTemperatureValue;
        attribute terminal_voltage : ISQ::ElectricPotentialValue;
        attribute open_circuit_voltage : ISQ::ElectricPotentialValue[0..1];
        attribute charge_current : ISQ::ElectricCurrentValue;
        attribute discharge_current : ISQ::ElectricCurrentValue;
        attribute available_charge : ISQ::ElectricChargeValue[0..1];
        attribute charge_inhibited : Boolean;
        attribute protector_tripped : Boolean;
        assert constraint socBound { state_of_charge >= 0 and state_of_charge <= 1 }
        assert constraint currentDirection {
            charge_current >= 0[SI::A] and discharge_current >= 0[SI::A] and
            (charge_current == 0[SI::A] or discharge_current == 0[SI::A])
        }
        assert constraint inhibitedCharge { not charge_inhibited or charge_current == 0[SI::A] }
    }
    part def BatterySOCStep {
        attribute soc_before : Real;
        attribute soc_after : Real;
        attribute step : ISQ::DurationValue;
        attribute charge_current : ISQ::ElectricCurrentValue;
        attribute discharge_current : ISQ::ElectricCurrentValue;
        attribute charge_coulombic_efficiency : Real;
        attribute discharge_coulombic_efficiency : Real;
        attribute available_charge : ISQ::ElectricChargeValue;
        assert constraint validInputs {
            step > 0[SI::s] and available_charge > 0[SI::C] and
            charge_coulombic_efficiency > 0 and charge_coulombic_efficiency <= 1 and
            discharge_coulombic_efficiency > 0 and discharge_coulombic_efficiency <= 1
        }
        assert constraint singleBatteryBoundary {
            charge_current >= 0[SI::A] and discharge_current >= 0[SI::A] and
            (charge_current == 0[SI::A] or discharge_current == 0[SI::A])
        }
        assert constraint coulombBalance {
            (soc_after - soc_before) * available_charge ==
                (charge_coulombic_efficiency * charge_current -
                 discharge_current / discharge_coulombic_efficiency) * step
        }
        constraint socAcceptance { soc_after >= 0 and soc_after <= 1 }
        doc /* SOC is remaining charge divided by effective available charge.
         * These currents are the nonnegative directions of one net battery
         * boundary current. Split intervals at direction changes and bind the
         * same boundary to EnergyBalanceStep. SOC is distinct from stored energy.
         * Effective available charge and efficiency are supplied models.
         * No empirical lifetime or universal allowable DoD relation is imposed.
         */
    }
    part def BatterySagCheck {
        attribute open_circuit_voltage : ISQ::ElectricPotentialValue;
        attribute dc_resistance : ISQ::ResistanceValue;
        attribute discharge_current : ISQ::ElectricCurrentValue;
        attribute charge_current : ISQ::ElectricCurrentValue;
        attribute polarization_drop : ISQ::ElectricPotentialValue;
        attribute terminal_voltage : ISQ::ElectricPotentialValue;
        attribute cutoff_voltage : ISQ::ElectricPotentialValue;
        assert constraint resistanceBound { dc_resistance >= 0[SI::ohm] }
        assert constraint sag {
            terminal_voltage == open_circuit_voltage -
                (discharge_current - charge_current) * dc_resistance - polarization_drop
        }
        constraint voltageAcceptance { terminal_voltage >= cutoff_voltage }
        doc /* Reduced DC model, valid only with characterized SOC/temperature
         * inputs. Polarization is explicit. AC impedance is not substituted.
         */
    }
    part def ChargeTemperatureCheck {
        attribute cell_temperature : ISQ::ThermodynamicTemperatureValue;
        attribute charge_temperature_min : ISQ::ThermodynamicTemperatureValue;
        attribute charge_temperature_max : ISQ::ThermodynamicTemperatureValue;
        attribute charge_request : Boolean;
        attribute autonomous_charger_ready : Boolean;
        attribute hardware_protection_clear : Boolean;
        attribute charge_permitted : Boolean;
        attribute charge_current : ISQ::ElectricCurrentValue;
        assert constraint temperatureOrder { charge_temperature_min <= charge_temperature_max }
        assert constraint permission {
            charge_permitted == (charge_request and autonomous_charger_ready and
                hardware_protection_clear and cell_temperature >= charge_temperature_min and
                cell_temperature <= charge_temperature_max)
        }
        assert constraint inhibitedCurrent { charge_permitted or charge_current == 0[SI::A] }
    }
    part def BatteryEnvelopeCheck {
        ref part battery_state : BatteryRuntime;
        attribute charge_current_limit : ISQ::ElectricCurrentValue;
        attribute continuous_discharge_limit : ISQ::ElectricCurrentValue;
        attribute pulse_discharge_limit : ISQ::ElectricCurrentValue;
        attribute pulse_duration_limit : ISQ::DurationValue;
        attribute discharge_pulse_active : Boolean;
        attribute discharge_pulse_elapsed : ISQ::DurationValue;
        attribute discharge_temperature_min : ISQ::ThermodynamicTemperatureValue;
        attribute discharge_temperature_max : ISQ::ThermodynamicTemperatureValue;
        attribute minimum_voltage : ISQ::ElectricPotentialValue;
        attribute maximum_voltage : ISQ::ElectricPotentialValue;
        constraint currentEnvelope {
            battery_state.charge_current <= charge_current_limit and
            (if discharge_pulse_active ?
                battery_state.discharge_current <= pulse_discharge_limit and
                discharge_pulse_elapsed <= pulse_duration_limit
             else battery_state.discharge_current <= continuous_discharge_limit)
        }
        constraint dischargeTemperature {
            battery_state.discharge_current == 0[SI::A] or
                (battery_state.cell_temperature >= discharge_temperature_min and
                 battery_state.cell_temperature <= discharge_temperature_max)
        }
        constraint terminalVoltage {
            battery_state.terminal_voltage >= minimum_voltage and
            battery_state.terminal_voltage <= maximum_voltage
        }
        doc /* Limits are for the configured cell/pack and stated conditions.
         * Pulse current ratings need their duration. Cell series/parallel topology
         * does not automatically scale protection or complete board ratings.
         */
    }
    enum def ChargePhase { disabled; precharge; constant_current; constant_voltage; terminated; inhibited; }
    part def ChargeControlCheck {
        attribute phase : ChargePhase;
        attribute charging_permitted : Boolean;
        attribute battery_voltage : ISQ::ElectricPotentialValue;
        attribute charge_current : ISQ::ElectricCurrentValue;
        attribute programmed_current : ISQ::ElectricCurrentValue;
        attribute maximum_charge_current : ISQ::ElectricCurrentValue;
        attribute precharge_current_limit : ISQ::ElectricCurrentValue;
        attribute regulation_voltage : ISQ::ElectricPotentialValue;
        attribute regulation_tolerance : ISQ::ElectricPotentialValue;
        attribute termination_current : ISQ::ElectricCurrentValue;
        attribute termination_qualified : Boolean;
        attribute recharge_voltage : ISQ::ElectricPotentialValue;
        attribute recharge_requested : Boolean;
        assert constraint currentCap {
            charge_current >= 0[SI::A] and charge_current <= maximum_charge_current
        }
        assert constraint chargeDisable {
            (charging_permitted and phase != ChargePhase::disabled and
             phase != ChargePhase::inhibited and phase != ChargePhase::terminated) or
                charge_current == 0[SI::A]
        }
        constraint phaseEnvelope {
            (phase != ChargePhase::precharge or charge_current <= precharge_current_limit) and
            (phase != ChargePhase::constant_current or charge_current <= programmed_current) and
            (phase != ChargePhase::constant_voltage or
                (battery_voltage >= regulation_voltage - regulation_tolerance and
                 battery_voltage <= regulation_voltage + regulation_tolerance)) and
            (not termination_qualified or charge_current <= termination_current)
        }
        assert constraint recharge {
            recharge_requested == (phase == ChargePhase::terminated and
                battery_voltage <= recharge_voltage and charging_permitted)
        }
        doc /* A phase observation and envelope check, not a charger state machine.
         * Transition qualification, taper, safety timeout and thermal regulation
         * come from the bound charger model. Unsupported phases stay unused.
         */
    }
    enum def SolarConditioning { mppt; direct_energy_transfer; fixed_voltage; }
    part def SolarOperatingPoint {
        attribute eclipsed : Boolean;
        attribute incidence_factor : Real;
        attribute irradiance : ISQ::IrradianceValue;
        attribute illuminated_area : ISQ::AreaValue;
        attribute cell_temperature : ISQ::ThermodynamicTemperatureValue;
        attribute conditioning : SolarConditioning;
        attribute pv_voltage : ISQ::ElectricPotentialValue;
        attribute pv_current : ISQ::ElectricCurrentValue;
        attribute pv_power : ISQ::PowerValue;
        attribute direct_available_power : ISQ::PowerValue;
        attribute other_available_power : ISQ::PowerValue;
        attribute maximum_power_at_conditions : ISQ::PowerValue;
        attribute achieved_tracking_fraction : Real[0..1];
        assert constraint incidenceBound { incidence_factor >= 0 and incidence_factor <= 1 }
        assert constraint incidentEnergy {
            direct_available_power >= 0[SI::W] and
            direct_available_power <= irradiance * illuminated_area * incidence_factor
        }
        assert constraint eclipse { not eclipsed or direct_available_power == 0[SI::W] }
        assert constraint terminalPower { pv_power == pv_voltage * pv_current }
        constraint availableGeneration {
            pv_power >= 0[SI::W] and pv_power <= direct_available_power + other_available_power
        }
        constraint mpptPerformance {
            achieved_tracking_fraction->forAll { in f : Real;
                f >= 0 and f <= 1 and
                (conditioning != SolarConditioning::mppt or
                 pv_power == f * maximum_power_at_conditions) }
        }
        doc /* Supply an I-V model at irradiance, angle and temperature. Four
         * headline ratings alone do not define the curve. Other flux is explicit.
         * MPPT performance is distinct from input voltage regulation and DET.
         */
    }
    part def RegulatorOperatingPoint {
        attribute enabled : Boolean;
        attribute input_voltage : ISQ::ElectricPotentialValue;
        attribute input_current : ISQ::ElectricCurrentValue;
        attribute output_voltage : ISQ::ElectricPotentialValue;
        attribute output_current : ISQ::ElectricCurrentValue;
        attribute input_power : ISQ::PowerValue;
        attribute output_power : ISQ::PowerValue;
        attribute loss_power : ISQ::PowerValue;
        attribute demanded_output_power : ISQ::PowerValue;
        attribute output_power_cap : ISQ::PowerValue;
        attribute output_current_cap : ISQ::ElectricCurrentValue;
        attribute input_current_cap : ISQ::ElectricCurrentValue;
        attribute demanded_output_current : ISQ::ElectricCurrentValue;
        attribute minimum_regulating_input : ISQ::ElectricPotentialValue;
        attribute rail_voltage_min : ISQ::ElectricPotentialValue;
        attribute rail_voltage_max : ISQ::ElectricPotentialValue;
        attribute saturated : Boolean;
        assert constraint terminalPowers {
            input_power == input_voltage * input_current and
            output_power == output_voltage * output_current and
            input_power == output_power + loss_power and loss_power >= 0[SI::W]
        }
        assert constraint disabledOutput {
            enabled or (output_current == 0[SI::A] and output_power == 0[SI::W])
        }
        assert constraint capability {
            demanded_output_power >= 0[SI::W] and demanded_output_current >= 0[SI::A] and
            output_power >= 0[SI::W] and output_power <= output_power_cap and
            output_current >= 0[SI::A] and output_current <= output_current_cap and
            input_current >= 0[SI::A] and input_current <= input_current_cap
        }
        assert constraint saturation {
            saturated == (demanded_output_power > output_power_cap or
                          demanded_output_current > output_current_cap or
                          input_voltage < minimum_regulating_input)
        }
        constraint railAcceptance {
            if not enabled ? demanded_output_power == 0[SI::W] and demanded_output_current == 0[SI::A]
            else output_voltage >= rail_voltage_min and output_voltage <= rail_voltage_max and
                output_power == demanded_output_power and output_current == demanded_output_current
        }
        doc /* Caps and losses come from characterized conditions, external passives
         * and thermal limits. Saturation is an observed state, not an acceptance
         * waiver. Demand must be delivered within rail voltage limits. Disabled
         * output current/power are zero. Quiescent input remains permitted loss.
         * The interface does not prescribe a fictitious transient transfer law.
         */
    }
    enum def RetryMode { automatic; manual_clear; power_cycle; no_retry; }
    enum def SwitchState { open; closed; tripped; inhibited; }
    part def VoltageProtectionCheck {
        attribute high_trip : Boolean;
        attribute sensed_voltage : ISQ::ElectricPotentialValue;
        attribute trip_threshold : ISQ::ElectricPotentialValue;
        attribute release_threshold : ISQ::ElectricPotentialValue;
        attribute threshold_exceeded : Boolean;
        attribute release_condition : Boolean;
        assert constraint hysteresisOrder {
            if high_trip ? release_threshold <= trip_threshold
            else release_threshold >= trip_threshold
        }
        assert constraint detection {
            threshold_exceeded == (if high_trip ? sensed_voltage >= trip_threshold
                                    else sensed_voltage <= trip_threshold) and
            release_condition == (if high_trip ? sensed_voltage <= release_threshold
                                  else sensed_voltage >= release_threshold)
        }
    }
    part def CurrentProtectionCheck {
        attribute sensed_current : ISQ::ElectricCurrentValue;
        attribute trip_threshold : ISQ::ElectricCurrentValue;
        attribute release_threshold : ISQ::ElectricCurrentValue;
        attribute threshold_exceeded : Boolean;
        attribute release_condition : Boolean;
        assert constraint detection {
            release_threshold <= trip_threshold and
            threshold_exceeded == (sensed_current >= trip_threshold) and
            release_condition == (sensed_current <= release_threshold)
        }
    }
    part def ProtectionTimingCheck {
        attribute threshold_exceeded : Boolean;
        attribute continuous_exceedance_time : ISQ::DurationValue;
        attribute trip_delay : ISQ::DurationValue;
        attribute trip_due : Boolean;
        attribute previous_tripped : Boolean;
        attribute next_tripped : Boolean;
        attribute release_condition : Boolean;
        attribute retry_mode : RetryMode;
        attribute retry_elapsed : ISQ::DurationValue;
        attribute retry_delay : ISQ::DurationValue;
        attribute clear_command : Boolean;
        attribute power_cycled : Boolean;
        attribute release_authorized : Boolean;
        assert constraint nonnegativeDelays {
            trip_delay >= 0[SI::s] and retry_delay >= 0[SI::s] and
            continuous_exceedance_time >= 0[SI::s] and retry_elapsed >= 0[SI::s]
        }
        assert constraint delay {
            trip_due == (threshold_exceeded and continuous_exceedance_time >= trip_delay)
        }
        assert constraint resetExceedanceTimer {
            threshold_exceeded or continuous_exceedance_time == 0[SI::s]
        }
        assert constraint retry {
            release_authorized == (release_condition and
                ((retry_mode == RetryMode::automatic and retry_elapsed >= retry_delay) or
                 (retry_mode == RetryMode::manual_clear and clear_command) or
                 (retry_mode == RetryMode::power_cycle and power_cycled)))
        }
        assert constraint latch {
            next_tripped == (trip_due or (previous_tripped and not release_authorized))
        }
        doc /* Exceedance timer resets when the condition clears. Retry elapsed
         * is measured from the trip. Timing inputs are supplied by the runner.
         * Autonomous hardware evaluation continues with the MCU unpowered.
         */
    }
    part def SwitchControlCheck {
        attribute mcu_powered : Boolean;
        attribute mcu_halted : Boolean;
        attribute mcu_enable_request : Boolean;
        attribute hardware_default_enable : Boolean;
        attribute autonomous_hardware_trip : Boolean;
        attribute flight_inhibited : Boolean;
        attribute source_available : Boolean;
        attribute effective_enable : Boolean;
        attribute switch_closed : Boolean;
        attribute switch_state : SwitchState;
        assert constraint control {
            effective_enable == (if mcu_powered ? mcu_enable_request else hardware_default_enable)
        }
        assert constraint hardwareOverride {
            switch_closed == (effective_enable and not autonomous_hardware_trip and
                not flight_inhibited and source_available)
        }
        assert constraint stateAgreement {
            switch_state == (if autonomous_hardware_trip ? SwitchState::tripped
                else if flight_inhibited ? SwitchState::inhibited
                else if switch_closed ? SwitchState::closed else SwitchState::open)
        }
        doc /* A halted MCU may retain a command latch or invoke a watchdog policy.
         * The runner supplies that design's resulting enable request. Autonomous
         * hardware override remains active during halt, reset or configuration
         * corruption. MCU software cannot clear an asserted hardware trip here.
         * This check describes interrupting load channels. A single-MOSFET ideal
         * diode can conduct forward through its body diode with gate drive off.
         * Its conduction model must preserve that catalog capability separately.
         */
    }
    part def SourceIsolationCheck {
        attribute reverse_biased : Boolean;
        attribute reverse_blocking_present : Boolean;
        attribute isolation_required : Boolean;
        attribute reverse_current : ISQ::ElectricCurrentValue;
        attribute allowed_reverse_leakage : ISQ::ElectricCurrentValue;
        attribute source_voltage : ISQ::ElectricPotentialValue;
        attribute bus_voltage : ISQ::ElectricPotentialValue;
        assert constraint direction { reverse_biased == (bus_voltage > source_voltage) }
        constraint reverseIsolation {
            not (isolation_required and reverse_biased) or
                (reverse_blocking_present and reverse_current >= 0[SI::A] and
                 reverse_current <= allowed_reverse_leakage)
        }
        doc /* Reverse leakage is a sourced or explicit test limit, not zero by
         * default. Exercise solar, battery, external supply and failed sources.
         */
    }
    part def FlightSwitchCheck {
        attribute deployer_present : Boolean;
        attribute remove_before_flight_removed : Boolean;
        attribute independent_inhibits_clear : Boolean[1..*];
        attribute separation_detected : Boolean;
        attribute since_separation : ISQ::DurationValue;
        attribute required_deployment_delay : ISQ::DurationValue;
        attribute deployment_command : Boolean;
        attribute deployment_power_enabled : Boolean;
        assert constraint sequence {
            deployment_power_enabled == (not deployer_present and remove_before_flight_removed and
                independent_inhibits_clear->forAll { in c : Boolean; c } and separation_detected and
                since_separation >= required_deployment_delay and deployment_command)
        }
        doc /* Inhibit count, polarity, bounce filtering and delay are interface
         * choices. These generic inputs do not certify deployer compliance.
         */
    }
    attribute def DeploymentLimits {
        attribute minimum_pulse_duration : ISQ::DurationValue[0..1];
        attribute maximum_pulse_duration : ISQ::DurationValue[0..1];
        attribute minimum_electrical_energy : ISQ::EnergyValue[0..1];
        attribute maximum_electrical_energy : ISQ::EnergyValue[0..1];
        attribute feedback_timeout : ISQ::DurationValue;
        attribute maximum_retries : Integer;
        attribute minimum_retry_interval : ISQ::DurationValue;
    }
    part def DeploymentActuationCheck {
        ref part load : LoadOperatingPoint;
        ref part resistive_actuator : HeaterOperatingPoint[0..1];
        ref part local_thermal_node : ThermalStep[0..1];
        attribute limits : DeploymentLimits;
        attribute characterized_model_id : String[0..1];
        attribute commanded_pulse_duration : ISQ::DurationValue;
        attribute command_active : Boolean;
        attribute inhibits_clear : Boolean;
        attribute step : ISQ::DurationValue;
        attribute pulse_duration_before : ISQ::DurationValue;
        attribute pulse_duration_after : ISQ::DurationValue;
        attribute delivered_energy_before : ISQ::EnergyValue;
        attribute delivered_energy_after : ISQ::EnergyValue;
        attribute since_attempt_start : ISQ::DurationValue;
        attribute completion_feedback : Boolean;
        attribute completion_time : ISQ::DurationValue[0..1];
        attribute completion_in_time : Boolean;
        attribute timed_out : Boolean;
        attribute attempt_finished : Boolean;
        attribute previous_attempt_failed : Boolean;
        attribute since_last_attempt_end : ISQ::DurationValue;
        attribute retry_count : Integer;
        attribute retry_count_after : Integer;
        attribute retry_request : Boolean;
        attribute retry_started : Boolean;
        attribute retry_allowed : Boolean;
        assert constraint limitCoverage {
            size(limits.minimum_pulse_duration) == size(limits.maximum_pulse_duration) and
            size(limits.minimum_electrical_energy) == size(limits.maximum_electrical_energy) and
            size(limits.minimum_pulse_duration) + size(limits.minimum_electrical_energy) >= 1 and
            limits.feedback_timeout > 0[SI::s] and limits.maximum_retries >= 0 and
            limits.minimum_retry_interval >= 0[SI::s] and commanded_pulse_duration > 0[SI::s]
        }
        assert constraint pulseGate {
            load.enabled == (command_active and inhibits_clear and not completion_feedback and
                not timed_out and pulse_duration_before < commanded_pulse_duration)
        }
        assert constraint deliveredElectricalEnergy {
            step > 0[SI::s] and load.power >= 0[SI::W] and
            pulse_duration_before >= 0[SI::s] and delivered_energy_before >= 0[SI::J] and
            pulse_duration_after == pulse_duration_before + (if load.enabled ? step else 0[SI::s]) and
            pulse_duration_after <= commanded_pulse_duration and
            (not load.enabled or since_attempt_start + step <= limits.feedback_timeout) and
            delivered_energy_after == delivered_energy_before + load.power * step
        }
        assert constraint actuatorModel {
            (load.law != LoadLawKind::characterized_curve or size(characterized_model_id) == 1) and
            (size(local_thermal_node) == 0 or size(resistive_actuator) == 1) and
            resistive_actuator->forAll { in heater : HeaterOperatingPoint;
                heater.energized == load.enabled and heater.voltage == load.voltage and
                heater.current == load.current and heater.electrical_power == load.power and
                local_thermal_node->forAll { in node : ThermalStep;
                    node.step == step and node.heater_power == heater.delivered_heat_power } }
        }
        assert constraint feedbackTiming {
            since_attempt_start >= pulse_duration_before and since_last_attempt_end >= 0[SI::s] and
            completion_feedback == (size(completion_time) == 1) and
            completion_time->forAll { in t : ISQ::DurationValue;
                t >= 0[SI::s] and t <= since_attempt_start } and
            completion_in_time == (completion_feedback and
                completion_time->forAll { in t : ISQ::DurationValue; t <= limits.feedback_timeout }) and
            timed_out == (not completion_in_time and since_attempt_start >= limits.feedback_timeout) and
            attempt_finished == (completion_feedback or timed_out)
        }
        assert constraint retryPermission {
            retry_allowed == (previous_attempt_failed and not command_active and inhibits_clear and
                not completion_feedback and retry_count < limits.maximum_retries and
                since_last_attempt_end >= limits.minimum_retry_interval)
        }
        assert constraint retryCountAdvance {
            retry_count_after == retry_count + (if retry_started ? 1 else 0)
        }
        constraint boundedRetry {
            retry_count >= 0 and retry_count_after <= limits.maximum_retries and
            (not retry_request or retry_allowed) and
            (not retry_started or (retry_request and retry_allowed))
        }
        constraint pulseDurationLimits {
            limits.minimum_pulse_duration->forAll { in lo : ISQ::DurationValue;
                limits.maximum_pulse_duration->forAll { in hi : ISQ::DurationValue;
                    lo >= 0[SI::s] and lo <= hi and commanded_pulse_duration >= lo and
                    commanded_pulse_duration <= hi and pulse_duration_after <= hi } }
        }
        constraint completedDeployment {
            attempt_finished and completion_feedback and completion_in_time and not timed_out and
            limits.minimum_pulse_duration->forAll { in lo : ISQ::DurationValue;
                pulse_duration_after >= lo } and
            limits.minimum_electrical_energy->forAll { in lo : ISQ::EnergyValue;
                limits.maximum_electrical_energy->forAll { in hi : ISQ::EnergyValue;
                    lo >= 0[SI::J] and lo <= hi and delivered_energy_after >= lo and
                    delivered_energy_after <= hi } }
        }
        doc /* Generic per-attempt electrical and feedback check. Bind inhibits_clear
         * to the flight switch authorization. Reuse the load law, or an optional
         * resistive heater/thermal view. Account for electrical demand only once.
         * Split steps at pulse, inhibit, feedback and timeout events. Energy is
         * integrated terminal electrical energy. It does not prove release.
         * Feedback and its qualified attempt time are independent model inputs.
         * Late feedback keeps the timeout failure. A missing model is inconclusive.
         * retry_count counts retries begun before this interval. The initial
         * attempt uses zero. Bind the next interval to retry_count_after. Timers
         * and per-attempt energy reset only on a permitted new attempt. Retry history
         * and feedback qualification are supplied by the runner, not a solver here.
         */
    }
    part def ClockStep {
        attribute virtual_time_before : ISQ::DurationValue;
        attribute virtual_time_after : ISQ::DurationValue;
        attribute rtc_time_before : ISQ::DurationValue;
        attribute rtc_time_after : ISQ::DurationValue;
        attribute primary_domain_valid : Boolean;
        attribute backup_domain_valid : Boolean;
        attribute oscillator_ready : Boolean;
        attribute relative_frequency_error : Real;
        attribute rtc_running : Boolean;
        attribute mcu_powered : Boolean;
        attribute mcu_halted : Boolean;
        assert constraint monotonicVirtualTime { virtual_time_after >= virtual_time_before }
        assert constraint forwardClockRate { relative_frequency_error > -1 }
        assert constraint retainedDomain {
            rtc_running == ((primary_domain_valid or backup_domain_valid) and oscillator_ready)
        }
        assert constraint clockAdvance {
            rtc_running implies (rtc_time_after - rtc_time_before ==
                (virtual_time_after - virtual_time_before) * (1 + relative_frequency_error))
        }
        doc /* MCU power, halt, reset and software configuration do not gate the
         * retained RTC domain. If both supplies fail, time retention is a separate
         * model choice. No value is invented.
         */
    }
    enum def TelemetryKind { voltage; current; temperature; state_of_charge; switch_state; protection_state; time; }
    enum def ADCEncoding { unsigned_integer; signed_integer; offset_binary; }
    attribute def TelemetryChannel {
        attribute channel_id : String;
        attribute resource_id : String;
        attribute kind : TelemetryKind;
        attribute encoding : ADCEncoding;
        attribute bit_width : Integer;
        attribute unit : CatalogModel::UnitCode;
        attribute scale : Real;
        attribute offset : Real;
        attribute acquisition_period : ISQ::DurationValue;
        attribute conversion_time : ISQ::DurationValue;
        attribute storage_resource_id : String[0..1];
        doc /* Decoded numeric values use unit. Scale has unit per code and offset
         * has unit. The encoding contract includes analog front end and shunt
         * scaling. Raw ADC codes are not engineering quantities by themselves.
         */
    }
    attribute def ADCRecord {
        attribute channel_id : String;
        attribute sample_time : ISQ::DurationValue;
        attribute available_time : ISQ::DurationValue;
        attribute raw_code : Integer;
        attribute decoded_value : Real;
        attribute unit : CatalogModel::UnitCode;
        attribute valid : Boolean;
        attribute saturated : Boolean;
    }
    attribute def TelemetryStorageRecord {
        attribute resource_id : String;
        attribute record_id : String;
        attribute samples : ADCRecord[0..*] ordered;
        attribute stored_at : ISQ::DurationValue;
        attribute encoded_bytes : Integer;
        attribute checksum_valid : Boolean[0..1];
    }
    part def SensorTransferCheck {
        attribute unit : CatalogModel::UnitCode;
        attribute true_value : Real;
        attribute measured_value : Real;
        attribute relative_gain_error : Real;
        attribute offset_error : Real;
        attribute injected_error : Real;
        attribute range_min : Real;
        attribute range_max : Real;
        attribute allowed_absolute_error : Real;
        attribute unconstrained_reading : Real;
        assert constraint transfer {
            unconstrained_reading == true_value * (1 + relative_gain_error) +
                offset_error + injected_error and
            measured_value == (if unconstrained_reading < range_min ? range_min
                else if unconstrained_reading > range_max ? range_max else unconstrained_reading)
        }
        constraint accuracy {
            measured_value >= true_value - allowed_absolute_error and
            measured_value <= true_value + allowed_absolute_error
        }
        doc /* All additive numeric fields use unit. Gain error is a fraction.
         * Supply characterized transfer/error limits. Clipping and fault injection
         * remain visible before ADC encoding. This numeric unit contract still
         * requires importer checks at the physical sensor interface.
         */
    }
    part def ADCDecodeCheck {
        attribute sample : ADCRecord;
        attribute channel : TelemetryChannel;
        attribute minimum_code : Integer;
        attribute maximum_code : Integer;
        attribute injected_decoding_error : Real;
        assert constraint channelAgreement {
            sample.channel_id == channel.channel_id and sample.unit == channel.unit
        }
        assert constraint decode {
            sample.decoded_value == sample.raw_code * channel.scale +
                channel.offset + injected_decoding_error
        }
        constraint codeRange { sample.raw_code >= minimum_code and sample.raw_code <= maximum_code }
    }
    part def TelemetryTimingCheck {
        attribute sample : ADCRecord;
        attribute channel : TelemetryChannel;
        attribute scheduled_sample_time : ISQ::DurationValue;
        attribute previous_sample_time : ISQ::DurationValue;
        attribute stored_at : ISQ::DurationValue;
        attribute read_at : ISQ::DurationValue;
        attribute maximum_age : ISQ::DurationValue;
        attribute maximum_jitter : ISQ::DurationValue;
        constraint acquisition {
            sample.sample_time >= scheduled_sample_time - maximum_jitter and
            sample.sample_time <= scheduled_sample_time + maximum_jitter and
            sample.available_time >= sample.sample_time + channel.conversion_time
        }
        constraint cadence {
            sample.sample_time - previous_sample_time >= channel.acquisition_period - maximum_jitter and
            sample.sample_time - previous_sample_time <= channel.acquisition_period + maximum_jitter
        }
        constraint storageAndAge {
            stored_at >= sample.available_time and read_at >= stored_at and
            read_at - sample.sample_time <= maximum_age
        }
    }
    part def TelemetryStorageCheck {
        attribute occupied_bytes_before : Integer;
        attribute added_bytes : Integer;
        attribute removed_bytes : Integer;
        attribute occupied_bytes_after : Integer;
        attribute capacity_bytes : Integer;
        assert constraint byteBalance {
            occupied_bytes_after == occupied_bytes_before + added_bytes - removed_bytes
        }
        constraint capacity { occupied_bytes_after >= 0 and occupied_bytes_after <= capacity_bytes }
    }
    part def ThermalStep {
        attribute step : ISQ::DurationValue;
        attribute temperature_before : ISQ::ThermodynamicTemperatureValue;
        attribute temperature_after : ISQ::ThermodynamicTemperatureValue;
        attribute heat_capacity : ISQ::HeatCapacityValue;
        attribute electronic_dissipation : ISQ::PowerValue;
        attribute heater_power : ISQ::PowerValue;
        attribute external_absorbed_power : ISQ::PowerValue;
        attribute conducted_power_out : ISQ::PowerValue;
        attribute radiated_power_out : ISQ::PowerValue;
        assert constraint thermalDomain {
            step > 0[SI::s] and heat_capacity > 0[SI::J / SI::K]
        }
        assert constraint heatBalance {
            heat_capacity * (temperature_after - temperature_before) ==
                (electronic_dissipation + heater_power + external_absorbed_power -
                 conducted_power_out - radiated_power_out) * step
        }
        doc /* Heat capacity, coupling, radiation and environmental inputs require
         * a supplied model. Catalog absence leaves these optional on hardware.
         * ThermalStep inputs are required only when this check is used.
         */
    }
    part def HeaterOperatingPoint {
        attribute energized : Boolean;
        attribute voltage : ISQ::ElectricPotentialValue;
        attribute current : ISQ::ElectricCurrentValue;
        attribute resistance : ISQ::ResistanceValue;
        attribute electrical_power : ISQ::PowerValue;
        attribute delivered_heat_power : ISQ::PowerValue;
        attribute thermal_coupling_fraction : Real;
        assert constraint resistiveLoad {
            resistance > 0[SI::ohm] and
            current == (if energized ? voltage / resistance else 0[SI::A]) and
            electrical_power == voltage * current
        }
        assert constraint thermalCoupling {
            thermal_coupling_fraction >= 0 and thermal_coupling_fraction <= 1 and
            delivered_heat_power == electrical_power * thermal_coupling_fraction
        }
        doc /* Coupling to the chosen thermal node is an explicit model input.
         * Remaining dissipation belongs to other nodes. Open/short faults alter
         * the bound circuit model, not the catalog's nominal resistance.
         */
    }
    part def HeaterControlCheck {
        attribute temperature : ISQ::ThermodynamicTemperatureValue;
        attribute turn_on_temperature : ISQ::ThermodynamicTemperatureValue;
        attribute turn_off_temperature : ISQ::ThermodynamicTemperatureValue;
        attribute enabled : Boolean;
        attribute previously_on : Boolean;
        attribute next_on : Boolean;
        assert constraint thermostatOrder { turn_on_temperature < turn_off_temperature }
        assert constraint thermostat {
            next_on == (enabled and (if temperature <= turn_on_temperature ? true
                else if temperature >= turn_off_temperature ? false else previously_on))
        }
    }
    enum def FaultKind { open_circuit; short_circuit; excess_current; stuck_switch_open;
        stuck_switch_closed; sensor_bias; sensor_stuck; telemetry_corruption; missing_telemetry;
        processor_halt; processor_reset; configuration_corruption;
        clock_drift; clock_stop; lost_backup_supply; thermal_coupling_loss; heater_stuck_on; heater_open; }
    attribute def FaultInjection {
        attribute fault_id : String;
        attribute resource_id : String;
        attribute kind : FaultKind;
        attribute start_time : ISQ::DurationValue;
        attribute duration : ISQ::DurationValue;
        attribute excess_current : ISQ::ElectricCurrentValue[0..1];
        attribute fault_resistance : ISQ::ResistanceValue[0..1];
        attribute sensor_error : Real[0..1];
        attribute sensor_error_unit : CatalogModel::UnitCode[0..1];
        attribute relative_clock_error : Real[0..1];
        attribute added_heat : ISQ::PowerValue[0..1];
        doc /* Bounded electrical/functional injection. Excess current can represent
         * latch-up-like behavior without asserting a radiation cause or rate.
         * Processor halt/reset and configuration corruption alter the bound MCU
         * model. Independent hardware protection and retained RTC still run.
         * Missing telemetry is an absent acquisition, not a zero-valued reading.
         */
    }
    part def FaultBoundCheck {
        attribute fault : FaultInjection;
        attribute test_end : ISQ::DurationValue;
        attribute maximum_duration : ISQ::DurationValue;
        attribute maximum_excess_current : ISQ::ElectricCurrentValue;
        attribute maximum_sensor_error : Real[0..1];
        attribute maximum_relative_clock_error : Real[0..1];
        attribute maximum_added_heat : ISQ::PowerValue[0..1];
        assert constraint boundCoverage {
            (size(fault.sensor_error) == 0 or
                (size(maximum_sensor_error) == 1 and size(fault.sensor_error_unit) == 1)) and
            (size(fault.relative_clock_error) == 0 or size(maximum_relative_clock_error) == 1) and
            (size(fault.added_heat) == 0 or size(maximum_added_heat) == 1)
        }
        assert constraint boundedTime {
            fault.start_time >= 0[SI::s] and fault.duration >= 0[SI::s] and
            fault.duration <= maximum_duration and fault.start_time + fault.duration <= test_end
        }
        assert constraint boundedCurrent {
            fault.excess_current->forAll { in i : ISQ::ElectricCurrentValue; i >= 0[SI::A] and i <= maximum_excess_current }
        }
        assert constraint boundedSensorError {
            fault.sensor_error->forAll { in error : Real;
                maximum_sensor_error->forAll { in bound : Real;
                    bound >= 0 and error >= -bound and error <= bound } }
        }
        assert constraint boundedClockError {
            fault.relative_clock_error->forAll { in error : Real;
                maximum_relative_clock_error->forAll { in bound : Real;
                    bound >= 0 and error >= -bound and error <= bound } }
        }
        assert constraint boundedHeat {
            fault.added_heat->forAll { in heat : ISQ::PowerValue;
                maximum_added_heat->forAll { in bound : ISQ::PowerValue;
                    heat >= 0[SI::W] and heat <= bound } }
        }
        assert constraint resistanceDomain {
            fault.fault_resistance->forAll { in r : ISQ::ResistanceValue; r >= 0[SI::ohm] }
        }
        doc /* Sensor error bounds use fault.sensor_error_unit. Clock error bounds
         * are fractions. Stuck/open/closed fault magnitudes are discrete states.
         */
    }
    enum def MILCaseKind { generation_angle_eclipse; solar_iv_mppt_det;
        battery_charge_discharge; charge_temperature_inhibition; maximum_load_voltage_sag;
        regulated_rail_saturation; startup_inrush; duty_mode_schedule; priority_shedding;
        overcurrent_hysteresis_delay_retry; overvoltage_hysteresis_delay_retry;
        undervoltage_hysteresis_delay_retry; autonomous_protection_mcu_off;
        source_isolation; flight_switch_deployment_sequence; retained_rtc_mcu_off;
        telemetry_acquisition_storage_decode; thermal_heater_cycle; bounded_fault_response;
        shared_processor_aggregate_accounting; deployment_pulse_energy_feedback_retry; }
    enum def MILResult { not_run; passed; failed; inconclusive; }
    attribute def MILAcceptanceLimits {
        attribute minimum_soc : Real[0..1];
        attribute minimum_bus_voltage : ISQ::ElectricPotentialValue[0..1];
        attribute maximum_bus_voltage : ISQ::ElectricPotentialValue[0..1];
        attribute maximum_load_current : ISQ::ElectricCurrentValue[0..1];
        attribute minimum_cell_temperature : ISQ::ThermodynamicTemperatureValue[0..1];
        attribute maximum_cell_temperature : ISQ::ThermodynamicTemperatureValue[0..1];
        attribute maximum_telemetry_age : ISQ::DurationValue[0..1];
        attribute maximum_clock_error : ISQ::DurationValue[0..1];
        attribute energy_residual_tolerance : ISQ::EnergyValue[0..1];
    }
    attribute def MILCaseDefinition {
        attribute case_id : String;
        attribute kind : MILCaseKind;
        attribute schedule : ModeSchedule[0..1];
        attribute duration : ISQ::DurationValue[0..1];
        attribute required_models : ModelKind[0..*];
        attribute acceptance : MILAcceptanceLimits[0..1];
        attribute faults : FaultInjection[0..*];
        attribute result : MILResult[0..1];
        doc /* A runner binds models, conditions, initial state and numeric limits.
         * Missing required behavior yields inconclusive, never a guessed pass.
         * Compare balance residuals within explicit solver tolerances. Definitions
         * and constraints specify interfaces and checks, not an implemented solver.
         */
    }
    part def MILReadinessCheck {
        attribute definition : MILCaseDefinition;
        attribute availability : ModelAvailability[0..*];
        attribute allow_assumed_models : Boolean;
        attribute models_ready : Boolean;
        assert constraint modelCoverage {
            models_ready == definition.required_models->forAll { in required_kind : ModelKind;
                availability->exists { in available : ModelAvailability;
                    available.model_kind == required_kind and
                    available.status != ModelStatus::unavailable and
                    (allow_assumed_models or available.status != ModelStatus::assumed) } }
        }
        constraint noUnsupportedPass {
            definition.result->forAll { in r : MILResult;
                models_ready or r != MILResult::passed }
        }
        doc /* Readiness checks model coverage. The runner must also establish
         * valid conditions, bindings, initial state and acceptance limits.
         */
    }
}
