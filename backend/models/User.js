const mongoose = require('mongoose');

// Define the User schema
const userSchema = new mongoose.Schema({
  user: {
    type: String,
    required: true,
    unique: true, // Ensure uniqueness of usernames
  },
  pwd: {
    type: String,
    required: true,
  },
  images: [{
    type: String, // You can store image filenames or URLs as strings
  }],
});

// Create the User model
const User = mongoose.model('User', userSchema);

module.exports = User;
