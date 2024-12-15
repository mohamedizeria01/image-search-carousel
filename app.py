from flask import Flask, render_template, request
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import os

app = Flask(__name__)

# Initialize the CLIP model and processor
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Path to the folder containing the images
images_folder = r"C:\Users\hp\Desktop\projet\static\images"

# Function for semantic image search
def semantic_image_search(text_query, image_collection, top_k=3, clip_model=clip_model, clip_processor=clip_processor):
    with torch.no_grad():
        # Load images and process them into suitable format for CLIP model
        images = [Image.open(img_path).convert("RGB") for img_path in image_collection]
        
        # Process the text query and images to get embeddings
        inputs = clip_processor(text=[text_query]*len(images), images=images, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)

        # Extract the embeddings
        text_query_embedding = outputs.text_embeds  # Shape: [batch_size, embedding_dim]
        image_embeddings = outputs.image_embeds  # Shape: [batch_size, embedding_dim]

        # Compute cosine similarities between the text query embedding and each image embedding
        similarities = torch.nn.functional.cosine_similarity(text_query_embedding, image_embeddings)

        # Get top-k indices based on similarity scores
        top_k_indices = torch.topk(similarities, k=top_k).indices

        # Get the top-k most similar images and only return the image filenames (not the full path)
        top_k_images = [os.path.basename(image_collection[i]) for i in top_k_indices]

    return top_k_images

# Route to handle form submission
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Capture query and top_k from the form
        text_query = request.form['query']
        top_k = int(request.form['top_k'])  # Convert top_k to integer

        # Initialize the image collection
        image_collection = []
        for filename in os.listdir(images_folder):
            file_path = os.path.join(images_folder, filename)
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                image_collection.append(file_path)

        # Run the semantic image search
        top_k_images = semantic_image_search(text_query, image_collection, top_k)

        # Return the results to the template
        return render_template("index.html", top_k_images=top_k_images)

    return render_template("index.html", top_k_images=None)

if __name__ == "__main__":
    app.run(debug=True)
