// Generic Neo4j import for SLR1 KG CSV artifacts.
// Copy nodes.csv and edges.csv into the Neo4j import directory before running.
// This portable script uses a generic :KGNode label and :KG_EDGE relationship,
// while preserving the controlled node label / edge type in properties.

CREATE CONSTRAINT kg_node_id IF NOT EXISTS
FOR (n:KGNode) REQUIRE n.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (n:KGNode {id: row.id})
SET n.label = row.label,
    n.type = row.type,
    n.properties_json = row.properties_json;

LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (source:KGNode {id: row.source})
MATCH (target:KGNode {id: row.target})
MERGE (source)-[edge:KG_EDGE {
    edge_key: row.source + '|' + row.target + '|' + row.type + '|' + row.source_field_path + '|' + row.source_value
}]->(target)
SET edge.type = row.type,
    edge.source_field_path = row.source_field_path,
    edge.source_value = row.source_value,
    edge.rationale = row.rationale,
    edge.evidence_quote = row.evidence_quote,
    edge.confidence = row.confidence,
    edge.properties_json = row.properties_json;
