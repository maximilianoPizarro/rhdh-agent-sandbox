import { quoteUnquotedYamlScalars } from './quoteUnquotedYamlScalars';

describe('quoteUnquotedYamlScalars', () => {
  it('quotes description values that contain colon+space', () => {
    const input =
      '  description: You are an agent. Example questions: Are pods healthy?\n';
    const out = quoteUnquotedYamlScalars(input);
    expect(out).toContain(
      '  description: "You are an agent. Example questions: Are pods healthy?"',
    );
  });

  it('quotes agent-spec annotation values', () => {
    const input =
      '    rhdh-agent-sandbox.io/agent-spec: Prefer read-only list and get actions\n';
    const out = quoteUnquotedYamlScalars(input);
    expect(out).toContain(
      '    rhdh-agent-sandbox.io/agent-spec: "Prefer read-only list and get actions"',
    );
  });

  it('leaves block scalars and already-quoted values alone', () => {
    const input = [
      '  description: >-',
      '    already a block',
      '  description: "already quoted"',
      '    rhdh-agent-sandbox.io/agent-spec: |',
      '      keep me',
      '',
    ].join('\n');
    expect(quoteUnquotedYamlScalars(input)).toEqual(input);
  });
});
