# LLNoteRandomizer
A script to help randomizing notes with swing icons.

## Usage
``python3 note.py [--mode MODE] path/to/note/json``

### Note JSON
This is a JSON file containing note information. It should be a list of key-value pairs.

### Mode
- f Forced random mode. Randomize all notes as regular notes including swing notes.
- w Random Walk mode. For swing notes, fix the beginning position and randomize the path with uncertain direction.
- p [default] Path mode. For swing notes, randomize the start and end position of paths. The direction remains uniform for each path.

### Output
The script outputs randomized JSON in the same directory as that of the input file.
