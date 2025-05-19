import re
import argparse
import pandas as pd
import os
from dotenv import load_dotenv
# Use langchain-openai for LLMs per deprecation guidance
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, Tool
from tools import list_pathway_drugs, get_drug_info

# Step 0: Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set. Please add it to your environment or .env file.")

# Step 1: Define a safe wrapper to clean pathway IDs and prefix for KEGG API

def list_pathway_drugs_clean(pathway_input: str):
    """
    Cleans input to extract the KEGG pathway ID (e.g., hsa04012) and prefixes with 'path:'
    before calling the tool.
    """
    # Remove any surrounding text (like parentheses) and whitespace
    cleaned = pathway_input.strip()
    # Attempt to extract the core ID (3 letters + 5 digits)
    match = re.search(r"[a-z]{3}\d{5}", cleaned, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not parse KEGG pathway ID from input: {pathway_input}")
    pid = match.group(0).lower()
    # Prefix with 'path:' as required by the KEGG tool
    kegg_id = f"path:{pid}"
    return list_pathway_drugs(kegg_id)

# Step 2: Wrap your existing functions as LangChain Tools
pathway_tool = Tool(
    name="list_pathway_drugs",
    func=list_pathway_drugs_clean,
    description="Given a KEGG pathway ID (e.g., hsa04012), returns a list of drug IDs associated with that pathway."
)

drug_info_tool = Tool(
    name="get_drug_info",
    func=get_drug_info,
    description="Given a drug ID, returns detailed information about the drug."
)

tools = [pathway_tool, drug_info_tool]

# Step 3: Initialize the LLM (explicitly passing the API key)
llm = OpenAI(openai_api_key=api_key, temperature=0)

# Step 4: Create an agent that can call your tools and plan steps
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

# Step 5a: Define a helper to interact with your agent

def ask_agent(prompt: str):
    """
    Ask a free-text question and let the agent choose tools.
    """
    return agent.run(prompt)

# Step 5b: Batch-process pathways from a CSV

def batch_process_csv(csv_path: str):
    """
    Reads a CSV with a 'pathway_id' column and uses the tools to build a summary.
    """
    df = pd.read_csv(csv_path)
    results = []
    for raw_id in df['pathway_id']:
        try:
            drugs = list_pathway_drugs_clean(raw_id)
            details = [get_drug_info(d) for d in drugs]
            results.append({
                'pathway_id': raw_id,
                'drug_ids': drugs,
                'drug_details': details
            })
        except Exception as e:
            results.append({
                'pathway_id': raw_id,
                'error': str(e)
            })
    return pd.DataFrame(results)

# Step 6: Command-line interface with default CSV

def main():
    parser = argparse.ArgumentParser(description="Run KEGG agent or batch CSV processing")
    parser.add_argument('--csv', type=str, help="Path to input CSV with 'pathway_id' column")
    parser.add_argument('--prompt', type=str, help="Free-text prompt for the agent")
    args = parser.parse_args()

    csv_path = args.csv or 'pathways.csv'
    if args.prompt:
        print(ask_agent(args.prompt))
    elif os.path.isfile(csv_path):
        df_out = batch_process_csv(csv_path)
        print(df_out.to_string(index=False))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
