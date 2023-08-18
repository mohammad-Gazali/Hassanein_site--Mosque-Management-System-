let searchTable = document.querySelector(".search-table-control-p")
let labelsOfSearch = Array.from(searchTable.children[1].children)
let textSearchTable = searchTable.children[0]

labelsOfSearch.forEach(element => {
    element.onclick = () => {

        textSearchTable.placeholder = element.dataset.place
        
        labelsOfSearch.forEach(e => {
            e.classList.remove("activeChooseTable")
        })
        element.classList.add("activeChooseTable")

        if (element.dataset.place === "أدخل الاسم") {
            textSearchTable.type = "text"
            textSearchTable.removeAttribute("min")
        } else {
            textSearchTable.type = "number"
            textSearchTable.min = 1
        }
    }
});