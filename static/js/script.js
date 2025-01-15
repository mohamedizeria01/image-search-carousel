function showClassification() {
    document.getElementById("main-content").innerHTML = `
        <div class="container py-5">
            <h2 class="text-center mb-4 text-primary font-weight-bold">Zero-Shot Classification</h2>
            <form id="classification-form" method="POST" enctype="multipart/form-data" action="/classify" class="p-4 bg-white border rounded shadow">
                <div class="form-group">
                    <label for="image" class="font-weight-bold">Upload Image:</label>
                    <input type="file" id="image" name="image" class="form-control-file" required>
                </div>
                <div class="form-group">
                    <label for="classes" class="font-weight-bold">Enter Classes (comma-separated):</label>
                    <input type="text" id="classes" name="classes" class="form-control" placeholder="e.g., cat, dog, car" required>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Classify</button>
            </form>
            <div id="results" class="mt-5"></div>
        </div>
    `;

    const form = document.getElementById("classification-form");
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const response = await fetch("/classify", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        const resultsDiv = document.getElementById("results");

        // Create a container to hold the image and results side by side
        const resultsContainer = document.createElement("div");
        resultsContainer.classList.add("d-flex", "align-items-center");

        // Create a div for the image on the left
        const imageDiv = document.createElement("div");
        imageDiv.classList.add("mr-4"); // Add margin to the right of the image
        const image = document.createElement("img");
        image.src = URL.createObjectURL(formData.get("image")); // Display the uploaded image
        image.classList.add("img-fluid", "rounded");
        image.style.maxWidth = "300px"; // Set a max width for the image
        imageDiv.appendChild(image);

        // Create a div for the results on the right
        const resultsContentDiv = document.createElement("div");
        resultsContentDiv.classList.add("ml-4", "w-75");

        Object.entries(result).forEach(([key, value]) => {
            resultsContentDiv.innerHTML += `
                <div class="mb-3">
                    <strong class="d-block">${key}</strong>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="px-3">${value.toFixed(2)}% </span>
                        <div class="progress w-100" style="height: 20px;">
                            <div class="progress-bar bg-info" role="progressbar" style="width: ${value}%" aria-valuenow="${value}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                    </div>
                </div>
            `;
        });

        // Append the image and result sections to the results container
        resultsContainer.appendChild(imageDiv);
        resultsContainer.appendChild(resultsContentDiv);

        // Append the results container to the results div
        resultsDiv.appendChild(resultsContainer);
    });
}
