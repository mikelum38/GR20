"""
Script de mise à jour du galleries.json avec les images Cloudinary.

Pour chaque galerie, il cherche dans le folder Cloudinary dont le nom = gallery_id,
récupère toutes les images, et reconstruit image_url / thumbnail_url / filename / public_id.

Usage :
    pip install cloudinary
    python update_galleries.py

Le fichier galleries_updated.json sera créé dans le même dossier.
"""

import json
import cloudinary
import cloudinary.api

# ── Config ────────────────────────────────────────────────────────────────────
CLOUD_NAME  = "dvhkgvemu"
API_KEY     = "446464431195751"
API_SECRET  = "dxtvSCE_JDAqI0aiAtPRco4S4C0"

INPUT_FILE  = "galleries.json"
OUTPUT_FILE = "galleries_updated.json"

BASE_URL       = f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload"
THUMBNAIL_OPTS = "w_300,h_300,c_fill"
# ──────────────────────────────────────────────────────────────────────────────

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
)


def get_all_resources_in_folder(folder_path: str) -> list:
    """Récupère toutes les images d'un folder via la Search API (gère la pagination)."""
    resources = []
    next_cursor = None

    while True:
        search = (
            cloudinary.Search()
            .expression(f'folder="{folder_path}"')
            .max_results(500)
        )
        if next_cursor:
            search = search.next_cursor(next_cursor)

        result = search.execute()
        resources.extend(result.get("resources", []))

        next_cursor = result.get("next_cursor")
        if not next_cursor:
            break

    return resources


def build_image_entry(resource: dict) -> dict:
    """Construit une entrée image à partir d'une ressource Cloudinary."""
    public_id = resource["public_id"]
    fmt       = resource.get("format", "jpg")
    filename  = public_id.split("/")[-1] + "." + fmt

    image_url     = f"{BASE_URL}/{public_id}.{fmt}"
    thumbnail_url = f"{BASE_URL}/{THUMBNAIL_OPTS}/{public_id}.{fmt}"

    return {
        "image_url":     image_url,
        "thumbnail_url": thumbnail_url,
        "filename":      filename,
        "public_id":     public_id,
    }


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        galleries = json.load(f)

    total = len(galleries)
    updated = 0
    skipped = 0

    for idx, (gallery_id, gallery) in enumerate(galleries.items(), 1):
        title = gallery.get("title", gallery_id)
        print(f"[{idx}/{total}] {title}")

        folder_path = f"GR20/{gallery_id}"
        print(f"  → folder : {folder_path}")
        try:
            resources = get_all_resources_in_folder(folder_path)
        except Exception as e:
            print(f"  ⚠️  Erreur Cloudinary pour {gallery_id} : {e}")
            skipped += 1
            continue

        if not resources:
            print(f"  ⚠️  Aucune image trouvée dans le folder '{gallery_id}'")
            skipped += 1
            continue

        # Tri par public_id pour un ordre stable
        resources.sort(key=lambda r: r["public_id"])

        gallery["images"] = [build_image_entry(r) for r in resources]
        print(f"  ✅ {len(resources)} images")
        updated += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(galleries, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Terminé : {updated} galeries mises à jour, {skipped} ignorées.")
    print(f"📄 Fichier généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
