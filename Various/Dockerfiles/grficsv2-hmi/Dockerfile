FROM tomcat:9.0.98-jdk11-temurin-jammy

# Installing ScadaBR webapp
COPY ScadaBR.tar.gz /tmp/ScadaBR.tar.gz
RUN tar xzvf /tmp/ScadaBR.tar.gz -C /usr/local/tomcat/webapps

# Startup
EXPOSE 80:8080
