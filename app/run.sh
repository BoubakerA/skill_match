#!/bin/bash

uv run python -m uvicorn app.api:app --host 0.0.0.0 --port 8000 &
uv run streamlit run app/app.py --server.address 0.0.0.0 --server.port 8501

