PREFIX=20210729

if [ -z ${AWS_ACCESS_KEY_ID+x} ] || [ -z ${AWS_SECRET_ACCESS_KEY+x} ] ; then
        . auth.sh
fi

rm -f /tmp/CHECKSUMS.md5

pushd ../../dgraph-data

for i in zero1 zero2 zero3 alpha1 alpha4 ; do
	echo packaging $i...
	ARCHIVE=${i}.tar
	tar cf /tmp/${ARCHIVE} ${i}
	pushd /tmp
	md5sum ${ARCHIVE} >> CHECKSUMS.md5
	echo uploading $i...
	aws s3 cp ${ARCHIVE} s3://esusa/dgraph/wd${PREFIX}/${i}.tar
	popd
done

aws s3 cp /tmp/CHECKSUMS.md5 s3://esusa/dgraph/wd${PREFIX}/CHECKSUMS.md5

popd
