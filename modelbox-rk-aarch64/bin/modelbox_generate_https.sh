# !/usr/bin/bash

main() {
  openssl genrsa -out https_cert.key 2048
  if [ $? -ne 0 ];then
    echo "failed to genrsa https key"
    return $?
  fi
  openssl req -new -x509 -days 3650 -key https_cert.key -out https_cert.pem
  if [ $? -ne 0 ];then
    echo "failed to generate x509"
    return $?
  fi
  openssl x509 -outform der -in https_cert.pem -out https_cert.der
  if [ $? -ne 0 ];then
    echo "failed to parse der"
    return $?
  fi
  return 0
}

main
exit $?

