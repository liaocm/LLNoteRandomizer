#!/usr/bin/env python3

import io, sys, argparse
import json, random

MIN_SPACE = 0.09

def in_range(note, trange):
  if note['effect'] == 3 or note['effect'] == 13:
    note_range = (note['timing_sec'], note['timing_sec'] + note['effect_value'])
  else:
    note_range = (note['timing_sec'], note['timing_sec'] + 0.01)

  #([)]
  if trange[0] <= note_range[0] and trange[1] >= note_range[0]:
    return 1

  #[(])
  if trange[0] >= note_range[0] and trange[0] <= note_range[1]:
    return 1

  #([])
  if trange[0] <= note_range[0] and trange[1] >= note_range[1]:
    return 1

  if trange[0] > note_range[1]:
    return 2

  return 0



def avail_location(notes, time, trange=MIN_SPACE):
  return avail_locationEX(notes, time, MIN_SPACE, MIN_SPACE)

def avail_locationEX(notes, time, ts, te):
  taken = set()
  for note in notes:
    check = in_range(note, (time-ts, time+te))
    if check == 1:
      taken.add(note['position'])
    elif check == 2:
      break

  avail = {1,2,3,4,5,6,7,8,9}
  return list(avail - taken)


def randomize_swing_group(notes, group, mode):
  if mode == 'f':
    return

  fail = False
  note = group[0]
  note_t = note['timing_sec']
  avail_locs = avail_location(notes, note_t)
  note['position'] = avail_locs[random.randint(0, len(avail_locs)-1)]

  if mode == 'w':
    last = note['position']
    for note in group[1:]:
      avail_locs = avail_location(notes, note['timing_sec'], trange=MIN_SPACE*1.5)
      if last+1 in avail_locs and last-1 in avail_locs:
        movement = -1 if random.randint(0, 1) else 1
        note['position'] = last + movement
        last = note['position']
      elif last+1 in avail_locs:
        note['position'] = last + 1
        last = note['position']
      elif last-1 in avail_locs:
        note['position'] = last - 1
        last = note['position']
      else:
        #epic fail
        fail = True
        break
  elif mode == 'p':
    last = note['position']
    last_dir = -1 if random.randint(0, 1) else 1
    for note in group[1:]:
      avail_locs = avail_location(notes, note['timing_sec'], trange=MIN_SPACE*1.5)
      if last+last_dir in avail_locs:
        note['position'] = last + last_dir
        last = note['position']
      elif last-last_dir in avail_locs:
        last_dir = -last_dir
        note['position'] = last + last_dir
        last = note['position']
      else:
        fail = True
        break

  if fail:
    for note in group:
      note['position'] = 0
    return randomize_swing_group(notes, group, mode)

  return

def randomize_remaining_notes(notes, group, mode):
  fail = False
  random_group = group
  if mode == 'f':
    random_group = notes

  for note in random_group:
    if note['effect'] == 3 or note['effect'] == 13:
      avail_locs = avail_locationEX(notes, note['timing_sec'], MIN_SPACE, note['effect_value']+MIN_SPACE)
    else:
      avail_locs = avail_location(notes, note['timing_sec'])
    if not avail_locs:
      # epic fail
      fail = True
      break
    note['position'] = avail_locs[random.randint(0, len(avail_locs)-1)]

  if fail:
    for note in random_group:
      note['position'] = 0
    return randomize_remaining_notes(notes, group, mode)

  return

def main(fname, mode):
  try:
    fd = io.open(fname, 'r')
    content = fd.read()
    fd.close()
    notes = json.loads(content)
  except BaseException:
    sys.exit("Error loading or parsing the JSON file.")

  if not mode or mode not in {"f", "w", "p"}:
    mode = 'p'

  #if mode == 'f':

  # Clear old notes' locations
  for note in notes:
    note['position'] = 0

  # Group different notes
  group_numbers = max([x['notes_level'] for x in notes])
  groups = []
  for i in range(group_numbers):
    curr_group = []
    for note in notes:
      if note['notes_level'] == i + 1:
        curr_group.append(note)
    groups.append(curr_group)

  for group in groups[1:]:
    randomize_swing_group(notes, group, mode)

  randomize_remaining_notes(notes, groups[0], mode)

  try:
    fd = io.open(fname+'.randomized.json', 'w')
    content = json.dumps(notes)
    fd.write(content)
    fd.close()
  except BaseException:
    sys.exit("Error writing back JSON.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to a JSON note file.")
    parser.add_argument("--mode", help="Randomization mode. Option: f, w, p.")
    args = parser.parse_args()
    main(args.file, args.mode)