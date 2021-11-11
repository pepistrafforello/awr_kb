#!/bin/bash

i=1
n_alpha=6
n_shards=2
#dgraph_data=../../dgraph-data
dgraph_data=../../dgraph-data-no-docker

while [ $i -le $n_alpha ] ; do
	s=$(( (i - 1) / ( n_alpha / n_shards) ))
	source_dir=out/${s}/p
	target_dir=${dgraph_data}/alpha${i}/p
	echo $source_dir: $target_dir
	sudo \rm -rf $target_dir
	sudo cp -r $source_dir $target_dir
	((i++))
done
