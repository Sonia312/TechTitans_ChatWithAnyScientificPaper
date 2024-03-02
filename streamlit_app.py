from dotenv import load_dotenv
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

import textract

def extract_text_from_text(uploaded_file):
    # Use read method to get the content of the uploaded file
    text = uploaded_file.read()
    return text

def main():
    load_dotenv()
    st.set_page_config(page_title="Ask your Text File")
    st.header("Ask your Text File 💬")
    
    # upload file
    uploaded_file = st.file_uploader("Upload your Text file", type="txt")
    
    # extract the text
    if uploaded_file is not None:
        text = extract_text_from_text(uploaded_file)

        # Ensure the text is decoded to a string
        if isinstance(text, bytes):
            text = text.decode('utf-8')

        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        # create embeddings
        embeddings = OpenAIEmbeddings()

        # check if there are chunks before creating the knowledge base
        if chunks:
            knowledge_base = FAISS.from_texts(chunks, embeddings)
            
            # show user input
            user_question = st.text_input("Ask a question about your document:")
            if user_question:
                docs = knowledge_base.similarity_search(user_question)
                
                llm = OpenAI()
                chain = load_qa_chain(llm, chain_type="stuff")
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=user_question)
                    print(cb)
                    
                st.write(response)

if __name__ == '__main__':
    main()
