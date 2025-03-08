# Local Video Assets

This directory contains local video assets and metadata for the TikTok AI Clone application.

## Directory Structure

- `/videos`: Contains the video files (MP4 format)
- `/data`: Contains metadata for the videos (JSON format)

## How It Works

The application uses these local videos instead of fetching from external sources like Hugging Face or Vimeo, which can cause CORS issues and slow down development.

The `fineVideoService.ts` file has been modified to load these local videos and their metadata, eliminating the need for external API calls during development.

## Adding More Videos

To add more videos:

1. Place MP4 video files in the `/videos` directory
2. Update the `/data/video_metadata.json` file with metadata for each video
3. Make sure each video entry in the JSON file has a `video_path` property pointing to the correct file path

## Video Sources

The sample videos included are from Pexels, which provides free stock videos for personal and commercial use.

## Troubleshooting

If videos aren't loading:

1. Check that the video files exist in the `/videos` directory
2. Verify that the paths in the metadata JSON file are correct
3. Check the browser console for specific error messages 