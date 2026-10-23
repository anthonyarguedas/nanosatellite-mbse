import { useEffect, useRef, useState } from 'react';
import type { Catalog, Workspace } from '../types';
import { buildKiCadExport, buildReviewedKiCadRules, getKiCadArchitectureFingerprint, getKiCadReadiness, type KiCadExport } from '../kicad';
import { checkedRules, ruleTemplate, saveBlob, saveProject } from './KiCadPanel';

export function useKiCadSession(workspace:Workspace,catalog:Catalog,generation=0) {
  const [storedRules,setRules]=useState<{result:KiCadExport;fingerprint:string;generation:number}|null>(null);
  const version=useRef(0);
  const rules=storedRules?.generation===generation?storedRules:null;
  const [error,setError]=useState<string|null>(null);
  const reset=()=>{version.current++;setRules(null);setError(null);};
  useEffect(()=>{reset();},[generation]);
  useEffect(()=>()=>{version.current++;},[]);
  const fingerprint=getKiCadArchitectureFingerprint(workspace,catalog), readiness=getKiCadReadiness(workspace,catalog);
  const review=()=>{try{saveProject(buildKiCadExport(workspace,catalog),'orbitwork-kicad-review.zip');setError(null);}catch(e){setError(e instanceof Error?e.message:String(e));}};
  const template=()=>saveBlob(new Blob([JSON.stringify(ruleTemplate(workspace,catalog),null,2)],{type:'application/json'}),'orbitwork-rule-input-template.json');
  const importRules=async(file:File)=>{
    const current=++version.current;
    setError(null);setRules(null);
    try {if(file.size>2_000_000)throw Error('Rule profiles must be smaller than 2 MB.');const input=checkedRules(JSON.parse(await file.text()),catalog);const result=buildReviewedKiCadRules(input,fingerprint);if(current===version.current)setRules({result,fingerprint,generation});}
    catch(e){if(current===version.current)setError(e instanceof TypeError?'Incomplete profile. Fill every required section and approved dimension.':e instanceof Error?e.message:String(e));}
  };
  const download=()=>{if(rules&&rules.fingerprint===fingerprint&&readiness.ready)saveProject(rules.result,'orbitwork-reviewed-rule-sidecars.zip');};
  return {rules,error,fingerprint,readiness,review,template,importRules,download,reset};
}
export type KiCadSession=ReturnType<typeof useKiCadSession>;
