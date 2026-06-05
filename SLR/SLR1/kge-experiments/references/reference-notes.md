# Reference Notes

This folder persists the papers used to shape the KG + embedding experiment plan. Metadata is in `references_used.json`; BibTeX is in `references_used.bib`; open-access PDFs that were directly downloadable are in `../papers/`.

## Search provenance

Recent KG+embedding searches were saved under `../searches/`:

- `s2_kg_text_embeddings_llm_survey_2025_2026.json`
- `scopus_kg_text_embeddings_llm_2025_2026.json`
- `gs_kg_text_embeddings_llm_survey_2025_2026.json`
- `s2_kg_embeddings_evidence_synthesis_2024_2026.json`
- `scopus_kg_embeddings_slr_evidence_2024_2026.json`
- `gs_kg_embeddings_slr_evidence_2024_2026.json`
- `merged_reference_candidates.json`

## Reference categories

### KG-based / machine-actionable literature reviews

- Fathalla et al. (2017), *Towards a Knowledge Graph Representing Research Findings by Semantifying Survey Articles* — foundational semantic representation of survey/review findings.
- Oelen et al. (2020), *Generate FAIR Literature Surveys with Scholarly Knowledge Graphs* — ORKG-style comparison tables and FAIR literature surveys.
- Sahlab et al. (2022), *A Knowledge Graph-Based Method for Automating Systematic Literature Reviews* — direct KG-based SLR automation reference.
- Karras et al. (2023, 2024), *KG-EmpiRE* — community-maintainable / sustainable literature-review KG.
- Wittenborg et al. (2024), *SWARM-SLR* — workflow automation requirements for machine-actionable SLRs.
- John et al. (2025), *ExtracTable* — human-in-the-loop extraction of scientific corpora into structured knowledge.
- Bolaños et al. (2024), *Artificial intelligence for literature reviews: opportunities and challenges* — broader AI-for-SLR context, explicitly identifying KGs and LLMs as future directions.

### Scholarly KGs, semantic literature exploration, and hypothesis generation

- Dessì et al. (2025), *CS-KG 2.0* — large-scale scientific KG enabling trend analysis, question answering, hypothesis generation, and automatic literature-review support.
- StructRAG (2025) — structure-aware RAG with a scholarly KG.
- ORKG ASK (2025/2026) — neuro-symbolic scholarly search and exploration.
- Borrego/Dessì et al. (2025), *Research hypothesis generation over scientific knowledge graphs* — combines path features, KGE, text embeddings, and bibliometric data.
- Xi et al. (2026), *Enhancing academic paper recommendations using fine-grained knowledge entities and multifaceted document embeddings* — paper recommendation from KG-like entities plus embeddings.

### KG + embeddings + LLM synthesis references

- Liu et al. (2025), *Large Language Models for Knowledge Graph Embedding: A Survey* — KGE and LLM integration taxonomy.
- Cai et al. (2025), *Practices, opportunities and challenges in the fusion of knowledge graphs and large language models* — KG-enhanced LLMs, LLM-enhanced KGs, collaborative KG/LLM systems.
- Wang et al. (2025), *Graph Machine Learning in the Era of Large Language Models* — graph ML, text-attributed graphs, and LLM/KG synergy.
- Ma et al. (2025), *Large Language Models Meet Knowledge Graphs for Question Answering* — useful for GraphRAG-style querying over the SLR KG.
- Yu et al. (2026), *Graph2text or Graph2token* — graph-to-text / graph-to-token integration approaches.
- Choi & Jung (2025), *Knowledge Graph Construction: Extraction, Learning, and Evaluation* — recent KG construction and evaluation survey.

### Evidence-map / review visualization references

- Mallavarapu et al. (2026), *Interactive Evidence Maps for Visualizing and Understanding Systematic Reviews* — directly relevant to planned evidence-map outputs; applies LLM-assisted topic modeling to a published scoping review and shows an interactive final evidence-map interface.
- Xie et al. (2025), *A Knowledge Graph-Based RAG-GLLM Approach for Literature Review and Knowledge Discovery* — recent KG-RAG literature-review application; useful for seeing how KG + retrieval/embedding ideas are positioned for literature-review synthesis.
- Doh et al. (2022), *A Systematic Review of Deep Knowledge Graph-Based Recommender Systems, with Focus on Explainable Embeddings* — a complete SLR about KG embeddings; useful as a finished systematic-review example with KG-embedding taxonomies, though it does not itself build a KG of the review output.

## Download status

PDFs were successfully saved for:

- `bolanos_2024_ai_for_literature_reviews.pdf`
- `cai_2025_kg_llm_fusion.pdf`
- `doh_2022_deep_kg_recommender_systems_slr_embeddings.pdf`
- `extractable_2025.pdf`
- `fathalla_2017_semantifying_survey_articles.pdf`
- `ma_2025_llms_meet_kgs_qa.pdf`
- `mallavarapu_2026_interactive_evidence_maps.pdf`
- `swarm_slr_2024.pdf`
- `xie_2025_kg_rag_gllm_literature_review.pdf`

Some direct downloads were blocked by publisher anti-bot protections or unavailable through OA APIs. Their metadata and URLs are still preserved in `references_used.json`.
