import {EntryResponse, ProteinResponse, AnnotationResponse, Configuration, DefaultApi} from "typescript-axios";

/** Singleton API client used by the entire application. */
const api = new DefaultApi(
    new Configuration({ basePath: "http://localhost:8000" })
);
