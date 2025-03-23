import asyncio
import re
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

file_path = "./papers/test.pdf"

async def test():
    def clean_text(text):
        text = re.sub(r'\n+', ' ', text)
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    loader = PyPDFLoader(file_path, mode="single")
    documents = loader.load()
    
    cleaned_documents = []
    for doc in documents:
        cleaned_text = clean_text(doc.page_content)
        
        cleaned_documents.append(Document(
            page_content=cleaned_text,
        ))
    text_splitter = SemanticChunker(GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key), 
                                    breakpoint_threshold_type="percentile", breakpoint_threshold_amount=80)

    chunks = text_splitter.split_documents(cleaned_documents)

    vector_store = InMemoryVectorStore.from_documents(chunks, 
                                GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key))
    docs = vector_store.similarity_search("What is the first model of change", k=2)
    for doc in docs:
        print(f'{doc.page_content}\n')


if __name__ == "__main__":
    asyncio.run(test())  
