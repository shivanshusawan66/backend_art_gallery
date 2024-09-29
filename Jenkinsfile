pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "avisoft/ai-mf-backend:latest"
        K8S_NAMESPACE = "ai-mf-backend"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/avi-soft/ai-mf-platform.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        echo Build Docker Image $DOCKER_IMAGE
                        docker build -t $DOCKER_IMAGE -f ./dockerfiles/Dockerfile.ai_mf_backend .
                    """
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    sh """
                        echo Push Docker Image $DOCKER_IMAGE
                        docker push $DOCKER_IMAGE
                    """
                }
            }
        }

        stage('Create Namespace') {
            steps {
                script {
                    sh """
                        echo Create Namespace $K8S_NAMESPACE
                        kubectl create namespace $K8S_NAMESPACE || true
                    """
                }
            }
        }

        stage('Deploy ConfigMap') {
            steps {
                script {
                    sh """
                        echo Create ConfigMap
                        kubectl -n $K8S_NAMESPACE create configmap ai-mf-config --from-env-file=./ai_mf_backend/.env.k8s --dry-run=client -o yaml > ./kubernetes/ai-mf-config-configmap.yaml
                        kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/ai-mf-config-configmap.yaml
                    """
                }
            }
        }

        stage('Deploy PostgresSQL') {
            steps {
                script {
                    sh """
                        echo Deploy PostgreSQL
                        kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/postgres-deployment.yaml
                    """
                }
            }
        }

        stage('Deploy Redis') {
            steps {
                script {
                    sh """
                        echo Deploy Redis
                        kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/redis-deployment.yaml
                    """
                }
            }
        }

        stage('Deploy Pipe Queue Server') {
            steps {
                script {
                    sh """
                        echo Deploy Pipe Queue Server
                        kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/wflow-pipe-deployment.yaml
                    """
                }
            }
        }

        stage('Deploy API Server') {
            steps {
                script {
                    sh """
                        echo Deploy API Server
                        kubectl -n $K8S_NAMESPACE apply -f ./kubernetes/wflow-api-deployment.yaml
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    sh """
                        echo Wait for Deployment and Display Pods and Ingress
                        kubectl -n $K8S_NAMESPACE rollout status deploy ai-mf-backend-api
                        kubectl -n $K8S_NAMESPACE get po
                        kubectl -n $K8S_NAMESPACE get ingress
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
