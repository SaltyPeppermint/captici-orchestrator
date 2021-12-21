#!/bin/bash
set -e

podman build -t registry.kube.informatik.uni-leipzig.de/nicole/cdpb-test-orchestrator .
podman push registry.kube.informatik.uni-leipzig.de/nicole/cdpb-test-orchestrator:latest
kubectl delete -f  kubernetes/cdpb-test-orchestrator/deployment.yaml
kubectl apply -k kubernetes/cdpb-test-orchestrator