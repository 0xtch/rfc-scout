# rfc-scout

## How to run

Run all commands from the project root.

### 1. Set up

```bash
conda create -n rfc-rag python=3.14
conda activate rfc-rag
pip install langchain-community langchain-text-splitters
```

### 2. Get the data

```bash
mkdir -p data/rfc
curl -o data/rfc/rfc4271.txt https://www.rfc-editor.org/rfc/rfc4271.txt
```
