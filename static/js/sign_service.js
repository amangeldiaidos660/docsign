export async function getBase64(documentId) {
  const resp = await fetch(`/sign/getbase64?document_id=${encodeURIComponent(documentId)}`, {
    credentials: 'same-origin'
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || 'request failed');
  }
  const data = await resp.json();
  console.log('getbase64', data);
  return data;
}


export async function addSign(document_id, file_base64, signature) {
  const resp = await fetch('/sign/addsign', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify({ document_id, file_base64, signature })
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || 'request failed');
  }
  const data = await resp.json();
  console.log('addsign', data);
  return data;
}

window.signService = { getBase64, addSign };