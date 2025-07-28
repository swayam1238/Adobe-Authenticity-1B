# Adobe-Authenticity-1B
# Round 1B: Persona-Driven Document Intelligence - Adobe Hackathon

This repository contains the solution for Round 1B of the Adobe "Connecting the Dots" Hackathon. This script functions as an intelligent document analyst, processing a collection of PDFs to extract and prioritize sections that are most relevant to a specific user persona and their defined "job-to-be-done."

The solution is built to run entirely offline in a constrained Docker environment, leveraging a lightweight AI model to achieve contextual understanding.

---

## 🚀 How to Build and Run

*Prerequisites:* You must have Docker installed and running on your system.

### Step 1: Set Up Inputs

Before running the solution, you need to provide the necessary input files.

1.  *Add Documents:* Place all the PDF documents you want to analyze into the input/documents/ directory.
2.  *Define Persona:* Open and edit the input/persona.json file. This file tells the script who the "user" is and what they are looking for.

    *Example persona.json for an Investment Analyst:*
    json
    {
      "persona": {
        "role": "Investment Analyst",
        "expertise": [
          "Financial Statement Analysis",
          "Market Trends",
          "R&D Investment Strategy"
        ]
      },
      "job_to_be_done": "From the provided annual reports, analyze and compare revenue trends, R&D investments, and market positioning strategies."
    }
    

### Step 2: Build the Docker Image

Navigate to this directory (Challenge-1/B/) in your terminal and execute the build command. This will create a self-contained Docker image named round1b-solution with all dependencies and the pre-downloaded AI model.

*Note:* This step will take a few minutes the first time as it downloads the sentence-transformer model (~90MB). This is a one-time download.

bash
docker build --platform linux/amd64 -t round1b-solution .


### Step 3: Run the Solution

Execute the following command to run the analysis. This starts the container, maps your local input and output folders, and runs the script in an isolated environment with no network access.

bash
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none round1b-solution


### Step 4: Check the Output

Once the script finishes, the results will be saved in a single file located at: output/challenge1b_output.json.

---

## 🛠 Technical Approach

This solution uses a *semantic search* methodology to understand the contextual meaning of the documents in relation to the user's needs, rather than just matching keywords.

### 1. Text Extraction and Chunking

-   *Library:* PyMuPDF is used for its high speed and efficiency in extracting raw text content from all provided PDF documents.
-   *Strategy:* Documents are not treated as single blocks of text. They are segmented into smaller, coherent paragraphs or "chunks." This granular approach is critical for accurate semantic analysis, as it allows the model to evaluate specific ideas in isolation.

### 2. Semantic Embedding

-   *Model:* The core of the solution is the all-MiniLM-L6-v2 sentence-transformer model. This model was specifically chosen for its excellent balance of performance, speed, and size (<100MB), making it perfect for the CPU-only, offline environment.
-   *Process:* The model converts the user's query (a combination of their role and job-to-be-done) and every text chunk from the documents into high-dimensional numerical vectors, or "embeddings." In this vector space, texts with similar meanings are positioned closely together.

### 3. Relevance Scoring and Ranking

-   *Metric:* We use *Cosine Similarity* to calculate the relevance between the user's query vector and each paragraph's vector. This measures the angle between vectors, providing a highly accurate gauge of semantic alignment. A score closer to 1.0 indicates a stronger contextual match.
-   *Ranking:* All paragraphs from all documents are ranked globally based on their cosine similarity score. This ensures that the most relevant information across the entire document set rises to the top.

### 4. Output Generation

The top-scoring text chunks are selected and formatted into the required JSON structure, providing the user with a concise, prioritized, and highly relevant list of sections that directly address their query.
