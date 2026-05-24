import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";

import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const loginButton = document.getElementById("login");
const signUpButton = document.getElementById("sign-up");
const signOutButton = document.getElementById("sign-out");
const loginLink = document.getElementById("login-link");
const loginBox = document.getElementById("login-box");

function setCookie(name, value, days) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
}

function deleteCookie(name) {
  document.cookie = `${name}=; Max-Age=0; path=/`;
}

if (signUpButton) {
  signUpButton.addEventListener("click", async () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();

      setCookie("token", token, 1);
      window.location.href = "/";
    } catch (error) {
      alert(error.message);
    }
  });
}

if (loginButton) {
  loginButton.addEventListener("click", async () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();

      setCookie("token", token, 1);
      window.location.href = "/";
    } catch (error) {
      alert(error.message);
    }
  });
}

if (signOutButton) {
  signOutButton.addEventListener("click", async () => {
    await signOut(auth);
    deleteCookie("token");
    window.location.href = "/";
  });
}

onAuthStateChanged(auth, async (user) => {
  if (user) {
    const token = await user.getIdToken();
    setCookie("token", token, 1);

    if (signOutButton) {
      signOutButton.hidden = false;
    }

    if (loginLink) {
      loginLink.hidden = true;
    }

    if (loginBox) {
      loginBox.hidden = true;
    }
  } else {
    deleteCookie("token");

    if (signOutButton) {
      signOutButton.hidden = true;
    }

    if (loginLink) {
      loginLink.hidden = false;
    }

    if (loginBox) {
      loginBox.hidden = false;
    }
  }
});