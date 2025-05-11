import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

def create_lebron_vectorstores():
    url = "https://en.wikipedia.org/wiki/LeBron_James"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Step 1: Navigate to mw-parser-output
    body_content = soup.find("div", id="bodyContent")
    if not body_content:
        raise ValueError("Cannot find bodyContent div.")

    mw_content_text = body_content.find("div", id="mw-content-text")
    if not mw_content_text:
        raise ValueError("Cannot find mw-content-text div.")

    parser_output = mw_content_text.find("div", class_="mw-parser-output")
    if not parser_output:
        raise ValueError("Cannot find mw-parser-output div.")

    # Step 2: Extract Infobox
    infobox = parser_output.find("table", class_="infobox")
    infobox_text = ""
    if infobox:
        for row in infobox.find_all(["tr", "th", "td"]):
            text = row.get_text(separator=" ", strip=True)
            if text:
                infobox_text += text + "\n"

    # Step 3: Extract Intro and Body Texts
    intro_text = ""
    body_text = ""
    split_point_found = False

    # Here's the key: find_all everything (p, div, h2, etc) in correct order
    for elem in parser_output.find_all(["p", "div", "ul", "ol", "h2", "h3", "h4"], recursive=True):
        if elem.name == "table" and "infobox" in elem.get("class", []):
            continue  # Skip infobox again

        # Handle meta weirdness
        if elem.name == "meta":
            continue

        # Detect Early life heading
        if elem.name == "h2" and elem.get("id") == "Early_life":
            split_point_found = True
            continue

        # Also detect if inside div.mw-heading2 with h2
        if elem.name == "div" and "mw-heading2" in elem.get("class", []):
            h2 = elem.find("h2")
            if h2 and h2.get("id") == "Early_life":
                split_point_found = True
                continue

        if not split_point_found:
            if elem.name == "p":
                intro_text += elem.get_text(separator=" ", strip=True) + "\n"
        else:
            if elem.name in ["p", "ul", "ol", "h3", "h4"]:
                body_text += elem.get_text(separator=" ", strip=True) + "\n"

    # Step 4: Build Document objects
    intro_doc = Document(
        page_content=infobox_text + "\n" + intro_text,
        metadata={"section": "intro"}
    )
    body_doc = Document(
        page_content=body_text,
        metadata={"section": "body"}
    )

    # Step 5: Split Documents
    small_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100,
        chunk_overlap=20
    )
    large_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=600,
        chunk_overlap=100
    )

    intro_chunks = small_splitter.split_documents([intro_doc])
    body_chunks = large_splitter.split_documents([body_doc])

    print(f"Intro chunks: {len(intro_chunks)}")
    print(f"Body chunks: {len(body_chunks)}")

    # Step 6: Create Vectorstores
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    intro_vectorstore = None
    body_vectorstore = None

    if intro_chunks:
        intro_vectorstore = Chroma.from_documents(
            documents=intro_chunks,
            collection_name="lebron_intro",
            embedding=embeddings,
            persist_directory="./lebron_intro_db"
        )

    if body_chunks:
        body_vectorstore = Chroma.from_documents(
            documents=body_chunks,
            collection_name="lebron_bio",
            embedding=embeddings,
            persist_directory="./lebron_bio_db"
        )

    return intro_vectorstore, body_vectorstore


# if __name__ == "__main__":
#     if True:
#         intro_vectorstore, body_vectorstore = create_lebron_vectorstores()
#     else:
#         intro_vectorstore = Chroma(
#             collection_name="lebron_intro",
#             embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
#             persist_directory="./lebron_intro_db"
#         )
#         body_vectorstore = Chroma(
#             collection_name="lebron_bio",
#             embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
#             persist_directory="./lebron_bio_db"
#         )

#     intro_vectorstore_retriever = intro_vectorstore.as_retriever(
#         search_type="mmr", search_kwargs={"k": 5,}
#     )
#     body_vectorstore_retriever = body_vectorstore.as_retriever(
#         search_type="mmr", search_kwargs={"k": 5,}
#     )

#     query = input("Enter a query (or 'exit' to quit): ")
#     while query != "exit":
#         intro_results = intro_vectorstore_retriever.invoke(query)
#         # body_results = body_vectorstore_retriever.invoke(query)

#         print("Intro Results:")
#         for result in intro_results:
#             print(result.page_content)

#         # print("\nBody Results:")
#         # for result in body_results:
#         #     print(result.page_content)

#         query = input("Enter a query (or 'exit' to quit): ")