#Question Answering Transformer (QAT)
from allennlp.predictors.predictor import Predictor
import allennlp_models.rc
import textwrap
import random
from nltk.tokenize import sent_tokenize, word_tokenize
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
    sources = []
    for result in search(question, tld="com", num=4, stop=4, pause=2):
        information = """\
                      """
        html = requests.get(result)
        soup = BeautifulSoup(html.text, "html5lib")
        for txt in soup.find_all("p"):
            information += "\n"+str(txt.get_text())
        sources.append([information.strip(), result])
    try:
        source = random.choice(sources)
        passage = source[0]
        ans = ""
        prediction = predictor.predict(
                        passage=textwrap.dedent(passage),
                        question=question
                     )
        sentences = sent_tokenize(passage)
        for sent in sentences:
            if prediction["best_span_str"].strip() in sent:
                ans_toks = word_tokenize(sent)
                for tok in ans_toks:
                    ans += tok+" "
                candidate_answer = ans.strip() + f".Source: {source[1].strip()}."
        if not candidate_answer:
            candidate_answer = prediction["best_span_str"].strip() + f".Source: {source[1].strip()}."
            return candidate_answer
        else:
            return candidate_answer
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
print("Input a user_input.")
print("Ask a question or type \"/help\" for usage.")
cache = {}
while True:
    start = default_timer()
    user_input = input("User: ")
    if not user_input:
        print("Please input a question or type \"/help\" for usage.") 
    elif user_input.strip().lower().startswith("/feedback"):
        if not bool(cache):
            print("There is currently nothing saved in cache.")
        else:
            correction = user_input.replace("/feedback", "", 1).strip()
            if not correction:
                print("Please give a correction that you want to make.")
            else:
                print("The previous answer will be replaced with this correction.")
                cache[list(cache.keys())[-1]] = [correction, default_timer()]
    elif user_input.strip().lower().startswith("/help"):
        print(textwrap.dedent("""\
                              User Guide:
                              - Input a question and get the answer for it.
                              - /feedback [correction]: Make a correction to the previous answer if it is incorrect.
                              - /help: Get the user guide for QAT.
                              - /wiki [query]: (Additional Feature) Search the result for a query with Wikipedia.
                              - /wolfram [query]: (Additional Feature) Search the result for a query with Wolfram|Alpha.
                              - /exit: Exit the application."""))
    elif user_input.strip().lower().startswith("/wiki"):
        query = user_input.replace("/wiki", "", 1).strip()
        if not query:
            print("Please input a query.")
        else:
            result = wiki(query)
            if not result:
                print("There are no results available.")
            else:
                print(f"QAT: {result}")
    elif user_input.strip().lower().startswith("/wolfram"):
        query = user_input.replace("/wolfram", "", 1).strip()
        if not query:
            print("Please input a query.")
        else:
            result = wolfram(query)
            if not result:
                print("There are no results available.")
            else:
                print("QAT:")
                for pod in result.pods:
                    for subpod in pod.subpods:
                        print(subpod.plaintext)
    elif user_input.strip().lower().startswith("/exit"):
        print("Exitting...")
        sys.exit()
    else:
        question = user_input
        if not question:
            print("Please input a question.")
        else:
            print("Thinking....")
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
                print("There are no answers available.")
            else:
                print(f"QAT: {ans}")

