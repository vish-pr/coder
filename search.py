import os
import requests
from googlesearch import search
from urllib.parse import urlparse

def do_search(query: str) -> str:
  results = search(query, num_results=3, advanced=True)
  for result in results:
    print(f"Found URL using googlesearch: {result}")

if __name__ == "__main__":
  print(do_search("google search python library documentation"))
