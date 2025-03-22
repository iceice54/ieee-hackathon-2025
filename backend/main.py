import asyncio
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain.schema import Document  # Import Document from langchain
import re
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

file_path = "./papers/test.pdf"

async def test():
    def clean_text(text):
        # Remove newlines that appear between words
        text = re.sub(r'\n+', ' ', text)
        
        # Remove leading/trailing spaces
        text = text.strip()
        
        # Optional: Remove multiple spaces and replace with a single space
        text = re.sub(r'\s+', ' ', text)
        
        return text
    loader = PyPDFLoader(file_path, mode="single")
    documents = loader.load()
    # pages = []
    # async for page in loader.alazy_load():
    #     pages.append(page)
    
    # if pages:
    #     # print(f"{pages[0].metadata}\n")
    #     pprint.pprint(pages[10].page_content)
    # else:
    #     print("No pages were loaded.")
    # for page in pages:
    #     print(page)
    cleaned_documents = []
    for doc in documents:
        # Clean the text while preserving the document structure (metadata + page content)
        cleaned_text = clean_text(doc.page_content)
        
        # Wrap cleaned text and metadata in a Document object
        cleaned_documents.append(Document(
            page_content=cleaned_text,
            # metadata=doc.metadata  # preserve metadata like page number
        ))
    text_splitter = SemanticChunker(GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key), 
                                    breakpoint_threshold_type="percentile", breakpoint_threshold_amount=80)
#     text_splitter = RecursiveCharacterTextSplitter(
#     # Set a really small chunk size, just to show.
#     chunk_size=500,
#     chunk_overlap=50,
#     length_function=len,
#     is_separator_regex=False,
# ) 
    chunks = text_splitter.split_documents(cleaned_documents)
    # for chunk in chunks:
    #     print(chunk.page_content)  
    vector_store = InMemoryVectorStore.from_documents(chunks, 
                                GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key))
    docs = vector_store.similarity_search("What is the first model of change", k=2)
    for doc in docs:
        print(f'{doc.page_content}\n')


# Ensure we're running the asyncio event loop properly
if __name__ == "__main__":
    asyncio.run(test())  # Properly running the coroutine in the event loop
