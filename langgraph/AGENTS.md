# LangGraph Guide Instructions

These rules apply inside the `langgraph/` guide.

## Project Direction

- This is a learning guide for LangGraph.
- Start with plain graph mechanics (State, Node, Edge), no LLM calls.
- Do not add an LLM provider or SDK until the user asks for it.
- Explain LangGraph concepts only when they are first used.
- From Step 05 onward, assume Langfuse is already configured (per Step 04) and wire the `langfuse_handler` callback into every example's `invoke`/`stream` call by default - do not re-explain the Langfuse setup itself.
