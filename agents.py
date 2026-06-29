from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url 
import os
from dotenv import load_dotenv

load_dotenv()
# model setup
llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0)
