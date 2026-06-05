-- DuckDB graph table loader for SLR1 KG CSV artifacts.
-- Run from SLR/SLR1/kge-experiments/kg or adjust paths below.

CREATE OR REPLACE TABLE kg_nodes AS
SELECT * FROM read_csv_auto('nodes.csv', header = true);

CREATE OR REPLACE TABLE kg_edges AS
SELECT * FROM read_csv_auto('edges.csv', header = true);

CREATE OR REPLACE VIEW kg_node_type_counts AS
SELECT type, count(*) AS node_count
FROM kg_nodes
GROUP BY type
ORDER BY node_count DESC, type;

CREATE OR REPLACE VIEW kg_edge_type_counts AS
SELECT type, count(*) AS edge_count
FROM kg_edges
GROUP BY type
ORDER BY edge_count DESC, type;
