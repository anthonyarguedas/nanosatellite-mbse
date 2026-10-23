import type { Role } from '../types.ts';

export const PROFILE_REVISION = 'sourced-comparison-1.1-function-applicability';
export const COMPARISON_SCOPE = 'Sourced product comparison only. Typical values retain their conditions. This profile does not establish installed compatibility, mission applicability, architecture feasibility or qualification.';
export const ROLES: readonly Role[] = ['solar', 'battery', 'conditioning', 'distribution', 'processor', 'software'];
export interface SpecDefinition { unit: string; type: 'number' | 'text'; positive?: boolean; integer?: boolean; fraction?: boolean; nonnegative?: boolean }
const n = (unit: string, options: Partial<SpecDefinition> = {}): SpecDefinition => ({ unit, type: 'number', nonnegative: true, ...options });
const t = (): SpecDefinition => ({ unit: '1', type: 'text' });
export const SPEC_DEFINITIONS: Readonly<Record<string, SpecDefinition>> = {
  ...Object.fromEntries(['powerBolW', 'powerEolW', 'maxInputW', 'idlePowerW', 'heaterPowerW', 'maxChargeW', 'maxDischargeW'].map(k => [k, n('W')])),
  ...Object.fromEntries(['vmpBolV', 'vmpEolV', 'vocV', 'vocEolV', 'voltageMinV', 'voltageNominalV', 'voltageMaxV', 'inputMinV', 'inputMaxV', 'absoluteInputMaxV', 'distributionSupplyMinV', 'distributionSupplyMaxV', 'processorSupplyMinV', 'processorSupplyMaxV', 'chargeVoltageV'].map(k => [k, n('V', { positive: true })])),
  ...Object.fromEntries(['impBolA', 'impEolA', 'iscA', 'iscEolA', 'maxChargeA', 'maxDischargeA', 'maxPvInputCurrentA', 'standbyCurrentA', 'sourcedChargeCurrentMinTypMaxA', 'sourcedDischargeCurrentMinTypMaxA', 'maxInputA'].map(k => [k, n('A')])),
  ...Object.fromEntries(['efficiency', 'retainedEnergyFraction', 'retainedChargeFraction', 'chargeEfficiency', 'dischargeEfficiency', 'coulombicChargeEfficiency', 'coulombicDischargeEfficiency', 'powerRemainingFactor'].map(k => [k, n('1', { fraction: true })])),
  ...Object.fromEntries(['widthM', 'heightM', 'depthM'].map(k => [k, n('m', { positive: true })])),
  ...Object.fromEntries(['chargeTemperatureMinK', 'chargeTemperatureMaxK', 'dischargeTemperatureMinK', 'dischargeTemperatureMaxK', 'operatingTemperatureMinK', 'operatingTemperatureMaxK'].map(k => [k, n('K', { positive: true })])),
  ...Object.fromEntries(['seriesCells', 'parallelCells', 'pvInputChannels', 'inputChannelCount', 'outputChannelCount', 'chargerSeriesCells'].map(k => [k, n('count', { positive: true, integer: true })])),
  ...Object.fromEntries(['programBytes', 'dataBytes', 'availableProgramBytes', 'availableDataBytes', 'requiredProgramBytes', 'requiredDataBytes'].map(k => [k, n('byte', { integer: true })])),
  ...Object.fromEntries(['taskPeriodsS', 'executionBoundsS', 'deadlinesS'].map(k => [k, n('s', { positive: true })])),
  ...Object.fromEntries(['providedFunctions', 'configurationDescription', 'includedItems', 'requiredExternalItems', 'cellTechnology', 'solarFeatures', 'chemistry', 'chargePolicy', 'chargerChemistry', 'chargeTermination', 'batteryFeatures', 'conditioningMode', 'conditioningApplicability', 'converterTopology', 'outputRails', 'modeConsumption', 'circuitFunction', 'channelGroups', 'controlMethod', 'defaultOutputStates', 'protectionBehavior', 'processorDescription', 'sensingIO', 'dataInterfaces', 'watchdog', 'firmwareReservations', 'softwareRelease', 'license', 'supportedHosts', 'serviceDefinitions', 'softwareBehavior', 'deliveryArtifact', 'buildConfiguration', 'cycleLifeModel', 'voltageChargeModel', 'solarOperatingExtrema', 'temperatureModel', 'conversionEnvelope', 'lossMap', 'startupEnvelope', 'protectionTiming', 'connectorMapping', 'qualificationEvidence', 'schedulingEvidence', 'procurementAvailability'].map(k => [k, t()])),
  massKg: n('kg', { positive: true }), energyWh: n('Wh', { positive: true }), chargeAh: n('Ah', { positive: true }), priceUsd: n('USD'), cycleLife: n('cycles', { positive: true }),
  absoluteChargeTemperatureC: n('°C', { nonnegative: false }), absoluteDischargeTemperatureC: n('°C', { nonnegative: false }),
  tempCoefficientVocBolVPerK: n('V/K', { nonnegative: false }), tempCoefficientVmpBolVPerK: n('V/K', { nonnegative: false }),
  tempCoefficientIscBolAPerK: n('A/K', { nonnegative: false }), tempCoefficientImpBolAPerK: n('A/K', { nonnegative: false }),
  activeAreaM2: n('m²', { positive: true }), eolFluencePerCm2: n('e−/cm²'), clockHz: n('Hz', { positive: true }), internalResistanceOhm: n('Ω'),
};
export interface CoverageRule { branch?: 'pv-receiver' | 'load-converter'; id: string; label: string; anyOf: readonly (readonly string[])[]; levels?: readonly string[]; condition?: 'solar-bol' | 'solar-eol' | 'battery-energy' | 'battery-current' | 'rails' | 'eps-services'; when?: { key: string; contains: string; orKey?: string } }
const rule = (key: string, label = key.replace(/([A-Z])/g, ' $1').replace(/^./, char => char.toUpperCase())): CoverageRule => ({ id: key, label, anyOf: [[key]] });
const any = (id: string, label: string, ...choices: string[][]): CoverageRule => ({ id, label, anyOf: choices });
const common = ['providedFunctions', 'configurationDescription', 'includedItems', 'requiredExternalItems'].map(k => rule(k));
const hardware = [...common, ...['massKg', 'widthM', 'heightM', 'depthM'].map(k => rule(k))];
const temperatures = ['operatingTemperatureMinK', 'operatingTemperatureMaxK', 'connectorMapping', 'qualificationEvidence'];
export interface RoleProfile { core: readonly CoverageRule[]; richer: readonly CoverageRule[] }
const profiles: Record<Role, RoleProfile> = {
  solar: { core: [...hardware, rule('cellTechnology'), { ...rule('activeAreaM2'), levels: ['cell'] },
    { id: 'bol', label: 'Conditioned BOL MPP and open/short circuit ratings', anyOf: [['powerBolW', 'vmpBolV', 'impBolA', 'vocV', 'iscA']], condition: 'solar-bol' },
    { ...any('eol', 'Conditional EOL power or matching MPP pair', ['powerEolW'], ['vmpEolV', 'impEolA']), condition: 'solar-eol' }, rule('solarFeatures')],
    richer: ['solarOperatingExtrema', 'temperatureModel', ...temperatures].map(k => rule(k)) },
  battery: { core: [...hardware, ...['chemistry', 'seriesCells', 'parallelCells', 'energyWh', 'chargeAh', 'voltageMinV', 'voltageNominalV', 'voltageMaxV', 'maxChargeA', 'maxDischargeA', 'chargeTemperatureMinK', 'chargeTemperatureMaxK', 'dischargeTemperatureMinK', 'dischargeTemperatureMaxK', 'chargePolicy', 'batteryFeatures'].map(k => ({ ...rule(k), ...(k === 'energyWh' ? { condition: 'battery-energy' as const } : ['maxChargeA', 'maxDischargeA'].includes(k) ? { condition: 'battery-current' as const } : {}) }))],
    richer: ['cycleLife', 'cycleLifeModel', 'retainedEnergyFraction', 'retainedChargeFraction', 'chargeEfficiency', 'dischargeEfficiency', 'coulombicChargeEfficiency', 'coulombicDischargeEfficiency', 'internalResistanceOhm', 'voltageChargeModel', ...temperatures].map(k => rule(k)) },
  conditioning: { core: [...hardware, ...['conditioningMode', 'converterTopology', 'inputMinV', 'inputMaxV'].map(k => rule(k)), { ...any('inputCurrent', 'Permissible PV source current', ['maxPvInputCurrentA'], ['maxInputA']), branch: 'pv-receiver' }, any('inputChannels', 'Input channel organization', ['pvInputChannels'], ['inputChannelCount']), { ...rule('outputRails'), condition: 'rails' }, any('consumption', 'Mode/idle consumption', ['modeConsumption'], ['idlePowerW']),
    ...['chargePolicy', 'chargerChemistry', 'chargerSeriesCells', 'chargeVoltageV', 'maxChargeA', 'chargeTermination', 'chargeTemperatureMinK', 'chargeTemperatureMaxK'].map(key => ({ ...rule(key), when: { key: 'conditioningMode', orKey: 'providedFunctions', contains: 'charg' } }))],
    richer: ['maxInputW', 'absoluteInputMaxV', 'conversionEnvelope', 'lossMap', 'startupEnvelope', ...temperatures].map(k => rule(k)) },
  distribution: { core: [...hardware, ...['circuitFunction', 'distributionSupplyMinV', 'distributionSupplyMaxV', 'outputRails', 'outputChannelCount', 'channelGroups', 'controlMethod', 'defaultOutputStates', 'protectionBehavior'].map(k => ({ ...rule(k), ...(k === 'outputRails' ? { condition: 'rails' as const } : {}) })), any('consumption', 'Mode/idle consumption', ['modeConsumption'], ['idlePowerW'])],
    richer: ['lossMap', 'protectionTiming', ...temperatures].map(k => rule(k)) },
  processor: { core: [...hardware, ...['processorDescription', 'clockHz', 'programBytes', 'dataBytes', 'processorSupplyMinV', 'processorSupplyMaxV', 'sensingIO', 'dataInterfaces', 'watchdog'].map(k => rule(k)), any('consumption', 'Mode consumption or included host consumption', ['modeConsumption'], ['idlePowerW'])],
    richer: ['firmwareReservations', 'availableProgramBytes', 'availableDataBytes', ...temperatures].map(k => rule(k)) },
  software: { core: [...common, ...['softwareRelease', 'license', 'supportedHosts', 'serviceDefinitions', 'softwareBehavior', 'deliveryArtifact', 'buildConfiguration'].map(k => ({ ...rule(k), ...(k === 'serviceDefinitions' ? { condition: 'eps-services' as const } : {}) }))],
    richer: ['requiredProgramBytes', 'requiredDataBytes', 'taskPeriodsS', 'executionBoundsS', 'deadlinesS', 'schedulingEvidence'].map(k => rule(k)) },
};
function freeze<T>(value: T): T { if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; }
/** Frozen before source integration. Missing richer facts never change core requirements. */
export const ROLE_PROFILES: Readonly<Record<Role, RoleProfile>> = freeze(profiles);
freeze(SPEC_DEFINITIONS);
