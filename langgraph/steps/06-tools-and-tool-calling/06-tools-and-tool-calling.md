# Step 06 - Tools and Tool Calling

Give Claude a custom tool it can call on its own when it needs your "nice number". The tool always returns `42`.

## What We Build

- A tool function `generate_my_number(a, b)`, registered as an in-process MCP server.
- A node that lets Claude decide whether to call the tool, based on the question.

## Concepts

- A `tool` is a function the model can choose to call mid-conversation. It has a name, a description, and an input schema - the model decides on its own whether and when to call it, based on the prompt.
- The Claude Agent SDK exposes custom tools through an in-process `MCP server` (`create_sdk_mcp_server`) - no separate process or network call needed.
- `allowed_tools` on `ClaudeAgentOptions` whitelists which tools the agent may use, named as `mcp__<server_name>__<tool_name>`.
- Calling the tool is the model's decision, not guaranteed: if the prompt doesn't need it, Claude just answers directly instead.
- The `@observe()` decorator manually creates a Langfuse span around a function, independent of LangChain - needed here because the tool call itself happens outside LangChain/LangGraph's view.
- The call and its result arrive as two separate messages: a `ToolUseBlock` (inside an `AssistantMessage`) requesting the call, and later a `ToolResultBlock` (inside a `UserMessage`) carrying what the tool returned. They're matched by `tool_use_id`.

## Files

Save this as `tools_and_tool_calling.py`:

```python
from typing import TypedDict

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    create_sdk_mcp_server,
    query,
    tool,
)
from langfuse import observe
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    question: str
    answer: str


@tool("generate_my_number", "Generates the user's nice number", {"a": int, "b": int})
async def generate_my_number(args: dict) -> dict:
    return {"content": [{"type": "text", "text": "42"}]}


server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[generate_my_number],
)

options = ClaudeAgentOptions(
    mcp_servers={"my": server},
    allowed_tools=["mcp__my__generate_my_number"],
)


@observe(name="tool_call")
def _log_tool_call(name: str, input: dict, result) -> object:
    print(f"[tool call] {name}({input}) -> {result}")
    return result


@observe()
async def _ask_claude(question: str) -> str:
    answer = ""
    pending_calls: dict[str, tuple[str, dict]] = {}

    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    answer += block.text
                elif isinstance(block, ToolUseBlock):
                    pending_calls[block.id] = (block.name, block.input)
        elif isinstance(message, UserMessage):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    name, input = pending_calls.pop(block.tool_use_id, ("unknown", {}))
                    _log_tool_call(name, input, block.content)
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
        {"question": "What is my nice number?"},
        config={"callbacks": [langfuse_handler]},
    )
    print(result["answer"])
```

## Run

```powershell
python tools_and_tool_calling.py
```

You should see a `[tool call] generate_my_number(...) -> ...` line printed before the final answer, and the answer should mention `42`.

## Additional Notes

### Why the tool call wasn't visible in Langfuse

`langfuse_handler` (the `CallbackHandler`) only instruments LangChain/LangGraph-native steps. It sees the `ask_claude` node as a single step in the graph, but has no visibility into what happens inside it - the Claude Agent SDK runs the `claude` CLI as a subprocess and handles the tool call entirely on its own, outside of LangChain's callback system.

`@observe()` fixes this by creating a span manually, attached to the currently active trace (the one the callback handler already started for this `invoke()` call), regardless of whether the code underneath is LangChain-native. Here it wraps the whole `_ask_claude` call, so the SDK's work - including the tool call - now shows up nested under the node's span in the Langfuse UI.

That single span shows the whole `_ask_claude` call, but not the tool call itself with its name, parameters, and result. `_log_tool_call` is a second `@observe()`-decorated function, called from the same call stack as `_ask_claude`, so it nests as its own child span underneath it - with name and input captured automatically as the span's input, and the returned `result` as the span's output.

The call (`ToolUseBlock`) and its result (`ToolResultBlock`) don't arrive together - the result only shows up in a later message, once the in-process MCP server has actually run the tool. `pending_calls` bridges that gap so both halves end up in one span instead of two unrelated ones.

Note: depending on the installed `langfuse` version, the exact span/context APIs can differ - if `@observe()` behaves differently, check `pip show langfuse` and that package's current docs.

## Navigation

- [Back to LangGraph README](../../README.md)
- [Previous step: 05 First LLM Node](../05-first-llm-node/05-first-llm-node.md)
