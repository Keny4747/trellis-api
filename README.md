# Trellis API

A RESTful API for Microsoft's [TRELLIS](https://github.com/microsoft/TRELLIS), enabling seamless evaluation of machine learning model robustness. This project simplifies TRELLIS’s powerful tools into an accessible interface for researchers and developers.

## Features

- Upload and process images for 3D model generation.
- Evaluate robustness against various perturbations.
- Retrieve detailed metrics and visualizations.
- Enable seamless integration into automated workflows.

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- Pipenv or pip for dependency management

### Tested Environment

- Operating System: Ubuntu 22.04.5 LTS (WSL2)
- Python Version: 3.10.12

### Docker Deployment

#### Start the Service

1. Stop and remove any existing container:
   ```bash
   docker stop trellis-service-client
   docker rm trellis-service-client
   ```

2. Build the Docker image and run it:
   ```bash
    docker build -t trellis-processor .

    docker run -d --gpus all -p 5000:5000 \
        -v "/mnt/d/Code/trellis_service/output:/workspace/TRELLIS/output:rw" \
        --name trellis-service-client trellis-processor

    docker logs -f trellis-service-client
   ```

   If you prefer to avoid building the Docker image, you can use the pre-built image from Docker Hub:
      ```bash
      docker pull plenost/trellis-processor

      docker run -d --gpus all -p 5000:5000 \
         -v "/mnt/d/Code/trellis_service/output:/workspace/TRELLIS/output:rw" \
         --name trellis-service-client plenost/trellis-processor

      docker logs -f trellis-service-client
   ```

The API will be available at `http://localhost:5000`.

#### Start the Client

Open a new bash

1. Initialize the models (download the weights):
   ```bash
   curl -v -X POST http://localhost:5000/initialize
   ```

2. Process an image (outputs 3 MP4 and 1 GLB files):
   ```bash
   curl -v -X POST -F "image=@input/cherry.webp" http://localhost:5000/process
   ```

## Usage

### Endpoints

#### Initialize Pipeline
- **POST** `/initialize`
  - Initialize the TRELLIS processing pipeline.

#### Process Image
- **POST** `/process`
  - Upload an image for processing and retrieve 3D outputs (Gaussian, radiance field, mesh, and GLB files).

### Example Request

#### Initialize Pipeline
```bash
curl -X POST http://localhost:5000/initialize
```

#### Process Image
```bash
curl -X POST -F 'image=@path/to/image.png' http://localhost:5000/process
```

## Code Overview

### `initialize.py`
Handles the initialization of the TRELLIS pipeline, loading pre-trained models and ensuring resources are ready for processing.

### `process.py`
Processes images using the TRELLIS pipeline, generating outputs like Gaussian videos, radiance fields, and 3D meshes.

### `service.py`
Implements the Flask API with endpoints for initialization and image processing. Logs all actions and provides detailed error handling.

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-branch
   ```
5. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

Special thanks to Microsoft for developing [TRELLIS](https://github.com/microsoft/TRELLIS).

---

Feel free to contribute or open issues to improve this project!

