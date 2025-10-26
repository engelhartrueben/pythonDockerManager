#!/bin/ash

apk add --no-cache maven
apk add --no-cache openjdk21
apk add --no-cache git
mvn -version
java --version
git -v
git clone $GH_REPO_URL agent
cd agent
ls
mvn package
cd target
java -jar *.jar

