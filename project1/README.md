# CSCI 8380 Project 1

This project is a conflict-of-interest checker for academic researchers in CS.

## Usage

To use this app, you will need to have `docker` and `docker-compose` installed.

To run the server:

```
docker-compose up
```

The app should be served at [http://localhost:8080/project1-1.0-SNAPSHOT/](http://localhost:8080/project1-1.0-SNAPSHOT/).


## Development

The standard `docker-compose` configuration will build everything within Docker. However,
there is a development configuration that will instead use a local WAR that exists in the
`target/` directory. This allows you to deploy a new app without rebuilding the Docker container,
however, you will still need to restart the container in order to redeploy. To use this
configuration, you will need to specify the proper overlay file:

```
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up
```

### Building the WAR

To build the WAR, you will need a Java 11 JDK, as well as `maven` installed. Building
the backend code and regenerating the WAR can be done with:

```
mvn verify
```

### Building the Frontend

The frontend code is written in Typescript, and will have to be compiled before it can be used.
In order to build the frontend code, you will need a working `npm` installation. Then, you can
use the `deploy.py` script:

```
python deploy.py build
```

In order to skip the formatting and linting steps (and speed up the build), you can also pass the `-b` flag.

The frontend uses an API client that is automatically generated from the OpenAPI spec provided by
the backend. If you modify the backend API, you will have to regenerate this client. This can
also be done with `deploy.py`, but you have to pass it the path to an existing WAR so that it knows
where to obtain the OpenAPI spec from:

```
python deploy.py build -w /target/project1-1.0-SNAPSHOT.war
```

### DBLP Data

This app requires the DBLP dataset to be available locally in order to run.
You can download it from [here](http://downloads.linkeddatafragments.org/hdt/dblp-20170124.hdt).

The app can be notified of the location of this file through a JVM argument: `-Ddblp.path=/path/to/hdt/file`