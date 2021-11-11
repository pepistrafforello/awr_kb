<!--
   Copyright 2021 Expert System USA, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Importing Wikidata to DGraph

## Downloading Wikidata dump

use `wikidata-tools/wd_download_latest.sh` to download the most recent Wikidata dump to file `latest-all.json.bz2`

## Converting Wikidata dump to RDF N-quads

check/change hard-coded input file name in wikidata-tools/wd2dgraph2.py

```
cd wikidata-tools
mkdir input_data
./run_chunks.sh # runs python wd2dgraph2.py START END splitting the work in 10 concurrent chunks
```

The input consists of file `latest-all.json.bz2`, hard-coded in `wikidata-tools/wd2dgraph2.py`

The N-quads files will be created in folder input_data; there will be more than 3M files (3,276,356 as of July 2021), taking 41 GB of disk space.

## Note about the schema

The schema definition is in `wikidata-tools/schema.txt`

## Bulk loading DGraph

From folder awr_kb/DGraph/docker:
```
rm -rf ../../../dgraph-data
mkdir ../../../dgraph-data
pushd ../../../dgraph-data
mkdir alpha1  alpha2  alpha3  alpha4  alpha5  alpha6  zero1  zero2  zero3
popd
./create_zeros.sh
# wait at least 1 minute
docker-compose exec bulk_loader bash
./bulk_load.sh
```

## Deploying to DGraph (development server)

From folder awr_kb/wikidata-tools:
```
./dgraph_copy.sh
```
From folder awr_kb/DGraph/docker:
```
# start the first node on the first shard
docker-compose scale alpha1=1
# wait a couple minutes
docker-compose logs alpha1=1 > /tmp/alpha1.log
# verify that the log shows "server ready" as opposed to "can't connect to group leader" or similar stuff

# start the first node on the second shard
docker-compose logs alpha4=1 > /tmp/alpha4.log
# verify that the log shows "server ready"

# start the rest of the cluster
docker-compose up -d
```

## Deploing to DGraph (application server)
**IMPORTANT**: read and apply [Using “p” directories coming from different Dgraph clusters](https://dgraph.io/docs/master/deploy/fast-data-loading/bulk-loader/#using-p-directories-coming-from-different-dgraph-clusters) by running
```shell
curl 'localhost:6080/assign?what=timestamps&num=1000000' | jq
```

To load the mutations, need to increas UIDs first
```shell
curl 'localhost:6080/assign?what=uids&num=110000000'
```
without that, we get errors like \
`Uid: [2600205] cannot be greater than lease: [10000]`

once DGraph is up, load the collections from the old AW, see kb_data/read.py

Script to run the whole workflow with our typical Docker deployment:
```shell
#!/bin/bash
cd /docker
docker-compose down
pushd /data/20210729
\rm -rf alpha1  alpha4  zero1
mkdir zero1
tar xf 0.tar
mv 0 alpha1
tar xf 1.tar
mv 1 alpha4
popd
docker-compose up --no-start
docker-compose start zero1

sleep 30

curl 'localhost:6080/assign?what=timestamps&num=1000000' | jq
curl 'localhost:6080/assign?what=uids&num=110000000' | jq

docker-compose start alpha1

sleep 60

docker-compose start alpha4

```

docker-compose.yml content:
```yml

version: '3.5'

services:
  ratel:
    image: 069455090175.dkr.ecr.us-east-1.amazonaws.com/dgraph-ratel
    ports:
      - "8000:8000"
    entrypoint:
      - "/usr/local/bin/dgraph-ratel"
      - "-addr"
      - "http://localhost:8000"
    deploy:
        resources:
            limits:
              cpus: 0.50
              memory: 512M
    restart: always

  zero1:
    image: dgraph/dgraph:latest
    working_dir: /data
    ports:
      - 5080
      - "6080:6080"
    labels:
      cluster: test
      service: zero
    volumes:
      - type: bind
        source: /data/20210729/zero1
        target: /data
    command: dgraph zero --my=zero1:5080 --replicas 1 --raft="idx=1" --logtostderr -v=2 --bindall --expose_trace --profile_mode block --block_rate 10 --telemetry "sentry=false"
    deploy:
        resources:
            limits:
              cpus: 0.50
              memory: 512M
    restart: always

  alpha1:
    image: dgraph/dgraph:latest
    working_dir: /data
    volumes:
      - type: bind
        source: /data/20210729/alpha1
        target: /data
    ports:
      - 7080
      - "8080:8080"
      - "9080:9080"
    labels:
      cluster: test
      service: alpha
    command: dgraph alpha --my=alpha1:7080 --zero=zero1:5080 --expose_trace --profile_mode block --block_rate 10 --logtostderr -v=2 --telemetry "sentry=false" --security whitelist=0.0.0.0/0
    deploy:
        resources:
            limits:
              cpus: 1
              memory: 7G
    restart: always

  alpha4:
    image: dgraph/dgraph:latest
    working_dir: /data
    volumes:
      - type: bind
        source: /data/20210729/alpha4
        target: /data
    ports:
      - 7080
      - 8080
      - 9080
    labels:
      cluster: test
      service: alpha
    command: dgraph alpha --my=alpha4:7080 --zero=zero1:5080 --expose_trace --profile_mode block --block_rate 10 --logtostderr -v=2 --telemetry "sentry=false"  --security whitelist=0.0.0.0/0
    deploy:
        resources:
            limits:
              cpus: 1
              memory: 7G
    restart: always


```
