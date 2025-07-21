#!/bin/bash

gumeter deploy aws_lambda
gumeter deploy gcp_cloudrun
gumeter deploy code_engine

gumeter warm-up aws_lambda
gumeter run-all aws_lambda  --num_replicas 5
gumeter warm-up gcp_cloudrun
gumeter run-all gcp_cloudrun --num_replicas 5
gumeter warm-up code_engine
gumeter run-all code_engine --num_replicas 5