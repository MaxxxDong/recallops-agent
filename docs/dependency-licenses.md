# Dependency license inventory

| Component | Frozen version/model | License | Use |
| --- | --- | --- | --- |
| RecallOps | 0.1.0 | MIT | Application |
| httpx | 0.28.1 | BSD-3-Clause | Authenticated MCP Streamable HTTP transport |
| langchain-cockroachdb | 0.2.1 | Apache-2.0 | C-SPANN vector store and CockroachDB checkpointer base |
| langgraph | 1.2.9 | MIT | Resumable state graph |
| mcp | 1.28.1 | MIT | Official Streamable HTTP MCP client/session |
| opentelemetry-sdk | 1.44.0 | Apache-2.0 | Trace SDK |
| psycopg / psycopg-binary | 3.3.4 | LGPL-3.0-only | Parameterized CockroachDB transactions and async SQLAlchemy driver |
| fastembed | 0.8.0 | Apache-2.0 per upstream repository; wheel classifier also contains `Other/Proprietary` | Local ONNX embeddings; recheck metadata and ship upstream LICENSE/NOTICE before publication |
| BAAI/bge-small-en-v1.5 | snapshot `52398278842ec682c6f32300af41344b1c0b0bb2` | MIT | 384-dimensional embeddings |

The probed environment contained LGPL-licensed Psycopg distributions and a `py-rust-stemmers` wheel with incomplete metadata (upstream states MIT). No AGPL distribution was found. Before Gate C, regenerate the complete recursive inventory from the final container image and include every required license/notice; this source-stage list is not a substitute for the final image audit.
