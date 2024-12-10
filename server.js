const express = require('express');
const bodyParser = require('body-parser');
const { jsPDF } = require('jspdf');
const fetch = require('node-fetch');
const app = express();
const PORT = 3000;

// Middleware для парсинга JSON
app.use(bodyParser.json());

app.post('/endpoint', (req, res) => {
    const data = req.body;

    // Генерация PDF
    const doc = new jsPDF();
    doc.text(`Имя: ${data.name || ''}`, 10, 10);
    doc.text(`Email: ${data.email || ''}`, 10, 20);
    doc.text(`Телефон: ${data.phone || ''}`, 10, 30);
    
    // Сохранение PDF во временный файл
    const pdfFilePath = './form_data.pdf';
    doc.save(pdfFilePath); // Здесь можно сохранять в буфер, но в этом примере для простоты мы сохраним в файл

    // Отправка PDF в Telegram
    sendPdfToTelegram(pdfFilePath)
        .then(() => {
            res.status(200).json({ message: 'Данные успешно получены и PDF отправлен в Telegram!' });
        })
        .catch(error => {
            console.error('Ошибка при отправке в Telegram:', error);
            res.status(500).json({ message: 'Ошибка при отправке PDF в Telegram' });
        });
});

// Функция для отправки PDF в Telegram
async function sendPdfToTelegram(pdfPath) {
    const chatId = '746551114'; // Ваш Telegram ID
    const token = '7350728888:AAGWakZ8esbTNog99EcDLLp9YyoVWd74Ug8'; // Ваш Bot API token
    
    const formData = new FormData();
    formData.append('chat_id', chatId);
    formData.append('document', fs.createReadStream(pdfPath));

    const response = await fetch(`https://api.telegram.org/bot${token}/sendDocument`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error('Ошибка отправки PDF в Telegram: ' + response.statusText);
    }
}

app.listen(PORT, () => {
    console.log(`Сервер запущен на http://localhost:${PORT}`);
});
