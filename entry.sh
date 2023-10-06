#!/bin/bash
nohup python /opt/loghelper/openai.py 2>&1 &
/usr/local/openresty/bin/openresty -g "daemon off;"