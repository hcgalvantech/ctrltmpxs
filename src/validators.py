import re
from typing import Dict, Any, Optional

class InputValidator:
    @staticmethod
    def validate_dni(dni: str) -> Dict[str, Any]:
        """
        Valida el DNI con reglas específicas
        """
        # Eliminar espacios en blanco
        dni = dni.strip()

        # Verificaciones
        validations = {
            'required': len(dni) > 0,
            'numeric': dni.isdigit(),
            'length': 7 <= len(dni) <= 8
        }

        # Si todas las validaciones son True
        if all(validations.values()):
            return {
                'valid': True, 
                'dni': int(dni)
            }
        
        # Generar mensaje de error detallado
        error_messages = [
            "DNI es obligatorio" if not validations['required'] else None,
            "DNI debe contener solo números" if not validations['numeric'] else None,
            "DNI debe tener entre 7 y 8 dígitos" if not validations['length'] else None
        ]
        
        return {
            'valid': False,
            'errors': [msg for msg in error_messages if msg is not None]
        }

    @staticmethod
    def validate_github_link(link: str) -> Optional[str]:
        """
        Valida que el enlace sea de GitHub
        """
        github_pattern = r'^https?://(?:www\.)?github\.com/[\w-]+/[\w-]+/?$'
        
        if re.match(github_pattern, link):
            return link
        
        return None