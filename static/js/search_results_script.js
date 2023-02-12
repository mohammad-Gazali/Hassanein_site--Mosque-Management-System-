// for form-add-q-memo

let qMemoAddForms = document.querySelectorAll('.form-add-q-memo')

qMemoAddForms.forEach((element) => {
    element.addEventListener("submit", (event) => {
        let childrens = element.children
        let one_page = childrens[4].value
        let start_range = childrens[6].children[0].children[1].value
        let end_range = childrens[6].children[1].children[1].value
        let check_array = Array.from(childrens[9].children).map((e) => e.children[0].children[0].children[0].checked)
        let first_con = one_page === '' || one_page === null
        let second_con = start_range === '' || start_range === null
        let third_con = end_range === '' || end_range === null
        let fourth_con = check_array.every((e) => e === false)
        let first_sub_con = start_range === '' || start_range === null;
        let second_sub_con = end_range === '' || end_range === null;
        let fifth_con = first_sub_con && !second_sub_con
        let sixth_con = !first_sub_con && second_sub_con
        if (first_con && second_con && third_con && fourth_con){
            event.preventDefault()
            element.children[1].innerText = 'يجب إدخال نوع واحد من التسميع على الأقل'
            element.closest('.model').scrollTo(0, element.children[1].scrollHeight)
            element.children[1].classList.add('active')
        }
        else if (fifth_con){
            event.preventDefault()
            element.children[1].innerText = 'لا يمكن ملء حقل النهاية دون حقل البداية'
            element.closest('.model').scrollTo(0, element.children[1].scrollHeight)
            element.children[1].classList.add('active')
        }
        else if (sixth_con) {
            event.preventDefault()
            element.children[1].innerText = 'لا يمكن ملء حقل البداية دون حقل النهاية'
            element.closest('.model').scrollTo(0, element.children[1].scrollHeight)
            element.children[1].classList.add('active')
        }
        else if (parseInt(start_range) >= parseInt(end_range)) {
            event.preventDefault()
            element.children[1].innerText = 'يجب أن يكون حقل البداية أصغر من حقل النهاية وأن لا يساويه'
            element.closest('.model').scrollTo(0, element.children[1].scrollHeight)
            element.children[1].classList.add('active')
        }
        
    })
})

// for q-memorize filter

let chooses1 = document.querySelectorAll('.student-q-memorizing .filter-container .filter-one input');
let chooses2 = document.querySelectorAll('.student-q-memorizing .filter-container .filter-two input');

chooses1.forEach( (element) => {
    element.addEventListener("click", () => {

        let firstContainer = document.getElementById(element.dataset.targetDisplay)
        let secondContainer = document.getElementById(element.dataset.targetDisplayOpposite)
        
        if (element.checked){
            firstContainer.classList.remove('d-none')
            firstContainer.classList.add('d-flex')
            secondContainer.classList.remove('d-flex')
            secondContainer.classList.add('d-none')
        }
        else {
            secondContainer.classList.remove('d-none')
            secondContainer.classList.add('d-flex')
            firstContainer.classList.remove('d-flex')
            firstContainer.classList.add('d-none')
        } 
    })
})

chooses2.forEach( (element) => {
    element.addEventListener("click", () => {

        let secondContainer = document.getElementById(element.dataset.targetDisplay)
        let firstContainer = document.getElementById(element.dataset.targetDisplayOpposite)

        if (element.checked){
            secondContainer.classList.remove('d-none')
            secondContainer.classList.add('d-flex')
            firstContainer.classList.remove('d-flex')
            firstContainer.classList.add('d-none')
        }
        else {
            firstContainer.classList.remove('d-none')
            firstContainer.classList.add('d-flex')
            secondContainer.classList.remove('d-flex')
            secondContainer.classList.add('d-none')
        }
    })
})

// for drop button in q_memorize_add_model.html

let button = document.querySelectorAll('.drop-button');

button.onclick = function() {
    button.classList.toggle('active');
}

// for memorize-note

let btn = document.querySelectorAll(".btn-dan")
let btn2 = document.querySelectorAll(".btn-save")
let over = document.querySelectorAll(".card-img-overlay")

btn.forEach((element, key) => {
    
    element.onclick = function() {
        over[key].classList.add("active")
    }

    btn2[key].onclick = function() {
        over[key].classList.remove("active")
    }
})