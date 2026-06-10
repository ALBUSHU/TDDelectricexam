package com.example.scoreextractor

import android.content.Context
import android.net.Uri
import com.example.scoreextractor.models.ExtractRequest
import com.example.scoreextractor.network.RetrofitClient
import com.example.scoreextractor.utils.ImageUtils
import com.google.gson.GsonBuilder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class MainViewModel {

    suspend fun submit(serverUrl: String, apiKey: String, uris: List<Uri>, context: Context): String? {
        return withContext(Dispatchers.IO) {
            try {
                // 将 URI 转换为 Base64
                val base64List = uris.mapNotNull { uri ->
                    ImageUtils.uriToBase64(context, uri)
                }
                if (base64List.isEmpty()) {
                    return@withContext "错误：无法转换任何图片（格式不支持或大小超限）"
                }

                // 创建 Retrofit 服务
                val apiService = RetrofitClient.create(serverUrl)
                val request = ExtractRequest(apiKey, base64List)
                val response = apiService.extract(request)

                if (response.isSuccessful && response.body() != null) {
                    val gson = GsonBuilder().setPrettyPrinting().create()
                    val prettyJson = gson.toJson(response.body())
                    return@withContext prettyJson
                } else {
                    return@withContext "服务器错误: ${response.code()} - ${response.message()}"
                }
            } catch (e: Exception) {
                return@withContext "网络异常: ${e.message}"
            }
        }
    }
}