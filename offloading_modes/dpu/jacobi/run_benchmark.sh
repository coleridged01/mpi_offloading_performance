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
  echo "Usage: $0 -s <setup> -n <numprocs> -l <ucc> -t <target>"
  exit 1
fi

if [ "$LIB" = "ucc" ]; then
  #This is a custom bash function specified to target the DPU-enabled MPI installation
  use_install dosinstall
  PR="$HOME/Benchmarking/dosinstall/ompi"
else
  echo "Error: Missing required flags."
  echo "Usage: $0 -s <setup> -n <numprocs> -l <ucc> -t <target>"
  exit 1
fi

HOSTFILE="../../../setup/${SETUP}/hostfile"

if [ ! -r "$HOSTFILE" ]; then
    echo "Setup $SETUP not configured!"
    exit 1
fi

mkdir -p "$TARGET"

# Change dpu hostnames
DPUENV="-x DPU_OFFLOAD_LIST_DPUS=dpu1,dpu2 -x DPU_OFFLOAD_SERVER_PORT=11111 -x OFFLOAD_CONFIG_FILE_PATH=$HOME/Benchmarking/mpibenchmarks/bmrkbackend/dpu/config.txt"

if [[ "$(echo "$SETUP" | tr -cd '-' | wc -c)" -eq 2 && "$SETUP" == 4* ]]; then
    NODES="4"
else
    NODES="2"
fi

BIN="../../../bmrkbackend/dpu/jacobi/jacobi"
echo "Running $LIB Jacobi benchmark"
OUTPUT_FILE="${TARGET}/jacobi.txt"

# Change dpu hostnames and user
if [ "$NODES" = "2" ]; then
  DPUENV="-x DPU_OFFLOAD_LIST_DPUS=dpu1,dpu2 -x DPU_OFFLOAD_SERVER_PORT=11111 -x OFFLOAD_CONFIG_FILE_PATH=$HOME/Benchmarking/mpibenchmarks/bmrkbackend/dpu/config.txt"
  ssh user@dpu1 "cd /home/user/install/dos/bin && ./hostconfig.sh" &
  ssh user@dpu2 "cd /home/user/install/dos/bin && ./hostconfig.sh" &
elif [ "$NODES" = "4" ]; then
  DPUENV="-x DPU_OFFLOAD_LIST_DPUS=dpu1,dpu2,dpu3,dpu4 -x DPU_OFFLOAD_SERVER_PORT=11111 -x OFFLOAD_CONFIG_FILE_PATH=$HOME/Benchmarking/mpibenchmarks/bmrkbackend/dpu/config4.txt"
  ssh user@dpu1 "cd /home/user/install/dos/bin && ./hostconfig4.sh" &
  ssh user@dpu2 "cd /home/user/install/dos/bin && ./hostconfig4.sh" &
  ssh user@dpu3 "cd /home/user/install/dos/bin && ./hostconfig4.sh" &
  ssh user@dpu4 "cd /home/user/install/dos/bin && ./hostconfig4.sh" &
fi
sleep 4

THRESH="-x UCX_RNDV_THRESH=16K"

mpirun --prefix "$PR" -x PATH -x LD_LIBRARY_PATH $DPUENV $THRESH -hostfile "$HOSTFILE" --map-by node \
  --bind-to core -np "$NPROCS" --mca pml ucx --mca osc ucx --mca coll_"$LIB"_enable 1 \
  --mca coll_"$LIB"_priority 100 "$BIN" 32768 100  > "$OUTPUT_FILE"
