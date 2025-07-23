import json
import os

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = {}
        self.default_config = {
            "aimbot": {
                "head_offset": -15,
                "smoothness": 2,
                "target_lock_threshold": 20,
                "capture_size": 450
            },
            "model": {
                "confidence_threshold": 0.5,
                "model_name": "yolov5s",
                "pretrained": True,
                "allowed_classes": [0]
            },
            "display": {
                "window_name": "Aimbot",
                "window_topmost": True,
                "show_fps": True,
                "show_target_info": True
            },
            "controls": {
                "activation_button": "right",
                "quit_key": "q"
            },
            "performance": {
                "device_idx": 0,
                "use_cuda": True
            }
        }
        
        self.init_config()
    
    def init_config(self):
        try:
            if not os.path.exists(self.config_path):
                print(f'Fichier {self.config_path} non trouvé, création avec la configuration par défaut...')
                self.create_default_config()
            self.load_config()
        except Exception as error:
            print(f'Erreur lors de l\'initialisation de la configuration: {error}')
            self.config = self.default_config
    
    def create_default_config(self):        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, indent=4, ensure_ascii=False)
            print(f'Configuration par défaut créée dans {self.config_path}')
        except Exception as error:
            print(f'Erreur lors de la création du fichier de configuration: {error}')
            raise error
    
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print('Configuration chargée avec succès')
        except Exception as error:
            print(f'Erreur lors du chargement de la configuration: {error}')
            print('Utilisation de la configuration par défaut')
            self.config = self.default_config
    
    def reload_config(self):
        self.load_config()
        return self.config
    
    def get(self, key, default_value=None):
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default_value
        
        return value
    
    def set(self, key, value):
        keys = key.split('.')
        current = self.config
        
        for i in range(len(keys) - 1):
            k = keys[i]
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print('Configuration sauvegardée')
            return True
        except Exception as error:
            print(f'Erreur lors de la sauvegarde: {error}')
            return False
    
    def get_all(self):
        return self.config.copy()
    
    def update(self, updates):
        self.config.update(updates)
        return self.save()