class NcaWebSocketManager {
    constructor() {
        this.ws = null;
        this.messageCallbacks = [];
        this.isConnected = false;
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket('wss://127.0.0.1:13579/');
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    resolve();
                };
                
                this.ws.onclose = () => {
                    this.isConnected = false;
                };
                
                this.ws.onerror = (error) => {
                    this.isConnected = false;
                    reject(error);
                };
                
                this.ws.onmessage = (event) => {
                    this.messageCallbacks.forEach(callback => callback(event.data));
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }

    send(message) {
        if (!this.isConnected) {
            throw new Error('WebSocket не подключен');
        }
        this.ws.send(JSON.stringify(message));
    }

    onMessage(callback) {
        this.messageCallbacks.push(callback);
    }
}

const ncaWebSocketManager = new NcaWebSocketManager();
export default ncaWebSocketManager;
