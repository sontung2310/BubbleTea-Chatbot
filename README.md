Built an AI agent for selling bubble tea using LangGraph, Gemini API, and Gradio interface
=======

You've probably heard a lot about AI Agents recently but aren't sure how to create one for your own application. Here’s an example of building an AI Agent using the Gemini API and LangGraph, as part of Kaggle’s 5-day Generative AI course (Day 3 – AI Agents).

I’ve also designed a user-friendly interface with Gradio. The project, ShinTea, is a simulated bubble tea ordering system that provides a looping chat interface, allowing customers to order bubble tea using natural language.

## Chatbot demo
![Alt text](Shintea/resources/demo_ShinTea.gif?raw=true "Chatbot demo")

## Key features of Chatbot
- Display the menu
- Consult with customers on choosing a suitable drink.
- Select size (S, M, L), ice level, sugar level, and toppings
- Add items to the order
- Remove items from the order
- Show the current order status


## How to run the Chatbot:
1. Install dependencies by running:
pip install -r requirements.txt
2. Open single_turn_bot.py and replace line 19 with your own GOOGLE_API_KEY. You can obtain a key [here](https://aistudio.google.com/app/apikey).
3. Start the chatbot by running:
python gradio_interface.py


