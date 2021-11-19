// const party_id = window.location.pathname.split("/")[2];

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
        console.log("query = " + query);
        results = await fetch(
            'http://localhost:5000/search_spotify_playground',
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
    fetchResults(query);
    console.log("results = ");
    console.log(results);
    searchResults.innerHTML = results.html;
    var children = searchResults.children;
    for (var i=0; i<children.length; i++){
        var child = children[i];
        child.addEventListener('click', addSong);
    }
};
