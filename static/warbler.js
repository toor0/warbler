
$("#terms").on("click", (e) => {
    e.preventDefault();
    $(".modal-terms").modal('toggle');
});

$("#new-message").on("click", (e) => {
    e.preventDefault();
    $(".modal-msg").modal('toggle');
});

$('#new-message-button').on("click", async function(e) {
    e.preventDefault();
    messageText = $('#new-message-text').val();
    let req = {"text": messageText}
    let res = await $.post("/messages/new", req);
    if (res.err) {
        displayError();
    }
    $(".modal").modal('toggle');
    window.location.replace(res);
});

$("ul").on("click", ".fa-heart", async function(e) {
    e.preventDefault();
    let heart = $(e.target)
    let id = heart.attr("message-id")
    let likeCount = $(`#count-${id}`)
    console.log(likeCount)
    if (heart.hasClass("fas")) {
        let res = await $.post(`/messages/${id}/unlike`);
        if (res.err) {
            displayError();
        }
        likeCount.text(res);
    } else if (heart.hasClass("far")) {
        let res = await $.post(`/messages/${id}/like`);
        if (res.err) {
            displayError();
        }
        likeCount.text(res);
    }
    heart.toggleClass("fas far")
});