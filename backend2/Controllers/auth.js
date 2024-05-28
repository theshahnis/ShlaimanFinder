
const express = require("express")
const router = express.Router()
const jwt = require("jsonwebtoken")
const userService = require("../Services/UserService")

router.post("/signup", async (req, res) => {
    // check if user exists
    const user = await userService.getUserByEmail(req.body.email)
   
    if (user.success) {
        return res.json({ success: false, message: "User already exists" })
    }
    // create user
    const newUser = await userService.createUser(req.body)
    if (newUser.success) {
        return res.json({ success: true, message: "User created successfully" })
    } else {
        return res.json({ success: false, message: "Failed to create user" })
    }

    
})

router.post("/login", async (req, res) => {
    const user = await userService.getUserByEmail(req.body.email)
    if (user.success) {
        if (user.data.password === req.body.password) {
            const token = jwt.sign({ id: user.data._id }, "secret")
            return res.json({ success: true, token: token })
        } else {
            return res.json({ success: false, message: "Invalid credentials" })
        }
    } else {
        return res.json({ success: false, message: "User not found" })
    }
})

module.exports = router