import sys
import pysqlite3
sys.modules["sqlite3"]=pysqlite3

from uuid import uuid4          #Used to generate unique ID
from dotenv import load_dotenv  #Loads environment variables from a .env file.
from pathlib import Path        #For working with file paths in a platform-independent way.
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma  #open-source vector database used to store and search embeddings efficiently.
from langchain_groq import ChatGroq   #For Module
from langchain_huggingface.embeddings import HuggingFaceEmbeddings   #way to convert text into vectors
from huggingface_hub import login
import os

# Load environment variables from .env
load_dotenv()

# Configuration

CHUNK_SIZE=1000
EMBEDDING_MODEL ="Alibaba-NLP/gte-base-en-v1.5"
VECTOR_STORE_DIR=Path(__file__).parent/"resources/vector_store"
COLLECTION_NAME="real_estate"
hf_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
#hf_token=st.secrets["APIKEYS"]["HUGGINGFACEHUB_API_TOKEN"]

# Ensure token is present
if not hf_token:
    raise ValueError("Hugging Face API token not found. Set HUGGINGFACEHUB_API_TOKEN in .env or system environment.")
login(token=hf_token)

# Initialize globals
llm=None
vector_store=None

def initialize_components():
    global llm, vector_store #Initializes the LLM and Vector Store.

    if llm is None:
        llm=ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.9,
            max_tokens=5000
            )

    if vector_store is None:
        ef=HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code":True}
        )
        vector_store=Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=ef,
            persist_directory=str(VECTOR_STORE_DIR)
        )

def process_urls(urls):
    """
    This function scrapes data from the URLs and stores it in a vector database.
    :param urls: input URLs
    :return: generator yielding status messages
    """
    yield "Initializing components...✅"
    initialize_components()
    vector_store.reset_collection()

    yield "Resetting vector Store...✅"
    loader=UnstructuredURLLoader(urls=urls)
    data=loader.load()

    yield "Splitting text into chunks...✅"
    # text_splitter=RecursiveCharacterTextSplitter(
    # separators=["\n\n","\n",",","."," "],
    # chunk_size=CHUNK_SIZE)
    text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ".", " ",","],
    chunk_size=CHUNK_SIZE,
    chunk_overlap=100  #For accuracy
)
    docs=text_splitter.split_documents(data)

    yield "Adding chunks to vector database...✅"
    uuids=[str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs,ids=uuids)

    yield "Done adding docs to vector databse...✅"

def generate_answer(query):
    if not vector_store:
        raise RuntimeError("Vector DataBase is not initiated")
    
    #retriever = vector_store.as_retriever(search_kwargs={"k": 6})  # was default (likely 2-4)
    #chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=retriever)
    chain=RetrievalQAWithSourcesChain.from_llm(llm=llm,retriever=vector_store.as_retriever())
    result=chain.invoke({"question":query},return_only_outputs=True)
    sources=result.get("sources","")

    return result['answer'],sources

if __name__=="__main__":
    # Step 1: Initialize the components
    initialize_components()
    
    urls=["https://www.foxbusiness.com/personal-finance/todays-mortgage-rates-august-14-2024",
    "https://www.foxbusiness.com/personal-finance/todays-mortgage-rates-august-13-2024"]
    #process_urls(urls)
    
    # Run through the RAG pipeline
    for status in process_urls(urls):
        print(status)


    answer,sources=generate_answer("Tell me what was the 30 year fixed mortgate rate along with the date?")
    print(f"Answer:{answer}")
    print(f"sources:{sources}")
