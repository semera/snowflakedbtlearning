# Step 05 - First LLM Node (Claude Agent SDK)

Replace a plain Python node with one that asks Claude for an answer. Uses the Claude Agent SDK, not a raw API key.

## What We Build

- A node that sends a question to Claude and waits for the full answer.
- A minimal one-node graph, run with `invoke()`.

## Concepts

- The Claude Agent SDK runs the `claude` CLI as a subprocess - it reuses whatever auth your CLI already has (`claude login`), no `ANTHROPIC_API_KEY` needed.
- `query()` is an async generator: it yields a stream of message objects as Claude responds, not a single return value.
- An `AssistantMessage` containing `TextBlock` parts is where Claude's actual reply text lives; other message types (tool calls, results) are ignored for now.
- The SDK is async-only. Since our node is a plain sync function, `anyio.run()` runs the async call to completion and blocks until it's done - similar in spirit to `invoke()`.
- From this step on, every example assumes Langfuse is already configured (Step 04) and passes the `langfuse_handler` callback by default.

## Files

Save this as `first_llm_node.py`:

```python
from typing import TypedDict

import anyio
from claude_agent_sdk import AssistantMessage, TextBlock, query
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    question: str
    answer: str


async def _ask_claude(question: str) -> str:
    answer = ""
    async for message in query(prompt=question):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    answer += block.text
    return answer


def ask_claude(state: State) -> State:
    answer = anyio.run(_ask_claude, state["question"])
    return {"answer": answer}


graph = StateGraph(State)
graph.add_node("ask_claude", ask_claude)
graph.add_edge(START, "ask_claude")
graph.add_edge("ask_claude", END)

app = graph.compile()

langfuse_handler = CallbackHandler()

if __name__ == "__main__":
    result = app.invoke(
        {"question": "What is LangGraph, in one sentence?"},
        config={"callbacks": [langfuse_handler]},
    )
    print(result["answer"])
```

## Run

```powershell
pip install claude-agent-sdk anyio
python first_llm_node.py
```

## Navigation

- [Back to LangGraph README](../../README.md)
- [Previous step: 04 Langfuse Tracing](../04-langfuse-tracing/04-langfuse-tracing.md)
- [Next step: 06 Tools and Tool Calling](../06-tools-and-tool-calling/06-tools-and-tool-calling.md)
