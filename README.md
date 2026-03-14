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

L'application nécessite un compte Cloudinary pour le stockage des images. Configurez les variables suivantes dans votre fichier `.env` :

- `CLOUDINARY_CLOUD_NAME` : Nom de votre cloud Cloudinary
- `CLOUDINARY_API_KEY` : Clé d'API Cloudinary
- `CLOUDINARY_API_SECRET` : Clé secrète Cloudinary

## Structure des données

Les galeries sont stockées dans `data/galleries.json` avec la structure suivante :
```json
{
  "gallery_id": {
    "title": "Titre de la galerie",
    "date": "YYYY-MM-DD",
    "description": "Description de l'étape",
    "images": [
      {
        "image_url": "URL de l'image",
        "thumbnail_url": "URL de la miniature",
        "filename": "nom_du_fichier.jpg",
        "public_id": "ID_public_cloudinary"
      }
    ]
  }
}



## Technologies utilisées

- Flask (Backend)
- Cloudinary (Stockage d'images)
- HTML/CSS/JavaScript (Frontend)
- Lightbox.js (Galerie photos)

## Licence

MIT
