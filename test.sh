#!/bin/ash

echo "[ do you see me ? ]"
apk add --no-cache maven
apk add --no-cache openjdk21
apk add --no-cache git
mvn -version
java --version
git -v
git clone https://github.com/engelhartrueben/agent_demo.git agent
cd agent
mvn package
cd target
java -jar *.jar

