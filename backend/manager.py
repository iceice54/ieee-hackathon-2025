import chromadb
import json
import re
import os
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=google_api_key)

client = chromadb.PersistentClient(path="../chroma")
collection = client.get_collection(name="knowledge_base")
embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key)

def query_chromadb(query_text, n_results=7):
    query_embedding = embedding_model.embed_query(query_text)
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

    output = []
    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "document": doc,
        })

    return output

def cleaner(response):
    return re.search(r"\{.*\}", response, re.DOTALL).group(0)

class Manager:
    def __init__(self):
        self.retrieval = Retriever()
        self.decomposer = Decomposer()
        self.informer = Informer()
        self.recommender = Recommender()
        self.emotion_recommender = Emotion_Recommender()
        self.critic = Critic()
        self.summariser = Summarise()
        self.communication_draft = Communication_Draft()
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user", 
        "parts":["You are the Manager of an Agentic AI system in charge of implementing change strategies and you have a team consisting of "
        "a decomposer to break down the problem statement into defined tasks, "
        "an informer to provide information on topics and to provide answers to questions that require information,"
        "a recommender to generate content/recommend actions based on the changes to be implemented if a recommendation is needed or asked for, "
        "an emotion recommender to recommend ways to manage emotions to reduce resistance to change and foster greater trust, resilience and optimism, "
        "a summariser to summarise the recommended strategies to implement changes and add a faq section to the end, "
        "a critic to determine if the recommended strategies are relevant to the defined tasks and there are clearly highlighted reasons, goals and impacts of change, "
        "and a communication drafter to write a communication draft to submit if the user asks for it"]}])

    def query(self, user_query):

        tasks = self.decomposer.breakdown(user_query)
        agents = self.identify_agents(tasks.text)

        if agents["informer"] == True:
            info = self.informer.inform(user_query)
            return [info]

        solution = self.recommender.recommend(tasks.text)

        if agents["emotion_recommender"] == True:
            solution_emotion = self.emotion_recommender.recommend(tasks.text)
            solution_emotion = solution_emotion.text
        else:
            solution_emotion = ""

        summary = self.summariser.summarise(solution.text, solution_emotion)

        if agents["communication_draft"] == True:
            communication_draft = self.communication_draft.draft(tasks.text, summary.text)
            return [summary, communication_draft]
        else:
            return [summary]
    
    def identify_agents(self, tasks):
        response = self.chat.send_message("Given the defined tasks: " + tasks + ". Determine some agents you may not require for this job"
        "specifically, the emotion_recommender, the communication_draft and the informer, give false if you dont require the agent. "
        "give true for communication_draft if they ask for a communication draft"
        "Use this JSON schema: Return: {emotion_recommender={boolean}, communication_draft={boolean}, informer={boolean}}}")
        response = response.text
        response = cleaner(response)
        response = json.loads(response)
        return response


class Decomposer:
    def __init__(self):
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user", 
        "parts":["You are an expert in decomposing problem statements related to implenting change management strategies "
        "into simpler, concise tasks in point form to tackle."]}])

    def breakdown(self, user_query):
        response = self.chat.send_message("Given the user query: " + user_query + ". Break down the problem into well defined tasks,")
        return response


class Retriever:
    def __init__(self):
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user",
        "parts":["You are a member of a change management committe that is in charge of suggesting what kind of data is required based on prompts"]}])

    def suggest(self, tasks):
        response = self.chat.send_message("Given the tasks: " + tasks + ", what kind of data might be required?")
        return response
    
    def retrieve(self, tasks):
        prompt = self.suggest(tasks)
        data = query_chromadb(prompt.text)
        data_string = json.dumps(data)
        return data_string

class Informer:
    def __init__(self):
        self.retrieval = Retriever()
        self.critic = Critic()
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user",
        "parts":["You are a member of a change management committe who is well read on all things regarding"
        "change management. Provide information and data on topics that are asked of you, but make each point"
        "concise, not more than 4 sentences long."]}])

    def inform(self, user_query):
        data = self.retrieval.retrieve(user_query)
        response = self.chat.send_message("Given the dataset: " + data + user_query)
        return response


class Recommender:
    def __init__(self):
        self.retrieval = Retriever()
        self.critic = Critic()
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user",
        "parts":["You are a member of a change management committe that is in charge of suggesting solutions "
        "to implement changes based on data given to you, you do not have to mention the source. Generate content/recommend actions based on the changes"
        "to be implemented including the scope of change: orangisational, projects and people."]}])

    def recommend(self, tasks):
        data = self.retrieval.retrieve(tasks)
        response = self.chat.send_message("Given the dataset: " + data + ", and the tasks: " + tasks + ", recommend some actions"
        "to implement this change.")
        evaluation, feedback = self.critic.critic(tasks, response.text)
        while evaluation == False:
            response = self.improve(response.text, feedback.text)
            evaluation, feedback = self.critic.critic(tasks, response.text)
        return response
    
    def improve(self, solution, feedback):
        data = self.retrieval.retrieve(solution + feedback)
        response = self.chat.send_message("Given the feedback: " + feedback + ", and the old solution: " + solution + ", and the dataset: "  + data + 
        ", use the feedback given and new data to improve upon the old solution and return a new improved solution.")
        return response
    

class Emotion_Recommender:
    def __init__(self):
        self.retrieval = Retriever()
        self.critic = Critic()
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })       
        self.chat = self.model.start_chat(history=[{"role":"user",
        "parts":["You are a member of a change management committe that is in charge of suggesting solutions "
        "to implement changes based on data given to you. Recommend ways to manage emotions to reduce resistance "
        "to change and foster greater trust, resilience and optimism "
        "to be implemented including the scope of change: orangisational, projects and people."]}])    

    def recommend(self, tasks):
        data = self.retrieval.retrieve(tasks)
        response = self.chat.send_message("Given the dataset: " + data + ", and the tasks: " + tasks + ", recommend some actions"
        "to implement this change.")
        evaluation, feedback = self.critic.critic(tasks, response.text)
        while evaluation == False:
            response = self.improve(response.text, feedback.text)
            evaluation, feedback = self.critic.critic(tasks, response.text)
        return response
    
    def improve(self, solution, feedback):
        data = self.retrieval.retrieve(solution + feedback)
        response = self.chat.send_message("Given the feedback: " + feedback + ", and the old solution: " + solution + ", and the dataset: " + data + 
        ", use the feedback given and the new dataset to improve upon the old solution and return a new improved solution.")
        return response
            

class Critic:
    def __init__(self):
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user",
        "parts":["You are a critc that critically analyses change management strategies by determining if they are relevant to the defined tasks,"
        "and satisfy the scope of change: organisational. projects and people. Strategies should also be following frameworks to be considered good."
        "You also critique communication drafts on whether reasons, goals and the impact of the change are clearly highlighted."
        "You also critique responses to specific requests by users to assess whether or not tey are relevant to the requests."]}])     

    def critic(self, tasks, solution):
        response = self.chat.send_message("Given the defined tasks: " + tasks + ", and the suggested solution: " + solution +
        ". Give an evaluation of the solution and determine whether or not you give it a pass, where true means pass and false means fail. "
        "Use this JSON Schema: Return: {'pass':boolean, 'feedback':string}")
        response = response.text
        response = cleaner(response)
        response = json.loads(response)
        return response["pass"], response["feedback"]
    
    def critic_draft(self, tasks, draft):
        response = self.chat.send_message("Given the defined tasks: " + tasks + ", and the suggested solution: " + draft +
        ". Give an evaluation of the communication draft and determine whether or not you give it a pass, where true means pass and false means fail. "
        "Use this JSON Schema: Return: {'pass':boolean, 'feedback':string}")
        response = response.text
        response = cleaner(response)
        response = json.loads(response)
        return response["pass"], response["feedback"]

    def critic_info(self, tasks, response):
        response = self.chat.send_message("Given the defined tasks: " + tasks + ", and the suggested response: " + response +
        ". Give an evaluation of the response and determine whether or not you give it a pass, where true means pass and false means fail. "
        "Use this JSON Schema: Return: {'pass':boolean, 'feedback':string}")
        response = response.text
        response = cleaner(response)
        response = json.loads(response)
        return response["pass"], response["feedback"]


class Summarise:
    def __init__(self):
        self.retrieval = Retriever()
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user",
        "parts":["You are a member of a change management committee in charge of summarising the solution and emotional solution to implementing change strategies."]}])   
        
    
    def summarise(self, solution, solution_emotion):
        data = self.retrieval.retrieve(solution + solution_emotion)
        response = self.chat.send_message("Given the solution: " + solution + ", and the emotional solution: " + solution_emotion + ", and the given dataset: " + data +
        "Give me a summary of the solutions in a concise, structured step-by-step format. "
        "do not include title of document "
        "Include a FAQ at the back of the summary using relevant data if asked for, do not include title of document.")
        return response
    

class Communication_Draft:
    def __init__(self):
        self.critic = Critic()
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                              generation_config={
                                  "temperature":0.0,
                                  "top_k":40,
                                  "top_p":0.0,
                              })
        self.chat = self.model.start_chat(history=[{"role":"user",
        "parts":["You are a member of a change management committee in charge of writing up communication drafts. "
        "Ensure that you clearly highlight reasons, goals, and the impact of change in your draft"]}])

    def draft(self, tasks, summary):
        response = self.chat.send_message("Given the summary: " + summary + ", write a communication draft. Ensure that you make it as concise as possible. Only include 1 or 2 of the most important faqs at the back.")
        evaluation, feedback = self.critic.critic_draft(tasks, response.text)
        while evaluation == False:
            response = self.improve(response.text, feedback.text)
            evaluation, feedback = self.critic.critic_draft(tasks, response.text)
        return response
    
    def improve(self, draft, feedback):
        response = self.chat.send_message("Given the draft: " + draft + ", and the feedback given: " + feedback + 
        "Write a new draft based on the old draft and feedback given")
        return response