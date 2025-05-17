document.addEventListener("DOMContentLoaded", function () {
    const voteForm = document.getElementById("voteForm");
    if (!voteForm) return;

    voteForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const surveyId = voteForm.getAttribute("data-survey-id");
        const formData = new FormData(voteForm);
        formData.append("survey_id", surveyId);

        fetch("/vote/submit", {
            method: "POST",
            body: formData,
            credentials: "same-origin"
        })
        .then(response => {
            if (!response.ok) throw new Error("Sunucu yanıt vermedi");
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const resultsUl = document.getElementById("results");
                resultsUl.innerHTML = "";

                let totalVotes = 0;
                data.results.forEach(r => totalVotes += r.count);

                data.results.forEach(r => {
                    const li = document.createElement("li");
                    const percent = totalVotes ? ((r.count / totalVotes) * 100).toFixed(1) : 0;
                    li.textContent = `${r.answer}: ${r.count} oy (${percent}%)`;
                    resultsUl.appendChild(li);
                });

                voteForm.style.display = "none";
                const votedMsg = document.createElement("p");
                votedMsg.id = "votedMessage";
                votedMsg.style.color = "green";
                votedMsg.style.fontWeight = "bold";
                votedMsg.style.marginTop = "10px";
                votedMsg.textContent = "Oy verdiniz, teşekkürler!";
                voteForm.parentNode.insertBefore(votedMsg, voteForm.nextSibling);
            } else {
                alert(data.message || "Oy gönderilemedi.");
            }
        })
        .catch(err => {
            alert("Sunucu ile bağlantı kurulamadı.");  // Gerekirse kaldırılabilir
            console.error("Hata:", err);
        });
    });
});
