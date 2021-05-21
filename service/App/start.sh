#!/bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y install mariadb-client
apt-get clean
rm -rf /var/lib/apt/lists/*