const questions = {

    I: [
        "I enjoy solving complex problems.",
        "I like analyzing information and finding solutions.",
        "I enjoy conducting experiments and research.",
        "I like learning how things work."
    ],

    A: [
        "I enjoy drawing, painting, or designing.",
        "I like writing stories, poems, or creative content.",
        "I enjoy expressing myself through music or art.",
        "I prefer activities that allow me to be creative."
    ],

    S: [
        "I enjoy helping people solve their problems.",
        "I like teaching or explaining things to others.",
        "I enjoy working as part of a team.",
        "I like activities that involve supporting other people."
    ],

    E: [
        "I enjoy leading a group or team.",
        "I like persuading people to accept my ideas.",
        "I enjoy starting new projects or businesses.",
        "I like making decisions and taking responsibility."
    ],

    C: [
        "I enjoy organizing information and documents.",
        "I like working with numbers and records.",
        "I prefer activities that follow clear rules and procedures.",
        "I enjoy maintaining accurate records."
    ]

};


const containers = {

    I: document.getElementById("investigativeQuestions"),
    A: document.getElementById("artisticQuestions"),
    S: document.getElementById("socialQuestions"),
    E: document.getElementById("enterprisingQuestions"),
    C: document.getElementById("conventionalQuestions")

};


let questionNumber = 5;


for (const category in questions) {

    questions[category].forEach(function(question) {

        const card = document.createElement("div");

        card.className =
            "card question-card shadow-sm mb-3";


        let options = "";


        for (let value = 1; value <= 5; value++) {

            options += `
                <label class="rating-option">

                    <input type="radio"
                           name="q${questionNumber}"
                           value="${value}">

                    <span class="rating-label">
                        ${value}
                    </span>

                </label>
            `;

        }


        card.innerHTML = `

            <div class="card-body">

                <p class="fw-semibold">

                    <span class="question-number">
                        ${questionNumber}
                    </span>

                    ${question}

                </p>

                <div class="text-center">

                    ${options}

                </div>

            </div>

        `;


        containers[category].appendChild(card);


        questionNumber++;

    });

}


/* ================= SUBMIT ================= */

document.getElementById("riasecForm")
.addEventListener("submit", async function(event) {

    event.preventDefault();


    const totalQuestions = 24;

    let answered = 0;


    for (let i = 1; i <= totalQuestions; i++) {

        const answer =
            document.querySelector(
                `input[name="q${i}"]:checked`
            );

        if (answer) {

            answered++;

        }

    }


    if (answered < totalQuestions) {

        alert(
            `Please answer all questions.\n\n` +
            `Answered: ${answered}/${totalQuestions}`
        );

        return;

    }


    /* ================= CALCULATE SCORES ================= */

    let scores = {

        R: 0,
        I: 0,
        A: 0,
        S: 0,
        E: 0,
        C: 0

    };


    // R questions: 1-4
    for (let i = 1; i <= 4; i++) {

        scores.R += Number(
            document.querySelector(
                `input[name="q${i}"]:checked`
            ).value
        );

    }


    // I questions: 5-8
    for (let i = 5; i <= 8; i++) {

        scores.I += Number(
            document.querySelector(
                `input[name="q${i}"]:checked`
            ).value
        );

    }


    // A questions: 9-12
    for (let i = 9; i <= 12; i++) {

        scores.A += Number(
            document.querySelector(
                `input[name="q${i}"]:checked`
            ).value
        );

    }


    // S questions: 13-16
    for (let i = 13; i <= 16; i++) {

        scores.S += Number(
            document.querySelector(
                `input[name="q${i}"]:checked`
            ).value
        );

    }


    // E questions: 17-20
    for (let i = 17; i <= 20; i++) {

        scores.E += Number(
            document.querySelector(
                `input[name="q${i}"]:checked`
            ).value
        );

    }


    // C questions: 21-24
    for (let i = 21; i <= 24; i++) {

        scores.C += Number(
            document.querySelector(
                `input[name="q${i}"]:checked`
            ).value
        );

    }


    try {

        const response = await fetch(
            "http://127.0.0.1:5000/assessment",
            {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ scores: scores })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            if (response.status === 401) {
                alert("Please log in before submitting an assessment.");
                window.location.href = "login.html";
                return;
            }

            throw new Error(data.message || "Could not save assessment results.");

        }

    } catch (error) {

        alert(error instanceof TypeError
            ? "Could not connect to the backend. Make sure Flask is running."
            : error.message);
        return;

    }

    /* Keep a cache for the existing result and course pages. */

    localStorage.setItem(
        "riasecScores",
        JSON.stringify(scores)
    );


    /* Go to result page */

    window.location.href = "result.html";

});


async function logoutAssessmentUser() {

    try {

        await fetch(
            "http://127.0.0.1:5000/logout",
            {
                method: "POST",
                credentials: "include"
            }
        );

    } finally {

        localStorage.removeItem("user");
        localStorage.removeItem("riasecScores");
        window.location.href = "login.html";

    }

}