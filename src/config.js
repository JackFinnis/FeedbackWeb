// Configure Firebase

import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// https://firebase.google.com/docs/web/setup#available-libraries

const firebaseConfig = {
  apiKey: "AIzaSyDB_xDCowcU0Isp3RB44iaIdkR19Toi2OE",
  authDomain: "feedback-5331f.firebaseapp.com",
  projectId: "feedback-5331f",
  storageBucket: "feedback-5331f.appspot.com",
  messagingSenderId: "764019426354",
  appId: "1:764019426354:web:a4a22f378274a6bff8282b",
  measurementId: "G-WHTYF6ECGJ"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);