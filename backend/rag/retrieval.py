from langchain_openai import OpenAIEmbeddings
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

def retrieve(user_query, user_id):

    embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
    chroma_client = chromadb.PersistentClient("./chroma_db")
    collection = chroma_client.get_or_create_collection(name="platemate")

    ids = []
    documents = []
    metadatas = []

    queries = generate_queries(user_query)
    queries.append(user_query)

    for query in queries:

        embedded_query = embeddings.embed_query(query)
        
        results = collection.query(
        query_embeddings=embedded_query,
        n_results=5,
        where={"user_id" : user_id}
        )

        ids.extend(results['ids'][0])
        documents.extend(results['documents'][0])
        metadatas.extend(results['metadatas'][0])
    
    final_results = {
        'ids' : [],
        'documents' : [],
        'metadatas' : []
    }
    for i, id in enumerate(ids):
        if id not in final_results['ids']:
            final_results['ids'].append(id)
            final_results['documents'].append(documents[i])
            final_results['metadatas'].append(metadatas[i])

    return final_results 


def generate_queries(user_query):

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                    {"role": "system", "content": f"""Generate 4 different variations of the user query such that 
                     the retrieval from a nutritional meal plan becomes easy. Return ONLY a JSON array of strings. No explanation, no numbering, just the array.
                     Example: ["variation 1", "variation 2", "variation 3", "variation 4"]
                      """}, 
                      {"role": "user", "content": user_query}
        ], temperature=0.7)
    
    queries = json.loads(response.choices[0].message.content)

    return queries

def generate(user_query, results, history=[]):
    client = OpenAI()
    # context = "\n".join(results['documents'][0])

    context_parts = []
    print(f"metadatas type: {type(results['metadatas'])}")
    print(results['metadatas'])
    for i, doc in enumerate(results['documents']):
        metadata = results['metadatas'][i]
        if metadata.get('type') == 'table':
            context_parts.append(metadata.get('original'))
        else:
            context_parts.append(doc)
    
    context = "\n".join(context_parts)

    print(f"Text getting sent to the LLM: {context} + {history} ")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                    {"role": "system", "content": f"""You are a nutrition assistant. Answer the user's question 
        using ONLY the context provided below. If the answer is 
        not in the context, say "I don't have that information 
        in your meal plan."
        Context:
    {context}"""}] + history +
            [{"role": "user", "content": user_query}
        ],
        temperature=0
    )
    return response.choices[0].message.content

if __name__ == '__main__':

    user_query = "What should I have for lunch on Monday?"
    user_id = "nivi"
    final_results = retrieve(user_query, user_id)
    # print(f"DISTANCES: {results['distances']}")
    # print(f"IDS: {results['ids']}")

    llm_output = generate(user_query, final_results)

    print(f"here's LLM output: \n {llm_output}")