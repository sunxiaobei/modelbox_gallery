# !/usr/bin/bash

BASE_PATH=$(cd `dirname $0`;pwd)

function generate_oaep()
{
  echo "If you already have the OAEP public key and private key, enter \"no\"."
  echo "Are you sure you want to automatically generate the OAEP public key and private key (yes/no)?"
  read -r YN
  if [ -z ${YN} ]; then
    YN="yes"
  fi
  if [ ${YN} == "yes" ]; then
    bash modelbox_generate_oaep.sh
    if [ $? -ne 0 ]; then
      echo "failed to generate oaep"
      return $?
    fi
  else
    echo "Enter the path of the public key certificate file."
    read -r PUBLIC_PATH
    if [ -z ${PUBLIC_PATH} ] || [ ! -f ${PUBLIC_PATH} ]; then
      echo "The public key certificate file does not exist."
      return 1
    fi
    cp ${PUBLIC_PATH} "./oaep.pub"
    echo "Enter the path of the private key certificate file."
    read -r PRIVATE_PATH
    if [ -z ${PRIVATE_PATH} ] || [ ! -f ${PRIVATE_PATH} ]; then
      echo "The private key certificate file does not exist."
      return 1
    fi
    cp ${PRIVATE_PATH} "./oaep.key"
  fi
  PUBLIC_PATH="./oaep.pub"
  PRIVATE_PATH="./oaep.key"

  if [ ! -f ${PUBLIC_PATH} ]; then
    echo "The public key certificate file does not exist."
    return 1
  fi
  
  if [ ! -f ${PRIVATE_PATH} ]; then
    echo "The private key certificate file does not exist."
    return 1
  fi
  echo ""
  modelbox_ma_tool -m oaep
  echo "manual generate oaep success"
}

function clean_oaep_resources()
{
  if [ ${BASE_PATH} == "/usr/local/etc/modelbox/cert" ]; then
    return 1
  fi
  if [ -f "./oaep.pub" ]; then
    rm "./oaep.pub"
  fi

  if [ -f "./oaep.key" ]; then
    rm "./oaep.key"
  fi
  return 0
}

function generate_https()
{
  MODELBOX_KEY="./https_cert.key"
  MODELBOX_PEM="./https_cert.pem"
  MODELBOX_DER="./https_cert.der"
  echo "If you already have the HTTPS certificates, enter \"no\"."
  echo "Are you sure you want to automatically generate the HTTPS certificates (yes/no)?"
  read -r YN
  if [ -z ${YN} ]; then
    YN="yes"
  fi
  echo ""
  if [ ${YN} == "yes" ]; then
    bash modelbox_generate_https.sh
    if [ $? -ne 0 ];then
      echo "failed to generate_https"
      return $?
    fi
  else
    echo "Enter the path of the https private key certificate file."
    read -r PRIVATE_PATH
    if [ -z ${PRIVATE_PATH} ] || [ ! -f ${PRIVATE_PATH} ]; then
      echo "The private key certificate file does not exist."
      return 1
    fi
    cp ${PRIVATE_PATH} ${MODELBOX_KEY}
    echo "Enter the path of the https pem certificate file."
    read -r CERTIFICATE_PATH
    if [ -z ${CERTIFICATE_PATH} ] || [ ! -f ${CERTIFICATE_PATH} ]; then
      echo "The https pem certificate file does not exist."
      return 1
    fi
    cp ${CERTIFICATE_PATH} ${MODELBOX_PEM}
    echo "Enter the path of the https der certificate file."
    read -r DER_PATH
    if [ -z ${DER_PATH} ] || [ ! -f ${DER_PATH} ]; then
      echo "The https der certificate file does not exist."
      return 1
    fi
    cp ${DER_PATH} ${MODELBOX_DER}
  fi

  if [ ! -f ${MODELBOX_KEY} ]; then
    echo "The private key certificate file does not exist."
    return 1
  fi
  if [ ! -f ${MODELBOX_PEM} ]; then
    echo "The https certificate pem file does not exist."
    return 1
  fi
  if [ ! -f ${MODELBOX_DER} ]; then
    echo "The https certificate der file does not exist."
    return 1
  fi
  
  modelbox_ma_tool -m https
  echo "manual generate https success"
  return 0
}

function clean_https_resources()
{
  if [ ${BASE_PATH} == "/usr/local/etc/modelbox/cert" ]; then
    return 1
  fi
  if [ -f "./https_cert.key" ]; then
    rm "./https_cert.key"
  fi

  if [ -f "./https_cert.pem" ]; then
    rm "./https_cert.pem"
  fi

  if [ -f "./https_cert.der" ]; then
    rm "./https_cert.der"
  fi
  return 0
}

function generate_id_code() {
  echo ""
  echo "Are you sure you want to automatically config the identification code (yes/no)?"
  read -r YN
  if [ -z ${YN} ]; then
    YN="yes"
  fi
  if [ ${YN} == "yes" ]; then
    modelbox_ma_tool -m idcode
    return
  fi

  echo ""
  echo "Enter the identification code, length less than 32, the maximum length is 4096."
  read -r ID_CODE
  ID_CODE_LENGTH=${#ID_CODE}
  if [ ${ID_CODE_LENGTH} -lt 32 ] || [ ${ID_CODE_LENGTH} -gt 4096 ]; then
    echo "The identification code is invalid!"
    return
  fi
  modelbox_ma_tool -e ${ID_CODE}
}

function main() {
  echo "=====================Config OAEP certificate====================================================="
  echo "The OAEP public key and private key are mainly used for huawei cloud ModelArts service video inference, enter \"no\"."
  echo "Are you sure you want to config the OAEP public key and private key (yes/no)?"
  read -r OAEP_YN
  if [ -z ${OAEP_YN} ]; then
    OAEP_YN="yes"
  fi
  if [ ${OAEP_YN} == "yes" ]; then
    echo ""
    generate_oaep
    clean_oaep_resources
    if [ $? -ne 0 ]; then
      echo "Don't operate /usr/local/etc/modelbox/cert."
    fi
  fi

  echo ""
  echo "=====================Config HTTPS certificate====================================================="
  echo "The HTTPS certificates are mainly used for HTTPS services. If they are not involved, enter \"no\"."
  echo "Are you sure you want to config an HTTPS certificate (yes/no)?"
  read -r HTTPS_YN
  if [ -z ${HTTPS_YN} ]; then
    HTTPS_YN="yes"
  fi
  if [ ${HTTPS_YN} == "yes" ]; then
    echo ""
    generate_https
    clean_https_resources
    if [ $? -ne 0 ]; then
      echo "Don't operate /usr/local/etc/modelbox/cert."
    fi
  fi

  echo ""
  echo "=====================Config identification code====================================================="
  echo "Are you sure you want to config an identification code (yes/no)?"
  read -r IDCODE_YN
  if [ -z ${IDCODE_YN} ]; then
    IDCODE_YN="yes"
  fi
  if [ ${IDCODE_YN} == "yes" ]; then
    generate_id_code
  fi
}

main