from chroma_client import ChromaClient
chroma_client = ChromaClient()
chroma_client.init_chroma()


if __name__ == '__main__':
    print(chroma_client.count())