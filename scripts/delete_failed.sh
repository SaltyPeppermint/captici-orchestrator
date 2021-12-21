#!/bin/bash
set -e

kubectl delete jobs $(kubectl get jobs -o=jsonpath='{.items[?(@.status.failed>0)].metadata.name}');
kubectl delete pods $(kubectl get pods -o=jsonpath='{.items[?(@.status.failed>0)].metadata.name}')