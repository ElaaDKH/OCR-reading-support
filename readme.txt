Description :
Application de reconnaissance optique de caractères (OCR) pour extraire du texte à partir d'images.

Livrables :

1.Version Desktop (Kivy)

  Dossier : Desktop Version/
  Lancement : python App.py
 (Le traitement OCR s'effectue directement dans l'application)


2.Version Mobile (Android)

  Dossier : VisionSpeak_App/
  APK : app-release.apk (prêt à installer)

   Installation de l'APK sur Android :

   1. Connecter le téléphone au PC via câble USB (type data)
   2. Copier-coller app-release.apk dans le téléphone
   3. Sur le téléphone, ouvrir le fichier pour installer
   4. Autoriser l'installation si demandé
   Note: Ignorer l'alerte "virus" (normale pour les APK non publiés sur Play Store)

 (L'application envoie l'image à un serveur Python pour le traitement)


3.Serveur Python

 Dossier : Serveur_Python/
 Lancement : python server.py  (Il faut changer l'adresse IP dans la fin du code)
(Reçoit les images depuis l'app Android et renvoie le texte extrait)