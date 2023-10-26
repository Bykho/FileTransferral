const mongoose = require('mongoose');

const MONGO_URI = 'mongodb+srv://nico:xX2SUpVJA9Rcrgxg@cluster0.uu6cuq7.mongodb.net/Cluster0?retryWrites=true&w=majority';

mongoose.connect(MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  useCreateIndex: true,
  useFindAndModify: false,
});

mongoose.connection.on('connected', () => {
  console.log('Connected to MongoDB');
});

mongoose.connection.on('error', (err) => {
  console.error('MongoDB connection error:', err);
});

module.exports = mongoose;
