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

mkdir -p "$TARGET"

BIN="../../../bmrkbackend/${HCOLL}/jacobi/jacobi"
echo "Running $LIB Jacobi benchmark"
OUTPUT_FILE="${TARGET}/jacobi.txt"
HOSTFILE="../../../setup/${SETUP}/hostfile"

if [ ! -r "$HOSTFILE" ]; then
    echo "Setup $SETUP not configured!"
    exit 1
fi

# Enables Hardware Tag Matching
TMARG="-x UCX_DC_MLX5_TM_ENABLE=y -x UCX_RC_MLX5_TM_ENABLE=y -x UCX_TLS=rc,dc,sm,self "
THRESH="-x UCX_RNDV_THRESH=16K"

mpirun --prefix "$PR" $TMARG -x PATH -x LD_LIBRARY_PATH -hostfile "$HOSTFILE" $THRESH --map-by node --bind-to core -np "$NPROCS" --mca pml ucx \
  --mca osc ucx --mca coll_"$LIB"_enable 1 --mca coll_"$LIB"_priority 100 \
  "$BIN" 32768 100  > "$OUTPUT_FILE"
