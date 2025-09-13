import ncaWebSocketManager from './ncaWebSocketManager.js';
import { signData } from './ncalayer.js';
import { fetchNonce, sign } from './auth_service.js';

document.addEventListener('DOMContentLoaded', function() {
    const ecpButton = document.getElementById('ecp-login');
    const egovButton = document.getElementById('egov-login');
    
    ecpButton.addEventListener('click', handleEcpLogin);
    egovButton.addEventListener('click', handleEgovLogin);
});

async function handleEcpLogin() {
    try {
        await ncaWebSocketManager.connect();
        
        const nonce = await fetchNonce();
        const signature = await signData(nonce);
        const userId = await sign(signature, nonce);
        
        console.log('Успешная аутентификация:', userId);
        window.location.href = `/user/dashboard?user_id=${userId}`;
        
    } catch (error) {
        console.error('Ошибка аутентификации:', error);
    } finally {
        ncaWebSocketManager.disconnect();
    }
}

function handleEgovLogin() {
    console.log('Вход через egovMobile');
}
