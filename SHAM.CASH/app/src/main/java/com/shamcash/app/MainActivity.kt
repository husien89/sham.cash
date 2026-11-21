package com.shamcash.app

import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val startButton = findViewById<Button>(R.id.startButton)

        startButton.setOnClickListener {
            Toast.makeText(this, "مرحبًا بك في SHAM.CASH", Toast.LENGTH_SHORT).show()
        }
    }
}
