from ..assistant import Assistant
from ..settings import OPENAI_API_KEY, ASSISTANT_ID

assistant = Assistant(OPENAI_API_KEY, ASSISTANT_ID)

while True:
    try:
        prompt = input(">>> ")
        assistant.send_message(prompt)
        print(assistant.get_response())
    except Exception as e:
        print(e)
        break
    
