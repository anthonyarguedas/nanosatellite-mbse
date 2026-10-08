// Proposed six-component physical candidate. Empirical status: proposed/unexecuted.
package CandidateCDT {
    private import PhysicalVocabulary::*;
    private import FrameworkDomain::*;
    private import BoundaryViews::*;
    private import FrameworkLogical::*;
    private import ScalarValues::*;
    doc /* PA-CDT: User custom native SysML v2/CSRM composite. Every cited method supplies a bounded subset. All joins, missing capabilities and whole-CUBICS/F Prime adapters are proposed completion. There is no selected candidate or empirical comparison outcome. */
    // Actual native enrichment used by C01/C02/C03. Actual C01/C02/C03 operations bind this native package.
    package NativeEPS {
        private import ScalarValues::*;
        private import ISQ::*;
        private import SI::*;
        private import FrameworkDomain::*;
        private import PhysicalVocabulary::IntegrationScaffold::*;
        doc /* PA-CDT proposed CSRM enrichment. The source provides a mission-tailored architecture and requirement/V&V relationship pattern. Its baseline is incomplete and the cited CSRM lacks added power/weight parametrics. The quantity properties, native requirements, calculations, bindings and maintained COTS roles below are proposed additions. No complete conversion, mission limits, measured values, numerical execution or product satisfaction is asserted. Python implements or orchestrates the declared analyses. */

        item def COTSRecord :> EngineeringArtifact {
            attribute recordIdentityRevisionPredecessor : String;
            attribute manufacturerPartNumberVariant : String;
            attribute technicalRoleAndSupportedEffects : String;
            attribute datasheetSourceRevisionLocatorDigest : String;
            attribute sourceDateReviewDateMaintainer : String;
            attribute heritageQualificationAndApplicabilityEvidence : String;
            attribute availabilityEvidenceDateAndUnknowns : String;
            attribute mass : MassValue [0..1];
            attribute occupiedVolume : VolumeValue [0..1];
            attribute ratedPower : PowerValue [0..1];
            attribute ratedEnergy : EnergyValue [0..1];
            attribute minimumVoltage : ElectricPotentialValue [0..1];
            attribute maximumVoltage : ElectricPotentialValue [0..1];
            attribute maximumCurrent : ElectricCurrentValue [0..1];
            attribute temperatureDomain : ThermodynamicTemperatureValue [0..*];
            attribute quantityUncertaintyValidityAndMissingFields : String;
            doc /* Required maintained component schema. Optional quantities represent absent source data without inventing zero. Every populated value retains source revision, unit, applicability and uncertainty. A record is technical evidence, not a design choice, compatibility verdict or qualification claim. */
        }
        item def COTSSnapshot :> EngineeringArtifact {
            ref item records : COTSRecord [0..*];
            attribute databaseSchemaSnapshotRevisionDigest : String;
            attribute maintainerAndReviewPolicy : String;
        }
        item def COTSChangeProposal :> EngineeringArtifact {
            ref item predecessor : COTSSnapshot;
            ref item maintainerDecision : BoundaryViews::EngineeringDecision;
            ref item currentContext : BoundaryViews::ContextRevision;
            ref item proposedRecords : COTSRecord [0..*];
            attribute authorizedMaintainerDecisionAndExactContext : String;
            attribute changeRationaleSourcesAndAffectedSubjects : String;
        }
        item def COTSChangeOutcome :> EngineeringArtifact {
            ref item proposal : COTSChangeProposal;
            ref item retainedPredecessor : COTSSnapshot;
            ref item successor : COTSSnapshot [0..1];
            attribute admittedRejectedStaleInterruptedFailure : String;
            attribute findingsRawSubmissionAndImpactReferences : String;
        }
        action def CheckCOTSChange {
            in proposal : COTSChangeProposal;
            out attribute authorizedCurrentSourcedCompatible : Boolean;
            doc /* Check exact current predecessor, authorized maintainer decision, source dates/revisions, identity/schema, quantity kinds/units and declared validity. Preserve unresolved values and affected design/recommendation dependencies. */
        }
        action def CreateCOTSSuccessor {
            in proposal : COTSChangeProposal;
            out outcome : COTSChangeOutcome;
            bind outcome.proposal = proposal;
            bind outcome.retainedPredecessor = proposal.predecessor;
            doc /* Create a distinct snapshot only on the admitted path. Retain exact source records and dependency impact. Notify configuration control so affected design/advice is invalidated before current use. */
        }
        action def PreserveCOTSPredecessor {
            in proposal : COTSChangeProposal;
            out outcome : COTSChangeOutcome;
            bind outcome.proposal = proposal;
            bind outcome.retainedPredecessor = proposal.predecessor;
            doc /* Rejected, stale, interrupted or unauthorized changes preserve the predecessor and raw proposal. No successor is registered. */
        }
        action def MaintainCOTSDatabase {
            in proposal : COTSChangeProposal;
            out outcome : COTSChangeOutcome;
            perform action check : CheckCOTSChange;
            perform action successor : CreateCOTSSuccessor;
            perform action preserve : PreserveCOTSPredecessor;
            first start then check;
            first check if check.authorizedCurrentSourcedCompatible then successor;
            first check if not check.authorizedCurrentSourcedCompatible then preserve;
            first successor then done;
            first preserve then done;
            bind check.proposal = proposal;
            bind successor.proposal = proposal;
            bind preserve.proposal = proposal;
            flow admittedChange of COTSChangeOutcome from successor.outcome to outcome;
            flow preservedChange of COTSChangeOutcome from preserve.outcome to outcome;
        }
        action def ResolveCOTSSnapshot {
            in attribute requestedExactSnapshotRevision : String;
            out databaseSnapshot : COTSSnapshot [0..1];
            out attribute sourceCurrencyCompatibilityAndMissingData : String;
            doc /* Resolve the exact maintained database revision, not a silently substituted latest record. Missing/unavailable snapshots remain explicit and block calculations requiring their fields. */
        }
        part def MaintainedCOTSDatabase {
            ref item databaseSnapshots : COTSSnapshot [0..*];
            perform action maintain : MaintainCOTSDatabase;
            perform action resolve : ResolveCOTSSnapshot;
            attribute status : String = "proposed/unexecuted";
        }

        part def GenerationModel {
            attribute deliveredMeanPower : PowerValue;
            attribute mass : MassValue;
            attribute occupiedVolume : VolumeValue;
            ref item componentRecords : COTSRecord [0..*];
        }
        part def StorageModel {
            attribute nominalEnergy : EnergyValue;
            attribute usableFraction : Real;
            attribute dischargeEfficiency : Real;
            attribute chargeEfficiency : Real;
            attribute mass : MassValue;
            attribute occupiedVolume : VolumeValue;
            ref item componentRecords : COTSRecord [0..*];
        }
        part def DistributionModel {
            attribute minimumBusVoltage : ElectricPotentialValue;
            attribute maximumBusVoltage : ElectricPotentialValue;
            attribute distributionEfficiency : Real;
            attribute mass : MassValue;
            attribute occupiedVolume : VolumeValue;
            ref item componentRecords : COTSRecord [0..*];
        }
        part def EPSSubject {
            part generation : GenerationModel;
            part storage : StorageModel;
            part distribution : DistributionModel;
            attribute modeledAvailableEnergy : EnergyValue;
            attribute modeledEPSMass : MassValue;
            attribute modeledEPSVolume : VolumeValue;
            attribute nativeDesignScenarioAndSourceRevisions : String;
            doc /* CSRM-informed modeled EPS subject with generation, storage and distribution. All properties are symbolic until sourced mission/component inputs are admitted. This is an engineering model, not executing EPS hardware. */
        }
        item def MissionSizingInputs :> EngineeringArtifact {
            attribute missionScenarioModeAndRequirementsRevisions : String;
            attribute wholeSpacecraftLoadHistoryAndValidity : String;
            attribute meanLoadPower : PowerValue;
            attribute eclipseDuration : DurationValue;
            attribute cycleDuration : DurationValue;
            attribute sunlitDuration : DurationValue;
            attribute reserveEnergy : EnergyValue;
            attribute allocatedEPSMass : MassValue;
            attribute allocatedEPSVolume : VolumeValue;
            attribute requiredBusMinimum : ElectricPotentialValue;
            attribute requiredBusMaximum : ElectricPotentialValue;
            attribute applicableScenarioAndIndependentBasis : Boolean;
            doc /* Mission-tailored inputs and product allocations remain unset. Mean-power interval sizing is a bounded preliminary model. Off-nominal loads, dynamics, illumination, aging, thermal and applicable EMC/RAM effects need separately declared models and evidence. */
        }
        item def NativeSizingInputs :> EngineeringArtifact {
            ref item mission : MissionSizingInputs;
            ref item cots : COTSSnapshot;
            ref item generationSources : COTSRecord [0..*];
            ref item storageSources : COTSRecord [0..*];
            ref item distributionSources : COTSRecord [0..*];
            attribute usableStorageFraction : Real;
            attribute dischargeEfficiency : Real;
            attribute chargeEfficiency : Real;
            attribute distributionEfficiency : Real;
            attribute selectedNominalStorageEnergy : EnergyValue;
            attribute selectedDeliveredGenerationPower : PowerValue;
            attribute generationMass : MassValue;
            attribute storageMass : MassValue;
            attribute distributionMass : MassValue;
            attribute generationVolume : VolumeValue;
            attribute storageVolume : VolumeValue;
            attribute distributionVolume : VolumeValue;
            attribute equationsAssumptionsBindingsAndSourceRevisions : String;
        }
        action def MapNativeSizingInputs {
            in mission : MissionSizingInputs;
            in eps : EPSSubject;
            in database : COTSSnapshot [0..1];
            out mapped : NativeSizingInputs [0..1];
            out attribute sourceInputsCompleteApplicable : Boolean;
            out attribute sourceMappingAndMissingDataFindings : String;
            bind mapped.mission = mission;
            bind mapped.cots = database;
            bind mapped.generationSources = eps.generation.componentRecords;
            bind mapped.storageSources = eps.storage.componentRecords;
            bind mapped.distributionSources = eps.distribution.componentRecords;
            bind mapped.selectedDeliveredGenerationPower = eps.generation.deliveredMeanPower;
            bind mapped.selectedNominalStorageEnergy = eps.storage.nominalEnergy;
            bind mapped.usableStorageFraction = eps.storage.usableFraction;
            bind mapped.dischargeEfficiency = eps.storage.dischargeEfficiency;
            bind mapped.chargeEfficiency = eps.storage.chargeEfficiency;
            bind mapped.distributionEfficiency = eps.distribution.distributionEfficiency;
            bind mapped.generationMass = eps.generation.mass;
            bind mapped.storageMass = eps.storage.mass;
            bind mapped.distributionMass = eps.distribution.mass;
            bind mapped.generationVolume = eps.generation.occupiedVolume;
            bind mapped.storageVolume = eps.storage.occupiedVolume;
            bind mapped.distributionVolume = eps.distribution.occupiedVolume;
            doc /* Check that every selected source record belongs to the exact resolved COTS snapshot and supports the declared design quantities. Retain datasheet-to-design transformations, derating/aggregation, revisions, uncertainty and unknowns. An unavailable snapshot, missing required property or incompatible source yields findings and no complete mapped input. This action proposes no component selection or design change. */
        }
        action def PrepareSourcedNativeSizing {
            in mission : MissionSizingInputs;
            in eps : EPSSubject;
            in attribute requestedExactCOTSRevision : String;
            out mapped : NativeSizingInputs [0..1];
            out attribute sourceInputsCompleteApplicable : Boolean;
            perform action resolve : ResolveCOTSSnapshot;
            perform action map : MapNativeSizingInputs;
            first start then resolve;
            first resolve then map;
            first map then done;
            bind resolve.requestedExactSnapshotRevision = requestedExactCOTSRevision;
            bind map.mission = mission;
            bind map.eps = eps;
            bind map.database = resolve.databaseSnapshot;
            bind mapped = map.mapped;
            bind sourceInputsCompleteApplicable = map.sourceInputsCompleteApplicable;
        }
        item def NativeSizingResults :> EngineeringArtifact {
            attribute eclipseLoadEnergy : EnergyValue;
            attribute cycleLoadEnergy : EnergyValue;
            attribute minimumNominalStorageEnergy : EnergyValue;
            attribute minimumDeliveredGenerationPower : PowerValue;
            attribute generatedCycleEnergy : EnergyValue;
            attribute usableStorageEnergy : EnergyValue;
            attribute storageCycleLosses : EnergyValue;
            attribute cycleEnergyBalance : EnergyValue;
            attribute modeledEPSMass : MassValue;
            attribute modeledEPSVolume : VolumeValue;
            attribute equationInputToolDependencyAndResultRevisions : String;
            doc /* Declared numerical outputs only. Their existence in a type supplies no values, predictive validity, product conformity or completed execution. */
        }
        constraint def SizingInputDomain {
            in inputs : NativeSizingInputs;
            inputs.mission.eclipseDuration >= 0[s] and
            inputs.mission.cycleDuration > 0[s] and
            inputs.mission.sunlitDuration > 0[s] and
            inputs.mission.sunlitDuration <= inputs.mission.cycleDuration and
            inputs.mission.eclipseDuration <= inputs.mission.cycleDuration and
            inputs.mission.meanLoadPower >= 0[W] and
            inputs.mission.reserveEnergy >= 0[J] and
            inputs.selectedNominalStorageEnergy >= 0[J] and
            inputs.selectedDeliveredGenerationPower >= 0[W] and
            inputs.generationMass >= 0[kg] and inputs.storageMass >= 0[kg] and inputs.distributionMass >= 0[kg] and
            inputs.generationVolume >= 0[m^3] and inputs.storageVolume >= 0[m^3] and inputs.distributionVolume >= 0[m^3] and
            inputs.usableStorageFraction > 0 and inputs.usableStorageFraction <= 1 and
            inputs.dischargeEfficiency > 0 and inputs.dischargeEfficiency <= 1 and
            inputs.chargeEfficiency > 0 and inputs.chargeEfficiency <= 1 and
            inputs.distributionEfficiency > 0 and inputs.distributionEfficiency <= 1
        }
        calc def IntervalEnergy {
            in attribute meanPower : PowerValue;
            in attribute duration : DurationValue;
            return attribute energy : EnergyValue = meanPower * duration;
        }
        calc def BatteryEnergySizing {
            in attribute loadEnergy : EnergyValue;
            in attribute reserveEnergy : EnergyValue;
            in attribute usableFraction : Real;
            in attribute dischargeEfficiency : Real;
            in attribute distributionEfficiency : Real;
            return attribute nominalEnergy : EnergyValue =
                (loadEnergy + reserveEnergy) / (usableFraction * dischargeEfficiency * distributionEfficiency);
        }
        calc def StorageCycleLosses {
            in attribute eclipseLoadEnergy : EnergyValue;
            in attribute chargeEfficiency : Real;
            in attribute dischargeEfficiency : Real;
            return attribute lossesAtLoadBoundary : EnergyValue = eclipseLoadEnergy * (1 / (chargeEfficiency * dischargeEfficiency) - 1);
        }
        calc def GenerationPowerSizing {
            in attribute cycleLoadEnergy : EnergyValue;
            in attribute storageLosses : EnergyValue;
            in attribute sunlitDuration : DurationValue;
            in attribute distributionEfficiency : Real;
            return attribute deliveredPower : PowerValue = (cycleLoadEnergy + storageLosses) / (sunlitDuration * distributionEfficiency);
            doc /* Preliminary cyclic replacement sizing includes eclipse charge/discharge losses. Reserve remains a capacity allocation. Constant declared efficiencies and interval means omit dynamic, aging and thermal effects. */
        }
        calc def UsableStoredEnergy {
            in attribute nominalEnergy : EnergyValue;
            in attribute usableFraction : Real;
            in attribute dischargeEfficiency : Real;
            in attribute distributionEfficiency : Real;
            return attribute energy : EnergyValue = nominalEnergy * usableFraction * dischargeEfficiency * distributionEfficiency;
        }
        calc def EPSMassRollup {
            in attribute generation : MassValue;
            in attribute storage : MassValue;
            in attribute distribution : MassValue;
            return attribute mass : MassValue = generation + storage + distribution;
        }
        calc def EPSVolumeRollup {
            in attribute generation : VolumeValue;
            in attribute storage : VolumeValue;
            in attribute distribution : VolumeValue;
            return attribute volume : VolumeValue = generation + storage + distribution;
            doc /* Sum declared occupied volumes for a technical estimate. Geometric accommodation, clearances and overlap require a separate checked model. */
        }
        calc def NativeEnergySizing {
            in inputs : NativeSizingInputs;
            return results : NativeSizingResults;
            calc eclipse : IntervalEnergy {
                in :>> meanPower = inputs.mission.meanLoadPower;
                in :>> duration = inputs.mission.eclipseDuration;
            }
            calc cycle : IntervalEnergy {
                in :>> meanPower = inputs.mission.meanLoadPower;
                in :>> duration = inputs.mission.cycleDuration;
            }
            calc battery : BatteryEnergySizing {
                in :>> loadEnergy = eclipse.energy;
                in :>> reserveEnergy = inputs.mission.reserveEnergy;
                in :>> usableFraction = inputs.usableStorageFraction;
                in :>> dischargeEfficiency = inputs.dischargeEfficiency;
                in :>> distributionEfficiency = inputs.distributionEfficiency;
            }
            calc storageLosses : StorageCycleLosses {
                in :>> eclipseLoadEnergy = eclipse.energy;
                in :>> chargeEfficiency = inputs.chargeEfficiency;
                in :>> dischargeEfficiency = inputs.dischargeEfficiency;
            }
            calc generation : GenerationPowerSizing {
                in :>> cycleLoadEnergy = cycle.energy;
                in :>> storageLosses = NativeEnergySizing::storageLosses.lossesAtLoadBoundary;
                in :>> sunlitDuration = inputs.mission.sunlitDuration;
                in :>> distributionEfficiency = inputs.distributionEfficiency;
            }
            calc generated : IntervalEnergy {
                in :>> meanPower = inputs.selectedDeliveredGenerationPower;
                in :>> duration = inputs.mission.sunlitDuration;
            }
            calc stored : UsableStoredEnergy {
                in :>> nominalEnergy = inputs.selectedNominalStorageEnergy;
                in :>> usableFraction = inputs.usableStorageFraction;
                in :>> dischargeEfficiency = inputs.dischargeEfficiency;
                in :>> distributionEfficiency = inputs.distributionEfficiency;
            }
            calc mass : EPSMassRollup {
                in :>> generation = inputs.generationMass;
                in :>> storage = inputs.storageMass;
                in :>> distribution = inputs.distributionMass;
            }
            calc volume : EPSVolumeRollup {
                in :>> generation = inputs.generationVolume;
                in :>> storage = inputs.storageVolume;
                in :>> distribution = inputs.distributionVolume;
            }
            bind results.eclipseLoadEnergy = eclipse.energy;
            bind results.cycleLoadEnergy = cycle.energy;
            bind results.minimumNominalStorageEnergy = battery.nominalEnergy;
            bind results.minimumDeliveredGenerationPower = generation.deliveredPower;
            bind results.generatedCycleEnergy = generated.energy;
            bind results.usableStorageEnergy = stored.energy;
            bind results.modeledEPSMass = mass.mass;
            bind results.modeledEPSVolume = volume.volume;
            bind results.storageCycleLosses = storageLosses.lossesAtLoadBoundary;
            attribute balance : EnergyValue = generated.energy * inputs.distributionEfficiency - cycle.energy - storageLosses.lossesAtLoadBoundary;
            bind results.cycleEnergyBalance = balance;
            doc /* Native equation and parameter-binding contract for a proposed Python implementation. A scalar preliminary sizing calculation does not replace time-dependent EPS simulation, model credibility assessment or independent requirement verification. */
        }

        requirement def <'CDT-EPS-R01'> EclipseEnergyProvision {
            subject eps : EPSSubject;
            in sizingInputs : NativeSizingInputs;
            attribute requiredLoadAndReserveEnergy : EnergyValue;
            attribute applicableScenario : Boolean;
            assume constraint scenarioApplicable { applicableScenario }
            assume constraint admittedInputDomain : SizingInputDomain { in :>> inputs = sizingInputs; }
            assume constraint nonnegativeDemand { requiredLoadAndReserveEnergy >= 0[J] }
            require constraint energyProvision { eps.modeledAvailableEnergy >= requiredLoadAndReserveEnergy }
            doc /* Under the declared mission scenario and admitted model assumptions, the modeled EPS shall provide the allocated eclipse load and reserve energy. Requirement evaluation requires suitable current evidence and remains separate from calculation completion. */
        }
        requirement def <'CDT-EPS-R02'> EPSMassAllocation {
            subject eps : EPSSubject;
            attribute maximumMass : MassValue;
            assume constraint validAllocation { maximumMass > 0[kg] }
            require constraint massAllocation { eps.modeledEPSMass <= maximumMass }
            doc /* The modeled EPS mass shall remain within its mission allocation. No allocation value is supplied by the reference model. */
        }
        requirement def <'CDT-EPS-R03'> EPSVolumeAllocation {
            subject eps : EPSSubject;
            attribute maximumVolume : VolumeValue;
            assume constraint validAllocation { maximumVolume > 0[m^3] }
            require constraint volumeAllocation { eps.modeledEPSVolume <= maximumVolume }
            doc /* The modeled occupied EPS volume shall remain within its mission allocation. Geometric fit is independently assessed. */
        }
        requirement def <'CDT-EPS-R04'> EPSBusVoltage {
            subject eps : EPSSubject;
            attribute requiredMinimum : ElectricPotentialValue;
            attribute requiredMaximum : ElectricPotentialValue;
            attribute applicableScenario : Boolean;
            assume constraint scenarioApplicable { applicableScenario }
            assume constraint validRange { requiredMinimum <= requiredMaximum }
            require constraint lowerBound { eps.distribution.minimumBusVoltage >= requiredMinimum }
            require constraint upperBound { eps.distribution.maximumBusVoltage <= requiredMaximum }
            doc /* For the admitted mission scenario and declared dynamic-model scope, the EPS bus voltage shall remain within its allocated range. The preliminary energy equations do not calculate or verify bus extrema. */
        }
        part def MissionTailoredEPSModel {
            part eps : EPSSubject;
            ref item inputs : NativeSizingInputs;
            ref item independentBusAssessment : EngineeringArtifact [0..1];
            calc sizing : NativeEnergySizing { in :>> inputs = MissionTailoredEPSModel::inputs; }
            constraint inputDomain : SizingInputDomain { in :>> inputs = MissionTailoredEPSModel::inputs; }
            requirement eclipseEnergy : EclipseEnergyProvision {
                subject :>> eps = MissionTailoredEPSModel::eps;
                in :>> sizingInputs = MissionTailoredEPSModel::inputs;
                attribute :>> requiredLoadAndReserveEnergy = sizing.results.eclipseLoadEnergy + inputs.mission.reserveEnergy;
                attribute :>> applicableScenario = inputs.mission.applicableScenarioAndIndependentBasis;
            }
            requirement massAllocation : EPSMassAllocation {
                subject :>> eps = MissionTailoredEPSModel::eps;
                attribute :>> maximumMass = inputs.mission.allocatedEPSMass;
            }
            requirement volumeAllocation : EPSVolumeAllocation {
                subject :>> eps = MissionTailoredEPSModel::eps;
                attribute :>> maximumVolume = inputs.mission.allocatedEPSVolume;
            }
            requirement busRange : EPSBusVoltage {
                subject :>> eps = MissionTailoredEPSModel::eps;
                attribute :>> requiredMinimum = inputs.mission.requiredBusMinimum;
                attribute :>> requiredMaximum = inputs.mission.requiredBusMaximum;
                attribute :>> applicableScenario = inputs.mission.applicableScenarioAndIndependentBasis;
            }
            bind eps.modeledAvailableEnergy = sizing.results.usableStorageEnergy;
            bind eps.modeledEPSMass = sizing.results.modeledEPSMass;
            bind eps.modeledEPSVolume = sizing.results.modeledEPSVolume;
            bind eps.generation.deliveredMeanPower = inputs.selectedDeliveredGenerationPower;
            bind eps.storage.nominalEnergy = inputs.selectedNominalStorageEnergy;
            bind eps.storage.usableFraction = inputs.usableStorageFraction;
            bind eps.storage.dischargeEfficiency = inputs.dischargeEfficiency;
            bind eps.storage.chargeEfficiency = inputs.chargeEfficiency;
            bind eps.generation.componentRecords = inputs.generationSources;
            bind eps.storage.componentRecords = inputs.storageSources;
            bind eps.distribution.componentRecords = inputs.distributionSources;
            bind eps.distribution.distributionEfficiency = inputs.distributionEfficiency;
            bind eps.generation.mass = inputs.generationMass;
            bind eps.storage.mass = inputs.storageMass;
            bind eps.distribution.mass = inputs.distributionMass;
            bind eps.generation.occupiedVolume = inputs.generationVolume;
            bind eps.storage.occupiedVolume = inputs.storageVolume;
            bind eps.distribution.occupiedVolume = inputs.distributionVolume;
            doc /* Reusable mission-tailored native template with requirements bound to its real EPS subject, allocations and parametric outputs. Input-domain constraints are declared, not asserted as established results. Mission allocations, bus evidence and component values remain unset. */
        }
        @SourceRecord about MissionTailoredEPSModel {
            identifier = "PA-CDT-native-EPS-enrichment";
            sourceText = "Mission-tailored CSRM architecture and requirement/V&V patterns enriched with proposed quantity-typed EPS requirements and power/energy/mass/volume parametrics. The cited reference baseline lacks added power/weight parametrics.";
            sourceLocator = "Kaslow 2019 PDF pages 2, 5-6. Proposed equation contracts informed by GREATCUBE+ EPS sizing and Boan mode/energy workflows.";
            citationRecord = "kaslow2019csrm, review-0711, review-0289";
            status = "proposed/unexecuted";
        }

        item def IndependentEPSAssessment :> EngineeringArtifact {
            ref part subjectModel : MissionTailoredEPSModel;
            ref item sizingResult : NativeSizingResults [0..1];
            ref item independentReference : EngineeringArtifact [0..*];
            attribute requirementsScenariosCriteriaAndExactRevisions : String;
            attribute dataIdentityUnitsTimingValidityMasks : String;
            attribute calibrationIndependentDataSeparationAndGaps : String;
            attribute credibilityApplicabilityUncertaintyAndProductFindings : String;
            doc /* Separate planned assessment record. A calculation or replay outcome is not an independent reference or a requirement verdict. Missing independent evidence and critical validity gaps remain explicit. */
        }
        action def PlanIndependentEPSAssessment {
            in modelContext : NativeSizingInputs;
            in sizingResult : NativeSizingResults [0..1];
            in referenceEvidence : EngineeringArtifact [0..*];
            out assessmentPlan : IndependentEPSAssessment;
            bind assessmentPlan.sizingResult = sizingResult;
            bind assessmentPlan.independentReference = referenceEvidence;
        }
        item def PythonSizingOutcome :> EngineeringArtifact {
            ref item inputs : NativeSizingInputs;
            ref item results : NativeSizingResults [0..1];
            attribute successFailureCancelledPartialAndLimits : String;
            attribute pythonEnvironmentSolverDependencyLogs : String;
            doc /* Failed, cancelled and partial executions may retain no numerical results. Preserve actual statuses and exact inputs/dependencies for independent replay. */
        }
        action def AdmitNativeSizing {
            in inputs : NativeSizingInputs;
            in decision : EngineerMethodDisposition [0..1];
            out attribute currentSourcedDomainValidApplicable : Boolean;
            constraint domain : SizingInputDomain { in :>> inputs = AdmitNativeSizing::inputs; }
            doc /* Check current native/mission/COTS revisions, sourced quantities, domain predicate, method applicability, declared mandatory effects and resources. An engineer can request an applicable analysis directly without a recommendation. If a suggestion is used, its actual current engineer disposition is checked separately. Missing inputs or mandatory model effects block the affected run. */
        }
        action def ExecutePythonSizing {
            in inputs : NativeSizingInputs;
            out outcome : PythonSizingOutcome;
            bind outcome.inputs = inputs;
            doc /* Proposed Python implementation executes or orchestrates the native equation contract and applicable specialist analyses. Preserve actual configuration, results, logs and failure/partial/cancelled statuses. Numerical completion establishes neither independent model credibility nor EPS conformity. */
        }
        action def BlockNativeSizing {
            in inputs : NativeSizingInputs;
            out outcome : PythonSizingOutcome;
            bind outcome.inputs = inputs;
            doc /* Retain missing-data, stale, domain, applicability or unsupported-effect findings without fabricating results or changing the design. */
        }
        action def CoordinateNativeSizing {
            in inputs : NativeSizingInputs;
            in decision : EngineerMethodDisposition [0..1];
            out outcome : PythonSizingOutcome;
            perform action admission : AdmitNativeSizing;
            perform action execute : ExecutePythonSizing;
            perform action blocked : BlockNativeSizing;
            first start then admission;
            first admission if admission.currentSourcedDomainValidApplicable then execute;
            first admission if not admission.currentSourcedDomainValidApplicable then blocked;
            first execute then done;
            first blocked then done;
            bind admission.inputs = inputs;
            bind admission.decision = decision;
            bind execute.inputs = inputs;
            bind blocked.inputs = inputs;
            flow completed of PythonSizingOutcome from execute.outcome to outcome;
            flow blockedOutcome of PythonSizingOutcome from blocked.outcome to outcome;
        }
        part def NativeEPSAnalysisResources {
            ref part cots : MaintainedCOTSDatabase;
            ref part methods : RequiredJevRecommendations;
            ref part platforms : RequiredPlatformConnections;
            perform action prepareInputs : PrepareSourcedNativeSizing {
                perform action :>> resolve references cots.resolve;
            }
            perform action sizeEPS : CoordinateNativeSizing;
            perform action planIndependentAssessment : PlanIndependentEPSAssessment;
            attribute status : String = "proposed/unexecuted";
        }
        dependency nativeEquations from ExecutePythonSizing to NativeEnergySizing;
        dependency sourcedSizingInputs from AdmitNativeSizing to ResolveCOTSSnapshot;
        dependency separateApplicabilityDecision from AdmitNativeSizing to EngineerMethodDisposition;
        dependency methodNativeContext from MethodContext to MissionTailoredEPSModel;
        dependency componentMaintenance from NativeSizingInputs to MaintainedCOTSDatabase;
        dependency independentProductAssessment from MissionTailoredEPSModel to PlanIndependentEPSAssessment;
        dependency energyVerificationPlan from EclipseEnergyProvision to PlanIndependentEPSAssessment;
        dependency massVerificationPlan from EPSMassAllocation to PlanIndependentEPSAssessment;
        dependency volumeVerificationPlan from EPSVolumeAllocation to PlanIndependentEPSAssessment;
        dependency voltageVerificationPlan from EPSBusVoltage to PlanIndependentEPSAssessment;
    }

    item def NativeEPSContextRecord :> EngineeringArtifact {
        ref part nativeModel : NativeEPS::MissionTailoredEPSModel;
        ref item inputs : NativeEPS::NativeSizingInputs;
        ref requirement energyRequirement : NativeEPS::EclipseEnergyProvision;
        ref requirement massRequirement : NativeEPS::EPSMassAllocation;
        ref requirement volumeRequirement : NativeEPS::EPSVolumeAllocation;
        ref requirement voltageRequirement : NativeEPS::EPSBusVoltage;
        attribute sourceScenarioRequirementCalculationAndBindingRevisions : String;
    }
    action def MapNativeMethodContext {
        in work : AssistanceWork;
        in authoring : NativeAuthoringProfile;
        in nativeModel : NativeEPS::MissionTailoredEPSModel;
        out context : IntegrationScaffold::MethodContext;
        out methods : IntegrationScaffold::EngineeringMethod [0..*];
        ref item nativeContext : NativeEPSContextRecord;
        bind context.contextRevision = work.request.context;
        bind nativeContext.nativeModel = nativeModel;
        bind nativeContext.inputs = nativeModel.inputs;
        bind nativeContext.energyRequirement = nativeModel.eclipseEnergy;
        bind nativeContext.massRequirement = nativeModel.massAllocation;
        bind nativeContext.volumeRequirement = nativeModel.volumeAllocation;
        bind nativeContext.voltageRequirement = nativeModel.busRange;
        bind context.nativeSubjectsAndInputs = nativeContext;
        bind methods = authoring.sourcedMethods;
        doc /* Pass native requirements, subjects, assumptions, quantity properties, calculation/binding revisions, actual mission/COTS inputs and intended use to Jev method classification. Native drafting/semantic checks remain a separate service. Missing inputs and scope limits remain explicit. */
    }
    action def ReturnJevMethodReport {
        in work : AssistanceWork;
        in recommendations : IntegrationScaffold::MethodRecommendations;
        out report : AssistanceReport;
        bind report.context = work.request.context;
        bind report.findings = work.findings;
        doc /* Map actual eligible analysis/V&V suggestions and their prerequisite/source/applicability explanations into MethodRecommendation records. Retain classifier/rubric identities and unavailable, no-eligible, abstained or stale status. An engineer checks applicability and acceptance separately. A classifier score is no independent requirement check, analysis execution, evidence or application authorization. */
    }
    action def NativeRecommendMethods :> RecommendMethods {
        ref part authoring : NativeAuthoringProfile;
        ref part nativeModel : NativeEPS::MissionTailoredEPSModel;
        ref part jev : IntegrationScaffold::RequiredJevRecommendations;
        perform action map : MapNativeMethodContext;
        perform action classify : IntegrationScaffold::JevMethodRecommendations references jev.recommendMethods;
        perform action returnReport : ReturnJevMethodReport;
        first start then map;
        first map then classify;
        first classify then returnReport;
        first returnReport then done;
        bind map.work = work;
        bind map.authoring = authoring;
        bind map.nativeModel = nativeModel;
        bind classify.context = map.context;
        bind classify.methods = map.methods;
        bind returnReport.work = work;
        bind returnReport.recommendations = classify.recommendations;
        bind report = returnReport.report;
    }
    item def NativeDesignWork :> DesignWork {
        ref item nativeSizingOutcome : NativeEPS::PythonSizingOutcome;
    }
    item def NativeDesignStudy :> DesignStudy {
        ref item sizingOutcome : NativeEPS::PythonSizingOutcome;
        ref item nativeQuantities : NativeEPS::NativeSizingResults [0..1];
        ref item predecessorStudy : DesignStudy [0..1];
        attribute scopedSizingStatusAssumptionsAndMissingEffects : String;
    }
    action def MapNativeResultQuantities {
        in outcome : NativeEPS::PythonSizingOutcome;
        out quantities : BoundaryViews::Quantity [0..*];
        doc /* Map present ISQ energy/power/mass/volume results to declared quantity kinds, units and revisions using checked dimensional conversion. Preserve uncertainty and missing-result reasons. No quantity value is fabricated for blocked, failed, cancelled or partial execution. A mapped result is not independent evidence or an EPS verdict. */
    }
    action def ReturnNativeDesignWork {
        in original : DesignWork;
        in outcome : NativeEPS::PythonSizingOutcome;
        out updated : NativeDesignWork;
        ref item proposedStudy : NativeDesignStudy;
        perform action mapQuantities : MapNativeResultQuantities;
        first start then mapQuantities;
        first mapQuantities then done;
        bind mapQuantities.outcome = outcome;
        bind updated.configuration = original.configuration;
        bind updated.specification = original.specification;
        bind updated.authorizations = original.authorizations;
        bind proposedStudy.configuration = original.configuration;
        bind proposedStudy.sizingOutcome = outcome;
        bind proposedStudy.nativeQuantities = outcome.results;
        bind proposedStudy.predecessorStudy = original.study;
        bind proposedStudy.quantities = mapQuantities.quantities;
        bind updated.study = proposedStudy;
        bind updated.nativeSizingOutcome = outcome;
        doc /* Retain current design and a distinct proposed sizing study with the actual optional results/status. Preserve the predecessor separately. Expose sourced budget/sizing and technical mass/volume quantities only when corresponding data exists. This operation neither applies a design change nor declares product conformity. */
    }
    action def NativeBudgetSize :> BudgetSize {
        ref part nativeModel : NativeEPS::MissionTailoredEPSModel;
        ref part resources : NativeEPS::NativeEPSAnalysisResources;
        perform action prepare : NativeEPS::PrepareSourcedNativeSizing references resources.prepareInputs;
        perform action calculate : NativeEPS::CoordinateNativeSizing references resources.sizeEPS;
        perform action blocked : NativeEPS::BlockNativeSizing;
        perform action retain : ReturnNativeDesignWork;
        first start then prepare;
        first prepare if prepare.sourceInputsCompleteApplicable then calculate;
        first prepare if not prepare.sourceInputsCompleteApplicable then blocked;
        first calculate then retain;
        first blocked then retain;
        first retain then done;
        bind prepare.mission = nativeModel.inputs.mission;
        bind prepare.eps = nativeModel.eps;
        bind prepare.requestedExactCOTSRevision = nativeModel.inputs.cots.databaseSchemaSnapshotRevisionDigest;
        bind calculate.inputs = prepare.mapped;
        bind blocked.inputs = nativeModel.inputs;
        bind retain.original = work;
        flow sizedOutcome of NativeEPS::PythonSizingOutcome from calculate.outcome to retain.outcome;
        flow blockedOutcome of NativeEPS::PythonSizingOutcome from blocked.outcome to retain.outcome;
        bind updatedWork = retain.updated;
    }
    item def NativeAnalysisPlan :> AnalysisPlan {
        ref item nativeBindings : NativeEPS::NativeSizingInputs [0..1];
        attribute nativeParameterPythonSolverUSDMappingAndAdmissionFindings : String;
    }
    action def NativeBindingsToAnalysisPlan :> MapNumericalPlan {
        ref part nativeModel : NativeEPS::MissionTailoredEPSModel;
        ref part resources : NativeEPS::NativeEPSAnalysisResources;
        out mapped : NativeAnalysisPlan :>> MapNumericalPlan::mapped;
        perform action prepare : NativeEPS::PrepareSourcedNativeSizing references resources.prepareInputs;
        first start then prepare;
        first prepare then done;
        bind prepare.mission = nativeModel.inputs.mission;
        bind prepare.eps = nativeModel.eps;
        bind prepare.requestedExactCOTSRevision = nativeModel.inputs.cots.databaseSchemaSnapshotRevisionDigest;
        bind mapped.nativeBindings = prepare.mapped;
        bind mapped.configuration = proposed.configuration;
        bind mapped.couplingProfile = proposed.couplingProfile;
        doc /* Proposed native quantity/parameter bindings feed Python specialist-model plans and USD/entity/time mappings. A missing exact COTS snapshot or unsupported required effect remains an admission finding. Mandatory whole-CUBICS input/EPS response meaning follows the source profile and declared coupling. Preliminary equations do not replace dynamic EPS/thermal/EMC/RAM analyses or independent assessment. */
    }
    action def NativePlanAnalysis :> PhysicalPlanAnalysis {
        ref part nativeModel : NativeEPS::MissionTailoredEPSModel;
        ref part resources : NativeEPS::NativeEPSAnalysisResources;
        perform action :>> map : NativeBindingsToAnalysisPlan {
            bind nativeModel = NativePlanAnalysis::nativeModel;
            bind resources = NativePlanAnalysis::resources;
        }
    }

    part def <'CDT-C01'> C01 :> RequirementsGuidanceSoftware {
        doc /* Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority. */
        part authoring : NativeAuthoringProfile {
            attribute :>> qualityRulesSemanticChecksAndLimitations = "Native requirement fields and Python rules support proposed semantic checks, separate from Jev.";
            attribute :>> recommendationContextAndApplicability = "Native subjects, assumptions, quantities and bindings feed required Jev analysis/V&V suggestions for engineer eligibility checks.";
        }
        ref part nativeModel : NativeEPS::MissionTailoredEPSModel;
        part jev : IntegrationScaffold::RequiredJevRecommendations;
        perform action :>> acknowledge;
        perform action :>> checkDraft : PhysicalCheckDraft {
            bind authoring = C01::authoring;
        }
        perform action :>> recommend : NativeRecommendMethods {
            bind authoring = C01::authoring;
            bind nativeModel = C01::nativeModel;
            bind jev = C01::jev;
        }
        perform action :>> dispose;
        perform action :>> reassess : PhysicalReassessAssistance {
            perform action :>> checkDraft references CandidateCDT::C01::checkDraft;
            perform action :>> recommend references CandidateCDT::C01::recommend;
        }
        perform action :>> retainRequirements;
        perform action :>> deriveAllocate;
        perform action :>> traceLinks;
        perform action :>> presentAdvice;
        perform action :>> sourceQuery;
    }
    @ComponentSpecification about C01 { tools = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; logical = "L01"; sourceMethods = ("L01.Native", "L01.Jev"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C01 { identifier = "CDT-C01"; sourceText = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; sourceLocator = "OOSEM L01 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "kaslow2019csrm, typesafe060"; status = "proposed/unexecuted"; }
    part def <'CDT-C02'> C02 :> MissionDesignSoftware {
        doc /* Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed. */
        part nativeModel : NativeEPS::MissionTailoredEPSModel;
        part cots : NativeEPS::MaintainedCOTSDatabase;
        ref part resources : NativeEPS::NativeEPSAnalysisResources;
        perform action :>> defineDesign;
        perform action :>> budgetSize : NativeBudgetSize {
            bind nativeModel = C02::nativeModel;
            bind resources = C02::resources;
        }
        perform action :>> compareDesigns;
        perform action :>> defineInterfaces;
        perform action :>> configureConcept;
    }
    @ComponentSpecification about C02 { tools = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; logical = "L02"; sourceMethods = ("L02.Parametrics", "L02.Python", "L02.COTS-DB"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C02 { identifier = "CDT-C02"; sourceText = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; sourceLocator = "OOSEM L02 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "kaslow2019csrm, review-0711, review-0289"; status = "proposed/unexecuted"; }
    part def <'CDT-C03'> C03 :> SimulationIntegrationSoftware {
        doc /* Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings. */
        part :>> mapping {
            attribute :>> authoringDesignToPythonPlantUSDOrFMIMappings = "Native quantity/calculation/parameter bindings -> Python specialist EPS/battery analysis -> USD and numerical whole-CUBICS Omniverse mappings.";
            attribute :>> fPrimeInterfaceTranslationPathAndVersions = "Native EPS interface fields -> checked Python semantic mappings -> required versioned F Prime profile.";
            attribute :>> numericalEntityUnitSampleReceiptScenarioTimeChecks = "Check same scenario, entity/channel identity, quantities/units, sample/receipt times, synchronization rules/limits/delays, raw missing/invalid/inactive values and masks.";
            attribute :>> disciplineSolverEffectsAndUnsupportedTransfers = "Required electrical/thermal and applicable EMC/geometry/RAM profiles with supported effects, validity, omissions and independent evidence. Authored failure data to fault trees is a proposed adaptation with unresolved missing rates.";
        }
        part :>> replayDependencies {
            attribute :>> requiredDependencyClasses = "Native baselines, Python/environment/solver versions, exact COTS/source revisions, F Prime host dependencies and raw outputs.";
        }
        ref part nativeModel : NativeEPS::MissionTailoredEPSModel;
        part nativeResources : NativeEPS::NativeEPSAnalysisResources {
            perform action :>> planIndependentAssessment {
                bind modelContext = C03::nativeModel.inputs;
                bind assessmentPlan.subjectModel = C03::nativeModel;
            }
        }
        perform action :>> planAnalysis : NativePlanAnalysis {
            bind profile = C03::mapping;
            bind nativeModel = C03::nativeModel;
            bind resources = C03::nativeResources;
        }
        perform action :>> planMIL;
        perform action :>> coordinateCoding;
        perform action :>> compareMILSil;
        perform action :>> replay;
        perform action :>> planRepeat;
        perform action :>> mapFPrime : PhysicalMapFPrime {
            bind profile = C03::mapping;
        }
    }
    @ComponentSpecification about C03 { tools = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; logical = "L03"; sourceMethods = ("L03.Python", "L03.IN1", "L03.IN2"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C03 { identifier = "CDT-C03"; sourceText = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; sourceLocator = "OOSEM L03 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "review-0853, handpicked-0001"; status = "proposed/unexecuted"; }
    part def <'CDT-C04'> C04 :> ModelCredibilitySoftware {
        doc /* Python assessment using Casado reference-waveform and CSRM model/V&V relationships. Calibration, independent model credibility and EPS conformity remain distinct. */
        part assessmentMethods : CredibilityMethodProfile {
            attribute :>> waveformHistorySeparateModelAndCSRMMethods = "Python Casado reference-waveform assessment plus CSRM model/V&V relationships.";
            attribute :>> applicabilityTimingRawMasksAndIndependentDataRules = "Keep calibration and independent reference use distinct. Check current intended use, units/timing/raw masks and uncertainty. Critical evidence gaps block unqualified claims.";
        }
        perform action :>> assessModel : PhysicalAssessModel {
            bind profile = C04::assessmentMethods;
        }
        perform action :>> proposeCalibration;
        perform action :>> checkReferenceData;
    }
    @ComponentSpecification about C04 { tools = "Python assessment using Casado reference-waveform and CSRM model/V&V relationships. Calibration, independent model credibility and EPS conformity remain distinct."; logical = "L04"; sourceMethods = ("L04.Python", "L04.CR1", "L04.CR5"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C04 { identifier = "CDT-C04"; sourceText = "Python assessment using Casado reference-waveform and CSRM model/V&V relationships. Calibration, independent model credibility and EPS conformity remain distinct."; sourceLocator = "OOSEM L04 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "review-0573, kaslow2019csrm"; status = "proposed/unexecuted"; }
    part def <'CDT-C05'> C05 :> EvidenceReviewSoftware {
        doc /* Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision. */
        part evidenceMethods : EvidenceMethodProfile {
            attribute :>> requirementProcedureVerdictAndPublishedReviewTraces = "Python/native assembly plus requirement/procedure/verdict feedback.";
            attribute :>> exactBaselineAuthorityAndCoverageAssembly = "Exact current baseline and scoped criteria, source-linked evidence and gaps. Preparation is not acceptance. Designated authority retains decisions and renewed closure control.";
        }
        perform action :>> planAssessment;
        perform action :>> assessProduct;
        perform action :>> prepareReview : PhysicalPrepareReviewPackage {
            bind profile = C05::evidenceMethods;
        }
        perform action :>> checkReviewDecision;
        perform action :>> recordReview;
        perform action :>> makeViews;
        perform action :>> presentAssessment;
    }
    @ComponentSpecification about C05 { tools = "Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision."; logical = "L05"; sourceMethods = ("L05.Python", "L05.EC2"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C05 { identifier = "CDT-C05"; sourceText = "Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision."; sourceLocator = "OOSEM L05 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "citation-0569, kaslow2019csrm"; status = "proposed/unexecuted"; }
    part def <'CDT-C06'> C06 :> ConfigurationExchangeSoftware {
        doc /* Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance. */
        part currency : CurrencyProfile {
            attribute :>> affectedRevisionKeysAndInvalidationPolicy = "Native, COTS/source, classifier/rubric and rule revisions invalidate current/pending advice before latest-context reassessment.";
        }
        ref part replayProfile : ReplayProfile;
        ref part numericalMapping : IntegrationMethodProfile;
        ref port numericalEndpoint : AnalysisPort;
        perform action :>> captureContext;
        perform action :>> checkCurrency : PhysicalCheckCurrency {
            bind profile = C06::currency;
        }
        perform action :>> invalidate : PhysicalInvalidateAndReassess {
            bind profile = C06::currency;
        }
        perform action :>> checkChange;
        perform action :>> successor;
        perform action :>> preserveRun : PhysicalPreserveRun {
            bind mapping = C06::numericalMapping;
            bind currency = C06::currency;
            bind numericalEndpoint = C06::numericalEndpoint;
        }
        perform action :>> checkDesignAuthorization;
        perform action :>> retrieveBaseline;
        perform action :>> retainReview;
        perform action :>> prepareReplay : PhysicalPrepareReplay {
            bind profile = C06::replayProfile;
        }
        perform action :>> preserveRecord;
        perform action :>> checkSelection;
        perform action :>> checkResultContext;
        perform action :>> prepareCalibrationChange;
        perform action :>> checkTransfer;
        perform action :>> checkEngineeringTransfer;
        perform action :>> checkSourceTransfer;
    }
    @ComponentSpecification about C06 { tools = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; logical = "L06"; sourceMethods = ("L06.Native", "L06.EC1"); authority = "Engineer application/change/release and designated review authority remain distinct. Profiles and scores confer no approval."; verificationNeed = "All allocated FR checks, exact IO fields, failure/currency/replay paths and source limits require verification."; status = "proposed/unexecuted"; }
    @SourceRecord about C06 { identifier = "CDT-C06"; sourceText = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; sourceLocator = "OOSEM L06 proposed physical synthesis. Cited partial method capabilities and missing completion are stated in this component specification."; citationRecord = "chiu2023sealion, kaslow2019csrm"; status = "proposed/unexecuted"; }
    part def Configuration :> LogicalFramework {
        part :>> L01 : C01 {
            perform action acknowledge : FrameworkLogical::AcknowledgeAssistance :>> C01::acknowledge, FrameworkLogical::RequirementsAssistance::acknowledge;
            perform action checkDraft : PhysicalCheckDraft :>> C01::checkDraft, FrameworkLogical::RequirementsAssistance::checkDraft;
            perform action recommend : NativeRecommendMethods :>> C01::recommend, FrameworkLogical::RequirementsAssistance::recommend;
            perform action dispose : FrameworkLogical::DisposeSuggestion :>> C01::dispose, FrameworkLogical::RequirementsAssistance::dispose;
            perform action reassess : PhysicalReassessAssistance :>> C01::reassess, FrameworkLogical::RequirementsAssistance::reassess;
            perform action retainRequirements : FrameworkLogical::RetainRequirements :>> C01::retainRequirements, FrameworkLogical::RequirementsAssistance::retainRequirements;
            perform action deriveAllocate : FrameworkLogical::DeriveAllocate :>> C01::deriveAllocate, FrameworkLogical::RequirementsAssistance::deriveAllocate;
            perform action traceLinks : FrameworkLogical::TraceLinks :>> C01::traceLinks, FrameworkLogical::RequirementsAssistance::traceLinks;
            perform action presentAdvice : FrameworkLogical::PresentAdvice :>> C01::presentAdvice, FrameworkLogical::RequirementsAssistance::presentAdvice;
            perform action sourceQuery : FrameworkLogical::RequestApplicableSource :>> C01::sourceQuery, FrameworkLogical::RequirementsAssistance::sourceQuery;
        }
        part :>> L02 : C02 {
            perform action defineDesign : FrameworkLogical::DefineDesign :>> C02::defineDesign, FrameworkLogical::MissionDesign::defineDesign;
            perform action budgetSize : NativeBudgetSize :>> C02::budgetSize, FrameworkLogical::MissionDesign::budgetSize;
            perform action compareDesigns : FrameworkLogical::CompareDesigns :>> C02::compareDesigns, FrameworkLogical::MissionDesign::compareDesigns;
            perform action defineInterfaces : FrameworkLogical::DefineInterfaces :>> C02::defineInterfaces, FrameworkLogical::MissionDesign::defineInterfaces;
            perform action configureConcept : FrameworkLogical::ConfigureConcept :>> C02::configureConcept, FrameworkLogical::MissionDesign::configureConcept;
        }
        part :>> L03 : C03 {
            perform action planAnalysis : NativePlanAnalysis :>> C03::planAnalysis, FrameworkLogical::SimulationIntegration::planAnalysis;
            perform action planMIL : FrameworkLogical::PlanMIL :>> C03::planMIL, FrameworkLogical::SimulationIntegration::planMIL;
            perform action coordinateCoding : FrameworkLogical::CoordinateCoding :>> C03::coordinateCoding, FrameworkLogical::SimulationIntegration::coordinateCoding;
            perform action compareMILSil : FrameworkLogical::CompareMILSil :>> C03::compareMILSil, FrameworkLogical::SimulationIntegration::compareMILSil;
            perform action replay : FrameworkLogical::ReplayRun :>> C03::replay, FrameworkLogical::SimulationIntegration::replay;
            perform action planRepeat : FrameworkLogical::PlanRepeatedAssessment :>> C03::planRepeat, FrameworkLogical::SimulationIntegration::planRepeat;
            perform action mapFPrime : PhysicalMapFPrime :>> C03::mapFPrime, FrameworkLogical::SimulationIntegration::mapFPrime;
        }
        part :>> L04 : C04 {
            perform action assessModel : PhysicalAssessModel :>> C04::assessModel, FrameworkLogical::ModelCredibility::assessModel;
            perform action proposeCalibration : FrameworkLogical::ProposeCalibration :>> C04::proposeCalibration, FrameworkLogical::ModelCredibility::proposeCalibration;
            perform action checkReferenceData : FrameworkLogical::CheckReferenceData :>> C04::checkReferenceData, FrameworkLogical::ModelCredibility::checkReferenceData;
        }
        part :>> L05 : C05 {
            perform action planAssessment : FrameworkLogical::PlanAssessment :>> C05::planAssessment, FrameworkLogical::EvidenceReview::planAssessment;
            perform action assessProduct : FrameworkLogical::AssessProduct :>> C05::assessProduct, FrameworkLogical::EvidenceReview::assessProduct;
            perform action prepareReview : PhysicalPrepareReviewPackage :>> C05::prepareReview, FrameworkLogical::EvidenceReview::prepareReview;
            perform action checkReviewDecision : FrameworkLogical::CheckReviewDecision :>> C05::checkReviewDecision, FrameworkLogical::EvidenceReview::checkReviewDecision;
            perform action recordReview : FrameworkLogical::RecordReviewDecision :>> C05::recordReview, FrameworkLogical::EvidenceReview::recordReview;
            perform action makeViews : FrameworkLogical::MakeViews :>> C05::makeViews, FrameworkLogical::EvidenceReview::makeViews;
            perform action presentAssessment : FrameworkLogical::PresentAssessment :>> C05::presentAssessment, FrameworkLogical::EvidenceReview::presentAssessment;
        }
        part :>> L06 : C06 {
            perform action captureContext : FrameworkLogical::CaptureContext :>> C06::captureContext, FrameworkLogical::ConfigurationExchange::captureContext;
            perform action checkCurrency : PhysicalCheckCurrency :>> C06::checkCurrency, FrameworkLogical::ConfigurationExchange::checkCurrency;
            perform action invalidate : PhysicalInvalidateAndReassess :>> C06::invalidate, FrameworkLogical::ConfigurationExchange::invalidate;
            perform action checkChange : FrameworkLogical::CheckEngineeringChange :>> C06::checkChange, FrameworkLogical::ConfigurationExchange::checkChange;
            perform action successor : FrameworkLogical::RetainSuccessor :>> C06::successor, FrameworkLogical::ConfigurationExchange::successor;
            perform action preserveRun : PhysicalPreserveRun :>> C06::preserveRun, FrameworkLogical::ConfigurationExchange::preserveRun;
            perform action checkDesignAuthorization : FrameworkLogical::CheckDetailedDesignAuthorization :>> C06::checkDesignAuthorization, FrameworkLogical::ConfigurationExchange::checkDesignAuthorization;
            perform action retrieveBaseline : FrameworkLogical::RetrieveBaseline :>> C06::retrieveBaseline, FrameworkLogical::ConfigurationExchange::retrieveBaseline;
            perform action retainReview : FrameworkLogical::RetainReviewedBaseline :>> C06::retainReview, FrameworkLogical::ConfigurationExchange::retainReview;
            perform action prepareReplay : PhysicalPrepareReplay :>> C06::prepareReplay, FrameworkLogical::ConfigurationExchange::prepareReplay;
            perform action preserveRecord : FrameworkLogical::PreserveRecord :>> C06::preserveRecord, FrameworkLogical::ConfigurationExchange::preserveRecord;
            perform action checkSelection : FrameworkLogical::CheckEngineerSelection :>> C06::checkSelection, FrameworkLogical::ConfigurationExchange::checkSelection;
            perform action checkResultContext : FrameworkLogical::CheckResultContext :>> C06::checkResultContext, FrameworkLogical::ConfigurationExchange::checkResultContext;
            perform action prepareCalibrationChange : FrameworkLogical::PrepareCalibrationChange :>> C06::prepareCalibrationChange, FrameworkLogical::ConfigurationExchange::prepareCalibrationChange;
            perform action checkTransfer : FrameworkLogical::CheckTransfer :>> C06::checkTransfer, FrameworkLogical::ConfigurationExchange::checkTransfer;
            perform action checkEngineeringTransfer : FrameworkLogical::CheckTransfer :>> C06::checkEngineeringTransfer, FrameworkLogical::ConfigurationExchange::checkEngineeringTransfer;
            perform action checkSourceTransfer : FrameworkLogical::CheckTransfer :>> C06::checkSourceTransfer, FrameworkLogical::ConfigurationExchange::checkSourceTransfer;
        }
        part N1 : EngineeringHost;
        part N2 : AssistanceHost;
        part N3 : ArchiveHost;
        part engineeringNode : ResponsibilityNode;
        part assistanceNode : ResponsibilityNode;
        part evidenceNode : ResponsibilityNode;
        part models : ModelEnvironment;
        part hostCode : HostToolchain;
        ref item modelRecords : ModelData [0..*];
        ref item sourceAndAdviceRecords : AdviceData [0..*];
        ref item rawResultsAndReleases : ReleaseData [0..*];
        perform action engineeringProcedure : EngineeringProcedure;
        perform action reviewProcedure : ReviewProcedure;
        bind N1.requirements = L01;
        bind N1.design = L02;
        bind N1.analyses = L03;
        bind N1.credibility = L04;
        bind N1.review = L05;
        bind N2.advice = L01;
        bind N3.configuration = L06;
        bind N1.models = L03.p03;
        bind N1.hostCode = L03.p04;
        bind L03.mapping.sourceRecords = L01.authoring.currentRecords;
        bind L06.replayProfile = L03.replayDependencies;
        bind L06.numericalMapping = L03.mapping;
        bind L06.numericalEndpoint = L03.p03;
        bind L06.currency.latest.context = L01.authoring.currentRecords.context;
        bind L01.nativeModel = L02.nativeModel;
        bind L03.nativeModel = L02.nativeModel;
        bind L02.resources = L03.nativeResources;
        bind L03.nativeResources.cots = L02.cots;
        bind L03.nativeResources.methods = L01.jev;
        bind L03.nativeResources.platforms = L03.platforms;
        interface adviceLink connect N1.assistance to N2.assistance;
        interface releasedData connect N1.revisions to N3.engineering;
        interface sourceAdvice connect N2.revisions to N3.assistance;
        interface modelLink connect N1.models to models.requests;
        interface codeLink connect N1.hostCode to hostCode.requests;
        perform action assistance : PhysicalAssistanceRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action capture :>> capture references L06.captureContext;
            perform action invalidateOnEdit :>> invalidateOnEdit references L06.invalidate;
            perform action acknowledge :>> acknowledge references L01.acknowledge;
            perform action retainDraft :>> retainDraft references L01.retainRequirements;
            perform action checkDraft :>> checkDraft references L01.checkDraft;
            perform action recommend :>> recommend references L01.recommend;
            perform action checkReply :>> checkReply references L06.checkCurrency;
            perform action present :>> present references L01.presentAdvice;
            perform action dispose :>> dispose references L01.dispose;
            perform action checkApplication :>> checkApplication references L06.checkCurrency;
            perform action derive :>> derive references L01.deriveAllocate;
            perform action trace :>> trace references L01.traceLinks;
            perform action retainValidation :>> retainValidation references L06.preserveRecord;
            perform action retainDisposition :>> retainDisposition references L06.preserveRecord;
            perform action invalidate :>> invalidate references L06.invalidate;
            perform action reassess :>> reassess references L01.reassess;
            perform action rejectTransfer :>> rejectTransfer references L06.preserveRecord;
            perform action rejectDisposition :>> rejectDisposition references L06.preserveRecord;
        }
        perform action concept : PhysicalConceptRealization {
            perform action makeConfiguration :>> makeConfiguration references L02.configureConcept;
            perform action receive :>> receive references L06.checkTransfer;
            perform action configure :>> configure references L02.defineDesign;
            perform action budget :>> budget references L02.budgetSize;
            perform action planCriteria :>> planCriteria references L05.planAssessment;
            perform action plan :>> plan references L03.planAnalysis;
            perform action :>> execute {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action checkCurrent :>> checkCurrent references L06.checkResultContext;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action compare :>> compare references L02.compareDesigns;
            perform action checkSelection :>> checkSelection references L06.checkSelection;
            perform action retainSelection :>> retainSelection references L06.preserveRecord;
            perform action retainGaps :>> retainGaps references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
        perform action designRun : PhysicalDesignRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action configure :>> configure references L02.defineDesign;
            perform action budget :>> budget references L02.budgetSize;
            perform action planCriteria :>> planCriteria references L05.planAssessment;
            perform action plan :>> plan references L03.planAnalysis;
            perform action :>> execute {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action checkCurrent :>> checkCurrent references L06.checkResultContext;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action compare :>> compare references L02.compareDesigns;
            perform action checkSelection :>> checkSelection references L06.checkSelection;
            perform action retainSelection :>> retainSelection references L06.preserveRecord;
            perform action retainGaps :>> retainGaps references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
        perform action software : PhysicalSoftwareRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action interfaces :>> interfaces references L02.defineInterfaces;
            perform action mapping :>> mapping references L03.mapFPrime;
            perform action planCriteria :>> planCriteria references L05.planAssessment;
            perform action planMIL :>> planMIL references L03.planMIL;
            perform action :>> executeMIL {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveMIL :>> receiveMIL references L06.checkTransfer;
            perform action preserveMIL :>> preserveMIL references L06.preserveRun;
            perform action assessMIL :>> assessMIL references L04.assessModel;
            perform action checkRelease :>> checkRelease references L06.checkDesignAuthorization;
            perform action coordinate :>> coordinate references L03.coordinateCoding;
            perform action :>> codeBuildSil {
                perform action :>> profiles references L03.verifyHostProfiles;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveSIL :>> receiveSIL references L06.checkTransfer;
            perform action preserveSIL :>> preserveSIL references L06.preserveRun;
            perform action checkCurrent :>> checkCurrent references L06.checkResultContext;
            perform action compare :>> compare references L03.compareMILSil;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action present :>> present references L05.presentAssessment;
            perform action checkProducts :>> checkProducts references L06.checkSelection;
            perform action retainProducts :>> retainProducts references L06.preserveRecord;
            perform action block :>> block references L06.preserveRecord;
            perform action retainRaw_receiveMIL :>> retainRaw_receiveMIL references L06.preserveRecord;
            perform action retainRaw_receiveSIL :>> retainRaw_receiveSIL references L06.preserveRecord;
            perform action rejectRelease :>> rejectRelease references L06.preserveRecord;
        }
        perform action changeReview : PhysicalChangeReviewRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action invalidate :>> invalidate references L06.invalidate;
            perform action checkChange :>> checkChange references L06.checkChange;
            perform action successor :>> successor references L06.successor;
            perform action reassessAdvice :>> reassessAdvice references L01.reassess;
            perform action planRepeat :>> planRepeat references L03.planRepeat;
            perform action :>> repeat {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action credibility :>> credibility references L04.assessModel;
            perform action retrieve :>> retrieve references L06.retrieveBaseline;
            perform action assess :>> assess references L05.assessProduct;
            perform action views :>> views references L05.makeViews;
            perform action prepare :>> prepare references L05.prepareReview;
            perform action checkBaseline :>> checkBaseline references L06.checkResultContext;
            perform action checkDecision :>> checkDecision references L05.checkReviewDecision;
            perform action record :>> record references L05.recordReview;
            perform action retain :>> retain references L06.retainReview;
            perform action holdChange :>> holdChange references L06.preserveRecord;
            perform action holdReview :>> holdReview references L06.preserveRecord;
            perform action rejectReview :>> rejectReview references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
        perform action replayRun : PhysicalReplayRealization {
            perform action prepare :>> prepare references L06.prepareReplay;
            perform action :>> execute {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receive :>> receive references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action compare :>> compare references L03.replay;
            perform action retain :>> retain references L06.preserveRecord;
            perform action missing :>> missing references L06.preserveRecord;
            perform action retainRaw_receive :>> retainRaw_receive references L06.preserveRecord;
        }
        perform action calibration : PhysicalCalibrationRealization {
            perform action receive :>> receive references L06.checkTransfer;
            perform action checkData :>> checkData references L04.checkReferenceData;
            perform action propose :>> propose references L04.proposeCalibration;
            perform action prepareChange :>> prepareChange references L06.prepareCalibrationChange;
            perform action invalidate :>> invalidate references L06.invalidate;
            perform action checkChange :>> checkChange references L06.checkChange;
            perform action successor :>> successor references L06.successor;
            perform action reassess :>> reassess references L01.reassess;
            perform action planRepeat :>> planRepeat references L03.planRepeat;
            perform action :>> repeat {
                perform action :>> profiles references L03.verifyProfiles;
                bind modelEndpoint = Configuration::models.requests;
                bind hostEndpoint = Configuration::hostCode.requests;
            }
            perform action receiveResult :>> receiveResult references L06.checkTransfer;
            perform action preserve :>> preserve references L06.preserveRun;
            perform action credibility :>> credibility references L04.assessModel;
            perform action assess :>> assess references L05.assessProduct;
            perform action retainEvidence :>> retainEvidence references L06.preserveRecord;
            perform action retain :>> retain references L06.preserveRecord;
            perform action unusable :>> unusable references L06.preserveRecord;
            perform action retainRaw_receiveResult :>> retainRaw_receiveResult references L06.preserveRecord;
        }
    }
    @SourceRecord about Configuration { identifier = "PA-CDT"; sourceText = "User custom native SysML v2/CSRM composite with exact six-component proposed composition and mandatory F Prime/numerical whole-CUBICS Omniverse connections."; sourceLocator = "OOSEM physical synthesis and neutral MOP comparison"; citationRecord = "kaslow2019csrm, typesafe060, review-0711, review-0289, review-0853, handpicked-0001, review-0573, citation-0569, chiu2023sealion"; status = "proposed/unexecuted"; }
    part candidate : Configuration;
    #logicalRealization allocation logical_L01 allocate logical.L01 to candidate.L01;
    #logicalRealization allocation logical_L02 allocate logical.L02 to candidate.L02;
    #logicalRealization allocation logical_L03 allocate logical.L03 to candidate.L03;
    #logicalRealization allocation logical_L04 allocate logical.L04 to candidate.L04;
    #logicalRealization allocation logical_L05 allocate logical.L05 to candidate.L05;
    #logicalRealization allocation logical_L06 allocate logical.L06 to candidate.L06;
    #physicalDetail allocation guidanceState allocate logical.L06.assistanceCurrency to candidate.L06.assistanceCurrency;
    #physicalDetail allocation reviewState allocate logical.L05.reviewState to candidate.L05.reviewState;
    #physicalPrimary allocation primary_FR_01 allocate FrameworkRequirements::FR_01 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "I,T: Round-trip quantitative and qualitative records, including unresolved criteria."; operation = CandidateCDT::C01::retainRequirements meta SysML::ActionUsage; } }
    dependency operation_FR_01 from FrameworkLogical::RequirementsAssistance::retainRequirements to CandidateCDT::C01::retainRequirements;
    dependency contract_FR_01 from FrameworkLogical::ContractFR01 to CandidateCDT::C01::contractFR01;
    #physicalPrimary allocation primary_FR_02 allocate FrameworkRequirements::FR_02 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "A,T: Compare clean and seeded drafts with an independent expert reference, including valid similar requirements and missed defects."; operation = CandidateCDT::C01::checkDraft meta SysML::ActionUsage; } }
    dependency operation_FR_02 from FrameworkLogical::RequirementsAssistance::checkDraft to CandidateCDT::C01::checkDraft;
    dependency contract_FR_02 from FrameworkLogical::ContractFR02 to CandidateCDT::C01::contractFR02;
    #physicalPrimary allocation primary_FR_03 allocate FrameworkRequirements::FR_03 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "A,T: Use contextual queries whose eligible methods change with inputs, maturity or intended use."; operation = CandidateCDT::C01::recommend meta SysML::ActionUsage; } }
    dependency operation_FR_03 from FrameworkLogical::RequirementsAssistance::recommend to CandidateCDT::C01::recommend;
    dependency contract_FR_03 from FrameworkLogical::ContractFR03 to CandidateCDT::C01::contractFR03;
    #physicalPrimary allocation primary_FR_04 allocate FrameworkRequirements::FR_04 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "T: Compare both query directions and coverage with a known relationship set."; operation = CandidateCDT::C01::traceLinks meta SysML::ActionUsage; } }
    dependency operation_FR_04 from FrameworkLogical::RequirementsAssistance::traceLinks to CandidateCDT::C01::traceLinks;
    dependency contract_FR_04 from FrameworkLogical::ContractFR04 to CandidateCDT::C01::contractFR04;
    #physicalPrimary allocation primary_FR_05 allocate FrameworkRequirements::FR_05 to candidate.L06 { @PhysicalAllocation { rationale = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; plannedCheck = "A,T: Compare the impact set of coupled load, pointing and interface changes with an expert reference."; operation = CandidateCDT::C06::invalidate meta SysML::ActionUsage; } }
    dependency operation_FR_05 from FrameworkLogical::ConfigurationExchange::invalidate to CandidateCDT::C06::invalidate;
    dependency contract_FR_05 from FrameworkLogical::ContractFR05 to CandidateCDT::C06::contractFR05;
    #physicalPrimary allocation primary_FR_06 allocate FrameworkRequirements::FR_06 to candidate.L06 { @PhysicalAllocation { rationale = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; plannedCheck = "T: Accept, decline and interrupt changes without erasing the predecessor."; operation = CandidateCDT::C06::successor meta SysML::ActionUsage; } }
    dependency operation_FR_06 from FrameworkLogical::ConfigurationExchange::successor to CandidateCDT::C06::successor;
    dependency contract_FR_06 from FrameworkLogical::ContractFR06 to CandidateCDT::C06::contractFR06;
    #physicalPrimary allocation primary_FR_07 allocate FrameworkRequirements::FR_07 to candidate.L06 { @PhysicalAllocation { rationale = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; plannedCheck = "I,T: Reconstruct predecessor and successor manifests and all applicable products."; operation = CandidateCDT::C06::retrieveBaseline meta SysML::ActionUsage; } }
    dependency operation_FR_07 from FrameworkLogical::ConfigurationExchange::retrieveBaseline to CandidateCDT::C06::retrieveBaseline;
    dependency contract_FR_07 from FrameworkLogical::ContractFR07 to CandidateCDT::C06::contractFR07;
    #physicalPrimary allocation primary_FR_08 allocate FrameworkRequirements::FR_08 to candidate.L06 { @PhysicalAllocation { rationale = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; plannedCheck = "T: Inject identity, unit, sign and revision mismatches at each active interface."; operation = CandidateCDT::C06::checkTransfer meta SysML::ActionUsage; } }
    dependency operation_FR_08 from FrameworkLogical::ConfigurationExchange::checkTransfer to CandidateCDT::C06::checkTransfer;
    dependency contract_FR_08 from FrameworkLogical::ContractFR08 to CandidateCDT::C06::contractFR08;
    #physicalPrimary allocation primary_FR_09 allocate FrameworkRequirements::FR_09 to candidate.L06 { @PhysicalAllocation { rationale = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; plannedCheck = "I,T: Trace successful, failed, cancelled and partial outputs to their configurations."; operation = CandidateCDT::C06::preserveRun meta SysML::ActionUsage; } }
    dependency operation_FR_09 from FrameworkLogical::ConfigurationExchange::preserveRun to CandidateCDT::C06::preserveRun;
    dependency contract_FR_09 from FrameworkLogical::ContractFR09 to CandidateCDT::C06::contractFR09;
    #physicalPrimary allocation primary_FR_10 allocate FrameworkRequirements::FR_10 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "D,T: Independently replay in the declared host environment and compare under fixed tolerances."; operation = CandidateCDT::C03::replay meta SysML::ActionUsage; } }
    dependency operation_FR_10 from FrameworkLogical::SimulationIntegration::replay to CandidateCDT::C03::replay;
    dependency contract_FR_10 from FrameworkLogical::ContractFR10 to CandidateCDT::C03::contractFR10;
    #physicalPrimary allocation primary_FR_11 allocate FrameworkRequirements::FR_11 to candidate.L05 { @PhysicalAllocation { rationale = "Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision."; plannedCheck = "T: Seed every evidence status and attempt a current claim with a blocking gap."; operation = CandidateCDT::C05::assessProduct meta SysML::ActionUsage; } }
    dependency operation_FR_11 from FrameworkLogical::EvidenceReview::assessProduct to CandidateCDT::C05::assessProduct;
    dependency contract_FR_11 from FrameworkLogical::ContractFR11 to CandidateCDT::C05::contractFR11;
    #physicalPrimary allocation primary_FR_13 allocate FrameworkRequirements::FR_13 to candidate.L02 { @PhysicalAllocation { rationale = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; plannedCheck = "A,T: Recalculate mass and volume after a component substitution and preserve unknown properties and aggregation assumptions."; operation = CandidateCDT::C02::budgetSize meta SysML::ActionUsage; } }
    dependency operation_FR_13 from FrameworkLogical::MissionDesign::budgetSize to CandidateCDT::C02::budgetSize;
    dependency contract_FR_13 from FrameworkLogical::ContractFR13 to CandidateCDT::C02::contractFR13;
    #physicalPrimary allocation primary_FR_14 allocate FrameworkRequirements::FR_14 to candidate.L02 { @PhysicalAllocation { rationale = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; plannedCheck = "A,T: Use infeasible and closely ranked alternatives with uncertain inputs."; operation = CandidateCDT::C02::compareDesigns meta SysML::ActionUsage; } }
    dependency operation_FR_14 from FrameworkLogical::MissionDesign::compareDesigns to CandidateCDT::C02::compareDesigns;
    dependency contract_FR_14 from FrameworkLogical::ContractFR14 to CandidateCDT::C02::contractFR14;
    #physicalPrimary allocation primary_FR_15 allocate FrameworkRequirements::FR_15 to candidate.L02 { @PhysicalAllocation { rationale = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; plannedCheck = "I,D: Configure alternate EPS topologies and retain the distinct allocation and extension revisions."; operation = CandidateCDT::C02::defineDesign meta SysML::ActionUsage; } }
    dependency operation_FR_15 from FrameworkLogical::MissionDesign::defineDesign to CandidateCDT::C02::defineDesign;
    dependency contract_FR_15 from FrameworkLogical::ContractFR15 to CandidateCDT::C02::contractFR15;
    #physicalPrimary allocation primary_FR_16 allocate FrameworkRequirements::FR_16 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "A,T: Use whole-CUBICS histories with a temporal shortage hidden by an average budget. Perturb load, mode or illumination and compare the mapped EPS numerical response with an independent reference within model scope."; operation = CandidateCDT::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_16 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateCDT::C03::planAnalysis;
    dependency contract_FR_16 from FrameworkLogical::ContractFR16 to CandidateCDT::C03::contractFR16;
    #physicalPrimary allocation primary_FR_17 allocate FrameworkRequirements::FR_17 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "A,T: Recalculate an allocation and follow it to the parent and source quantities."; operation = CandidateCDT::C01::deriveAllocate meta SysML::ActionUsage; } }
    dependency operation_FR_17 from FrameworkLogical::RequirementsAssistance::deriveAllocate to CandidateCDT::C01::deriveAllocate;
    dependency contract_FR_17 from FrameworkLogical::ContractFR17 to CandidateCDT::C01::contractFR17;
    #physicalPrimary allocation primary_FR_18 allocate FrameworkRequirements::FR_18 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "D,T: Exercise each discipline profile and incompatible mappings. Perturb an incoming whole-CUBICS history, compare the EPS numerical effect independently and return its identified response to the same scenario. Scene-only updates or missing numerical exchange cannot pass. Retain failed/partial status and transfer limits."; operation = CandidateCDT::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_18 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateCDT::C03::planAnalysis;
    dependency contract_FR_18 from FrameworkLogical::ContractFR18 to CandidateCDT::C03::contractFR18;
    #physicalPrimary allocation primary_FR_19 allocate FrameworkRequirements::FR_19 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "D,T: Run declared nominal and fault sequences with a simulated plant and retain stimuli, expected/actual state/event responses and failed criteria for matched SIL comparison."; operation = CandidateCDT::C03::planMIL meta SysML::ActionUsage; } }
    dependency operation_FR_19 from FrameworkLogical::SimulationIntegration::planMIL to CandidateCDT::C03::planMIL;
    dependency contract_FR_19 from FrameworkLogical::ContractFR19 to CandidateCDT::C03::contractFR19;
    #physicalPrimary allocation primary_FR_20 allocate FrameworkRequirements::FR_20 to candidate.L02 { @PhysicalAllocation { rationale = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; plannedCheck = "A,T: Compare sizing and energy balance with independent calculations, including an infeasible eclipse case."; operation = CandidateCDT::C02::budgetSize meta SysML::ActionUsage; } }
    dependency operation_FR_20 from FrameworkLogical::MissionDesign::budgetSize to CandidateCDT::C02::budgetSize;
    dependency contract_FR_20 from FrameworkLogical::ContractFR20 to CandidateCDT::C02::contractFR20;
    #physicalPrimary allocation primary_FR_21 allocate FrameworkRequirements::FR_21 to candidate.L04 { @PhysicalAllocation { rationale = "Python assessment using Casado reference-waveform and CSRM model/V&V relationships. Calibration, independent model credibility and EPS conformity remain distinct."; plannedCheck = "I,T: Attempt conclusions outside validity and with missing independent evidence."; operation = CandidateCDT::C04::assessModel meta SysML::ActionUsage; } }
    dependency operation_FR_21 from FrameworkLogical::ModelCredibility::assessModel to CandidateCDT::C04::assessModel;
    dependency contract_FR_21 from FrameworkLogical::ContractFR21 to CandidateCDT::C04::contractFR21;
    #physicalPrimary allocation primary_FR_22 allocate FrameworkRequirements::FR_22 to candidate.L04 { @PhysicalAllocation { rationale = "Python assessment using Casado reference-waveform and CSRM model/V&V relationships. Calibration, independent model credibility and EPS conformity remain distinct."; plannedCheck = "A,T: Calibrate from supplied data, retain separate assessment data and decline an update."; operation = CandidateCDT::C04::proposeCalibration meta SysML::ActionUsage; } }
    dependency operation_FR_22 from FrameworkLogical::ModelCredibility::proposeCalibration to CandidateCDT::C04::proposeCalibration;
    dependency contract_FR_22 from FrameworkLogical::ContractFR22 to CandidateCDT::C04::contractFR22;
    #physicalPrimary allocation primary_FR_23 allocate FrameworkRequirements::FR_23 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "I,T: Change the time step, solver and resource limits and inspect the run configuration and findings."; operation = CandidateCDT::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_23 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateCDT::C03::planAnalysis;
    dependency contract_FR_23 from FrameworkLogical::ContractFR23 to CandidateCDT::C03::contractFR23;
    #physicalPrimary allocation primary_FR_24 allocate FrameworkRequirements::FR_24 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "A,T: Execute released F Prime host software with simulated EPS/subsystem products connected to the same whole-CUBICS scenario. Use matched MIL results and fixed comparison rules. Seed a code/interface discrepancy and failed/partial runs. Retain raw host responses, requirement/ConOps outcomes, differences, status and limits. Builds and scene updates supply no SIL evidence."; operation = CandidateCDT::C03::compareMILSil meta SysML::ActionUsage; } }
    dependency operation_FR_24 from FrameworkLogical::SimulationIntegration::compareMILSil to CandidateCDT::C03::compareMILSil;
    dependency contract_FR_24 from FrameworkLogical::ContractFR24 to CandidateCDT::C03::contractFR24;
    #physicalPrimary allocation primary_FR_25 allocate FrameworkRequirements::FR_25 to candidate.L02 { @PhysicalAllocation { rationale = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; plannedCheck = "I,T: Revise a degraded mode and trace its requirement and analysis inputs."; operation = CandidateCDT::C02::defineDesign meta SysML::ActionUsage; } }
    dependency operation_FR_25 from FrameworkLogical::MissionDesign::defineDesign to CandidateCDT::C02::defineDesign;
    dependency contract_FR_25 from FrameworkLogical::ContractFR25 to CandidateCDT::C02::contractFR25;
    #physicalPrimary allocation primary_FR_26 allocate FrameworkRequirements::FR_26 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "I,T: Assess applicability with and without repair or redundancy assumptions."; operation = CandidateCDT::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_26 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateCDT::C03::planAnalysis;
    dependency contract_FR_26 from FrameworkLogical::ContractFR26 to CandidateCDT::C03::contractFR26;
    #physicalPrimary allocation primary_FR_27 allocate FrameworkRequirements::FR_27 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "A,T: Compare transformations and results with a reference and leave missing rates unresolved."; operation = CandidateCDT::C03::planAnalysis meta SysML::ActionUsage; } }
    dependency operation_FR_27 from FrameworkLogical::SimulationIntegration::planAnalysis to CandidateCDT::C03::planAnalysis;
    dependency contract_FR_27 from FrameworkLogical::ContractFR27 to CandidateCDT::C03::contractFR27;
    #physicalPrimary allocation primary_FR_28 allocate FrameworkRequirements::FR_28 to candidate.L05 { @PhysicalAllocation { rationale = "Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision."; plannedCheck = "I,T: Distinguish planned activities from results and verification criteria from validation expectations."; operation = CandidateCDT::C05::planAssessment meta SysML::ActionUsage; } }
    dependency operation_FR_28 from FrameworkLogical::EvidenceReview::planAssessment to CandidateCDT::C05::planAssessment;
    dependency contract_FR_28 from FrameworkLogical::ContractFR28 to CandidateCDT::C05::contractFR28;
    #physicalPrimary allocation primary_FR_29 allocate FrameworkRequirements::FR_29 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "I,T: Exercise all dispositions and an unauthorized attempt to apply a suggestion."; operation = CandidateCDT::C01::dispose meta SysML::ActionUsage; } }
    dependency operation_FR_29 from FrameworkLogical::RequirementsAssistance::dispose to CandidateCDT::C01::dispose;
    dependency contract_FR_29 from FrameworkLogical::ContractFR29 to CandidateCDT::C01::contractFR29;
    #physicalPrimary allocation primary_FR_30 allocate FrameworkRequirements::FR_30 to candidate.L06 { @PhysicalAllocation { rationale = "Controlled native revisions plus Git history and preserved raw/source/COTS/Python dependencies. Native/source/classifier/rule changes immediately invalidate current and pending guidance."; plannedCheck = "T: Edit during a delayed response and check that the old response cannot replace current guidance."; operation = CandidateCDT::C06::invalidate meta SysML::ActionUsage; } }
    dependency operation_FR_30 from FrameworkLogical::ConfigurationExchange::invalidate to CandidateCDT::C06::invalidate;
    dependency contract_FR_30 from FrameworkLogical::ContractFR30 to CandidateCDT::C06::contractFR30;
    #physicalPrimary allocation primary_FR_31 allocate FrameworkRequirements::FR_31 to candidate.L04 { @PhysicalAllocation { rationale = "Python assessment using Casado reference-waveform and CSRM model/V&V relationships. Calibration, independent model credibility and EPS conformity remain distinct."; plannedCheck = "A,T: Seed clock offset, delayed/out-of-order samples and missing timing. Compare checked alignments, delays and exceeded/unknown limits with fixed timing references. Distinguish scenario/sample/receipt times, scene update rate and numerical time step."; operation = CandidateCDT::C04::assessModel meta SysML::ActionUsage; } }
    dependency operation_FR_31 from FrameworkLogical::ModelCredibility::assessModel to CandidateCDT::C04::assessModel;
    dependency contract_FR_31 from FrameworkLogical::ContractFR31 to CandidateCDT::C04::contractFR31;
    #physicalPrimary allocation primary_FR_32 allocate FrameworkRequirements::FR_32 to candidate.L04 { @PhysicalAllocation { rationale = "Python assessment using Casado reference-waveform and CSRM model/V&V relationships. Calibration, independent model credibility and EPS conformity remain distinct."; plannedCheck = "T: Seed wrong entity/channel/revision, unit/sign/frame mismatch and missing, inactive or invalid samples. Compare admission findings and masks with a fixed reference before numerical use. Preserve raw histories and unchanged controlled content for rejected transfers."; operation = CandidateCDT::C04::assessModel meta SysML::ActionUsage; } }
    dependency operation_FR_32 from FrameworkLogical::ModelCredibility::assessModel to CandidateCDT::C04::assessModel;
    dependency contract_FR_32 from FrameworkLogical::ContractFR32 to CandidateCDT::C04::contractFR32;
    #physicalPrimary allocation primary_FR_33 allocate FrameworkRequirements::FR_33 to candidate.L02 { @PhysicalAllocation { rationale = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; plannedCheck = "I,T: Round-trip endpoint ownership/directions and all interface and ground-definition fields. Reject inconsistent identifiers, types, units, ranges, polarity and temporal meanings against an independent reference. Structural checks supply no behavior verdict."; operation = CandidateCDT::C02::defineInterfaces meta SysML::ActionUsage; } }
    dependency operation_FR_33 from FrameworkLogical::MissionDesign::defineInterfaces to CandidateCDT::C02::defineInterfaces;
    dependency contract_FR_33 from FrameworkLogical::ContractFR33 to CandidateCDT::C02::contractFR33;
    #physicalPrimary allocation primary_FR_34 allocate FrameworkRequirements::FR_34 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "D,T: Compare required F Prime component/instance/port/topology and command/telemetry/event/parameter mappings with an independent reference at declared actual profile/tool/representation versions. Seed conflicts, wrong directions/types, missing meanings and incompatible versions. Retain unsupported behavior and lossy translations."; operation = CandidateCDT::C03::mapFPrime meta SysML::ActionUsage; } }
    dependency operation_FR_34 from FrameworkLogical::SimulationIntegration::mapFPrime to CandidateCDT::C03::mapFPrime;
    dependency contract_FR_34 from FrameworkLogical::ContractFR34 to CandidateCDT::C03::contractFR34;
    #physicalPrimary allocation primary_FR_35 allocate FrameworkRequirements::FR_35 to candidate.L02 { @PhysicalAllocation { rationale = "Native CSRM-informed EPS requirements, quantity properties, calculations, constraints and parameter bindings plus Python analyses and required maintained COTS database. Conversion/enrichment is proposed."; plannedCheck = "A,T: Exercise nominal, rejected, protection and recovery sequences in simulated conditions."; operation = CandidateCDT::C02::defineInterfaces meta SysML::ActionUsage; } }
    dependency operation_FR_35 from FrameworkLogical::MissionDesign::defineInterfaces to CandidateCDT::C02::defineInterfaces;
    dependency contract_FR_35 from FrameworkLogical::ContractFR35 to CandidateCDT::C02::contractFR35;
    #physicalPrimary allocation primary_FR_36 allocate FrameworkRequirements::FR_36 to candidate.L03 { @PhysicalAllocation { rationale = "Python implementation/orchestration plus F Prime architecture and Zhu battery USD/data patterns. Native quantity bindings feed required numerical whole-CUBICS and checked host-software mappings."; plannedCheck = "D,T: Reject stale, unreleased and unauthorized design requests. Coordinate an authorized current-release F Prime host build, retaining exact source/build, toolchain/dependency/host revisions, logs and generation/compilation failures. Review acceptance cannot replace exact authorization. Build success supplies no SIL verdict."; operation = CandidateCDT::C03::coordinateCoding meta SysML::ActionUsage; } }
    dependency operation_FR_36 from FrameworkLogical::SimulationIntegration::coordinateCoding to CandidateCDT::C03::coordinateCoding;
    dependency contract_FR_36 from FrameworkLogical::ContractFR36 to CandidateCDT::C03::contractFR36;
    #physicalPrimary allocation primary_FR_37 allocate FrameworkRequirements::FR_37 to candidate.L05 { @PhysicalAllocation { rationale = "Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision."; plannedCheck = "I,D: Compare views with their source baseline and follow represented record links."; operation = CandidateCDT::C05::makeViews meta SysML::ActionUsage; } }
    dependency operation_FR_37 from FrameworkLogical::EvidenceReview::makeViews to CandidateCDT::C05::makeViews;
    dependency contract_FR_37 from FrameworkLogical::ContractFR37 to CandidateCDT::C05::contractFR37;
    #physicalPrimary allocation primary_FR_38 allocate FrameworkRequirements::FR_38 to candidate.L05 { @PhysicalAllocation { rationale = "Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision."; plannedCheck = "I,D: Prepare phase-specific packages, including CDR design release and SIR released-product evidence."; operation = CandidateCDT::C05::prepareReview meta SysML::ActionUsage; } }
    dependency operation_FR_38 from FrameworkLogical::EvidenceReview::prepareReview to CandidateCDT::C05::prepareReview;
    dependency contract_FR_38 from FrameworkLogical::ContractFR38 to CandidateCDT::C05::contractFR38;
    #physicalPrimary allocation primary_FR_39 allocate FrameworkRequirements::FR_39 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "A,D: Change maturity and blocking findings and inspect the revised activity proposals."; operation = CandidateCDT::C01::recommend meta SysML::ActionUsage; } }
    dependency operation_FR_39 from FrameworkLogical::RequirementsAssistance::recommend to CandidateCDT::C01::recommend;
    dependency contract_FR_39 from FrameworkLogical::ContractFR39 to CandidateCDT::C01::contractFR39;
    #physicalPrimary allocation primary_FR_41 allocate FrameworkRequirements::FR_41 to candidate.L01 { @PhysicalAllocation { rationale = "Enriched native requirement subjects, assumptions and fields plus required Jev analysis/V&V suggestions. Python drafting/semantic checks are separate. Engineers retain applicability and acceptance authority."; plannedCheck = "T: Measure response delay under the declared workload, including outage and superseded edits."; operation = CandidateCDT::C01::acknowledge meta SysML::ActionUsage; } }
    dependency operation_FR_41 from FrameworkLogical::RequirementsAssistance::acknowledge to CandidateCDT::C01::acknowledge;
    dependency contract_FR_41 from FrameworkLogical::ContractFR41 to CandidateCDT::C01::contractFR41;
    #physicalPrimary allocation primary_FR_42 allocate FrameworkRequirements::FR_42 to candidate.L05 { @PhysicalAllocation { rationale = "Python/native evidence assembly plus requirement/procedure/verdict feedback. Plans and numerical outputs supply no automatic satisfaction or authority decision."; plannedCheck = "I,T: Reject unauthorized or stale-baseline decisions and exercise blocking and conditional findings."; operation = CandidateCDT::C05::recordReview meta SysML::ActionUsage; } }
    dependency operation_FR_42 from FrameworkLogical::EvidenceReview::recordReview to CandidateCDT::C05::recordReview;
    dependency contract_FR_42 from FrameworkLogical::ContractFR42 to CandidateCDT::C05::contractFR42;
    #physicalDetail allocation step_AssistanceRealization_edit allocate LogicalRealization::AssistanceRealization::edit to candidate.assistance.edit;
    #physicalDetail allocation step_AssistanceRealization_receive allocate LogicalRealization::AssistanceRealization::receive to candidate.assistance.receive;
    #physicalDetail allocation step_AssistanceRealization_capture allocate LogicalRealization::AssistanceRealization::capture to candidate.assistance.capture;
    #physicalDetail allocation step_AssistanceRealization_invalidateOnEdit allocate LogicalRealization::AssistanceRealization::invalidateOnEdit to candidate.assistance.invalidateOnEdit;
    #physicalDetail allocation step_AssistanceRealization_acknowledge allocate LogicalRealization::AssistanceRealization::acknowledge to candidate.assistance.acknowledge;
    #physicalDetail allocation step_AssistanceRealization_retainDraft allocate LogicalRealization::AssistanceRealization::retainDraft to candidate.assistance.retainDraft;
    #physicalDetail allocation step_AssistanceRealization_checkDraft allocate LogicalRealization::AssistanceRealization::checkDraft to candidate.assistance.checkDraft;
    #physicalDetail allocation step_AssistanceRealization_recommend allocate LogicalRealization::AssistanceRealization::recommend to candidate.assistance.recommend;
    #physicalDetail allocation step_AssistanceRealization_checkReply allocate LogicalRealization::AssistanceRealization::checkReply to candidate.assistance.checkReply;
    #physicalDetail allocation step_AssistanceRealization_present allocate LogicalRealization::AssistanceRealization::present to candidate.assistance.present;
    #physicalDetail allocation step_AssistanceRealization_engineerDisposition allocate LogicalRealization::AssistanceRealization::engineerDisposition to candidate.assistance.engineerDisposition;
    #physicalDetail allocation step_AssistanceRealization_dispose allocate LogicalRealization::AssistanceRealization::dispose to candidate.assistance.dispose;
    #physicalDetail allocation step_AssistanceRealization_checkApplication allocate LogicalRealization::AssistanceRealization::checkApplication to candidate.assistance.checkApplication;
    #physicalDetail allocation step_AssistanceRealization_derive allocate LogicalRealization::AssistanceRealization::derive to candidate.assistance.derive;
    #physicalDetail allocation step_AssistanceRealization_trace allocate LogicalRealization::AssistanceRealization::trace to candidate.assistance.trace;
    #physicalDetail allocation step_AssistanceRealization_validate allocate LogicalRealization::AssistanceRealization::validate to candidate.assistance.validate;
    #physicalDetail allocation step_AssistanceRealization_retainValidation allocate LogicalRealization::AssistanceRealization::retainValidation to candidate.assistance.retainValidation;
    #physicalDetail allocation step_AssistanceRealization_retainDisposition allocate LogicalRealization::AssistanceRealization::retainDisposition to candidate.assistance.retainDisposition;
    #physicalDetail allocation step_AssistanceRealization_invalidate allocate LogicalRealization::AssistanceRealization::invalidate to candidate.assistance.invalidate;
    #physicalDetail allocation step_AssistanceRealization_reassess allocate LogicalRealization::AssistanceRealization::reassess to candidate.assistance.reassess;
    #physicalDetail allocation step_AssistanceRealization_rejectTransfer allocate LogicalRealization::AssistanceRealization::rejectTransfer to candidate.assistance.rejectTransfer;
    #physicalDetail allocation step_AssistanceRealization_rejectDisposition allocate LogicalRealization::AssistanceRealization::rejectDisposition to candidate.assistance.rejectDisposition;
    #physicalDetail allocation step_DesignRealization_submit allocate LogicalRealization::DesignRealization::submit to candidate.designRun.submit;
    #physicalDetail allocation step_DesignRealization_receive allocate LogicalRealization::DesignRealization::receive to candidate.designRun.receive;
    #physicalDetail allocation step_DesignRealization_configure allocate LogicalRealization::DesignRealization::configure to candidate.designRun.configure;
    #physicalDetail allocation step_DesignRealization_budget allocate LogicalRealization::DesignRealization::budget to candidate.designRun.budget;
    #physicalDetail allocation step_DesignRealization_planCriteria allocate LogicalRealization::DesignRealization::planCriteria to candidate.designRun.planCriteria;
    #physicalDetail allocation step_DesignRealization_plan allocate LogicalRealization::DesignRealization::plan to candidate.designRun.plan;
    #physicalDetail allocation step_DesignRealization_execute allocate LogicalRealization::DesignRealization::execute to candidate.designRun.execute;
    #executionHost allocation external_DesignRealization_execute allocate candidate.designRun.execute to candidate.models;
    #physicalDetail allocation step_DesignRealization_receiveResult allocate LogicalRealization::DesignRealization::receiveResult to candidate.designRun.receiveResult;
    #physicalDetail allocation step_DesignRealization_preserve allocate LogicalRealization::DesignRealization::preserve to candidate.designRun.preserve;
    #physicalDetail allocation step_DesignRealization_checkCurrent allocate LogicalRealization::DesignRealization::checkCurrent to candidate.designRun.checkCurrent;
    #physicalDetail allocation step_DesignRealization_credibility allocate LogicalRealization::DesignRealization::credibility to candidate.designRun.credibility;
    #physicalDetail allocation step_DesignRealization_assess allocate LogicalRealization::DesignRealization::assess to candidate.designRun.assess;
    #physicalDetail allocation step_DesignRealization_compare allocate LogicalRealization::DesignRealization::compare to candidate.designRun.compare;
    #physicalDetail allocation step_DesignRealization_select allocate LogicalRealization::DesignRealization::select to candidate.designRun.select;
    #physicalDetail allocation step_DesignRealization_checkSelection allocate LogicalRealization::DesignRealization::checkSelection to candidate.designRun.checkSelection;
    #physicalDetail allocation step_DesignRealization_retainSelection allocate LogicalRealization::DesignRealization::retainSelection to candidate.designRun.retainSelection;
    #physicalDetail allocation step_DesignRealization_retainGaps allocate LogicalRealization::DesignRealization::retainGaps to candidate.designRun.retainGaps;
    #physicalDetail allocation step_DesignRealization_retainRaw_receiveResult allocate LogicalRealization::DesignRealization::retainRaw_receiveResult to candidate.designRun.retainRaw_receiveResult;
    #physicalDetail allocation step_ConceptRealization_makeConfiguration allocate LogicalRealization::ConceptRealization::makeConfiguration to candidate.concept.makeConfiguration;
    #physicalDetail allocation step_ConceptRealization_submit allocate LogicalRealization::ConceptRealization::submit to candidate.concept.submit;
    #physicalDetail allocation step_ConceptRealization_receive allocate LogicalRealization::ConceptRealization::receive to candidate.concept.receive;
    #physicalDetail allocation step_ConceptRealization_configure allocate LogicalRealization::ConceptRealization::configure to candidate.concept.configure;
    #physicalDetail allocation step_ConceptRealization_budget allocate LogicalRealization::ConceptRealization::budget to candidate.concept.budget;
    #physicalDetail allocation step_ConceptRealization_planCriteria allocate LogicalRealization::ConceptRealization::planCriteria to candidate.concept.planCriteria;
    #physicalDetail allocation step_ConceptRealization_plan allocate LogicalRealization::ConceptRealization::plan to candidate.concept.plan;
    #physicalDetail allocation step_ConceptRealization_execute allocate LogicalRealization::ConceptRealization::execute to candidate.concept.execute;
    #executionHost allocation external_ConceptRealization_execute allocate candidate.concept.execute to candidate.models;
    #physicalDetail allocation step_ConceptRealization_receiveResult allocate LogicalRealization::ConceptRealization::receiveResult to candidate.concept.receiveResult;
    #physicalDetail allocation step_ConceptRealization_preserve allocate LogicalRealization::ConceptRealization::preserve to candidate.concept.preserve;
    #physicalDetail allocation step_ConceptRealization_checkCurrent allocate LogicalRealization::ConceptRealization::checkCurrent to candidate.concept.checkCurrent;
    #physicalDetail allocation step_ConceptRealization_credibility allocate LogicalRealization::ConceptRealization::credibility to candidate.concept.credibility;
    #physicalDetail allocation step_ConceptRealization_assess allocate LogicalRealization::ConceptRealization::assess to candidate.concept.assess;
    #physicalDetail allocation step_ConceptRealization_compare allocate LogicalRealization::ConceptRealization::compare to candidate.concept.compare;
    #physicalDetail allocation step_ConceptRealization_select allocate LogicalRealization::ConceptRealization::select to candidate.concept.select;
    #physicalDetail allocation step_ConceptRealization_checkSelection allocate LogicalRealization::ConceptRealization::checkSelection to candidate.concept.checkSelection;
    #physicalDetail allocation step_ConceptRealization_retainSelection allocate LogicalRealization::ConceptRealization::retainSelection to candidate.concept.retainSelection;
    #physicalDetail allocation step_ConceptRealization_retainGaps allocate LogicalRealization::ConceptRealization::retainGaps to candidate.concept.retainGaps;
    #physicalDetail allocation step_ConceptRealization_retainRaw_receiveResult allocate LogicalRealization::ConceptRealization::retainRaw_receiveResult to candidate.concept.retainRaw_receiveResult;
    #physicalDetail allocation step_SoftwareRealization_submit allocate LogicalRealization::SoftwareRealization::submit to candidate.software.submit;
    #physicalDetail allocation step_SoftwareRealization_receive allocate LogicalRealization::SoftwareRealization::receive to candidate.software.receive;
    #physicalDetail allocation step_SoftwareRealization_interfaces allocate LogicalRealization::SoftwareRealization::interfaces to candidate.software.interfaces;
    #physicalDetail allocation step_SoftwareRealization_mapping allocate LogicalRealization::SoftwareRealization::mapping to candidate.software.mapping;
    #physicalDetail allocation step_SoftwareRealization_planCriteria allocate LogicalRealization::SoftwareRealization::planCriteria to candidate.software.planCriteria;
    #physicalDetail allocation step_SoftwareRealization_planMIL allocate LogicalRealization::SoftwareRealization::planMIL to candidate.software.planMIL;
    #physicalDetail allocation step_SoftwareRealization_executeMIL allocate LogicalRealization::SoftwareRealization::executeMIL to candidate.software.executeMIL;
    #executionHost allocation external_SoftwareRealization_executeMIL allocate candidate.software.executeMIL to candidate.models;
    #physicalDetail allocation step_SoftwareRealization_receiveMIL allocate LogicalRealization::SoftwareRealization::receiveMIL to candidate.software.receiveMIL;
    #physicalDetail allocation step_SoftwareRealization_preserveMIL allocate LogicalRealization::SoftwareRealization::preserveMIL to candidate.software.preserveMIL;
    #physicalDetail allocation step_SoftwareRealization_assessMIL allocate LogicalRealization::SoftwareRealization::assessMIL to candidate.software.assessMIL;
    #physicalDetail allocation step_SoftwareRealization_release allocate LogicalRealization::SoftwareRealization::release to candidate.software.release;
    #physicalDetail allocation step_SoftwareRealization_checkRelease allocate LogicalRealization::SoftwareRealization::checkRelease to candidate.software.checkRelease;
    #physicalDetail allocation step_SoftwareRealization_coordinate allocate LogicalRealization::SoftwareRealization::coordinate to candidate.software.coordinate;
    #physicalDetail allocation step_SoftwareRealization_codeBuildSil allocate LogicalRealization::SoftwareRealization::codeBuildSil to candidate.software.codeBuildSil;
    #executionHost allocation external_SoftwareRealization_codeBuildSil allocate candidate.software.codeBuildSil to candidate.hostCode;
    #physicalDetail allocation step_SoftwareRealization_receiveSIL allocate LogicalRealization::SoftwareRealization::receiveSIL to candidate.software.receiveSIL;
    #physicalDetail allocation step_SoftwareRealization_preserveSIL allocate LogicalRealization::SoftwareRealization::preserveSIL to candidate.software.preserveSIL;
    #physicalDetail allocation step_SoftwareRealization_checkCurrent allocate LogicalRealization::SoftwareRealization::checkCurrent to candidate.software.checkCurrent;
    #physicalDetail allocation step_SoftwareRealization_compare allocate LogicalRealization::SoftwareRealization::compare to candidate.software.compare;
    #physicalDetail allocation step_SoftwareRealization_credibility allocate LogicalRealization::SoftwareRealization::credibility to candidate.software.credibility;
    #physicalDetail allocation step_SoftwareRealization_assess allocate LogicalRealization::SoftwareRealization::assess to candidate.software.assess;
    #physicalDetail allocation step_SoftwareRealization_present allocate LogicalRealization::SoftwareRealization::present to candidate.software.present;
    #physicalDetail allocation step_SoftwareRealization_approve allocate LogicalRealization::SoftwareRealization::approve to candidate.software.approve;
    #physicalDetail allocation step_SoftwareRealization_checkProducts allocate LogicalRealization::SoftwareRealization::checkProducts to candidate.software.checkProducts;
    #physicalDetail allocation step_SoftwareRealization_retainProducts allocate LogicalRealization::SoftwareRealization::retainProducts to candidate.software.retainProducts;
    #physicalDetail allocation step_SoftwareRealization_block allocate LogicalRealization::SoftwareRealization::block to candidate.software.block;
    #physicalDetail allocation step_SoftwareRealization_retainRaw_receiveMIL allocate LogicalRealization::SoftwareRealization::retainRaw_receiveMIL to candidate.software.retainRaw_receiveMIL;
    #physicalDetail allocation step_SoftwareRealization_retainRaw_receiveSIL allocate LogicalRealization::SoftwareRealization::retainRaw_receiveSIL to candidate.software.retainRaw_receiveSIL;
    #physicalDetail allocation step_SoftwareRealization_rejectRelease allocate LogicalRealization::SoftwareRealization::rejectRelease to candidate.software.rejectRelease;
    #physicalDetail allocation step_ChangeReviewRealization_request allocate LogicalRealization::ChangeReviewRealization::request to candidate.changeReview.request;
    #physicalDetail allocation step_ChangeReviewRealization_receive allocate LogicalRealization::ChangeReviewRealization::receive to candidate.changeReview.receive;
    #physicalDetail allocation step_ChangeReviewRealization_invalidate allocate LogicalRealization::ChangeReviewRealization::invalidate to candidate.changeReview.invalidate;
    #physicalDetail allocation step_ChangeReviewRealization_changeDecision allocate LogicalRealization::ChangeReviewRealization::changeDecision to candidate.changeReview.changeDecision;
    #physicalDetail allocation step_ChangeReviewRealization_checkChange allocate LogicalRealization::ChangeReviewRealization::checkChange to candidate.changeReview.checkChange;
    #physicalDetail allocation step_ChangeReviewRealization_successor allocate LogicalRealization::ChangeReviewRealization::successor to candidate.changeReview.successor;
    #physicalDetail allocation step_ChangeReviewRealization_reassessAdvice allocate LogicalRealization::ChangeReviewRealization::reassessAdvice to candidate.changeReview.reassessAdvice;
    #physicalDetail allocation step_ChangeReviewRealization_planRepeat allocate LogicalRealization::ChangeReviewRealization::planRepeat to candidate.changeReview.planRepeat;
    #physicalDetail allocation step_ChangeReviewRealization_repeat allocate LogicalRealization::ChangeReviewRealization::repeat to candidate.changeReview.repeat;
    #executionHost allocation external_ChangeReviewRealization_repeat allocate candidate.changeReview.repeat to candidate.models;
    #physicalDetail allocation step_ChangeReviewRealization_receiveResult allocate LogicalRealization::ChangeReviewRealization::receiveResult to candidate.changeReview.receiveResult;
    #physicalDetail allocation step_ChangeReviewRealization_preserve allocate LogicalRealization::ChangeReviewRealization::preserve to candidate.changeReview.preserve;
    #physicalDetail allocation step_ChangeReviewRealization_credibility allocate LogicalRealization::ChangeReviewRealization::credibility to candidate.changeReview.credibility;
    #physicalDetail allocation step_ChangeReviewRealization_retrieve allocate LogicalRealization::ChangeReviewRealization::retrieve to candidate.changeReview.retrieve;
    #physicalDetail allocation step_ChangeReviewRealization_assess allocate LogicalRealization::ChangeReviewRealization::assess to candidate.changeReview.assess;
    #physicalDetail allocation step_ChangeReviewRealization_views allocate LogicalRealization::ChangeReviewRealization::views to candidate.changeReview.views;
    #physicalDetail allocation step_ChangeReviewRealization_prepare allocate LogicalRealization::ChangeReviewRealization::prepare to candidate.changeReview.prepare;
    #physicalDetail allocation step_ChangeReviewRealization_reviewers allocate LogicalRealization::ChangeReviewRealization::reviewers to candidate.changeReview.reviewers;
    #physicalDetail allocation step_ChangeReviewRealization_authority allocate LogicalRealization::ChangeReviewRealization::authority to candidate.changeReview.authority;
    #physicalDetail allocation step_ChangeReviewRealization_checkBaseline allocate LogicalRealization::ChangeReviewRealization::checkBaseline to candidate.changeReview.checkBaseline;
    #physicalDetail allocation step_ChangeReviewRealization_checkDecision allocate LogicalRealization::ChangeReviewRealization::checkDecision to candidate.changeReview.checkDecision;
    #physicalDetail allocation step_ChangeReviewRealization_record allocate LogicalRealization::ChangeReviewRealization::record to candidate.changeReview.record;
    #physicalDetail allocation step_ChangeReviewRealization_retain allocate LogicalRealization::ChangeReviewRealization::retain to candidate.changeReview.retain;
    #physicalDetail allocation step_ChangeReviewRealization_holdChange allocate LogicalRealization::ChangeReviewRealization::holdChange to candidate.changeReview.holdChange;
    #physicalDetail allocation step_ChangeReviewRealization_holdReview allocate LogicalRealization::ChangeReviewRealization::holdReview to candidate.changeReview.holdReview;
    #physicalDetail allocation step_ChangeReviewRealization_rejectReview allocate LogicalRealization::ChangeReviewRealization::rejectReview to candidate.changeReview.rejectReview;
    #physicalDetail allocation step_ChangeReviewRealization_retainRaw_receiveResult allocate LogicalRealization::ChangeReviewRealization::retainRaw_receiveResult to candidate.changeReview.retainRaw_receiveResult;
    #physicalDetail allocation step_ReplayRealization_request allocate LogicalRealization::ReplayRealization::request to candidate.replayRun.request;
    #physicalDetail allocation step_ReplayRealization_prepare allocate LogicalRealization::ReplayRealization::prepare to candidate.replayRun.prepare;
    #physicalDetail allocation step_ReplayRealization_execute allocate LogicalRealization::ReplayRealization::execute to candidate.replayRun.execute;
    #executionHost allocation external_ReplayRealization_execute allocate candidate.replayRun.execute to candidate.models;
    #physicalDetail allocation step_ReplayRealization_receive allocate LogicalRealization::ReplayRealization::receive to candidate.replayRun.receive;
    #physicalDetail allocation step_ReplayRealization_preserve allocate LogicalRealization::ReplayRealization::preserve to candidate.replayRun.preserve;
    #physicalDetail allocation step_ReplayRealization_compare allocate LogicalRealization::ReplayRealization::compare to candidate.replayRun.compare;
    #physicalDetail allocation step_ReplayRealization_retain allocate LogicalRealization::ReplayRealization::retain to candidate.replayRun.retain;
    #physicalDetail allocation step_ReplayRealization_missing allocate LogicalRealization::ReplayRealization::missing to candidate.replayRun.missing;
    #physicalDetail allocation step_ReplayRealization_retainRaw_receive allocate LogicalRealization::ReplayRealization::retainRaw_receive to candidate.replayRun.retainRaw_receive;
    #physicalDetail allocation step_CalibrationRealization_supply allocate LogicalRealization::CalibrationRealization::supply to candidate.calibration.supply;
    #physicalDetail allocation step_CalibrationRealization_receive allocate LogicalRealization::CalibrationRealization::receive to candidate.calibration.receive;
    #physicalDetail allocation step_CalibrationRealization_checkData allocate LogicalRealization::CalibrationRealization::checkData to candidate.calibration.checkData;
    #physicalDetail allocation step_CalibrationRealization_propose allocate LogicalRealization::CalibrationRealization::propose to candidate.calibration.propose;
    #physicalDetail allocation step_CalibrationRealization_choose allocate LogicalRealization::CalibrationRealization::choose to candidate.calibration.choose;
    #physicalDetail allocation step_CalibrationRealization_prepareChange allocate LogicalRealization::CalibrationRealization::prepareChange to candidate.calibration.prepareChange;
    #physicalDetail allocation step_CalibrationRealization_invalidate allocate LogicalRealization::CalibrationRealization::invalidate to candidate.calibration.invalidate;
    #physicalDetail allocation step_CalibrationRealization_checkChange allocate LogicalRealization::CalibrationRealization::checkChange to candidate.calibration.checkChange;
    #physicalDetail allocation step_CalibrationRealization_successor allocate LogicalRealization::CalibrationRealization::successor to candidate.calibration.successor;
    #physicalDetail allocation step_CalibrationRealization_reassess allocate LogicalRealization::CalibrationRealization::reassess to candidate.calibration.reassess;
    #physicalDetail allocation step_CalibrationRealization_planRepeat allocate LogicalRealization::CalibrationRealization::planRepeat to candidate.calibration.planRepeat;
    #physicalDetail allocation step_CalibrationRealization_repeat allocate LogicalRealization::CalibrationRealization::repeat to candidate.calibration.repeat;
    #executionHost allocation external_CalibrationRealization_repeat allocate candidate.calibration.repeat to candidate.models;
    #physicalDetail allocation step_CalibrationRealization_receiveResult allocate LogicalRealization::CalibrationRealization::receiveResult to candidate.calibration.receiveResult;
    #physicalDetail allocation step_CalibrationRealization_preserve allocate LogicalRealization::CalibrationRealization::preserve to candidate.calibration.preserve;
    #physicalDetail allocation step_CalibrationRealization_credibility allocate LogicalRealization::CalibrationRealization::credibility to candidate.calibration.credibility;
    #physicalDetail allocation step_CalibrationRealization_assess allocate LogicalRealization::CalibrationRealization::assess to candidate.calibration.assess;
    #physicalDetail allocation step_CalibrationRealization_retainEvidence allocate LogicalRealization::CalibrationRealization::retainEvidence to candidate.calibration.retainEvidence;
    #physicalDetail allocation step_CalibrationRealization_retain allocate LogicalRealization::CalibrationRealization::retain to candidate.calibration.retain;
    #physicalDetail allocation step_CalibrationRealization_unusable allocate LogicalRealization::CalibrationRealization::unusable to candidate.calibration.unusable;
    #physicalDetail allocation step_CalibrationRealization_retainRaw_receiveResult allocate LogicalRealization::CalibrationRealization::retainRaw_receiveResult to candidate.calibration.retainRaw_receiveResult;
    @ComparisonMechanism about C01::checkDraft { mop = "MOP-FR02"; mechanism = "Native requirement fields and Python rules support proposed semantic checks, separate from Jev."; operation = CandidateCDT::C01::checkDraft meta SysML::ActionUsage; }
    dependency comparison_MOP_FR02 from FrameworkRequirements::MOP_FR02 to CandidateCDT::C01::checkDraft;
    @ComparisonMechanism about C01::recommend { mop = "MOP-FR03"; mechanism = "Native subjects, assumptions, quantities and bindings feed required Jev analysis/V&V suggestions for engineer eligibility checks."; operation = CandidateCDT::C01::recommend meta SysML::ActionUsage; }
    dependency comparison_MOP_FR03 from FrameworkRequirements::MOP_FR03 to CandidateCDT::C01::recommend;
    @ComparisonMechanism about C03::planAnalysis { mop = "MOP-FR18"; mechanism = "Native quantity/calculation/parameter bindings -> Python specialist EPS/battery analysis -> USD and numerical whole-CUBICS Omniverse mappings."; operation = CandidateCDT::C03::planAnalysis meta SysML::ActionUsage; }
    dependency comparison_MOP_FR18 from FrameworkRequirements::MOP_FR18 to CandidateCDT::C03::planAnalysis;
    @ComparisonMechanism about C03::mapFPrime { mop = "MOP-FR34"; mechanism = "Native EPS interface fields -> checked Python semantic mappings -> required versioned F Prime profile."; operation = CandidateCDT::C03::mapFPrime meta SysML::ActionUsage; }
    dependency comparison_MOP_FR34 from FrameworkRequirements::MOP_FR34 to CandidateCDT::C03::mapFPrime;
    @ComparisonMechanism about C06::invalidate { mop = "MOP-FR30"; mechanism = "Native, COTS/source, classifier/rubric and rule revisions invalidate current/pending advice before latest-context reassessment."; operation = CandidateCDT::C06::invalidate meta SysML::ActionUsage; }
    dependency comparison_MOP_FR30 from FrameworkRequirements::MOP_FR30 to CandidateCDT::C06::invalidate;
    @ComparisonMechanism about C06::prepareReplay { mop = "MOP-FR10"; mechanism = "Native baselines, Python/environment/solver versions, exact COTS/source revisions, F Prime host dependencies and raw outputs."; operation = CandidateCDT::C06::prepareReplay meta SysML::ActionUsage; }
    dependency comparison_MOP_FR10 from FrameworkRequirements::MOP_FR10 to CandidateCDT::C06::prepareReplay;
}
