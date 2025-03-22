import chromadb
import os
import asyncio
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
import re

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Function to clean and process text
def clean_text(text):
    # Remove newlines and excess spaces
    text = re.sub(r'\n+', ' ', text)
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

# Function to load PDFs from the folder
async def load_pdfs_from_folder(folder_path):
    i=0
    for filename in os.listdir(folder_path):
        print(i)
        i+=1
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path, mode="single")
            pdf_documents = loader.load()
            cleaned_documents = []
            for doc in pdf_documents:
                # Clean the text while preserving the document structure (metadata + page content)
                cleaned_text = clean_text(doc.page_content)
                
                # Wrap cleaned text and metadata in a Document object
                cleaned_documents.append(Document(
                    page_content=cleaned_text,
                    # metadata=doc.metadata  # preserve metadata like page number
                ))
            text_splitter = SemanticChunker(GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key), 
                                            breakpoint_threshold_type="percentile", breakpoint_threshold_amount=80)
            chunks = text_splitter.split_documents(cleaned_documents)   
            db = Chroma("knowledge_base", GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key), persist_directory="../chroma")
            db.add_documents(chunks)

# Function to store documents in ChromaDB
# async def store_in_chromadb():
#     # Load PDFs from the folder
#     documents = await load_pdfs_from_folder(pdf_folder_path)

#     # Split documents into smaller chunks (optional, depending on document length)
#     text_splitter = SemanticChunker(
#         chunk_size=500,  # Adjust as necessary
#         chunk_overlap=50,
#         length_function=len,
#     )
#     chunks = text_splitter.split_documents(documents)

#     # Create embeddings for the chunks
#     embeddings = [embedding_model.embed_text(doc.page_content) for doc in chunks]

#     # Create or load the Chroma vector store
#     db = Chroma(collection_name=collection_name, embedding_function=embedding_model)

#     # Add the chunks to ChromaDB
#     db.add_documents(chunks, embeddings)

#     # Optionally, you can check the number of documents in the collection
#     print(f"Number of documents in ChromaDB: {len(db)}")

# Run the async function
if __name__ == "__main__":
    client = chromadb.PersistentClient()
    collection = client.create_collection(name="knowledge_base")
    pdf_folder_path = "../papers"
    asyncio.run(load_pdfs_from_folder(pdf_folder_path))
