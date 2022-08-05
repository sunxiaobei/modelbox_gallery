# !/usr/bin/bash

main() {
  openssl genrsa -out oaep.key 3072
  if [ $? -ne 0 ];then
    echo "failed genrsa oaep key"
    return $?
  fi
  openssl rsa -in oaep.key -pubout -out oaep.pub
  if [ $? -ne 0 ];then
    echo "failed genrsa oaep pub"
    return $?
  fi
  return 0
}

main
exit $?