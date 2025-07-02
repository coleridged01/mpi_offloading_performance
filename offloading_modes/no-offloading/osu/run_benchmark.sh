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
  COLLECTIVES=("allgather" "allreduce" "alltoall" "bcast" "gather" "reduce" "reduce_scatter" "scatter"
             "iallgather" "ialltoall" "ibcast" "igather" "iscatter" "iallgatherv" "ialltoallv" "allgatherv" "alltoallv")
  HCOLL="."
  use_install newinstall
  PR="$HOME/Benchmarking/newinstall/ompi"
elif [ "$LIB" = "han" ]; then
  COLLECTIVES=("allgather" "allreduce" "alltoall" "bcast" "gather" "reduce" "scatter" "allgatherv" "alltoallv")
  HCOLL="."
  use_install newinstall
  PR="$HOME/Benchmarking/newinstall/ompi"
elif [ "$LIB" = "hcoll" ]; then
  COLLECTIVES=("allgather" "allreduce" "alltoall" "reduce" "iallgatherv" "ialltoallv" "allgatherv" "alltoallv")
  HCOLL="hcoll"
  use_install hcollinstall
  PR="$HOME/Benchmarking/hcollinstall/ompi"
else
  echo "Error: Missing required flags."
  echo "Usage: $0 -s <setup> -n <numprocs> -l <ucc|han|hcoll> -t <target>"
  exit 1
fi

mkdir -p "$TARGET"

HOSTFILE="../../../setup/${SETUP}/hostfile"

if [ ! -r "$HOSTFILE" ]; then
    echo "Setup $SETUP not configured!"
    exit 1
fi

for COLL in "${COLLECTIVES[@]}"; do
  BIN="../../../bmrkbackend/${HCOLL}/osu/collective/osu_${COLL}"
  echo "Running $LIB benchmark: $COLL"
  OUTPUT_FILE="${TARGET}/${COLL}.txt"
  mpirun --prefix "$PR" -x PATH -x LD_LIBRARY_PATH -hostfile "$HOSTFILE" --mca coll_hcoll_np 1 --map-by node --bind-to core \
    -np "$NPROCS" --mca pml ucx --mca osc ucx --mca coll_"$LIB"_enable 1 \
    --mca coll_"$LIB"_priority 100 "$BIN" > "$OUTPUT_FILE"
done

