import argparse
import os
import random
import subprocess
import tempfile
import vlc

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_dir',
        type=str,
        help='directory of mp3 files',
    )
    parser.add_argument(
        '--num_samples',
        type=int,
        help='number of chords to sample',
    )
    parser.add_argument(
        '--random_seed',
        type=int,
        help='random seed',
    )
    return parser.parse_args()

def list_dir(path, ext):
    for dirpath, _, filenames in os.walk(os.path.abspath(path)):
        for filename in filenames:
            if filename.endswith(ext) and '_' in filename:
                yield os.path.join(dirpath, filename)

def to_note(path):
    base = os.path.basename(path)
    tokens = os.path.splitext(base)[0].split('_')
    note = tokens[0].upper()
    if tokens[1] == 'minor':
        return note + 'm'
    else:
        return note

def concat_files(filenames, output_filename):
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        sample_filename = f.name
        for filename in filenames:
            print("file '{}'".format(filename), file=f)
    cmd = [
        'ffmpeg',
        '-f',
        'concat',
        '-safe',
        '0',
        '-i',
        sample_filename,
        '-c',
        'copy',
        '-y',
        output_filename,
    ]
    res = subprocess.run(cmd, stderr=subprocess.DEVNULL)
    return res.returncode

def uniq(v):
    return sorted(list(set(v)))

def play_guess(actual):
    notes = uniq(actual)
    print('Used notes:', ' '.join(notes))
    lower_notes = [note.lower() for note in notes]
    num_samples = len(actual)
    guess = []
    while len(guess) < num_samples:
        val = input('> ')
        if val.lower() in lower_notes:
            guess.append(val)
        else:
            print('Input not recognized')
    correct = 0
    for x, y in zip(guess, actual):
        if x.lower() == y.lower():
            print('Correct guess', y)
            correct += 1
        else:
            print('Wrong guess', x, 'instead of', y)
    print(correct, 'out of', num_samples)
    print('Score:', float(correct) / num_samples)

def play_shuffle_round(samples):
    with open('solution.txt', 'w') as f:
        for s in samples:
            print(to_note(s), file=f)
    output_filename = 'samples.mp3'
    res = concat_files(samples, output_filename)
    print('Code returned from ffmpeg', res)
    p = vlc.MediaPlayer(output_filename)
    p.play()
    actual = [to_note(s) for s in samples]
    play_guess(actual)

def main():
    args = parse_args()
    dirs = list_dir(args.input_dir, '.mp3')
    random.seed(args.random_seed)
    samples = random.sample(list(dirs), args.num_samples)
    random.seed()
    random.shuffle(samples)
    play_shuffle_round(samples)
    '''
    print('pos', p.get_position())
    p.stop()
    p.set_position(0)
    p.play()
    '''

if __name__ == '__main__':
    main()
