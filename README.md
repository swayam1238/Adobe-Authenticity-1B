# Adobe-Authenticity-1B
Round 1B: Persona-Driven Document Intelligence
This solution addresses the "Connect What Matters" challenge by acting as an intelligent document analyst. It processes a collection of PDF documents and extracts the most relevant sections based on a specific user persona and their stated "job-to-be-done."

How to Build and Run
Prerequisites: Docker must be installed and running on your system.

Step 1: Set Up Inputs
Add Documents: Place all the PDF documents you want to analyze into the input/documents/ directory.

Define Persona: Open the input/persona.json file and edit it to define the user role and the task they need to accomplish.

Example persona.json for a researcher:

{
  "persona": {
    "role": "PhD Researcher in Computational Biology",
    "expertise": [
      "Graph Neural Networks",
      "Drug Discovery"
    ]
  },
  "job_to_be_done": "Prepare a literature review focusing on methodologies, datasets, and performance benchmarks."
}

Step 2: Build the Docker Image
Navigate to this directory (Challenge-1/1B/) in your terminal and run the build command. This will create a self-contained Docker image with all dependencies and the pre-downloaded AI model.

Note: This step will take a few minutes the first time as it downloads the sentence-transformer model (~90MB).

docker build --platform linux/amd64 -t round1b-solution .

Step 3: Run the Solution
Execute the following command to run the analysis. This command starts the container, maps your local input and output folders, and runs the script in an isolated environment with no network access.

docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none round1b-solution

Step 4: Check the Output
Once the script finishes, the results will be saved in a single file: output/challenge1b_output.json.

Technical Approach
This solution uses a semantic search methodology to understand the context of the documents in relation to the user's needs.

Text Extraction: The PyMuPDF library is used to efficiently parse and extract text content from all provided PDF documents. The text is broken down into smaller, manageable paragraphs.

Semantic Embedding: The core of the solution is the all-MiniLM-L6-v2 sentence-transformer model. This is a lightweight but powerful model (under 100MB) that runs efficiently on a CPU. It converts the persona's query (role + job-to-be-done) and every paragraph from the documents into numerical vectors (embeddings) that represent their semantic meaning.

Relevance Scoring: The relevance of each paragraph is determined by calculating the cosine similarity between its vector and the persona's query vector. A higher score indicates a stronger contextual match.

Ranking and Output: All paragraphs from all documents are ranked based on their relevance scores. The top-scoring sections are then formatted and written to the final JSON output file, providing a prioritized list of the most important information for the user.
