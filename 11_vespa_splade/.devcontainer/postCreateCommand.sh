#!/usr/bin/env bash
set -ex

vespa config set target http://vespa:19071
vespa status
vespa deploy vespa-config --wait 30

echo "FINISH"