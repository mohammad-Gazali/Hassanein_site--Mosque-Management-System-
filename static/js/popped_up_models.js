const openModelButtons = document.querySelectorAll("[data-model-target]")
const closeModelButtons = document.querySelectorAll("[data-close-button]")
const overlay = document.getElementById("overlay")

overlay.addEventListener("click", () => {
    const models = document.querySelectorAll(".model.active")
    models.forEach(model => 
        closeModel(model)
    )
})

openModelButtons.forEach(btn =>{
    btn.addEventListener("click", () => {
        const model = document.querySelector(btn.dataset.modelTarget)
        openModel(model)
    })
})

closeModelButtons.forEach(btn =>{
    btn.addEventListener("click", () => {
        const model = btn.closest(".model")
        closeModel(model)
    })
})

function openModel(model) {
    if (model == null) {
        return
    }
    model.classList.add('active')
    overlay.classList.add('active')
}

function closeModel(model) {
    if (model == null) {
        return
    }
    model.classList.remove('active')
    overlay.classList.remove('active')
}