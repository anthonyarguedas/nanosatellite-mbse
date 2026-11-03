package FrameworkRequirements {
    private import ScalarValues::*;
    doc /* Reusable parametric orbit and EPS requirements.
     * Every requirement has at least one numeric table parameter.
     * Mission inputs remain unassigned. Numeric suffixes identify scalar units.
     * UI annotations store unit labels separately from requirement prose.
     * Fractions have no unit label. Counts use cells or cycles.
     * Convert Wh to 3600 J before binding. Angles use radians.
     * The requirements-ui annotations supply the table projection.
     * @Name references bind to mission requirement usages.
     * Circular orbit equations follow El Hachimi et al., Eqs. (1)-(10).
     * Additional assessment evidence stays unbound until supplied.
     */

    requirement def OrbitPeriod {
        doc /* @requirements-ui
        {"id":"ORB001","context":"mission","affected":["Orbit"],"origin":"final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)","text":"The preliminary circular orbit shall have period $$orbit_period_s$$ at altitude $$altitude_km$$, using Earth radius $$earthRadius_km$$ and gravitational parameter $$gravitationalParameter_km3_s2$$.","units":{"altitude_km":"km","earthRadius_km":"km","gravitationalParameter_km3_s2":"km^3/s^2","orbit_period_s":"s"},"parameters":{"altitude_km":null,"earthRadius_km":"6378","gravitationalParameter_km3_s2":"398601","orbit_period_s":"2 * pi * sqrt((earthRadius_km + altitude_km) ^ 3 / gravitationalParameter_km3_s2)"},"condition":"altitude_km > 0 and earthRadius_km > 0 and gravitationalParameter_km3_s2 > 0 and orbit_period_s > 0 and orbit_period_s == 2 * pi * sqrt((earthRadius_km + altitude_km) ^ 3 / gravitationalParameter_km3_s2)"}
        */
        attribute altitude_km : Real[0..1];
        attribute earthRadius_km : Real[0..1];
        attribute gravitationalParameter_km3_s2 : Real[0..1];
        attribute orbit_period_s : Real[0..1];
        require constraint acceptance {
            altitude_km > 0 and earthRadius_km > 0 and gravitationalParameter_km3_s2 > 0 and
            orbit_period_s > 0 and orbit_period_s == 2 * TrigFunctions::pi * RealFunctions::sqrt(
                (earthRadius_km + altitude_km) ^ 3 / gravitationalParameter_km3_s2)
        }
    }
    requirement def IlluminationPeriods {
        doc /* @requirements-ui
        {"id":"ORB002","context":"mission","affected":["Orbit"],"origin":"final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period, eq:eclipse-geometry","text":"The preliminary circular orbit at altitude $$altitude_km$$ shall provide $$sunlight_s$$ of sunlight and $$eclipse_s$$ of eclipse per $$orbit_period_s$$ orbit, using Earth radius $$earthRadius_km$$ and horizon angle $$horizon_angle_rad$$.","units":{"altitude_km":"km","earthRadius_km":"km","orbit_period_s":"s","horizon_angle_rad":"rad","sunlight_s":"s","eclipse_s":"s"},"parameters":{"altitude_km":"@OrbitPeriod.altitude_km","earthRadius_km":"@OrbitPeriod.earthRadius_km","orbit_period_s":"@OrbitPeriod.orbit_period_s","horizon_angle_rad":"arccos(earthRadius_km / (earthRadius_km + altitude_km))","sunlight_s":"(0.5 + horizon_angle_rad / pi) * orbit_period_s","eclipse_s":"(0.5 - horizon_angle_rad / pi) * orbit_period_s"},"condition":"altitude_km > 0 and earthRadius_km > 0 and orbit_period_s > 0 and sunlight_s > 0 and eclipse_s > 0 and horizon_angle_rad == arccos(earthRadius_km / (earthRadius_km + altitude_km)) and sunlight_s == (0.5 + horizon_angle_rad / pi) * orbit_period_s and eclipse_s == (0.5 - horizon_angle_rad / pi) * orbit_period_s and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s"}
        */
        attribute altitude_km : Real[0..1];
        attribute earthRadius_km : Real[0..1];
        attribute orbit_period_s : Real[0..1];
        attribute horizon_angle_rad : Real[0..1];
        attribute sunlight_s : Real[0..1];
        attribute eclipse_s : Real[0..1];
        require constraint acceptance {
            altitude_km > 0 and earthRadius_km > 0 and orbit_period_s > 0 and
            horizon_angle_rad == TrigFunctions::arccos((earthRadius_km / (earthRadius_km + altitude_km)) as TrigFunctions::UnitBoundedReal) and
            sunlight_s == (0.5 + horizon_angle_rad / TrigFunctions::pi) * orbit_period_s and
            eclipse_s == (0.5 - horizon_angle_rad / TrigFunctions::pi) * orbit_period_s and
            sunlight_s > 0 and eclipse_s > 0 and
            RealFunctions::abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s
        }
    }
    requirement def LoadEnergy {
        doc /* @requirements-ui
        {"id":"SIZ001","context":"eps","affected":["Batteries","SolarArrays"],"origin":"final_report/design-proposal.tex#eq:minimum-panel-power; EPSModel::ModeLoadProfile and AccountingPlan","text":"The preliminary load budget shall allocate $$sunlight_energy_J$$ during $$sunlight_s$$ of sunlight and $$eclipse_energy_J$$ during $$eclipse_s$$ of eclipse.","units":{"sunlight_power_W":"W","eclipse_power_W":"W","sunlight_s":"s","eclipse_s":"s","sunlight_energy_J":"J","eclipse_energy_J":"J"},"parameters":{"sunlight_power_W":null,"eclipse_power_W":null,"sunlight_duty":null,"eclipse_duty":null,"sunlight_s":"@IlluminationPeriods.sunlight_s","eclipse_s":"@IlluminationPeriods.eclipse_s","sunlight_energy_J":"sunlight_power_W * sunlight_duty * sunlight_s","eclipse_energy_J":"eclipse_power_W * eclipse_duty * eclipse_s"},"condition":"sunlight_power_W >= 0 and eclipse_power_W >= 0 and sunlight_duty >= 0 and sunlight_duty <= 1 and eclipse_duty >= 0 and eclipse_duty <= 1 and sunlight_s > 0 and eclipse_s > 0 and sunlight_energy_J == sunlight_power_W * sunlight_duty * sunlight_s and eclipse_energy_J == eclipse_power_W * eclipse_duty * eclipse_s"}
        */
        attribute sunlight_power_W : Real[0..1];
        attribute eclipse_power_W : Real[0..1];
        attribute sunlight_duty : Real[0..1];
        attribute eclipse_duty : Real[0..1];
        attribute sunlight_s : Real[0..1];
        attribute eclipse_s : Real[0..1];
        attribute sunlight_energy_J : Real[0..1];
        attribute eclipse_energy_J : Real[0..1];
        require constraint acceptance {
            sunlight_power_W >= 0 and eclipse_power_W >= 0 and sunlight_s > 0 and eclipse_s > 0 and
            sunlight_duty >= 0 and sunlight_duty <= 1 and eclipse_duty >= 0 and eclipse_duty <= 1 and
            sunlight_energy_J == sunlight_power_W * sunlight_duty * sunlight_s and
            eclipse_energy_J == eclipse_power_W * eclipse_duty * eclipse_s
        }
    }
    requirement def MinimumPanelPower {
        doc /* @requirements-ui
        {"id":"SIZ002","context":"eps","affected":["SolarArrays","RegulatorsAndConverters"],"origin":"final_report/design-proposal.tex#eq:minimum-panel-power (handpicked-0003)","text":"The solar panels shall provide at least $$panel_min_W$$ at the declared source boundary.","units":{"sunlight_energy_J":"J","eclipse_energy_J":"J","sunlight_s":"s","panel_min_W":"W"},"parameters":{"sunlight_energy_J":"@LoadEnergy.sunlight_energy_J","eclipse_energy_J":"@LoadEnergy.eclipse_energy_J","sunlight_s":"@IlluminationPeriods.sunlight_s","sunlight_efficiency":null,"eclipse_efficiency":null,"panel_min_W":"(sunlight_energy_J / sunlight_efficiency + eclipse_energy_J / eclipse_efficiency) / sunlight_s"},"condition":"sunlight_energy_J >= 0 and eclipse_energy_J >= 0 and sunlight_s > 0 and sunlight_efficiency > 0 and sunlight_efficiency <= 1 and eclipse_efficiency > 0 and eclipse_efficiency <= 1 and panel_min_W == (sunlight_energy_J / sunlight_efficiency + eclipse_energy_J / eclipse_efficiency) / sunlight_s"}
        */
        attribute sunlight_energy_J : Real[0..1];
        attribute eclipse_energy_J : Real[0..1];
        attribute sunlight_s : Real[0..1];
        attribute sunlight_efficiency : Real[0..1];
        attribute eclipse_efficiency : Real[0..1];
        attribute panel_min_W : Real[0..1];
        require constraint acceptance {
            sunlight_energy_J >= 0 and eclipse_energy_J >= 0 and sunlight_s > 0 and
            sunlight_efficiency > 0 and sunlight_efficiency <= 1 and
            eclipse_efficiency > 0 and eclipse_efficiency <= 1 and
            panel_min_W == (sunlight_energy_J / sunlight_efficiency + eclipse_energy_J / eclipse_efficiency) / sunlight_s
        }
    }
    requirement def SolarCellPower {
        doc /* @requirements-ui
        {"id":"SIZ003","context":"eps","affected":["SolarArrays"],"origin":"final_report/design-proposal.tex#eq:solar-cell-eol-power","text":"The selected solar cell shall provide EOL maximum power $$cell_eol_W$$ from maximum power point voltage $$cell_eol_V$$ and current $$cell_eol_A$$.","units":{"cell_eol_V":"V","cell_eol_A":"A","cell_eol_W":"W"},"parameters":{"cell_eol_V":null,"cell_eol_A":null,"cell_eol_W":"cell_eol_V * cell_eol_A"},"condition":"cell_eol_V > 0 and cell_eol_A > 0 and cell_eol_W == cell_eol_V * cell_eol_A"}
        */
        attribute cell_eol_V : Real[0..1];
        attribute cell_eol_A : Real[0..1];
        attribute cell_eol_W : Real[0..1];
        require constraint acceptance { cell_eol_V > 0 and cell_eol_A > 0 and cell_eol_W == cell_eol_V * cell_eol_A }
    }
    requirement def SolarCellCount {
        doc /* @requirements-ui
        {"id":"SIZ004","context":"eps","affected":["SolarArrays"],"origin":"final_report/design-proposal.tex#eq:solar-cell-count, eq:pv-integer-configuration","text":"The array shall install $$installed_cells$$, at least the minimum $$minimum_cells$$ obtained by rounding calculated count $$required_cells$$ upward.","units":{"panel_min_W":"W","cell_eol_W":"W","required_cells":"cells","minimum_cells":"cells","installed_cells":"cells"},"parameters":{"panel_min_W":"@MinimumPanelPower.panel_min_W","cell_eol_W":"@SolarCellPower.cell_eol_W","required_cells":"panel_min_W / cell_eol_W","minimum_cells":"-floor(-required_cells)","installed_cells":null},"integers":["minimum_cells","installed_cells"],"condition":"panel_min_W >= 0 and cell_eol_W > 0 and required_cells == panel_min_W / cell_eol_W and minimum_cells == -floor(-required_cells) and installed_cells > 0 and installed_cells >= minimum_cells"}
        */
        attribute panel_min_W : Real[0..1];
        attribute cell_eol_W : Real[0..1];
        attribute required_cells : Real[0..1];
        attribute minimum_cells : Integer[0..1];
        attribute installed_cells : Integer[0..1];
        require constraint acceptance {
            panel_min_W >= 0 and cell_eol_W > 0 and required_cells == panel_min_W / cell_eol_W and
            minimum_cells == -RealFunctions::floor(-required_cells) and installed_cells > 0 and installed_cells >= minimum_cells
        }
    }
    requirement def MissionCycles {
        doc /* @requirements-ui
        {"id":"SIZ005","context":"eps","affected":["Batteries"],"origin":"final_report/design-proposal.tex#eq:battery-mission-cycles","text":"For one nominal cycle per orbit, the battery shall support at least $$required_cycles$$ over $$lifetime_years$$, using $$days_per_year$$ and $$orbits_per_day$$ derived from period $$orbit_period_s$$.","units":{"orbit_period_s":"s","orbits_per_day":"orbits/day","lifetime_years":"years","days_per_year":"days/year","required_cycles":"cycles"},"parameters":{"orbit_period_s":"@OrbitPeriod.orbit_period_s","orbits_per_day":"86400 / orbit_period_s","lifetime_years":null,"days_per_year":null,"required_cycles":"lifetime_years * days_per_year * orbits_per_day"},"condition":"orbit_period_s > 0 and lifetime_years > 0 and days_per_year > 0 and orbits_per_day == 86400 / orbit_period_s and required_cycles == lifetime_years * days_per_year * orbits_per_day"}
        */
        attribute orbit_period_s : Real[0..1];
        attribute orbits_per_day : Real[0..1];
        attribute lifetime_years : Real[0..1];
        attribute days_per_year : Real[0..1];
        attribute required_cycles : Real[0..1];
        require constraint acceptance {
            orbit_period_s > 0 and lifetime_years > 0 and days_per_year > 0 and
            orbits_per_day == 86400 / orbit_period_s and required_cycles == lifetime_years * days_per_year * orbits_per_day
        }
    }
    requirement def CycleLife {
        doc /* @requirements-ui
        {"id":"SIZ006","context":"eps","affected":["Batteries"],"origin":"final_report/design-proposal.tex#eq:battery-cycle-life; EPS-09","text":"The selected maximum depth of discharge $$dod_max$$ shall support $$supported_cycles$$, at least the required $$required_cycles$$.","units":{"required_cycles":"cycles","cycle_a":"cycles","supported_cycles":"cycles"},"parameters":{"required_cycles":"@MissionCycles.required_cycles","cycle_a":null,"cycle_b":null,"dod_max":null,"fit_dod_min":null,"fit_dod_max":null,"dod_cycle_limit":"(required_cycles / cycle_a) ^ (1 / cycle_b)","supported_cycles":"cycle_a * dod_max ^ cycle_b"},"condition":"required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max and dod_cycle_limit == (required_cycles / cycle_a) ^ (1 / cycle_b) and supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles"}
        */
        attribute required_cycles : Real[0..1];
        attribute cycle_a : Real[0..1];
        attribute cycle_b : Real[0..1];
        attribute dod_max : Real[0..1];
        attribute fit_dod_min : Real[0..1];
        attribute fit_dod_max : Real[0..1];
        attribute dod_cycle_limit : Real[0..1];
        attribute supported_cycles : Real[0..1];
        require constraint acceptance {
            required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and
            fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and
            dod_max >= fit_dod_min and dod_max <= fit_dod_max and
            dod_cycle_limit == (required_cycles / cycle_a) ^ (1 / cycle_b) and
            supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles
        }
    }
    requirement def MinimumBatteryEnergy {
        doc /* @requirements-ui
        {"id":"SIZ007","context":"eps","affected":["Batteries"],"origin":"final_report/design-proposal.tex#eq:battery-energy; EPS-08","text":"The battery shall provide at least $$battery_min_J$$ of BOL energy for eclipse demand $$eclipse_energy_J$$ at maximum DoD $$dod_max$$ and degradation margin $$degradation_margin$$.","units":{"eclipse_energy_J":"J","battery_min_J":"J","required_cycles":"cycles","supported_cycles":"cycles","cycle_a":"cycles"},"parameters":{"eclipse_energy_J":"@LoadEnergy.eclipse_energy_J","dod_max":"@CycleLife.dod_max","degradation_margin":null,"battery_min_J":"eclipse_energy_J / dod_max * (1 + degradation_margin)","required_cycles":"@MissionCycles.required_cycles","supported_cycles":"@CycleLife.supported_cycles","fit_dod_min":"@CycleLife.fit_dod_min","fit_dod_max":"@CycleLife.fit_dod_max","cycle_a":"@CycleLife.cycle_a","cycle_b":"@CycleLife.cycle_b"},"condition":"eclipse_energy_J >= 0 and dod_max > 0 and dod_max <= 1 and degradation_margin >= 0 and battery_min_J == eclipse_energy_J / dod_max * (1 + degradation_margin) and required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max and supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles"}
        */
        attribute eclipse_energy_J : Real[0..1];
        attribute dod_max : Real[0..1];
        attribute degradation_margin : Real[0..1];
        attribute battery_min_J : Real[0..1];
        attribute required_cycles : Real[0..1];
        attribute supported_cycles : Real[0..1];
        attribute fit_dod_min : Real[0..1];
        attribute fit_dod_max : Real[0..1];
        attribute cycle_a : Real[0..1];
        attribute cycle_b : Real[0..1];
        require constraint acceptance {
            eclipse_energy_J >= 0 and dod_max > 0 and dod_max <= 1 and degradation_margin >= 0 and
            battery_min_J == eclipse_energy_J / dod_max * (1 + degradation_margin) and
            required_cycles > 0 and cycle_a > 0 and cycle_b < 0 and
            fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and
            dod_max >= fit_dod_min and dod_max <= fit_dod_max and
            supported_cycles == cycle_a * dod_max ^ cycle_b and supported_cycles >= required_cycles
        }
    }
    requirement def BatteryCapacityScreen {
        doc /* @requirements-ui
        {"id":"SIZ008","context":"eps","affected":["Batteries"],"origin":"final_report/design-proposal.tex#eq:battery-assembly-capacity; EPS-08","text":"The selected battery shall have BOL energy $$pack_bol_J$$, at least the preliminary minimum $$battery_min_J$$.","units":{"battery_min_J":"J","pack_bol_J":"J","pack_eol_J":"J"},"parameters":{"battery_min_J":"@MinimumBatteryEnergy.battery_min_J","pack_bol_J":null,"retained_energy_factor":null,"pack_eol_J":"retained_energy_factor * pack_bol_J"},"condition":"battery_min_J >= 0 and pack_bol_J > 0 and pack_bol_J >= battery_min_J and retained_energy_factor > 0 and retained_energy_factor <= 1 and pack_eol_J == retained_energy_factor * pack_bol_J"}
        */
        attribute battery_min_J : Real[0..1];
        attribute pack_bol_J : Real[0..1];
        attribute retained_energy_factor : Real[0..1];
        attribute pack_eol_J : Real[0..1];
        require constraint acceptance {
            battery_min_J >= 0 and pack_bol_J > 0 and pack_bol_J >= battery_min_J and
            retained_energy_factor > 0 and retained_energy_factor <= 1 and
            pack_eol_J == retained_energy_factor * pack_bol_J
        }
    }
    requirement def EPS02 {
        doc /* @requirements-ui
        {"id":"EPS002","context":"eps","affected":["SolarArrays"],"origin":"final_report/eps-requirements.tex#EPS-02; eq:array-generation-screen, eq:pv-integer-configuration","text":"EPS-02. The solar arrays shall provide at least $$panel_min_W$$ of average source power from $$sunlight_generation_J$$ over $$sunlight_s$$ of sunlight at each section's attainable DET or MPPT operating point under applicable illumination and EOL conditions.","units":{"sunlight_generation_J":"J","sunlight_s":"s","panel_min_W":"W"},"parameters":{"sunlight_generation_J":null,"sunlight_s":"@IlluminationPeriods.sunlight_s","panel_min_W":"@MinimumPanelPower.panel_min_W"},"condition":""}
        */
        attribute sunlight_generation_J : Real[0..1];
        attribute sunlight_s : Real[0..1];
        attribute panel_min_W : Real[0..1];
        attribute applicable_conditions_assessed : Boolean[0..1];
        attribute cell_arrangement_compliant : Boolean[0..1];
        require constraint acceptance { applicable_conditions_assessed and sunlight_s > 0 and panel_min_W >= 0 and sunlight_generation_J / sunlight_s >= panel_min_W }
    }
    requirement def EPS08 {
        doc /* @requirements-ui
        {"id":"EPS008","context":"eps","affected":["Batteries"],"origin":"final_report/eps-requirements.tex#EPS-08; eq:battery-energy, eq:battery-assembly-capacity, eq:battery-assembly-ratings","text":"EPS-08. The battery pack BOL energy $$pack_bol_J$$ shall meet minimum energy $$battery_min_J$$ from preliminary battery sizing.","units":{"pack_bol_J":"J","battery_min_J":"J"},"parameters":{"pack_bol_J":"@BatteryCapacityScreen.pack_bol_J","battery_min_J":"@MinimumBatteryEnergy.battery_min_J"},"condition":""}
        */
        attribute pack_bol_J : Real[0..1];
        attribute battery_min_J : Real[0..1];
        attribute retained_capacities_applicable : Boolean[0..1];
        attribute assembly_or_pack_ratings_supported : Boolean[0..1];
        attribute margin_applied_once : Boolean[0..1];
        require constraint acceptance { battery_min_J >= 0 and pack_bol_J >= battery_min_J }
    }
    requirement def EPS09 {
        doc /* @requirements-ui
        {"id":"EPS009","context":"eps","affected":["Batteries"],"origin":"final_report/eps-requirements.tex#EPS-09; eq:battery-mission-cycles, eq:battery-cycle-life","text":"EPS-09. For nominal operation, the battery pack shall support $$supported_cycles$$, at least the required $$required_cycles$$ at the selected DoD and applicable conditions.","units":{"required_cycles":"cycles","supported_cycles":"cycles"},"parameters":{"required_cycles":"@MissionCycles.required_cycles","supported_cycles":"@CycleLife.supported_cycles","dod_max":"@CycleLife.dod_max","nominal_dod":null},"condition":""}
        */
        attribute required_cycles : Real[0..1];
        attribute supported_cycles : Real[0..1];
        attribute nominal_dod : Real[0..1];
        attribute dod_max : Real[0..1];
        attribute cycle_data_applicable : Boolean[0..1];
        attribute exceptional_discharge_separate : Boolean[0..1];
        require constraint acceptance { required_cycles > 0 and supported_cycles >= required_cycles and cycle_data_applicable }
    }
    requirement def EPS11 {
        doc /* @requirements-ui
        {"id":"EPS011","context":"eps","affected":["Batteries","SolarArrays"],"origin":"final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility","text":"EPS-11. The EPS shall replenish the battery from starting energy $$energy_start_J$$ and charge based SOC $$soc_start$$ over every specified nominal repeating interval.","units":{"energy_start_J":"J","energy_end_J":"J","closure_tolerance_J":"J"},"parameters":{"energy_start_J":null,"energy_end_J":null,"closure_tolerance_J":null,"soc_start":null,"soc_end":null},"condition":""}
        */
        attribute energy_start_J : Real[0..1];
        attribute energy_end_J : Real[0..1];
        attribute closure_tolerance_J : Real[0..1];
        attribute soc_start : Real[0..1];
        attribute soc_end : Real[0..1];
        attribute all_repeating_intervals_assessed : Boolean[0..1];
        require constraint acceptance { closure_tolerance_J >= 0 and energy_start_J >= 0 and energy_end_J >= energy_start_J - closure_tolerance_J and soc_start >= 0 and soc_end <= 1 and soc_end >= soc_start and all_repeating_intervals_assessed }
    }
    requirement def EPS19 {
        doc /* @requirements-ui
        {"id":"EPS019","context":"eps","affected":["Batteries","SolarArrays","ProcessorAndMemory","RegulatorsAndConverters","PowerCircuitsAndSwitches"],"origin":"final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets","text":"EPS-19. Total EPS mass $$mass_kg$$ shall remain within allocation $$mass_allocation_kg$$.","units":{"mass_kg":"kg","mass_allocation_kg":"kg","volume_m3":"m^3","volume_allocation_m3":"m^3"},"parameters":{"mass_kg":null,"mass_allocation_kg":null,"volume_m3":null,"volume_allocation_m3":null},"condition":""}
        */
        attribute mass_kg : Real[0..1];
        attribute mass_allocation_kg : Real[0..1];
        attribute volume_m3 : Real[0..1];
        attribute volume_allocation_m3 : Real[0..1];
        attribute required_auxiliaries_included : Boolean[0..1];
        attribute accounting_boundaries_disjoint : Boolean[0..1];
        require constraint acceptance { mass_kg >= 0 and mass_kg <= mass_allocation_kg and required_auxiliaries_included and accounting_boundaries_disjoint }
    }
    requirement def EPS21 {
        doc /* @requirements-ui
        {"id":"EPS021","context":"eps","affected":["ProcessorAndMemory","Software"],"origin":"final_report/design-proposal.tex#eq:software-resource-screen; Software-host checks","text":"EPS-21. Each software execution host shall provide $$required_data_bytes$$ of data memory within an allocation of $$available_data_bytes$$.","units":{"required_data_bytes":"bytes","available_data_bytes":"bytes","required_program_bytes":"bytes","available_program_bytes":"bytes"},"parameters":{"required_data_bytes":null,"available_data_bytes":null,"required_program_bytes":null,"available_program_bytes":null,"required_utilization":null,"allocated_utilization":null},"integers":["required_data_bytes","available_data_bytes","required_program_bytes","available_program_bytes"],"condition":""}
        */
        attribute required_data_bytes : Integer[0..1];
        attribute available_data_bytes : Integer[0..1];
        attribute required_program_bytes : Integer[0..1];
        attribute available_program_bytes : Integer[0..1];
        attribute required_utilization : Real[0..1];
        attribute allocated_utilization : Real[0..1];
        attribute all_hosts_and_tasks_assessed : Boolean[0..1];
        attribute host_firmware_drivers_compatible : Boolean[0..1];
        attribute deadlines_and_service_response_supported : Boolean[0..1];
        require constraint acceptance {
            required_data_bytes >= 0 and required_data_bytes <= available_data_bytes and all_hosts_and_tasks_assessed
        }
    }
    requirement def OrbitPeriodClosure {
        doc /* @requirements-ui
        {"id":"ORB003","context":"mission","affected":["Orbit"],"derivesFrom":["IlluminationPeriods"],"origin":"final_report/design-proposal.tex#eq:sunlight-period, eq:eclipse-period","text":"The positive sunlight and eclipse periods shall sum to $$orbit_period_s$$ within numerical tolerance.","units":{"orbit_period_s":"s","sunlight_s":"s","eclipse_s":"s"},"parameters":{"orbit_period_s":"@IlluminationPeriods.orbit_period_s","sunlight_s":"@IlluminationPeriods.sunlight_s","eclipse_s":"@IlluminationPeriods.eclipse_s"},"condition":"orbit_period_s > 0 and sunlight_s > 0 and eclipse_s > 0 and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s"}
        */
        attribute orbit_period_s : Real[0..1];
        attribute sunlight_s : Real[0..1];
        attribute eclipse_s : Real[0..1];
        require constraint acceptance { orbit_period_s > 0 and sunlight_s > 0 and eclipse_s > 0 and RealFunctions::abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s }
    }
    requirement def EnergyPathEfficiencyBounds {
        doc /* @requirements-ui
        {"id":"SIZ011","context":"eps","affected":["SolarArrays","RegulatorsAndConverters"],"derivesFrom":["MinimumPanelPower"],"origin":"final_report/design-proposal.tex#eq:minimum-panel-power","text":"Sunlight path efficiency $$sunlight_efficiency$$ and eclipse path efficiency $$eclipse_efficiency$$ shall lie in (0,1].","parameters":{"sunlight_efficiency":"@MinimumPanelPower.sunlight_efficiency","eclipse_efficiency":"@MinimumPanelPower.eclipse_efficiency"},"condition":"sunlight_efficiency > 0 and sunlight_efficiency <= 1 and eclipse_efficiency > 0 and eclipse_efficiency <= 1"}
        */
        attribute sunlight_efficiency : Real[0..1];
        attribute eclipse_efficiency : Real[0..1];
        require constraint acceptance { sunlight_efficiency > 0 and sunlight_efficiency <= 1 and eclipse_efficiency > 0 and eclipse_efficiency <= 1 }
    }
    requirement def CycleFitDomain {
        doc /* @requirements-ui
        {"id":"SIZ013","context":"eps","affected":["Batteries"],"derivesFrom":["CycleLife"],"origin":"final_report/design-proposal.tex#eq:battery-cycle-life","text":"Maximum DoD $$dod_max$$ shall lie in (0,1] and the sourced fit interval [$$fit_dod_min$$,$$fit_dod_max$$] for power law coefficients $$cycle_a$$ and $$cycle_b$$.","units":{"cycle_a":"cycles"},"parameters":{"dod_max":"@CycleLife.dod_max","fit_dod_min":"@CycleLife.fit_dod_min","fit_dod_max":"@CycleLife.fit_dod_max","cycle_a":"@CycleLife.cycle_a","cycle_b":"@CycleLife.cycle_b"},"condition":"cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max"}
        */
        attribute dod_max : Real[0..1];
        attribute fit_dod_min : Real[0..1];
        attribute fit_dod_max : Real[0..1];
        attribute cycle_a : Real[0..1];
        attribute cycle_b : Real[0..1];
        require constraint acceptance { cycle_a > 0 and cycle_b < 0 and fit_dod_min > 0 and fit_dod_min <= fit_dod_max and fit_dod_max <= 1 and dod_max >= fit_dod_min and dod_max <= fit_dod_max }
    }
    requirement def CycleLimitedDoD {
        doc /* @requirements-ui
        {"id":"SIZ014","context":"eps","affected":["Batteries"],"derivesFrom":["CycleLife"],"origin":"final_report/design-proposal.tex#eq:battery-cycle-life","text":"Maximum DoD $$dod_max$$ shall not exceed fitted cycle limit $$dod_cycle_limit$$.","parameters":{"dod_max":"@CycleLife.dod_max","dod_cycle_limit":"@CycleLife.dod_cycle_limit"},"condition":"dod_max > 0 and dod_max <= 1 and dod_cycle_limit > 0 and dod_max <= dod_cycle_limit"}
        */
        attribute dod_max : Real[0..1];
        attribute dod_cycle_limit : Real[0..1];
        require constraint acceptance { dod_max > 0 and dod_max <= 1 and dod_cycle_limit > 0 and dod_max <= dod_cycle_limit }
    }
    requirement def BatteryRetainedEnergy {
        doc /* @requirements-ui
        {"id":"SIZ016","context":"eps","affected":["Batteries"],"derivesFrom":["BatteryCapacityScreen"],"origin":"final_report/design-proposal.tex#eq:battery-assembly-capacity","text":"Battery EOL energy $$pack_eol_J$$ shall equal BOL energy $$pack_bol_J$$ multiplied by retained energy factor $$retained_energy_factor$$ in (0,1].","units":{"pack_bol_J":"J","pack_eol_J":"J"},"parameters":{"pack_bol_J":"@BatteryCapacityScreen.pack_bol_J","pack_eol_J":"@BatteryCapacityScreen.pack_eol_J","retained_energy_factor":"@BatteryCapacityScreen.retained_energy_factor"},"condition":"pack_bol_J > 0 and retained_energy_factor > 0 and retained_energy_factor <= 1 and pack_eol_J == retained_energy_factor * pack_bol_J"}
        */
        attribute pack_bol_J : Real[0..1];
        attribute pack_eol_J : Real[0..1];
        attribute retained_energy_factor : Real[0..1];
        require constraint acceptance { pack_bol_J > 0 and retained_energy_factor > 0 and retained_energy_factor <= 1 and pack_eol_J == retained_energy_factor * pack_bol_J }
    }
    requirement def EPS47 {
        doc /* @requirements-ui
        {"id":"EPS047","context":"eps","affected":["Batteries"],"derivesFrom":["EPS09"],"origin":"final_report/eps-requirements.tex#EPS-09","text":"EPS-47. Nominal cycle DoD $$nominal_dod$$ shall not exceed maximum DoD $$dod_max$$.","parameters":{"nominal_dod":"@EPS09.nominal_dod","dod_max":"@EPS09.dod_max"},"condition":""}
        */
        attribute nominal_dod : Real[0..1];
        attribute dod_max : Real[0..1];
        require constraint acceptance { nominal_dod >= 0 and nominal_dod <= dod_max and dod_max > 0 and dod_max <= 1 }
    }
    requirement def EPS52 {
        doc /* @requirements-ui
        {"id":"EPS052","context":"eps","affected":["Batteries","SolarArrays"],"derivesFrom":["EPS11"],"origin":"final_report/eps-requirements.tex#EPS-11; eq:nominal-energy-feasibility","text":"EPS-52. Ending energy $$energy_end_J$$ shall be at least starting energy $$energy_start_J$$ minus nonnegative numerical closure tolerance $$closure_tolerance_J$$ over each nominal repeating interval.","units":{"energy_start_J":"J","energy_end_J":"J","closure_tolerance_J":"J"},"parameters":{"energy_start_J":"@EPS11.energy_start_J","energy_end_J":"@EPS11.energy_end_J","closure_tolerance_J":"@EPS11.closure_tolerance_J"},"condition":""}
        */
        attribute energy_start_J : Real[0..1];
        attribute energy_end_J : Real[0..1];
        attribute closure_tolerance_J : Real[0..1];
        attribute all_repeating_intervals_assessed : Boolean[0..1];
        require constraint acceptance { energy_start_J >= 0 and energy_end_J >= 0 and closure_tolerance_J >= 0 and energy_end_J >= energy_start_J - closure_tolerance_J and all_repeating_intervals_assessed }
    }
    requirement def EPS53 {
        doc /* @requirements-ui
        {"id":"EPS053","context":"eps","affected":["Batteries","SolarArrays"],"derivesFrom":["EPS11"],"origin":"final_report/eps-requirements.tex#EPS-11","text":"EPS-53. Ending charge based SOC $$soc_end$$ shall be at least starting SOC $$soc_start$$ over each nominal repeating interval.","parameters":{"soc_start":"@EPS11.soc_start","soc_end":"@EPS11.soc_end"},"condition":""}
        */
        attribute soc_start : Real[0..1];
        attribute soc_end : Real[0..1];
        attribute all_repeating_intervals_assessed : Boolean[0..1];
        require constraint acceptance { soc_start >= 0 and soc_end <= 1 and soc_end >= soc_start and all_repeating_intervals_assessed }
    }
    requirement def EPS78 {
        doc /* @requirements-ui
        {"id":"EPS078","context":"eps","affected":["Batteries","SolarArrays","ProcessorAndMemory","RegulatorsAndConverters","PowerCircuitsAndSwitches"],"derivesFrom":["EPS19"],"origin":"final_report/eps-requirements.tex#EPS-19; eq:eps-product-budgets","text":"EPS-78. Occupied EPS volume $$volume_m3$$ shall remain within allocation $$volume_allocation_m3$$.","units":{"volume_m3":"m^3","volume_allocation_m3":"m^3"},"parameters":{"volume_m3":"@EPS19.volume_m3","volume_allocation_m3":"@EPS19.volume_allocation_m3"},"condition":""}
        */
        attribute volume_m3 : Real[0..1];
        attribute volume_allocation_m3 : Real[0..1];
        attribute required_auxiliaries_included : Boolean[0..1];
        attribute accounting_boundaries_disjoint : Boolean[0..1];
        require constraint acceptance { volume_m3 >= 0 and volume_m3 <= volume_allocation_m3 and required_auxiliaries_included and accounting_boundaries_disjoint }
    }
    requirement def EPS88 {
        doc /* @requirements-ui
        {"id":"EPS088","context":"eps","affected":["ProcessorAndMemory","Software"],"derivesFrom":["EPS21"],"origin":"final_report/design-proposal.tex#eq:software-resource-screen","text":"EPS-88. Each software execution host shall provide $$required_program_bytes$$ of program storage within an allocation of $$available_program_bytes$$.","units":{"required_program_bytes":"bytes","available_program_bytes":"bytes"},"parameters":{"required_program_bytes":"@EPS21.required_program_bytes","available_program_bytes":"@EPS21.available_program_bytes"},"integers":["required_program_bytes","available_program_bytes"],"condition":""}
        */
        attribute required_program_bytes : Integer[0..1];
        attribute available_program_bytes : Integer[0..1];
        attribute all_hosts_and_tasks_assessed : Boolean[0..1];
        require constraint acceptance { required_program_bytes >= 0 and required_program_bytes <= available_program_bytes and all_hosts_and_tasks_assessed }
    }
    requirement def EPS89 {
        doc /* @requirements-ui
        {"id":"EPS089","context":"eps","affected":["ProcessorAndMemory","Software"],"derivesFrom":["EPS21"],"origin":"final_report/design-proposal.tex#eq:software-resource-screen","text":"EPS-89. The sum of each allocated task's execution time divided by its period shall give required utilization $$required_utilization$$, at most allocation $$allocated_utilization$$.","parameters":{"required_utilization":"@EPS21.required_utilization","allocated_utilization":"@EPS21.allocated_utilization"},"condition":""}
        */
        attribute required_utilization : Real[0..1];
        attribute allocated_utilization : Real[0..1];
        attribute all_hosts_and_tasks_assessed : Boolean[0..1];
        require constraint acceptance { required_utilization >= 0 and required_utilization <= allocated_utilization and allocated_utilization <= 1 and all_hosts_and_tasks_assessed }
    }
}
