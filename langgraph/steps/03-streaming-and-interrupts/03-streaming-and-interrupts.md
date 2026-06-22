# Step 03 - Streaming and Interrupts

Inspect graph execution as it happens and pause it mid-run. Still no LLM calls.

## What We Build

- Reuse the conditional graph from Step 02.
- Stream node updates as they happen instead of waiting for the final result.
- Pause execution before a node runs, then resume it.

## Concepts

- `stream()` runs the graph and yields output incrementally, instead of waiting for the final state like `invoke()` does.
- `stream_mode="updates"` yields only what changed after each node, as `{node_name: update}`.
- `interrupt_before` (and its counterpart `interrupt_after`) pauses execution right before (or after) the listed nodes run.
- Pausing and resuming requires a `checkpointer` (here `MemorySaver`) so LangGraph can remember where execution stopped.
- A `thread_id` inside `config` identifies which paused run to resume.
- When a node returns a partial dict, only those keys are merged into `State` (default is a shallow overwrite) - the rest of `State` is left untouched.

## Additional Notes

`stream_mode` has more options than `"updates"`:

- `"values"` (default) - yields the full `State` after every node, not just what changed.
- `"updates"` (used here) - yields only what the node returned, as `{node_name: update}`.
- `"debug"` - most verbose, includes internal step/timing events.
- `"messages"` - streams LLM tokens as they're generated (relevant once a node calls an LLM).
- `"custom"` - a node can push arbitrary custom data via `get_stream_writer()`.

For comparison, `invoke()` does not stream at all - it waits for the whole graph to finish and returns the final `State` once.

### Why not just use `input()` or a conditional node for human-in-the-loop?

- A conditional node only branches on data already in `State` - it never waits for anything new.
- A node using `input()` blocks the whole process until someone types something - fine for a console script, unusable for a web server handling many users at once.
- `interrupt_before`/`interrupt_after` actually **stops and exits the graph run**. The state is saved by the `checkpointer`, so the app/server is free to do anything else (even restart). Whoever approves later (a person, a webhook, another service) just calls `invoke(None, config)` with the same `thread_id`, and execution continues exactly where it stopped. No thread sits there waiting.

### What about a node that itself takes an hour to run (e.g. a long calculation)?

`interrupt` does not help here - it only pauses *between* nodes, not *during* one. While a node's own function is running, it occupies a worker/thread for as long as that function takes, same as any normal Python call.

This is solved outside of LangGraph itself:

- Run the graph in a background worker (e.g. a Celery/RQ job, or a separate process), not inside a web request - so the long node only blocks that one worker, not the whole server.
- For really long external work, the node usually does not wait synchronously at all: it kicks off the job (submits to an external system) and the graph then pauses (e.g. via `interrupt_after`, or simply ends the run) until a webhook/callback resumes it with the result - the same pattern as human approval, just with a system as the "approver" instead of a person.

## Files

Save this as `streaming_and_interrupts.py`:

```python
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    name: str


def ask_name(state: State) -> State:
    name = input("Enter your name (empty for none): ")
    return {"name": name}


def greet_known(state: State) -> State:
    print(f"Hello, {state['name']}!")
    return state


def greet_unknown(state: State) -> State:
    print("Hello, stranger!")
    return state


def route(state: State) -> str:
    if state["name"].strip():
        return "known"
    return "unknown"


graph = StateGraph(State)
graph.add_node("ask_name", ask_name)
graph.add_node("greet_known", greet_known)
graph.add_node("greet_unknown", greet_unknown)

graph.add_edge(START, "ask_name")
graph.add_conditional_edges(
    "ask_name",
    route,
    path_map={"known": "greet_known", "unknown": "greet_unknown"},
)
graph.add_edge("greet_known", END)
graph.add_edge("greet_unknown", END)

app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["greet_known", "greet_unknown"],
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo"}}

    print("--- first run, stops before greeting ---")
    for update in app.stream({"name": ""}, config, stream_mode="updates"):
        print(update)

    input("paused before greeting, press enter to resume...")

    print("--- resumed run ---")
    for update in app.stream(None, config, stream_mode="updates"):
        print(update)
```

## Run

```powershell
python streaming_and_interrupts.py
```

Type a name (or leave it empty), watch the `updates` printed after `ask_name`, then press Enter to resume and see the greeting node run.

## Navigation

- [Back to LangGraph README](../../README.md)
- [Previous step: 02 Conditional Node](../02-conditional-node/02-conditional-node.md)
- [Next step: 04 Langfuse Tracing](../04-langfuse-tracing/04-langfuse-tracing.md)
