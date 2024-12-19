# GR20 Gallery App

Application web pour partager et gérer des photos du GR20 en Corse.

## Fonctionnalités

- Création et gestion de galeries photos
- Upload d'images avec génération automatique de miniatures
- Stockage des images sur Supabase
- Lecteur audio intégré avec musique d'ambiance corse
- Interface responsive et moderne

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/mikelum38/GR20.git
cd GR20
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
- Copier `.env.example` vers `.env`
- Remplir les variables avec vos propres valeurs

4. Lancer l'application :
```bash
python app.py
```

## Configuration

L'application nécessite un compte Supabase pour le stockage des images. Configurez les variables suivantes dans votre fichier `.env` :

- `SUPABASE_URL` : URL de votre projet Supabase
- `SUPABASE_KEY` : Clé d'API Supabase
- `SUPABASE_BUCKET_NAME` : Nom du bucket pour le stockage des images

## Technologies utilisées

- Flask (Backend)
- Supabase (Stockage)
- HTML/CSS/JavaScript (Frontend)
- Lightbox.js (Galerie photos)

## Licence

MIT
