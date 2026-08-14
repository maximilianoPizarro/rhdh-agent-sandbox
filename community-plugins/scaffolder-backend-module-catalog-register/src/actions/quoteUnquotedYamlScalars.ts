const QUOTE_KEYS = 'description|rhdh-agent-sandbox\\.io/agent-spec';
const LINE_RE = new RegExp(`^([ \\t]*)(${QUOTE_KEYS}): ([^\\n]+)$`, 'gm');

/**
 * Quote plain YAML scalars that Hub later parses as catalog entities.
 * Unquoted `description: Example questions: ...` is invalid YAML
 * (nested compact mapping) and makes catalog:wait-for-entity time out.
 */
export function quoteUnquotedYamlScalars(text: string): string {
  return text.replace(LINE_RE, (full, indent: string, key: string, val: string) => {
    const stripped = val.trim();
    if (!stripped || ['"', "'", '|', '>'].includes(stripped[0])) {
      return full;
    }
    return `${indent}${key}: ${JSON.stringify(stripped)}`;
  });
}
