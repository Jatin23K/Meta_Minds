from crewai import Agent
from langchain_openai import ChatOpenAI
import logging

def create_agents():
    """Defines and returns the AI agents for the CrewAI workflow.

    These agents are responsible for specific roles in the data analysis process.

    Returns:
        tuple: A tuple containing the schema sleuth and question genius agents.
    """
    logging.info("Creating CrewAI agents...")
    
    # Configure GPT-4 LLM for all agents
    gpt4_llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7
    )
    
    schema_sleuth = Agent(
        role="Schema Sleuth",
        goal="Analyze data structure and describe dataset schema",
        backstory=(
            "You are an expert data detective, skilled at quickly understanding "
            "the structure and metadata of any dataset. Your job is to identify "
            "the number of rows, columns, data types, and provide a high-level "
            "overview of the dataset's composition."
        ),
        verbose=True, # Keep verbose for seeing agent thought process
        allow_delegation=False, # Agents in this simple setup don't delegate to each other
        llm=gpt4_llm  # Use GPT-4 explicitly
    )
    # Refined backstory for clarity and emphasis on focusing on the provided data
    question_genius = Agent(
        role="Curious Catalyst",
        goal="Generate insightful, analytical questions based *strictly* on the provided dataset(s)",
        backstory=(
            "You are a brilliant data analyst with a knack for asking the right questions "
            "to uncover hidden patterns, trends, anomalies, and relationships within a dataset. "
            "Your key strength is generating diverse and meaningful questions "
            "that prompt deeper analysis, but you *strictly* adhere to the information "
            "available in the dataset(s) provided to you. You never reference external data or knowledge."
        ),
        verbose=True, # Keep verbose
        allow_delegation=False, # Agents don't delegate
        llm=gpt4_llm  # Use GPT-4 explicitly
    )
    logging.info("CrewAI agents created.")
    return schema_sleuth, question_genius