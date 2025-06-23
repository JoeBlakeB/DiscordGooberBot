# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

"""
Manages API keys and other secrets in a TOML file
"""

import os
import tomllib
import traceback

KEYS_FILE_PATH = os.path.join(os.environ.get("DATA_DIR", os.path.dirname(os.path.dirname(__file__))), "keys.toml")


class KeyManager:
    _instance = None
    _keys = None
    _missing = []
    _missingTraces = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._keys is None:
            if os.path.exists(KEYS_FILE_PATH):
                with open(KEYS_FILE_PATH, "rb") as f:
                    self._keys = tomllib.load(f)
            else:
                self._keys = {}

    def get(self, name, default=None):
        """Get the value of a key from the keys.toml file.
        Records if they key is not in the file, this should be called during app initialisation.

        Args:
            name (str): The name of the key to retrieve.

        Returns:
            str: The value of the key, or None if the key is not found.
        """
        if self._keys.get(name, None):
            return self._keys[name]
        elif default is not None:
            return default
        else:
            self._missing.append(name)
            self._missingTraces.append(traceback.format_stack()[-2].strip())
            return None

    def reportMissingKeys(self):
        """Call to report missing keys, saving blanks to the keys.toml file.
        Call after app initialisation, but before keys are used."""
        if self._missing:
            if not os.path.exists(os.path.dirname(KEYS_FILE_PATH)):
                os.makedirs(os.path.dirname(KEYS_FILE_PATH), exist_ok=True)
            with open(KEYS_FILE_PATH, "w") as f:
                self._keys.update({k: "" for k in self._missing})
                for key, value in self._keys.items():
                    f.write(f"{key} = \"{value}\"\n")

            for trace in self._missingTraces:
                print(trace)

            raise Exception(f"Missing API Keys: \"{"\", \"".join(self._missing)}\", please check the {KEYS_FILE_PATH} file.")
