import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="platemate")

result = collection.get(ids=["7"])
print(f"Chunk 7: {result['documents']}")
print(f"Metadata: {result['metadatas']}")

# def combine_elements_into_chunks(elements, source, user_id):

#     final_chunks = []
#     current_text = ""
#     current_title = "" 

#     for element in elements:

#         if isinstance(element, Title):
            
#             if current_title is not Null:
#                 chunk = Document(
#                     page_content=current_title + current_text,
#                     metadata={
#                         "section": current_title,
#                         "source": source,
#                         "user_id": user_id
#                     }
#                 )
#                 final_chunks.append(chunk)
            
#             current_title += element.text
        
#         elif isinstance(element, Table):
#             print(f"TABLE FOUND: {element.text[:50]}")
#             summary = summarize(element.text)
#             chunk = Document(
#                 page_content=summary,
#                 metadata={
#                     "section": current_title,
#                     "source": source,
#                     "user_id": user_id,
#                     "type": "table",
#                     "original": element.text
#                 }
#             )
#             final_chunks.append(chunk)
        
#         else:
#             current_text += element.text