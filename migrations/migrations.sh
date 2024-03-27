#!/bin/bash

sh ./migrations/001_old_config_to_new_config.sh || exit 1
sh ./migrations/002_old_config_to_new_config.sh || exit 1
