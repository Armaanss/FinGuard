const HISTORY_KEY = "finguardSearchHistory";
const MAX_HISTORY = 4;


// Load FinGuard search history
let searchHistory = JSON.parse(
    localStorage.getItem(HISTORY_KEY)
) || [];


// Filter transactions
function filterTransactions() {

    let searchInput = document
        .getElementById("searchInput")
        .value
        .toLowerCase();

    let riskFilter = document.getElementById("riskFilter").value;

    let table = document.getElementById("transactionTable");

    let rows = table
        .getElementsByTagName("tbody")[0]
        .getElementsByTagName("tr");

    for (let row of rows) {

        let rowText = row.innerText.toLowerCase();
        let risk = row.cells[8].innerText.trim();

        let searchMatch = rowText.includes(searchInput);

        let riskMatch =
            riskFilter === "ALL" || risk === riskFilter;

        if (searchMatch && riskMatch) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    }
}


// Save search keyword
function saveSearch() {

    let input = document.getElementById("searchInput");

    let keyword = input.value.trim();

    if (keyword === "") {
        return;
    }

    // Remove duplicate
    searchHistory = searchHistory.filter(
        item => item.toLowerCase() !== keyword.toLowerCase()
    );

    // Add newest search at beginning
    searchHistory.unshift(keyword);

    // Keep only last 4 searches
    searchHistory = searchHistory.slice(0, MAX_HISTORY);

    // Save FinGuard history
    localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(searchHistory)
    );

    showSearchHistory();
}


// Display FinGuard search history
function showSearchHistory() {

    let datalist = document.getElementById("searchHistory");

    datalist.innerHTML = "";

    searchHistory.forEach(function(keyword) {

        let option = document.createElement("option");

        option.value = keyword;

        datalist.appendChild(option);
    });
}


// Save search when user presses Enter
document.getElementById("searchInput").addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {
            saveSearch();
        }

    }
);


// Load history when page opens
showSearchHistory();