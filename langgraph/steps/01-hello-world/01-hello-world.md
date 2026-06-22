# Step 01 - Hello World

Build the first LangGraph graph using plain Python functions, no LLM calls.

## What We Build

- A `State` type with one field.
- One node function that updates the state.
- A compiled graph with a single node.
- A manual run from the command line.

## Concepts

- LangGraph models a workflow as a graph of `nodes` connected by `edges`.
- `State` is a shared data structure passed between nodes.
- A `node` is a function that receives the state and returns updates to it.
- An `edge` connects two nodes and defines which node runs next.
- `START` and `END` are special markers for the graph entry and exit points.
- `compile()` turns the graph definition into a runnable application.

## Install

```powershell
pip install langgraph
```

## Files

Save this as `hello_langgraph.py`:

```python
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    message: str


def say_hello(state: State) -> State:
    print(f"Hello from {state["message"]}")
    return {"message": state["message"]}


graph = StateGraph(State)
graph.add_node("say_hello", say_hello)
graph.add_edge(START, "say_hello")
graph.add_edge("say_hello", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"message": "abc"})
    print(result)
```

## Run

```powershell
python hello_langgraph.py
```

Expected output:

```text
Hello from LangGraph
{'message': 'Hello from LangGraph'}
```

## Navigation

- [Back to LangGraph README](../../README.md)
- [Next step: 02 Conditional Node](../02-conditional-node/02-conditional-node.md)
