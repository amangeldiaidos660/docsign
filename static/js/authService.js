export async function fetchNonce() {
    try {
        const response = await fetch('/get', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка получения nonce');
        }
        
        const data = await response.json();
        return data.nonce;
    } catch (error) {
        throw error;
    }
}

export async function sign(signature, nonce) {
    try {
        const response = await fetch('/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                signature: signature,
                nonce: nonce
            })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка проверки подписи');
        }
        
        const data = await response.json();
        return data.user_id;
    } catch (error) {
        throw error;
    }
}
