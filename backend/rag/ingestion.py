from langchain_community.document_loaders import PyPDFLoader
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import NarrativeText, Title, ListItem, Table
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from dotenv import load_dotenv
from openai import OpenAI
import chromadb


load_dotenv()


def load_pdf(file_path):

    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return docs

    except FileNotFoundError:
        print("Please include the path of a file that exists")

        #Nothing is returned here - this needs to be handled properly
    
    except Exception as e:
        print(f"An unexpected error has occured: {e}")

def chunking_using_unstructured(file_path):

    elements = partition_pdf(filename=file_path,
                            skip_infer_table_types=False,
                            strategy='hi_res')

    return elements

DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

def combine_elements_into_chunks(elements, source, user_id):
    final_chunks = []
    current_text = ""
    current_title = ""

    for element in elements:
        if isinstance(element, Title):
            if element.text in DAYS:
                if current_title:
                    chunk = Document(
                        page_content=current_title + current_text,
                        metadata={
                            "section": current_title,
                            "source": source,
                            "user_id": user_id
                        }
                    )
                    final_chunks.append(chunk)
                current_title = element.text
                current_text = ""
            else:
                current_text += "\n" + element.text

        elif isinstance(element, Table):
            summary = summarize(element.text)
            chunk = Document(
                page_content=summary,
                metadata={
                    "section": current_title,
                    "source": source,
                    "user_id": user_id,
                    "type": "table",
                    "original": element.text
                }
            )
            final_chunks.append(chunk)

        else:
            current_text += "\n" + element.text

    # save the last chunk
    if current_text:
        chunk = Document(
            page_content=current_title + current_text,
            metadata={
                "section": current_title,
                "source": source,
                "user_id": user_id
            }
        )
        final_chunks.append(chunk)

    return final_chunks
        
def summarize(text):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a nutrition document assistant. 
Your job is to convert structured table data into clear, natural language summaries.
Include all specific numbers, values, and facts from the table.
Write in a way that matches how someone would ask questions about this information."""},
            {"role": "user", "content": f"Summarize this nutrition table into natural language:\n\n{text}"}
        ],
        temperature=0
    )
    return response.choices[0].message.content

def embed(final_chunks):

    embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    )

    embedded_chunks = []

    for chunk in final_chunks:
        embedded_chunk = embeddings.embed_documents([chunk.page_content])[0]
        embedded_chunks.append((embedded_chunk, chunk))

    return embedded_chunks

def store(embedded_chunks):

    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="platemate")
    
    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for i, (vector, chunk) in enumerate(embedded_chunks):

        ids.append(str(i))
        embeddings.append(vector)
        metadatas.append(chunk.metadata)
        documents.append(chunk.page_content)
    
    collection.add(
    ids=ids,
    embeddings=embeddings,
    metadatas=metadatas,
    documents=documents
    )
    
if __name__ == '__main__':

    pdf_file_path = "backend/meal_plan.pdf"

    elements = chunking_using_unstructured(pdf_file_path)

    for element in elements:
        print(f"{type(element).__name__}: '{element.text[:50]}'")

    final_chunks = combine_elements_into_chunks(elements, "meal_plan.pdf", "nivi")

    for chunk in final_chunks:
        if chunk.metadata.get('type') == 'table':
            print(f"TABLE CHUNK: {chunk.page_content}")
            print(f"ORIGINAL: {chunk.metadata.get('original')}")
            print("---")
            break

    embedded_chunks = embed(final_chunks)

    store(embedded_chunks)

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="platemate")
