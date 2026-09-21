// SysML v2 transcription of the Papyrus SysML 1.4 CubeSat model.
// Source repository: https://github.com/snogrady/NogradyThesis_CubeSatConceptualDesignTool
// Source file: cubesatModel/cubesatModel.uml
// Source commit: 3fcde82462dd4988601262ae490a490df2c03281

package cubesatModel {
    doc
    /*
     * This source transcribes the semantic content of the June 2021 Papyrus model.
     * SysML v1 Block stereotypes become SysML v2 part definitions.
     * SysML v1 ValueTypes become SysML v2 attribute definitions.
     * UML actors become part definitions. The UML use case and activity become a use case definition and an action definition.
     * The source Power Parameters defaults are LiteralString values, so this transcription preserves them as strings.
     * Papyrus notation layout, diagram coordinates, and Eclipse project metadata remain outside this semantic source.
     */
    package 'CubeSat Model' {
        package '0 - CSM Overview and Navigation pkg' {
            doc
            /*
             * Package Notation
             *
             * sc- supplemental content such as examples and illustrations
             *
             * ec - extended or expert content such as technical measure parametrics
             */
        }
        package '1 - Stakeholder pkg' {
            package '1.1 - Regulatory Agency Stakeholders pkg' {
            }
            package '1.2 - Mission Stakeholders pkg' {
            }
            package '1.3 - CubeSat Deployer Systems pkg' {
            }
        }
        package '2 - Technical Measures pkg' {
            package '2.1 - Technical Measures - Concepts and Population pkg' {
            }
            package '2.2 - Technical Measures - Concepts - Illustration 1 sc pkg' {
            }
        }
        package '3 - Use Cases pkg' {
        }
        package '4 - Requirements pkg' {
            package 'L1 Enterprise Requirements pkg' {
            }
            package 'L2 Segment Requirements pkg' {
            }
            package 'L3 Subsystem Requirements pkg' {
            }
            package 'L4 Component Requirements pkg' {
            }
            package 'L5 CubeSat Deployer Interface Requirements pkg' {
            }
            package 'Requirement Properties - Illustration sc pkg' {
            }
        }
        package '5 - Architecture pkg' {
            package 'L0_Domain pkg' {
                package 'L0.1_Behaviors pkg' {
                }
                package 'L0.2_Structures pkg' {
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'CubeSat Domain' {
                        ref part 'external constraint' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L0_Domain pkg'::'L0.2_Structures pkg'::'External Constraint' [0..1];
                        ref part 'external environment' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L0_Domain pkg'::'L0.2_Structures pkg'::'External Environment' [0..1];
                        ref part 'cubesat mission enterprise' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L1_Enterprise pkg'::'L1.2_Structures pkg'::'CubeSat Mission Enterprise' [0..1];
                    }
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'External Constraint';
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'External Environment';
                    // Original UML element: uml:Association _KF60cKySEeu1X4pMkZB-mA.
                    // Source end multiplicities: [0..1] and [1].
                    connection def 'External Constraint Association' {
                        end 'external constraint' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L0_Domain pkg'::'L0.2_Structures pkg'::'External Constraint';
                        end 'cubesat domain' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L0_Domain pkg'::'L0.2_Structures pkg'::'CubeSat Domain';
                    }
                    // Original UML element: uml:Association _LHHywKySEeu1X4pMkZB-mA.
                    // Source end multiplicities: [0..1] and [1].
                    connection def 'External Environment Association' {
                        end 'external environment' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L0_Domain pkg'::'L0.2_Structures pkg'::'External Environment';
                        end 'cubesat domain' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L0_Domain pkg'::'L0.2_Structures pkg'::'CubeSat Domain';
                    }
                    // Original UML element: uml:Association _1ySGsKySEeu1X4pMkZB-mA.
                    // Source end multiplicities: [0..1] and [1].
                    connection def 'Cubesat Mission Enterprise Association' {
                        end 'cubesat mission enterprise' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L1_Enterprise pkg'::'L1.2_Structures pkg'::'CubeSat Mission Enterprise';
                        end 'cubesat domain' : cubesatModel::'CubeSat Model'::'5 - Architecture pkg'::'L0_Domain pkg'::'L0.2_Structures pkg'::'CubeSat Domain';
                    }
                    // Original UML element: uml:Actor.
                    part def 'CubeSat Model Stakeholder';
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'Block8';
                }
            }
            package 'L1_Enterprise pkg' {
                package 'L1.1_Behaviors pkg' {
                    package 'Enterprise Use Cases pkg' {
                    }
                }
                package 'L1.2_Structures pkg' {
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'CubeSat Mission Enterprise';
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'GPS';
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'Ground Station Services';
                    // Original UML element: uml:Class with SysML::Blocks::Block.
                    part def 'Transport, Launch, and Deploy Services';
                }
            }
            package 'L2_Segment pkg' {
                package 'L2.1_Space Segment pkg' {
                    package 'L2.1.1_Behaviors pkg' {
                        package 'CubeSat Use Cases pkg' {
                        }
                    }
                    package 'L2.1.2_Structures pkg' {
                        // Original UML element: uml:Class with SysML::Blocks::Block.
                        part def 'CubeSat';
                        // Original UML element: uml:Class with SysML::Blocks::Block.
                        part def 'CubeSat Orbit';
                        // Original UML element: uml:Class with SysML::Blocks::Block.
                        part def 'Space Segment';
                    }
                }
                package 'L2.2_Ground Segment pkg' {
                    package 'L2.2.1_Behaviors pkg' {
                    }
                    package 'L2.2.2_Structures pkg' {
                        // Original UML element: uml:Class with SysML::Blocks::Block.
                        part def 'Block1';
                    }
                }
            }
            package 'L3_Subsystems pkg' {
                package 'L3.1_CubeSat Subsystems pkg' {
                    package 'L3.1.1_Behaviors pkg' {
                    }
                    package 'L3.1.2_Structures pkg' {
                        // Original UML element: uml:Class with SysML::Blocks::Block.
                        part def 'Power Subsystem';
                    }
                }
                package 'L3.2_Ground Subsystems pkg' {
                    package 'L3.2.1_Behaviors pkg' {
                    }
                    package 'L3.2.2_Structures pkg' {
                    }
                }
            }
            package 'L4_Components pkg' {
                package 'L4.1_CubeSat Subsystems Components pkg' {
                    package 'L4.1.0_Shared Components pkg' {
                    }
                    package 'L4.1.1_Mission Payload Components pkg' {
                    }
                    package 'L4.1.2_Command and Data Handling Components pkg' {
                    }
                    package 'L4.1.3_Communication Components pkg' {
                    }
                    package 'L4.1.4_Attitude Determination and Control Components pkg' {
                    }
                    package 'L4.1.5_Guidance Navigation and Control Components pkg' {
                    }
                    package 'L4.1.6_Structures and Mechanisms Components pkg' {
                    }
                    package 'L4.1.7_Power Components pkg' {
                        package 'L4.1.7.1_Behaviors pkg' {
                        }
                        package 'L4.1.7.2_Structures pkg' {
                            // Original UML element: uml:Class with SysML::Blocks::Block.
                            part def 'Solar Arrays';
                            // Original UML element: uml:Class with SysML::Blocks::Block.
                            part def 'Software';
                            // Original UML element: uml:Class with SysML::Blocks::Block.
                            abstract part def 'Regulators and Converters';
                            // Original UML element: uml:Class with SysML::Blocks::Block.
                            part def 'Processor and Memory';
                            // Original UML element: uml:Class with SysML::Blocks::Block.
                            part def 'Power Circuits and Switches';
                            // Original UML element: uml:Class with SysML::Blocks::Block.
                            part def 'Batteries';
                        }
                    }
                    package 'L4.1.8_Thermal Components pkg' {
                    }
                    package 'L4.1.9_Propulsion Components pkg' {
                    }
                }
                package 'L4.2_Ground Subsystems Components pkg' {
                    package 'L4.2.1_Plan and Schedule Components pkg' {
                    }
                    package 'L4.2.2_Spacecraft Command Components pkg' {
                    }
                    package 'L4.2.3_Ground Equipment Control Components pkg' {
                    }
                    package 'L4.2.4_Space-Ground Communication Components pkg' {
                    }
                    package 'L4.2.5_Mission Data Processing Components pkg' {
                    }
                    package 'L4.2.6_Mission Data Dissemination Components pkg' {
                    }
                    package 'L4.2.7_Network Components pkg' {
                    }
                    package 'L4.2.8_Facility Components pkg' {
                    }
                }
            }
            package 'L5_Parameters pkg' {
                package 'L5.1_CubeSat Subsystem Parameters' {
                    package 'L5.1.7_Power Parameters pkg' {
                        // Original UML element: uml:Class with SysML::Blocks::Block.
                        part def 'Power Parameters' {
                            attribute 'Use Case' : ScalarValues::String = "1";
                            // Source UML property type: [none].
                            attribute 'Design Option' : ScalarValues::String = "Custom";
                            // Source UML property type: [none].
                            attribute 'Average Power' : ScalarValues::String = "10.7713";
                            // Source UML property type: [W].
                            attribute 'Average PDU Power Loss' : ScalarValues::String = "11.96811111";
                            // Source UML property type: [W].
                            attribute 'Power Margin' : ScalarValues::String = "2.393622222";
                            // Source UML property type: [W].
                            attribute 'Average Power with Margin' : ScalarValues::String = "14.36173333";
                            // Source UML property type: [W].
                            attribute 'Percent Power Margin' : ScalarValues::String = "20";
                            // Source UML property type: [%].
                            attribute 'Mode 1 Name' : ScalarValues::String = "Ops";
                            // Source UML property type: [none].
                            attribute 'Mode 2 Name' : ScalarValues::String = "Standby";
                            // Source UML property type: [none].
                            attribute 'Mode 3 Name' : ScalarValues::String = "UHF";
                            // Source UML property type: [none].
                            attribute 'Mode 4 Name' : ScalarValues::String = "X-Band";
                            // Source UML property type: [none].
                            attribute 'Mode 1 Duty Cycle' : ScalarValues::String = "10";
                            // Source UML property type: [%].
                            attribute 'Mode 2 Duty Cycle' : ScalarValues::String = "77.4";
                            // Source UML property type: [%].
                            attribute 'Mode 3 Duty Cycle' : ScalarValues::String = "11.1";
                            // Source UML property type: [%].
                            attribute 'Mode 4 Duty Cycle' : ScalarValues::String = "1.5";
                            // Source UML property type: [%].
                            attribute 'ADCS Power Mode 1' : ScalarValues::String = "2.5";
                            // Source UML property type: [W].
                            attribute 'ADCS Power Mode 2' : ScalarValues::String = "2.5";
                            // Source UML property type: [W].
                            attribute 'ADCS Power Mode 3' : ScalarValues::String = "2.5";
                            // Source UML property type: [W].
                            attribute 'ADCS Power Mode 4' : ScalarValues::String = "2.5";
                            // Source UML property type: [W].
                            attribute 'ADCS Average Power' : ScalarValues::String = "2.5";
                            // Source UML property type: [W].
                            attribute 'C&DH Power Mode 1' : ScalarValues::String = "0.3";
                            // Source UML property type: [W].
                            attribute 'C&DH Power Mode 2' : ScalarValues::String = "0.3";
                            // Source UML property type: [W].
                            attribute 'C&DH Power Mode 3' : ScalarValues::String = "0.3";
                            // Source UML property type: [W].
                            attribute 'C&DH Power Mode 4' : ScalarValues::String = "0.3";
                            // Source UML property type: [W].
                            attribute 'C&DH Average Power' : ScalarValues::String = "0.3";
                            // Source UML property type: [W].
                            attribute 'Comms Power Mode 1' : ScalarValues::String = "6";
                            // Source UML property type: [W].
                            attribute 'Comms Power Mode 2' : ScalarValues::String = "6";
                            // Source UML property type: [W].
                            attribute 'Comms Power Mode 3' : ScalarValues::String = "9";
                            // Source UML property type: [W].
                            attribute 'Comms Power Mode 4' : ScalarValues::String = "51";
                            // Source UML property type: [W].
                            attribute 'Comms Average Power' : ScalarValues::String = "7.008";
                            // Source UML property type: [W].
                            attribute 'EPS Power Mode 1' : ScalarValues::String = "0.68";
                            // Source UML property type: [W].
                            attribute 'EPS Power Mode 2' : ScalarValues::String = "0.18";
                            // Source UML property type: [W].
                            attribute 'EPS Power Mode 3' : ScalarValues::String = "0.48";
                            // Source UML property type: [W].
                            attribute 'EPS Power Mode 4' : ScalarValues::String = "0.18";
                            // Source UML property type: [W].
                            attribute 'EPS Average Power' : ScalarValues::String = "0.2633";
                            // Source UML property type: [W].
                            attribute 'GNC Power Mode 1' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'GNC Power Mode 2' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'GNC Power Mode 3' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'GNC Power Mode 4' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'GNC Average Power' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Payload Power Mode 1' : ScalarValues::String = "7";
                            // Source UML property type: [W].
                            attribute 'Payload Power Mode 2' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Payload Power Mode 3' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Payload Power Mode 4' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Payload Average Power' : ScalarValues::String = "0.7";
                            // Source UML property type: [W].
                            attribute 'Structure Power Mode 1' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Structure Power Mode 2' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Structure Power Mode 3' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Structure Power Mode 4' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Structure Average Power' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Thermal Power Mode 1' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Thermal Power Mode 2' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Thermal Power Mode 3' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Thermal Power Mode 4' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Thermal Average Power' : ScalarValues::String = "0";
                            // Source UML property type: [W].
                            attribute 'Solar Cell Efficiency BOL' : ScalarValues::String = "29.5";
                            // Source UML property type: [%].
                            attribute 'Solar Cell Degradation Rate' : ScalarValues::String = "2.5";
                            // Source UML property type: [%/yr].
                            attribute 'Solar Cell Temp Degradation' : ScalarValues::String = "0.5";
                            // Source UML property type: [%/degC].
                            attribute 'Solar Cell Temperature' : ScalarValues::String = "75";
                            // Source UML property type: [degC].
                            attribute 'Solar Tracking' : ScalarValues::String = "1";
                            // Source UML property type: [none].
                            attribute 'Solar Deployable' : ScalarValues::String = "1";
                            // Source UML property type: [none].
                            attribute 'Solar Packing Density' : ScalarValues::String = "1";
                            // Source UML property type: [none].
                            attribute 'Battery One-way Efficiency' : ScalarValues::String = "100";
                            // Source UML property type: [%].
                            attribute 'Battery Cell Mass' : ScalarValues::String = "0.05";
                            // Source UML property type: [kg].
                            attribute 'Battery Cell Energy Capacity' : ScalarValues::String = "9.14";
                            // Source UML property type: [W-hr].
                            attribute 'Battery DoD' : ScalarValues::String = "50";
                            // Source UML property type: [%].
                            attribute 'PDU Efficiency' : ScalarValues::String = "90";
                            // Source UML property type: [%].
                            attribute 'PDU Mass' : ScalarValues::String = "0.1";
                            // Source UML property type: [kg].
                            attribute 'PDU Data Rate' : ScalarValues::String = "1.5";
                            // Source UML property type: [kb/day].
                            attribute 'Solar Flux' : ScalarValues::String = "1367";
                            // Source UML property type: [W/m^2].
                            attribute 'Orbit Energy' : ScalarValues::String = "23.14259348";
                            // Source UML property type: [W-hr].
                            attribute 'Max Eclipse Energy' : ScalarValues::String = "8.494141337";
                            // Source UML property type: [W-hr].
                            attribute 'Min Sun Energy' : ScalarValues::String = "14.64845214";
                            // Source UML property type: [W-hr].
                            attribute 'Battery Roundtrip Efficiency' : ScalarValues::String = "100";
                            // Source UML property type: [%].
                            attribute 'Battery Cycles' : ScalarValues::String = "5439.967414";
                            // Source UML property type: [cycles].
                            attribute 'Battery Degradation Rate' : ScalarValues::String = "15";
                            // Source UML property type: [%/5000 cycles].
                            attribute 'Battery Degradation' : ScalarValues::String = "0.837930987";
                            // Source UML property type: [%].
                            attribute 'Battery Discharge Energy' : ScalarValues::String = "10.13704167";
                            // Source UML property type: [W-hr].
                            attribute 'Number of Battery Cells' : ScalarValues::String = "3";
                            // Source UML property type: [none].
                            attribute 'Battery Capacity' : ScalarValues::String = "27.42";
                            // Source UML property type: [W-hr].
                            attribute 'Battery Mass' : ScalarValues::String = "0.15";
                            // Source UML property type: [kg].
                            attribute 'Solar Cell Efficiency EOL' : ScalarValues::String = "22.38621492";
                            // Source UML property type: [%].
                            attribute 'Lifetime Degradation' : ScalarValues::String = "0.975";
                            // Source UML property type: [%].
                            attribute 'Temperature Degradation' : ScalarValues::String = "0.778312557";
                            // Source UML property type: [%].
                            attribute 'Solar Energy Minimum Sun' : ScalarValues::String = "23.14259348";
                            // Source UML property type: [W-hr].
                            attribute 'Average Solar Power Minimum Sun' : ScalarValues::String = "22.68961614";
                            // Source UML property type: [W].
                            attribute 'Solar Power Flux - EOL' : ScalarValues::String = "306.019558";
                            // Source UML property type: [W/m^2].
                            attribute 'Solar Effective Area' : ScalarValues::String = "0.074144333";
                            // Source UML property type: [m^2].
                            attribute 'Solar Panel Area' : ScalarValues::String = "0.230696212";
                            // Source UML property type: [m^2].
                        }
                    }
                }
            }
        }
        package '6 - Data Models pkg' {
            package 'L1_Enterprise Data Models pkg' {
            }
            package 'L2_Segment Data Models pkg' {
            }
            package 'L3_Subsystem Data Models pkg' {
            }
        }
        package '7 - Validation Verification pkg' {
            package '7.1 - Validation Activities - Population pkg' {
            }
            package '7.2 - Verification Activities - Population pkg' {
            }
            package 'Validation Verification - Concepts - Illustration sc pkg' {
            }
            package 'Validation Verification - Concepts sc pkg' {
            }
        }
        package '8 - CSM Elements and Population pkg' {
            package '8.1 - CSM Elements pkg' {
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Component' {
                    ref part 'parameters' : cubesatModel::'CubeSat Model'::'8 - CSM Elements and Population pkg'::'8.1 - CSM Elements pkg'::'Parameters';
                }
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Component Requirement';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'CubeSat' {
                    ref part 'subsystem' : cubesatModel::'CubeSat Model'::'8 - CSM Elements and Population pkg'::'8.1 - CSM Elements pkg'::'Subsystem';
                }
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'CubeSat Requirement';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Deployer Interface Requirement';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Domain' {
                    ref part 'enterprise' : cubesatModel::'CubeSat Model'::'8 - CSM Elements and Population pkg'::'8.1 - CSM Elements pkg'::'Enterprise';
                }
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Enterprise' {
                    ref part 'segment' : cubesatModel::'CubeSat Model'::'8 - CSM Elements and Population pkg'::'8.1 - CSM Elements pkg'::'Segment';
                }
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Ground Segment Requirement';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Mission Constraint';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'MOE Specification';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'MOP Specification';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Parameters';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Segment' {
                    ref part 'cubeSat' : cubesatModel::'CubeSat Model'::'8 - CSM Elements and Population pkg'::'8.1 - CSM Elements pkg'::'CubeSat';
                }
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Stakeholder Concern';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Subsystem' {
                    ref part 'component' : cubesatModel::'CubeSat Model'::'8 - CSM Elements and Population pkg'::'8.1 - CSM Elements pkg'::'Component';
                }
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Subsystem Requirement';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'TPM Specification';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Validation Activity';
                // Original UML element: uml:Class with SysML::Blocks::Block.
                part def 'Verification Activity';
                // Original UML element: uml:Actor.
                part def 'Stakeholder';
                // Original UML element: uml:UseCase.
                use case def 'Use Case';
                // Original UML element: uml:Activity.
                action def 'Activity';
            }
            package '8.2 - CSM Population pkg' {
            }
            package '8.3 - CSM Types pkg' {
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[W]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[W-hr]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[%]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[kg]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[none]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[m^2]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[W/m^2]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[%/5000 cycles]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[cycles]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[kb/day]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[degC]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[%/degC]';
                // Original UML element: uml:DataType with SysML::Blocks::ValueType.
                attribute def '[%/yr]';
            }
        }
        package '9 - CubeSat Reference Information' {
        }
        package '10 - Background sc pkg' {
        }
    }
}
