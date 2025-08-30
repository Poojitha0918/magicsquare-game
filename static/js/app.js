let startTime, timerInterval, currentPuzzle = null;

// Fetch puzzle sizes and populate dropdown
async function loadLevels() {
  const res = await fetch("/api/puzzles");
  const puzzles = await res.json();
  const select = document.getElementById("level");
  select.innerHTML = "";
  puzzles.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.size} x ${p.size}`;
    select.appendChild(opt);
  });
}

function renderGrid(puzzle) {
  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  grid.style.gridTemplateColumns = `repeat(${puzzle.size}, 50px)`;

  puzzle.given.forEach((row, r) => {
    row.forEach((val, c) => {
      const input = document.createElement("input");
      input.type = "number";
      input.min = 1;
      input.max = puzzle.size * puzzle.size;
      if (val !== 0) {
        input.value = val;
        input.readOnly = true;
      }
      grid.appendChild(input);
    });
  });
}

function startTimer() {
  startTime = Date.now();
  timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const mins = String(Math.floor(elapsed / 60)).padStart(2, "0");
    const secs = String(elapsed % 60).padStart(2, "0");
    document.getElementById("timer").textContent = `${mins}:${secs}`;
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}

async function startGame() {
  const level = document.getElementById("level").value;
  const res = await fetch(`/api/puzzle/${level}`);
  currentPuzzle = await res.json();
  renderGrid(currentPuzzle);
  stopTimer();
  document.getElementById("timer").textContent = "00:00";
  startTimer();
}

function getSolution() {
  const inputs = document.querySelectorAll("#grid input");
  const n = currentPuzzle.size;
  const solution = [];
  for (let r = 0; r < n; r++) {
    solution.push([]);
    for (let c = 0; c < n; c++) {
      const val = parseInt(inputs[r * n + c].value) || 0;
      solution[r].push(val);
    }
  }
  return solution;
}

async function submitSolution() {
  stopTimer();
  const username = document.getElementById("username").value || "anon";
  const duration = Date.now() - startTime;
  const solution = getSolution();

  const res = await fetch("/api/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: username,
      puzzle_id: currentPuzzle.size,
      solution: solution,
      duration_ms: duration
    })
  });

  const result = await res.json();
  alert(result.message || (result.ok ? "Submitted!" : "Error"));

  loadLeaderboard(currentPuzzle.size);
}

async function loadLeaderboard(pid) {
  const res = await fetch(`/api/leaderboard?puzzle_id=${pid}`);
  const items = await res.json();
  const tbody = document.querySelector("#leaderboard tbody");
  tbody.innerHTML = "";
  items.forEach((row, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${i + 1}</td>
                    <td>${row.username}</td>
                    <td>${(row.duration_ms/1000).toFixed(1)}s</td>
                    <td>${new Date(row.submitted_at).toLocaleString()}</td>`;
    tbody.appendChild(tr);
  });
}

document.getElementById("start").addEventListener("click", startGame);
document.getElementById("submit").addEventListener("click", submitSolution);
document.getElementById("reset").addEventListener("click", startGame);

loadLevels();


