commentForm = document.querySelector('.comment-form');

commentForm.addEventListener('click', commenting)

async function commenting(evt){
    evt.preventDefault()
    if (evt.target.id === "comment-btn"){
        console.log('Clicked')
        businessId = evt.target.dataset.business;
        message = document.querySelector('#message');
        const res = await axios.post(`/users/comments/${businessId}`,{message:message.value});
        if (res.data['result'] =='OK'){
            const newComment = res.data['new_comment'];
            const commentHTML = document.createElement('div');
            commentHTML.classList.add('comment');
            commentHTML.classList.add('card');
            commentHTML.classList.add('my-2');
            const content = `
                        <div class="comment card my-2">
                            <div class="row">
                                <div class="col-md-4">
                                    <img src="${newComment.user_image_url}" alt="" class="card-img-top">
                                </div>
                                <div class="col-md-8">
                                    <div class="card-body">
                                        <h4 class="card-title">${newComment.user_first_name} ${newComment.user_last_name} @<a href="/restaurants/${newComment.business_id}">${newComment.business_name}</a></h4>
                                        <p class="card-text">${newComment.message}</p>
                                        <p class="card-text text-mute">${newComment.created_at}</p>
                                    </div>
                                </div>
                            </div>
                        </div>`
            commentHTML.innerHTML = content;
            document.querySelector('.comments-list').append(commentHTML);
            message.textContent=''
        }
    }
}