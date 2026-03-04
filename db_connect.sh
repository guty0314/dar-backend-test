#!/bin/bash
ssh -i ../.ssh/DAR.pem \
-f -N -L 5433:ls-12d7b609c2b3f5bc72b708b72e5db7a4547c7783.cjft96j28czt.us-east-1.rds.amazonaws.com:5432 \
ubuntu@34.229.78.137
