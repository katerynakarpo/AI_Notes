from openai import OpenAI
import os
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import ast

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = "text-embedding-3-small"
GPT_MODEL = "gpt-3.5-turbo"
CLIENT = OpenAI(api_key=OPENAI_API_KEY)


def get_embeddings(text):
    response = CLIENT.embeddings.create(input=text, model=EMBEDDING_MODEL)
    embedding = response.data[0].embedding
    return np.array(embedding, dtype=np.float32)


#  TODO: refactoring
def search_by_embeddings_str(search_prompt: str, notes: list, n: int = 5, threshold: float = 0.4):
    notes_df = pd.DataFrame(notes, columns=['note_id', 'notes_text'])
    search_embedding = get_embeddings(search_prompt)
    notes_df["embedding"] = notes_df['notes_text'].apply(lambda x: get_embeddings(x))
    notes_df['similarities'] = notes_df['embedding'].apply(lambda x: cosine_similarity([x], [search_embedding]))
    res = notes_df.sort_values('similarities', ascending=False).head(n)
    return res


# TODO: make cosine in DB
def search_by_embeddings_emb(search_embedding: str, note_embeddings: list, n: int = 5, threshold: float = 0.4):
    notes_embeddings_df = pd.DataFrame(note_embeddings, columns=['note_id', 'embedding'])
    notes_embeddings_df['embedding'] = notes_embeddings_df['embedding'].apply(lambda x: np.array(x))
    notes_embeddings_df['similarities'] = notes_embeddings_df['embedding'].apply(
        lambda x: cosine_similarity([x], [search_embedding]))
    filtered_res = notes_embeddings_df[notes_embeddings_df['similarities'] >= threshold]
    sorted_res = notes_embeddings_df.sort_values('similarities', ascending=False).head(n)
    return filtered_res

# TODO: re-write it to use in system
def search_by_prompt(search_prompt: str, notes: [str]):
    query = f'Return only list with ID in format [ID_1,ID_2,..]. Search prompt: {search_prompt} '.join(
        str(f'ID_{i}: {notes[i]}') for i in range(len(notes) - 1))

    response = CLIENT.chat.completions.create(
        messages=[
            {'role': 'system',
             'content': "You are an intelligent note management system capable of understanding and responding to "
                        "natural language queries from a user. Your task is to analyze the user's questions about "
                        "their notes and retrieve the most relevant information from a database of text entries. Here "
                        "are some examples of queries you might receive: 'What plans do I have for this weekend?', "
                        "'Show recent notes about LLM', 'Portuguese words to learn'. You should parse these queries "
                        "to determine the user's intent and provide accurate and relevant responses based on the "
                        "notes available. Return list with ids of most relevant notes."},
            {'role': 'user', 'content': query},
        ],
        model=GPT_MODEL,
        temperature=0,
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    notes = ["Dentist appointment on Monday at 10:00",
             "Recipe for Sunday's pasta dinner: 8 cups of pasta (we used Farfalle) 12 cups of cold water 1 "
             "tablespoon of olive oil 1 tablespoon of sea salt or kosher salt 2 medium onions, diced 2 large garlic "
             "cloves, minced 1 tablespoon of Italian seasoning ...",
             "TODO: Check articles about LLMs with Memory",
             "#portuguese sorrir - to smile",
             "Words to learn:  semana, ano,  hoje,  amanhã.",
             "calendário,  segundo,  minuto, amanhã, relógio - teach.",
             "minuto, amanhã, relógio"
             ]
    result = search_by_embeddings_str('Portuguese words to learn', notes)
    print(result)

    result = search_by_prompt('Portuguese words to learn', notes)
    print(result)
