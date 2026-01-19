import pytesseract
from PIL import Image, ImageDraw, ImageFont
import time

# For proper Arabic text rendering
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("⚠️  Pour un meilleur support de l'arabe, installez :")
    print("   pip install arabic-reshaper python-bidi")

# Configuration Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print("=" * 80)
print("COMPARAISON COMPLÈTE : TESSERACT vs EASYOCR vs DOCTR")
print("Avec support multilingue (Français, Anglais, Arabe)")
print("=" * 80)

# ========== CRÉATION D'UNE IMAGE DE TEST ==========
print("\n📝 Création d'une image de test avec texte multilingue...")

# Créer une image plus grande avec fond blanc et meilleur contraste
img = Image.new('RGB', (900, 700), color='white')
d = ImageDraw.Draw(img)

# Essayer de charger une police qui supporte l'arabe
font_loaded = False
font_name = "Police par défaut"

# Essayer plusieurs polices qui supportent bien l'arabe
arabic_fonts = [
    ("C:/Windows/Fonts/tahoma.ttf", "Tahoma"),
    ("C:/Windows/Fonts/tahomabd.ttf", "Tahoma Bold"),
    ("C:/Windows/Fonts/arial.ttf", "Arial"),
    ("C:/Windows/Fonts/calibri.ttf", "Calibri"),
    ("tahoma.ttf", "Tahoma"),
    ("arial.ttf", "Arial")
]

for font_path, name in arabic_fonts:
    try:
        font = ImageFont.truetype(font_path, 20)  # Taille augmentée à 20
        font_loaded = True
        font_name = name
        print(f"✅ Police chargée : {font_name}")
        break
    except:
        continue

if not font_loaded:
    print("⚠️  Aucune police TrueType trouvée, utilisation de la police par défaut")
    font = ImageFont.load_default()

# Textes de test
texte_francais = """Bonjour! Ceci est un test OCR.
Les chiffres: 123456789 et 0
Caractères spéciaux: @#$%&*()
Email: test@example.com
Prix: 99.99€ ou $49.50"""

texte_arabe_raw = """مرحبا! هذا اختبار OCR.
الأرقام: 123456789 و 0
أحرف خاصة: @#$%&*()
البريد: test@example.com
السعر: 99.99€ أو $49.50"""

texte_anglais = """Hello! This is an OCR test.
Numbers: 123456789 and 0
Special chars: @#$%&*()
Email: test@example.com
Price: €99.99 or $49.50"""

# Fonction pour préparer le texte arabe
def preparer_texte_arabe(texte):
    if ARABIC_SUPPORT:
        # Reshape Arabic text for proper display
        reshaped_text = arabic_reshaper.reshape(texte)
        # Apply bidirectional algorithm
        bidi_text = get_display(reshaped_text)
        return bidi_text
    else:
        return texte

# Position Y pour dessiner le texte
y_position = 40
line_height = 30  # Espacement augmenté entre les lignes

# Dessiner le texte français
d.text((30, y_position), "=== FRANÇAIS ===", fill='blue', font=font)
y_position += line_height + 10
for ligne in texte_francais.split('\n'):
    d.text((30, y_position), ligne, fill='black', font=font)
    y_position += line_height

y_position += 30

# Dessiner le texte arabe (avec support RTL si disponible)
d.text((30, y_position), "=== العربية (ARABE) ===", fill='blue', font=font)
y_position += line_height + 10
if ARABIC_SUPPORT:
    for ligne in texte_arabe_raw.split('\n'):
        ligne_formatee = preparer_texte_arabe(ligne)
        d.text((30, y_position), ligne_formatee, fill='black', font=font)
        y_position += line_height
else:
    # Sans support, on écrit quand même pour tester
    d.text((30, y_position), texte_arabe_raw, fill='black', font=font)
    y_position += 150

y_position += 30

# Dessiner le texte anglais
d.text((30, y_position), "=== ENGLISH ===", fill='blue', font=font)
y_position += line_height + 10
for ligne in texte_anglais.split('\n'):
    d.text((30, y_position), ligne, fill='black', font=font)
    y_position += line_height

img.save('texte_multilingue_test.png')
print("✅ Image créée : texte_multilingue_test.png")
print(f"   Police utilisée : {font_name}")
if not ARABIC_SUPPORT:
    print("⚠️  Note : Le texte arabe peut ne pas s'afficher correctement sans arabic-reshaper")
    print("   Installez avec : pip install arabic-reshaper python-bidi")
else:
    print("✅ Support arabe activé (arabic-reshaper + python-bidi)")

# Stockage des résultats
resultats = {}

# ========== TEST AVEC TESSERACT ==========
print("\n" + "=" * 80)
print("📘 TEST AVEC TESSERACT OCR")
print("=" * 80)

try:
    debut = time.time()
    image_pil = Image.open('texte_multilingue_test.png')
    
    # CORRECTION 1: Tester d'abord si ara.traineddata est disponible
    try:
        # Essayer avec l'arabe inclus
        texte_tesseract = pytesseract.image_to_string(image_pil, lang='eng+fra+ara')
        print("✅ Support arabe activé")
    except pytesseract.TesseractError as e:
        print(f"⚠️  Tesseract sans arabe : {e}")
        print("💡 Utilisation de eng+fra uniquement")
        # Fallback sans arabe
        texte_tesseract = pytesseract.image_to_string(image_pil, lang='eng+fra')
    
    temps_tesseract = time.time() - debut
    
    print(f"⏱️  Temps d'exécution : {temps_tesseract:.3f} secondes")
    print(f"\n📝 Texte détecté par Tesseract :")
    print("-" * 80)
    print(texte_tesseract if texte_tesseract.strip() else "❌ Aucun texte détecté")
    print("-" * 80)
    
    resultats['Tesseract'] = {
        'texte': texte_tesseract,
        'temps': temps_tesseract,
        'succes': True
    }
except Exception as e:
    print(f"❌ Erreur Tesseract : {e}")
    print("💡 Astuce : Assurez-vous que les données de langue arabe sont installées")
    print("   Téléchargez 'ara.traineddata' depuis https://github.com/tesseract-ocr/tessdata")
    print("   Et placez-le dans : C:\\Program Files\\Tesseract-OCR\\tessdata\\")
    resultats['Tesseract'] = {'succes': False, 'temps': 0}

# ========== TEST AVEC EASYOCR ==========
print("\n" + "=" * 80)
print("📗 TEST AVEC EASYOCR")
print("=" * 80)

try:
    import easyocr
    
    # CORRECTION 2: EasyOCR requiert une combinaison spécifique pour l'arabe
    # L'arabe doit être combiné avec anglais uniquement
    print("🔄 Chargement du lecteur EasyOCR...")
    
    # Test 1: Français et Anglais uniquement
    print("\n📝 Test 1: Français et Anglais (fr, en)")
    debut_total = time.time()
    reader_fr_en = easyocr.Reader(['fr', 'en'], gpu=False)
    temps_chargement_1 = time.time() - debut_total
    print(f"✅ Lecteur fr+en chargé en {temps_chargement_1:.3f} secondes")
    
    debut = time.time()
    resultats_fr_en = reader_fr_en.readtext('texte_multilingue_test.png')
    temps_fr_en = time.time() - debut
    print(f"⏱️  Temps d'exécution OCR : {temps_fr_en:.3f} secondes")
    
    # Test 2: Arabe et Anglais pour la partie arabe
    print("\n📝 Test 2: Arabe et Anglais (ar, en)")
    debut_total = time.time()
    reader_ar_en = easyocr.Reader(['ar', 'en'], gpu=False)
    temps_chargement_2 = time.time() - debut_total
    print(f"✅ Lecteur ar+en chargé en {temps_chargement_2:.3f} secondes")
    
    debut = time.time()
    resultats_ar_en = reader_ar_en.readtext('texte_multilingue_test.png')
    temps_ar_en = time.time() - debut
    print(f"⏱️  Temps d'exécution OCR : {temps_ar_en:.3f} secondes")
    
    # Combiner les résultats
    resultats_easyocr = resultats_fr_en + resultats_ar_en
    temps_easyocr = temps_fr_en + temps_ar_en
    temps_chargement = temps_chargement_1 + temps_chargement_2
    
    print(f"\n⏱️  Temps total OCR : {temps_easyocr:.3f} secondes")
    print(f"⏱️  Temps total (chargement + OCR) : {temps_chargement + temps_easyocr:.3f} secondes")
    
    # Extraire le texte complet
    texte_easyocr = ' '.join([detection[1] for detection in resultats_easyocr])
    
    print(f"\n📝 Texte détecté par EasyOCR ({len(resultats_easyocr)} détections) :")
    print("-" * 80)
    if resultats_easyocr:
        # AFFICHER TOUTES LES DÉTECTIONS
        for i, detection in enumerate(resultats_easyocr, 1):
            texte = detection[1]
            confiance = detection[2]
            print(f"{i}. {texte}")
            print(f"   Confiance : {confiance:.2%}")
    else:
        print("❌ Aucun texte détecté")
    print("-" * 80)
    
    # SAUVEGARDER LES RÉSULTATS DANS UN FICHIER UTF-8
    print("\n💾 Sauvegarde des résultats dans 'resultats_easyocr.txt'...")
    try:
        with open('resultats_easyocr.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RÉSULTATS EASYOCR - TEXTE DÉTECTÉ\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Nombre total de détections : {len(resultats_easyocr)}\n\n")
            
            for i, detection in enumerate(resultats_easyocr, 1):
                texte = detection[1]
                confiance = detection[2]
                bbox = detection[0]
                f.write(f"Détection #{i}:\n")
                f.write(f"  Texte: {texte}\n")
                f.write(f"  Confiance: {confiance:.2%}\n")
                f.write(f"  Position: {bbox}\n\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("TEXTE COMPLET (tout en une ligne):\n")
            f.write("=" * 80 + "\n")
            f.write(texte_easyocr + "\n")
        
        print("✅ Résultats sauvegardés! Ouvrez 'resultats_easyocr.txt' avec Notepad pour voir le texte arabe correctement")
    except Exception as e:
        print(f"⚠️  Erreur lors de la sauvegarde : {e}")
    
    resultats['EasyOCR'] = {
        'texte': texte_easyocr,
        'temps': temps_easyocr,
        'temps_chargement': temps_chargement,
        'succes': True,
        'detections': resultats_easyocr
    }
except ImportError:
    print("⚠️  EasyOCR non installé. Installation : pip install easyocr")
    resultats['EasyOCR'] = {'succes': False, 'temps': 0}
except Exception as e:
    print(f"❌ Erreur EasyOCR : {e}")
    resultats['EasyOCR'] = {'succes': False, 'temps': 0}

# ========== TEST AVEC DOCTR ==========
print("\n" + "=" * 80)
print("📙 TEST AVEC DOCTR (Document Text Recognition)")
print("=" * 80)

try:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    
    print("🔄 Chargement du modèle Doctr...")
    print("⚠️  Note : Doctr supporte principalement les langues latines")
    debut_total = time.time()
    
    # Charger le document
    doc = DocumentFile.from_images('texte_multilingue_test.png')
    
    # Charger le modèle OCR
    model = ocr_predictor(pretrained=True)
    
    temps_chargement = time.time() - debut_total
    print(f"✅ Modèle chargé en {temps_chargement:.3f} secondes")
    
    # Effectuer l'OCR
    debut = time.time()
    result = model(doc)
    temps_doctr = time.time() - debut
    
    print(f"⏱️  Temps d'exécution OCR : {temps_doctr:.3f} secondes")
    print(f"⏱️  Temps total (chargement + OCR) : {temps_chargement + temps_doctr:.3f} secondes")
    
    # Extraire le texte
    texte_doctr = ""
    confidences = []
    mots_detectes = []
    
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    texte_doctr += word.value + " "
                    confidences.append(word.confidence)
                    mots_detectes.append((word.value, word.confidence))
                texte_doctr += "\n"
    
    confiance_moyenne = (sum(confidences) / len(confidences)) if confidences else 0
    
    print(f"\n📝 Texte détecté par Doctr ({len(mots_detectes)} mots) :")
    print("-" * 80)
    if mots_detectes:
        for i, (mot, conf) in enumerate(mots_detectes[:20], 1):
            print(f"{i}. {mot}")
            print(f"   Confiance : {conf:.2%}")
        if len(mots_detectes) > 20:
            print(f"... et {len(mots_detectes) - 20} mots supplémentaires")
    else:
        print("❌ Aucun texte détecté")
    print("-" * 80)
    
    resultats['Doctr'] = {
        'texte': texte_doctr,
        'temps': temps_doctr,
        'temps_chargement': temps_chargement,
        'confiance_moyenne': confiance_moyenne,
        'succes': True,
        'mots': mots_detectes
    }
except ImportError:
    print("⚠️  Doctr non installé. Installation :")
    print("   pip install python-doctr[torch]  # Pour PyTorch")
    print("   OU")
    print("   pip install python-doctr[tf]     # Pour TensorFlow")
    resultats['Doctr'] = {'succes': False, 'temps': 0}
except Exception as e:
    print(f"❌ Erreur Doctr : {e}")
    resultats['Doctr'] = {'succes': False, 'temps': 0}

# ========== ANALYSE DES PERFORMANCES ==========
print("\n" + "=" * 80)
print("📊 ANALYSE DÉTAILLÉE DES PERFORMANCES")
print("=" * 80)

def analyser_texte(texte, nom_systeme):
    """Analyse le texte détecté pour vérifier différents types de contenu"""
    
    # Détection de caractères arabes
    def contient_arabe(s):
        return any('\u0600' <= c <= '\u06FF' for c in s)
    
    analyse = {
        'chiffres_detectes': any(c.isdigit() for c in texte),
        'caracteres_speciaux': any(c in '@#$%&*()' for c in texte),
        'email_detecte': '@' in texte and '.' in texte,
        'symboles_monnaie': any(c in '€$' for c in texte),
        'ponctuation': any(c in '!?.,' for c in texte),
        'arabe_detecte': contient_arabe(texte),
        'longueur': len(texte.strip()),
        'nombre_lignes': len([l for l in texte.split('\n') if l.strip()])
    }
    
    print(f"\n🔍 Analyse pour {nom_systeme} :")
    print(f"   ✓ Chiffres détectés : {'Oui' if analyse['chiffres_detectes'] else 'Non'}")
    print(f"   ✓ Caractères spéciaux (@#$%...) : {'Oui' if analyse['caracteres_speciaux'] else 'Non'}")
    print(f"   ✓ Email détecté : {'Oui' if analyse['email_detecte'] else 'Non'}")
    print(f"   ✓ Symboles monétaires (€$) : {'Oui' if analyse['symboles_monnaie'] else 'Non'}")
    print(f"   ✓ Ponctuation : {'Oui' if analyse['ponctuation'] else 'Non'}")
    print(f"   ✓ Texte arabe détecté : {'Oui' if analyse['arabe_detecte'] else 'Non'}")
    print(f"   ✓ Longueur du texte : {analyse['longueur']} caractères")
    print(f"   ✓ Nombre de lignes : {analyse['nombre_lignes']}")
    
    return analyse

# Analyser chaque système
analyses = {}
for nom, data in resultats.items():
    if data['succes']:
        analyses[nom] = analyser_texte(data['texte'], nom)

# ========== TABLEAU COMPARATIF ==========
print("\n" + "=" * 80)
print("📊 TABLEAU COMPARATIF FINAL")
print("=" * 80)

print(f"\n{'Critère':<35} {'Tesseract':<20} {'EasyOCR':<20} {'Doctr':<20}")
print("-" * 95)

# Vitesse
if resultats['Tesseract']['succes']:
    tess_time = f"{resultats['Tesseract']['temps']:.3f}s"
else:
    tess_time = "N/A"

if resultats['EasyOCR']['succes']:
    easy_time = f"{resultats['EasyOCR']['temps']:.3f}s"
else:
    easy_time = "N/A"

if resultats['Doctr']['succes']:
    doctr_time = f"{resultats['Doctr']['temps']:.3f}s"
else:
    doctr_time = "N/A"

print(f"{'⚡ Vitesse (OCR seul)':<35} {tess_time:<20} {easy_time:<20} {doctr_time:<20}")

# Détection des différents types de contenu
for critere, cle in [
    ('🔢 Chiffres détectés', 'chiffres_detectes'),
    ('🔣 Caractères spéciaux', 'caracteres_speciaux'),
    ('📧 Email détecté', 'email_detecte'),
    ('💰 Symboles monétaires', 'symboles_monnaie'),
    ('🌍 Texte arabe détecté', 'arabe_detecte')
]:
    valeurs = []
    for nom in ['Tesseract', 'EasyOCR', 'Doctr']:
        if nom in analyses:
            valeurs.append("✓" if analyses[nom][cle] else "✗")
        else:
            valeurs.append("N/A")
    print(f"{critere:<35} {valeurs[0]:<20} {valeurs[1]:<20} {valeurs[2]:<20}")

# Informations supplémentaires
print("\n" + "-" * 95)
print("📋 CARACTÉRISTIQUES TECHNIQUES")
print("-" * 95)
print(f"{'📦 Taille installation':<35} {'~5 MB':<20} {'~500 MB':<20} {'~200 MB':<20}")
print(f"{'🌐 Support arabe':<35} {'Oui (avec ara.data)':<20} {'Excellent (ar+en)':<20} {'Non':<20}")
print(f"{'🎯 Précision texte imprimé':<35} {'Très bonne':<20} {'Excellente':<20} {'Excellente':<20}")
print(f"{'💻 GPU recommandé':<35} {'Non':<20} {'Oui':<20} {'Oui':<20}")
print("-" * 95)

# ========== RECOMMANDATIONS ==========
print("\n" + "=" * 80)
print("🏆 RECOMMANDATIONS FINALES")
print("=" * 80)

print("\n💡 POUR LE SUPPORT DE L'ARABE :")
print("\n✅ EasyOCR (RECOMMANDÉ POUR L'ARABE) :")
print("   • Utilisez: reader = easyocr.Reader(['ar', 'en'], gpu=False)")
print("   • L'arabe doit être combiné avec l'anglais uniquement")
print("   • Ne PAS utiliser ['ar', 'fr', 'en'] - incompatible!")

print("\n✅ Tesseract :")
print("   • Installez ara.traineddata depuis:")
print("     https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata")
print("   • Placez-le dans: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
print("   • Utilisez: lang='eng+fra+ara'")

print("\n✅ Doctr :")
print("   • Pas de support officiel de l'arabe")
print("   • À éviter pour le texte arabe")

print("\n📥 INSTALLATION COMPLÈTE :")
print("   pip install easyocr")
print("   pip install arabic-reshaper python-bidi")
print("   pip install python-doctr[torch]")

print("\n" + "=" * 80)
print("COMPARAISON TERMINÉE !")
print("=" * 80)