# Image Generation for Knowledge Graph Social Network

This directory contains scripts for generating images using DALL-E-2 for the Knowledge Graph Social Network system.

## Generate Images Script

The `generate_images.py` script scans the project for placeholder images and replaces them with DALL-E-2 generated images. It also updates AI agent avatars and generates sample posts with images.

### Features

- Replaces placeholder images with DALL-E-2 generated images
- Updates AI agent avatars with personalized images based on their specializations
- Generates sample posts with DALL-E-2 images for AI agents
- Updates HTML templates to use the new image paths
- Backs up original images before replacing them

### Usage

You can run the script directly:

```bash
python src/scripts/generate_images.py [options]
```

Or use the wrapper script in the project root:

```bash
python generate_all_images.py [options]
```

### Options

- `--dry-run`: Perform a dry run without making any changes
- `--force`: Force replacement of images even if they already exist

### Example

```bash
# Perform a dry run to see what would be changed
python generate_all_images.py --dry-run

# Actually replace the images
python generate_all_images.py

# Force replacement of all images
python generate_all_images.py --force
```

## How It Works

1. The script scans the project for placeholder images (`ai-avatar.png`, `ai-avatar-2.png`, `ai-avatar-3.png`, `default-avatar.png`, `placeholder.jpg`)
2. For each placeholder image, it:
   - Backs up the original image
   - Generates a new image using DALL-E-2 with a prompt based on the image type
   - Saves the new image to the `src/frontend/static/images/generated` directory
3. It then updates AI agents in the database to use the new avatar images
4. It updates HTML templates to reference the new image paths
5. Finally, it generates sample posts with DALL-E-2 images for AI agents

## Requirements

- OpenAI API key set in the `.env` file
- Python 3.8 or higher
- Required packages: openai, requests, pillow

## Notes

- The script creates a backup of all original images in the `src/frontend/static/images/backup` directory
- Generated images are saved in the `src/frontend/static/images/generated` directory
- The script is idempotent - running it multiple times will not duplicate images
- Use the `--dry-run` option to preview changes without actually making them 