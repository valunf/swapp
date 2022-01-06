pipeline {
    agent any
    options {
        disableConcurrentBuilds()
    }
    environment {
        registryUrl = "537006042321.dkr.ecr.eu-central-1.amazonaws.com/lisin"
        testImageName = "swfrontend:test-${env.BUILD_ID}"
        imageName = "swfrontend:latest"
    }
    stages{
        stage('Build test container and run tests') {
            environment {
                dockerfile = "Dockerfile.test"
            }
            steps {
               dir("swfrontend") {
                sh 'docker build -f ${dockerfile} . -t swfrontend:test'
                script {
                    docker.build(testImageName, "-f ${dockerfile} .")
                }
               }
            }
        }
        stage('Run tests') {
            agent {
                docker {
                    image testImageName
                    reuseNode true
                    label "test-image"
                }
            }
            steps {
                sh "python3 -m pytest -o cache_dir=/tmp /app/tests/unit/test_frontend.py"
            }
        }
        stage('Build prod image') {
            when { branch 'master' }
            steps {
                dir("swfrontend") {
                    script {
                        dockerImage = docker.build imageName
                    }
                    // sh "docker build . -t ${imageName}"
                }
            }
        }
        stage('Push prod image to registry') {
            when { branch 'master' }
            steps {
                script {
                    withDockerRegistry(url: registryUrl){
                        dockerImage.push()
                    }
                }
            }
        }

    }
    post {
        always {
            sh "docker rmi ${testImageName}"
            step([$class: "WsCleanup"])
            cleanWs()
        }
    }
}