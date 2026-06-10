package com.example.scoreextractor.network

import com.example.scoreextractor.models.ExtractRequest
import com.example.scoreextractor.models.ExtractResponse
import retrofit2.http.Body
import retrofit2.http.POST

interface ApiService {
    @POST("api/extract")
    suspend fun extract(@Body request: ExtractRequest): retrofit2.Response<ExtractResponse>
}