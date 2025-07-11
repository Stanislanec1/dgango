#!/usr/bin/env bash
# wait-for-it.sh — Скрипт ожидания доступности хоста и порта
# https://github.com/vishnubob/wait-for-it

set -e

HOST=""
PORT=""
TIMEOUT=15
QUIET=0
STRICT=0
USAGE="Usage: wait-for-it.sh host:port [-t timeout] [-- command args]"

print_help() {
  echo "$USAGE"
}

error() {
  echo "$@" 1>&2
}

usage() {
  print_help
  exit 1
}

wait_for() {
  if [[ $TIMEOUT -gt 0 ]]; then
    echo "Waiting $TIMEOUT seconds for $HOST:$PORT"
  else
    echo "Waiting for $HOST:$PORT without timeout"
  fi

  start_ts=$(date +%s)
  while :
  do
    if nc -z "$HOST" "$PORT" >/dev/null 2>&1; then
      end_ts=$(date +%s)
      echo "$HOST:$PORT is available after $((end_ts - start_ts)) seconds"
      break
    fi
    sleep 1
    if [[ $TIMEOUT -gt 0 ]]; then
      now_ts=$(date +%s)
      if (( now_ts - start_ts >= TIMEOUT )); then
        echo "Timeout occurred after waiting $TIMEOUT seconds for $HOST:$PORT"
        return 1
      fi
    fi
  done
}

cmd_started=0

while [[ $# -gt 0 ]]
do
  case "$1" in
    *:* )
    HOST=$(echo "$1" | cut -d : -f 1)
    PORT=$(echo "$1" | cut -d : -f 2)
    shift 1
    ;;
    -q | --quiet)
    QUIET=1
    shift 1
    ;;
    -t)
    TIMEOUT="$2"
    if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
      error "Timeout argument must be a number"
      usage
    fi
    shift 2
    ;;
    --)
    shift
    cmd_started=1
    break
    ;;
    *)
    error "Unknown argument: $1"
    usage
    ;;
  esac
done

if [[ -z "$HOST" || -z "$PORT" ]]; then
  error "Host and port must be specified"
  usage
fi

wait_for

if [[ $cmd_started -eq 1 ]]; then
  exec "$@"
fi
