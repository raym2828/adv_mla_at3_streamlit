# adv_mla_at3_streamlit
Repository to host streamlit app and Dockerfile development

## Folder Structure
```bash
├── fast_api
│   └── app
├── requirements.txt


├── streamlit
│   └── app
|         └── main.py
│   └── requirements.txt
│   └── .gitignore
└── README.md

```

## Getting Started

To get started, clone the repository and install the necessary dependencies.

### Prerequisites (requirement.txt)

streamlit==1.38.0
pandas==2.2.3
scikit-learn==1.5.1
fastapi==0.115.0
uvicorn==0.31.0
joblib==1.4.2
dumb-init
xgboost==2.1.1
pydantic==2.9.2
prophet==1.1.5
requests==2.32.3

### Installation

1. Clone the repo:
    ```bash
   git clone https://github.com/raym2828/adv_mla_at3_streamlit.git


2. Connect this git repository on Render and streamlit cloud 
 - (FASTAPI) Start Command: uvicorn fast_api.app:app --host 0.0.0.0 --port 8000
 - (Streamlit on Render) It does not need start command for Streamlit cloud, but if you want to deploy it on Render
             Start Command: streamlit run streamlit/app/main.py --server.port 8501

3. Display this service on the web
 - (FASTAPI) https://adv-mla-at3.onrender.com/
 - (Streamlit) https://airflighter.streamlit.app/