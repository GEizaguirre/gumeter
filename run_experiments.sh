#!/bin/bash

gumeter deploy aws_lambda
gumeter deploy gcp_cloudrun
gumeter deploy code_engine

gumeter warmup aws_lambda
gumeter run-all aws_lambda  --num_replicas 5
gumeter warmup gcp_cloudrun
gumeter run-all gcp_cloudrun --num_replicas 5
gumeter warmup code_engine
gumeter run-all code_engine --num_replicas 5