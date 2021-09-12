####
# builder image is used for building the application.
####
FROM openjdk:11-slim AS builder

# Install dependencies.
RUN apt-get update
RUN apt-get install -y maven python3 curl unzip

# Install Node.
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . ~/.nvm/nvm.sh && echo ${NVM_DIR} && nvm install 15.8.0

# Install glassfish.
WORKDIR /glassfish
RUN curl https://download.eclipse.org/ee4j/glassfish/glassfish-6.1.0.zip --output glassfish.zip
RUN unzip glassfish.zip
ENV PATH=/glassfish/glassfish6/bin:${PATH}

# Install NPM dependencies.
WORKDIR /build
COPY frontend/ frontend/
RUN cd frontend && . ~/.nvm/nvm.sh && npm install

# Build the backend.
COPY src/ src/
COPY pom.xml pom.xml
# Create an empty "bundled" directory to bootstrap the build.
RUN mkdir frontend/bundled
RUN mvn verify

# Build the frontend.
COPY deploy.py deploy.py
RUN . ~/.nvm/nvm.sh && python3 deploy.py build -w target/project1-1.0-SNAPSHOT.war

# Now rebuild the web app, incorporating the new frontend.
RUN mvn verify

####
# app image is used to run the sevlet.
####
FROM openjdk:11-slim AS app

# Copy glassfish.
COPY --from=builder /glassfish /glassfish
ENV PATH=/glassfish/glassfish6/bin:${PATH}
# Copy WAR.
WORKDIR /app
COPY --from=builder /build/target target

# Run the app.
CMD asadmin start-domain domain1 && \
    asadmin deploy --force target/project1-1.0-SNAPSHOT.war && \
    sleep infinity