import logging
from src.action_handler import register_action
from src.helpers import print_h_bar
from src.actions.api_tools_actions import detect_gas_price_query

logger = logging.getLogger("actions.ollama_actions")

@register_action("ollama-chat")
def ollama_chat(agent, **kwargs):
    """
    Action to chat with Ollama model using the agent's personality.
    """
    logger.info(f"\n💬 STARTING OLLAMA CHAT SESSION AS {agent.name}")
    print_h_bar()
    logger.info(f"You are now chatting with {agent.name}")
    logger.info("Type 'exit' or 'quit' to end the chat session.")
    print_h_bar()
    
    # Create a system prompt from the agent's personality
    system_prompt = agent._construct_system_prompt()
    
    # Display personality info
    logger.info(f"\n🧠 Personality: {agent.name}")
    if hasattr(agent, 'traits') and agent.traits:
        logger.info(f"Traits: {', '.join(agent.traits)}")
    if hasattr(agent, 'bio') and agent.bio:
        logger.info(f"Bio: {agent.bio[0]}")
    print_h_bar()
    
    # Initialize chat with a strong personality directive
    personality_directive = f"""
You are {agent.name}. You must always stay in character and respond exactly as {agent.name} would.
Never break character or refer to yourself as 'Assistant' or any other name.
Your name is {agent.name} and you should sign your responses as {agent.name} if appropriate.

You have access to special tools that can provide real-time information. When a user asks about:
1. Gas prices or transaction fees on blockchain networks - I will fetch the current gas prices for you.

Only use these tools when directly relevant to the user's query.
"""
    
    # Combine the personality directive with the system prompt
    combined_system_prompt = personality_directive + "\n\n" + system_prompt
    
    chat_history = []
    
    # Add system message to set the personality
    chat_history.append({"role": "system", "content": combined_system_prompt})
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            logger.info("\n👋 Ending chat session...")
            break
        
        # Add user message to history
        chat_history.append({"role": "user", "content": user_input})
        
        # Check if this is a gas price query
        network = detect_gas_price_query(user_input)
        
        if network and "api_tools" in agent.connection_manager.connections:
            # This is a gas price query and we have the API tools connection
            try:
                # Execute the gas price action
                from src.action_handler import execute_action
                gas_result = execute_action(agent, "get-gas-price", network=network)
                
                if gas_result and not isinstance(gas_result, bool):
                    # Format the gas price information in a clearer way
                    gas_info = "EXACT CURRENT GAS PRICES (use these EXACT values in your response):\n"
                    
                    # Store the raw values for direct insertion
                    formatted_values = {}
                    
                    # Handle the nested dictionary format from 1inch API
                    if "low" in gas_result:
                        if isinstance(gas_result['low'], dict):
                            # Format the nested dictionary values
                            low_details = []
                            for key, value in gas_result['low'].items():
                                low_details.append(f"{key}: {value}")
                            low_value = f"{{{', '.join(low_details)}}}"
                        else:
                            low_value = str(gas_result['low'])
                        formatted_values["low"] = low_value
                        gas_info += f"- Low: {low_value} Gwei\n"
                    
                    if "standard" in gas_result:
                        if isinstance(gas_result['standard'], dict):
                            standard_details = []
                            for key, value in gas_result['standard'].items():
                                standard_details.append(f"{key}: {value}")
                            standard_value = f"{{{', '.join(standard_details)}}}"
                        else:
                            standard_value = str(gas_result['standard'])
                        formatted_values["standard"] = standard_value
                        gas_info += f"- Standard: {standard_value} Gwei\n"
                    
                    if "fast" in gas_result:
                        if isinstance(gas_result['fast'], dict):
                            fast_details = []
                            for key, value in gas_result['fast'].items():
                                fast_details.append(f"{key}: {value}")
                            fast_value = f"{{{', '.join(fast_details)}}}"
                        else:
                            fast_value = str(gas_result['fast'])
                        formatted_values["fast"] = fast_value
                        gas_info += f"- Fast: {fast_value} Gwei\n"
                    
                    if "instant" in gas_result:
                        if isinstance(gas_result['instant'], dict):
                            instant_details = []
                            for key, value in gas_result['instant'].items():
                                instant_details.append(f"{key}: {value}")
                            instant_value = f"{{{', '.join(instant_details)}}}"
                        else:
                            instant_value = str(gas_result['instant'])
                        formatted_values["instant"] = instant_value
                        gas_info += f"- Instant: {instant_value} Gwei\n"
                    
                    if "baseFee" in gas_result:
                        base_fee_value = str(gas_result['baseFee'])
                        formatted_values["baseFee"] = base_fee_value
                        gas_info += f"- Base Fee: {base_fee_value} Gwei\n"
                    
                    # Create a template response that the model can use
                    template_response = f"Here are the current gas prices for {network.capitalize()}:\n"
                    for key, value in formatted_values.items():
                        if key == "baseFee":
                            template_response += f"- Base Fee: {value} Gwei\n"
                        else:
                            template_response += f"- {key.capitalize()}: {value} Gwei\n"
                    
                    # Modify the user's query to include the gas price information
                    modified_user_input = f"{user_input}\n\n{gas_info}\n\nYou MUST use these EXACT values in your response. DO NOT convert, calculate, or modify these values in any way."
                    
                    # Replace the last user message with the modified one
                    chat_history[-1]["content"] = modified_user_input
                    
                    # Add a strong instruction as a system message with the template
                    chat_history.append({
                        "role": "system", 
                        "content": f"""CRITICAL INSTRUCTION: The user has asked about gas prices on {network.capitalize()}. 
I have fetched the real data above. Your response MUST include these EXACT gas price values.
DO NOT calculate, convert, or modify these values in any way.
DO NOT make up different values.
If you're unsure how to format the response, use this template:
{template_response}
"""
                    })
            except Exception as e:
                logger.error(f"\n❌ Error using gas price tool: {e}")
        
        # Get response from Ollama
        response = agent.connection_manager.perform_action(
            connection_name="ollama",
            action_name="chat",
            params=[chat_history]
        )
        
        if response:
            # Check if this was a gas price query and if the response contains the gas price data
            if network and "api_tools" in agent.connection_manager.connections:
                # Check if the response contains the gas price data
                contains_gas_data = False
                
                # Look for key indicators that the model used the gas price data
                if "baseFee" in response or "Base Fee" in response:
                    contains_gas_data = True
                
                for key in formatted_values.keys() if 'formatted_values' in locals() else []:
                    if key in response or key.capitalize() in response:
                        contains_gas_data = True
                
                # If the model didn't use the gas price data, append a correction
                if not contains_gas_data and 'template_response' in locals():
                    logger.info("\n⚠️ Model didn't use gas price data. Adding correction...")
                    
                    # Create a corrected response that includes the agent's style but with the correct data
                    corrected_response = f"{response}\n\nActually, let me correct myself with the exact data:\n\n{template_response}"
                    
                    # Update the response
                    response = corrected_response
            
            # Print the response
            logger.info(f"\n{agent.name}: {response}")
            
            # Add assistant response to history
            chat_history.append({"role": "assistant", "content": response})
        else:
            logger.error("\n❌ Failed to get response from Ollama")
    
    return True 