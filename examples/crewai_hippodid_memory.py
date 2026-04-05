"""
CrewAI + HippoDid: Agents with persistent character identity.

Each agent loads its character identity at task start using
strategy="task_focused" for work agents.

Requirements: pip install hippodid crewai
"""

from crewai import Agent, Task, Crew

from hippodid import HippoDid


def make_hippodid_agent(
    hd: HippoDid,
    character_id: str,
    role: str,
    goal: str,
    task_query: str,
) -> Agent:
    """Create a CrewAI agent with HippoDid character identity."""
    context = hd.assemble_context(
        character_id,
        task_query,
        strategy="task_focused",
        max_context_tokens=3000,
    )

    return Agent(
        role=role,
        goal=goal,
        backstory=context.formatted_prompt,
        verbose=True,
    )


if __name__ == "__main__":
    hd = HippoDid(api_key="hd_your_key")

    # Create agents with HippoDid-backed identities
    researcher = make_hippodid_agent(
        hd,
        character_id="researcher-char-uuid",
        role="Senior Researcher",
        goal="Find and synthesize information",
        task_query="research and analysis tasks",
    )

    writer = make_hippodid_agent(
        hd,
        character_id="writer-char-uuid",
        role="Technical Writer",
        goal="Write clear, concise documentation",
        task_query="writing and documentation tasks",
    )

    # Define tasks
    research_task = Task(
        description="Research the latest trends in AI agent frameworks",
        expected_output="A summary of top 5 AI agent frameworks with pros and cons",
        agent=researcher,
    )

    writing_task = Task(
        description="Write a blog post based on the research findings",
        expected_output="A 500-word blog post about AI agent frameworks",
        agent=writer,
    )

    # Run the crew
    crew = Crew(agents=[researcher, writer], tasks=[research_task, writing_task], verbose=True)
    result = crew.kickoff()
    print(result)

    # Save task outcomes back as memories
    hd.add_memory("researcher-char-uuid", f"Completed research task: {research_task.description}")
    hd.add_memory("writer-char-uuid", f"Completed writing task: {writing_task.description}")
