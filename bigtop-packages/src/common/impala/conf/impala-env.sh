#!/bin/bash

export IMPALA_BIN=${IMPALA_BIN:-/usr/lib/impala/sbin}
export IMPALA_HOME=${IMPALA_HOME:-/usr/lib/impala}
export HIVE_HOME=${HIVE_HOME:-/usr/lib/hive}
export HBASE_HOME=${HBASE_HOME:-/usr/lib/hbase}
export HADOOP_CONF_DIR=${HADOOP_CONF_DIR:-/etc/impala/conf}
export HIVE_CONF_DIR=${HIVE_CONF_DIR:-/etc/impala/conf}
export HBASE_CONF_DIR=${HBASE_CONF_DIR:-/etc/impala/conf}
export LIBHDFS_OPTS=${LIBHDFS_OPTS:--Djava.library.path=/usr/lib/impala/lib}

if [ "$ENABLE_CORE_DUMPS" == "true" ]; then
    ulimit -c unlimited
elif [ -z "$ENABLE_CORE_DUMPS" -o "$ENABLE_CORE_DUMPS" == "false" ]; then
    ulimit -c 0
else
    echo 'WARNING: $ENABLE_CORE_DUMPS must be either "true" or "false"'
fi

# Autodetect JAVA_HOME if not defined
. /usr/lib/bigtop-utils/bigtop-detect-javahome

# ensure that java has already been found
if [ -z "${JAVA_HOME}" ]; then
    echo "Unable to find Java. JAVA_HOME should be set in /etc/default/bigtop-utils"
    exit 1
fi

# Autodetect location of native java libraries
for library in libjvm.so libjsig.so libjava.so; do
    library_file=$(find ${JAVA_HOME}/ -name $library | head -1)
    if [ -n "$library_file" ]; then
        library_dir=$(dirname $library_file)
        export LD_LIBRARY_PATH=$library_dir:${LD_LIBRARY_PATH}
    fi
done
export LD_LIBRARY_PATH="${IMPALA_HOME}/lib:${IMPALA_BIN}:${LD_LIBRARY_PATH}"

export CLASSPATH="${IMPALA_CONF_DIR}:${HADOOP_CONF_DIR}:${HIVE_CONF_DIR}:${HBASE_CONF_DIR}:\
$IMPALA_HOME/lib:\
${CLASSPATH}"
for JAR_FILE in ${IMPALA_HOME}/*.jar; do
    export CLASSPATH="${JAR_FILE}:${CLASSPATH}"
done
if [ -n "${AUX_CLASSPATH}" ]; then
    export CLASSPATH="${AUX_CLASSPATH}:${CLASSPATH}"
fi

# Add non-standard kinit location to PATH
if [ -d /usr/kerberos/bin ]; then
    export PATH=/usr/kerberos/bin:${PATH}
fi
