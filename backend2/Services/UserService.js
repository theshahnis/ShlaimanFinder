// crud operations for user (a service in which the controller interacts with)
const UserModel = require("../models/UserModel")


// Get all users
const getAllUsers = async () => {
    try {
        const users = await UserModel.find({})
        return { success: true, data: users }
    }catch(e) {
        return { success: false, error: e }
    

    }

}

// Get user by id
const getUserById = async (id) => {
    try {
        const user = await UserModel.findById(id)
        return { success: true, data: user }

    }catch(e) {
        return { success: false, error: e }
    }
   
}

const getUserByEmail = async (email) => {
    try {
        const user = await UserModel.findOne({ email: email })
        if (!user) return { success: false, error: "User not found" }
         return { success: true, data: user }
    } catch(e) {
        return { success: false, error: e }
    }
}

// Create a new user
const createUser = async (user) => {
    try {
        const newUser = new UserModel(user)
        await newUser.save()
        return { success: true, data: newUser }
    }catch(e) {
        return { success: false, error: e }
    }
}

// Update a user
const updateUser = async (id, user) => {
    try {
        await UserModel.findByIdAndUpdate(id, user)
        const updatedUser = await UserModel.findById(id)
        return { success: true, data: updatedUser }
    }catch(e) {
        return { success: false, error: e }
    }
}

// Delete a user
const deleteUser = async (id) => {
    try {
        await UserModel.findByIdAndDelete(id)
        return { success: true }
    } catch(e) {
        return { success: false, error: e }
    }
}



module.exports = { getAllUsers, getUserById, createUser, updateUser, deleteUser, getUserByEmail }