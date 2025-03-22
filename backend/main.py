from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
import chromadb
import json
import re

genai.configure(api_key="AIzaSyDIUseb8tdRlaNzkQW29KwDUx6sU4_1bAk")

client = chromadb.PersistentClient(path="../chroma")
collection = client.get_collection(name="knowledge_base")
embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key="AIzaSyDIUseb8tdRlaNzkQW29KwDUx6sU4_1bAk")

def query_chromadb(query_text, n_results=5):
    """
    Queries ChromaDB and returns the top results.

    Args:
        query_text (str): The search query.
        db_path (str): Path to the ChromaDB storage file.
        collection_name (str): Name of the collection.
        n_results (int): Number of results to return.

    Returns:
        list: A list of matching documents with metadata.
    """
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
        "a recommender to generate content/recommend actions based on the changes to be implemented, "
        "an emotion recommender to recommend ways to manage emotions to reduce resistance to change and foster greater trust, resilience and optimism, "
        "a summariser to summarise the recommended strategies to implement changes and add a faq section to the end, "
        "a critic to determine if the recommended strategies are relevant to the defined tasks and there are clearly highlighted reasons, goals and impacts of change, "
        "and a communication drafter to write a communication draft to submit", "you are gay"]}])

    def query(self):
        user_query = input("What is your problem statement: ")

        tasks = self.decomposer.breakdown(user_query)
        agents = self.identify_agents(tasks.text)

        solution = self.recommender.recommend(tasks.text)

        if agents["emotion_recommender"] == True:
            solution_emotion = self.emotion_recommender.recommend(tasks.text)
            solution_emotion = solution_emotion.text
        else:
            solution_emotion = ""

        summary = self.summariser.summarise(solution.text, solution_emotion)

        if agents["communication_draft"] == True:
            communication_draft = self.communication_draft.draft(tasks.text, summary.text)
            return communication_draft
        else:
            return summary
    
    def identify_agents(self, tasks):
        response = self.chat.send_message("Given the defined tasks: " + tasks + ". Determine some agents you may not require for this job"
        "specifically, the emotion_recommender and the communication_drafter, give true if you require the agent "
        "Use this JSON schema: Return: {emotion_recommender={boolean}, communication_draft={boolean}}")
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
        "to implement changes based on data given to you. Generate content/recommend actions based on the changes"
        "to be implemented including the scope of change: orangisational, projects and people."]}])

    def recommend(self, tasks):
        data = self.retrieval.retrieve(tasks)
        response = self.chat.send_message("Given the dataset: " + data + ", and the tasks: " + tasks + ", recommend some actions"
        "to implement this change. Explcitly mention what frameworks are used.")
        evaluation, feedback = self.critic.critic(tasks, response.text)
        while evaluation == False:
            response = self.improve(response.text, feedback.text)
            evaluation, feedback = self.critic.critic(tasks, response.text)
        return response
    
    def improve(self, solution, feedback):
        data = self.retrieval.retrieve(solution + feedback)
        response = self.chat.send_message("Given the feedback: " + feedback + ", and the old solution: " + solution + ", and the dataset: "  + data + 
        ", use the feedback given and new data to improve upon the old solution and return a new improved solution. Explcitly mention what frameworks are used.")
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
        "to implement this change. Explcitly mention what frameworks are used.")
        evaluation, feedback = self.critic.critic(tasks, response.text)
        while evaluation == False:
            response = self.improve(response.text, feedback.text)
            evaluation, feedback = self.critic.critic(tasks, response.text)
        return response
    
    def improve(self, solution, feedback):
        data = self.retrieval.retrieve(solution + feedback)
        response = self.chat.send_message("Given the feedback: " + feedback + ", and the old solution: " + solution + ", and the dataset: " + data + 
        ", use the feedback given and the new dataset to improve upon the old solution and return a new improved solution. Explcitly mention what frameworks are used.")
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
        "You also critique communication drafts on whether reasons, goals and the impact of the change are clearly highlighted."]}])     

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
        "Give me a summary of the solutions in a concise, structured step-by-step format. Explcitly mention what frameworks are used. Include a FAQ at the back of the summary using relevant data form the data set given.")
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
        evaluation, feedback = self.critic.critic(tasks, response.text)
        while evaluation == False:
            response = self.improve(response.text, feedback.text)
            evaluation, feedback = self.critic.critic(tasks, response.text)
        return response
    
    def improve(self, draft, feedback):
        response = self.chat.send_message("Given the draft: " + draft + ", and the feedback given: " + feedback + 
        "Write a new draft based on the old draft and feedback given")
        return response
    

main = Manager()
response = main.query()
print(response.text)