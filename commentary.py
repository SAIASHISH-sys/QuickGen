import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        temperature=0.7,
        max_tokens=1000
    )

except Exception as e:
    llm = None
    prompt_template = None

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly commentary generator who gives <30 seconds of match summary based on the JSON file given to it as the human input. Keep your responses:
    - very short so that it is lesss than 30 seconds, technical and enthusiastic
    - Engaging and conversational 
    - Helpful and concise and very short"""),
    ("human", "{input}"),    
])

chain = prompt_template | llm


def get_langchain_response(message):
    try:
        # Get response from LangChain
        response = chain.invoke({"input": message})
        return response.content
        
    except Exception as e:
        return "Sorry, I'm having trouble processing your message right now. Please try again!"
    

