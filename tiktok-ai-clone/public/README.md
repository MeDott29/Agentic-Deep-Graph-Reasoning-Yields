# Public Directory

This directory contains static assets and resources that are served directly by the web server.

## Directory Structure

- **assets/**: Contains various asset files used by the application
  - **videos/**: Sample video files used in the application
  - **images/**: Static images used throughout the application
  - **data/**: JSON data files, including video metadata
- **favicon.svg**: The application favicon

## Assets

### Videos

The `assets/videos` directory contains sample MP4 video files used in the application. These videos are used as fallbacks when the application cannot fetch videos from the FineVideo dataset.

To add new videos:
1. Place MP4 video files in the `assets/videos` directory
2. Update the `assets/data/video_metadata.json` file with metadata for each video
3. Make sure each video entry has a `video_path` property pointing to the correct file path

### Data

The `assets/data` directory contains JSON data files used by the application:

- **video_metadata.json**: Contains metadata for the sample videos, including:
  - Video title
  - Description
  - Creator information
  - Tags and categories
  - Path to the video file

## Usage Guidelines

When working with files in the public directory:

1. **File Size**: Keep file sizes as small as possible, especially for videos and images
2. **Formats**: Use modern formats like WebP for images and MP4 (H.264) for videos
3. **Organization**: Maintain a clear directory structure for different types of assets
4. **Naming**: Use descriptive, lowercase filenames with hyphens instead of spaces
5. **Metadata**: Keep metadata files up to date when adding or removing assets 