// Initialize google map.
let map;

// async function return map based on address search form response coordinates.
async function initMap(coordinates) {
    // Coordinates of address form input
    const position = coordinates;
    // Request needed libraries.
    //@ts-ignore
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    // The map, centered at Uluru
    map = new Map(document.getElementById("map"), {
        zoom: 12,
        center: position,
        mapId: "8e0d75328319566e",
    });

    // The marker, positioned at Uluru
    const marker = new AdvancedMarkerElement({
        map: map,
        position: position,
        title: "Your search location",
    });
}

// Process address search form.
async function processForm(evt) {
    evt.preventDefault();

    let streetAddress = $("#street-address").val();
    let zipcode = $("#postal-code").val();
    let city = $("#city").val();
    let state = $("#state").val();

    let payload = {
        address: streetAddress,
        zipcode: zipcode,
        city: city,
        state: state,
    };

    const data = await axios
        .post("/api/geocode", payload, {
            headers: { "Content-Type": "application/json" },
        })
        .then(function (response) {
            console.log(response);
            return response;
        });

    const coordinates = data.data;
    console.log(coordinates);

    initMap(coordinates);
}

// on submit, process form.
$("#address-lookup-form").on("submit", processForm);
