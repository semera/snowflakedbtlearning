# Step 04 - Tracing with Langfuse

Send every node run to Langfuse so the execution can be inspected in a UI after the fact. Still no LLM calls.

## What We Build

- Reuse the graph from Step 02/03.
- Attach a Langfuse `callback handler` to the run.
- View the resulting trace (each node, its input/output, timing) in the Langfuse UI.

## Concepts

- Langfuse is an observability platform: unlike `stream()`, it does not show you anything live in your own process - it logs structured trace data so you can inspect a run later in a separate UI.
- A `callback handler` hooks into each step of a run and reports it, without changing the graph itself.
- Credentials (`LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST`) are read from environment variables, never hardcoded in committed files - put them in a local `.env` (already in `.gitignore`).
- SDK note: Langfuse `v3` moved the LangChain/LangGraph integration to `langfuse.langchain.CallbackHandler` (the older `langfuse.callback.CallbackHandler` was the `v2` location). Check `pip show langfuse` if the import fails.

## Files

`.env` (not committed):

```text
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

Save this as `langfuse_tracing.py`:

```python
from typing import TypedDict

from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    name: str


def ask_name(state: State) -> State:
    name = input("Enter your name (empty for none): ")
    return {"name": name}


def greet(state: State) -> State:
    print(f"Hello, {state['name'] or 'stranger'}!")
    return state


graph = StateGraph(State)
graph.add_node("ask_name", ask_name)
graph.add_node("greet", greet)
graph.add_edge(START, "ask_name")
graph.add_edge("ask_name", "greet")
graph.add_edge("greet", END)

app = graph.compile()

langfuse_handler = CallbackHandler()

if __name__ == "__main__":
    app.invoke({"name": ""}, config={"callbacks": [langfuse_handler]})
```

## Run

```powershell
pip install langfuse
pip install langchain
python langfuse_tracing.py
```

Then open your Langfuse UI (`LANGFUSE_HOST`) and check the new trace - you should see `ask_name` and `greet` as separate steps.

## Additional Notes

### Combining this with Step 03 (streaming and interrupts)

Passing the same `langfuse_handler` in `config["callbacks"]` works for `stream()` and `interrupt_before` too, but two things are easy to miss:

- **Data shows up late.** Langfuse buffers spans and sends them in the background, not instantly - so a paused run (waiting on `input()` before resuming) won't appear in the UI until the buffer is sent. Force it immediately with:

  ```python
  from langfuse import get_client

  for update in app.stream({"name": ""}, config, stream_mode="updates"):
      print(update)

  get_client().flush()
  input("paused before greeting, press enter to resume...")
  ```

- **One `stream()` call = one trace.** Pausing on `interrupt_before` does not keep a single trace "open" while you wait - the first `stream()` call closes its own trace, and the resumed `stream()` call starts a new one. If you want them visually linked in the UI, pass the same `session_id` in both calls' config metadata; they'll still show as two separate traces, just grouped together.

## Navigation

- [Back to LangGraph README](../../README.md)
- [Previous step: 03 Streaming and Interrupts](../03-streaming-and-interrupts/03-streaming-and-interrupts.md)
- [Next step: 05 First LLM Node](../05-first-llm-node/05-first-llm-node.md)
