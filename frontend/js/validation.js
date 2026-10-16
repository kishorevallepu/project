/* =====================================================
   CAREERGUIDE
   FORM VALIDATION JAVASCRIPT
   ===================================================== */


/* =====================================================
   1. EMAIL VALIDATION
   ===================================================== */

function validateEmail(email) {

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return emailPattern.test(email);

}


/* =====================================================
   2. PASSWORD VALIDATION
   ===================================================== */

function validatePassword(password) {

    /*
       Password requirements:

       Minimum 8 characters
       At least one uppercase letter
       At least one lowercase letter
       At least one number
    */

    const passwordPattern =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

    return passwordPattern.test(password);

}


/* =====================================================
   3. NAME VALIDATION
   ===================================================== */

function validateName(name) {

    const namePattern =
        /^[A-Za-z ]{2,50}$/;

    return namePattern.test(name.trim());

}


/* =====================================================
   4. SHOW ERROR MESSAGE
   ===================================================== */

function showError(input, message) {

    input.classList.add("is-invalid");


    let errorElement =
        input.parentElement.querySelector(
            ".validation-error"
        );


    if (!errorElement) {

        errorElement =
            document.createElement("div");

        errorElement.className =
            "validation-error text-danger small mt-1";

        input.parentElement.appendChild(
            errorElement
        );

    }


    errorElement.textContent =
        message;

}


/* =====================================================
   5. CLEAR ERROR
   ===================================================== */

function clearError(input) {

    input.classList.remove(
        "is-invalid"
    );


    const errorElement =
        input.parentElement.querySelector(
            ".validation-error"
        );


    if (errorElement) {

        errorElement.remove();

    }

}


/* =====================================================
   6. REGISTER FORM VALIDATION
   ===================================================== */

const registerForm =
    document.getElementById(
        "registerForm"
    );


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        function(event) {

            event.preventDefault();


            let isValid = true;


            /* ================= NAME ================= */

            const name =
                document.getElementById(
                    "name"
                );


            if (
                !name.value.trim()
            ) {

                showError(
                    name,
                    "Name is required."
                );

                isValid = false;

            }

            else if (
                !validateName(
                    name.value
                )
            ) {

                showError(
                    name,
                    "Enter a valid name."
                );

                isValid = false;

            }

            else {

                clearError(name);

            }



            /* ================= EMAIL ================= */

            const email =
                document.getElementById(
                    "email"
                );


            if (
                !email.value.trim()
            ) {

                showError(
                    email,
                    "Email is required."
                );

                isValid = false;

            }

            else if (
                !validateEmail(
                    email.value
                )
            ) {

                showError(
                    email,
                    "Enter a valid email address."
                );

                isValid = false;

            }

            else {

                clearError(email);

            }



            /* ================= PASSWORD ================= */

            const password =
                document.getElementById(
                    "password"
                );


            if (
                !password.value
            ) {

                showError(
                    password,
                    "Password is required."
                );

                isValid = false;

            }

            else if (
                !validatePassword(
                    password.value
                )
            ) {

                showError(
                    password,
                    "Password must contain 8+ characters, uppercase, lowercase and a number."
                );

                isValid = false;

            }

            else {

                clearError(password);

            }



            /* ================= CONFIRM PASSWORD ================= */

            const confirmPassword =
                document.getElementById(
                    "confirmPassword"
                );


            if (
                !confirmPassword.value
            ) {

                showError(
                    confirmPassword,
                    "Please confirm your password."
                );

                isValid = false;

            }

            else if (
                password.value !==
                confirmPassword.value
            ) {

                showError(
                    confirmPassword,
                    "Passwords do not match."
                );

                isValid = false;

            }

            else {

                clearError(
                    confirmPassword
                );

            }



            /* ================= EDUCATION ================= */

            const education =
                document.getElementById(
                    "education"
                );


            if (
                education &&
                !education.value
            ) {

                showError(
                    education,
                    "Please select your education."
                );

                isValid = false;

            }

            else if (education) {

                clearError(
                    education
                );

            }



            /* ================= AGE ================= */

            const age =
                document.getElementById(
                    "age"
                );


            if (
                age &&
                age.value
            ) {

                const ageValue =
                    Number(age.value);


                if (
                    ageValue < 15 ||
                    ageValue > 60
                ) {

                    showError(
                        age,
                        "Enter an age between 15 and 60."
                    );

                    isValid = false;

                }

                else {

                    clearError(age);

                }

            }



            /* =================================================
               SAVE USER
               ================================================= */

            if (isValid) {

                const user = {

                    name:
                        name.value.trim(),

                    email:
                        email.value.trim(),

                    password:
                        password.value,

                    education:
                        education
                            ? education.value
                            : "",

                    age:
                        age
                            ? age.value
                            : ""

                };


                localStorage.setItem(

                    "registeredUser",

                    JSON.stringify(user)

                );


                alert(
                    "Registration successful! Please login."
                );


                window.location.href =
                    "login.html";

            }

        }
    );

}


/* =====================================================
   7. LOGIN FORM VALIDATION
   ===================================================== */

const loginForm =
    document.getElementById(
        "loginForm"
    );


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        function(event) {

            event.preventDefault();


            const email =
                document.getElementById(
                    "email"
                );


            const password =
                document.getElementById(
                    "password"
                );


            const errorMessage =
                document.getElementById(
                    "errorMessage"
                );


            let valid = true;


            /* EMAIL */

            if (
                !email.value.trim()
            ) {

                showError(
                    email,
                    "Email is required."
                );

                valid = false;

            }

            else if (
                !validateEmail(
                    email.value
                )
            ) {

                showError(
                    email,
                    "Enter a valid email address."
                );

                valid = false;

            }

            else {

                clearError(email);

            }


            /* PASSWORD */

            if (
                !password.value
            ) {

                showError(
                    password,
                    "Password is required."
                );

                valid = false;

            }

            else {

                clearError(password);

            }


            if (!valid) {

                return;

            }


            /* =============================
               CHECK REGISTERED USER
               ============================= */

            const savedUser =
                localStorage.getItem(
                    "registeredUser"
                );


            if (!savedUser) {

                if (errorMessage) {

                    errorMessage.textContent =
                        "No account found. Please register first.";

                    errorMessage.classList.remove(
                        "d-none"
                    );

                }

                return;

            }


            const user =
                JSON.parse(savedUser);


            if (
                user.email ===
                    email.value.trim() &&

                user.password ===
                    password.value
            ) {


                /* LOGIN SUCCESS */

                localStorage.setItem(
                    "loggedIn",
                    "true"
                );


                localStorage.setItem(
                    "loggedInUser",
                    JSON.stringify(user)
                );


                window.location.href =
                    "profile.html";


            }

            else {

                if (errorMessage) {

                    errorMessage.textContent =
                        "Invalid email or password.";

                    errorMessage.classList.remove(
                        "d-none"
                    );

                }

            }

        }
    );

}


/* =====================================================
   8. REAL-TIME EMAIL VALIDATION
   ===================================================== */

document.addEventListener(
    "input",
    function(event) {

        if (
            event.target.id ===
            "email"
        ) {

            const email =
                event.target;


            if (
                email.value &&
                validateEmail(
                    email.value
                )
            ) {

                clearError(email);

            }

        }

    }
);


/* =====================================================
   9. REAL-TIME PASSWORD MATCH
   ===================================================== */

document.addEventListener(
    "input",
    function(event) {

        if (
            event.target.id ===
            "confirmPassword"
        ) {

            const password =
                document.getElementById(
                    "password"
                );


            const confirmPassword =
                event.target;


            if (
                password &&
                confirmPassword.value ===
                password.value
            ) {

                clearError(
                    confirmPassword
                );

            }

        }

    }
);