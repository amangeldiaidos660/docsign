import ncaWebSocketManager from './ncaWebSocketManager.js';

export async function signData(base64data) {
    return new Promise((resolve, reject) => {
        const message = {
            module: "kz.gov.pki.knca.basics",
            method: "sign",
            args: {
                allowedStorages: ["PKCS12"],
                format: "cms",
                data: base64data,
                signingParams: {
                    decode: true,
                    encapsulate: false,
                    digested: false,
                    tsaProfile: {}
                },
                signerParams: {
                    extKeyUsageOids: ["1.3.6.1.5.5.7.3.2"],
                    chain: []
                },
                locale: "ru"
            }
        };

        const messageHandler = (data) => {
            try {
                const response = JSON.parse(data);
                if (response.body && response.body.result) {
                    ncaWebSocketManager.onMessage(messageHandler);
                    resolve(response.body.result[0]);
                }
            } catch (error) {
                reject(error);
            }
        };

        ncaWebSocketManager.onMessage(messageHandler);
        ncaWebSocketManager.send(message);
    });
}

