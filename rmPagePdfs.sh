for dirs in $(find /root/renminRibao/pdf | grep -v -E '\.pdf$' | grep -E '201[7-8]/[0-9]{2}/[0-9]{2}')
do 
  echo $dirs
  rm -r $dirs
done
