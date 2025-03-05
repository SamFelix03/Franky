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

@register_action("get-transaction-history")
def get_transaction_history(agent, **kwargs):
    """
    Action to get transaction history for a specific wallet address.
    This will be triggered when the user asks about wallet transactions.
    """
    # Check if wallet_address and chain_id are provided in kwargs
    wallet_address = kwargs.get("wallet_address")
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
    
    if not wallet_address:
        logger.error("\n❌ No wallet address provided")
        return False
    
    logger.info(f"\n🔍 FETCHING TRANSACTION HISTORY FOR {wallet_address} ON {network.upper()} (Chain ID: {chain_id})")
    print_h_bar()
    
    # Call the API through the connection
    result = agent.connection_manager.perform_action(
        connection_name="api_tools",
        action_name="get-transaction-history",
        params=[wallet_address, chain_id]
    )
    
    if result and "error" not in result:
        logger.info(f"\n✅ Transaction history fetched for {wallet_address} on {network}:")
        print_h_bar()
        
        # Format and display the transaction history
        if "events" in result:
            logger.info("\nTransaction Events:")
            for idx, event in enumerate(result["events"], 1):
                logger.info(f"\nTransaction #{idx}:")
                if isinstance(event, dict):
                    for key, value in event.items():
                        logger.info(f"  {key}: {value}")
                else:
                    logger.info(f"  {event}")
                
            logger.info(f"\nTotal Events Found: {len(result['events'])}")
        
        if "pagination" in result:
            logger.info("\nPagination Info:")
            for key, value in result["pagination"].items():
                logger.info(f"  {key}: {value}")
        
        print_h_bar()
        return result
    else:
        error = result.get("error", "Unknown error") if result else "Failed to get transaction history"
        logger.error(f"\n❌ {error}")
        print_h_bar()
        return False

def detect_transaction_history_query(text):
    """
    Detect if a user query is asking about transaction history.
    Returns a tuple of (wallet_address, network) if found, otherwise (None, None).
    """
    # Patterns to match transaction history queries
    tx_patterns = [
        r"(?:what(?:'s| are) the|show|get|fetch|check) (?:transactions|tx|history)",
        r"transaction (?:history|list)",
        r"wallet (?:history|transactions)",
        r"what (?:happened|occurred) in (?:wallet|address)"
    ]
    
    # Pattern to match Ethereum addresses
    eth_address_pattern = r"0x[a-fA-F0-9]{40}"
    
    # Check if any transaction pattern matches
    is_tx_query = any(re.search(pattern, text.lower()) for pattern in tx_patterns)
    
    if not is_tx_query:
        return None, None
    
    # Try to extract wallet address
    wallet_match = re.search(eth_address_pattern, text)
    wallet_address = wallet_match.group(0) if wallet_match else None
    
    # Try to extract network
    network = None
    for net in NETWORK_TO_CHAIN_ID.keys():
        if net.lower() in text.lower():
            network = net
            break
    
    # Default to Ethereum if no specific network mentioned
    if not network:
        network = "ethereum"
    
    return wallet_address, network 