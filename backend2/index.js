const express = require('express');
const app = express();
const port = 8000;
const cors = require('cors');
const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/testDB').then(() => console.log("Connected to MongoDB")).catch((e) => console.log(e));

app.use(express.json())
app.use(cors())

const authController = require("./Controllers/auth")
const superUserController = require("./Controllers/superUser")
app.use("/auth", authController)
app.use("/superuser", superUserController)


app.listen(port, () => {
    console.log(`Server is running at http://127.0.0.1:${port}`);
});