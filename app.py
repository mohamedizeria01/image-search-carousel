from flask import Flask, render_template, request, jsonify
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

# Route for the main page with sidebar navigation
@app.route("/", methods=["GET", "POST"])
def index():
    # Handle the retrieval system form submission
    if request.method == "POST" and request.form.get("action") == "retrieval":
        text_query = request.form["query"]
        top_k = int(request.form["top_k"])

        # Initialize the image collection
        image_collection = [
            os.path.join(images_folder, filename)
            for filename in os.listdir(images_folder)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        ]

        # Run the semantic image search
        top_k_images = semantic_image_search(text_query, image_collection, top_k)

        return render_template("index.html", page="retrieval", top_k_images=top_k_images)

    # Default rendering for the retrieval system
    return render_template("index.html", page="retrieval", top_k_images=None)


# Route for zero-shot classification
@app.route("/classify", methods=["POST"])
def classify():
    if "image" not in request.files or "classes" not in request.form:
        return jsonify({"error": "Missing image or classes"}), 400

    image_file = request.files["image"]
    classes = request.form["classes"].split(",")

    # Preprocess the image
    image = Image.open(image_file).convert("RGB")
    inputs = clip_processor(text=classes, images=image, return_tensors="pt", padding=True)

    # Run the CLIP model
    with torch.no_grad():
        outputs = clip_model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).tolist()[0]

    # Prepare classification results
    result = {cls.strip(): round(prob * 100, 2) for cls, prob in zip(classes, probs)}
    return jsonify(result)
                                                                                                                                                                                                                                                                                                   
if __name__ == "__main__":
    app.run(debug=True)
