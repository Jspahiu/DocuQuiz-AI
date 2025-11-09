from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
import os.path
from config import *



class Chatbot:
    def __init__(self, pdf_files:list, reset_vectorstore:bool, token_count:int):
        self.pdf_files = pdf_files
        self.reset_vectorstore = reset_vectorstore
        self.token_count = token_count
        self.is_initialized = False

    def initialize(self):
        if not self.is_initialized:
            self.vectorstore = self._build_vectorstore()
            self.qa = self._build_qa(self.vectorstore, self.token_count)
            self.is_initialized = True

    def query(self, query, token_count):
        if not self.is_initialized:
            raise Exception("Bot not initialized yet")
        
        # Rebuild the QA chain with the current token count
        self.qa = self._build_qa(self.vectorstore, token_count)
        response = self.qa.invoke(query)
        #print(response)
        
        return response
    
    def _build_vectorstore(self):
        vectorstore_file_name = "quiz_vectorstore"
    
        vectorstore_file_exists = os.path.exists(vectorstore_file_name)
    
        embeddings = OpenAIEmbeddings()
    
        if not vectorstore_file_exists or self.reset_vectorstore:
            documents = []            
            
            for pdf_file in self.pdf_files:
                if not os.path.exists(pdf_file):
                    raise Exception(f"File {pdf_file} does not exist")
                
                # Load document using PyPDFLoader document loader
                loader = PyPDFLoader(pdf_file)
                documents.extend(loader.load())
                
            # Split document in chunks
            text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=50, separator="\n")

            docs = text_splitter.split_documents(documents=documents)
        
            # Create vectors
            vectorstore = FAISS.from_documents(docs, embeddings)
            
            # Persist the vectors locally on disk
            vectorstore.save_local(vectorstore_file_name)

        # Load from local storage
        persisted_vectorstore = FAISS.load_local(vectorstore_file_name, embeddings, allow_dangerous_deserialization=True)
    
        return persisted_vectorstore
    
    def _build_qa(self, persisted_vectorstore, token_count):
        # Define a custom prompt template
        from langchain_core.prompts import PromptTemplate

        prompt_template = """
        You are an intelligent and helpful AI assistant for making a quiz.
        Make sure to make a quiz set based on the context provided.
        Please provide the quiz in 10 questions.
        ONLY use information from the context below. Do NOT add anything not in the context. 
        If there is not enough information to generate all 10 questions, generate fewer questions instead.
        State every question and options only once, do not repeat the same question or/and responses.
        Each question should have 4 options (a, b, c, d) and indicate the correct answer.
        Make it in this format:
        1. Question

        a) Option A
        b) Option B
        c) Option C
        d) Option D

        Make sure the answer key is provided after all the questions and options are listed that you are creating in this format:
        Make sure you provide the correct answer after the options like this form:
        Question #1 Answer: A/B/C/D

        ONLY use information from the context below. Do NOT add anything not in the context. 
        If there is not enough information to generate all 10 questions, generate fewer questions instead.


        If there is mutliple answers, list them separated by commas like this:
        Question #2 Answer: A,C

        Context:
        {context}

        Question:
        {question}

        Helpful answer in markdown:
        """

        prompt = PromptTemplate.from_template(prompt_template)

        # Rough approximation: 1 token ≈ 4 chars
        
        print(f"Token count for context: {token_count}")
        # Use default model if token_count is None
        if token_count is None or token_count <= 8192:  # ≤ mini 4o context, 8192 tokens
            model_use = "gpt-4o-mini"
            print("Using gpt-4o-mini model")
        elif token_count >= 16384:  # ≤ gpt-3.5-turbo / gpt-5-mini context, 16384 tokens
            model_use = "gpt-5-mini"
            print("Using gpt-5-mini model")
        elif token_count >= 32768:  # ≤ gpt-4o / gpt-5 context, 32768 tokens
            model_use = "gpt-5"
            print("Using gpt-5 model")
        else:
            model_use = "truncate or split context"
        
        # Create the chain
        llm = ChatOpenAI(
            model=model_use,  # More cost-effective model
            temperature=0
        )
        qa = (
            {"context": persisted_vectorstore.as_retriever(), "question": RunnablePassthrough()}
            | prompt 
            | llm 
            | StrOutputParser()
        )

        return qa

