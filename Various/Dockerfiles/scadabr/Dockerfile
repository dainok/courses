ARG VERSION_AD=2
FROM tomcat:9.0.98-jdk11-temurin-jammy

# Installing ScadaBR webapp
RUN curl -s -o /usr/local/tomcat/webapps/ROOT.war -L https://github.com/ScadaBR/ScadaBR/releases/download/v1.2/ScadaBR.war

# Startup
EXPOSE 80:8080
