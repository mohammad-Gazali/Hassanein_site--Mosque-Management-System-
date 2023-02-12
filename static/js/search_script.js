let filter = document.getElementById("filter-search-radio")
let firstInput = filter.children[0].children[0]
let secondInput = filter.children[1].children[0]

let searchText = document.getElementById("search-text")
let searchId = document.getElementById("search-id")

firstInput.onclick = function () {
    if (firstInput.checked) {
        searchText.classList.remove("d-none")
        searchText.children[0].required = true
        searchId.classList.add("d-none")
        searchId.children[0].required = false
    }
    else if (secondInput.checked) {
        searchText.classList.add("d-none")
        searchText.children[0].required = false
        searchId.classList.remove("d-none")
        searchId.children[0].required = true
    }
}


secondInput.onclick = function () {
    if (firstInput.checked) {
        searchText.classList.remove("d-none")
        searchText.children[0].required = true
        searchId.classList.add("d-none")
        searchId.children[0].required = false
    }
    else if (secondInput.checked) {
        searchText.classList.add("d-none")
        searchText.children[0].required = false
        searchId.classList.remove("d-none")
        searchId.children[0].required = true
    }
}