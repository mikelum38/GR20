import os
import sys
from flask import Flask

# Ajouter le répertoire parent au path pour importer les modules locaux
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer l'application Flask depuis le répertoire parent
from app import app

# Handler pour Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)
