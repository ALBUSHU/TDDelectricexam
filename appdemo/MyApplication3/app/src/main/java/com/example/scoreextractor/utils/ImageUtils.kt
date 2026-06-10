package com.example.scoreextractor.utils

import android.content.ContentResolver
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Base64
import java.io.ByteArrayOutputStream

object ImageUtils {

    /**
     * 将图片 URI 转换为 Base64 字符串 (JPEG 格式，压缩至长边≤1024px，质量80%)
     * @return Base64 纯字符串，不带 data:image 前缀，失败返回 null
     */
    fun uriToBase64(context: android.content.Context, uri: Uri): String? {
        return try {
            val inputStream = context.contentResolver.openInputStream(uri) ?: return null
            val originalBitmap = BitmapFactory.decodeStream(inputStream)
            inputStream.close()

            if (originalBitmap == null) return null

            // 压缩图片：限制长边不超过 1024 像素
            val maxSize = 1024
            val width = originalBitmap.width
            val height = originalBitmap.height
            val scale = if (width > height && width > maxSize) {
                maxSize.toFloat() / width
            } else if (height > maxSize) {
                maxSize.toFloat() / height
            } else {
                1.0f
            }

            val scaledBitmap = if (scale < 1.0f) {
                val newWidth = (width * scale).toInt()
                val newHeight = (height * scale).toInt()
                Bitmap.createScaledBitmap(originalBitmap, newWidth, newHeight, true)
            } else {
                originalBitmap
            }

            val stream = ByteArrayOutputStream()
            scaledBitmap.compress(Bitmap.CompressFormat.JPEG, 80, stream)
            val bytes = stream.toByteArray()
            Base64.encodeToString(bytes, Base64.NO_WRAP)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}