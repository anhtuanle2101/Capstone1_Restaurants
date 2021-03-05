restaurantCards = document.querySelector('.cards-list')

restaurantCards.addEventListener('click', favoriteToggle)

async function favoriteToggle(evt){
    if (evt.target.classList.contains('favorite-btn')){
        businessId = evt.target.dataset.business;
        const res = await axios.post(`/users/favorites/${businessId}`)
        if (res.data['result'] == 'OK'){
            evt.target.classList.remove('favorite-btn');
            evt.target.classList.add('unfavorite-btn');
        }
    }else if (evt.target.classList.contains('unfavorite-btn')){
        businessId = evt.target.dataset.business;
        const res = await axios.delete(`/users/favorites/${businessId}`)
        if (res.data['result'] == 'OK'){
            evt.target.classList.add('favorite-btn');
            evt.target.classList.remove('unfavorite-btn');
        }
    }
    
}