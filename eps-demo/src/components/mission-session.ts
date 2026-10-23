import { useEffect, useRef, useState } from 'react';
import catalogueData from '../data/missions.json';
import { acceptAltitude, queryProblem, searchLexical } from '../mission-assist/retrieval';
import type { MissionCatalogue, MissionSearchResult, RetrievalMethod } from '../mission-assist/types';

export const missionCatalogue = catalogueData as MissionCatalogue;
export interface MissionSearchContext { query:string; generation:number; method:RetrievalMethod }
export function missionSearchIsCurrent(context:MissionSearchContext|null,query:string,generation:number,method:RetrievalMethod):boolean {
  return !!context&&context.query===query&&context.generation===generation&&context.method===method;
}
/** Navigation preserves this session. Explicit workspace replacement invalidates it. */
export function useMissionSession(query:string,onQuery:(value:string)=>void,generation=0) {
  const [method,setMethodState]=useState<RetrievalMethod>('semantic-qwen');
  const [response,setResponse]=useState<{result:MissionSearchResult;context:MissionSearchContext}|null>(null);
  const [error,setError]=useState<string|null>(null);
  const [busy,setBusy]=useState(false);
  const [accepted,setAccepted]=useState<string|null>(null);
  const request=useRef<AbortController|null>(null), version=useRef(0);
  const invalidate=()=>{version.current++;request.current?.abort();setResponse(null);setError(null);setBusy(false);setAccepted(null);};
  const reset=()=>{invalidate();setMethodState('semantic-qwen');};
  useEffect(()=>()=>{version.current++;request.current?.abort();},[]);
  useEffect(()=>{invalidate();},[query,generation]);
  const changeQuery=(value:string)=>{
    if(value.length>2000){setError('Mission ConOps is limited to 2,000 characters. Shorten the query before applying this edit.');return;}
    invalidate();onQuery(value);
  };
  const setMethod=(value:RetrievalMethod)=>{invalidate();setMethodState(value);};
  const search=async()=>{
    invalidate();const current=version.current, controller=new AbortController();request.current=controller;setBusy(true);
    const context={query,generation,method};
    try {
      const problem=queryProblem(query);
      const next:MissionSearchResult=problem?{status:'abstained',matches:[],reason:problem,method}:method==='lexical-tfidf'?searchLexical(query,missionCatalogue):await(await import('../mission-assist/semantic')).searchSemantic(query,missionCatalogue,controller.signal);
      if(current===version.current)setResponse({result:next,context});
    } catch(cause) {if(current===version.current)setError(`Retrieval unavailable. ${method==='semantic-qwen'?'Start the optional local Qwen service or explicitly choose lexical mode. ':''}${cause instanceof Error?cause.message:String(cause)}`);}
    finally {if(current===version.current)setBusy(false);}
  };
  const result=missionSearchIsCurrent(response?.context??null,query,generation,method)?response!.result:null;
  const canAccept=(id:string)=>accepted===id&&!!result?.matches.some(match=>match.mission.id===id&&typeof match.mission.orbit.altitudeKm?.value==='number');
  const accept=(id:string)=>{
    const match=result?.matches.find(match=>match.mission.id===id);
    if(!match||!canAccept(id))return null;
    const receipt=acceptAltitude(match);
    setAccepted(null);
    return receipt;
  };
  return {query,changeQuery,method,setMethod,result,error,busy,search,accepted,setAccepted,canAccept,accept,reset};
}
export type MissionSession=ReturnType<typeof useMissionSession>;
