#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = []
# ///
"""Check released physical designs with licensed native semantics.

Actual allocations map logical steps to configured performed steps, then to
configured physical operations. IO contracts remain separate. Frozen native
bindings, typed flow ends, guards, dominance, rejection routes and custom roles
are checked. This is planned specification checking, never empirical V&V.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

TOOL = Path('/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py')
FILES = tuple(f'{n}.sysml' for n in ('00-domain','01-concerns','02-needs-context','03-requirements','04-logical','05-verification','06-system-context','07-report-views','08-physical-vocabulary','09-scenarios','10-interface-views','11-logical-responsibilities')) + tuple(f'candidates/{n}.sysml' for n in ('comet','custom','git-yaml','nanospace','valispace'))
CONTROL_INVARIANTS = {'compatibility','mandatory_profiles','coding_release','review_authority','guidance_currency','guidance_application','change_authority'}
NEGATIVE_INVARIANTS = CONTROL_INVARIANTS | {'wrong_owner','missing_FR','missing_integration','missing_custom_role','false_satisfaction','history_masks','replay_dependencies'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def qn(element):
    return str(element.qualified_name) if element is not None and element.qualified_name else ''


def chain(feature):
    return list(feature.chaining_features) or [feature]


def compact(text):
    return re.sub(r'\s+', '', text)


@lru_cache(maxsize=4096)
def effective_features(context):
    features = list(context.features)
    redefined = {r.redefined_feature for f in features for r in f.owned_redefinitions}
    return [f for f in features if f not in redefined]


@lru_cache(maxsize=4096)
def feature(context, name):
    matches = [f for f in effective_features(context) if f.name == name]
    require(len(matches) == 1, f'{qn(context)}: ambiguous/missing actual feature {name}')
    return matches[0]


@lru_cache(maxsize=1024)
def control_edges(context):
    features = effective_features(context)
    def current(endpoint):
        matches = [f for f in features if f == endpoint or (f.name == endpoint.name and f.conforms(endpoint))]
        matches = [f for f in matches if not any(g != f and g.conforms(f) and not f.conforms(g) for g in matches)]
        require(len(matches) == 1, f'{qn(context)}: unresolved control endpoint {qn(endpoint)}')
        return matches[0]
    result = []
    for edge in features:
        if type(edge).__name__ == 'SuccessionAsUsage':
            result.extend((current(edge.source_feature), current(t), edge) for t in edge.target_features)
        elif type(edge).__name__ == 'TransitionUsage':
            result.append((current(edge.source), current(edge.target), edge))
    return result


def reachable(context, removed=(), initial=None):
    edges = control_edges(context); removed = set(removed)
    reached = {feature(context, 'start')} if initial is None else {initial}
    while True:
        update = reached | {t for s,t,e in edges if s in reached and s not in removed and t not in removed and e not in removed}
        if update == reached:
            return reached
        reached = update


def require_dominates(context, dominator, target):
    require(target in reachable(context), f'{qn(context)}: disconnected performed action {target.name}')
    require(target not in reachable(context, (dominator,)), f'{qn(context)}: actual execution/control bypass of {getattr(dominator,"name",None)}')


def mutate_once(path, old, new, name):
    text = path.read_text(); matches = text.count(old)
    require(old != new and matches == 1, f'Negative mutation must change exactly one current selector: {name} (matches={matches})')
    path.write_text(text.replace(old,new,1))
    return matches


def current_records(root, enforce_snapshot=True):
    audit = module(root.parent/'tools/audit_report.py','current_physical_report_audit')
    _,fr,*_ = audit.current_trace(root.parent)
    logical = audit.load(root.parent/'traceability/logical-architecture.json')
    try:
        trade,candidates = audit.audit_candidate_records(root.parent,fr,logical,require_native=True)
    except AssertionError as error:
        raise ValueError(str(error)) from error
    for record in candidates.values():
        c = record['native_contract']
        require(c and c['schema']=='task7-current-physical-v1' and c['status']=='reconciled with final native contract','Final physical native contract not reconciled')
        require({r['invariant'] for r in c['controls']} >= CONTROL_INVARIANTS,'Missing meaningful authority/admission/currency control checks')
        require(c['bindings'] and c['record_fields'] and c['derived_values'],'Missing raw-history/replay and actual binding checks')
        require(len(c['procedure_performers'])==24 and len(c['framework_calls'])==118,'Missing performed procedure/framework exports')
        require({r['FR'] for r in c['behavior_calls']}==set(fr),'Allocated operations lack performed current behavior calls')
        if enforce_snapshot:
            require(c['source_sha256'] and all(audit.sha(root.parent/p)==h for p,h in c['source_sha256'].items()),'Physical native source identity mismatch')
    if enforce_snapshot:
        audit.audit_final_logical_ledger(root.parent,fr,logical,audit.load(root.parent/'traceability/framework-baseline.json')['logical_io_contract'],require_sources=True)
    return audit,fr,logical,trade,candidates


def flow_record(native, flow):
    """Resolved flow ends also support direct action parameters without a prefix."""
    ends={e.name:e for e in flow.owned_features if type(e).__name__=='FlowEnd'}
    require(set(ends)=={'source','target'},'Physical flow lacks two native ends')
    targets=list(flow.target_features)
    prefixes={'source':flow.source_feature,'target':targets[0] if targets else None}
    record={'native':qn(flow),'ends':{}}
    for side,end in ends.items():
        parameters=list(end.owned_features)
        require(len(parameters)==1,'Physical flow needs one declared parameter')
        redefinitions=list(parameters[0].owned_redefinitions)
        require(len(redefinitions)==1,'Physical flow parameter declaration is unresolved')
        declaration=redefinitions[0].redefined_feature
        record['ends'][side]={'context':[qn(x) for x in chain(prefixes[side])] if prefixes[side] is not None else [],'parameter':qn(declaration)}
    payloads=list(flow.payload_types)
    record['payload_basis']='explicit flow type' if payloads else 'resolved producer parameter type'
    if not payloads:payloads=list(native.by[record['ends']['source']['parameter']].types)
    leaves=[t for t in payloads if not any(t!=other and other.conforms(t) and not t.conforms(other) for other in payloads)]
    require(len(leaves)==1,'Physical flow payload missing/ambiguous')
    record['payload']=qn(leaves[0])
    for side,end in record['ends'].items():
        require(any(t.conforms(leaves[0]) if side=='source' else leaves[0].conforms(t) for t in native.by[end['parameter']].types),'Physical flow payload/parameter conformance lost')
    return record


def guard_records(context, api):
    return [{'source':s.name,'target':t.name,'expression':compact(api.pprint(e.guard_expression))}
            for s,t,e in control_edges(context) if type(e).__name__=='TransitionUsage' and e.guard_expression is not None]


def check_controls(contract, by, api):
    for row in contract['controls']:
        context=by[row['context']]
        gate=feature(context,row['gate']); target=feature(context,row['target'])
        require(gate.guard_expression is not None and compact(api.pprint(gate.guard_expression))==compact(row['expression']) and gate.target.name==target.name,'Lost native safety guard/target: '+row['invariant'])
    for row in contract['dominance']:
        context=by[row['context']]
        require_dominates(context,feature(context,row['gate']),feature(context,row['target']))
    for row in contract['guard_contexts']:
        context=by[row['context']]
        require(guard_records(context,api)==row['guards'],'Lost native physical admission/rejection guard')
        for protected in row['protected']:
            edges=[e for s,t,e in control_edges(context) if s.name==protected['source'] and t.name==protected['target'] and type(e).__name__=='TransitionUsage' and e.guard_expression is not None and compact(api.pprint(e.guard_expression))==protected['expression']]
            require(len(edges)==1,'Missing actual physical admission edge')
            target=feature(context,protected['target']); require_dominates(context,edges[0],target)
            if protected.get('failure'):
                failure=feature(context,protected['failure'])
                require(failure in reachable(context,(edges[0],)) and target not in reachable(context,(edges[0],),initial=failure),'Rejected admission can execute or lost failure retention')
    for row in contract['derived_values']:
        f=feature(by[row['context']],row['feature'])
        expression=compact(api.pprint(f.feature_value_expression)) if f.feature_value_expression is not None else None
        require(expression==row['expression'],'Physical currency/replay/profile result is disconnected')


def check_custom(record, native, logical_checker):
    by=native.by; c=record['native_contract']['custom_definitions']
    expected={'requirements':('RequirementDefinition',4),'requirement_usages':('RequirementUsage',4),'calculations':('CalculationDefinition',8),'constraints':('ConstraintDefinition',1)}
    for name,(kind,count) in expected.items():
        require(len(c[name])==count and all(q in by and type(by[q]).__name__==kind for q in c[name]),'Missing substantive custom native '+name)
    require(c['assumptions'] and all(type(by[q]).__name__=='ConstraintUsage' for q in c['assumptions']),'Missing native EPS assumptions')
    require(c['quantity_properties'] and all(type(by[q]).__name__=='AttributeUsage' and any('ISQ' in qn(t) or 'Quantities' in qn(t) for t in by[q].types) for q in c['quantity_properties']),'Missing quantity-typed custom properties')
    require(c['cots_records'] and c['cots_fields'] and c['parameter_bindings'],'Missing maintained COTS/native parametric links')
    require(c['analysis_operations'] and c['jev_calls'] and not set(c['analysis_operations']) & set(c['jev_calls']),'Classifier substituted for numerical execution')
    for q in c['analysis_operations']+c['jev_calls']:
        require(type(by[q]).__name__=='PerformActionUsage','Custom role is not actually performed')
    for row in c['required_parts']:
        f=feature(by[row['context']],row['feature'])
        require(logical_checker.multiplicity(f)=='1' and by[row['type']] in f.types,'Custom Jev/Python/COTS role is optional or disconnected')
    for name,role in record['custom_roles'].items():
        require(role['native_elements'] and all(q in by for q in role['native_elements']),'Missing custom native role: '+name)


def check(tool,root,validation=None,enforce_snapshot=True):
    effective_features.cache_clear(); feature.cache_clear(); control_edges.cache_clear()
    audit,fr,ledger,trade,candidates=current_records(root,enforce_snapshot)
    lc=module(root/'check_logical_responsibilities.py','physical_logical_native_helpers')
    native=lc.Native(tool,root,FILES); by=native.by; elements=native.elements; api=native.api
    require(not any(type(e).__name__=='SatisfyRequirementUsage' for e in elements),'False native satisfaction assertion')
    allocations=[e for e in elements if type(e).__name__=='AllocationUsage']
    rows=audit.unique(ledger['allocations'],'logical allocation','FR'); results={}
    def allocation_matches(source,target,owned):
        return any([qn(x) for x in chain(e.source_feature)]==source and [qn(x) for x in chain(list(e.target_features)[0])]==target for e in owned)
    def actual_bindings(context):
        return [lc.binding_record(f) for f in effective_features(context) if type(f).__name__=='BindingConnectorAsUsage']
    for cid,record in candidates.items():
        pkg=audit.CANDIDATES[cid][1]; c=record['native_contract']; configuration=by[pkg+'::Configuration']; instance=by[record['native']]
        require(configuration.conforms(by['FrameworkLogical::LogicalFramework']),'Candidate changes current logical framework')
        parts={p.name:p for p in configuration.owned_features if type(p).__name__=='PartUsage' and re.fullmatch(r'L\d{2}',p.name or '')}
        require(set(parts)==set(audit.GROUPS),'Six exact physical components required')
        own=[e for e in allocations if qn(e.owner)==pkg]
        primary=[e for e in own if native.annotations(e,'PhysicalVocabulary::physicalPrimary')]
        require(len(primary)==40,'Exactly one physical primary allocation per FR required')
        declared=audit.unique(record['allocations'],'physical allocation','FR'); seen=set()
        for e in primary:
            requirement=e.source_feature; rid=requirement.name.replace('_','-'); require(rid in fr and rid not in seen,'Duplicate/retired physical primary FR'); seen.add(rid)
            row=declared[rid]; common=rows[rid]; lid=common['primary']
            require(chain(list(e.target_features)[0])==[instance,parts[lid]],'Wrong physical FR owner')
            meta=native.annotations(e,'PhysicalVocabulary::PhysicalAllocation'); require(len(meta)==1,'Missing physical allocation/check metadata')
            fields=native.values(meta[0]); operation=fields['operation'].element
            definition=by[next(r['type'] for r in record['components'] if r['logical']==lid)]
            require(definition in parts[lid].types and operation.owner==definition and qn(operation)==row['operation'] and by[common['operation']] in native.dependencies(requirement) and operation.conforms(by[common['operation']]),'Disconnected physical FR operation: '+cid+' '+rid)
            require(fields['plannedCheck']==row['planned_check']==fr[rid]['planned_check'] and fields['rationale'],'Changed planned check/rationale')
            support=[s for s in own if s.source_feature==requirement and native.annotations(s,'PhysicalVocabulary::physicalSupport')]
            require(len(support)==len(common['support'])==0,'Invented supporting physical allocation')
        require(seen==set(fr),'Missing physical FR')
        for row in c['component_specifications']:
            definition=by[row['component']]
            metas=native.annotations(definition,'PhysicalVocabulary::ComponentSpecification')
            sources=native.annotations(definition,'FrameworkDomain::SourceRecord')
            require(len(metas)==len(sources)==1 and native.values(metas[0])==row['specification'] and native.values(sources[0])==row['source'] and row['specification']['status']=='proposed/unexecuted','Changed component methods/source or false fulfilment')
        require(len(c['comparison_mechanisms'])==6 and {r['id'] for r in c['comparison_mechanisms']}==set(audit.CRITICAL_MOPS),'Missing native critical-MOP mechanism matrix')
        for row in c['comparison_mechanisms']:
            operation=by[row['native']];metas=native.annotations(operation,'PhysicalVocabulary::ComparisonMechanism')
            require(len(metas)==1 and row['achieved']=='unknown' and type(operation).__name__=='PerformActionUsage','False/missing native comparison mechanism')
            values=native.values(metas[0]);require(values['mop']==row['id'] and values['mechanism']==row['mechanism'] and qn(values['operation'].element)==row['operation']==row['native'] and values.get('achieved','unknown')=='unknown','Unmeasured result or disconnected critical-MOP mechanism')
        for row in c['framework_calls']:
            context=by[row['context']]; call=feature(context,row['feature'])
            require(type(call).__name__=='PerformActionUsage' and call.owned_reference_subsetting is not None and [qn(x) for x in chain(call.referenced_feature)]==row['reference_chain'],'Configured framework call is disconnected')
            require(call in reachable(context),'Configured framework call is unreachable')
            require(allocation_matches(row['allocation_source'],row['allocation_target'],own),'Logical step lacks actual configured physical allocation')
        calls={r['logical_behavior']:r for r in c['framework_calls']}
        for row in c['behavior_calls']:
            require(row['logical_behavior'] in rows[row['FR']]['behaviors'] and row['logical_behavior'] in calls,'FR behavior has no physical performer')
            invoke=by[calls[row['logical_behavior']]['reference_chain'][-1]]
            require(invoke.conforms(by[declared[row['FR']]['operation']]),'FR behavior disconnected from allocated physical operation')
        for row in c['procedure_performers']:
            require(allocation_matches(row['source'],row['target'],own) and allocation_matches(row['actor_source'],row['actor_target'],allocations),'Procedure loses actual engineering/review authority')
            canonical=by[row['source'][0]]
            require(by[row['action_type']] in canonical.types and by[row['target'][-1]].conforms(canonical),'Configured external performer changes its logical actor meaning')
        for row in c['bindings']:
            require(row['binding'] in actual_bindings(by[row['context']]),'Actual native parameter/profile binding lost')
        for row in c['flows']:
            require(flow_record(native,by[row['native']])==row,'Actual physical flow parameter/type route lost')
        for row in c['record_fields']:
            f=by[row['native']]
            expression=compact(api.pprint(f.feature_value_expression)) if f.feature_value_expression is not None else None
            require(by[row['type']] in f.types and lc.multiplicity(f)==row['multiplicity'] and expression==row['expression'],'Raw history/status/optional numerical record changed')
        for key,integration in record['required_integrations'].items():
            require(integration['native_elements'] and all(q in by for q in integration['native_elements']),'Required platform lacks actual native operations')
            for row in c['required_platform_parts']:
                f=feature(by[row['context']],row['feature'])
                require(lc.multiplicity(f)=='1' and by[row['type']] in f.types,'Required platform connection is optional or absent')
        check_controls(c,by,api)
        if cid=='PA-CDT': check_custom(record,native,lc)
        results[cid]={'primary_FR':40,'support_FR':0,'logical_components':6,'configured_framework_calls':len(c['framework_calls']),'logical_guards':len(c['controls']),'dominance_checks':len(c['dominance']),'status':'proposed/unexecuted'}
    physical_flows=[e for e in elements if type(e).__name__=='FlowUsage' and qn(e).startswith(('PhysicalVocabulary::','CandidateCOM::','CandidateVS::','CandidateNS::','CandidateGY::','CandidateCDT::'))]
    require({qn(e) for e in physical_flows}=={r['native'] for r in candidates['PA-CDT']['native_contract']['flows']},'Unrecorded or missing physical typed flow')
    return {'valid':True,'status':'passed current specification checks, not empirical V&V','candidates':results,'physical_flows':len(physical_flows),'source_sha256':{str(p.relative_to(root.parent)):audit.sha(p) for p in root.rglob('*.sysml')}}


def negative_cases(tool,root,candidates):
    baseline=check(tool,root); require(baseline['valid'],'Passing native physical baseline required')
    specs=candidates['PA-CDT']['native_contract']['negative_mutations']
    require(specs and {s['invariant'] for s in specs}>=NEGATIVE_INVARIANTS,'Current negative selectors incomplete')
    tests={}
    with tempfile.TemporaryDirectory(prefix='physical-negative-') as td:
        base=Path(td)/'baseline'
        for folder in ('sysml','candidates','traceability','tools'):shutil.copytree(root.parent/folder,base/folder,ignore=shutil.ignore_patterns('__pycache__'))
        for p in root.parent.glob('*.tex'):shutil.copy2(p,base/p.name)
        shutil.copy2(root.parent/'literatura.bib',base/'literatura.bib')
        jobs=[]
        for spec in specs:
            require(spec['id'] not in tests,'Duplicate negative ID')
            case=Path(td)/spec['id'];shutil.copytree(base,case); path=case/'sysml'/spec['file']
            if spec.get('scope_start'):
                text=path.read_text(); require(text.count(spec['scope_start'])==1,'Mutation scope must match once')
                start=text.index(spec['scope_start']);end=text.index(spec['scope_end'],start+len(spec['scope_start'])) if spec.get('scope_end') else len(text)
                old,new=spec['old'],spec['new'];region=text[start:end];require(old!=new and region.count(old)==1,'Scoped mutation must change exactly one selector')
                path.write_text(text[:start]+region.replace(old,new,1)+text[end:]);matches=1
            else:matches=mutate_once(path,spec['old'],spec['new'],spec['id'])
            jobs.append((spec,case,matches))
        # Syside API objects stay isolated in separate processes.
        import subprocess
        def run(job):
            spec,case,matches=job
            command=[sys.executable,str(Path(__file__).resolve()),'--root',str(case/'sysml'),'--tool',str(Path(tool.__file__).resolve()),'--mutation-check']
            done=subprocess.run(command,capture_output=True,text=True,timeout=180)
            require(done.returncode==1 and done.stdout.strip() and 'Traceback' not in done.stderr,'Mutation not rejected by actual checker: '+spec['id'])
            result=json.loads(done.stdout);require(result.get('valid') is False and result.get('failure_kind') in ('model_invalid','invariant'),'Tool availability failure is not a mutation rejection')
            if spec.get('expected_rejection'):require(spec['expected_rejection'] in result['error'],'Mutation reached unrelated rejection: '+spec['id']+': '+result['error'])
            return spec['id'],{'mutation_matches':matches,'baseline_passed':True,'native_check_executed':True,'rejected':True,'failure_kind':result['failure_kind'],'reason':result['error']}
        with ThreadPoolExecutor(max_workers=2) as pool:
            for name,result in pool.map(run,jobs):require(name not in tests,'Duplicate negative ID');tests[name]=result
    return tests


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--tool',type=Path,default=TOOL)
    parser.add_argument('--negative-cases',action='store_true')
    parser.add_argument('--mutation-check',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    try:
        tool=module(args.tool,'native_physical_tool')
        result=check(tool,args.root,enforce_snapshot=not args.mutation_check)
        if args.negative_cases:
            candidates=current_records(args.root)[4];result['negative_cases']=negative_cases(tool,args.root,candidates);result['negative_baseline_passed']=True
        print(json.dumps(result,indent=2));return 0
    except Exception as error:
        text=str(error)
        unavailable=isinstance(error,(ImportError,OSError)) or 'tooling unavailable' in text.lower()
        kind='tool_unavailable' if unavailable else 'model_invalid' if text.startswith('Native model invalid') else 'invariant'
        print(json.dumps({'valid':False,'failure_kind':kind,'error':text},indent=2));return 3 if unavailable else 1


if __name__=='__main__':
    raise SystemExit(main())
