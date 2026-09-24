// ---------- TAB SWITCHING ----------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// ---------- CHAT (STUDY HELPER) ----------
const chatWindow = document.getElementById("chat-window");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendChat() {
  const question = chatInput.value.trim();
  if (!question) return;

  addMessage(question, "user");
  chatInput.value = "";
  addMessage("Thinking...", "bot");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();

    // remove "Thinking..." placeholder
    chatWindow.removeChild(chatWindow.lastChild);

    if (data.error) {
      addMessage("Error: " + data.error, "bot");
    } else {
      addMessage(data.answer, "bot");
    }
  } catch (err) {
    chatWindow.removeChild(chatWindow.lastChild);
    addMessage("Something went wrong. Please try again.", "bot");
  }
}

chatSend.addEventListener("click", sendChat);
chatInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendChat();
});

// ---------- QUIZ GENERATOR ----------
const quizTopic = document.getElementById("quiz-topic");
const quizCount = document.getElementById("quiz-count");
const quizDifficulty = document.getElementById("quiz-difficulty");
const quizGenerate = document.getElementById("quiz-generate");
const quizContainer = document.getElementById("quiz-container");
const quizLoading = document.getElementById("quiz-loading");
const quizScore = document.getElementById("quiz-score");

let currentScore = 0;
let totalAnswered = 0;

quizGenerate.addEventListener("click", async () => {
  const topic = quizTopic.value.trim();
  if (!topic) {
    alert("Please enter a topic.");
    return;
  }

  quizContainer.innerHTML = "";
  quizScore.classList.add("hidden");
  quizLoading.classList.remove("hidden");
  currentScore = 0;
  totalAnswered = 0;

  try {
    const res = await fetch("/quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic,
        num_questions: quizCount.value,
        difficulty: quizDifficulty.value,
      }),
    });
    const data = await res.json();
    quizLoading.classList.add("hidden");

    if (data.error) {
      quizContainer.innerHTML = `<p style="color:red">${data.error}</p>`;
      return;
    }

    renderQuiz(data.questions);
  } catch (err) {
    quizLoading.classList.add("hidden");
    quizContainer.innerHTML = `<p style="color:red">Something went wrong. Please try again.</p>`;
  }
});

function renderQuiz(questions) {
  quizContainer.innerHTML = "";

  questions.forEach((q, idx) => {
    const block = document.createElement("div");
    block.className = "question-block";

    const title = document.createElement("h3");
    title.textContent = `${idx + 1}. ${q.question}`;
    block.appendChild(title);

    q.options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.className = "option-btn";
      btn.textContent = opt;
      btn.addEventListener("click", () => {
        // disable all options in this block after answering
        const allBtns = block.querySelectorAll(".option-btn");
        if (block.dataset.answered) return;
        block.dataset.answered = "true";

        allBtns.forEach((b) => {
          if (b.textContent === q.answer) {
            b.classList.add("correct");
          } else if (b === btn) {
            b.classList.add("wrong");
          }
        });

        totalAnswered++;
        if (opt === q.answer) currentScore++;

        const explanation = document.createElement("div");
        explanation.className = "explanation";
        explanation.textContent = q.explanation || "";
        block.appendChild(explanation);

        updateScore(questions.length);
      });
      block.appendChild(btn);
    });

    quizContainer.appendChild(block);
  });
}

function updateScore(total) {
  quizScore.classList.remove("hidden");
  quizScore.textContent = `Score: ${currentScore} / ${totalAnswered} answered (out of ${total} total)`;
}

// ---------- SUMMARY MODULE ----------
const summaryInput = document.getElementById("summary-input");
const summaryGenerate = document.getElementById("summary-generate");
const summaryLoading = document.getElementById("summary-loading");
const summaryResult = document.getElementById("summary-result");

summaryGenerate.addEventListener("click", async () => {
  const text = summaryInput.value.trim();
  if (!text) {
    alert("Please paste some text first.");
    return;
  }

  summaryResult.style.display = "none";
  summaryLoading.classList.remove("hidden");

  try {
    const res = await fetch("/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    summaryLoading.classList.add("hidden");

    summaryResult.style.display = "block";
    summaryResult.textContent = data.error ? data.error : data.summary;
  } catch (err) {
    summaryLoading.classList.add("hidden");
    summaryResult.style.display = "block";
    summaryResult.textContent = "Something went wrong. Please try again.";
  }
});

// ---------- LEARNING PATH MODULE ----------
const pathTopic = document.getElementById("path-topic");
const pathGenerate = document.getElementById("path-generate");
const pathLoading = document.getElementById("path-loading");
const pathResult = document.getElementById("path-result");

pathGenerate.addEventListener("click", async () => {
  const topic = pathTopic.value.trim();
  if (!topic) {
    alert("Please enter a topic.");
    return;
  }

  pathResult.style.display = "none";
  pathLoading.classList.remove("hidden");

  try {
    const res = await fetch("/learning-path", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
    const data = await res.json();
    pathLoading.classList.add("hidden");

    pathResult.style.display = "block";
    pathResult.textContent = data.error ? data.error : data.path;
  } catch (err) {
    pathLoading.classList.add("hidden");
    pathResult.style.display = "block";
    pathResult.textContent = "Something went wrong. Please try again.";
  }
});
