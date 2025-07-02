#!/bin/bash

BSET=false
NSET=false

OFFLOAD=("no-offloading" "tm" "dpu")
LIBS=("ucc" "hcoll" "han")

while getopts "b:n:" opt; do
  case $opt in
    b)
      BMARK=$OPTARG
      BSET=true
      ;;
    n)
      NODES=$OPTARG
      NSET=true
      ;;
    *)
      ;;
  esac
done

if [ "$BSET" != "true" ] || [ "$NSET" != "true" ]; then
  echo "Error: Missing required flags."
  echo "Usage: $0 -b <osu|fourier|jacobi> -n <2|4>"
  exit 1
fi

if [ "$BMARK" != "osu" ] && [ "$BMARK" != "jacobi" ] && [ "$BMARK" != "fourier" ]; then
  echo "Usage: $0 -b <osu|fourier|jacobi> -n <nodes>"
  exit 1
fi

if [ "$NODES" = "2" ]; then
  SETUPS=("one-to-one" "4-dist" "8-dist" "16-dist" "32-dist" "64-dist")
  NPS=("2" "4" "8" "16" "32" "64")
elif [ "$NODES" = "4" ]; then
  SETUPS=("4-4-dist" "4-8-dist" "4-16-dist" "4-32-dist" "4-64-dist")
  NPS=("4" "8" "16" "32" "64")
else
  echo "Usage: $0 -b <osu|fourier|jacobi> -n <nodes>"
  exit 1
fi

for i in "${!SETUPS[@]}"; do
  SETUP="${SETUPS[$i]}"
  NP="${NPS[$i]}"
  for OFF in "${OFFLOAD[@]}"; do
    for LIB in "${LIBS[@]}"; do
      SCRIPT="./$OFF/$BMARK/run_benchmark.sh"
      TARGET="$PWD/benchmarks/$BMARK/$SETUP/$LIB/$OFF/extended"
      if [ -x "$SCRIPT" ]; then
        "$SCRIPT" -s "$SETUP" -p "$NP" -l "$LIB" -t "$TARGET"
      else
        echo "Error: Script $SCRIPT not found or not executable"
        exit 1
      fi
    done
  done
done






