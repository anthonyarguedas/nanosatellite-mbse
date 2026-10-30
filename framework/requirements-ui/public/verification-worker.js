import { evaluateChecks } from '/verification.mjs';

self.onmessage = ({ data }) => {
  self.postMessage({ token: data.token, results: evaluateChecks(data.workspace) });
};
