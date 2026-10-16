/* =====================================================
   CAREERGUIDE - COMMON JAVASCRIPT
   Career Guidance using RIASEC Assessment
   ===================================================== */


/* =====================================================
   1. CHECK LOGIN STATUS
   ===================================================== */

function isLoggedIn() {

    return localStorage.getItem("loggedIn") === "true";

}


/* =====================================================
   2. GET LOGGED-IN USER
   ===================================================== */

function getLoggedInUser() {

    const user =
        localStorage.getItem("loggedInUser");

    if (!user) {

        return null;

    }

    try {

        return JSON.parse(user);

    } catch (error) {

        return null;

    }

}


/* =====================================================
   3. LOGOUT
   ===================================================== */

async function logout() {

    try {

        await fetch(
            "http://127.0.0.1:5000/logout",
            {
                method: "POST",
                credentials: "include"
            }
        );

    } finally {

        localStorage.removeItem("loggedIn");
        localStorage.removeItem("loggedInUser");
        localStorage.removeItem("user");
        localStorage.removeItem("riasecScores");
        window.location.href = "login.html";

    }

}


/* =====================================================
   4. PROTECT PAGE
   ===================================================== */

function requireLogin() {

    if (!isLoggedIn()) {

        alert(
            "Please login to continue."
        );

        window.location.href =
            "login.html";

    }

}


/* =====================================================
   5. GET RIASEC SCORES
   ===================================================== */

function getRiasecScores() {

    const data =
        localStorage.getItem(
            "riasecScores"
        );

    if (!data) {

        return null;

    }

    try {

        return JSON.parse(data);

    } catch (error) {

        return null;

    }

}


/* =====================================================
   6. FIND HIGHEST RIASEC TYPE
   ===================================================== */

function getHighestRiasecType(scores) {

    if (!scores) {

        return null;

    }


    let highestType = "R";

    let highestScore =
        Number(scores.R) || 0;


    const types = [
        "R",
        "I",
        "A",
        "S",
        "E",
        "C"
    ];


    types.forEach(function(type) {

        const score =
            Number(scores[type]) || 0;


        if (score > highestScore) {

            highestScore = score;

            highestType = type;

        }

    });


    return highestType;

}


/* =====================================================
   7. RIASEC INFORMATION
   ===================================================== */

const riasecInfo = {

    R: {

        name: "Realistic",

        description:
            "You prefer practical and hands-on activities and enjoy working with tools, machines and physical environments.",

        careers: [
            "Mechanical Engineer",
            "Civil Engineer",
            "Electrical Engineer",
            "Automobile Engineer",
            "Agricultural Officer"
        ]

    },


    I: {

        name: "Investigative",

        description:
            "You enjoy research, analysis, problem-solving and understanding how things work.",

        careers: [
            "Data Analyst",
            "Software Developer",
            "Research Scientist",
            "Doctor",
            "Engineer"
        ]

    },


    A: {

        name: "Artistic",

        description:
            "You enjoy creativity, design, writing, art and self-expression.",

        careers: [
            "Graphic Designer",
            "UI/UX Designer",
            "Writer",
            "Animator",
            "Content Creator"
        ]

    },


    S: {

        name: "Social",

        description:
            "You enjoy helping, teaching, supporting and communicating with other people.",

        careers: [
            "Teacher",
            "Counselor",
            "Social Worker",
            "HR Professional",
            "Trainer"
        ]

    },


    E: {

        name: "Enterprising",

        description:
            "You enjoy leadership, business, persuasion, decision-making and taking responsibility.",

        careers: [
            "Entrepreneur",
            "Business Manager",
            "Marketing Manager",
            "Sales Manager",
            "Bank Manager"
        ]

    },


    C: {

        name: "Conventional",

        description:
            "You prefer organized environments and enjoy working with records, numbers and structured procedures.",

        careers: [
            "Accountant",
            "Banking Professional",
            "Financial Analyst",
            "Office Administrator",
            "Data Entry Specialist"
        ]

    }

};


/* =====================================================
   8. GET RIASEC RESULT INFORMATION
   ===================================================== */

function getRiasecResult() {

    const scores =
        getRiasecScores();


    if (!scores) {

        return null;

    }


    const type =
        getHighestRiasecType(scores);


    if (!type) {

        return null;

    }


    return {

        type: type,

        score:
            Number(scores[type]) || 0,

        name:
            riasecInfo[type].name,

        description:
            riasecInfo[type].description,

        careers:
            riasecInfo[type].careers

    };

}


/* =====================================================
   9. SAVE RIASEC SCORES
   ===================================================== */

function saveRiasecScores(scores) {

    if (!scores) {

        return false;

    }


    localStorage.setItem(

        "riasecScores",

        JSON.stringify(scores)

    );


    return true;

}


/* =====================================================
   10. CLEAR RIASEC RESULT
   ===================================================== */

function clearRiasecResult() {

    localStorage.removeItem(
        "riasecScores"
    );

}


/* =====================================================
   11. SAVE PROFILE
   ===================================================== */

function saveProfile(profile) {

    if (!profile) {

        return false;

    }


    localStorage.setItem(

        "userProfile",

        JSON.stringify(profile)

    );


    return true;

}


/* =====================================================
   12. GET PROFILE
   ===================================================== */

function getProfile() {

    const profile =
        localStorage.getItem(
            "userProfile"
        );


    if (!profile) {

        return null;

    }


    try {

        return JSON.parse(profile);

    } catch (error) {

        return null;

    }

}


/* =====================================================
   13. UPDATE NAVBAR
   ===================================================== */

function updateNavbar() {

    const loggedIn =
        isLoggedIn();


    const loginLinks =
        document.querySelectorAll(
            ".login-link"
        );


    const logoutLinks =
        document.querySelectorAll(
            ".logout-link"
        );


    loginLinks.forEach(function(link) {

        if (loggedIn) {

            link.style.display =
                "none";

        } else {

            link.style.display =
                "";

        }

    });


    logoutLinks.forEach(function(link) {

        if (loggedIn) {

            link.style.display =
                "";

        } else {

            link.style.display =
                "none";

        }

    });

}


/* =====================================================
   14. DISPLAY USER NAME
   ===================================================== */

function displayUserName() {

    const user =
        getLoggedInUser();


    const elements =
        document.querySelectorAll(
            ".user-name"
        );


    if (!user) {

        return;

    }


    elements.forEach(function(element) {

        element.textContent =
            user.name || "User";

    });

}


/* =====================================================
   15. PROTECT ASSESSMENT / RESULT / CAREER PAGES
   ===================================================== */

function protectUserPages() {

    const currentPage =
        window.location.pathname
            .split("/")
            .pop();


    const protectedPages = [

        "profile.html",

        "assessment.html",

        "result.html",

        "career.html",

        "courses.html"

    ];


    if (
        protectedPages.includes(
            currentPage
        )
    ) {

        requireLogin();

    }

}


/* =====================================================
   16. PAGE LOAD
   ===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        updateNavbar();

        displayUserName();

        protectUserPages();

    }
);