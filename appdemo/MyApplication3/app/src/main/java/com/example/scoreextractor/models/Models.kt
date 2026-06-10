package com.example.scoreextractor.models

import com.google.gson.annotations.SerializedName

data class ExtractRequest(
    @SerializedName("api_key") val apiKey: String,
    @SerializedName("images_base64") val imagesBase64: List<String>
)

data class ExtractResponse(
    val code: Int,
    val message: String,
    val data: ResponseData?
)

data class ResponseData(
    @SerializedName("total_image_count") val totalImageCount: Int,
    @SerializedName("base_info") val baseInfo: BaseInfo,
    @SerializedName("all_item_scores") val allItemScores: List<ItemScore>
)

data class BaseInfo(
    @SerializedName("student_id") val studentId: String,
    val name: String,
    @SerializedName("class_name") val className: String,
    val teacher: String,
    @SerializedName("total_score") val totalScore: String
)

data class ItemScore(
    @SerializedName("question_no") val questionNo: String,
    val score: String
)