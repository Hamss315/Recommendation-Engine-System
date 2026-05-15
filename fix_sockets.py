import os
import glob

# Ensure we use an absolute path globally resolved
GUI_PAGES = glob.glob('gui/pages/*.py')
UTILS = glob.glob('utils/*.py')

CACHE_FUNC = '''
import streamlit as st
@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()
'''

for filepath in GUI_PAGES + UTILS:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If it's already using get_database(), skip
    if "get_database()" in content:
        continue

    # Remove all standard MongoDB client invocations and replace with cached accessor
    content = content.replace('client = MongoClient("mongodb://localhost:27017/")', '')
    content = content.replace('db = client["ecommerce_recommendation"]', 'db = get_database()')
    
    # Ensure correct imports
    if "import streamlit as st" not in content:
        content = "import streamlit as st\n" + content
    
    if "@st.cache_resource\ndef get_database():" not in content:
        # Prepend the caching function after standard imports
        parts = content.split('import streamlit as st', 1)
        if len(parts) > 1:
            content = parts[0] + 'import streamlit as st\n' + CACHE_FUNC + parts[1]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Patch applied to all Streamlit files successfully!")
