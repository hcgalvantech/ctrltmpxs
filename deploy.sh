#!/bin/bash
# deploy.sh

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno para Netlify
export FLASK_APP=main.py
export FLASK_ENV=production

# Configuraciones específicas de Netlify
netlify_toml_content=$(cat <<EOL
[build]
  command = "pip install -r requirements.txt && flask db upgrade"
  functions = "netlify/functions"
  publish = "."

[build.environment]
  PYTHON_VERSION = "3.9"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
EOL
)

echo "$netlify_toml_content" > netlify.toml

# Preparar para despliegue
echo "Deployment preparado para Netlify"