I have dialogues in this format:

```
dialogue_6:
 - s: A
   c: 你最近在做什么？
   p: Nǐ zuìjìn zài zuò shénme?
   t: What have you been doing lately?
   d: 最近 (zuìjìn) is a very common time word meaning "recently, lately". The 在 indicates ongoing action.
 
 - s: B
   c: 我在学习。你呢？
   p: Wǒ zài xuéxí. Nǐ ne?
   t: I'm studying. How about you?
   d: 呢 (ne) is a common particle used to ask "how about you/what about...?"
   
dialogue_7:
 - s: A
   c: 你看见我的书了吗？
   p: Nǐ kànjiàn wǒ de shū le ma?
   t: Have you seen my book?
   d: 看见 (kànjiàn) specifically means "to see" as in "to spot/notice", different from just 看 (kàn)
```

I want to generate high-quality speech audio for the individual dialogue lines.

Help me write a python script that uses the google cloud text to speech service to generate speech-to-text.

Given a yaml with dialogues like this, generate audio for each line of chinese text and save it as an audio file. To decide the file name, hash the chinese text string for content addressing. Output an updated yaml with `a: generated_audio_filename.extension` attributes added for individual dialogue lines.

Use different voices for different speakers.

Let's use TextToSpeechAsyncClient from google's google-cloud-texttospeech python library.

let's take advantage of the asynchrony to do batching

let's use google application default credentials if available.

let's take the following as flags:
* -i, --input-yaml: input yaml file
* -d, --audio-output-dir: dir to output audio to
* -b, --batch_size
by default, output the with_audio yaml to the audio-output-dir


