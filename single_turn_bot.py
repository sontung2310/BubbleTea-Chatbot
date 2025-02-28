from langgraph.graph import StateGraph, START, END
from langchain_core.messages.ai import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated
from typing_extensions import TypedDict, List
from collections.abc import Iterable
from random import randint
from langgraph.prebuilt import InjectedState
from langchain_core.messages.tool import ToolMessage
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display
from langgraph.graph.message import add_messages
from pprint import pprint
from langchain_core.tools import tool
from typing import Literal

# Init LLM
import os
os.environ['GOOGLE_API_KEY'] = 'ENTER_YOUR_GOOGLE_API_KEY'



llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

class OrderDetails(TypedDict):
    """TypedDict for storing order details."""
    item: List[str]      # Stores the name of the item (list of strings)
    iced: List[str]      # Stores the modifiers for iced (e.g., "50%")
    sugar: List[str]     # Stores the modifiers for sugar (e.g., "50%")
    topping: List[str]   # Stores the modifiers for toppings (e.g., "Coconut Jelly")
    size: List[str]      # Stores the modifiers for size (e.g., "Large")
    quantity: List[int]  # Stores the quantity (list of integers)


class OrderState(TypedDict):
    """State representing the customer's order conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    # The customer's in-progress order.
    # order: list[str]
    order: OrderDetails

    # Flag indicating that the order is placed and completed.
    finished: bool


# System prompt
BARISTABOT_SYSINT = (
    "system",  # 'system' indicates the message is a system instruction.
    "You are a ShinTea-Bot, an interactive tea ordering system. A human will talk to you about the "
    "available products you have and you will answer any questions about menu items (and only about "
    "menu items - no off-topic discussion, but you can chat about the products and their history). "
    "The customer will place an order for 1 or more items from the menu, which you will structure "
    "and send to the ordering system after confirming the order with the human. "
    "\n\n"
    "Use get_menu when the customer asks about the MENU. "
    "Add items to the customer's order with add_to_order, and reset the order with clear_order. "
    "To see the contents of the order so far, call get_order (this is shown to you, not the user) "
    "Always confirm_order with the user (double-check) before calling place_order. Calling confirm_order will "
    "display the order items to the user and returns their response to seeing the list. Their response may contain modifications about ice, sugar and adding topping. "
    "When receive a drink, ask about amount of sugar, iced, added topping and size (S,M,L)."
    "Always verify and respond with drink and amount of sugar, amount of iced, added topping, quantity and size before adding them to the order. "
    "If you are unsure a drink or modifier matches those on the MENU, ask a question to clarify or redirect. "
    "You only have the modifiers listed on the menu. "
    "Once the customer has finished ordering items, ask them if they want anything else. If no, Call confirm_order to ensure it is correct then make "
    "any necessary updates and then call place_order. Once place_order has returned, thank the user and "
    "say goodbye!",
)



"""
Function:
- add_to_order:  Add items to the customer's order
- clear_order: Reset the order
- get_order: See the contents of the order so far
- confirm_order: double-check -> accept the modifications
- place_order: finish the order
"""

# This is the message with which the system opens the conversation.
WELCOME_MSG = "Welcome to the ShinTea-Bot. How may I serve you today?"



@tool
def get_menu() -> str:
    """Provide the latest up-to-date menu. use this tool when custumer ask about the menu"""
    # Note that this is just hard-coded text, but you could connect this to a live stock
    # database, or you could use Gemini's multi-modal capabilities and take live photos of
    # your cafe's chalk menu or the products on the counter and assmble them into an input.
    print("GET MENU")
    return """
    MENU:
    - Milk Tea
    + Black Milk Tea
    + Oat Milk Tea
    + Black Milk Tea with Cream Cheese Foam
    + Caramel Creme Cheese Foam Milk Tea
    + Brown Sugar Latte with Pearls
    + Chocolate Mocha Milk Tea
    + Caramel Coffee Milk Tea
    - Matcha
    + Red Bean Matcha Smoothie
    + Shizuoka Matcha Latte with Panna Cotta
    - Cream Cheese Foam
    + Oolong Tea Cream Cheese Foam
    + Jasmine Green Tea Cream Cheese Foam
    - Fruit Tea
    + Jasmine Green Tea
    + Plum Green Tea
    + Passionfruit Green Tea
    + Lychee Green Tea
    + Grapefruit Green Tea Slush
    + Mango Smoothie
    - Toppings
    + Pearls
    + Katen Jelly
    + Coconut Jelly
    + Mini Taro Balls
    - Modify: Sugar (Less, Half, Regular), Ice (Less, Half, Regular, Extra), Size (S, M, L)

  """


# These functions have no body; LangGraph does not allow @tools to update
# the conversation state, so you will implement a separate node to handle
# state updates. Using @tools is still very convenient for defining the tool
# schema, so empty functions have been defined that will be bound to the LLM
# but their implementation is deferred to the order_node.


@tool
def add_to_order(drink: str, ice: Iterable[str], sugar: Iterable[str], topping: Iterable[str], size: Iterable[str], quantity: Iterable[int]) -> str:
    """Adds the specified drink to the customer's order, including any information about amount of ice, amount of sugar, adding topping, size and quantity.

    Returns:
      The updated order in progress.
    """


@tool
def confirm_order() -> str:
    """Asks the customer if the order is correct.

    Returns:
      The user's free-text response.
    """


@tool
def get_order() -> str:
    """Returns the users order so far. One item per line."""


@tool
def clear_order():
    """Removes all items from the user's order."""


@tool
def place_order() -> int:
    """Sends the order to the barista for fulfillment.

    Returns:
      The estimated number of minutes until the order is ready.
    """

def convert_order_to_text(order):
    description = []
    for i in range(len(order["item"])):
        item = order["item"][i]
        size = order["size"][i]
        quantity = order["quantity"][i]
        iced = order["iced"][i] if i < len(order["iced"]) else "no iced"
        sugar = order["sugar"][i] if i < len(order["sugar"]) else "no sugar"
        topping = order["topping"][i] if i < len(order["topping"]) else "no topping"
        

        # Format the description
        description.append(f"{quantity} {item} size {size} with {iced}, {sugar}, and {topping}")
        print(description)

    return description

def order_node(state: OrderState) -> OrderState:
    """The ordering node. This is where the order state is manipulated."""
    tool_msg = state.get("messages", [])[-1]
    order = state.get("order", {"item": [], "iced": [], "sugar": [], "topping": [], "quantity": [], "size": []})
    if not isinstance(order, dict):
        # If `order` is not a dict, reinitialize it
        order = {"item": [], "iced": [], "sugar": [], "topping": [], "quantity": [], "size": []}


    print("Check 1 ",type(order))
    print("Check 2 ",order)
    outbound_msgs = []
    order_placed = False

    for tool_call in tool_msg.tool_calls:
        print("Which tool is using: ", tool_call)
        if tool_call["name"] == "add_to_order":

            # Each order item is just a string. This is where it assembled as "drink (modifiers, ...)".
            # modifiers = tool_call["args"]["modifiers"]
            print("Hehe: ", tool_call["args"])
            # order: dict = {
            #     "item": list[str],        # Stores the name of the item (str)
            #     "iced": list[str],     # Stores the list of modifiers amount of iced (list of str). 50%, 20% for example
            #     "sugar": list[str],     # Stores the list of modifiers amount of sugar (list of str). 50%, 20% for example
            #     "topping": list[str],     # Stores the list of modifiers about adding topping (list of str).
            #     "quantity": list[int]       # Stores the quantity (int)
            # }
            # Adding args to order
            order["item"].append(tool_call["args"].get("drink", ""))
            order["iced"].extend(tool_call["args"].get("ice", []))
            order["sugar"].extend(tool_call["args"].get("sugar", []))
            order["topping"].extend(tool_call["args"].get("topping", []))
            order["size"].extend(tool_call["args"].get("size", []))
            order["quantity"].extend(map(int, tool_call["args"].get("quantity", [])))  # Convert quantity to integers

            # Print the updated order dictionary
            print(order)
            # modifier_str = ", ".join(modifiers) if modifiers else "no modifiers"

            # print("Modify str: ", modifier_str)
            # order.append(f'{tool_call["args"]["drink"]} ({modifier_str})')
            # print("After modify: ", order)
            # response = "\n".join(order)
            
            description = convert_order_to_text(order)
            response = "\n".join(description)

        elif tool_call["name"] == "confirm_order":

            # We could entrust the LLM to do order confirmation, but it is a good practice to
            # show the user the exact data that comprises their order so that what they confirm
            # precisely matches the order that goes to the kitchen - avoiding hallucination
            # or reality skew.

            # In a real scenario, this is where you would connect your POS screen to show the
            # order to the user.

            print("Your order:")
            if not order:
                print("  (no items)")

            description = convert_order_to_text(order)

            for drink in description:
                print(f"  {drink}")

            response = input("Is this correct? ")

        elif tool_call["name"] == "get_order":

            response = "\n".join(convert_order_to_text(order)) if order else "(no order)"

        elif tool_call["name"] == "clear_order":

            order.clear()
            response = None

        elif tool_call["name"] == "place_order":

            order_text = "\n".join(convert_order_to_text(order))
            print("Sending order to kitchen!")
            print(order_text)

            # TODO(you!): Implement cafe.
            order_placed = True
            response = randint(1, 5)  # ETA in minutes

        else:
            raise NotImplementedError(f'Unknown tool call: {tool_call["name"]}')

        # Record the tool results as tool messages.
        outbound_msgs.append(
            ToolMessage(
                content=response,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": outbound_msgs, "order": order, "finished": order_placed}

   
def human_node(state: OrderState) -> OrderState:
    """Display the last model message to the user, and receive the user's input."""
    last_msg = state["messages"][-1]
    state["finished"] = True
    print("Model:", last_msg.content)
    return state

    # user_input = input("User: ")

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    # if user_input in {"q", "quit", "exit", "goodbye"}:
    #     state["finished"] = True

    # print("State after user input: ", state | {"messages": [("user", user_input)]})
    # return state | {"messages": [("user", user_input)]}

def maybe_route_to_tools(state: OrderState) -> str:
    """Route between chat and tool nodes if a tool call is made."""
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    msg = msgs[-1]

    # print("Test1",msg)
    # print("Test2",state)
    # print("Test3",hasattr(msg, "tool_calls"))
    # print("Test4",len(msg.tool_calls))

    # if state.get("finished", False):
    #     # When an order is placed, exit the app. The system instruction indicates
    #     # that the chatbot should say thanks and goodbye at this point, so we can exit
    #     # cleanly.
    #     return END

    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        # Route to `tools` node for any automated tool calls first.
        if any(
            tool["name"] in tool_node.tools_by_name.keys() for tool in msg.tool_calls
        ):
            print("Using Tools")
            return "tools"
        else:
            print("Using Ordering")

            return "ordering"

    else:
        print("Using Human")
        return "human"

    
def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Route to the chatbot, unless it looks like the user is exiting."""
    if state.get("finished", False):
        return END
    else:
        return "chatbot"


def chatbot(state: OrderState) -> OrderState:
    """The chatbot itself. A simple wrapper around the model's own chat interface."""
    message_history = [BARISTABOT_SYSINT] + state["messages"]
    return {"messages": [llm.invoke(message_history)]}

def chatbot_with_tools(state: OrderState) -> OrderState:
    """The chatbot with tools. A simple wrapper around the model's own chat interface."""
    defaults = {"order": [], "finished": False}
    message_history = [BARISTABOT_SYSINT] + state["messages"]
    # print("State message: ",state["messages"])
    return {"messages": [llm_with_tools.invoke(message_history)]}


def chatbot_reply(user_msg, first_message=False, state=None):
    
    # Set up the initial graph based on our state definition.
    graph_builder = StateGraph(OrderState)

    # Add the chatbot function to the app graph as a node called "chatbot".
    # graph_builder.add_node("chatbot", chatbot)

    graph_builder.add_node("chatbot", chatbot_with_tools) # Chatbot node which have switch tools ability
    graph_builder.add_node("human", human_node) # User input node
    graph_builder.add_node("tools", tool_node) # Auto-tools node - Looking to the menu
    graph_builder.add_node("ordering", order_node) # The ordering node. This is where the order state is manipulated.

    # Define the chatbot node as the app entrypoint.
    graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
    # graph_builder.add_conditional_edges("human", maybe_exit_human_node)

    # Tools (both kinds) always route back to chat afterwards.
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("ordering", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    chat_graph = graph_builder.compile()

    # user_msg = "Hello, what can you do?"
    if first_message:
        state = chat_graph.invoke({"messages": [user_msg]})
    else:
        state["messages"].append(user_msg)
        state = chat_graph.invoke(state)
    # The state object contains lots of information. Uncomment the pprint lines to see it all.
    # pprint(state)

    # Note that the final state now has 2 messages. Our HumanMessage, and an additional AIMessage.
    for msg in state["messages"]:
        print(f"{type(msg).__name__}: {msg.content}")
    
    return state

auto_tools = [get_menu]
tool_node = ToolNode(auto_tools)

# Order-tools will be handled by the order node.
order_tools = [add_to_order, confirm_order, get_order, clear_order, place_order]

# The LLM needs to know about all of the tools, so specify everything here.
llm_with_tools = llm.bind_tools(auto_tools + order_tools)

if __name__ == "__main__":
    user_msg = "Hello, what can you do?"
    # Auto-tools will be invoked automatically by the ToolNode

    state = chatbot_reply(user_msg=user_msg)
    print("State: ",state)
