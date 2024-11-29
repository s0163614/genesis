const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();
const port = 3000;

// Настройка хранения загруженных файлов
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/'); // Папка для хранения загруженных файлов
    },
    filename: (req, file, cb) => {
        cb(null, ${Date.now()}-${file.originalname}); // Переименовываем файл
    }
});

const upload = multer({ storage: storage });

// Обработка POST-запроса для загрузки файла
app.post('/upload', upload.single('file'), (req, res) => {
    console.log('Файл загружен:', req.file);
    res.send('Файл успешно загружен');
});
