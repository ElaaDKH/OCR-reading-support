package com.example.ocr__app;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import java.text.SimpleDateFormat;
import java.util.Date;
import android.provider.MediaStore;
import android.speech.tts.TextToSpeech;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.util.Locale;
import okhttp3.*;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_IMAGE_CAPTURE = 1;
    private static final int REQUEST_CAMERA_PERMISSION = 100;
    private ImageView imageView;
    private TextView tvResult;
    private TextToSpeech tts;
    private Button btnSpeak;
    private Button btnPause;
    private Button btnRepeat;
    private boolean isSpeaking = false;
    private String lastOcrText = "";
    private String currentPhotoPath;
    private static final String SERVER_URL = "http://192.168.247.162:5000/ocr";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button btnCamera = findViewById(R.id.btnCamera);
        btnSpeak = findViewById(R.id.btnSpeak);
        btnPause = findViewById(R.id.btnPause);
        btnRepeat = findViewById(R.id.btnRepeat);
        imageView = findViewById(R.id.imageView);
        tvResult = findViewById(R.id.tvResult);

        tts = new TextToSpeech(this, status -> {
            if (status == TextToSpeech.SUCCESS) {
                tts.setLanguage(Locale.US);
            }
        });

        btnCamera.setOnClickListener(v -> {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.CAMERA},
                        REQUEST_CAMERA_PERMISSION);
            } else {
                openCamera();
            }
        });

        btnSpeak.setOnClickListener(v -> {
            if (!lastOcrText.isEmpty()) {
                tts.speak(lastOcrText, TextToSpeech.QUEUE_FLUSH, null, null);
            } else {
                Toast.makeText(this, "No text to read", Toast.LENGTH_SHORT).show();
            }
        });

        btnPause.setOnClickListener(v -> {
            tts.stop();
        });

        btnRepeat.setOnClickListener(v -> {
            if (!lastOcrText.isEmpty()) {
                tts.speak(lastOcrText, TextToSpeech.QUEUE_FLUSH, null, null);
            } else {
                Toast.makeText(this, "No text to read", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void openCamera() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            File photoFile = null;
            try {
                // Create the File where the photo should go
                String timeStamp = new java.text.SimpleDateFormat("yyyyMMdd_HHmmss",
                        java.util.Locale.US).format(new java.util.Date());
                String imageFileName = "JPEG_" + timeStamp + "_";
                File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);

                if (storageDir != null && !storageDir.exists()) {
                    storageDir.mkdirs();
                }

                photoFile = File.createTempFile(imageFileName, ".jpg", storageDir);
                currentPhotoPath = photoFile.getAbsolutePath();

                Uri photoURI = FileProvider.getUriForFile(this,
                        "com.example.ocr__app.fileprovider",
                        photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);

            } catch (Exception ex) {
                Toast.makeText(this, "Error: " + ex.getMessage(), Toast.LENGTH_LONG).show();
                ex.printStackTrace();
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CAMERA_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                openCamera();
            } else {
                Toast.makeText(this, "Camera permission is required", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            try {
                // Load image
                Bitmap bitmap = BitmapFactory.decodeFile(currentPhotoPath);

                // Fix rotation using EXIF
                android.media.ExifInterface exif = new android.media.ExifInterface(currentPhotoPath);
                int orientation = exif.getAttributeInt(android.media.ExifInterface.TAG_ORIENTATION,
                        android.media.ExifInterface.ORIENTATION_NORMAL);

                android.graphics.Matrix matrix = new android.graphics.Matrix();
                switch (orientation) {
                    case android.media.ExifInterface.ORIENTATION_ROTATE_90:
                        matrix.postRotate(90);
                        break;
                    case android.media.ExifInterface.ORIENTATION_ROTATE_180:
                        matrix.postRotate(180);
                        break;
                    case android.media.ExifInterface.ORIENTATION_ROTATE_270:
                        matrix.postRotate(270);
                        break;
                }

                bitmap = Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(),
                        bitmap.getHeight(), matrix, true);

                // Scale down if needed
                int maxDimension = 1600;
                if (bitmap.getWidth() > maxDimension || bitmap.getHeight() > maxDimension) {
                    float scale = Math.min(
                            (float) maxDimension / bitmap.getWidth(),
                            (float) maxDimension / bitmap.getHeight()
                    );
                    int newWidth = Math.round(bitmap.getWidth() * scale);
                    int newHeight = Math.round(bitmap.getHeight() * scale);
                    bitmap = Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true);
                }

                imageView.setImageBitmap(bitmap);
                tvResult.setText("Processing... Please wait 10-30 seconds...");
                sendImageToServer(bitmap);

            } catch (Exception e) {
                Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        }
    }

    private void sendImageToServer(Bitmap bitmap) {
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, stream);
        byte[] byteArray = stream.toByteArray();

        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
                .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
                .writeTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
                .build();

        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("image", "photo.jpg",
                        RequestBody.create(byteArray, MediaType.parse("image/jpeg")))
                .build();

        Request request = new Request.Builder()
                .url(SERVER_URL)
                .post(requestBody)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, java.io.IOException e) {
                runOnUiThread(() -> {
                    tvResult.setText("Error: " + e.getMessage());
                    Toast.makeText(MainActivity.this,
                            "Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
                });
            }

            @Override
            public void onResponse(Call call, Response response) throws java.io.IOException {
                String responseData = response.body().string();
                String text = responseData.replace("{\"text\":\"", "").replace("\"}", "");

                runOnUiThread(() -> {
                    lastOcrText = text;
                    tvResult.setText(text);
                    if (!text.isEmpty()) {
                        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);
                    }
                });
            }
        });
    }

    @Override
    protected void onDestroy() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
        }
        super.onDestroy();
    }
}