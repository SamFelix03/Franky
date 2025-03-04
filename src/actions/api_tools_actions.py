import logging
import re
from src.action_handler import register_action
from src.helpers import print_h_bar

logger = logging.getLogger("actions.api_tools_actions")

# Dictionary mapping network names to chain IDs
NETWORK_TO_CHAIN_ID = {
    "ethereum": "1",
    "eth": "1",
    "mainnet": "1",
    "binance": "56",
    "bsc": "56",
    "polygon": "137",
    "matic": "137",
    "avalanche": "43114",
    "avax": "43114",
    "arbitrum": "42161",
    "optimism": "10",
    "base": "8453",
    "fantom": "250",
    "ftm": "250"
}

@register_action("get-gas-price")
def get_gas_price(agent, **kwargs):
    """
    Action to get gas price for a specific blockchain network.
    This will be triggered when the user asks about gas prices.
    """
    # Check if chain_id is provided in kwargs
    chain_id = kwargs.get("chain_id")
    network = kwargs.get("network")
    
    # If network name is provided, convert to chain_id
    if network and not chain_id:
        network = network.lower()
        chain_id = NETWORK_TO_CHAIN_ID.get(network)
        if not chain_id:
            logger.error(f"\n❌ Unknown network: {network}")
            return False
    
    # If no chain_id or network provided, default to Ethereum
    if not chain_id:
        chain_id = "1"  # Default to Ethereum
        network = "Ethereum"
    else:
        # Find network name from chain ID for display
        for net, cid in NETWORK_TO_CHAIN_ID.items():
            if cid == chain_id:
                network = net.capitalize()
                break
        else:
            network = f"Chain ID {chain_id}"
    
    logger.info(f"\n🔍 FETCHING GAS PRICE FOR {network.upper()} (Chain ID: {chain_id})")
    print_h_bar()
    
    # Call the API through the connection
    result = agent.connection_manager.perform_action(
        connection_name="api_tools",
        action_name="get-gas-price",
        params=[chain_id]
    )
    
    if result and "error" not in result:
        logger.info(f"\n✅ Current gas prices for {network}:")
        
        # Format and display the gas price information
        if "low" in result:
            logger.info(f"Low: {result['low']} Gwei")
        if "standard" in result:
            logger.info(f"Standard: {result['standard']} Gwei")
        if "fast" in result:
            logger.info(f"Fast: {result['fast']} Gwei")
        if "instant" in result:
            logger.info(f"Instant: {result['instant']} Gwei")
        if "baseFee" in result:
            logger.info(f"Base Fee: {result['baseFee']} Gwei")
            
        return result
    else:
        error = result.get("error", "Unknown error") if result else "Failed to get gas price"
        logger.error(f"\n❌ {error}")
        return False

def detect_gas_price_query(text):
    """
    Detect if a user query is asking about gas prices.
    Returns the network name if found, otherwise None.
    """
    # Patterns to match gas price queries
    gas_patterns = [
        r"(?:what(?:'s| is) the|current|check|get|show) (?:gas|gas price|gas fee)",
        r"gas (?:price|fee|cost)",
        r"how much (?:gas|fee)",
        r"transaction fee",
        r"network fee"
    ]
    
    # Check if any gas pattern matches
    is_gas_query = any(re.search(pattern, text.lower()) for pattern in gas_patterns)
    
    if not is_gas_query:
        return None
    
    # If it's a gas query, try to extract the network
    for network in NETWORK_TO_CHAIN_ID.keys():
        if network.lower() in text.lower():
            return network
    
    # Default to Ethereum if no specific network mentioned
    return "ethereum" 