# Step 02 - Conditional Node

Build a graph with a conditional edge that routes based on console input. Still no LLM calls.

## What We Build

- A node that reads input from the console.
- A routing function that picks the next node based on the input.
- Two possible follow-up nodes, only one of which runs per execution.

## Concepts

- A `conditional edge` routes execution to different nodes based on a function of the state.
- The `routing function` receives the current state and returns a key.
- `path_map` maps each possible key to a target node name.
- Only the matched branch runs; the other node is skipped entirely.

## Files

Save this as `conditional_node.py`:

```python
from typing import TypedDict

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

app = graph.compile()

if __name__ == "__main__":
    app.invoke({"name": ""})
```

## Run

```powershell
python conditional_node.py
```

Try it twice: once with a name, once with empty input. Inspect which branch printed each time.

## Navigation

- [Back to LangGraph README](../../README.md)
- [Previous step: 01 Hello World](../01-hello-world/01-hello-world.md)
- [Next step: 03 Streaming and Interrupts](../03-streaming-and-interrupts/03-streaming-and-interrupts.md)
