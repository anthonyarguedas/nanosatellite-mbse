#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = []
# ///
"""Inspect proposed physical allocations using real licensed Syside semantics.

This is a specification check, not framework or EPS product V&V.
All current dependencies are included. Run the full model check separately
as well. --negative-cases mutates temporary copies.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

TOOL = Path('/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py')
FILES = tuple(f'{n}.sysml' for n in (
    '00-domain', '01-concerns', '02-needs-context', '03-requirements',
    '04-logical', '05-verification', '06-system-context', '07-report-views', '08-physical-vocabulary',
    '09-scenarios', '10-interface-views', '11-logical-responsibilities')) + tuple(
    f'candidates/{n}.sysml' for n in ('comet','custom','git-yaml','nanospace','valispace'))
CANDIDATES = {'comet':('PA-COM','CandidateCOM'), 'custom':('PA-CDT','CandidateCDT'),
              'git-yaml':('PA-GY','CandidateGY'), 'nanospace':('PA-NS','CandidateNS'),
              'valispace':('PA-VS','CandidateVS')}
EXPECTED = {'L01':{8,37},'L02':{2,3,29,39,41},'L03':{1,4,17},
            'L04':{12,13,14,15,20,25,33,34,35},
            'L05':{10,16,18,19,23,24,26,27,36},'L06':{21,22,31,32},
            'L07':{11,28,38,42},'L08':{5,6,7,9,30}}
GATES = {
    'PhysicalVocabulary::ActiveAssistance::admitOptions':('applicability.hasEligible','explain'),
    'PhysicalVocabulary::ActiveAssistance::admitCurrent':('currency.current','publish'),
    'PhysicalVocabulary::ScoreCandidates::remoteAdmitted':
        ('admit.remoteSelected and admit.remoteAuthorizedQualifiedPinnedBudgeted','remote'),
    'PhysicalVocabulary::ScoreCandidates::localAdmitted':
        ('not admit.remoteSelected and admit.localQualifiedAvailable','local'),
    'PhysicalVocabulary::ScoreCandidates::admitScores':
        ('check.qualifiedIdentityFiniteComplete','returnScores'),
    'PhysicalVocabulary::SupportedExecution::admitProfiles':('profiles.mandatoryProfilesVerified','execute'),
    'LogicalRealization::AssistanceRealization::admitReply':('checkReply.sameContext','present'),
    'LogicalRealization::AssistanceRealization::admitDisposition':
        ('dispose.authorized and checkApplication.sameContext','applyCorrection'),
    'LogicalRealization::SoftwareRealization::authorizeCoding':
        ('checkRelease.authorizedDetailedDesign and checkRelease.currentDesign and checkRelease.blockersClear and interfaces.profileCompatible','coordinate'),
    'LogicalRealization::ChangeReviewRealization::admitReviewDecision':
        ('checkDecision.authorized and checkDecision.current and checkDecision.decisionConsistent and (checkDecision.blocking or not checkDecision.conditional or checkDecision.conditionsComplete)','record'),
}

def require(test, message):
    if not test:
        raise ValueError(message)

def qn(e):
    return str(e.qualified_name) if e.qualified_name else ''

def chain(f):
    return list(f.chaining_features) or [f]

def compact(s):
    return re.sub(r'\s+','',s)

def module(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

REALIZATIONS = {
    'AssistanceRealization': 'assistance', 'ConceptRealization': 'concept',
    'DesignRealization': 'designRun', 'SoftwareRealization': 'software',
    'ChangeReviewRealization': 'changeReview', 'ReplayRealization': 'replayRun',
    'CalibrationRealization': 'calibration',
}
EXECUTIONS = {
    'concept': 'execute', 'designRun': 'execute', 'software': 'executeMIL',
    'changeReview': 'repeat', 'replayRun': 'execute', 'calibration': 'repeat',
}


@lru_cache(maxsize=2048)
def effective_features(context):
    """Apply native redefinitions, including explicit multiple inheritance joins."""
    features = list(context.features)
    redefined = {r.redefined_feature for f in features for r in f.owned_redefinitions}
    return [f for f in features if f not in redefined]


@lru_cache(maxsize=2048)
def feature(context, name):
    matches = [f for f in effective_features(context) if f.name == name]
    require(len(matches) == 1, f'{qn(context)}: ambiguous/missing actual feature {name}')
    return matches[0]


def actual_path(context, names):
    path = []
    for name in names:
        context = feature(context, name)
        path.append(context)
    return path


def flow_end(flow, name):
    end = next(e for e in flow.owned_features if type(e).__name__ == 'FlowEnd' and e.name == name)
    prefix = chain(end.referenced_feature) if end.referenced_feature is not None else []
    fields = list(end.owned_features)
    require(len(fields) == 1, 'Flow must map one actual parameter')
    return tuple(f.name for f in prefix) + (fields[0].name,)


def has_flow(context, source, target):
    return any(type(f).__name__ == 'FlowUsage' and flow_end(f, 'source') == tuple(source.split('.'))
               and flow_end(f, 'target') == tuple(target.split('.')) for f in effective_features(context))


def require_flow(context, source, target):
    require(has_flow(context, source, target), f'{qn(context)}: missing actual output/parameter route {source} -> {target}')


def binding_pairs(context):
    return {(tuple(f.name for f in chain(b.source_feature)), tuple(f.name for f in chain(t)))
            for b in effective_features(context) if type(b).__name__=='BindingConnectorAsUsage'
            for t in b.target_features}


def require_binding(context, source, target):
    pair=(tuple(source.split('.')),tuple(target.split('.')))
    require(pair in binding_pairs(context) or pair[::-1] in binding_pairs(context),
            f'{qn(context)}: adapter/port mapping lost {source} = {target}')


def output_producers(context, parameter):
    return {flow_end(f,'source') for f in effective_features(context) if type(f).__name__=='FlowUsage'
            and flow_end(f,'target')==(parameter,)}


def execution_tasks(context, by):
    bases=[by['ScenarioViews::'+name] for name in
           ('SC01External3','SC03External3','SC04External3','SC04External5','SC05External3')]
    bases.append(by['PhysicalVocabulary::ExecuteExistingSoftware'])
    return {f for f in effective_features(context) if type(f).__name__=='PerformActionUsage'
            and any(t.conforms(base) for t in f.types for base in bases)}


@lru_cache(maxsize=512)
def control_edges(context):
    """Only native successions/transitions are control edges. Dependencies are ignored."""
    features = effective_features(context)
    def current(f):
        replacements = [g for g in features if g == f or (g.name == f.name and g.conforms(f))]
        replacements = [g for g in replacements if not any(
            h != g and h.conforms(g) and not g.conforms(h) for h in replacements)]
        require(len(replacements) == 1, f'{qn(context)}: unresolved control endpoint {qn(f)}')
        return replacements[0]
    edges = []
    for e in features:
        if type(e).__name__ == 'SuccessionAsUsage':
            edges.extend((current(e.source_feature), current(t), e) for t in e.target_features)
        elif type(e).__name__ == 'TransitionUsage':
            edges.append((current(e.source), current(e.target), e))
    return edges


def reachable(context, removed=(), initial=None):
    edges = control_edges(context)
    reached = {feature(context, 'start')} if initial is None else {initial}
    removed = set(removed)
    while True:
        update = reached | {t for s, t, edge in edges if s in reached and s not in removed
                            and t not in removed and edge not in removed}
        if update == reached:
            return reached
        reached = update


def require_dominates(context, dominator, target):
    require(target in reachable(context), f'{qn(context)}: disconnected performed action {target.name}')
    require(target not in reachable(context, (dominator,)),
            f'{qn(context)}: actual execution/control bypass of {dominator.name}')


def admission_value(api, expression, profiles, mandatory, prior_feature=None, prior=False):
    if isinstance(expression,api.FeatureChainExpression):
        operands=list(expression.operands)
        require(len(operands)==1 and isinstance(operands[0],api.FeatureReferenceExpression) and
                profiles.conforms(operands[0].referent) and expression.target_feature.name=='mandatoryProfilesVerified' and
                expression.target_feature.owner in profiles.types,
                'Admission Boolean is not the result of the actual configured profile call')
        return mandatory
    if isinstance(expression,api.FeatureReferenceExpression):
        require(prior_feature is not None and prior_feature.conforms(expression.referent),
                'Admission uses an independent uncontrolled Boolean')
        return prior
    require(isinstance(expression,api.OperatorExpression), 'Admission requires native Boolean result expressions')
    operands=[admission_value(api,e,profiles,mandatory,prior_feature,prior) for e in expression.operands]
    operator=str(expression.operator)
    require(operator in ('and','not') and len(operands)==(1 if operator=='not' else 2), 'Unsupported admission operator')
    return not operands[0] if operator=='not' else all(operands)


def check_execution(context, api, host=False):
    profiles, execute, blocked = (feature(context, n) for n in ('profiles', 'execute', 'blocked'))
    admit, reject = (feature(context, n) for n in ('admitProfiles', 'rejectProfiles'))
    expression = ('priorProfilesAdmitted and profiles.mandatoryProfilesVerified' if host
                  else 'profiles.mandatoryProfilesVerified')
    require(compact(api.pprint(admit.guard_expression)) == compact(expression), 'Actual admission guard changed')
    require(compact(api.pprint(reject.guard_expression)) == compact('not (' + expression + ')' if host
                  else 'not ' + expression), 'Actual rejection guard changed')
    prior_feature=feature(context,'priorProfilesAdmitted') if host else None
    for mandatory in (False,True):
        for prior in ((False,True) if host else (True,)):
            admitted=admission_value(api,admit.guard_expression,profiles,mandatory,prior_feature,prior)
            rejected=admission_value(api,reject.guard_expression,profiles,mandatory,prior_feature,prior)
            require(admitted is (mandatory and prior) and rejected is not admitted,
                    'Failed admission permits execution or loses its blocked response')
    require_dominates(context, profiles, execute)
    require_dominates(context, admit, execute)
    require(blocked in reachable(context, (admit,)), 'Failed admission has no defined blocked response')
    require(execute not in reachable(context, initial=blocked), 'Blocked admission reaches external execution')
    require(feature(context, 'done') in reachable(context, initial=blocked), 'Blocked response cannot complete')
    incoming, admitted_input = ('request', 'admittedRequest') if host else ('plan', 'admittedPlan')
    require_flow(context, incoming, 'profiles.' + incoming)
    require_flow(context, 'profiles.' + admitted_input, 'execute.' + incoming)
    require_flow(context, incoming, 'blocked.' + incoming)
    require_flow(context, 'execute.result', 'result')
    require_flow(context, 'blocked.result', 'result')
    require(output_producers(context,'result')=={('execute','result'),('blocked','result')},
            'Actual execution returns an unrelated or bypass result')
    require(any(t.name == ('BlockHostExecution' if host else 'BlockExecution') for t in blocked.types),
            'Failure result lost its defined blocked meaning')


def check_assistance_operation(operation, api, draft=False):
    pipeline = feature(operation, 'pipeline')
    require(any(t.name == 'ActiveAssistance' for t in pipeline.types), 'Actual operation disconnects explained assistance')
    require_dominates(operation, feature(operation, 'map'), pipeline)
    require_dominates(operation, pipeline, feature(operation, 'returnWork' if draft else 'done'))
    require_flow(operation, 'work', 'map.work')
    require_flow(operation, 'map.input', 'pipeline.input')
    if draft:
        require_flow(operation, 'work', 'returnWork.work')
        require_flow(operation, 'pipeline.report', 'returnWork.report')
        require_flow(operation, 'returnWork.updatedWork', 'updatedWork')
    else:
        require_flow(operation, 'pipeline.report', 'report')
    for before, after in [('rules', 'sources'), ('sources', 'retrieve'), ('retrieve', 'scores'),
                          ('scores', 'applicability'), ('applicability', 'currency'), ('currency', 'publish')]:
        require_dominates(pipeline, feature(pipeline, before), feature(pipeline, after))
    # Both explanation alternatives must precede currency and publication.
    require(feature(pipeline, 'publish') not in reachable(pipeline,
            (feature(pipeline, 'explain'), feature(pipeline, 'none'))), 'Explanation pipeline disconnected or bypassed')
    require_flow(pipeline, 'publish.report', 'report')
    require_flow(pipeline, 'stale.report', 'report')
    require(output_producers(pipeline,'report')=={('publish','report'),('stale','report')},
            'An unexplained score batch bypasses the report output route')
    require(output_producers(operation,'updatedWork' if draft else 'report')==
            {('returnWork','updatedWork') if draft else ('pipeline','report')}, 'Operation returns a score or unrelated result')
    scores = feature(pipeline, 'scores')
    require_dominates(scores, feature(scores, 'admit'), feature(scores, 'remote'))
    require_dominates(scores, feature(scores, 'admit'), feature(scores, 'local'))
    fallback = feature(scores, 'admitFallback')
    require(compact(api.pprint(fallback.guard_expression)) == 'fallback.localQualifiedAvailable',
            'Outage fallback bypasses separate local qualification')
    require(feature(scores, 'unavailable') in reachable(scores), 'Probabilistic outage has no unavailable result')
    require(feature(scores,'local') not in reachable(scores,(fallback,),initial=feature(scores,'validRemote')),
            'Remote failure bypasses independently qualified local fallback')


def check(tool, root, validation=None):
    effective_features.cache_clear()
    feature.cache_clear()
    control_edges.cache_clear()
    report=root.parent
    logical=json.loads((report/'traceability/logical-architecture.json').read_text())
    logical_rows={r['FR']:r for r in logical['allocations']}
    reviewed_sources={r['id'] for r in json.loads((report/'traceability/source-review.json').read_text())['sources']}
    result=validation if validation is not None else tool.validate([root/p for p in FILES], [], warnings_as_errors=True,
                         config=root/'physical-allocations.toml')
    model,api=tool.require_semantic_model(result)
    elements=list(model.nodes(api.Element,include_subtypes=True))
    by={qn(e):e for e in elements if e.qualified_name}
    compiler=api.Compiler()
    def annotations(e,t):
        return [m for m in elements if isinstance(m,api.MetadataUsage) and
                e in m.annotated_elements and any(qn(x)==t for x in m.types)]
    def values(m):
        out={}
        for f in m.owned_features:
            v,d=compiler.evaluate_feature(f,m)
            require(bool(d),'Cannot evaluate native annotation')
            out[f.name]=v
        return out
    def deps(e):
        return {t for d in elements if isinstance(d,api.Dependency) and e in d.sources for t in d.targets}
    frs={e.name for e in elements if type(e).__name__=='RequirementUsage' and qn(e.owner)=='FrameworkRequirements'}
    require(frs=={f'FR_{n:02}' for n in range(1,40)}|{'FR_41','FR_42'},'Current FR set or retired requirement changed')
    owners={f'FR-{n:02}':lid for lid,ns in EXPECTED.items() for n in ns}
    require(set(logical_rows)==set(owners),'Current logical ledger coverage changed')
    allocations=[e for e in elements if type(e).__name__=='AllocationUsage']
    candidate_results={}
    for file,(cid,pkg) in CANDIDATES.items():
        ledger=json.loads((report/f'candidates/{file}.json').read_text())
        require(ledger['id']==cid and ledger['numerical_results'] is None,'Candidate ID or invented result')
        require(set(ledger['sources'])<=reviewed_sources,'Candidate cites missing current primary-source support')
        configuration=by[f'{pkg}::Configuration']; instance=by[f'{pkg}::candidate']
        require(configuration.conforms(by['FrameworkLogical::LogicalFramework']), 'Candidate must specialize current logical design')
        components={p.name:p for p in configuration.owned_features if type(p).__name__=='PartUsage' and p.name.startswith('L')}
        require(set(components)==set(EXPECTED),'Eight exact physical software components required')
        rows={r['FR']:r for r in ledger['allocations']}
        require(set(rows)==set(owners) and len(ledger['allocations'])==41,'Exact candidate 41FR coverage')
        aa=[a for a in allocations if qn(a.owner)==pkg]
        primary=[a for a in aa if annotations(a,'PhysicalVocabulary::physicalPrimary')]
        require(len(primary)==41,'Exactly one candidate primary allocation per FR')
        seen=set()
        for a in primary:
            fr=a.source_feature; fid=fr.name.replace('_','-'); row=rows[fid]; common=logical_rows[fid]
            end=chain(list(a.target_features)[0]); lid=owners[fid]
            require(fr not in seen and type(fr).__name__=='RequirementUsage','Duplicate or invalid FR source')
            seen.add(fr)
            require(end==[instance,components[lid]] and row['primary']==common['primary']==lid,'Wrong physical FR owner')
            meta=annotations(a,'PhysicalVocabulary::PhysicalAllocation')
            require(len(meta)==1,'Allocation needs rationale, operation and planned check')
            fields=values(meta[0]); operation=fields['operation'].element
            definition=by[f'{pkg}::C{int(lid[-2:]):02}']
            require(definition in components[lid].types and operation.owner==definition and
                    qn(operation)==row['operation'] and operation in deps(fr),'Operation does not belong to physical component')
            require(operation.name==common['operation'].split('::')[-1] and
                    operation.conforms(by[common['operation']]),'Changed logical operation meaning')
            plan=annotations(fr,'FrameworkRequirements::PlannedRequirementCheck')
            require(len(plan)==1,'Missing approved FR verification need')
            p=values(plan[0]); planned=p['methods']+': '+p['checkSummary']
            require(row['planned_check']==fields['plannedCheck']==planned,'Changed planned FR check')
            require(fields['rationale'],'Allocation rationale missing')
            support=set()
            for s in aa:
                if s.source_feature==fr and annotations(s,'PhysicalVocabulary::physicalSupport'):
                    target=chain(list(s.target_features)[0])
                    require(target[0]==instance and target[-1] in components.values(),'Wrong supporting physical target')
                    support.add(target[-1].name)
            require(support==set(row['support'])==set(common['support']),'Supporting allocation mismatch')
            require(row['interfaces']==common['interfaces'],'External interface relationship changed')
            for b in common['behaviors']:
                realization, step = b.split('::')[-2:]
                behavior = feature(configuration, REALIZATIONS[realization])
                actual = feature(behavior, step)
                require(actual.conforms(by[b]), 'Physical task changes logical operation meaning')
                require(any(a.source_feature==actual and chain(list(a.target_features)[0])==[instance,components[lid]] for a in aa),
                        'FR operation lacks actual physical realization action allocation')
        for lid,part in components.items():
            n=int(lid[-2:]); host='N2' if n==2 else 'N3' if n==8 else 'N1'
            require(any(chain(a.source_feature)==[instance,part] and chain(list(a.target_features)[0])==[instance,by[f'{pkg}::Configuration::{host}']]
                        for a in aa if annotations(a,'PhysicalVocabulary::executionHost')),'Missing/wrong execution host')
            require(any(chain(a.source_feature)==[by['FrameworkLogical::logical'],by[f'FrameworkLogical::LogicalFramework::{lid}']] and
                        chain(list(a.target_features)[0])==[instance,part] for a in aa if annotations(a,'PhysicalVocabulary::logicalRealization')),
                    'Missing exact logical-to-physical allocation')
            spec=annotations(by[f'{pkg}::C{n:02}'],'PhysicalVocabulary::ComponentSpecification')
            require(len(spec)==1 and values(spec[0])['status']=='proposed, not verified','False component fulfilment')
        source=annotations(configuration,'FrameworkDomain::SourceRecord')
        require(len(source)==1 and values(source[0])['sourceText']==ledger['retention_rationale'] and
                values(source[0])['citationRecord']==', '.join(ledger['sources']) and
                values(source[0])['status']=='proposed, access and verification pending', 'Native/ledger source rationale or status mismatch')
        for data,host,typ in [('modelRecords','N1','ModelData'),('sourceAndAdviceRecords','N2','AdviceData'),('rawResultsAndReleases','N3','ReleaseData')]:
            datum=by[f'{pkg}::Configuration::{data}']
            require(by[f'PhysicalVocabulary::{typ}'] in datum.types,'Wrong persistent record meaning')
            require(any(chain(a.source_feature)==[instance,datum] and chain(list(a.target_features)[0])==[instance,by[f'{pkg}::Configuration::{host}']]
                        for a in aa if annotations(a,'PhysicalVocabulary::persistentStorage')),'Wrong persistent storage')
        for proc,actor in [('engineeringProcedure','systemsEngineer'),('reviewProcedure','reviewAuthority')]:
            require(any(chain(a.source_feature)==[instance,by[f'{pkg}::Configuration::{proc}']] and
                        list(a.target_features)==[by[f'ScenarioViews::{actor}']] for a in aa if annotations(a,'PhysicalVocabulary::procedurePerformer')),
                    'Procedure performer loses engineering/review authority')
        behavior_instances = {name: feature(configuration, name) for name in REALIZATIONS.values()}
        require(ledger['behavior_realizations']=={logical_name:qn(behavior_instances[name]) for logical_name,name in REALIZATIONS.items()},
                'Candidate behavior index is stale or points to unperformed definitions')
        require(ledger['controls']['assistance']==qn(behavior_instances['assistance']) and
                ledger['controls']['mandatory_profiles']=='PhysicalVocabulary::SupportedExecution::admitProfiles' and
                ledger['controls']['host_profiles']=='PhysicalVocabulary::SupportedHostExecution::admitProfiles', 'Candidate control index mismatch')
        require({e.name for e in configuration.owned_features if type(e).__name__=='PerformActionUsage'} ==
                set(behavior_instances) | {'engineeringProcedure','reviewProcedure'},
                'Disconnected or additional unrefined performed candidate behavior')
        for logical_name, name in REALIZATIONS.items():
            behavior = behavior_instances[name]
            require(by['PhysicalVocabulary::Physical'+logical_name] in behavior.types and
                    behavior.conforms(by['LogicalRealization::'+logical_name]), 'Candidate performs an unrefined logical behavior')
        # The calls reference the real configured component operations, not dependency tags.
        assistance = behavior_instances['assistance']
        for task_name, operation_name in [('checkDraft','checkDraft'),('recommend','recommend'),('reassess','reassess')]:
            task = feature(assistance, task_name)
            operation = feature(components['L02'], operation_name)
            require(task.owned_reference_subsetting is not None and
                    chain(task.referenced_feature)==[components['L02'],operation], 'Advice call does not invoke configured L02 operation')
        currency_operation=feature(components['L08'],'checkCurrency')
        require(by['PhysicalVocabulary::PhysicalCheckCurrency'] in currency_operation.types, 'Physical stale-report rejection disconnected')
        for name in ('checkReply','checkApplication'):
            call=feature(assistance,name)
            require(call.owned_reference_subsetting is not None and
                    chain(call.referenced_feature)==[components['L08'],currency_operation], 'Advice currency result is not from the configured operation')
        require_dominates(assistance, feature(assistance,'checkDraft'), feature(assistance,'checkReply'))
        require_dominates(assistance, feature(assistance,'recommend'), feature(assistance,'checkReply'))
        for operation_name in ('checkDraft','recommend'):
            operation = feature(components['L02'],operation_name)
            check_assistance_operation(operation,api,draft=operation_name=='checkDraft')
            for step,end in [('rules',['L02','rules']),('sources',['L02','localScoring']),('retrieve',['L02','localScoring']),
                             ('explain',['L02','explanation']),('none',['L02','explanation']),
                             ('currency',['L08']),('publish',['L01']),('stale',['L08'])]:
                source=[instance]+actual_path(configuration,['L02',operation_name,'pipeline',step])
                require(any(chain(a.source_feature)==source and
                            [f.name for f in chain(list(a.target_features)[0])]==['candidate']+end for a in aa),
                        'Assistance allocation does not follow an actual invoked operation/pipeline path')
        reassess = feature(components['L02'],'reassess')
        for step in ('checkDraft','recommend'):
            call=feature(reassess,step)
            require(call.owned_reference_subsetting is not None and
                    call.performed_action==by[f'{pkg}::C02::{step}'], 'Repeated advice does not invoke configured qualified operation')
        require_flow(reassess,'returnWork.updatedWork','work')
        for name,step in EXECUTIONS.items():
            behavior=behavior_instances[name]; execution=feature(behavior,step)
            require(by['PhysicalVocabulary::SupportedExecution'] in execution.types, 'Numerical/MIL/change/replay admission disconnected')
            profiles=feature(execution,'profiles')
            require(profiles.owned_reference_subsetting is not None and
                    chain(profiles.referenced_feature)==[components['L05'],by[f'{pkg}::C05::verifyProfiles']],
                    'Admission does not invoke the configured profile verification method')
            check_execution(execution,api)
            require(execution in reachable(behavior), 'Checked execution is beside the actual scenario path')
            allowed={execution}
            if name=='software': allowed.add(feature(behavior,'codeBuildSil'))
            require(execution_tasks(behavior,by)==allowed, 'Applicable realization contains an unrefined external execution bypass')
            require(not execution_tasks(execution,by), 'Raw external execution bypasses the checked dispatcher')
            dispatcher=feature(execution,'execute')
            require(execution_tasks(dispatcher,by)=={feature(dispatcher,'models')}, 'Dispatcher contains an unguarded external bypass')
            require_dominates(dispatcher,feature(dispatcher,'kind'),feature(dispatcher,'sil'))
            sil=feature(dispatcher,'sil')
            require(execution_tasks(sil,by)=={feature(sil,'execute')}, 'Existing SIL contains an extra external operation')
            require_dominates(sil,feature(sil,'map'),feature(sil,'execute'))
            for source,target in [('map.request','execute.request'),('execute.result','returnResult.software'),
                                  ('returnResult.result','result')]: require_flow(sil,source,target)
            for leaf,ext in [(('execute','models'),'models'),(('execute','sil','execute'),'hostCode')]:
                source=[instance]+actual_path(configuration,[name,step]+list(leaf))
                require(any(chain(a.source_feature)==source and
                            [f.name for f in chain(list(a.target_features)[0])]==['candidate',ext] for a in aa),
                        'Actual numerical or existing SIL call lacks the correct external performer')
                endpoint=source+[feature(source[-1],'endpoint')]
                require(any(type(b).__name__=='BindingConnectorAsUsage' and qn(b.owner)==pkg and
                            chain(b.source_feature)==endpoint and
                            [f.name for f in chain(list(b.target_features)[0])]==['candidate',ext,'requests'] for b in elements),
                        'External call lacks its actual typed port mapping')
        host=feature(behavior_instances['software'],'codeBuildSil')
        require(by['PhysicalVocabulary::SupportedHostExecution'] in host.types, 'Host coding/SIL admission disconnected')
        require(chain(feature(host,'profiles').referenced_feature)==[components['L05'],by[f'{pkg}::C05::verifyHostProfiles']],
                'Host admission does not invoke configured verification')
        check_execution(host,api,host=True)
        require(execution_tasks(host,by)=={feature(host,'execute')}, 'Host wrapper contains an unguarded execution')
        host_source=[instance]+actual_path(configuration,['software','codeBuildSil','execute'])
        require(any(chain(a.source_feature)==host_source and
                    [f.name for f in chain(list(a.target_features)[0])]==['candidate','hostCode'] for a in aa),
                'Actual coding/build/SIL performer changed')
        require(any(type(b).__name__=='BindingConnectorAsUsage' and qn(b.owner)==pkg and
                    chain(b.source_feature)==host_source+[feature(host_source[-1],'endpoint')] and
                    [f.name for f in chain(list(b.target_features)[0])]==['candidate','hostCode','requests'] for b in elements),
                'Actual coding/build/SIL port mapping missing')
        require_flow(behavior_instances['software'],'executeMIL.admitted','codeBuildSil.priorProfilesAdmitted')
        require_flow(behavior_instances['software'],'planMIL.plan','codeBuildSil.plan')
        candidate_results[cid]={'primary_FR':41,'logical_components':8,'performed_refinements':7,
                               'admitted_execution_calls':7,'external_port_routes':13,'planned':'not verified'}
        connections={e.name:e for e in configuration.owned_features if type(e).__name__=='InterfaceUsage'}
        require(set(connections)=={'adviceLink','releasedData','sourceAdvice','modelLink','codeLink'},'Physical exchange coverage')
        expected_ends={'adviceLink':(['N1','assistance'],['N2','assistance']),
                       'releasedData':(['N1','revisions'],['N3','engineering']),
                       'sourceAdvice':(['N2','revisions'],['N3','assistance']),
                       'modelLink':(['N1','models'],['models','requests']),
                       'codeLink':(['N1','hostCode'],['hostCode','requests'])}
        for name,c in connections.items():
            ends=[chain(c.source_feature),chain(list(c.target_features)[0])]
            require(tuple([f.name for f in end] for end in ends)==expected_ends[name], 'Wrong physical exchange endpoint')
            require(all(type(end[-1]).__name__=='PortUsage' for end in ends),'Exchange endpoint is not a real port')
        require(len([e for e in configuration.owned_features if type(e).__name__=='BindingConnectorAsUsage'])==10,
                'Missing software-to-host port/reference binding')
        for s,typ in [('guidanceState','GuidanceControl'),('reviewState','BaselineControl')]:
            a=by[f'{pkg}::{s}']; end=chain(list(a.target_features)[0])
            require(end[0]==instance and by[f'ScenarioViews::{typ}'] in end[-1].types,'Missing physical state ownership')
    prefixes=tuple(pkg+'::' for _,pkg in CANDIDATES.values())+('PhysicalVocabulary::',)
    require(not any(type(e).__name__=='SatisfyRequirementUsage' and qn(e).startswith(prefixes) for e in elements),'Physical design asserts satisfaction')
    forbidden={'FrameworkDomain::TestingFacilityTechnician','FrameworkDomain::EPSHardware','FrameworkDomain::AsIs::TestingFacility'}
    require(not any(type(e).__name__=='PartUsage' and qn(e).startswith(prefixes) and forbidden.intersection(qn(t) for t in e.types)
                    for e in elements),'Excluded physical participant/target obligation')
    for path,(expression,target) in GATES.items():
        g=by[path]; owner=g.owner
        require(compact(api.pprint(g.guard_expression))==compact(expression) and g.target==by[qn(owner)+'::'+target], 'Lost native applicability/currency/authority gate: '+path)
        require(not any(type(e).__name__=='SuccessionAsUsage' and e.owner==owner and g.target in e.target_features for e in elements),
                'Unguarded bypass into protected action')
        require(any(type(e).__name__=='TransitionUsage' and e.owner==owner and e.source==g.source and e!=g and e.guard_expression is not None for e in elements),
                'Gate lost failure response')
    for name in ('noOptions','rejectStale'):
        require(by['PhysicalVocabulary::ActiveAssistance::'+name].guard_expression is not None,'Lost no-eligible/stale branch')
    # Preserve immediate logical invalidation and no new direct route to host coding.
    for x,y in [('capture','invalidateOnEdit'),('invalidateOnEdit','acknowledge')]:
        owner=by['LogicalRealization::AssistanceRealization']
        require(any(type(e).__name__=='SuccessionAsUsage' and e.owner==owner and e.source_feature==by[qn(owner)+'::'+x] and
                    list(e.target_features)==[by[qn(owner)+'::'+y]] for e in elements),'Lost immediate edit invalidation')
    owner=by['LogicalRealization::SoftwareRealization']; release=by[qn(owner)+'::authorizeCoding']
    edges=[(e.source_feature,t) for e in elements if type(e).__name__=='SuccessionAsUsage' and e.owner==owner for t in e.target_features]
    edges += [(e.source,e.target) for e in elements if type(e).__name__=='TransitionUsage' and e.owner==owner and e!=release]
    host_reachable={s for s,_ in edges if s.name=='start'}
    while True:
        update=host_reachable|{t for s,t in edges if s in host_reachable}
        if update==host_reachable:break
        host_reachable=update
    require(by[qn(owner)+'::codeBuildSil'] not in host_reachable,'Direct host bypass of exact authorized release')
    # Native payload/parameter conformance, including cases accepted by native syntax alone.
    flows=[e for e in elements if type(e).__name__=='FlowUsage' and qn(e).startswith('PhysicalVocabulary::')]
    for flow in flows:
        payload=[t for t in flow.payload_types if qn(t).startswith(('PhysicalVocabulary::','BoundaryViews::','FrameworkLogical::','ScalarValues::'))]
        require(len(payload)==1,'Ambiguous physical typed flow')
        for end in [e for e in flow.owned_features if type(e).__name__=='FlowEnd']:
            types=[t for f in end.owned_features for t in f.types]
            require(any(t.conforms(payload[0]) if end.name=='source' else payload[0].conforms(t) for t in types),
                    'Physical flow payload/parameter mismatch')
    # Structural adapters preserve context, human dispositions and typed return values.
    mapper=by['PhysicalVocabulary::MapAdviceWork']
    for source,target in [('input.work','work'),('input.request','work.request'),
                          ('input.context','work.request.context'),('input.drafts','work.drafts'),('input.purpose','purpose')]:
        require_binding(mapper,source,target)
    return_work=by['PhysicalVocabulary::ReturnAdviceWork']
    for source,target in [('updatedWork.triggerAcknowledgementCompletion','work.triggerAcknowledgementCompletion'),
                          ('updatedWork.submission','work.submission'),('updatedWork.request','work.request'),
                          ('updatedWork.drafts','work.drafts'),('updatedWork.dispositions','work.dispositions'),
                          ('updatedWork.findings','report.findings'),('updatedWork.report','report')]:
        require_binding(return_work,source,target)
    require_binding(by['PhysicalVocabulary::AdmitProfiles'],'admittedPlan','plan')
    require_binding(by['PhysicalVocabulary::AdmitHostProfiles'],'admittedRequest','request')
    require_binding(by['PhysicalVocabulary::UnavailableScore'],'scored.report','batch.report')
    require_binding(by['PhysicalVocabulary::PublishAdvice'],'report.context','batch.input.context')
    currency=by['PhysicalVocabulary::PhysicalCheckCurrency']
    require(compact(api.pprint(feature(currency,'sameContext').feature_value_expression))==
            'latest.sameContextandstatus.presentable', 'A stale physical report can pass the logical display/application gate')
    require(compact(api.pprint(feature(by['PhysicalVocabulary::CheckReturnedAdvice'],'presentable').feature_value_expression))==
            'report.currentStalePendingUnavailable!="stale"', 'Physical stale-report status no longer controls currency')
    for source,target in [('report','latest.report'),('context','latest.context'),('report','status.report')]:
        require_flow(currency,source,target)
    for name,source,target in [('DeclaredModelExecution','plan','endpoint.analysisPlan'),
                              ('DeclaredModelExecution','result','endpoint.analysisResult'),
                              ('DeclaredHostExecution','request','endpoint.codingRequest'),
                              ('DeclaredHostExecution','result','endpoint.softwareResult'),
                              ('ExecuteExistingSoftware','request','endpoint.codingRequest'),
                              ('ExecuteExistingSoftware','result','endpoint.softwareResult'),
                              ('MapSoftwareResult','result.plan','plan'),('MapSoftwareResult','result.software','software'),
                              ('MapExistingSILRequest','request.plan','plan')]:
        require_binding(by['PhysicalVocabulary::'+name],source,target)
    for name,field,value in [('BlockedAnalysisResult','externalExecutionOccurred',False),
                             ('BlockedSoftwareResult','externalExecutionOccurred',False),
                             ('ExistingSILRequest','codingOrBuildAllowed',False),
                             ('RequestedSoftwareProduct','built',False)]:
        definition=by['PhysicalVocabulary::'+name]
        require(compiler.evaluate_feature(feature(definition,field),definition)[0] is value, 'Blocked or existing SIL status fabricated execution')
    require_binding(by['PhysicalVocabulary::BlockExecution'],'result.plan','plan')
    require_binding(by['PhysicalVocabulary::BlockHostExecution'],'result.request','request')
    scoring=by['PhysicalVocabulary::LocalScoring']
    defaults={f.name:compiler.evaluate_feature(f,scoring)[0] for f in scoring.owned_features if type(f).__name__=='AttributeUsage' and f.feature_value}
    require(defaults['embeddingModel']=='Qwen/Qwen3-Embedding-0.6B' and defaults['embeddingRevision']=='97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3' and
            defaults['rerankerModel']=='Qwen/Qwen3-Reranker-0.6B' and defaults['rerankerRevision']=='e61197ed45024b0ed8a2d74b80b4d909f1255473','Unpinned local assistance models')
    jev=by['PhysicalVocabulary::JevScoring']
    defaults={f.name:compiler.evaluate_feature(f,jev)[0] for f in jev.owned_features if type(f).__name__=='AttributeUsage' and f.feature_value}
    require(defaults['modelIdentity']=='jev-1.13.0' and defaults['sdkIdentity']=='typesafe-sdk 0.6.0','Unpinned remote model/SDK')
    trade=json.loads((report/'traceability/trade-study.json').read_text())
    require(set(trade['candidate_ids'])=={c for c,_ in CANDIDATES.values()} and trade['decision']['preferred']=='PA-CDT','Trade/candidate disagreement')
    require(all(v is None for v in trade['numerical_results'].values()),'Invented numerical trade result')
    require(set(trade['physical_behavior']['realizations'])=={'PhysicalVocabulary::Physical'+name for name in REALIZATIONS} and
            trade['physical_behavior']['admission']==['PhysicalVocabulary::SupportedExecution::admitProfiles','PhysicalVocabulary::SupportedHostExecution::admitProfiles'],
            'Trade behavior/control index mismatch')
    text=(report/'trade-selection.tex').read_text()
    require('PA-CDT' in text and 'conditional' in text.lower() and '41 FRs' in text,'Report design direction/coverage mismatch')
    for lid,ns in EXPECTED.items():
        require(f'L{lid[-2:]} / CDT-C{lid[-2:]}' in text,'Report physical allocation row missing')
    return {'status':'passed specification checks, not framework V&V','candidates':candidate_results,
            'physical_flows':len(flows),'native_guards_checked':len(GATES),'profile_guard_cases':80,
            'scope':'Full current model dependencies, planned physical allocation consistency only'}

MUTATIONS={
 'wrong-owner':('candidates/custom.sysml','FR_02 to candidate.L02 {','FR_02 to candidate.L03 {'),
 'missing-FR':('candidates/custom.sysml','#physicalPrimary allocation FR_41_primary','#physicalSupport allocation FR_41_primary'),
 'wrong-operation':('candidates/custom.sysml','operation = CandidateCDT::C02::checkDraft','operation = CandidateCDT::C03::retainRequirements'),
 'wrong-host':('candidates/custom.sysml','host_L02 allocate candidate.L02 to candidate.N2','host_L02 allocate candidate.L02 to candidate.N1'),
 'wrong-store':('candidates/custom.sysml','store_rawResultsAndReleases allocate candidate.rawResultsAndReleases to candidate.N3','store_rawResultsAndReleases allocate candidate.rawResultsAndReleases to candidate.N1'),
 'wrong-procedure-authority':('candidates/custom.sysml','reviewProcedure to ScenarioViews::reviewAuthority','reviewProcedure to ScenarioViews::systemsEngineer'),
 'wrong-tool-port':('candidates/custom.sysml','connect N1.hostCode to hostCode.requests','connect N1.models to hostCode.requests'),
 'stale-display':('08-physical-vocabulary.sysml','if currency.current then publish','if true then publish'),
 'eligibility-bypass':('08-physical-vocabulary.sysml','if applicability.hasEligible then explain','if true then explain'),
 'remote-privacy-budget-bypass':('08-physical-vocabulary.sysml','if admit.remoteSelected and admit.remoteAuthorizedQualifiedPinnedBudgeted then remote','if admit.remoteSelected then remote'),
 'invalid-model-response':('08-physical-vocabulary.sysml','if check.qualifiedIdentityFiniteComplete then returnScores','if true then returnScores'),
 'unverified-discipline':('08-physical-vocabulary.sysml','if profiles.mandatoryProfilesVerified then execute','if true then execute'),
 'model-latest':('08-physical-vocabulary.sysml','modelIdentity : String = "jev-1.13.0"','modelIdentity : String = "jev-latest"'),
 'score-as-explanation':('candidates/custom.sysml','checkDraft.pipeline.explain to candidate.L02.explanation','checkDraft.pipeline.explain to candidate.L02.localScoring'),
 'wrong-payload':('08-physical-vocabulary.sysml','flow scoreFlow of AdviceBatch','flow scoreFlow of AdviceInput'),
 'direct-host-bypass':('11-logical-responsibilities.sysml','first checkRelease then codingRelease;','first checkRelease then codingRelease;\n        first start then codeBuildSil;'),
 'false-fulfilment':('candidates/custom.sysml','proposed, access and verification pending','verified and fulfilled'),
 'excluded-participant':('08-physical-vocabulary.sysml','part def HostResource {','part def HostResource {\n        part technician : FrameworkDomain::TestingFacilityTechnician;'),
 'retired-requirement':('03-requirements.sysml','package FrameworkRequirements {','package FrameworkRequirements {\n    requirement FR_40;'),
 'disconnect-candidate-behavior':('candidates/custom.sysml','perform action designRun : PhysicalDesignRealization','perform action designRun : LogicalRealization::DesignRealization'),
 'disconnect-advice-method':('candidates/custom.sysml','checkDraft references L02.checkDraft','checkDraft : FrameworkLogical::CheckDraft'),
 'wrong-profile-method':('candidates/custom.sysml','perform action :>> verifyProfiles;','perform action verifyProfiles : FrameworkLogical::PlanAnalysis;'),
 'disconnect-advice-pipeline':('08-physical-vocabulary.sysml','first map then pipeline;\n        first pipeline then returnWork;','first map then returnWork;\n        first pipeline then returnWork;'),
 'disconnect-admission':('08-physical-vocabulary.sysml','first start then profiles;\n        first profiles then ready;\n        succession admitProfiles first ready if profiles.mandatoryProfilesVerified',
                        'first start then execute;\n        first profiles then ready;\n        succession admitProfiles first ready if profiles.mandatoryProfilesVerified'),
 'direct-design-external-bypass':('08-physical-vocabulary.sysml','action def PhysicalDesignRealization :> LogicalRealization::DesignRealization {',
                        'action def PhysicalDesignRealization :> LogicalRealization::DesignRealization {\n        perform action raw : ScenarioViews::SC03External3;\n        first plan then raw;'),
 'direct-repeat-external-bypass':('08-physical-vocabulary.sysml','action def PhysicalChangeReviewRealization :> LogicalRealization::ChangeReviewRealization {',
                        'action def PhysicalChangeReviewRealization :> LogicalRealization::ChangeReviewRealization {\n        perform action raw : ScenarioViews::SC05External3;\n        first planRepeat then raw;'),
 'direct-replay-external-bypass':('08-physical-vocabulary.sysml','action def PhysicalReplayRealization :> LogicalRealization::ReplayRealization {',
                        'action def PhysicalReplayRealization :> LogicalRealization::ReplayRealization {\n        perform action raw : ScenarioViews::SC05External3;\n        first prepare then raw;'),
 'SIL-profile-bypass':('08-physical-vocabulary.sysml','if priorProfilesAdmitted and profiles.mandatoryProfilesVerified then execute','if priorProfilesAdmitted then execute'),
 'SIL-after-blocked-MIL':('08-physical-vocabulary.sysml','from executeMIL.admitted to codeBuildSil.priorProfilesAdmitted','from checkRelease.blockersClear to codeBuildSil.priorProfilesAdmitted'),
 'blocked-result-not-returned':('08-physical-vocabulary.sysml','flow blockedResult of AnalysisResult from blocked.result to result;','dependency blockedResult from blocked to result;'),
 'blocked-execution-leak':('08-physical-vocabulary.sysml','first blocked then complete;\n        first complete then done;\n        flow planFlow','first blocked then execute;\n        first complete then done;\n        flow planFlow'),
 'pipeline-report-not-returned':('08-physical-vocabulary.sysml','flow publishedReport of AssistanceReport from publish.report to report;','dependency publishedReport from publish to report;'),
 'advice-score-return':('08-physical-vocabulary.sysml','flow explainedReport of AssistanceReport from pipeline.report to report;',
                      'flow explainedReport of AssistanceReport from pipeline.scores.scored.report to report;'),
 'advice-context-adapter':('08-physical-vocabulary.sysml','bind input.context = work.request.context;','bind input.context = input.context;'),
 'draft-report-adapter':('08-physical-vocabulary.sysml','bind updatedWork.report = report;','bind updatedWork.report = work.report;'),
 'lost-human-dispositions':('08-physical-vocabulary.sysml','bind updatedWork.dispositions = work.dispositions;','bind updatedWork.dispositions = updatedWork.dispositions;'),
 'outage-unqualified-local':('08-physical-vocabulary.sysml','if fallback.localQualifiedAvailable then local','if true then local'),
 'wrong-model-call-allocation':('candidates/custom.sysml','designRun.execute.execute.models to candidate.models','designRun.execute.execute.models to candidate.hostCode'),
 'wrong-model-call-port':('candidates/custom.sysml','designRun.execute.execute.models.endpoint = candidate.models.requests','designRun.execute.execute.models.endpoint = candidate.hostCode.requests'),
 'missing-existing-SIL-return':('08-physical-vocabulary.sysml','flow returnedResult of AnalysisResult from returnResult.result to result;','dependency returnedResult from returnResult to result;'),
 'existing-SIL-new-coding':('08-physical-vocabulary.sysml','codingOrBuildAllowed : Boolean = false','codingOrBuildAllowed : Boolean = true'),
 'physical-stale-report-current':('08-physical-vocabulary.sysml','latest.sameContext and status.presentable','latest.sameContext'),
 'changed-admitted-plan':('08-physical-vocabulary.sysml','bind admittedPlan = plan;','bind admittedPlan = admittedPlan;'),
 'outage-discards-deterministic':('08-physical-vocabulary.sysml','bind scored.report = batch.report;','bind scored.report = scored.report;'),
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--tool',type=Path,default=TOOL)
    parser.add_argument('--negative-cases',action='store_true')
    args=parser.parse_args(); tool=module(args.tool,'native_physical_tool')
    try:
        result=check(tool,args.root)
        if args.negative_cases:
            tests={}
            with tempfile.TemporaryDirectory(prefix='physical-negative-') as td:
                baseline=Path(td)/'baseline'
                shutil.copytree(args.root,baseline/'sysml')
                for folder in ('candidates','traceability'):
                    shutil.copytree(args.root.parent/folder,baseline/folder)
                shutil.copy2(args.root.parent/'trade-selection.tex',baseline/'trade-selection.tex')
                for name,(file,old,new) in MUTATIONS.items():
                    print('Checking negative: '+name,file=sys.stderr,flush=True)
                    case=Path(td)/name; shutil.copytree(baseline,case)
                    path=case/'sysml'/file; text=path.read_text()
                    require(text.count(old)==1,'Negative mutation must match exactly once: '+name)
                    path.write_text(text.replace(old,new))
                    native=tool.validate([case/'sysml'/p for p in FILES],[],warnings_as_errors=True,
                                         config=case/'sysml/physical-allocations.toml')
                    try:
                        check(tool,case/'sysml',validation=native)
                    except (ValueError,KeyError,AttributeError,StopIteration,tool.ToolError) as exc:
                        if isinstance(exc,tool.ToolError) and exc.status!='model_invalid': raise
                        tests[name]={'rejected':True,'native_valid':native.valid,'native_summary':native.summary,'reason':str(exc)[:250]}
                    else:
                        raise ValueError('Negative case accepted: '+name)
                result['negative_cases']=tests
        print(json.dumps(result,indent=2))
    except Exception as exc:
        print(json.dumps({'status':'failed','error':str(exc)},indent=2));return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
