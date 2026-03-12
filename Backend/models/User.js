import mongoose from "mongoose";
import bcrypt from "bcrypt";

const userSchema = new mongoose.Schema(
    {
        firstName: {type: String, required: true},
        lastName: {type: String, required: true},
    
    email: {
        type: String,
        required: true,
         unique: true,
        match: /^\S+@\S+\.\S+$/,
    },

    username: {
      type: String,
      required: true,
      unique: true,   // 👈 यह username को unique बनाएगा
      trim: true
    },

    password: { 
        type: String,
        required: true,
    },
    resetToken: String,
    },
    { timestamps: true}
);

// 🔐 PASSWORD HASHING (before save)
userSchema.pre("save", async function (next) {
  // debug: inspect what 'next' is when hook runs
  try {
    console.log('pre-save hook - typeof next:', typeof next);
  } catch (e) {
    console.error('pre-save hook logging failed', e);
  }

  // agar password change nahi hua, dobara hash mat karo
  if (!this.isModified("password")) {
    if (typeof next === 'function') return next();
    return;
  }

  // password ko hash karo
  const salt = await bcrypt.genSalt(10);
  this.password = await bcrypt.hash(this.password, salt);

  if (typeof next === 'function') next();
});


// 🔑 PASSWORD COMPARE METHOD (login ke liye)
userSchema.methods.comparePassword = async function (enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};


export const User = mongoose.model("User", userSchema);
