import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Ensure Gemini API Key is available
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("Please set GEMINI_API_KEY in your environment or .env file.")

# Initialize LLM and Embeddings
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# -------------------------------------------------------------------
# 1. Document Loading & Chunking
# -------------------------------------------------------------------
def load_and_chunk_documents(file_path: str):
    """Loads a document and splits it into sensible, overlapping chunks."""
    print(f"[*] Loading document: {file_path}")
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    
    raw_documents = loader.load()
    
    # Chunking strategy: 500 characters (~100-150 tokens) with 100 character overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(raw_documents)
    print(f"[✓] Created {len(chunks)} chunks from document.")
    return chunks

# -------------------------------------------------------------------
# 2. Embedding & Vector Database Creation
# -------------------------------------------------------------------
def build_vector_store(chunks, db_directory="./chroma_db"):
    """Embeds document chunks and persists them into a Chroma vector DB."""
    print("[*] Generating embeddings and storing in Chroma DB...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_directory
    )
    print("[✓] Vector DB created successfully.")
    return vector_db

# -------------------------------------------------------------------
# 3. Retrieval & Generation Pipeline
# -------------------------------------------------------------------
def rag_answer_question(query: str, vector_db):
    """Retrieves top relevant chunks and generates a grounded response."""
    # Retrieve top 3 relevant chunks
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    retrieved_docs = retriever.invoke(query)
    
    # Extract text from retrieved chunks
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Construct RAG Prompt
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use ONLY the following pieces of retrieved context to answer the question. "
        "If the context does not contain the answer, strictly reply with 'I cannot answer this based on the provided documents.'\n\n"
        "Context:\n{context}"
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    chain = prompt_template | llm
    response = chain.invoke({"context": context, "input": query})
    return response.content, retrieved_docs

def plain_llm_answer_question(query: str):
    """Answers a question using only the LLM's general knowledge (No Context)."""
    response = llm.invoke(query)
    return response.content

# -------------------------------------------------------------------
# 4. Demonstration / Test Script
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Create a sample document with proprietary/custom knowledge
    sample_doc_content = """
    Avanish's Personal Project Policy v2.4 (Internal Doc - 2026):
    All internal AI projects built at Avanish's lab must follow Protocol Alpha-9. 
    Protocol Alpha-9 mandates that all local vector databases must use Chroma, 
    and memory usage must not exceed 4GB per container instance. 
    The designated emergency supervisor for code deployments is Dr. Robert Vance, 
    reachable at extension #8821. Any unauthorized deployment without Dr. Vance's sign-off 
    results in automatic deployment rollback.
    """
    
    # Save dummy document for testing
    file_path = "internal_policy.txt"
    with open(file_path, "w") as f:
        f.write(sample_doc_content)

    # Process Document and build Vector Database
    chunks = load_and_chunk_documents(file_path)
    vector_db = build_vector_store(chunks)

    # Question ONLY answerable from the document
    test_query = "Who is the emergency supervisor for code deployments according to Protocol Alpha-9, and what is their extension?"

    print("\n" + "=" * 60)
    print("TEST QUERY:", test_query)
    print("=" * 60)

    # 1. Plain LLM (Without RAG)
    print("\n--- 1. Plain LLM Response (No RAG) ---")
    plain_output = plain_llm_answer_question(test_query)
    print(plain_output)

    # 2. RAG Pipeline (With Retrieval)
    print("\n--- 2. RAG System Response (With Retrieval & Grounding) ---")
    rag_output, retrieved_chunks = rag_answer_question(test_query, vector_db)
    print(rag_output)

    print("\n--- Retrieved Context Chunks ---")
    for idx, doc in enumerate(retrieved_chunks):
        print(f"Chunk {idx+1}: {doc.page_content.strip()}")
