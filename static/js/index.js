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

    let rentalPayload = {
        zipcode: zipcode,
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

    const realtyData = await axios
        .post("/api/rental-data", rentalPayload, {
            headers: { "Content-Type": "application/json" },
        })
        .then(function (response) {
            console.log(response);
            return response;
        });

    // const rentalAverages = realtyData["data"]["rentalData"]["detailed"];
    // for (let average in rentalAverages) {
    //   for () {
    //       console.log(average.)
    //     }
    // }
    const average0 =
        realtyData["data"]["rentalData"]["detailed"][0]["averageRent"];
    const average1 =
        realtyData["data"]["rentalData"]["detailed"][1]["averageRent"];
    const average2 =
        realtyData["data"]["rentalData"]["detailed"][2]["averageRent"];
    const average3 =
        realtyData["data"]["rentalData"]["detailed"][3]["averageRent"];
    const average4 =
        realtyData["data"]["rentalData"]["detailed"][4]["averageRent"];

    $("#rental-data").html(`
        <div class="container-fluid">
    <p class="h2">Rental Averages for ${zipcode}</p>
    <button type="button" class="btn btn-outline-info" action="/search/favorite"> Save to favorites </button>
  <table class="table table-striped">
  <thead>
  <tr>
  <th scope="col">Bedrooms</th>
      <th scope="col">Average Rent in USD</th>
      </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">0</th>
      <td>${average0}</td>
    </tr>
    <tr>
      <th scope="row">1</th>
      <td>${average1}</td>
    </tr>
    <tr>
      <th scope="row">2</th>
      <td>${average2}</td>
    </tr>
    <tr>
      <th scope="row">3</th>
      <td>${average3}</td>
    </tr>
    <tr>
      <th scope="row">4</th>
      <td>${average4}</td>
    </tr>
    </tbody>
    </table>
    </div>`);

    initMap(coordinates);
}

// on submit, process form.
$("#address-lookup-form").on("submit", processForm);
