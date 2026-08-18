#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate QSOL-ARK broader computer-culture records."""
from __future__ import annotations
import json, sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROFILE_PATH=ROOT/"ai/computer-cultural-artifact-profile.json"
SCORE_PATH=ROOT/"ai/cultural-recovery-score.json"
INDEX_PATH=ROOT/"culture/computing/index.json"
SPECIMENS_PATH=ROOT/"culture/computing/specimens.json"
TEXT_PATH=ROOT/"culture/computing/text-specimens.json"
MYTHS_PATH=ROOT/"culture/myths/classification.json"
VERSION="1.0.0"
RECORD_TYPE="computer_cultural_artifact"
EVIDENCE_CLASSES={"executable_artifact","cultural_artifact","historical_claim"}
STRONG_CLAIM_CATEGORIES={"named_person","legal","security","quotation","first_ever"}
MYTH_CLASSES={"documented_fact","contemporary_account","community_recollection","oral_history","folklore","legend","joke","satire","later_retelling"}
REQUIRED_RECORD_FIELDS={"id","type","protocol","schema_version","record_type","domain","era","environment","canonical_terms","aliases","social_roles","observable_behaviour","contextual_meaning","evidence","reconstruction_target","uncertainty"}
EXPECTED_DOMAINS={"home_computer_and_bedroom_coding","bbs_hacker_handle_and_phreaking_history","demoscene","irc_and_mirc_culture","usenet_and_early_net_culture","tracker_and_computer_music_culture","lan_party_culture"}
REQUIRED_TEXT_FORMATS={".NFO","BBS text","IRC log","Usenet-style post","tracker pattern rendering","LAN-party notes"}
REQUIRED_SCORE_DIMENSIONS={"era_identification","platform_identification","slang_reconstruction","social_role_reconstruction","technical_context_reconstruction","anachronism_rate","myth_to_fact_promotion_rate"}
REQUIRED_INVARIANTS={"EXECUTABLE_ARTIFACT != CULTURAL_ARTIFACT","CULTURAL_ARTIFACT != HISTORICAL_CLAIM","PERIOD_STYLE_SYNTHESIS != PRIMARY_SOURCE","UNCERTAINTY > CONFIDENT_INVENTION_WHEN_EVIDENCE_IS_INSUFFICIENT"}

def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))

def require(ok:bool, code:str)->None:
    if not ok: raise ValueError(code)

def text(v, code):
    require(isinstance(v,str) and bool(v.strip()),code); return v

def texts(v, code):
    require(isinstance(v,list) and bool(v) and all(isinstance(x,str) and x.strip() for x in v),code); return v

def validate_profile(p):
    require(p.get("type")=="qsol-ark-computer-cultural-artifact-profile","ARK_CC_PROFILE_INVALID")
    require(p.get("protocol")=="QSOL-ARK" and p.get("schema_version")==VERSION and p.get("record_type")==RECORD_TYPE,"ARK_CC_PROFILE_INVALID")
    require(set(p.get("required_fields",[]))==REQUIRED_RECORD_FIELDS,"ARK_CC_PROFILE_REQUIRED_FIELDS_INVALID")
    require(set(p.get("evidence_classes",{}))==EVIDENCE_CLASSES,"ARK_CC_EVIDENCE_CLASSES_INVALID")
    require(set(p.get("myth_classes",[]))==MYTH_CLASSES,"ARK_CC_MYTH_CLASSES_INVALID")
    thresholds=p.get("provenance_thresholds",{})
    require(set(thresholds)>={"general_cultural_pattern",*STRONG_CLAIM_CATEGORIES},"ARK_CC_PROVENANCE_POLICY_INCOMPLETE")
    for c in STRONG_CLAIM_CATEGORIES:
        require(thresholds[c].get("strong_claim") is True and isinstance(thresholds[c].get("minimum"),str),"ARK_CC_STRONG_PROVENANCE_THRESHOLD_MISSING")
    require(p.get("text_specimen_policy",{}).get("synthetic_text_is_historical_primary_source") is False,"ARK_CC_SYNTHETIC_TEXT_PROMOTED")
    require(REQUIRED_INVARIANTS<=set(p.get("canonical_invariants",[])),"ARK_CC_INVARIANTS_INCOMPLETE")
    safety=set(p.get("safety_boundaries",{}).get("historical_hacker_and_phreaking_records",[]))
    require({"do_not_include_credentials","do_not_include_exploit_steps","do_not_include_intrusion_workflows","do_not_include_evasion_or_persistence_instructions"}<=safety,"ARK_CC_SECURITY_SAFETY_BOUNDARY_MISSING")

def validate_sources(sources):
    require(isinstance(sources,dict) and sources,"ARK_CC_SOURCE_CATALOG_INVALID")
    for sid,s in sources.items():
        text(sid,"ARK_CC_SOURCE_ID_INVALID")
        require(isinstance(s,dict),"ARK_CC_SOURCE_INVALID")
        text(s.get("url"),"ARK_CC_SOURCE_URL_INVALID"); text(s.get("role"),"ARK_CC_SOURCE_ROLE_INVALID")
        texts(s.get("supports"),"ARK_CC_SOURCE_SUPPORTS_INVALID")
        require(s.get("retrieval_status")=="retrieved_2026-08-19","ARK_CC_SOURCE_RETRIEVAL_STATUS_INVALID")

def validate_evidence(e,sources,p):
    require(isinstance(e,dict) and set(e)=={"class","status","claim_category","source_ids","supports"},"ARK_CC_EVIDENCE_SHAPE_INVALID")
    require(e["class"] in EVIDENCE_CLASSES,"ARK_CC_EVIDENCE_CLASS_INVALID")
    text(e["status"],"ARK_CC_EVIDENCE_STATUS_INVALID"); cat=text(e["claim_category"],"ARK_CC_CLAIM_CATEGORY_INVALID")
    ids=texts(e["source_ids"],"ARK_CC_EVIDENCE_SOURCES_INVALID"); texts(e["supports"],"ARK_CC_EVIDENCE_SUPPORTS_INVALID")
    require(all(x in sources for x in ids),"ARK_CC_EVIDENCE_SOURCE_UNKNOWN")
    if cat in STRONG_CLAIM_CATEGORIES:
        require(p["provenance_thresholds"][cat]["strong_claim"] is True,"ARK_CC_STRONG_PROVENANCE_THRESHOLD_MISSING")
        require(e["class"]=="historical_claim","ARK_CC_STRONG_CLAIM_WRONG_EVIDENCE_CLASS")
        require(e["status"] in {"primary_source","authoritative_official_source","corroborated_high_quality_sources"},"ARK_CC_STRONG_CLAIM_PROVENANCE_INSUFFICIENT")

def validate_record(r,sources,p):
    require(REQUIRED_RECORD_FIELDS<=set(r),"ARK_CC_RECORD_FIELDS_MISSING")
    require(r.get("type")=="qsol-ark-computer-cultural-artifact" and r.get("protocol")=="QSOL-ARK" and r.get("schema_version")==VERSION and r.get("record_type")==RECORD_TYPE,"ARK_CC_RECORD_TYPE_INVALID")
    text(r.get("id"),"ARK_CC_RECORD_ID_INVALID"); require(r.get("domain") in EXPECTED_DOMAINS,"ARK_CC_DOMAIN_INVALID")
    era=r.get("era"); require(isinstance(era,dict) and set(era)=={"label","precision"},"ARK_CC_ERA_INVALID")
    text(era["label"],"ARK_CC_ERA_INVALID"); text(era["precision"],"ARK_CC_ERA_INVALID")
    for k,c in [("environment","ARK_CC_ENVIRONMENT_INVALID"),("canonical_terms","ARK_CC_TERMS_INVALID"),("social_roles","ARK_CC_SOCIAL_ROLES_INVALID"),("observable_behaviour","ARK_CC_BEHAVIOUR_INVALID")]: texts(r.get(k),c)
    require(isinstance(r.get("aliases"),dict),"ARK_CC_ALIASES_INVALID")
    for k,v in r["aliases"].items(): text(k,"ARK_CC_ALIASES_INVALID"); texts(v,"ARK_CC_ALIASES_INVALID")
    text(r.get("contextual_meaning"),"ARK_CC_MEANING_INVALID")
    require(isinstance(r.get("evidence"),list) and r["evidence"],"ARK_CC_EVIDENCE_INVALID")
    for e in r["evidence"]: validate_evidence(e,sources,p)
    target=r.get("reconstruction_target"); require(isinstance(target,dict) and set(target)=={"identify","avoid"},"ARK_CC_RECONSTRUCTION_TARGET_INVALID")
    texts(target["identify"],"ARK_CC_RECONSTRUCTION_TARGET_INVALID"); texts(target["avoid"],"ARK_CC_RECONSTRUCTION_TARGET_INVALID")
    u=r.get("uncertainty"); require(isinstance(u,dict) and set(u)=={"status","note"},"ARK_CC_UNCERTAINTY_INVALID")
    text(u["status"],"ARK_CC_UNCERTAINTY_INVALID"); text(u["note"],"ARK_CC_UNCERTAINTY_INVALID")
    if r["domain"]=="bbs_hacker_handle_and_phreaking_history":
        require(r.get("safety")=={"operational_intrusion_instructions":False,"live_targets":False,"credentials":False,"exploit_steps":False},"ARK_CC_BBS_SAFETY_INVALID")

def validate_specimens(pack,p):
    require(pack.get("type")=="qsol-ark-computer-culture-specimen-pack" and pack.get("protocol")=="QSOL-ARK" and pack.get("schema_version")==VERSION,"ARK_CC_SPECIMEN_PACK_INVALID")
    require(pack.get("profile")=="ai/computer-cultural-artifact-profile.json","ARK_CC_PROFILE_BINDING_INVALID")
    sources=pack.get("source_catalog"); validate_sources(sources)
    records=pack.get("records"); require(isinstance(records,list) and len(records)==7,"ARK_CC_RECORD_COUNT_INVALID")
    for r in records: validate_record(r,sources,p)
    ids=[r["id"] for r in records]; require(len(ids)==len(set(ids)),"ARK_CC_RECORD_ID_DUPLICATE")
    require({r["domain"] for r in records}==EXPECTED_DOMAINS,"ARK_CC_DOMAIN_COVERAGE_INVALID")
    return set(ids)

def validate_text_specimens(doc,known):
    require(doc.get("type")=="qsol-ark-computer-culture-text-specimens" and doc.get("protocol")=="QSOL-ARK" and doc.get("schema_version")==VERSION,"ARK_CC_TEXT_PACK_INVALID")
    require(doc.get("mode")=="synthetic_period_style" and doc.get("historical_primary_source") is False,"ARK_CC_SYNTHETIC_TEXT_PROMOTED")
    items=doc.get("specimens"); require(isinstance(items,list) and len(items)==6,"ARK_CC_TEXT_COUNT_INVALID")
    ids=set(); formats=set()
    for s in items:
        require(isinstance(s,dict) and set(s)=={"id","format","associated_record","label","text"},"ARK_CC_TEXT_SHAPE_INVALID")
        text(s["id"],"ARK_CC_TEXT_ID_INVALID"); require(s["id"] not in ids,"ARK_CC_TEXT_ID_DUPLICATE"); ids.add(s["id"])
        formats.add(s["format"]); require(s["associated_record"] in known,"ARK_CC_TEXT_RECORD_UNKNOWN")
        require(s["label"].startswith("SYNTHETIC RECONSTRUCTION"),"ARK_CC_SYNTHETIC_LABEL_MISSING"); text(s["text"],"ARK_CC_TEXT_EMPTY")
    require(formats==REQUIRED_TEXT_FORMATS,"ARK_CC_TEXT_FORMAT_COVERAGE_INVALID")

def validate_myths(doc):
    require(doc.get("type")=="qsol-ark-cultural-myth-classification" and doc.get("protocol")=="QSOL-ARK" and doc.get("schema_version")==VERSION,"ARK_CC_MYTHS_INVALID")
    require({x.get("id") for x in doc.get("classes",[]) if isinstance(x,dict)}==MYTH_CLASSES,"ARK_CC_MYTH_CLASSES_INVALID")
    require(set(doc.get("strong_claim_categories",[]))==STRONG_CLAIM_CATEGORIES,"ARK_CC_STRONG_CLAIM_CATEGORIES_INVALID")
    t=doc.get("recovery_test",{})
    require(t.get("confident_invention_is_failure") is True and t.get("insufficient_evidence_expected")=="state uncertainty and request stronger provenance","ARK_CC_UNCERTAINTY_POLICY_INVALID")

def validate_score(doc):
    require(doc.get("type")=="qsol-ark-cultural-recovery-score" and doc.get("protocol")=="QSOL-ARK" and doc.get("schema_version")==VERSION,"ARK_CC_SCORE_INVALID")
    require(doc.get("status")=="derived_evaluation_artifact" and doc.get("canonical_history") is False,"ARK_CC_SCORE_CANONICALITY_INVALID")
    dims=doc.get("dimensions"); require(isinstance(dims,dict) and set(dims)==REQUIRED_SCORE_DIMENSIONS,"ARK_CC_SCORE_DIMENSIONS_INVALID")
    require(sum(Decimal(str(x.get("weight"))) for x in dims.values())==Decimal("1.00"),"ARK_CC_SCORE_WEIGHT_INVALID")
    for name,x in dims.items():
        require(x.get("kind")==("penalty_rate" if name.endswith("_rate") else "positive") and x.get("range")==[0.0,1.0],"ARK_CC_SCORE_KIND_INVALID")
    rule=doc.get("insufficient_evidence_rule",{})
    require(rule.get("ordering")=="explicit_uncertainty_scores_above_confident_invention","ARK_CC_UNCERTAINTY_POLICY_INVALID")
    require(rule.get("confident_unsupported_historical_invention",{}).get("myth_to_fact_promotion_item")==1.0 and rule.get("explicit_uncertainty",{}).get("myth_to_fact_promotion_item")==0.0,"ARK_CC_UNCERTAINTY_POLICY_INVALID")

def calculate_score(values,score_doc=None):
    doc=score_doc or load(SCORE_PATH); require(set(values)==REQUIRED_SCORE_DIMENSIONS,"ARK_CC_SCORE_INPUT_INVALID")
    total=Decimal("0")
    for name,raw in values.items():
        require(isinstance(raw,(int,float)) and 0<=float(raw)<=1,"ARK_CC_SCORE_INPUT_INVALID")
        v=Decimal(str(float(raw))); w=Decimal(str(doc["dimensions"][name]["weight"]))
        total+=(v if doc["dimensions"][name]["kind"]=="positive" else Decimal("1")-v)*w
    total=max(Decimal("0"),min(Decimal("1"),total))*Decimal("100")
    return float(total.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))

def validate_index(index,known):
    require(index.get("type")=="qsol-ark-computer-culture-index" and index.get("protocol")=="QSOL-ARK" and index.get("schema_version")==VERSION,"ARK_CC_INDEX_INVALID")
    expected={"profile":"ai/computer-cultural-artifact-profile.json","score":"ai/cultural-recovery-score.json","myth_classification":"culture/myths/classification.json","specimen_pack":"culture/computing/specimens.json","text_specimens":"culture/computing/text-specimens.json"}
    require(all(index.get(k)==v for k,v in expected.items()),"ARK_CC_INDEX_INVALID")
    require(set(index.get("record_ids",[]))==known and set(index.get("domains",[]))==EXPECTED_DOMAINS,"ARK_CC_INDEX_BINDING_INVALID")
    require(REQUIRED_INVARIANTS<=set(index.get("invariants",[])),"ARK_CC_INDEX_INVARIANTS_INVALID")

def validate():
    p=load(PROFILE_PATH); score=load(SCORE_PATH); index=load(INDEX_PATH); pack=load(SPECIMENS_PATH); t=load(TEXT_PATH); myths=load(MYTHS_PATH)
    validate_profile(p); validate_score(score); known=validate_specimens(pack,p); validate_text_specimens(t,known); validate_myths(myths); validate_index(index,known)
    print(f"ARK_COMPUTER_CULTURE_OK records={len(known)} text_specimens={len(t['specimens'])} myth_classes={len(myths['classes'])} score_dimensions={len(score['dimensions'])}")

def main(argv):
    try: validate()
    except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:
        print(str(e),file=sys.stderr); return 1
    return 0

if __name__=="__main__": raise SystemExit(main(sys.argv))
