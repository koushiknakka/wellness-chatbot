from typing import Annotated
from dotenv import load_dotenv
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import os
from langchain.chat_models import init_chat_model

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = init_chat_model("google_genai:gemini-2.0-flash")

MENTAL_WELLNESS_SYSTEM_PROMPT = (
    "You are a supportive and empathetic mental wellness assistant for college students. "
    "Listen carefully, offer encouragement, practical self-care tips, and suggest campus resources. "
    "If a student seems in crisis, gently encourage them to reach out to a counselor or trusted adult. "
    "Never give medical advice or diagnose. Always be kind, non-judgmental, and supportive."
    "try to ask and know his goals and try to inspire him with that goals"
    "try to answer in 10-15 words, only in rare cases make it 20-25 words but not more than that"
    
)

def chatbot(state: State):
    # Insert the system prompt as the first message
    messages = [{"role": "system", "content": MENTAL_WELLNESS_SYSTEM_PROMPT}] + state["messages"]
    return {"messages": [llm.invoke(messages)]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

##VISUALIZING GRAPH
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass


def stream_graph_updates(user_input: str):
    # Crisis keyword check (very basic)
    crisis_keywords = ["suicide", "self-harm", "kill myself", "end my life", "can't go on"]
    if any(kw in user_input.lower() for kw in crisis_keywords):
        print("Assistant: I'm really sorry you're feeling this way. Please consider reaching out to a mental health professional, counselor, or someone you trust. You're not alone, and there are people who care about you.")
        return
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)



if __name__ == "__main__":
    print("Welcome! I'm your mental wellness assistant. How can I support you today? (Type 'quit' to exit)")

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye! Take care of yourself.")
                break
            stream_graph_updates(user_input)
        except:
            # fallback if input() is not available
            user_input = "I'm feeling stressed about my college life."
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break

def get_wellness_response(user_input: str) -> str:
    crisis_keywords = ["suicide", "self-harm", "kill myself", "end my life", "can't go on"]
    if any(kw in user_input.lower() for kw in crisis_keywords):
        return ("I'm really sorry you're feeling this way. Please consider reaching out to a mental health professional, counselor, or someone you trust. You're not alone, and there are people who care about you.")
    response = ""
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            response = value["messages"][-1].content
    return response