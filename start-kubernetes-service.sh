#!/bin/bash

DOCKER_IMAGE=avisoft/ai-mf-backend:latest
K8S_NAMESPACE=ai-mf-backend

echo Build Docker Image $DOCKER_IMAGE
docker build -t $DOCKER_IMAGE -f ./dockerfiles/Dockerfile.ai_mf_backend .

echo Push Docker Image $DOCKER_IMAGE
docker push $DOCKER_IMAGE

echo Create Namespace $K8S_NAMESPACE
kubectl create namespace $K8S_NAMESPACE

echo Create ConfigMap
kubectl -n $K8S_NAMESPACE create configmap ai-mf-config --from-env-file=./ai_mf_backend/.env.k8s --dry-run=client -o yaml > ./kubernetes/ai-mf-config-configmap.yaml
kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/ai-mf-config-configmap.yaml

echo Deploy PostgreSQL
kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/postgres-deployment.yaml

echo Deploy Redis
kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/redis-deployment.yaml

echo Deploy Pipe Queue Server
kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/wflow-pipe-deployment.yaml

echo Deploy API Server
kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/wflow-api-deployment.yaml

echo Wait for Deployment and Display Pods and Ingress
kubectl -n $K8S_NAMESPACE rollout status deploy ai-mf-backend-api
kubectl -n $K8S_NAMESPACE get po
kubectl -n $K8S_NAMESPACE get ingress

# Start local server
# minikube service ai-mf-api-service