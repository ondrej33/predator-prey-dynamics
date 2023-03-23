const express = require('express');
const app = express();
const port = 5000;
const path = require('path');
const Vec2 = require('vec2');

app.get('/', (req, res) => {
    const filePath = path.join(__dirname, 'index.html');
    res.sendFile(filePath);
});

app.listen(port, () => {
    console.log(`Now listening on port ${port}`);
});

app.use('/bower_components', express.static(path.join(__dirname, 'bower_components')));
app.use('/js', express.static(path.join(__dirname, 'js')));

module.exports = app;
