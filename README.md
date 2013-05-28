===================================
The LabROSA aligned lyrics database
===================================

This repository contains phoneme-aligned lyrics data for use
in automatic lyric transcription.  This is based on the following
work:

@inproceedings{mcvicar2013dataset,
  title={A Dataset of Phoneme-Aligned Lyrics for use in Automatic Lyric Transcription from Auio (submitted)},
  author={McVicar, M. and Ellis, D.},
  booktitle={14th International Society for Music Information Retrieval (ISMIR)},
  year={2013}
}

With further information available here:

[link]

--------
Contents
--------

1. Audio
We have split the audio into train and test splits. Additionally, 
the data is split into mostly containing sung or rapped vocals.
For each of these songs, we provide acapella, polyphonic and synthesized
audio, available here:

[link]

The number of tracks in each of these settings is below:

--------------------------
|          Train |  Test |
--------------------------
| Sung   |  153  |  221  |
| Rapped |  142  |  283  |
-------------------------

Note that results reported in the ISMIR paper were on the
training set. This is additionally the data we used
to train the acoustic models.

2. Lyrics data
For each song, we provide the raw lyrics scraped from the web,
a phoneme-level alignment, and a word-level alignment. The format
for each of these is listed below:

*.lyrics. Flat file with lines delimited by [linebreak]
*.words. One line per word with start time in seconds: <start><space><word>
*.phones. One line per phoneme, <start><space><phone> 

3. Models
Acoustic and language models are available for download
from 

[link]

4. Evaluation
The main script for evaluation is align_words.pl. It is a command
line script which takes two files as input and outputs the minimum
number of Insertions (I), Deletions (D) and Substitutions (S) to 
convert the transcript to the reference. The Word Error Rate (WER)
for a reference of N words is then:

>       I + S + D
>WER =  ---------
>           N

The Phoneme Error Rate may be defined analagously. We have built
a python wrapper for align_words.pl in which you can specify a
transcript and reference directory. 

5. Predictions
We include our best transcripts from the above paper for
reproducability.

