Project Title: Simple Notes Generator with Built-in Toggle Parameters (.mp4 in, .txt out).

Overview: Users access the HTML user interface via a public sharing link, which allows them to upload a single .mp4 file from their local device.

How It Works:
* Python (.py) files run in the background to process and transcribe the audio from the uploaded .mp4 file.
* Output: The application generates and automatically downloads a .txt file to the user's device. This text file contains the transcription of the first 3, 5, 10, 30, or 60 minutes of the uploaded video.

About This Repository: This repo contains everything needed to run the .html file and open the user interface. This simple UI lets users upload .mp4 files, which are then scanned and transcribed into raw text (currently supporting English only). It also includes an optional paid toggle that unlocks advanced features, 

Use Vercel to host the public site.

such as: 
1. Speaker labels
2. Timestamps
3. Summaries
4. Other supported functionalities
