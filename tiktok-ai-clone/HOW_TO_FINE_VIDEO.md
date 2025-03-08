Hugging Face's logo
Hugging Face
Models
Datasets
Spaces
Posts
Docs
Enterprise
Pricing



Datasets:

HuggingFaceFV
/
finevideo 

like
301

Follow

Hugging Face FineVideo
50
Tasks:
Visual Question Answering
Video-Text-to-Text
Modalities:
Text
Video
Formats:
parquet
Languages:
English
Size:
10K - 100K
Tags:
video
Libraries:
Datasets
Dask

Croissant
+ 1
License:

cc
Dataset card
Data Studio
Files and versions
Community
18
Dataset Viewer (First 5GB)
 Auto-converted to Parquet

Data Studio
Split (1)
train
·
~39.5k rows (showing the first 330)

train (~39.5k rows, showing the first 330)
mp4


unknown
json


dict
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAAG61W1vb3YAAABsbXZoZAAAAADVdA+r1XQPqwABX5ABHhCnAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Engineering Projects","content_metadata":{"characterList":[{"characterId":(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAASeuG1vb3YAAABsbXZoZAAAAADgV3P04Fdz9AAALtQAbmQlAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Game Reviews","content_metadata":{"characterList":[{"characterId":"1","des(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAAGabW1vb3YAAABsbXZoZAAAAADhMa464TGuOgAAMgAANFzhAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Career Highlights","content_metadata":{"characterList":[{"characterId":"c1(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAAJ2fG1vb3YAAABsbXZoZAAAAADf6poi3+qaIgAAdFMAuiEZAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Recipe Videos","content_metadata":{"characterList":[{"characterId":"c1","d(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAABDA21vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAL0rAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Fashion Hauls","content_metadata":{"characterList":[{"characterId":"TL","d(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAAAu8W1vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAIb3AAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Remixes","content_metadata":{"characterList":[{"characterId":"1","descript(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAAMxh21vb3YAAABsbXZoZAAAAADiTRiv4k0YrwAAMgAAbVxMAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Skincare Routines","content_metadata":{"characterList":[{"characterId":"1"(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAAFHO21vb3YAAABsbXZoZAAAAADb5VVO2+VVTgAAXcAAQy1HAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Music Videos","content_metadata":{"characterList":[{"characterId":"1","des(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAABRs21vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAOpVAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Documentaries","content_metadata":{"characterList":[{"characterId":"1","de(...TRUNCATED)
"AAAAGGZ0eXBtcDQyAAAAAGlzb21tcDQyAAT/G21vb3YAAABsbXZoZAAAAADZGelF2RnpRQAAdTABJMLwAAEAAAEAAAAAAAAAAAA(...TRUNCATED)
{"content_fine_category":"Home Improvement","content_metadata":{"characterList":[{"characterId":"1",(...TRUNCATED)
End of preview. Expand in Data Studio
Gated dataset
You have been granted access to this dataset

FineVideo
FineVideo
FineVideo
Description
Dataset Explorer
Revisions
Dataset Distribution
How to download and use FineVideo
Using datasets
Using huggingface_hub
Load a subset of the dataset
Dataset Structure
Data Instances
Data Fields
Dataset Creation
License CC-By
Considerations for Using the Data
Social Impact of Dataset
Discussion of Biases
Additional Information
Credits
Future Work
Opting out of FineVideo
Citation Information
Terms of use for FineVideo
Description
This dataset opens up new frontiers in video understanding, with special focus on the tricky tasks of mood analysis, storytelling and media edition in multimodal settings.

It's packed with detailed notes on scenes, characters, plot twists, and how audio and visuals play together, making it a versatile tool for everything from beefing up pre-trained models to fine-tuning AI for specific video tasks.

What sets this dataset apart is its focus on capturing the emotional journey and narrative flow of videos - areas where current multimodal datasets fall short - giving researchers the ingredients to cook up more context-savvy video analysis models.

Dataset Explorer
You can explore the dataset directly from your browser in the FineVideo Space.

FineVideo Explorer
Revisions
Date	Changes
Sept '24	Initial release of FineVideo
Nov '24	Addition of time-coded speech-to-text
Dataset Distribution
This comprehensive dataset includes:

43,751 videos
An average video length of 4.7 minutes with approximately 3,425 hours of content
Content from 122 categories with 358.61 videos per category on average
Content categories
The videos were originally shared on YouTube under Creative Commons Attribution (CC-BY) licenses. FineVideo obtained these videos along with their speech-to-text transcriptions from YouTube-Commons, a project that aggregates audio transcripts of CC-BY licensed YouTube videos.

How to download and use FineVideo
Using datasets
from datasets import load_dataset
import os

#full dataset (600GB of data)
dataset = load_dataset("HuggingFaceFV/finevideo", split="train")
print(dataset[0]['json']) # Access the metadata and speech to text of the first sample
dataset['0']['mp4'] # Access the video

#dataset streaming (will only download the data as needed)
dataset = load_dataset("HuggingFaceFV/finevideo", split="train", streaming=True)
sample = next(iter(dataset))
print(sample['json'])

with open('sample.mp4', 'wb') as video_file:
    video_file.write(sample['mp4'])

Using huggingface_hub
from huggingface_hub import snapshot_download
folder = snapshot_download('HuggingFaceFV/finevideo',
                           repo_type='dataset',
                           local_dir='./finevideo/')

Load a subset of the dataset
To load just a subset from a given content_parent_category such as 'Sports' you may use the following script:

from datasets import load_dataset
import json
import os

# Load the dataset in streaming mode
dataset = load_dataset("HuggingFaceFV/finevideo", split="train", streaming=True)

# Define the category you want to filter by
desired_category = 'Your_Category_Here'  # Replace with your desired category

def is_desired_category(sample):
    return sample['json']['content_parent_category'] == desired_category

filtered_dataset = filter(is_desired_category, dataset)

# Create directories to save videos and metadata
os.makedirs("videos", exist_ok=True)
os.makedirs("metadata", exist_ok=True)

for idx, sample in enumerate(filtered_dataset):
    video_filename = f"videos/sample_{idx}.mp4"
    with open(video_filename, 'wb') as video_file:
        video_file.write(sample['mp4'])

    json_filename = f"metadata/sample_{idx}.json"
    with open(json_filename, 'w') as json_file:
        json.dump(sample['json'], json_file)

Dataset Structure
Data Instances
Each data instance has a video and a metadata part. In metadata we can find different collections of metadata:

technical metadata (i.e. resolution, duration)
title level metadata (content fine / parent categories)
youtube details (i.e. channel, title, view count)
speech to text of the full video
timecode-level metadata (i.e. beginning / end of scenes, activities, object appearances)
{
    "content_fine_category": "Engineering Projects",
    "content_metadata": {
        "characterList": [
            {
                "characterId": "1",
                "description": "A young woman with long blonde hair, wearing a grey shirt and an orange safety vest. She is a participant in the heavy equipment operators course.",
                "name": "Sara Paynton"
            }
            // ... (other characters omitted for brevity)
        ],
        "description": "A video highlighting the Heavy Equipment Operators course, focusing on its benefits, collaboration between institutions, and testimonials from clients and coordinators.",
        "fps": 23.976024615513296,
        "scenes": [
            {
                "activities": [
                    {
                        "description": "Sara stands in front of a 'Heavy Equipment Operator Training Centre' sign and talks about the course.",
                        "timestamp": {
                            "end_timestamp": "00:00:09.009",
                            "start_timestamp": "00:00:00.000"
                        }
                    }
                    // ... (other activities omitted for brevity)
                ],
                "audioVisualCorrelation": 0.8,
                "cast": ["Sara Paynton"],
                "characterInteraction": [],
                "contextualRelevance": "The visuals of heavy equipment in action create a sense of excitement and potential for those interested in this field.",
                "dynamismScore": 0.7,
                "mood": {
                    "description": "Excited",
                    "keyMoments": []
                },
                "narrativeProgression": [
                    {
                        "description": "Introduction to the training center and Sara's presence.",
                        "timestamp": "00:00:00.000"
                    }
                    // ... (other narrative progression points omitted for brevity)
                ],
                "props": [
                    {
                        "name": "'Heavy Equipment Operator Training Centre' sign, construction site in the background.",
                        "timestamp": {
                            "end_timestamp": "00:00:09.009",
                            "start_timestamp": "00:00:00.000"
                        }
                    }
                    // ... (other props omitted for brevity)
                ],
                "sceneId": 1,
                "thematicElements": "Importance of training, career opportunities, personal growth.",
                "timestamps": {
                    "end_timestamp": "00:00:28.779",
                    "start_timestamp": "00:00:00.000"
                },
                "title": "Introductory Scenes",
                "videoEditingDetails": [
                    {
                        "description": "Fade in from black, slow zoom into the sign.",
                        "timestamps": {
                            "end_timestamp": "00:00:09.009",
                            "start_timestamp": "00:00:00.000"
                        }
                    }
                    // ... (other video editing details omitted for brevity)
                ]
            }
            // ... (other scenes omitted for brevity)
        ],
        "storylines": {
            "climax": {
                "description": "High success and employment rates emphasized by Bill Everitt.",
                "timestamp": "00:01:45.981"
            },
            "description": "Stories surrounding the Heavy Equipment Operators Course, featuring its success, training benefits, and client experiences.",
            "scenes": [1, 2, 3, 4, 5]
        },
        "title": "Heavy Equipment Operators Course Promo"
    },
    "content_parent_category": "Education",
    "duration_seconds": 208,
    "resolution": "640x360",
    "youtube_title": "Training Heavy Equipment Operators",
    "youtube_upload_date": "20160511",
    "youtube_view_count": 89462
}

Data Fields
{
  "resolution": "string",  # Video resolution, e.g. "640x360"
  "duration_seconds": int,  # Duration of the video in seconds
  "content_parent_category": "string",  # Broad category of the content
  "content_fine_category": "string",  # Specific category of the content
  "youtube_title": "string",  # Title of the YouTube video
  "youtube_description": "string",  # Description of the YouTube video
  "text_to_speech_word_count": int,  # Word count of the text-to-speech content
  "youtube_categories": ["string"],  # List of YouTube categories
  "youtube_tags": ["string"],  # List of YouTube tags
  "youtube_channel": "string",  # Name of the YouTube channel
  "youtube_view_count": int,  # Number of views on the video
  "youtube_comment_count": int,  # Number of comments on the video
  "youtube_like_count": int,  # Number of likes on the video
  "youtube_channel_follower_count": int,  # Number of followers for the channel
  "youtube_upload_date": "string",  # Upload date in YYYYMMDD format
  "youtube_age_limit": int,  # Age limit for the video (0 if none)
  "content_metadata": {
    "title": "string",  # Generated title
    "description": "string",  # Generated description
    "characterList": [  # Full list of characters that appear in the video
      {
        "characterId": "string",
        "name": "string", # Descriptive name or real name of the character
        "description": "string" # Description that should allow a person or a model recognize them
      }
    ],
    "scenes": [
      {
        "sceneId": int,
        "title": "string",
        "timestamps": {
          "start_timestamp": "string",
          "end_timestamp": "string"
        },
        "cast": ["string"],  # Characters from characterList that appear in this specific scene 
        "activities": [  # List of activities happening in the scene
          {
            "description": "string",
            "timestamp": {
              "start_timestamp": "string",
              "end_timestamp": "string"
            }
          }
        ],
        "props": [  # List of objects / props that appear in the scene 
          {
            "name": "string",
            "timestamp": {
              "start_timestamp": "string",
              "end_timestamp": "string"
            }
          }
        ],
        "videoEditingDetails": [  # Editing work in the scene such as transitions or effects
          {
            "description": "string",
            "timestamps": {
              "start_timestamp": "string",
              "end_timestamp": "string"
            }
          }
        ],
        "mood": {  # General mood of the scene
          "description": "string",
          "keyMoments": [  # If mood transitions within the scene, we annotate a key moment
            {
              "timestamp": "string",
              "changeDescription": "string"
            }
          ]
        },
        "narrativeProgression": [  # How the story unfolds over time
          {
            "description": "string",
            "timestamp": "string"
          }
        ],
        "characterInteraction": [  # Describes which characters from Cast interact within the scene
          {
            "characters": ["string"],
            "description": "string"
          }
        ],
        "thematicElements": "string",  # Main ideas or messages in a story that give it deeper meaning beyond just the events that happen. 
        "contextualRelevance": "string",  # Analyzes if information, ideas, or actions are appropriate and useful for the particular circumstances at hand
        "dynamismScore": float, # Score [0,1] that measures the dynamism of the scene
        "audioVisualCorrelation": float  # Score [0,1] that measures the correlation between what we see and what we hear
      }
    ],
    "storylines": {  # Storyline and list of scenes that contributed to it
      "description": "string",
      "scenes": [int],
      "climax": {  # If applies, climax of the story
        "description": "string",
        "timestamp": "string"
      }
    },
    "qAndA": [  # Collection of five Q&A about the video that focus on specific timestamp question as well as overall video understanding
      {
        "question": "string",
        "answer": "string"
      }
    ],
    "trimmingSuggestions": [ # Overall suggestions that could help make the video more dynamic
      {
        "description": "string",  # Type of trimming and why
        "timestamps": {
          "start_timestamp": "string",
          "end_timestamp": "string"
        }
      }
    ],
    "fps": float  # Video frames per second
  },
  "text_to_speech": "string"  # Full text-to-speech content
  "timecoded_text_to_speech": [  # List of time-coded text segments with start and end timestamps
    {
      "start": "string",  # Start timestamp of the segment, e.g., "00:00:00.000"
      "end": "string",    # End timestamp of the segment, e.g., "00:00:04.546"
      "text": "string"    # Text content for the specific segment, e.g., "We're in West Bank, BC, in the heart of the reserve."
    },
    ...
  ]
}

Dataset Creation
From an initial pool of 1.8M videos, we distilled a dynamic and diverse selection suitable to be meaningfully temporally annotated

Dataset Creation
License CC-By
The videos and transcripts provided are derived from YouTube-Commons.

All the transcripts are part of a video shared under a CC-By license and, in accordance with that license, every YouTube channel is fully credited. The timecode-level metadata has been generated with Google’s Gemini API and structured with OpenAI’s GPT-4o.

While content under a free license can be lawfully reproduced in any setting, we recommend that this set be preferably used for open research. Along with the requirements of proper attribution of the license, we encourage full release of data sources used for training models, extensive open documentation and responsible use of the dataset.

Considerations for Using the Data
Social Impact of Dataset
With the release of this dataset we aim to make model training more accessible to the machine learning community at large.

While multiple open-weights models with strong performance have been publicly released in the past, more often than not these releases are not accompanied by the corresponding training dataset. This is unfortunate as the dataset specificities and characteristics have been demonstrated to have a very large impact and role in the performances of the models. As the creation of a high quality training dataset is a fundamental requirement to training an LLM capable of excelling at downstream tasks, with FineVideo we (a) not only make the dataset creation process more transparent, by documenting our entire processing setup, we also (b) help alleviate the costs of dataset curation, both in time and in compute, for model creators by publicly releasing our dataset with the community.

Discussion of Biases
Efforts were made to minimize the amount of NSFW and toxic content present in the dataset by employing metadata and visual filters. However, there are still a significant number of videos present in the final dataset that could be considered toxic or contain harmful content. As FineVideo was sourced from diverse content creators from YouTube as a whole, any harmful biases typically present in it may be reproduced on our dataset.

Additional Information
Credits
Created by:

Miquel Farré, Andi Marafioti, Lewis Tunstall, Leandro Von Werra and Thomas Wolf

With the expertise and support of the 🤗 crew:

Abubakar Abid, Charles Bensimon, Eliott Coyac, Merve Enoyan, Hynek Kydlíček, Quentin Lhoest, Omar Sanseviero, Apolinário Passos, Guilherme Penedo, Bruna Trevelin, Ross Wightman

Thanks to:

Mara Lucien and Romann Weber for their inputs on narrative aspects and taxonomies.

Kavya Srinet and Francisco Massa for their inputs on video data loaders and multimodal LLMs.

Marc Pampols for the FineVideo promo video.

Future Work
We plan to release the code for the data pipeline used to create FineVideo. In future iterations, we aim to expand the dataset's size and increase the range of annotated aspects.

Opting out of FineVideo
In addition to selecting videos with permissive licenses, we are giving content creators the ability to have their videos removed from the dataset upon request. The process for submitting and enacting removal requests will keep evolving throughout the project as we receive feedback and build up more data governance tools.

If you have videos that include your personal data, you may use the following form to request its removal from the dataset submit the following form. We may follow up for additional information. We will then work on excluding the videos in the next iteration of FineVideo as we keep updating the dataset.

Citation Information

  title={FineVideo},
  author={Farré, Miquel and Marafioti, Andi and Tunstall, Lewis and Von Werra, Leandro and Wolf, Thomas},
  year={2024},
  howpublished={\url{https://huggingface.co/datasets/HuggingFaceFV/finevideo}},
}

Terms of use for FineVideo
FineVideo dataset is a collection of over 43.000 YouTube videos. We ask that you read and acknowledge the following points before using the dataset:

FineVideo is a collection of Creative Commons videos. Any use of all or part of the videos must abide by the terms of the original licenses, including attribution clauses when relevant. We facilitate this by providing provenance information for each data point.
FineVideo is regularly updated to enact validated data removal requests. By clicking on "Access repository", you agree to update your own version of FineVideo to the most recent usable version specified by the maintainers in the following thread. If you have questions about dataset versions and allowed uses, please also ask them in the dataset's community discussions. We will also notify users via email when the latest usable version changes.
To host, share, or otherwise provide access to FineVideo, you must include these Terms of Use.
Downloads last month
9,554
Size of the auto-converted Parquet files (First 5GB):
5.17 GB
Number of rows (First 5GB):
330
Estimated number of rows:
39,500
Models trained or fine-tuned on
HuggingFaceFV/finevideo

HuggingFaceTB/SmolVLM2-2.2B-Instruct
Image-Text-to-Text
•
Updated 1 day ago
•
427k
•
106

OpenGVLab/InternVL2_5-8B
Image-Text-to-Text
•
Updated about 1 month ago
•
62.8k
•
81

OpenGVLab/InternVL2_5-1B
Image-Text-to-Text
•
Updated about 1 month ago
•
28.5k
•
48

OpenGVLab/InternVL2_5-4B
Image-Text-to-Text
•
Updated about 1 month ago
•
26.1k
•
44

OpenGVLab/InternVL2_5-38B
Image-Text-to-Text
•
Updated about 1 month ago
•
24.1k
•
48

OpenGVLab/InternVL2_5-26B
Image-Text-to-Text
•
Updated about 1 month ago
•
20k
•
32
Browse 43 models trained on this dataset
Spaces using
HuggingFaceFV/finevideo
2
🐢
KwabsHug/GameConfigIdea
🚀
Seraph19/cardiffnlp-twitter-roberta-base-sentiment-latest



