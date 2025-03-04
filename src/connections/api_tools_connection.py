import logging
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from src.connections.base_connection import BaseConnection, Action, ActionParameter

logger = logging.getLogger("connections.api_tools_connection")

class APIToolsConnectionError(Exception):
    """Base exception for API Tools connection errors"""
    pass

class APIToolsConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", os.getenv("ONEINCH_API_KEY", ""))

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API Tools configuration from JSON"""
        # API key is optional in config as it can be in .env
        return config

    def register_actions(self) -> None:
        """Register available API Tools actions"""
        self.actions = {
            "get-gas-price": Action(
                name="get-gas-price",
                parameters=[
                    ActionParameter("chain_id", True, str, "Chain ID (e.g., 1 for Ethereum, 56 for BSC)")
                ],
                description="Get current gas price for a specific blockchain network"
            )
        }

    def configure(self) -> bool:
        """Configure API Tools connection"""
        logger.info("\n🔧 API TOOLS CONFIGURATION")
        
        if self.is_configured(verbose=False):
            logger.info("\nAPI Tools is already configured.")
            reconfigure = input("Do you want to reconfigure? (y/n): ")
            if reconfigure.lower() != 'y':
                return True
        
        api_key = input("\nEnter your 1inch API key (leave blank to use existing): ")
        
        if api_key:
            # Save to .env file
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write('')
            
            set_key('.env', 'ONEINCH_API_KEY', api_key)
            self.api_key = api_key
            logger.info("\n✅ API key saved successfully!")
        
        return True

    def is_configured(self, verbose=False) -> bool:
        """Check if API Tools is configured"""
        load_dotenv()
        api_key = self.api_key or os.getenv("ONEINCH_API_KEY", "")
        
        if not api_key and verbose:
            logger.error("\n❌ API key not found. Please configure API Tools.")
            return False
        
        return bool(api_key)

    def get_gas_price(self, chain_id: str, **kwargs) -> Dict[str, Any]:
        """Get current gas price for a specific blockchain network"""
        try:
            api_url = f"https://api.1inch.dev/gas-price/v1.5/{chain_id}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(api_url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"Gas price request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            return response.json()
            
        except Exception as e:
            error_msg = f"Error getting gas price: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Perform a registered action with the given parameters"""
        if action_name == "get-gas-price":
            return self.get_gas_price(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action_name}") 