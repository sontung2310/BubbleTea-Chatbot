import gradio as gr
# from langgraph import StateGraph
from single_turn_bot import *

# Step 1: Define your LangGraph chatbot
# graph_with_order_tools = StateGraph(...)  # Your StateGraph definition here
initial_state = {"messages": []}  # Initial chatbot state

# auto_tools = [get_menu]
# tool_node = ToolNode(auto_tools)

# # Order-tools will be handled by the order node.
# order_tools = [add_to_order, confirm_order, get_order, clear_order, place_order]

# # The LLM needs to know about all of the tools, so specify everything here.
# llm_with_tools = llm.bind_tools(auto_tools + order_tools)

# Step 2: Function to interact with the chatbot
def chat_with_langgraph(user_message, chat_history, state):
    """
    Function to handle conversation between user and LangGraph chatbot.

    Args:
        user_message (str): User input message.
        chat_history (list): The list of tuples for chat history [(user, bot)].
        state (dict): LangGraph state object.

    Returns:
        Updated chat history and chatbot state.
    """
    # Append the user's message to the chatbot state
    # state["messages"].append({"role": "user", "content": user_message})
    # print("Chat history: ", chat_history)
    if len(chat_history)==0:
        print("First messsage")
        new_state = chatbot_reply(user_msg=user_message, first_message=True)
    else:
        new_state = chatbot_reply(user_msg=user_message, state=state)

    # new_state = graph_with_order_tools.invoke(state)
    # bot_message = new_state["messages"][-1]["content"]  # Get the latest bot response
    # new_state = state
    # Update chat history
    last_msg = new_state["messages"][-1]
    chat_history.append((user_message, last_msg.content))
    # print("Chat history: ", chat_history)
    return chat_history, new_state

# Step 3: Reset function
def reset_langgraph_chat():
    """
    Resets the LangGraph chatbot state and chat history.
    """
    return [], initial_state

# Step 4: Gradio UI setup
with gr.Blocks() as demo:
    gr.Markdown("## LangGraph Chatbot with Gradio")
    
    chatbot = gr.Chatbot(value=[(None, WELCOME_MSG)])
    user_input = gr.Textbox(label="Your Message", placeholder="Type your message here...", lines=1)
    send_button = gr.Button("Send")
    clear_button = gr.Button("Clear Chat")
    
    # Gradio State for preserving chatbot context
    chat_state = gr.State(initial_state)

    # Interaction logic
    send_button.click(chat_with_langgraph, [user_input, chatbot, chat_state], [chatbot, chat_state])
    send_button.click(lambda x: gr.update(value=""), None, [user_input], queue=False)
    user_input.submit(chat_with_langgraph, [user_input, chatbot, chat_state], [chatbot, chat_state])
    user_input.submit(lambda x: gr.update(value=""), None, [user_input], queue=False)
    clear_button.click(reset_langgraph_chat, [], [chatbot, chat_state])

    # Gradio Examples
    examples = gr.Examples(
        examples=["Can I have a look at the menu?", "What kind of Bubble Tea you have?"],
        inputs=user_input
    )

# Step 5: Launch the Gradio interface
demo.launch()
