ulimit -n 100000
export PATH=~/go/bin:/data2/pepi/node/node-v14.17.6-linux-x64/bin:$PATH
dgraph bulk -f input_data -s schema.txt --map_shards=4 --reduce_shards=1 --http localhost:8000 --zero=localhost:5080

