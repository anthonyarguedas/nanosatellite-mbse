#!/usr/bin/env python3
"""Build E11 hybrid KG + embedding similarity graph for SLR1.

The base KG CSVs remain unchanged. This script reads `kg/nodes.csv`,
`kg/edges.csv`, and ISSUE-003 nearest-neighbor/card metadata, then writes a
separate GraphML export with exploratory `SIMILAR_TO` edges and a community
summary table.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

from kg_common import (
    BASE_DIR,
    GRAPH_EXPORTS_DIR,
    KG_DIR,
    REPORTS_DIR,
    TABLES_DIR,
    clean_text,
    ensure_dirs,
    load_jsonl,
    markdown_table,
    node_id,
    write_csv,
    write_graphml,
    write_text,
)


EMBEDDINGS_DIR = BASE_DIR / "embeddings"
CARD_INDEX_PATH = EMBEDDINGS_DIR / "card_index.jsonl"
NEIGHBORS_PATH = EMBEDDINGS_DIR / "nearest_neighbors.jsonl"
MANIFEST_PATH = EMBEDDINGS_DIR / "embedding_manifest.json"
NODES_PATH = KG_DIR / "nodes.csv"
EDGES_PATH = KG_DIR / "edges.csv"

PLAN_THRESHOLDS = {
    "study_card": 0.72,
    "claim_card": 0.78,
    "emergent_code_card": 0.78,
}
AUDITED_THRESHOLDS = {
    "study_card": 0.72,
    # The implementation-plan 0.78 threshold yields zero claim-card edges for
    # the deterministic hashing-TFIDF fallback. The audited fallback threshold
    # keeps only the highest-specificity claim pairs (about the top 1% of
    # nearest-neighbor similarities) and is documented in the report.
    "claim_card": 0.65,
    "emergent_code_card": 0.78,
}
UNIT_TYPE_LABELS = {
    "study_card": "Study",
    "claim_card": "Claim",
    "emergent_code_card": "EmergentCode",
}

COMMUNITY_COLUMNS = [
    "community_id",
    "node_count",
    "edge_count_internal",
    "similarity_edge_count_internal",
    "study_count",
    "claim_count",
    "emergent_code_count",
    "top_node_types",
    "representative_studies",
    "representative_claims",
    "representative_emergent_codes",
    "controlled_label_examples",
    "community_method",
    "exploratory",
]


def require_paths(paths: Iterable[Path], issue_hint: str) -> None:
    missing = [path for path in paths if not path.exists()]
    if missing:
        missing_text = ", ".join(str(path.relative_to(BASE_DIR)) for path in missing)
        raise FileNotFoundError(f"Missing required {issue_hint} artifact(s): {missing_text}. Run the earlier issue scripts first.")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_cards() -> dict[str, dict[str, Any]]:
    cards = {}
    for card in load_jsonl(CARD_INDEX_PATH):
        unit_type = str(card.get("unit_type"))
        if unit_type in AUDITED_THRESHOLDS:
            cards[str(card.get("card_id"))] = card
    return cards


def card_to_kg_node(card: dict[str, Any]) -> str | None:
    unit_type = str(card.get("unit_type"))
    if unit_type == "study_card":
        return clean_text(card.get("study_id"))
    if unit_type == "claim_card":
        return clean_text(card.get("claim_id")) or str(card.get("card_id", "")).replace("claim_card::", "")
    if unit_type == "emergent_code_card":
        metadata = card.get("metadata", {}) if isinstance(card.get("metadata"), dict) else {}
        source_record = metadata.get("source_record", {}) if isinstance(metadata.get("source_record"), dict) else {}
        label = clean_text(source_record.get("label")) or clean_text(card.get("label"))
        if label:
            return node_id("EmergentCode", label)
    return None


def build_base_graph(node_rows: list[dict[str, str]], edge_rows: list[dict[str, str]]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.graph["construction_version"] = "issue-004-hybrid-similarity-v1"
    graph.graph["description"] = "SLR1 hybrid controlled-code KG plus exploratory embedding SIMILAR_TO edges"
    graph.graph["base_kg_edges_unchanged"] = "true"
    for row in node_rows:
        graph.add_node(
            row["id"],
            label=row.get("label", row["id"]),
            type=row.get("type", ""),
            properties_json=row.get("properties_json", ""),
        )
    for idx, row in enumerate(edge_rows, start=1):
        graph.add_edge(
            row["source"],
            row["target"],
            key=f"kg_e{idx:07d}",
            type=row.get("type", ""),
            source_field_path=row.get("source_field_path", ""),
            source_value=row.get("source_value", ""),
            rationale=row.get("rationale", ""),
            evidence_quote=row.get("evidence_quote", ""),
            confidence=row.get("confidence", ""),
            properties_json=row.get("properties_json", ""),
            exploratory="false",
        )
    return graph


def collect_similarity_pairs(
    cards_by_id: dict[str, dict[str, Any]],
    kg_node_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    """Return undirected, de-duplicated same-unit similarity edges."""
    plan_counts: dict[str, dict[str, int]] = {
        unit_type: {"plan_directed_records": 0, "audited_directed_records": 0}
        for unit_type in AUDITED_THRESHOLDS
    }
    best_by_pair: dict[tuple[str, str, str], dict[str, Any]] = {}

    with NEIGHBORS_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            unit_type = str(record.get("unit_type"))
            if unit_type not in AUDITED_THRESHOLDS:
                continue
            score = float(record.get("cosine_similarity", 0.0))
            if score >= PLAN_THRESHOLDS[unit_type]:
                plan_counts[unit_type]["plan_directed_records"] += 1
            if score < AUDITED_THRESHOLDS[unit_type]:
                continue
            plan_counts[unit_type]["audited_directed_records"] += 1
            source_card = cards_by_id.get(str(record.get("card_id")))
            target_card = cards_by_id.get(str(record.get("neighbor_card_id")))
            if not source_card or not target_card:
                continue
            source_node = card_to_kg_node(source_card)
            target_node = card_to_kg_node(target_card)
            if not source_node or not target_node or source_node == target_node:
                continue
            if source_node not in kg_node_ids or target_node not in kg_node_ids:
                continue
            left, right = sorted((source_node, target_node))
            key = (unit_type, left, right)
            current = best_by_pair.get(key)
            if current is None or score > float(current["cosine"]):
                best_by_pair[key] = {
                    "type": "SIMILAR_TO",
                    "model": MODEL_NAME_FROM_MANIFEST,
                    "cosine": round(score, 6),
                    "unit_type": unit_type,
                    "unit_label": UNIT_TYPE_LABELS[unit_type],
                    "source": "embedding_nearest_neighbors",
                    "exploratory": "true",
                    "threshold": AUDITED_THRESHOLDS[unit_type],
                    "plan_threshold": PLAN_THRESHOLDS[unit_type],
                    "source_card_id": source_card.get("card_id"),
                    "target_card_id": target_card.get("card_id"),
                    "source_node": left,
                    "target_node": right,
                }

    rows = sorted(
        best_by_pair.values(),
        key=lambda row: (str(row["unit_type"]), -float(row["cosine"]), str(row["source_node"]), str(row["target_node"])),
    )
    return rows, plan_counts


# Filled in main after reading the embedding manifest; kept module-level so the
# pair collector can stay simple without threading metadata through every call.
MODEL_NAME_FROM_MANIFEST = "hashing_tfidf_v1"


def add_similarity_edges(graph: nx.MultiDiGraph, similarity_rows: list[dict[str, Any]]) -> None:
    for idx, row in enumerate(similarity_rows, start=1):
        graph.add_edge(
            row["source_node"],
            row["target_node"],
            key=f"sim_e{idx:07d}",
            type="SIMILAR_TO",
            model=row["model"],
            cosine=float(row["cosine"]),
            unit_type=row["unit_type"],
            unit_label=row["unit_label"],
            source="embedding_nearest_neighbors",
            exploratory="true",
            threshold=float(row["threshold"]),
            plan_threshold=float(row["plan_threshold"]),
            source_card_id=row["source_card_id"],
            target_card_id=row["target_card_id"],
        )


def as_simple_undirected(graph: nx.MultiDiGraph) -> nx.Graph:
    simple = nx.Graph()
    for node, attrs in graph.nodes(data=True):
        simple.add_node(node, **attrs)
    for source, target, attrs in graph.edges(data=True):
        edge_type = attrs.get("type", "")
        weight = float(attrs.get("cosine", 1.0)) if edge_type == "SIMILAR_TO" else 1.0
        if simple.has_edge(source, target):
            simple[source][target]["weight"] = float(simple[source][target].get("weight", 0.0)) + weight
            simple[source][target]["edge_count"] = int(simple[source][target].get("edge_count", 1)) + 1
            if edge_type == "SIMILAR_TO":
                simple[source][target]["similarity_edge_count"] = int(simple[source][target].get("similarity_edge_count", 0)) + 1
        else:
            simple.add_edge(
                source,
                target,
                weight=weight,
                edge_count=1,
                similarity_edge_count=1 if edge_type == "SIMILAR_TO" else 0,
            )
    return simple


def detect_communities(simple: nx.Graph) -> tuple[list[set[str]], str]:
    if simple.number_of_nodes() == 0:
        return [], "none"
    try:
        communities = list(nx.algorithms.community.greedy_modularity_communities(simple, weight="weight"))
        method = "networkx.greedy_modularity_communities(weighted undirected projection)"
    except Exception:
        communities = [set(component) for component in nx.connected_components(simple)]
        method = "networkx.connected_components fallback"
    communities = [set(community) for community in communities]
    communities.sort(key=lambda community: (-len(community), min(str(node) for node in community)))
    return communities, method


def top_labels(items: Iterable[str], max_items: int = 8) -> str:
    counts = Counter(items)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], str(item[0]).lower()))[:max_items]
    return "; ".join(f"{label} ({count})" for label, count in ordered)


def representative_nodes(simple: nx.Graph, nodes: list[str], max_items: int = 8) -> list[str]:
    return sorted(nodes, key=lambda node: (-simple.degree(node), str(node)))[:max_items]


def write_community_table(graph: nx.MultiDiGraph, simple: nx.Graph, communities: list[set[str]], method: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, community in enumerate(communities, start=1):
        subgraph = simple.subgraph(community)
        node_types = Counter(str(graph.nodes[node].get("type", "")) for node in community)
        study_nodes = sorted(node for node in community if graph.nodes[node].get("type") == "Study")
        claim_nodes = sorted(node for node in community if graph.nodes[node].get("type") == "Claim")
        emergent_nodes = sorted(node for node in community if graph.nodes[node].get("type") == "EmergentCode")
        controlled_examples = sorted(
            str(graph.nodes[node].get("label", node))
            for node in community
            if graph.nodes[node].get("type") not in {"Study", "Claim"}
        )[:12]
        similarity_edges = 0
        for source, target, attrs in graph.edges(data=True):
            if source in community and target in community and attrs.get("type") == "SIMILAR_TO":
                similarity_edges += 1
        rows.append(
            {
                "community_id": f"hybrid_community_{idx:03d}",
                "node_count": len(community),
                "edge_count_internal": subgraph.number_of_edges(),
                "similarity_edge_count_internal": similarity_edges,
                "study_count": len(study_nodes),
                "claim_count": len(claim_nodes),
                "emergent_code_count": len(emergent_nodes),
                "top_node_types": top_labels(node_types.elements()),
                "representative_studies": "; ".join(representative_nodes(simple, study_nodes)),
                "representative_claims": "; ".join(representative_nodes(simple, claim_nodes)),
                "representative_emergent_codes": "; ".join(representative_nodes(simple, emergent_nodes)),
                "controlled_label_examples": "; ".join(controlled_examples),
                "community_method": method,
                "exploratory": True,
            }
        )
    write_csv(TABLES_DIR / "hybrid_communities.csv", rows, COMMUNITY_COLUMNS)
    return rows


def write_report(
    *,
    graph: nx.MultiDiGraph,
    base_node_count: int,
    base_edge_count: int,
    similarity_rows: list[dict[str, Any]],
    plan_counts: dict[str, dict[str, int]],
    community_rows: list[dict[str, Any]],
    community_method: str,
    model_name: str,
) -> None:
    similarity_counts = Counter(row["unit_type"] for row in similarity_rows)
    threshold_rows = []
    for unit_type in ["study_card", "claim_card", "emergent_code_card"]:
        threshold_rows.append(
            {
                "unit_type": unit_type,
                "plan_threshold": PLAN_THRESHOLDS[unit_type],
                "audited_threshold_used": AUDITED_THRESHOLDS[unit_type],
                "plan_directed_neighbor_records": plan_counts[unit_type]["plan_directed_records"],
                "audited_directed_neighbor_records": plan_counts[unit_type]["audited_directed_records"],
                "deduplicated_similarity_edges": similarity_counts.get(unit_type, 0),
            }
        )
    top_communities = sorted(
        community_rows,
        key=lambda row: (-int(row["similarity_edge_count_internal"]), -int(row["study_count"]), -int(row["claim_count"]), row["community_id"]),
    )[:15]
    top_edges = sorted(similarity_rows, key=lambda row: (-float(row["cosine"]), str(row["unit_type"])))[:20]

    report = f"""# E11 — Hybrid similarity graph

**Exploratory notice:** `SIMILAR_TO` edges are embedding-derived audit links from `{model_name}` nearest neighbors. They are not controlled-code assertions and do not modify the base KG.

## Inputs and graph construction

- Base KG input: `kg/nodes.csv` (**{base_node_count}** nodes) and `kg/edges.csv` (**{base_edge_count}** edges).
- Embedding input: `embeddings/nearest_neighbors.jsonl` plus card metadata from `embeddings/card_index.jsonl`.
- Hybrid output: `outputs/graph_exports/hybrid_similarity_graph.graphml`.
- Base `kg/edges.csv` was not overwritten.

## Thresholds and similarity-edge counts

{markdown_table(threshold_rows, ["unit_type", "plan_threshold", "audited_threshold_used", "plan_directed_neighbor_records", "audited_directed_neighbor_records", "deduplicated_similarity_edges"], max_rows=10)}

The implementation-plan claim threshold (`0.78`) produced zero claim-card edges with the deterministic hashing-TFIDF fallback, whose nearest-neighbor cosine range is compressed relative to neural sentence embeddings. For E11, the audited claim threshold is lowered to `0.65` and documented here; study (`0.72`) and emergent-code (`0.78`) thresholds retain the plan values.

Total deduplicated `SIMILAR_TO` edges added: **{len(similarity_rows)}**.
Hybrid graph total: **{graph.number_of_nodes()}** nodes and **{graph.number_of_edges()}** edges.

## Highest-similarity edges

{markdown_table(top_edges, ["unit_type", "source_node", "target_node", "cosine", "threshold"], max_rows=20)}

## Communities

Community method: `{community_method}` over an undirected weighted projection of controlled-code and similarity edges.
Communities detected: **{len(community_rows)}**.

{markdown_table(top_communities, ["community_id", "node_count", "similarity_edge_count_internal", "study_count", "claim_count", "emergent_code_count", "representative_studies", "representative_claims"], max_rows=15)}

Caveats: the local embedding fallback is lexical hashing-TFIDF, so thresholds are corpus/model-specific. Similarity edges should be manually inspected before they are used as evidence.
"""
    write_text(REPORTS_DIR / "e11_hybrid_similarity_graph.md", report)


def main() -> None:
    global MODEL_NAME_FROM_MANIFEST
    require_paths([NODES_PATH, EDGES_PATH, CARD_INDEX_PATH, NEIGHBORS_PATH, MANIFEST_PATH], "ISSUE-002/ISSUE-003")
    ensure_dirs(GRAPH_EXPORTS_DIR, TABLES_DIR, REPORTS_DIR)

    manifest = load_manifest()
    MODEL_NAME_FROM_MANIFEST = clean_text(manifest.get("model_name")) or "hashing_tfidf_v1"
    node_rows = read_csv_rows(NODES_PATH)
    edge_rows = read_csv_rows(EDGES_PATH)
    graph = build_base_graph(node_rows, edge_rows)
    cards_by_id = load_cards()
    similarity_rows, plan_counts = collect_similarity_pairs(cards_by_id, set(graph.nodes))
    add_similarity_edges(graph, similarity_rows)

    write_graphml(graph, GRAPH_EXPORTS_DIR / "hybrid_similarity_graph.graphml")

    simple = as_simple_undirected(graph)
    communities, method = detect_communities(simple)
    community_rows = write_community_table(graph, simple, communities, method)
    write_report(
        graph=graph,
        base_node_count=len(node_rows),
        base_edge_count=len(edge_rows),
        similarity_rows=similarity_rows,
        plan_counts=plan_counts,
        community_rows=community_rows,
        community_method=method,
        model_name=MODEL_NAME_FROM_MANIFEST,
    )

    print("Hybrid similarity graph complete (exploratory):")
    print(f"  base_nodes: {len(node_rows)}")
    print(f"  base_edges: {len(edge_rows)}")
    print(f"  similarity_edges: {len(similarity_rows)}")
    for unit_type, count in sorted(Counter(row["unit_type"] for row in similarity_rows).items()):
        print(f"  {unit_type}_similarity_edges: {count}")
    print(f"  hybrid_communities: {len(community_rows)}")


if __name__ == "__main__":
    main()
