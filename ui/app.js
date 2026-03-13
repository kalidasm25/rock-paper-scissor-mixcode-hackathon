const CHOICES = ["rock", "paper", "scissors", "lizard", "spock"];

const ICONS = {
  rock: "🪨",
  paper: "📄",
  scissors: "✂️",
  lizard: "🦎",
  spock: "🖖",
  unknown: "❔"
};

const ACTION_HINTS = {
  rock: "Smash!",
  paper: "Wrap!",
  scissors: "Snip!",
  lizard: "Zap!",
  spock: "Beam!"
};

const choicesContainer = document.getElementById("choices");
const statusEl = document.getElementById("status");
const playerChoiceEl = document.getElementById("playerChoice");
const computerChoiceEl = document.getElementById("computerChoice");
const playerIconEl = document.getElementById("playerIcon");
const computerIconEl = document.getElementById("computerIcon");
const resultEl = document.getElementById("result");
const playerScoreEl = document.getElementById("playerScore");
const computerScoreEl = document.getElementById("computerScore");
const tieScoreEl = document.getElementById("tieScore");
const roundTrackerEl = document.getElementById("roundTracker");
const newMatchBtn = document.getElementById("newMatchBtn");
const buttonsByChoice = new Map();

const TARGET_WINS = 3;
let playerWins = 0;
let computerWins = 0;
let ties = 0;
let decisiveRounds = 0;
let matchOver = false;

function toLabel(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : "-";
}

function getIconMarkup(choice) {
  const symbol = ICONS[choice] || ICONS.unknown;
  return `<span class="emoji-icon" role="img" aria-label="${toLabel(choice)}">${symbol}</span>`;
}

function setBadgeIcon(targetEl, choice) {
  targetEl.classList.remove("move-rock", "move-paper", "move-scissors", "move-lizard", "move-spock", "move-unknown");
  targetEl.classList.add(`move-${choice || "unknown"}`);
  targetEl.innerHTML = getIconMarkup(choice);
}

function refreshResultStyle(winner) {
  resultEl.classList.remove("player", "computer", "tie", "pulse");
  if (winner) {
    resultEl.classList.add(winner);
  }
  resultEl.classList.add("pulse");
}

function setChoicesEnabled(enabled) {
  for (const button of buttonsByChoice.values()) {
    button.disabled = !enabled;
  }
}

function updateScoreboard() {
  playerScoreEl.textContent = String(playerWins);
  computerScoreEl.textContent = String(computerWins);
  tieScoreEl.textContent = String(ties);
  roundTrackerEl.textContent = `Round ${decisiveRounds + 1}`;
}

function checkMatchWinner() {
  if (playerWins >= TARGET_WINS) {
    matchOver = true;
    setChoicesEnabled(false);
    statusEl.textContent = `Match over: You win best of 5, ${playerWins}-${computerWins}!`;
    return true;
  }

  if (computerWins >= TARGET_WINS) {
    matchOver = true;
    setChoicesEnabled(false);
    statusEl.textContent = `Match over: Computer wins best of 5, ${computerWins}-${playerWins}.`;
    return true;
  }

  return false;
}

function resetMatch() {
  playerWins = 0;
  computerWins = 0;
  ties = 0;
  decisiveRounds = 0;
  matchOver = false;

  statusEl.textContent = "New match started. Make your move!";
  playerChoiceEl.textContent = "-";
  computerChoiceEl.textContent = "-";
  setBadgeIcon(playerIconEl, null);
  setBadgeIcon(computerIconEl, null);
  refreshResultStyle();
  setChoicesEnabled(true);
  updateScoreboard();

  for (const button of buttonsByChoice.values()) {
    button.classList.remove("is-selected");
  }
}

function setActiveChoice(choice) {
  for (const [key, button] of buttonsByChoice.entries()) {
    if (key === choice) {
      button.classList.add("is-selected");
    } else {
      button.classList.remove("is-selected");
    }
  }
}

function animateChoiceClick(choice) {
  const button = buttonsByChoice.get(choice);
  if (!button) {
    return;
  }

  button.classList.remove("click-pop");
  // Force reflow to restart the animation when the same choice is clicked repeatedly.
  void button.offsetWidth;
  button.classList.add("click-pop");
}

async function play(choice) {
  if (matchOver) {
    statusEl.textContent = "Match finished. Tap 'Start New Match' to play again.";
    return;
  }

  statusEl.textContent = "Playing...";
  setActiveChoice(choice);
  animateChoiceClick(choice);
  setBadgeIcon(playerIconEl, choice);
  playerChoiceEl.textContent = toLabel(choice);
  refreshResultStyle();

  try {
    const response = await fetch(`/api/${choice}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}"
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    playerChoiceEl.textContent = toLabel(result.player_choice);
    computerChoiceEl.textContent = toLabel(result.computer_choice);
    statusEl.textContent = result.message;
    setBadgeIcon(playerIconEl, result.player_choice);
    setBadgeIcon(computerIconEl, result.computer_choice);
    refreshResultStyle(result.winner);

    if (result.winner === "player") {
      playerWins += 1;
      decisiveRounds += 1;
    } else if (result.winner === "computer") {
      computerWins += 1;
      decisiveRounds += 1;
    } else {
      ties += 1;
    }

    updateScoreboard();
    if (!checkMatchWinner()) {
      statusEl.textContent = `${result.message} Keep going to 3 wins.`;
    }
  } catch (error) {
    statusEl.textContent = "Could not reach API. Make sure the server is running.";
    refreshResultStyle();
    console.error(error);
  }
}

for (const choice of CHOICES) {
  const button = document.createElement("button");
  button.className = `choice-btn move-${choice}`;
  button.innerHTML = `<span class="choice-icon">${getIconMarkup(choice)}</span><span class="choice-name">${toLabel(choice)}</span><span class="choice-note">${ACTION_HINTS[choice]}</span>`;
  button.addEventListener("click", () => play(choice));
  choicesContainer.appendChild(button);
  buttonsByChoice.set(choice, button);
}

setBadgeIcon(playerIconEl, null);
setBadgeIcon(computerIconEl, null);
updateScoreboard();

newMatchBtn.addEventListener("click", resetMatch);
