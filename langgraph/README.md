# LangGraph Learning

Small learning guide for LangGraph.

The guide starts with plain graph mechanics. LLM calls are not used in the first steps.

## Goals

- Learn LangGraph concepts step by step.
- Start with plain Python nodes, no LLM calls.
- Add an LLM node only after the basics are clear.
- Keep examples simple and practical.

## Structure

- `steps/` - LangGraph learning steps.
- [steps/01-hello-world/](steps/01-hello-world/01-hello-world.md) - first StateGraph with state, nodes, and edges.
- [steps/02-conditional-node/](steps/02-conditional-node/02-conditional-node.md) - conditional edge that routes based on console input.
- [steps/03-streaming-and-interrupts/](steps/03-streaming-and-interrupts/03-streaming-and-interrupts.md) - `stream()`, `stream_mode="updates"`, and pausing/resuming with `interrupt_before`.
- [steps/04-langfuse-tracing/](steps/04-langfuse-tracing/04-langfuse-tracing.md) - sending node runs to Langfuse for tracing.
- [steps/05-first-llm-node/](steps/05-first-llm-node/05-first-llm-node.md) - first node backed by an LLM, using the Claude Agent SDK.
- [steps/06-tools-and-tool-calling/](steps/06-tools-and-tool-calling/06-tools-and-tool-calling.md) - a custom tool the agent can call dynamically.

## TODO

- Step 07 - Persistence and checkpoints (`get_state()`, `get_state_history()`).
