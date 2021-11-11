#!/bin/bash

if [ -z ${AWS_ACCESS_KEY_ID+x} ] || [ -z ${AWS_SECRET_ACCESS_KEY+x} ] ; then
	. auth.sh
fi

AWS_PREFIX=s3://esusa/tmp/wikidata-20210614-all
aws s3 cp ${AWS_PREFIX}/md5sums.txt .

while read line
do
	fields=( $line )
	FILE=${fields[1]}
	SUM=${fields[0]}
	echo file: $FILE
	echo sum: $SUM
	[ -e $FILE ] || touch $FILE
	MD5OPT=--status
	while ! echo "$SUM $FILE" | md5sum -c --strict $MD5OPT
	do
		MD5OPT=""
		echo downloading $FILE...
		aws s3 cp ${AWS_PREFIX}/$FILE .
	done
done < md5sums.txt

