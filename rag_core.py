from pdf_utils import extract_text_from_pdf, chunk_text
from bedrock_utils import get_embedding
from openai_utils import generate_answer
from mongo_utils import insert_chunks, search_similar_chunks



def process_pdf_and_store(pdf_bytes, filename):
    text = extract_text_from_pdf(pdf_bytes)
    chunks = chunk_text(text)
    embedded_chunks = [(chunk, get_embedding(chunk)) for chunk in chunks]
    insert_chunks(embedded_chunks, source_name=filename)
    return len(embedded_chunks)



def process_multiple_pdfs(file_list):
    total_chunks = 0
    for file in file_list:
        text = extract_text_from_pdf(file.read())
        chunks = chunk_text(text)
        embedded_chunks = []
        for chunk in chunks:
            embedding = get_embedding(chunk)
            embedded_chunks.append((chunk, embedding))
        insert_chunks(embedded_chunks, source_name=file.name)
        total_chunks += len(embedded_chunks)
    return total_chunks



def answer_question(question: str, k: int = 3) -> str:
    query_embedding = get_embedding(question)
    results = search_similar_chunks(query_embedding, k=k)
    if not results:
        return "No relevant content found in the documents. Try rephrasing your question."
    context = "\n".join([doc["content"] for doc in results])
    prompt = f"""Here is the information we have: {context}.
    Taking this information into account, clearly answer the following question: {question} """
    return generate_answer(prompt)
