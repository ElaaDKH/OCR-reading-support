from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
import easyocr
import cv2
import numpy as np
from threading import Thread
import pyttsx3
import os

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class AccessibleOCRApp(App):
    def build(self):
        self.title = "VisionSpeak - Desktop Version (ENG+FR)"
        
        # Initialize components
        self.reader = None
        self.reader_ready = False
        self.tts_engine = None
        self.is_speaking = False
        self.last_detected_text = ""
        
        # OpenCV camera
        self.capture = None
        self.camera_active = False
        self.camera_frame = None
        
        # Main layout - LARGE elements for accessibility
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Camera preview - TOP SECTION
        self.camera_widget = KivyImage(
            size_hint=(1, 0.5),
            allow_stretch=True,
            keep_ratio=True
        )
        main_layout.add_widget(self.camera_widget)
        
        # Status display 
        self.status_label = Label(
            text='STARTING...',
            size_hint=(1, 0.15),
            font_size='40sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        main_layout.add_widget(self.status_label)
        
        # Detected text 
        self.text_label = Label(
            text='Starting camera...',
            size_hint=(1, 0.2),
            font_size='28sp',
            color=(0.9, 0.9, 0.9, 1),
            halign='center',
            valign='middle'
        )
        self.text_label.bind(size=self.text_label.setter('text_size'))
        main_layout.add_widget(self.text_label)
        
        # LARGE buttons
        button_layout = BoxLayout(size_hint=(1, 0.15), spacing=15)
        
        self.capture_btn = Button(
            text='CAPTURE & READ',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='32sp',
            bold=True,
            disabled=True
        )
        self.capture_btn.bind(on_press=self.capture_and_read)
        button_layout.add_widget(self.capture_btn)
        
        self.stop_btn = Button(
            text='STOP',
            background_color=(0.9, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size='32sp',
            bold=True
        )
        self.stop_btn.bind(on_press=self.stop_speaking)
        button_layout.add_widget(self.stop_btn)
        
        main_layout.add_widget(button_layout)
        
        # Initialize in background
        Thread(target=self.initialize_system, daemon=True).start()
        
        return main_layout
    
    def initialize_system(self):
        """Initialize camera, OCR, and TTS"""
        try:
            # Initialize TTS first (faster)
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'LOADING TTS...'))
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Slower for clarity
            self.tts_engine.setProperty('volume', 1.0)
            
            # Initialize camera
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'STARTING CAMERA...'))
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise Exception("Cannot open camera")
            
            # Set camera resolution
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.camera_active = True
            
            # Start camera preview loop
            Clock.schedule_interval(self.update_camera_preview, 1.0 / 30.0)  # 30 FPS
            
            # Initialize EasyOCR (this takes longest)
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'LOADING OCR...\n(First time may take 1-2 minutes)'))
            self.reader = easyocr.Reader(['en', 'fr'], gpu=False, verbose=False)
            self.reader_ready = True
            
            # Ready!
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', '✓ READY'))
            Clock.schedule_once(lambda dt: setattr(self.text_label, 'text', 'Press CAPTURE & READ button'))
            Clock.schedule_once(lambda dt: setattr(self.capture_btn, 'disabled', False))
            
            # Speak ready message
            self.speak("System prêt.")
            
        except Exception as e:
            error_msg = f'ERROR: {str(e)}'
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', error_msg))
            self.speak(f"Error starting system: {str(e)}")
    
    def update_camera_preview(self, dt):
        """Update camera preview in real-time"""
        if not self.camera_active or not self.capture:
            return
        
        ret, frame = self.capture.read()
        if ret:
            # Store frame for capture
            self.camera_frame = frame.copy()
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Flip horizontally for mirror effect (more intuitive)
            frame_rgb = cv2.flip(frame_rgb, 1)
            
            # Convert to Kivy texture
            h, w = frame_rgb.shape[:2]
            texture = Texture.create(size=(w, h))
            texture.blit_buffer(frame_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            
            self.camera_widget.texture = texture
    
    def capture_and_read(self, instance):
        """Capture image from camera and read text"""
        if not self.camera_active or not self.reader_ready:
            self.speak("System not ready yet")
            return
        
        self.capture_btn.disabled = True
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'CAPTURING...'))
        self.speak("Capturing")
        
        Thread(target=self._capture_and_process, daemon=True).start()
    
    def _capture_and_process(self):
        """Capture and process in background"""
        try:
            # Use the stored camera frame
            if self.camera_frame is None:
                Clock.schedule_once(lambda dt: self._update_ui('CAMERA ERROR', 'No frame available', True))
                self.speak("Camera error")
                return
            
            frame = self.camera_frame.copy()
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'READING TEXT...'))
            
            # Convert to RGB
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Apply preprocessing for better OCR
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Try adaptive threshold
            adaptive = cv2.adaptiveThreshold(
                gray, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 
                11, 2
            )
            
            # Run OCR on both original and processed
            results1 = self.reader.readtext(img_rgb, detail=1)
            results2 = self.reader.readtext(adaptive, detail=1)
            
            # Combine results
            all_results = results1 + results2
            
            if all_results:
                # Filter by confidence and remove duplicates
                seen = set()
                text_blocks = []
                
                for (bbox, text, conf) in all_results:
                    text_lower = text.lower().strip()
                    if conf > 0.3 and text_lower and text_lower not in seen:
                        seen.add(text_lower)
                        text_blocks.append((bbox[0][1], text, conf))  # (y_pos, text, conf)
                
                if text_blocks:
                    # Sort by vertical position
                    text_blocks.sort(key=lambda x: x[0])
                    detected_text = ' '.join([text for (_, text, _) in text_blocks])
                    avg_conf = sum(conf for (_, _, conf) in text_blocks) / len(text_blocks)
                    
                    Clock.schedule_once(lambda dt: self._update_ui(
                        f'FOUND TEXT\nConfidence: {avg_conf:.0%}',
                        detected_text,
                        True
                    ))
                    
                    self.last_detected_text = detected_text
                    self.speak(detected_text)
                else:
                    Clock.schedule_once(lambda dt: self._update_ui(
                        'NO TEXT FOUND',
                        'Try: Better lighting, closer/farther, steadier hold',
                        True
                    ))
                    self.speak("No text found. Try adjusting position or lighting.")
            else:
                Clock.schedule_once(lambda dt: self._update_ui(
                    'NO TEXT DETECTED',
                    'Ensure text is visible and well-lit',
                    True
                ))
                self.speak("No text detected. Make sure text is visible.")
                
        except Exception as e:
            error_msg = f'Error: {str(e)}'
            Clock.schedule_once(lambda dt: self._update_ui('ERROR', error_msg, True))
            self.speak(f"Error: {str(e)}")
    
    def _update_ui(self, status, text, enable_button):
        """Update UI on main thread"""
        self.status_label.text = status
        self.text_label.text = text
        if enable_button:
            self.capture_btn.disabled = False
    
    def speak(self, text):
        """Speak text using TTS"""
        if self.tts_engine and text:
            try:
                # Stop any current speech
                self.tts_engine.stop()
                # Speak new text
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
    
    def stop_speaking(self, instance):
        """Stop TTS"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
                self.status_label.text = 'STOPPED'
            except:
                pass
    
    def on_stop(self):
        """Cleanup on exit"""
        if self.capture:
            self.capture.release()
        if self.tts_engine:
            self.tts_engine.stop()

if __name__ == '__main__':
    AccessibleOCRApp().run()