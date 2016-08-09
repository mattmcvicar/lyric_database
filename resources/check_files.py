import argparse
import os
import string


def get_cl_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--audio-folder', '-f', type=str, required=True,
       help='folder of audio files. Each file should have a ".lyrics"'
            'extension')

    cl_args = vars(parser.parse_args())

    audio_root = cl_args['audio_folder']

    return audio_root


def load_dict(filename, comment):
    D = dict()
    with open(filename, 'r') as f:
        for line in f:
            if comment and line.startswith(comment):
                continue

            stuff = line.split()
            D[stuff[0]] = stuff[1:]

    return D


def get_filenames(root, ext):

    filenames = []
    for folder, subFolders, files in os.walk(root):
        if 'Holdout' in folder:
            continue

        for filename in files:
            if filename.endswith(ext):
                filenames.append(os.path.join(folder, filename))

    return set(filenames)


def get_local_name(p):
    return os.path.splitext(os.path.split(l)[-1])[0]


def check_words(lyric_names, pronounciations):
    exclude = [',', '?', '!', '-']
    bad_words = []
    for lyrics_file in lyric_names:
        with open(lyrics_file, 'r') as f:
            for line in f:
                if line.startswith('['):
                    continue

                if len(line) == 0:
                    continue

                line = ''.join(ch for ch in line if ch not in exclude)
                w = line.upper().strip().split()
                for ww in w:
                    if ww not in pronounciations and ww not in bad_words:
                        print '  WARNING:', ww, 'in', lyrics_file, 'has no pronounciation'
                        bad_words.append(ww)

    print '  a total of', len(bad_words), 'words with no pronounciation'


if __name__ == "__main__":

    # lyrics folder should be relative to where we are
    lyrics_root = '../lyrics/'

    # get audio folder
    audio_root = get_cl_args()

    # get files for each
    lyrics_names = get_filenames(lyrics_root, 'lyrics')
    audio_names = get_filenames(audio_root, 'wav')

    # check difference
    local_lyrics = set([get_local_name(l) for l in lyrics_names])
    local_audio = set([get_local_name(l) for l in audio_names])

    print ''
    print '  Checking for mismatch of files...'
    differences = local_lyrics.symmetric_difference(local_lyrics)
    for d in differences:
        if d not in lyrics_names:
            print '  WARNING:', d, 'has an audio file but no lyrics'
        else:
            print '  WARNING:', d, 'has a lyrics file but no audio'

    # get word pronounciations
    lyric_dict = load_dict('./Train_Test_Holdout.dict', None)
    cmu_dict = load_dict('./cmu.dict', ';;;')
    pronounciations = lyric_dict.copy()
    pronounciations.update(cmu_dict)

    # load up words
    words = check_words(lyrics_names, pronounciations)

print ''
print '  Everything else looks peachy!'
print '  Done'
print ''

