ulimit -f 100000
#export PATH=~/go/bin:/data2/pepi/node/node-v14.17.6-linux-x64/bin:$PATH
strace -o /tmp/strace.log -f -s256 ~/go/bin/dgraph bulk --mapoutput_mb 512 -f input_data -s schema.txt --map_shards=4 --reduce_shards=2 --http localhost:8000 --zero=localhost:5080 # NO DOCKER
#DOCKER# dgraph bulk -f input_data -s schema.txt --map_shards=4 --reduce_shards=2 --http localhost:8000 --zero=zero1:5080
#dgraph bulk -f input_data.minimal -s schema.txt --map_shards=4 --reduce_shards=1 --http localhost:8000 --zero=zero1:5080


