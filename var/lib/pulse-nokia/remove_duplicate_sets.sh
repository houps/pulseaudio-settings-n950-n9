pushd algs

for alg in * ; do
  echo processing: $alg
  echo ==========

  pushd $alg
  for file in set* ; do
    echo checking duplicates of: $file

    if [ -f $file ] ; then
      for compare in set* ; do
          if [ $file != $compare ] ; then
             diff $file $compare > /dev/null
             if [ $? -eq 0 ] ; then
               echo $file and $compare match, combining

               rm $compare

               pushd ../../modes
               for mode in * ; do
                  pushd $mode
                  ls -l $alg | grep $compare
                  if [ $? -eq 0 ] ; then
                    echo $mode uses the duplicate set, re-linking
                    rm $alg
                    ln -s ../../algs/$alg/$file $alg
                  fi
                  popd
               done
               popd

             fi
          fi
      done
    fi
  done
  popd

done

popd

