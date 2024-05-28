const express = require('express');
const router = express.Router();
const UserModel = require("../models/UserModel")
const jwt = require("jsonwebtoken")
// Get all users
router.get("/", checkSuperUser, async (req, res) => {
    try {
        const users = await UserModel.find({})
        return res.json({ success: true, data: users })
    } catch (e) {
        return res.json({ success: false, error: e })
    }
})

// Get user by id
router.get("/:id", checkSuperUser, async (req, res) => {
    try {
        const user = await UserModel.findById(req.params.id)
        return res.json({ success: true, data: user })
    } catch (e) {
        return res.json({ success: false, error: e })
    }
})

// Create a new user
router.post("/", checkSuperUser, async (req, res) => {
    try {
        const newUser = new UserModel(req.body)
        await newUser.save()
        return res.json({ success: true, data: newUser })
    } catch (e) {
        return res.json({ success: false, error: e })
    }
})

// Update a user
router.put("/:id", checkSuperUser, async (req, res) => {
    try {
        await UserModel.findByIdAndUpdate(req.params.id, req.body)
        const updatedUser = await UserModel.findById(req.params.id)
        return res.json({ success: true, data: updatedUser })
    } catch (e) {
        return res.json({ success: false, error: e })
    }
})

// Delete a user
router.delete("/:id", checkSuperUser, async (req, res) => {
    try {
        await UserModel.findByIdAndDelete(req.params.id)
        return res.json({ success: true })
    } catch (e) {
        return res.json({ success: false, error: e })
    }
})

// assume the decoded token includes the user's id
async function checkSuperUser(req, res, next) {
    const token = req.headers["access_token"]
    if (!token) return res.json({ success: false, message: "Access denied, No Token" })

    try {
        const decoded = jwt.verify(token, "secret")
        const user = await UserModel.findById(decoded.id)
        if (user.superuser) {
            next()
        } else {
            return res.json({ success: false, message: "Access denied, Not a superuser" })
        }
    } catch (e) {
        return res.json({ success: false, message: "Invalid Token", error: e.message})
    }

}

module.exports = router