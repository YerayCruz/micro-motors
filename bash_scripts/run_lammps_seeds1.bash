#!/bin/bash

LMP_SERIAL="$HOME/Documents/Projects/tetrahedron/lmp_serial"

freq=$1

input_file="seeds_1"
last_process_file="last_process_${freq}.txt"

if [ ! -f "$input_file" ]; then
  echo "Error: Input file $input_file not found" >&2
  exit 1
fi

# Outer loop: frequencies
# Inner loop: seeds
while IFS= read -r seed; do
  seed=$(echo "$seed" | xargs) # Trim whitespace
  [ -z "$seed" ] && continue   # Skip empty lines

  data_file="mag_ratchet_${freq}Hz_${seed}.lmpin"

  if [ -f "$data_file" ]; then
    echo "Processing $data_file"
    "$LMP_SERIAL" -in "$data_file"
    # Your command here (runs for 1 frequency across all seeds)

    echo "$data_file" >"$last_process_file"

  else
    echo "Warning: Data file $data_file not found" >&2
  fi
done <"$input_file"

echo "Processing complete"
