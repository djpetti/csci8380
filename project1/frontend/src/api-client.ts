/** Singleton API client used by the entire application. */
import {
  Configuration,
  ConflictCheckResult,
  ConflictCheckResultLevelEnum,
  DefaultApi,
} from "typescript-axios";

const api = new DefaultApi(
  new Configuration({
    basePath: "http://localhost:8080/project1-1.0-SNAPSHOT",
  })
);

/**
 * Used for translating raw conflict level strings to enum values.
 * Must be kept in-sync with `ConflictCheckResultLevel` on the backend.
 */
const CONFLICT_LEVEL_TO_ENUM = new Map<string, ConflictCheckResultLevelEnum>([
  ["STRONG", ConflictCheckResultLevelEnum.STRONG],
  ["MEDIUM", ConflictCheckResultLevelEnum.MEDIUM],
  ["LOW", ConflictCheckResultLevelEnum.LOW],
  ["NONE", ConflictCheckResultLevelEnum.NONE],
]);

/**
 * Coerces a raw response from Axios to the ConflictCheckResult structure.
 * @param {ConflictCheckResult} response The response to coerce.
 * @return {ConflictCheckResult} The coerced response.
 */
function responseToConflictCheckResult(
  response: ConflictCheckResult
): ConflictCheckResult {
  const rawResult = { ...response };

  // Fix the enums.
  rawResult.level = CONFLICT_LEVEL_TO_ENUM.get(rawResult.level as string);

  return rawResult;
}

/**
 * Checks two researchers by name to see if they
 * have a conflict-of-interest.
 * @param {string} firstName The name of the first researcher.
 * @param {string} secondName The name of the second researcher.
 * @return {ConflictCheckResult} The result of the check.
 */
export async function checkNames(
  firstName: string,
  secondName: string
): Promise<ConflictCheckResult> {
  const response = await api
    .checkNames(firstName, secondName)
    .catch(function (error) {
      console.error(error.toJSON());
      throw error;
    });

  return responseToConflictCheckResult(response.data);
}
