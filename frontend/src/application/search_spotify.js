const party_id = window.location.pathname.split("/")[2];

const search_input = document.getElementById('search');
let search_term = '';

search_input.addEventListener('input', e => {
    // saving the input value
    search_term = e.target.value;

    // re-displaying countries based on the new search_term
    showResults(search_term);
});

var searchResults = document.querySelector("#searchResults");
let results;

const fetchResults = async (query) => {
    if (query.length > 0) {
        results = await fetch(
            'http://localhost:5000/search_spotify',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "query": query
                })
            }
        ).then(
            res => res.json()
        );
    }
    else {
        results = Object();
        results.items = Array();
    }
};

const addSong = async (event) => {
    console.log("event:");
    console.log(event);
    fetch(
        "http://localhost:5000/add_track",
        {

            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "track": event.target.parentNode.track_info,
            })
        }
    ).then(
        res => res.json()
    );
    searchResults.innerHTML = '';
};

const showResults = async (query) => {
    searchResults.innerHTML = '';
    await fetchResults(query);
    const ul = document.createElement('ul');
    ul.classList.add('results', 'text-left');
    ul.classList.add('overflow-visible');
    ul.classList.add('bg-white', 'divide-y-2', 'divide-green-400');
    results.items.forEach(result => {
        console.log("here is the result you look for");
        console.log(result);
        const li = document.createElement('li');
        li.classList.add('result-item', 'text-left', 'px-2');
        const add_track_btn = document.createElement('button');
        add_track_btn.classList.add('bg-white', 'hover:bg-blue-200', 'w-full', 'rounded-full');
        let artist_name_div = document.createElement('div');
        artist_name_div.classList.add('text-left', 'text-lg', 'text-gray-500');
        artist_name_div.innerText = result.name;

        let track_name_div = document.createElement('div');
        track_name_div.classList.add('text-left', 'text-lg', 'font-bold', 'text-gray-300');
        track_name_div.innerText = result.artist;

        add_track_btn.appendChild(track_name_div);
        add_track_btn.appendChild(artist_name_div);

        add_track_btn.track_info = result;
        add_track_btn.track_info.party_id = party_id;

        add_track_btn.addEventListener('click', addSong);
        li.appendChild(add_track_btn);
        ul.appendChild(li);
    });
    searchResults.appendChild(ul);
};
