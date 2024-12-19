from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from datetime import datetime
from PIL import Image
import uuid
from supabase_config import storage

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
THUMBNAIL_SIZE = (400, 300)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'galleries.json')

# Créer le dossier data s'il n'existe pas
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_gallery_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_gallery_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            date_obj = datetime.strptime(date_str, '%d %B %Y')
        except ValueError:
            return date_str
    return date_obj.strftime('%d %B %Y')

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B %Y')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%d %B %Y').strftime('%d %B %Y')
        except ValueError:
            return date_str

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/galleries')
def galleries():
    galleries_data = load_gallery_data()
    formatted_galleries = []
    
    for gallery_id, gallery in galleries_data.items():
        formatted_gallery = gallery.copy()
        formatted_gallery['id'] = gallery_id
        
        # Format the date
        if 'date' in formatted_gallery:
            formatted_gallery['date'] = format_date(formatted_gallery['date'])
            
        # Get cover image
        if formatted_gallery.get('images'):
            formatted_gallery['cover_image'] = formatted_gallery['images'][0]['thumbnail_url']
        else:
            formatted_gallery['cover_image'] = None
            
        formatted_galleries.append(formatted_gallery)
    
    # Sort galleries by date (most recent first)
    formatted_galleries.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template('gallery.html', galleries=formatted_galleries)

@app.route('/gallery/<gallery_id>')
def gallery(gallery_id):
    galleries = load_gallery_data()
    if gallery_id not in galleries:
        flash('Galerie introuvable', 'error')
        return redirect(url_for('galleries'))
    
    gallery = galleries[gallery_id]
    gallery['date'] = format_date(gallery['date'])
    return render_template('gallery_detail.html', gallery=gallery, gallery_id=gallery_id)

@app.route('/create_gallery', methods=['GET', 'POST'])
def create_gallery():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date = request.form.get('date')
        
        if not title or not date:
            flash('Le titre et la date sont requis', 'error')
            return redirect(url_for('create_gallery'))
        
        gallery_id = str(uuid.uuid4())
        galleries = load_gallery_data()
        
        galleries[gallery_id] = {
            'title': title,
            'description': description,
            'date': date,
            'images': []
        }
        
        save_gallery_data(galleries)
        flash('Galerie créée avec succès', 'success')
        return redirect(url_for('gallery', gallery_id=gallery_id))
    
    return render_template('create_gallery.html')

@app.route('/gallery/<gallery_id>/upload', methods=['POST'])
def upload_photos(gallery_id):
    if 'photos' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('gallery', gallery_id=gallery_id))
    
    galleries = load_gallery_data()
    if gallery_id not in galleries:
        flash('Galerie introuvable', 'error')
        return redirect(url_for('galleries'))
    
    gallery = galleries[gallery_id]
    files = request.files.getlist('photos')
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        for file in files:
            if file and allowed_file(file.filename):
                filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                temp_path = os.path.join(temp_dir, filename)
                thumb_path = os.path.join(temp_dir, f"thumb_{filename}")
                
                try:
                    # Sauvegarder temporairement le fichier
                    file.save(temp_path)
                    
                    # Upload vers Supabase
                    result = storage.upload_image(temp_path, folder=gallery_id)
                    
                    # Créer et uploader la miniature
                    with Image.open(temp_path) as img:
                        img.thumbnail(THUMBNAIL_SIZE)
                        img.save(thumb_path)
                        thumb_result = storage.upload_image(thumb_path, folder=f"{gallery_id}/thumbnails")
                    
                    # Ajouter les URLs à la galerie
                    gallery['images'].append({
                        'image_url': result['url'],
                        'thumbnail_url': thumb_result['url'],
                        'filename': file.filename,
                        'storage_path': result['path'],
                        'thumbnail_path': thumb_result['path']
                    })
                    
                except Exception as e:
                    flash(f'Erreur lors du téléchargement de {file.filename}: {str(e)}', 'error')
                    continue
                
                finally:
                    # Nettoyer les fichiers temporaires
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
        
        save_gallery_data(galleries)
        flash('Photos ajoutées avec succès', 'success')
        
    finally:
        # Supprimer le répertoire temporaire s'il est vide
        try:
            os.rmdir(temp_dir)
        except:
            pass
    
    return redirect(url_for('gallery', gallery_id=gallery_id))

@app.route('/gallery/<gallery_id>/delete', methods=['POST'])
def delete_gallery(gallery_id):
    try:
        galleries = load_gallery_data()
        if gallery_id not in galleries:
            flash('Galerie introuvable', 'error')
            return redirect(url_for('galleries'))

        gallery = galleries[gallery_id]
        
        # Supprimer toutes les images de Supabase
        for image in gallery['images']:
            try:
                if 'storage_path' in image:
                    storage.delete_image(image['storage_path'])
                if 'thumbnail_path' in image:
                    storage.delete_image(image['thumbnail_path'])
            except Exception as e:
                print(f"Erreur lors de la suppression de l'image {image.get('filename', 'unknown')}: {str(e)}")
        
        del galleries[gallery_id]
        save_gallery_data(galleries)
        flash('Galerie supprimée avec succès', 'success')
        
    except Exception as e:
        flash(f'Erreur lors de la suppression de la galerie: {str(e)}', 'error')
    
    return redirect(url_for('galleries'))

@app.route('/gallery/<gallery_id>/edit', methods=['GET', 'POST'])
def edit_gallery(gallery_id):
    galleries = load_gallery_data()
    if gallery_id not in galleries:
        flash('Galerie introuvable', 'error')
        return redirect(url_for('galleries'))
    
    gallery = galleries[gallery_id]
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date = request.form.get('date')
        
        if not title or not date:
            flash('Le titre et la date sont requis', 'error')
        else:
            gallery['title'] = title
            gallery['description'] = description
            gallery['date'] = date
            
            save_gallery_data(galleries)
            flash('Galerie mise à jour avec succès', 'success')
            return redirect(url_for('gallery', gallery_id=gallery_id))
        
    return render_template('edit_gallery.html', gallery=gallery, gallery_id=gallery_id)

@app.route('/gallery/<gallery_id>/set_cover/<int:image_index>', methods=['POST'])
def set_gallery_cover(gallery_id, image_index):
    galleries = load_gallery_data()
    if gallery_id not in galleries:
        flash('Galerie introuvable', 'error')
        return redirect(url_for('galleries'))
    
    gallery = galleries[gallery_id]
    if not gallery['images'] or image_index >= len(gallery['images']):
        flash('Image introuvable', 'error')
        return redirect(url_for('gallery', gallery_id=gallery_id))
    
    # Déplacer l'image sélectionnée en première position
    image = gallery['images'].pop(image_index)
    gallery['images'].insert(0, image)
    
    save_gallery_data(galleries)
    flash('Photo de couverture mise à jour avec succès', 'success')
    return redirect(url_for('gallery', gallery_id=gallery_id))

if __name__ == '__main__':
    app.run(debug=True)
