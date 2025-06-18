import os
import getpass
import json
from pathlib import Path

class APIKeyManager:
    """
    Manages OpenAI API key with multiple fallback methods:
    1. Environment variable (OPENAI_API_KEY)
    2. .env file
    3. Config file (.scraper_config.json)
    4. Prompt user and optionally save
    """
    
    def __init__(self):
        self.config_file = Path.home() / '.scraper_config.json'
        self.env_file = Path('.env')
        
    def get_api_key(self) -> str:
        """Get API key using multiple fallback methods"""
        
        # Method 1: Environment variable
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            print("✅ Using API key from environment variable")
            return api_key
        
        # Method 2: .env file
        api_key = self._load_from_env_file()
        if api_key:
            print("✅ Using API key from .env file")
            return api_key
        
        # Method 3: Config file
        api_key = self._load_from_config()
        if api_key:
            print("✅ Using API key from config file")
            return api_key
        
        # Method 4: Prompt user
        print("🔑 OpenAI API key not found. Let's set it up!")
        return self._prompt_and_save()
    
    def _load_from_env_file(self) -> str:
        """Load API key from .env file"""
        if not self.env_file.exists():
            return None
            
        try:
            with open(self.env_file, 'r') as f:
                content = f.read()
                # Look for OPENAI_API_KEY= and extract the value
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip('\'"')
                        # Handle multiline keys by reading next lines if needed
                        if not api_key.startswith('sk-'):
                            # Key might continue on next lines
                            lines = content.split('\n')
                            idx = lines.index(line)
                            full_key = api_key
                            for i in range(idx + 1, len(lines)):
                                next_line = lines[i].strip()
                                if next_line and not next_line.startswith('#'):
                                    full_key += next_line
                                if full_key.startswith('sk-') and len(full_key) > 50:
                                    break
                            api_key = full_key
                        
                        if api_key.startswith('sk-'):
                            return api_key
        except Exception as e:
            print(f"Warning: Could not read .env file: {e}")
        return None
    
    def _load_from_config(self) -> str:
        """Load API key from config file"""
        if not self.config_file.exists():
            return None
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                api_key = config.get('openai_api_key')
                if api_key and api_key.startswith('sk-'):
                    return api_key
        except Exception as e:
            print(f"Warning: Could not read config file: {e}")
        return None
    
    def _prompt_and_save(self) -> str:
        """Prompt user for API key and offer to save it"""
        print("\n" + "="*50)
        print("🔑 OpenAI API Key Setup")
        print("="*50)
        print("You need an OpenAI API key to use this scraper.")
        print("Get one at: https://platform.openai.com/api-keys")
        print()
        
        api_key = getpass.getpass("Enter your OpenAI API key (sk-...): ").strip()
        
        if not api_key.startswith('sk-'):
            print("❌ Invalid API key format. Should start with 'sk-'")
            raise ValueError("Invalid API key format")
        
        # Ask if user wants to save it
        print("\n💾 Save API key for future use?")
        print("1. Save to .env file (recommended)")
        print("2. Save to config file (~/.scraper_config.json)")
        print("3. Don't save (prompt every time)")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == '1':
            self._save_to_env_file(api_key)
            print("✅ API key saved to .env file")
        elif choice == '2':
            self._save_to_config_file(api_key)
            print("✅ API key saved to config file")
        else:
            print("⚠️  API key not saved - you'll need to enter it each time")
        
        return api_key
    
    def _save_to_env_file(self, api_key: str):
        """Save API key to .env file"""
        try:
            with open(self.env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
                f.write(f"# OpenAI API key for Universal Blog Scraper\n")
        except Exception as e:
            print(f"❌ Could not save to .env file: {e}")
    
    def _save_to_config_file(self, api_key: str):
        """Save API key to config file"""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['openai_api_key'] = api_key
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"❌ Could not save to config file: {e}")


def get_openai_api_key() -> str:
    """Simple function to get API key - use this in other scripts"""
    manager = APIKeyManager()
    return manager.get_api_key()


if __name__ == "__main__":
    # Test the API key manager
    print("🧪 Testing API Key Manager")
    try:
        api_key = get_openai_api_key()
        print(f"✅ API key retrieved successfully (length: {len(api_key)})")
        print(f"✅ Valid format: {api_key.startswith('sk-')}")
    except Exception as e:
        print(f"❌ Error: {e}") 