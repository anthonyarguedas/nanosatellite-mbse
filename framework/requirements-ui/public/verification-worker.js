// Browser transport only. The persistent server-side Python worker owns all
// expression parsing and calculation. Superseded requests are cancelled.
let controller = null;
self.onmessage = async ({ data }) => {
  controller?.abort();
  const request = new AbortController(); controller = request;
  try {
    const response = await fetch('/api/evaluate', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workspace: data.workspace, scriptResults: data.scriptResults }), signal: request.signal });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Python evaluation failed.');
    if (controller === request) self.postMessage({ token: data.token, ...result });
  } catch (error) {
    if (error.name !== 'AbortError' && controller === request) self.postMessage({ token: data.token, error: error.message });
  }
};
