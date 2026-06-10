package com.example.scoreextractor

import android.net.Uri
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.scoreextractor.databinding.ItemImagePreviewBinding

class ImagePreviewAdapter(private val onItemClick: (Uri) -> Unit) :
    RecyclerView.Adapter<ImagePreviewAdapter.ViewHolder>() {

    private var items: List<Uri> = emptyList()

    fun submitList(uris: List<Uri>) {
        items = uris
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemImagePreviewBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val uri = items[position]
        Glide.with(holder.itemView.context)
            .load(uri)
            .centerCrop()
            .into(holder.binding.imageView)
        holder.binding.imageView.setOnClickListener { onItemClick(uri) }
    }

    override fun getItemCount() = items.size

    class ViewHolder(val binding: ItemImagePreviewBinding) : RecyclerView.ViewHolder(binding.root)
}