from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic : str) -> dir:
    state = {}
    # search agent working
    print("\n" "="*50)
    print("Step 1 - Search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state["search_results"] = search_result["messages"][-1].content
    print("\n search result", state['search_results'])

    #step 2 - reader agent
    print("\n")
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content: \n", state['scraped_content'])
