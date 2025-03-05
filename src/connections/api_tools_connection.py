import logging
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from src.connections.base_connection import BaseConnection, Action, ActionParameter
import json

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
            ),
            "get-transaction-history": Action(
                name="get-transaction-history",
                parameters=[
                    ActionParameter("wallet_address", True, str, "Wallet address to fetch transactions for"),
                    ActionParameter("chain_id", True, str, "Chain ID (e.g., 1 for Ethereum, 56 for BSC)")
                ],
                description="Get transaction history for a specific wallet address"
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

    def get_transaction_history(self, wallet_address: str, chain_id: str, **kwargs) -> Dict[str, Any]:
        """Get transaction history for a specific wallet address"""
        try:
            api_url = f"https://api.1inch.dev/history/v2.0/history/{wallet_address}/events"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            params = {
                "chainId": chain_id,
                "limit": "1"  # Limit to 1 transaction
            }
            
            # Log request details
            logger.info("\n📡 Transaction History API Request:")
            logger.info(f"URL: {api_url}")
            logger.info("Headers: Authorization: Bearer ***[API_KEY_HIDDEN]***")
            logger.info(f"Parameters: {params}")
            
            response = requests.get(api_url, headers=headers, params=params)
            
            # Log response details
            logger.info("\n📥 API Response Details:")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                error_msg = f"Transaction history request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Log the raw response data
            logger.info("\n📦 Raw Response Data:")
            response_data = response.json()
            logger.info(json.dumps(response_data, indent=2))
            logger.info("\n" + "-" * 80 + "\n")
            
            return response_data
            
        except Exception as e:
            error_msg = f"Error getting transaction history: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Perform a registered action with the given parameters"""
        if action_name == "get-gas-price":
            return self.get_gas_price(**kwargs)
        elif action_name == "get-transaction-history":
            return self.get_transaction_history(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action_name}") 