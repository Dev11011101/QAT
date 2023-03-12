#Question Answering Transformer (QAT)
from allennlp.predictors.predictor import Predictor
import allennlp_models.rc
import textwrap
import random
from googlesearch import search
import requests, html5lib
from bs4 import BeautifulSoup
import wikipediaapi
import wolframalpha
from timeit import default_timer
import sys

predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/transformer-qa.2021-02-11.tar.gz")
wikipedia = wikipediaapi.Wikipedia("en")
wolframalpha_client = wolframalpha.Client("67PEAP-WG9HRK2966")

def answer(question):
    information = """\
                  """
    source = ""
    for result in search(question, tld="com", num=1, stop=1, pause=2):        
        html = requests.get(result)
        soup = BeautifulSoup(html.text, "html5lib")
        for txt in soup.find_all("p"):
            information += "\n"+str(txt.get_text().strip())
        source += result.strip()
    information = information.strip()
    source = source.strip()
    try:        
        prediction = predictor.predict(
                        passage=textwrap.dedent(information),
                        question=question
                     )
        paragraphs = information.split("\n")
        for paragraph in paragraphs:
            if prediction["best_span_str"] in paragraph:
                tokens = paragraph.split()                
                ans = " ".join(tokens) + f" Source: {source}."               
        if not ans.strip():
            ans = prediction["best_span_str"] + f". Source: {source}."
            if not ans.strip():
                return ""
            else:
                return ans
        else:
            return ans
    except:
        return ""
  
def wiki(query):
    page = wikipedia.page(query)
    result = page.summary
    return result 

def wolfram(query):
    result = wolframalpha_client.query(query)
    return result

print("Question Answering Transformer (QAT)")
print("Ask a question or type \"/help\" for usage.")
print("Note: This application is not a chatbot and it can only answer academic questions about science or other fields of knowledge. Please don't try to have a conversation with it!")
cache = {}
while True:
    start = default_timer()
    user_input = input("User: ")
    if not user_input.strip():
        print("QAT: Please input a question or a command. Type \"/help\" for usage.")
    elif user_input.strip().lower().startswith("/help"):
        print(textwrap.dedent("""\
                              User Guide:
                              - Input a question and get the answer for it.
                              - Commands:
                                  + /help: Get the user guide for QAT.                                 
                                  + /feedback [correction]: Make a correction to the answer for the previous question if it is incorrect.
                                  + /clearcache: Clear all the saved data in cache memory (answers for user's questions)
                                  + /wiki [query]: (Additional Feature) Search the result for a query with Wikipedia.
                                  + /wolfram [query]: (Additional Feature) Search the result for a query with Wolfram|Alpha.
                                  + /info: Get information about this application. 
                                  + /exit: Exit the application.
                                  - Note: This application is not a chatbot and it can only answer academic questions about science or other fields of knowledge. Please don't try to have a conversation with it!"""))
    elif user_input.strip().lower().startswith("/feedback"):
        if not bool(cache):
            print("QAT: There is currently nothing saved in cache memory.")
        else:
            correction = user_input.replace("/feedback", "", 1).strip()
            if not correction.strip():
                print("QAT: Please give a correction that you want to make.")
            else:
                cache[list(cache.keys())[-1]] = [correction, default_timer()]
                print("QAT: The answer for the previous question has been corrected.")
    elif user_input.strip().lower().startswith("/clearcache"):
        cache.clear()
        print("All the saved data in cache memory has been deleted.")
    elif user_input.strip().lower().startswith("/wiki"):
        query = user_input.replace("/wiki", "", 1).strip()
        if not query.strip():
            print("QAT: Please input a query.")
        else:
            result = wiki(query)
            if not result.strip():
                print("QAT: There are no results available.")
            else:
                print(f"QAT: {result}")
    elif user_input.strip().lower().startswith("/wolfram"):
        query = user_input.replace("/wolfram", "", 1).strip()
        if not query.strip():
            print("QAT: Please input a query.")
        else:
            result = wolfram(query)
            if not result.strip():
                print("QAT: There are no results available.")
            else:
                print("QAT:")
                for pod in result.pods:
                    for subpod in pod.subpods:
                        print(subpod.plaintext)
    elif user_input.strip().lower().startswith("/info"):
        print(textwrap.dedent("""\
                              Question Answering Transformer (QAT)
                              Developer: Nguyễn Hải Cường
                              Language: English                              
                              Model: Transformer-QA
                              Powered by Python, AllenNLP and Google Search
                              This application is still in research and development."""))                                                              
    elif user_input.strip().lower().startswith("/exit"):
        print("Exitting QAT...")
        sys.exit()
    else:
        question = user_input                
        print("QAT: Searching for answer...")
        if question.strip().lower() in cache.keys():
            if (default_timer() - cache[question.strip().lower()][1]) <= 3600:
                ans = cache[question.strip().lower()][0]
                cache[question.strip().lower()] = cache.pop(question.strip().lower())
            else:
                ans = answer(question)
                cache[question.strip().lower()] = [ans, default_timer()]
        else:
            ans = answer(question)
            cache[question.strip().lower()] = [ans, default_timer()]
        if not ans:
            print("QAT: There are no answers available.")
        else:
            print(f"QAT: {ans}")
