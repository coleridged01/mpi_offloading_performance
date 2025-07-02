#!/bin/bash

SSET=false
NSET=false
LSET=false
TSET=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit

source "${HOME}/.bashrc"

while getopts "s:p:l:t:" opt; do
  case $opt in
    s)
      SETUP=$OPTARG
      SSET=true
      ;;
    p)
      NPROCS=$OPTARG
      NSET=true
      ;;
    l)
      LIB=$OPTARG
      LSET=true
      ;;
    t)
      TARGET=$OPTARG
      TSET=true
      ;;
    *)
      ;;
  esac
done

if [ "$SSET" != "true" ] || [ "$NSET" != "true" ] || [ "$LSET" != "true" ] || [ "$TSET" != "true" ]; then
  echo "Error: Missing required flags."
  echo "Usage: $0 -s <setup> -n <numprocs> -l <ucc|han|hcoll> -t <target>"
  exit 1
fi

if [ "$LIB" = "ucc" ]; then
  HCOLL="."
  #This is a custom bash function specified to target the HCOLL-compatible MPI installation
  use_install newinstall
  PR="$HOME/Benchmarking/newinstall/ompi"
elif [ "$LIB" = "han" ]; then
  HCOLL="."
  use_install newinstall
  PR="$HOME/Benchmarking/newinstall/ompi"
elif [ "$LIB" = "hcoll" ]; then
  HCOLL="hcoll"
  use_install hcollinstall
  PR="$HOME/Benchmarking/hcollinstall/ompi"
else
  echo "Error: Missing required flags."
  echo "Usage: $0 -s <setup> -n <numprocs> -l <ucc|han|hcoll> -t <target>"
  exit 1
fi

HOSTFILE="../../../setup/${SETUP}/hostfile"

if [ ! -r "$HOSTFILE" ]; then
    echo "Setup $SETUP not configured!"
    exit 1
fi

mkdir -p "$TARGET"

BIN="../../../bmrkbackend/${HCOLL}/fourier/bench_c2c_cpp"
echo "Running $LIB P3DFFT++ benchmark"
OUTPUT_FILE="${TARGET}/fourier.txt"

mpirun --prefix "$PR" -x PATH -x LD_LIBRARY_PATH -hostfile "$HOSTFILE" --map-by node \
    --bind-to core -np "$NPROCS" --mca pml ucx --mca osc ucx --mca coll_"$LIB"_enable 1 \
    --mca coll_"$LIB"_priority 100 "$BIN" > "$OUTPUT_FILE"

