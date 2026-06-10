package com.example.scoreextractor

import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.scoreextractor.databinding.ActivityMainBinding
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel = MainViewModel()
    private lateinit var imagePreviewAdapter: ImagePreviewAdapter
    private var selectedUris: List<Uri> = emptyList()

    // 使用 PickMultipleVisualMedia 支持多选（最多可选数量可设）
    private val pickMultipleImages =
        registerForActivityResult(ActivityResultContracts.PickMultipleVisualMedia(20)) { uris ->
            if (uris.isNotEmpty()) {
                selectedUris = uris
                updateImagePreview()
                binding.tvImageCount.text = "已选 ${selectedUris.size} 张图片"
            } else {
                Toast.makeText(this, "未选择图片", Toast.LENGTH_SHORT).show()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupRecyclerView()

        binding.btnSelectImages.setOnClickListener {
            // 启动图片选择器（支持多选）
            pickMultipleImages.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
        }

        binding.btnSubmit.setOnClickListener {
            val serverUrl = binding.etServerUrl.text.toString().trim()
            val apiKey = binding.etApiKey.text.toString().trim()
            if (serverUrl.isEmpty() || apiKey.isEmpty()) {
                Toast.makeText(this, "请填写服务器地址和 API Key", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (selectedUris.isEmpty()) {
                Toast.makeText(this, "请先选择图片", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            binding.progressBar.visibility = android.view.View.VISIBLE
            binding.tvResult.text = "处理中，请稍候..."

            lifecycleScope.launch {
                val result = viewModel.submit(serverUrl, apiKey, selectedUris, this@MainActivity)
                binding.progressBar.visibility = android.view.View.GONE
                if (result != null) {
                    binding.tvResult.text = result
                } else {
                    binding.tvResult.text = "请求失败，请查看日志"
                }
            }
        }
    }

    private fun setupRecyclerView() {
        imagePreviewAdapter = ImagePreviewAdapter { uri ->
            // 点击缩略图弹出确认删除对话框
            MaterialAlertDialogBuilder(this)
                .setTitle("移除图片")
                .setMessage("确定要移除这张图片吗？")
                .setPositiveButton("移除") { _, _ ->
                    selectedUris = selectedUris.filter { it != uri }
                    updateImagePreview()
                    binding.tvImageCount.text = "已选 ${selectedUris.size} 张图片"
                }
                .setNegativeButton("取消", null)
                .show()
        }
        binding.recyclerViewPreview.apply {
            layoutManager = LinearLayoutManager(this@MainActivity, LinearLayoutManager.HORIZONTAL, false)
            adapter = imagePreviewAdapter
        }
    }

    private fun updateImagePreview() {
        imagePreviewAdapter.submitList(selectedUris)
    }
}